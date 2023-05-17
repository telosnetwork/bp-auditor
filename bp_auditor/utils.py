#!/usr/bin/env python3

import sys

from random import randint
from pathlib import Path


class NetworkError(BaseException):
    ...


class MalformedJSONError(BaseException):
    ...


def _validate_fields(fields: list[str], obj: dict) -> None:
    for field in fields:
        if field not in obj:
            raise MalformedJSONError(
                f'json validation error: {field} not present')

def validate_bp_json(bp_json: dict):
    _validate_fields(['producer_account_name', 'org', 'nodes'], bp_json)


def validate_block(block: dict):
    _validate_fields([
        "timestamp",
        "producer",
        "confirmed",
        "previous",
        "transaction_mroot",
        "action_mroot",
        "schedule_version",
        "new_producers",
        "producer_signature",
        "transactions",
        "id",
        "block_num",
        "ref_block_prefix"
    ], block)


async def call_with_retry(
    call, *args, **kwargs
):
    '''Attempts to run the same call 3 times, and caches the exception
    if it runs out of tries raises, usefull for network functions to
    discard unrelated network errors to the query at hand
    '''
    ex = None
    for i in range(3):
        try:
            return await call(*args, **kwargs)

        except BaseException as e:
            ex = e

    raise ex


def get_random_block_number(head_block: int, percentile: int):
    '''Gets a random block number from the bottom 10% or top 90%
    of blocks
    '''
    match percentile:
        case 10:
            value = randint(1, round(head_block * 0.1))
        case 90:
            value = randint(round(head_block * 0.9), head_block)
        case _:
            raise ValueError('percentile must be 10 or 90')

    return round(value, 0)


_templates_dir = Path(__file__).resolve().parent / 'templates'
_binary_dir = Path(sys.executable).resolve().parent
def install_sysmted_service(chain: str, url: str, db: str = 'reports.db'):
    with (
        open(_templates_dir / 'auditor.service') as service_template_file,
        open(_templates_dir / 'auditor.timer') as timer_template_file,
    ):
        service_template = service_template_file.read()
        timer_template = timer_template_file.read()

    work_dir = Path().cwd()

    python_bin = input(f'Enter python bin directory (def: {_binary_dir}): ')
    if len(python_bin) == 0:
        python_bin = _binary_dir

    service_unit = service_template.format(
        python_bin=str(python_bin),
        chain_url=url,
        db_location=db,
        work_dir=str(work_dir)
    )
    timer_unit = timer_template.format(
        chain=chain
    )

    service_unit_path = work_dir / f'bpaudit-{chain}.service'
    timer_unit_path = work_dir / f'bpaudit-{chain}.timer'

    with (
        open(service_unit_path, 'w+') as service_template_file,
        open(timer_unit_path, 'w+') as timer_template_file,
    ):
        service_template_file.write(service_unit)
        timer_template_file.write(timer_unit)

    print('Generated .service and .timer files:\n')
    print(str(service_unit_path))
    print(str(timer_unit_path))

    while True:
        resp = input('Do you wish to install units? y/n: ')
        match resp:
            case 'y':
                _systemd_default = str((Path().home() / '.config/systemd/user/').resolve())
                systemd_dir = input(f'Enter systemd unit directory (def: {_systemd_default}): ')
                if len(systemd_dir) == 0:
                    systemd_dir = _systemd_default

                systemd_dir = Path(systemd_dir).resolve()

                service_link = systemd_dir / service_unit_path.name
                if service_link.is_file():
                    service_link.unlink()
                service_link.symlink_to(service_unit_path)

                timer_link = systemd_dir / timer_unit_path.name
                if timer_link.is_file():
                    timer_link.unlink()
                timer_link.symlink_to(timer_unit_path)

                print(f'Done! create symlinks on {systemd_dir} to the generated unit files.\n')
                print('To make systemd daemon aware of the new unit files please run:\n')
                print('\t\"systemctl daemon-reload\"\n')

                print('To run data gatherer manually:\n')
                print(f'\t\"systemctl start {service_unit_path.name}\"\n')

                print('To start timer (will run data gatherer every day at 00:00 UTC):\n')
                print(f'\t\"systemctl enable {timer_unit_path.name}\"\n')
                print(f'\t\"systemctl start {timer_unit_path.name}\"\n')

                print('IMPORTANT: add \"--user\" to systemd commands if installed at user level.')

            case 'n':
                print('skip install...')

            case _:
                print('invalid option...')
                continue

        break
