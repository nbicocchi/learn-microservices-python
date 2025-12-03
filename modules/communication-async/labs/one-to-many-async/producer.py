import asyncio
import aio_pika
import json
import uuid
from datetime import datetime, timezone
import random

RABBIT_URL = "amqp://guest:guest@localhost/"
EXCHANGE_NAME = "app.events"
ROUTING_KEY = "event.key"
NUM_MESSAGES = 100

# create a pool of 10 random UUIDs
uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

async def main():
    # connect to RabbitMQ
    connection = await aio_pika.connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()

        # declare exchange
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

        # publish messages asynchronously
        for i in range(NUM_MESSAGES):
            message = {
                "id": random.choice(uuid_pool),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"event-{i}"
            }

            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode("utf-8"),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=ROUTING_KEY
            )
            # optional: yield control to event loop
            await asyncio.sleep(0)

        print(f"Sent {NUM_MESSAGES} structured messages to exchange")

if __name__ == "__main__":
    asyncio.run(main())
