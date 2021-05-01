# RedisStreamConsumerGroup

## _Content :-_
- Introduction
- Redis Stream
- Consumer Group
- Scenario
- Development
- Redis Stream consumer failure recovery

## Introduction:-
In a perfect world, both data producers and consumers work at the same pace, and there’s no data loss or data backlog. Unfortunately, that’s not the case in the real world. In nearly all real-time data stream processing use cases, producers and consumers work at different speeds. In addition, there is more than one type of consumer, each with its own requirements and processing pace. Redis Streams addresses this need with a feature set that gravitates heavily towards supporting the consumers.

## Redis Stream:-
Streams are like a log file, often implemented as a file open in append only mode, it implements additional, non mandatory features: a set of blocking operations allowing consumers to wait for new data added to a stream by producers, and in addition to that a concept called Consumer Groups.

## Consumer Group:-
The purpose of consumer groups is to scale out your data consumption process. A consumer group is a way to split a stream of messages among multiple clients to speed up processing or lighten the load for slower consumers. The main goal is to allow a group of clients to cooperate consuming a different portion of the same stream of messages.

## Scenario:-
There are four scenarios which need to understand before implementing consumer groups

### 1st scenario:
![1 to 1 scenario](https://lh3.googleusercontent.com/X67WkqncyD7myIfcgk26GFaJVAX-3YyvZg29dyQxc8gvT6RuR13Qu60rG5GYpbS3q3MN84cF2fRLJW6nAuWhqCECpSUCzz3kiZ40v20)


In this scenario there will be 1 producer which produces messages and 1 consumer which consumes message

### 2nd scenario:
![1 producer to consumer n](https://lh6.googleusercontent.com/fBI5S9P4T3UjSLHiPU2hGP2u4vOZoy4Dy3WOCkkaZwOamZrXMa-C8xL1cN3ZtGS9wA-JJLL58cFoSGWBlPJRX8q31qb0D4drIWzTkms)
In this scenario there will be 1 producer which produces messages and stores in redis database and number of consumers which consume messages at a time, if producer produces 800 messages per second then at a time 1 consumer will consume 200 messages that means redis will divide all messages equally to all the consumers 

### 3rd scenario:

![N producers to 1 consumer](https://lh5.googleusercontent.com/zk2SGZgzCqjIG2qhaL2nSb6uhFewwgiz0-7CJH-_WXl1c2qG4ZsfKp1HCyEdEZbepby65iuqlV4GCE8MGR0EvegvH9Bidmfvarp_weg)

In this scenario there will be many producers and single consumer all the  messages produced by producers will be consumed by single consumer 

### 4th scenario:

![Producer n to consumer n](https://lh5.googleusercontent.com/gB6NEId003-Y31bgXxO60JNMa8kiu8WVOH8bDVFaGKKEiFICh2Zi7Qk0nXon4aAM5mNKasE5hDOl0pwrNzJV6vDTOYN11pOp_31GJPwr-zuiBFK2lGI4d-LdZHxNhXb6ErkdIp-CJLrlzuRQ1Q)

In this scenario there will be many producers and many consumers, In practical terms, if we imagine having three consumers C1, C2, C3, and a stream that contains the messages 1, 2, 3, 4, 5, 6, 7 then what we want is to serve the messages according to the following diagram:

1 -> C1\
2 -> C2\
3 -> C3\
4 -> C1\
5 -> C2\
6 -> C3\
7 -> C1

In order to achieve this, Redis uses a concept called consumer groups.

A consumer group is like a pseudo consumer that gets data from a stream, and actually serves multiple consumers, providing certain guarantees:
- Each message is served to a different consumer so that it is not possible that the same message will be delivered to multiple consumers.
- Consumers are identified, within a consumer group, by a name, which is a case-sensitive string that the clients implementing consumers must choose. This means that even after a disconnect, the stream consumer group retains all the state, since the client will claim again to be the same consumer. However, this also means that it is up to the client to provide a unique identifier.
- Each consumer group has the concept of the first ID never consumed so that, when a consumer asks for new messages, it can provide just messages that were not previously delivered.
- Consuming a message, however, requires an explicit acknowledgment using a specific command. Redis interperts the acknowledgment as: this message was correctly processed so it can be evicted from the consumer group.
- A consumer group tracks all the messages that are currently pending, that is, messages that were delivered to some consumer of the consumer group, but are yet to be acknowledged as processed. Thanks to this feature, when accessing the message history of a stream, each consumer will only see messages that were delivered to it.

## Development:-
Before developing, one must learn and understand following commands
- [XADD](https://redis.io/commands/XADD) - Appends the specified stream entry to the stream at the specified key.
- [XGROUP](https://redis.io/commands/xgroup) - This command is used in order to manage the consumer groups associated with a stream data structure.
- [XREADGROUP](https://redis.io/commands/xreadgroup) - This command is a special version of the XREAD command with support for consumer groups.
- [XACK](https://redis.io/commands/xack) - The XACK command removes one or multiple messages from the Pending Entries List (PEL) of a stream consumer group.
- [XPENDING](https://redis.io/commands/xpending) - The XPENDING command is the interface to inspect the list of pending messages.
- [XCLAIM](https://redis.io/commands/xclaim) - This command changes the ownership of a pending message.

#### Producer (GoLang):
Redis Client
```
type Database struct {
	Client *redis.Client
}
func Connect() (*Database, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     "127.0.0.1:6379",
		Password: "",
		DB:       0,
	})
	return &Database{
		Client: client,
	}, nil
}
```
Creating producers using GOLang concurrency\
Producer produces 1000 messages at a time using goroutine
```
client, err := Connect()
ctx := context.Background()
for i := 1; i <= 1000; i++ {
	go Producer(ctx, client, i)
}
```
XADD to add messages in stream
```
func Producer(ctx context.Context, client *Database, producer int) {
	values := make(map[string]interface{})
	i := 1 // Initializing serial
	for {
		values["producer"] = producer
		values["serial"] = i
		
		// Adding to stream
		client.Client.XAdd(ctx, &redis.XAddArgs{Stream: "messageStream", ID: "*", Values: values})
		
		// After adding putting in sleep for 1sec
		time.Sleep(time.Millisecond * 1000)
	    
	    i += 1 // increment serial
	}
}
```
Every second producer will produce 1000 messages and will add to redis stream using xadd command  

#### Consumer (Python):
> Note : Before running consumer create consumer group using XGROUP command

Redis connection
```
import redis
# Connect to a local redis instance
redis = redis.Redis(host='127.0.0.1', port=6379, db=0)
```
Consuming messages using xreadgroup
```
lastId = '0-0'
check_backlog = True

# while True : For infinite loop
while True:
    myid = ""
    if check_backlog:
        myid = lastId
    else:
        myid = '>'
    
    # consuming messages
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
            redis.xack(streamName , groupName, id)

            lastId = id
```
As you can see the idea here is to start by consuming the history, that is, our list of pending messages. This is useful because the consumer may have crashed before, so in the event of a restart we want to re-read messages that were delivered to us without getting acknowledged. 
Once the history was consumed, and we get an empty list of messages, we can switch to use the > special ID in order to consume new messages.
## Redis Stream consumer failure recovery:-
The example above allows us to write consumers that participate in the same consumer group, each taking a subset of messages to process, and when recovering from failures re-reading the pending messages that were delivered just to them. However in the real world consumers may permanently fail and never recover. What happens to the pending messages of the consumer that never recovers after stopping for any reason?

Redis consumer groups offer a feature that is used in these situations in order to claim the pending messages of a given consumer so that such messages will change ownership and will be re-assigned to a different consumer. The feature is very explicit. A consumer has to inspect the list of pending messages, and will have to claim specific messages using a special command, otherwise the server will leave the messages pending forever and assigned to the old consumer.

In this scenario we can use following commands:
- XPENDING
- XCLAIM

The implementation is very simple
- A dedicated consumer to monitor the pending message
- Use special commands to distribute these messages to other consumers

XPENDING is a read-only command that will output the total number of all messages in the pending message in the specified group, the start ID, the end ID, and the number of messages in the pending message in each consumer. You can get more detailed information by specifying the start and end id and consumerName.

XCLAIM is used to change the ownership of the message
```
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
                    
                    # acknowledging
                    redis.xack(streamName , groupName, id)
```

