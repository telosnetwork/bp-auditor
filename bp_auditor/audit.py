#!/usr/bin/env python3

import logging

import trio

from .queries import *


async def check_producer(chain_url: str, producer: dict, chain_id: str):
    report = {'owner': producer['owner']}
    url = producer['url']

    if not url:
        report['bp_json'] = f'NO URL ON CHAIN! owner: {producer["owner"]}'

    report['url'] = url
    try:
        bp_json = await get_bp_json(url, chain_id)
        logging.info(f'got bp json for {url}')

    except BaseException as e:
        report['bp_json'] = str(e)
        return report

    try:
        validate_bp_json(bp_json)

    except MalformedJSONError as e:
        report['bp_json'] = str(e)
        return report

    report['bp_json'] = 'ok'
    logging.info(f'bp json for {url} valid')

    # check tls version on each ssl endpoint
    ssl_endpoints = [
        node
        for node in bp_json['nodes']
        if 'ssl_endpoint' in node and node['ssl_endpoint'] != ''
    ]
    report['ssl_endpoints'] = []
    tlsv = None
    for node in ssl_endpoints:

        try:
            tlsv = await get_tls_version(node['ssl_endpoint'])

        except NetworkError as e:
            tlsv = str(e)

        report['ssl_endpoints'].append(
            (node['node_type'], node['ssl_endpoint'], tlsv))

    logging.info(f'checked ssl endpoint for {url}')

    # check p2p node connect
    p2p_endpoints = [
        node
        for node in bp_json['nodes']
        if 'p2p_endpoint' in node and node['p2p_endpoint'] != ''
    ]
    report['p2p_endpoints'] = []
    for node in p2p_endpoints:
        try:

            domain, port = node['p2p_endpoint'].split(':')
            port = int(port)

        except ValueError:
            report['p2p_endpoints'].append(
                (node['node_type'], node['p2p_endpoint'], 'error'))

        try:
            await check_port(domain, port)
            result = 'ok'

        except NetworkError as e:
            result = str(e)

        report['p2p_endpoints'].append(
            (node['node_type'], node['p2p_endpoint'], 'ok'))

    logging.info(f'checked p2p endpoint for {url}')

    # get api node for history query
    api_endpoints = [
        node
        for node in bp_json['nodes']
        if 'api_endpoint' in node and node['api_endpoint'] != ''
    ]
    report['api_endpoints'] = []
    api_endpoint = None
    for node in api_endpoints:
        node_type = node['node_type']
        if (node_type == 'query' or
            node_type == 'full' or
            'query' in node_type or
            'full' in node_type):
            api_endpoint = node['api_endpoint']

        report['api_endpoints'].append(
            (node['node_type'], node['api_endpoint']))

    if api_endpoint:
        logging.info(f'checking history for {api_endpoint}')
        early_block, late_block = await check_history(chain_url, api_endpoint)

    else:
        early_block, late_block = ('couldn\'t figure out api endpoint' for i in range(2))

    report['history'] = {
        'early': early_block,
        'late': late_block
    }

    logging.info(f'checked history for {url}')

    report['cpu'] = await get_avg_performance_this_month(
        chain_url,
        bp_json['producer_account_name']
    )

    return report


import traceback
async def check_all_producers(
    chain_url: str,
    db_location: str = 'reports.db',
    concurrency: int = 10
):
    chain_id = await get_chain_id(chain_url)
    logging.info(f'{chain_url} chain id {chain_id}')

    # get top 42 producers ordered by vote
    producers = await get_all_producers(chain_url)

    limit = trio.CapacityLimiter(concurrency)
    reports = []
    async def get_report(_prod: dict):
        async with limit:
            try:
                report = await check_producer(chain_url, _prod, chain_id)

            except BaseException as e:
                e_text = traceback.format_exc()
                logging.critical(e_text)
                report = {
                    'url': _prod['url'],
                    'exception': e_text
                }

        reports.append(report)
        logging.info(f'finished report {len(reports)}/42')

    async with trio.open_nursery() as n:
        for producer in producers:
            n.start_soon(get_report, producer)

    return reports
