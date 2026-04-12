# PRODUCER SENDS MESSAGE OR TASK INTO QUEUE
from redis import Redis
from rq import Queue

# Create Redis connection
redis_conn = Redis(
    host="localhost",
    port=6379,
    db=0
)

# Create Queue
queue = Queue(
    "default",
    connection=redis_conn,
    default_timeout=None
)



'''# Create Redis connection and Queue
queue = Queue("default",connection=Redis(
    host = "localhost",
    port = 6379,
    db = 0),
    default_timeout=None
)'''
