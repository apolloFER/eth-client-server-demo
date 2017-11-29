import logging

import redis
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

redis_conn = None  # type: redis.Redis
sql_engine = None
db_session = None
logger = logging.getLogger(__name__)


def connect_redis(host: str, port: int, db: int):
    global redis_conn
    try:
        redis_conn = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        redis_conn.ping()
    except:
        logger.error("While connecting to Redis")
        raise ConnectionError("Unable to connect to Redis")
    finally:
        logger.debug("Establishing Redis connection to [%s:%d %d]", host, port, db)


_conn_str_template = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8'

Base = declarative_base()


class EthereumData(Base):
    __tablename__ = 'ethereum_data'

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), unique=True)
    payload = Column(Text)

    def __repr__(self):
        return "[EthereumBlock - hash %s - value %s]" % (self.hash, self.payload)


def connect_mysql(host: str, port: str, user: str, password: str, db: str):
    global sql_engine, db_session
    conn_str = _conn_str_template % (user, password, host, port, db)

    try:
        engine = create_engine(conn_str)
        Base.metadata.create_all(engine)
        db_session = sessionmaker(bind=engine)
    except:
        logger.error("While syncing tables to MySQL.")
        raise ConnectionError("Unable to connect to MySQL")
    finally:
        logger.debug("Establishing MySQL connection to [%s %s]", host, db)
