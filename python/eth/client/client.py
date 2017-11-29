import requests
import logging
import socket
import click
import time
import json

from string import Template
from ..util import netstring


class EthConnectionError(Exception):
    pass


logger = logging.getLogger(__name__)


SOCK_TIMEOUT = 1
PAYLOAD = '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":0}'
HEADERS = {'content-type': 'application/json'}
URL = "https://mainnet.infura.io/"
TEMPLATE = """<!doctype html>
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>Ethereum Current Block Number</title>
        <meta name="description" content="eth current block">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h2>Current Ethereum Block Number</h2>
        <p>$block_num</p>
    </body>
</html>"""


@click.command()
@click.option("--host", type=str, required=True)
@click.option("--port", type=int, required=True)
def run_client(*args, **kwargs):
    """Fetch the current Ethereum block number and send it to an Eth project server."""

    logger.debug("Launching client with server %s on port %d", kwargs["host"], kwargs["port"])

    eth_current_block = None

    while True:
        try:
            eth_new_block = get_current_block()
            if eth_new_block != eth_current_block:
                logger.debug("Block number has changed, sending to server")
                html = create_html(eth_new_block)
                send_html(kwargs["host"], kwargs["port"], html)
                eth_current_block = eth_new_block
                logger.debug("Block number sent to server")
        except EthConnectionError:
            logger.warning("Issue with sending current batch, moving to next!")
        except TypeError:
            logger.warning("Issue with type of response received!")
        finally:
            time.sleep(5)


def get_current_block():
    logger.debug("Fetching current block number from Eth mainnet")

    try:
        response = requests.post(url=URL, data=PAYLOAD, headers=HEADERS).json()
    except requests.ConnectionError:
        logger.info("Could not connect to Eth backend")
        raise EthConnectionError("Could not connect to Eth backend")
    except json.JSONDecodeError:
        logger.info("Malformed response")
        raise EthConnectionError("Malformed response")

    cur_block = int(response["result"], 16)

    logger.debug("Received current block from mainnet - %d", cur_block)

    return cur_block


def create_html(block_num: int):
    if not isinstance(block_num, int):
        logger.error("Expecting int, received %s", str(type(block_num)))
        raise TypeError("Expecting int, received " + str(type(block_num)))

    template = Template(TEMPLATE)
    html = template.substitute(block_num=block_num)

    logger.debug("Generating HTML")

    return html


def send_html(host: str, port: int, html: str):
    try:
        payload = netstring.encode(html.encode())
    except AttributeError:
        logger.error("Data has to be a string.")
        raise EthConnectionError("Data has to be a string.")

    logger.debug("Connecting to server %s:%d", host, port)
    s = None

    try:
        s = socket.socket()

        s.settimeout(SOCK_TIMEOUT)
        s.connect((host, port))

        s.sendall(payload)
    except socket.error:
        logger.info("Error connecting to server %s:%d", host, port)
        raise EthConnectionError("Error connecting to server.")
    except TypeError:
        logger.error("Port has to be an int")
        raise EthConnectionError("Port has to be an int")
    finally:
        if s:
            s.close()
        logger.debug("Data sent to server")
