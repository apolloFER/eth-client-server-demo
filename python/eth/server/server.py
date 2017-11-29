import time
import click
import socket
import socketserver
import datetime
import hashlib
import logging

from . import conn
from ..util import netstring


SOCK_TIMEOUT = 1

logger = logging.getLogger(__name__)


class EthTCPHandler(socketserver.BaseRequestHandler):
    use_redis = False
    use_mysql = False

    def __init__(self, request, client_address, server):
        self.hash_value = None
        super(EthTCPHandler, self).__init__(request, client_address, server)

    @staticmethod
    def _redis_hash_timestamp_key():
        return "eth:hashes"

    @staticmethod
    def _redis_client_count_key():
        return "eth:ip_addresses"

    def _calculate_hash(self, payload: str):
        if not self.hash_value:
            hasher = hashlib.sha256()
            hasher.update(payload.encode())
            self.hash_value = hasher.hexdigest()

            logger.debug("Calculated hash is %s", self.hash_value)

    def setup(self):
        logger.debug("Connection established from %s", self.client_address[0])
        self.request.settimeout(SOCK_TIMEOUT)

    def handle(self):
        decoder = netstring.Decoder()
        client_ip, client_port = self.client_address

        while True:
            try:
                data = self.request.recv(1024)

                logger.debug("Received raw data %s", data.decode())

                decoded_data = list(decoder.feed(data))
                if decoded_data:
                    payload = decoded_data[0]
                    logger.debug("Received decoded data %s", payload.decode())
                    break
                if not data:
                    raise socket.error("timed out")
            except socket.error:
                logger.error("Error while receiving data from %s:%d", client_ip, int(client_port))
                return
            except netstring.DecoderError:
                logger.error("Error while decoding data from %s:%d", client_ip, int(client_port))
                return

        payload = payload.decode()

        print("DATA - {}:{} - {}".format(client_ip, client_port, payload.replace("\n", "\\n")))

        if self.use_redis:
            self.store_redis_data(payload, client_ip)

        if self.use_mysql:
            self.store_mysql_data(payload)

    def store_redis_data(self, payload: str, client_ip: str):
        self._calculate_hash(payload)

        if not conn.redis_conn.zscore(self._redis_hash_timestamp_key(), self.hash_value):
            conn.redis_conn.zadd(self._redis_hash_timestamp_key(), self.hash_value, datetime.datetime.now().timestamp())
            conn.redis_conn.hincrby(self._redis_client_count_key(), client_ip, 1)
            logger.debug("Stored data to Redis")

    def store_mysql_data(self, payload: str):
        session = conn.db_session()
        self._calculate_hash(payload)

        try:
            if not session.query(conn.EthereumData).filter_by(hash=self.hash_value).first():
                value = conn.EthereumData(hash=self.hash_value, payload=payload)
                session.add(value)
                session.commit()
                session.close()
        except:
            logger.error("Error while inserting data to SQL - %s", self.hash_value)


@click.command()
@click.option("--redis-host", type=str)
@click.option("--redis-port", type=int)
@click.option("--redis-db", type=int)
@click.option("--mysql-host", type=str)
@click.option("--mysql-user", type=str)
@click.option("--mysql-pass", type=str)
@click.option("--mysql-db", type=str)
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=9999)
@click.option('--use-redis', is_flag=True)
@click.option('--use-mysql', is_flag=True)
def run_server(*args, **kwargs):
    """Run an Eth project server for receiving Ethereum block numbers."""

    if kwargs["use_redis"]:
        if kwargs["redis_host"] is None:
            raise click.BadParameter("--use-redis called without --redis-host")
        if kwargs["redis_port"] is None:
            raise click.BadParameter("--use-redis called without --redis-port")
        if kwargs["redis_db"] is None:
            raise click.BadParameter("--use-redis called without --redis-db")

        try:
            conn.connect_redis(host=kwargs["redis_host"],
                               port=kwargs["redis_port"],
                               db=kwargs["redis_db"])
        except ConnectionError:
            return

        EthTCPHandler.use_redis = True

    if kwargs["use_mysql"]:
        if kwargs["mysql_host"] is None:
            raise click.BadParameter("--use-mysql called without --mysql-host")
        if kwargs["mysql_user"] is None:
            raise click.BadParameter("--use-mysql called without --mysql-user")
        if kwargs["mysql_pass"] is None:
            raise click.BadParameter("--use-mysql called without --mysql-pass")
        if kwargs["mysql_db"] is None:
            raise click.BadParameter("--use-mysql called without --mysql-db")

        try:
            conn.connect_mysql(host=kwargs["mysql_host"],
                               user=kwargs["mysql_user"],
                               password=kwargs["mysql_pass"],
                               db=kwargs["mysql_db"])
        except ConnectionError:
            return

        EthTCPHandler.use_mysql = True

    with socketserver.TCPServer((kwargs["host"], kwargs["port"]), EthTCPHandler) as server:
        logger.debug("Launching server %s on port %d", kwargs["host"], kwargs["port"])
        server.serve_forever()


