from click.testing import CliRunner
from unittest import mock

from eth.server import server
from eth import cli


def test_not_netstring():
    mock_socket = mock.Mock()
    mock_socket.recv.return_value = b"afsfjsij"

    handler = server.EthTCPHandler(mock_socket, ("localhost", 8000), None)
    handler.handle()


def test_parameters_redis():
    runner = CliRunner()
    result = runner.invoke(cli, ['server', '--use-redis'])
    assert result.exit_code != 0


def test_parameters_mysql():
    runner = CliRunner()
    result = runner.invoke(cli, ['server', '--use-mysql'])
    assert result.exit_code != 0
