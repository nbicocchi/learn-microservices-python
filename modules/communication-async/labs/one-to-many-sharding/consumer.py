import pika
import json
import time
import random
import argparse

RABBIT_URL = "amqp://guest:guest@localhost/"
exchange_name = "app.events"

def handle_message(ch, method, properties, body, shard_id):
    message = json.loads(body)
    print(f"[Shard {shard_id}] Received UUID {message['id']} - {message['message']}")
    time.sleep(random.uniform(0.1, 0.2))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    parser = argparse.ArgumentParser(description="Shard-based RabbitMQ consumer")
    parser.add_argument("--shard", type=int, required=True, help="Shard ID for this consumer")
    args = parser.parse_args()

    shard_id = args.shard
    queue_name = f"shard-{shard_id}.queue"

    params = pika.URLParameters(RABBIT_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # declare exchange
    ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

    # declare and bind shard queue
    ch.queue_declare(queue=queue_name, durable=True)
    ch.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=f"shard-{shard_id}")

    print(f"[*] Waiting for messages on shard {shard_id} (queue: {queue_name})")

    # use lambda to pass shard_id to the callback
    ch.basic_consume(
        queue=queue_name,
        on_message_callback=lambda ch, method, properties, body: handle_message(ch, method, properties, body, shard_id)
    )
    ch.start_consuming()

if __name__ == "__main__":
    main()
