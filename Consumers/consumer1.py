# importing module
from connect import redis

consumerName = "consumerRecover"    # defining consumer name
groupName = "service"               # defining group name
streamName = "messageStream"        # defining stream key name

def process_message(id):
    redis.hincrby(name="consumer",key=id,amount=1)

lastId = '0-0'
check_backlog = True

while True:
    myid = ""
    if check_backlog:
        myid = lastId
    else:
        myid = '>'
    
    consumer = redis.xreadgroup(groupName, consumerName, {streamName: myid},block=2000,count=10)
    try:
        if len(consumer[0][1]) == 0:
            check_backlog = False
    except:
        pass
    if len(consumer) > 0:
        for e in consumer[0][1]:
            id = e[0].decode("utf-8")

            # processing message
            process_message(id)

            # acknowledging
            # redis.xack(streamName , groupName, id)

            lastId = id