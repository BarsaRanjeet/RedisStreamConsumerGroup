from connect import r

consumerName = "consumerRecover"
groupName = "service-1"
streamName = "scenario-3"

def process_message(id):
    r.hincrby(name="consumer",key=id,amount=1)

while True:

    pending = r.xpending(name="scenario-3",groupname=groupName)
    if pending.get("pending"):
        if int(pending.get("pending")) > 0:
            pending = r.xpending_range(name=streamName,groupname=groupName,min="-",max="+",count=10,consumername=pending.get("consumers")[0].get("name"))
            message_ids = list()
            for k in pending:
                id = k.get("message_id").decode("utf-8")
                message_ids.append(id)  
            claim = r.xclaim(name=streamName,groupname=groupName,consumername=consumerName,min_idle_time=2000,message_ids=message_ids) 
            if len(claim) > 0:
                for e in claim:
                    id = e[0].decode("utf-8")

                    # processing message
                    process_message(id)

                    # acknowledging
                    r.xack(streamName , groupName, id)