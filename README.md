# RedisStreamConsumerGroup

## _Contents :-_
- Introduction
- Redis Stream
- Consumer Group
- Scenario
- Development
- Recovering from failures
- Conclusion

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


In this scenario there will be 1 producer which produces messages and 1 consumer which consumes message both 

### 2nd scenario:
![1 producer to consumer n](https://lh6.googleusercontent.com/fBI5S9P4T3UjSLHiPU2hGP2u4vOZoy4Dy3WOCkkaZwOamZrXMa-C8xL1cN3ZtGS9wA-JJLL58cFoSGWBlPJRX8q31qb0D4drIWzTkms)

In this scenario there will be 1 producer which produces messages and stores in redis database and number of consumers which consume messages at a time, if producer produces 800 messages per second then at a time 1 consumer will consume 200 messages that means redis will divide all messages equally to all the consumers 

### 3rd scenario:

![N producers to 1 consumer](https://lh5.googleusercontent.com/zk2SGZgzCqjIG2qhaL2nSb6uhFewwgiz0-7CJH-_WXl1c2qG4ZsfKp1HCyEdEZbepby65iuqlV4GCE8MGR0EvegvH9Bidmfvarp_weg)

In this scenario there will be many producers and single consumer all the  messages produced by producers will be consumed by single consumer 

### 4th scenario:

![Producer n to consumer n](https://lh5.googleusercontent.com/gB6NEId003-Y31bgXxO60JNMa8kiu8WVOH8bDVFaGKKEiFICh2Zi7Qk0nXon4aAM5mNKasE5hDOl0pwrNzJV6vDTOYN11pOp_31GJPwr-zuiBFK2lGI4d-LdZHxNhXb6ErkdIp-CJLrlzuRQ1Q)

In this scenario there will be many producers and many consumers, In practical terms, if we imagine having three consumers C1, C2, C3, and a stream that contains the messages 1, 2, 3, 4, 5, 6, 7 then what we want is to serve the messages according to the following diagram:
##### 1 -> C1
##### 2 -> C2
##### 3 -> C3
##### 4 -> C1
##### 5 -> C2
##### 6 -> C3
##### 7 -> C1
In order to achieve this, Redis uses a concept called consumer groups.

A consumer group is like a pseudo consumer that gets data from a stream, and actually serves multiple consumers, providing certain guarantees:

Each message is served to a different consumer so that it is not possible that the same message will be delivered to multiple consumers.



## Development:-

## Recovering From Failures:-

## Conclusion:-
