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

# pool of 10 random UUIDs
uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

# initial concurrency parameters
INITIAL_CONCURRENCY = 5
MAX_CONCURRENCY = 20
MIN_CONCURRENCY = 1

async def publish_message(semaphore, exchange, message_body, in_flight_counter):
    async with semaphore:
        in_flight_counter[0] += 1
        try:
            message = aio_pika.Message(
                body=json.dumps(message_body).encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await exchange.publish(message, routing_key=ROUTING_KEY)
        finally:
            in_flight_counter[0] -= 1

async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

        concurrency = INITIAL_CONCURRENCY
        semaphore = asyncio.Semaphore(concurrency)
        in_flight = [0]  # mutable counter

        tasks = []

        for i in range(NUM_MESSAGES):
            message = {
                "id": random.choice(uuid_pool),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"event-{i}"
            }

            task = asyncio.create_task(publish_message(semaphore, exchange, message, in_flight))
            tasks.append(task)

            # dynamically adjust concurrency every few messages
            if i % 5 == 0:
                # if all slots are currently occupied → broker likely busy
                if in_flight[0] >= concurrency and concurrency > MIN_CONCURRENCY:
                    concurrency = max(MIN_CONCURRENCY, concurrency / 2)
                    semaphore = asyncio.Semaphore(concurrency)
                    print(f"Backpressure detected → reducing concurrency to {concurrency}")
                # if many slots are free → increase concurrency
                elif in_flight[0] < concurrency // 2 and concurrency < MAX_CONCURRENCY:
                    concurrency = min(MAX_CONCURRENCY, concurrency * 2)
                    semaphore = asyncio.Semaphore(concurrency)
                    print(f"Broker idle → increasing concurrency to {concurrency}")

        await asyncio.gather(*tasks)
        print(f"Sent {NUM_MESSAGES} messages with corrected dynamic backpressure")

if __name__ == "__main__":
    asyncio.run(main())
