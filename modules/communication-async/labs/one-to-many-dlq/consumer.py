import pika
import json
import random
import time

RABBIT_URL = "amqp://guest:guest@localhost/"

exchange_name = "app.events"
queue_name = "main.queue"
dlq_name = "dead.letter.queue"

def handle_message(ch, method, properties, body):
    message = json.loads(body)
    print(f"[MAIN] Received: {message}")
    time.sleep(0.1)

    # randomly reject some messages
    if random.random() < 0.3:
        print(f"[MAIN] Rejecting message {message['id']}")
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    params = pika.URLParameters(RABBIT_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # declare exchange
    ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

    # declare DLQ
    ch.queue_declare(queue=dlq_name, durable=True)

    # declare main queue with dead-letter exchange set
    ch.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",  # default exchange
            "x-dead-letter-routing-key": dlq_name  # route to DLQ
        }
    )
    print("[*] Waiting for messages on main queue")
    ch.basic_consume(queue=queue_name, on_message_callback=handle_message)
    ch.start_consuming()

if __name__ == "__main__":
    main()
