import redis

def get_redis():
    rd = redis.Redis(host="redis", port=6379, db=0)
    try:
        yield rd
    finally:
        pass