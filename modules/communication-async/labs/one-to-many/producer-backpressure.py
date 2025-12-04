import pika
import json
import uuid
from datetime import datetime, timezone
import random
import time

RABBIT_URL = "amqp://guest:guest@localhost/"

params = pika.URLParameters(RABBIT_URL)
conn = pika.BlockingConnection(params)
ch = conn.channel()

exchange_name = "app.events"
routing_key = "event.key"

# declare exchange
ch.exchange_declare(
    exchange=exchange_name,
    exchange_type="topic",
    durable=True
)

# enable publisher confirms
ch.confirm_delivery()

# create a pool of 10 random UUIDs
uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

for i in range(100):
    message = {
        "id": random.choice(uuid_pool),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"event-{i}"
    }

    body = json.dumps(message).encode("utf-8")

    # publish with retry (backpressure) — only retry on exception
    retries = 0
    while True:
        try:
            # basic_publish does not return False, but will raise if broker disconnects
            ch.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            break  # success → exit while
        except (pika.exceptions.UnroutableError) as e:
            retries += 1
            print(f"Broker busy / connection issue, retrying... attempt {retries}")
            time.sleep(0.1)  # wait a bit before retrying

print("Sent messages safely with backpressure")
conn.close()
