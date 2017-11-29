from eth.client import client


def test_wrong_url():
    url = client.URL
    client.URL = "https://url.which.wrong.is/"
    try:
        client.get_current_block()
    except client.EthConnectionError:
        pass
    else:
        raise

    client.URL = url


def test_wrong_payload():
    payload = client.PAYLOAD
    client.PAYLOAD = PAYLOAD = '{"jsonrpc":"2.0","method":"eth_blockNumbesadfsafr","params":[],"id":0}'
    try:
        client.get_current_block()
    except client.EthConnectionError:
        pass
    else:
        raise AssertionError

    client.PAYLOAD = payload


def test_html_generation_none():
    try:
        client.create_html(None)
    except TypeError:
        pass
    else:
        raise AssertionError


def test_wrong_server_url():
    try:
        client.send_html("wrong_url", 8000, "values")
    except client.EthConnectionError:
        pass
    else:
        raise AssertionError


def test_port_string():
    try:
        client.send_html("localhost", "aaa", "values")
    except client.EthConnectionError:
        pass
    else:
        raise AssertionError

def test_wrong_data_sending():
    try:
        client.send_html("localhost", 8000, 122222)
    except client.EthConnectionError:
        pass
    else:
        raise AssertionError