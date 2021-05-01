package main

import (
	"context"
	"fmt"
	"log"

	"github.com/go-redis/redis/v8"
)

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

func Producer(ctx context.Context, client *Database, producer int) {

	values := make(map[string]interface{})
	i := 1
	for {
		values["producer"] = producer
		values["serial"] = i
		inc := client.Client.Incr(ctx, "producer"+fmt.Sprint(producer))
		if inc.Val() > 0 {
			client.Client.XAdd(ctx, &redis.XAddArgs{Stream: "messageStream", ID: "*", Values: values})
		}
		i += 1
		// time.Sleep(time.Millisecond * 1000)
	}
}

func main() {
	client, err := Connect()
	ctx := context.Background()
	if err != nil {
		log.Fatal("Error in redis")
	}
	fmt.Println(client.Client.Ping(ctx))
	for i := 1; i <= 1000; i++ {
		go Producer(ctx, client, i)
	}
	fmt.Scanln()
	client.Client.Close()
}
