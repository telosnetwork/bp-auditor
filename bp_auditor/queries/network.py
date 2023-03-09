#!/usr/bin/env python3

import ssl
import socket

import trio

from ..utils import NetworkError


async def get_tls_version(host, port=443):
    context = ssl.create_default_context()
    try:
        with trio.move_on_after(10) as cscope:
            ssock = await trio.open_ssl_over_tcp_stream(
                host, port,
                ssl_context=context
            )

        if cscope.cancelled_caught:
            raise NetworkError('timeout connecting to endpoint')

    except OSError as e:
        raise NetworkError(str(e))

    except trio.BrokenResourceError as e:
        raise NetworkError(str(e))

    try:
        await ssock.do_handshake()

    except ssl.SSLCertVerificationError as e:
        raise NetworkError(str(e))

    except trio.BrokenResourceError as e:
        raise NetworkError(str(e))

    tls_version = ssock.cipher()[1]
    await ssock.aclose()
    return tls_version


async def check_port(domain, port: int, timeout=5):
    try:
        with trio.move_on_after(timeout) as cs:
            s = await trio.open_tcp_stream(domain, port)
            await s.aclose()

        if cs.cancelled_caught:
            raise NetworkError(
                f'Connection to {domain}:{port} timed out after {timeout} seconds')

    except socket.error as e:
        raise NetworkError(f"Could not connect to {domain}:{port}: {e}")
