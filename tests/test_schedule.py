#!/usr/bin/env python3

import random
import logging

from bp_auditor.queries import *
from bp_auditor.audit import check_producer


url = 'https://mainnet.telos.net'


async def test_check_one():
    chain_id = await get_chain_id(url)
    logging.info(f'{url} chain id {chain_id}')

    # get top 42 producers ordered by vote
    producers = await get_all_producers(url)

    logging.info(
        json.dumps(
            (await check_producer(url, producers[random.randint(0, 41)]['url'], chain_id)),
            indent=4
        )
    )
