import os
import json
import redis

from .constants import ENV_REDIS_CONF


conf = json.loads(os.getenv(ENV_REDIS_CONF, """{
    "host": "127.0.0.1",
    "port": 6379,
    "db": 1
}"""))
pool = redis.ConnectionPool(**conf)


def get_db():
    """Returns DB connection"""
    return redis.Redis(connection_pool=pool)
