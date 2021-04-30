import redis
# Connect to a local redis instance
r = redis.Redis(host='127.0.0.1', port=6379, db=0)