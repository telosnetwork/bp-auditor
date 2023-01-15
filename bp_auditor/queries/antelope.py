#!/usr/bin/env python3

import time
import json

import asks

from ..utils import call_with_retry, MalformedJSONError


'''This module is meant for standard antelope io queries
'''


async def get_producer_schedule(url: str):
    response = await call_with_retry(
        asks.get, f'{url}/v1/chain/get_producer_schedule')
    return response.json()


async def get_all_producers(url: str):
    producers = []
    lower = 0
    while len(producers) < 42:
        response = await call_with_retry(
            asks.post,
            f'{url}/v1/chain/get_table_rows',
            json={
                'json': 'true',
                'code': 'eosio',
                'scope': 'eosio',
                'table': 'producers',
                'index_position': 2,
                'key_type': 'float64',
                'lower': lower,
                'limit': 42
            }
        )
        response = response.json()

        producers += response['rows']

        lower = response['rows'][0]['total_votes']

    return producers


_info = None
_last_time = 0
async def get_info(url: str):
    '''Simple get info query with 4 second cache
    '''
    global _info, _last_time
    now = time.time()
    if now - _last_time > 4 or not _info:
        _last_time = now
        response = await call_with_retry(
            asks.get, f'{url}/v1/chain/get_info')
        _info = response.json()

    return _info

async def get_chain_id(url: str):
    result = await get_info(url)
    return result['chain_id']


async def get_block(node_url: str, block_num: int) -> dict:
    url = f"{node_url}/v1/chain/get_block"
    params = {"block_num_or_id": str(block_num)}
    response = await call_with_retry(
        asks.post, url, json=params)
    try:
        return response.json()

    except json.JSONDecodeError as e:
        raise MalformedJSONError(str(e))
