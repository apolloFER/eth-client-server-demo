import time
import click
import logging

from eth import server
from eth import client


def init_logging(verbose: bool):
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)

    handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
@click.option("--wait", type=int, default=0)
def cli(verbose: bool, wait: int):
    """Eth project client and server implementation in Python.

    Go implementation of a client and server that communicate via TCP connections.
    Compatible with the Go version of client and server.
    """
    init_logging(verbose)

    # Wait for other services to be ready
    time.sleep(wait)


@click.command()
@click.argument("section", required=False)
@click.pass_context
def help(ctx, section):
    """Print help about a command."""
    if section == "server":
        with click.Context(server.run_server) as ctx:
            click.echo(server.run_server.get_help(ctx))
    elif section == "client":
        with click.Context(client.run_client) as ctx:
            click.echo(client.run_client.get_help(ctx))
    elif section != "help":
        click.echo(ctx.parent.get_help())
        click.echo("Error: Command {} does not exist.".format(section))
    else:
        click.echo(ctx.parent.get_help())


cli.add_command(help)
cli.add_command(server.run_server, name="server")
cli.add_command(client.run_client, name="client")


def main():
    cli(obj={}, auto_envvar_prefix="ETH")
