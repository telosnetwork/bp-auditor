#!/usr/bin/python3

import logging

from functools import partial

import trio
import click

from .db import store_reports
from .xlsx import produce_monthly_report
from .audit import check_all_producers
from .utils import install_sysmted_service
from .telegram import send_file_over_telegram


@click.group()
def bpaudit(*args, **kwargs):
    pass

@bpaudit.command()
@click.option('--chain', '-c', default='telos-mainnet')
@click.option('--url', '-u', default='https://mainnet.telos.net')
@click.option('--db', '-d', default='reports.db')
@click.option('--log-level', '-l', default='INFO')
def install(chain, url, db, log_level):
    logging.basicConfig(level=log_level)
    install_sysmted_service(chain, url, db)


@bpaudit.command()
@click.option('--url', '-u', default='https://mainnet.telos.net')
@click.option('--db', '-d', default='reports.db')
@click.option('--log-level', '-l', default='INFO')
@click.option('--concurrency', '-c', default=10)
def gather(url, db, log_level, concurrency):
    logging.basicConfig(level=log_level)
    reports = trio.run(
        partial(
            check_all_producers,
            url,
            db_location=db,
            concurrency=concurrency
        ))

    logging.info('storing to db...')
    store_reports(db, reports)
    logging.info('done.')

@bpaudit.command()
@click.option('--db', '-d', default='reports.db')
@click.option('--doc', '-D', default='report.xlsx')
@click.option('--log-level', '-l', default='INFO')
def produce(db, doc, log_level):
    logging.basicConfig(level=log_level)
    produce_monthly_report(db, doc)

@bpaudit.command()
@click.option('--doc', '-D', default='report.xlsx')
@click.option('--log-level', '-l', default='INFO')
def sendtg(doc, log_level):
    logging.basicConfig(level=log_level)
    send_file_over_telegram(doc)
