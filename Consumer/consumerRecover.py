# importing module
from connect import redis

consumerName = "consumerRecover"    # defining consumer name
groupName = "service"               # defining group name
streamName = "messageStream"        # defining stream key name

# function for processing message 
def process_message(id):
    redis.hincrby(name="consumer",key=id,amount=1)

# while True : For infinite loop
while True:

    # Fetching details of pending message
    pending = redis.xpending(name=streamName,groupname=groupName)

    # checking if there any pending message
    if pending.get("pending"):

        if int(pending.get("pending")) > 0:

            # Fetching pending messages with count 10 
            pending = redis.xpending_range(name=streamName,groupname=groupName,min="-",max="+",count=10,consumername=pending.get("consumers")[0].get("name"))
            
            message_ids = list()
            for k in pending:
                id = k.get("message_id").decode("utf-8")
                message_ids.append(id)
            
            # changing ownership of messages to acknowledge
            claim = redis.xclaim(name=streamName,groupname=groupName,consumername=consumerName,min_idle_time=2000,message_ids=message_ids) 
            
            if len(claim) > 0:
                
                for e in claim:
                    
                    id = e[0].decode("utf-8")

                    # processing message
                    process_message(id)

                    # acknowledging
                    redis.xack(streamName , groupName, id)