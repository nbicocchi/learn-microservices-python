import pika
import json
import uuid
from datetime import datetime, timezone
import random

RABBIT_URL = "amqp://guest:guest@localhost/"

params = pika.URLParameters(RABBIT_URL)
conn = pika.BlockingConnection(params)
ch = conn.channel()

exchange_name = "app.events"
routing_key = "event.key"
queue_name = "events.queue"  # e.g., "events.queue" or None

# declare exchange
ch.exchange_declare(
    exchange=exchange_name,
    exchange_type="topic",
    durable=True
)

# declare queue
ch.queue_declare(queue=queue_name, durable=True)
ch.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
print(f"Queue '{queue_name}' declared and bound to exchange '{exchange_name}' with routing key '{routing_key}'")

# create a pool of 10 random UUIDs
uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

# publish messages with UUID from pool, timestamp, and string
for i in range(100):
    message = {
        "id": random.choice(uuid_pool),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"event-{i}"
    }

    ch.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(message).encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2  # persistent messages
        )
    )

print("Sent 100 structured messages to exchange")
conn.close()
