from flask import Flask, Response, redirect
from sqlalchemy.orm.exc import NoResultFound
from tabulate import tabulate

try:
    import conn
except ImportError:
    from . import conn

import logging
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", "6379")
redis_db = os.environ.get("REDIS_DB", "0")

mysql_host = os.environ.get("MYSQL_HOST", "localhost")
mysql_port = os.environ.get("MYSQL_PORT", "3306")
mysql_user = os.environ.get("MYSQL_USER", "eth_user")
mysql_pass = os.environ.get("MYSQL_PASS", "eth_password")
mysql_db = os.environ.get("MYSQL_DB", "eth")


def init_logging():
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.WARNING)

    handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)


init_logging()

conn.connect_redis(redis_host, redis_port, redis_db)
conn.connect_mysql(mysql_host, mysql_port, mysql_user, mysql_pass, mysql_db)


@app.route('/')
def root():
    return redirect("_cat")


@app.route("/_cat")
def cat():
    response = "\n".join(["=^.^=", "/_cat/hashes", "/_cat/hashes/{hash}", "/_cat/clients"])
    return Response(response, content_type="text/plain")


@app.route("/_cat/hashes")
def hashes():
    hashes_pairs = conn.redis_conn.zrevrangebyscore("eth:hashes", "+inf", "-inf", start=0, num=100, withscores=True)
    header = ["hash", "timestamp"]
    response = tabulate(hashes_pairs, header, tablefmt="plain", floatfmt="10.4f")
    return Response(response, content_type="text/plain")


@app.route("/_cat/hashes/<target_hash>")
def fetch_hash(target_hash):
    session = conn.db_session()
    try:
        response = session.query(conn.EthereumData.payload).filter_by(hash=target_hash).one()
    except NoResultFound:
        response = "Hash not found"
    return Response(response, content_type="text/plain")


@app.route("/_cat/clients")
def clients():
    clients_count = conn.redis_conn.hgetall("eth:ip_addresses")
    headers = ["client", "count"]
    response = tabulate(clients_count.items(), headers, tablefmt="plain")
    return Response(response, content_type="text/plain")
