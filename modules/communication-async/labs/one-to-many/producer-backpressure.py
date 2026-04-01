import pika
import json
import uuid
from datetime import datetime, timezone
import random
import time
from threading import Event

RABBIT_URL = "amqp://guest:guest@localhost/"

exchange_name = "app.events"
routing_key = "event.key"

# evento per messaggi non routabili
backpressure_event = Event()

def on_return(ch, method, properties, body):
    print("Message returned: cannot route. Applying backpressure...")
    backpressure_event.set()

def main():
    params = pika.URLParameters(RABBIT_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # dichiara exchange
    ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

    # abilita publisher confirms
    ch.confirm_delivery()

    # callback per messaggi non routabili
    ch.add_on_return_callback(on_return)

    # pool di UUID casuali
    uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

    for i in range(100):
        message = {
            "id": random.choice(uuid_pool),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"event-{i}"
        }
        body = json.dumps(message).encode("utf-8")

        while True:
            try:
                # publish con mandatory=True
                ch.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2),
                    mandatory=True
                )
                break  # messaggio inviato correttamente

            except pika.exceptions.ConnectionClosed:
                print("Connection closed, retrying...")
                time.sleep(0.1)
                conn = pika.BlockingConnection(params)
                ch = conn.channel()
                ch.confirm_delivery()
                ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)
                ch.add_on_return_callback(on_return)

        # applica backpressure solo se messaggio non routabile
        if backpressure_event.is_set():
            wait_time = 0.2 + random.random() * 0.3
            print(f"Backpressure applied, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            backpressure_event.clear()

    print("All messages sent safely with backpressure")
    conn.close()

if __name__ == "__main__":
    main()