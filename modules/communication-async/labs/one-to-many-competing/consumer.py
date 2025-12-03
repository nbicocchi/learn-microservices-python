import pika
import time
import random

RABBIT_URL = "amqp://guest:guest@localhost/"

exchange_name = "app.events"
routing_key = "event.#"

def handle_message(ch, method, properties, body):
    print(f"[SYNC] Received {body.decode()}")
    time.sleep(random.uniform(0.1, 0.2))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    params = pika.URLParameters(RABBIT_URL)
    connection = pika.BlockingConnection(params)
    ch = connection.channel()

    # declare exchange
    ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

    # declare queue
    result = ch.queue_declare("events.queue", durable=True)
    print(f"Temporary exclusive queue '{result.method.queue}' declared")
    actual_queue_name = result.method.queue

    # bind queue to exchange
    ch.queue_bind(exchange=exchange_name, queue=actual_queue_name, routing_key=routing_key)
    print(f"Queue '{actual_queue_name}' bound to exchange '{exchange_name}' with routing key '{routing_key}'")

    print(" [*] Waiting for messages (SYNC consumer)…")
    ch.basic_consume(queue=actual_queue_name, on_message_callback=handle_message)
    ch.start_consuming()

if __name__ == "__main__":
    main()
