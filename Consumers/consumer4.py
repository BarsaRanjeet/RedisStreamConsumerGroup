from connect import r

consumerName = "consumer4"
groupName = "service-1"
streamName = "scenario-3"

def process_message(id):
    r.hincrby(name="consumer",key=id,amount=1)

lastId = '0-0'
check_backlog = True

while True:
    myid = ""
    if check_backlog:
        myid = lastId
    else:
        myid = '>'
    
    consumer = r.xreadgroup(groupName, consumerName, {streamName: myid},block=2000,count=10)
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
            r.xack(streamName , groupName, id)

            lastId = id