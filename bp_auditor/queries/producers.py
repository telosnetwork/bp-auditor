#!/usr/bin/env python3

import ssl
import json
import socket

from datetime import datetime

import asks
import trio

from ..utils import *

from .antelope import *


async def get_bp_json(url: str, chain_id: str):
    # https://github.com/eosrio/bp-info-standard

    try:
        response = await call_with_retry(
            asks.get, f'{url}/chains.json')

        if response.status_code == 404:
            response = await call_with_retry(
                asks.get, f'{url}/bp.json')

            if response.status_code == 404:
                response = await call_with_retry(
                    asks.get, f'{url}/telos.json')

    except ssl.SSLCertVerificationError as e:
        raise NetworkError(str(e))

    except socket.gaierror as e:
        raise NetworkError(str(e))

    if response.status_code == 404:
        raise NetworkError('404: bp json not found')

    try:
        data = response.json()

        if 'chains' in data:
            data = data['chains']
            if chain_id not in data:
                raise MalformedJSONError('chain_id not in chains.json')

            sub_url = data[chain_id]

            response = await call_with_retry(
                asks.get,
                f'{url}{sub_url}'
            )

            if response.status_code == 404:
                raise NetworkError('404: sub url not found')

            data = response.json()

        return data

    except json.JSONDecodeError:
        raise MalformedJSONError('json decode error')


async def check_history(chain_url: str, url: str):
    chain_info = await get_info(chain_url)

    head_block_num = chain_info['head_block_num']

    # get two samples
    try:
        with trio.move_on_after(5) as cs:
            early_block = await get_block(
                url, get_random_block_number(head_block_num, 10))

        if cs.cancelled_caught:
            early = 'timeout'

        else:
            if 'code' in early_block and early_block['code'] <= 400:
                early = f'{early_block["code"]}: not found'

            else:
                validate_block(early_block)
                early = (early_block['id'], early_block['block_num'])

    except BaseException as e:
        early = str(e)

    try:
        with trio.move_on_after(5) as cs:
            late_block = await get_block(
                url, get_random_block_number(head_block_num, 90))

        if cs.cancelled_caught:
            late = 'timeout'

        else:
            if 'code' in late_block and late_block['code'] <= 400:
                late = f'{late_block["code"]}: not found'

            else:
                validate_block(late_block)
                late = (late_block['id'], late_block['block_num'])

    except BaseException as e:
        late = str(e)

    return (early, late)


async def get_avg_performance_this_month(chain_url: str, producer: str):
    # Get current UTC date and time
    now = datetime.utcnow()

    # Set hour, minute, second, and microsecond to 0
    first_day_month = str(
        now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)).replace(' ', 'T')

    # build API call
    url = f'{chain_url}/v2/history/get_actions?filter=eosmechanics:cpu'
    url += '&producer=' + producer
    # url += "limit=2&" # url += "sort=desc&"
    url += '&after=' + first_day_month

    # make API call
    response = await call_with_retry(asks.get, url)

    try:
        response = response.json()

        if 'actions' not in response:
            raise json.JSONDecodeError()

        actions = response['actions']

    except json.JSONDecodeError:
        return 'json decode error on get_performance query'

    total_actions = len(actions)

    if total_actions == 0:
        return 'bp hasn\'t called eosmechanics:cpu this month'

    sum_cpu = 0
    for action in actions:
        sum_cpu += action['cpu_usage_us']

    return f'{sum_cpu / total_actions:.2f} us'
