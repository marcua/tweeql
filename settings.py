from private_settings import *

# Running in debug mode, the system prints a lot more information
DEBUG = True

REDIS_HOSTNAME = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

POLL_TIME = .25 # seconds between looking for new content in redis
MAX_MESSAGES = 10000

TWEET_GROUP_ID = 'tweet-group-id'
TO_INDEX = 'tweet-groups-to-index'
CONSUMED_INDICES = 'tweet-groups-consumed'
