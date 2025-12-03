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
num_shards = 2  # number of consumers/shards

# declare exchange
ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

# create a pool of 10 UUIDs
uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

# declare queues (shards)
for i in range(num_shards):
    queue_name = f"shard-{i}.queue"
    ch.queue_declare(queue=queue_name, durable=True)
    ch.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=f"shard-{i}")

# publish messages
for i in range(100):
    u = random.choice(uuid_pool)
    shard = hash(u) % num_shards
    routing_key = f"shard-{shard}"

    message = {
        "id": u,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"event-{i}"
    }

    ch.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(message).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2)
    )

print("Sent 100 messages to exchange")
conn.close()
