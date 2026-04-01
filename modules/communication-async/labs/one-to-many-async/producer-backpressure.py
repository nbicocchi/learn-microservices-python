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

# pool di 10 UUID casuali
uuid_pool = [str(uuid.uuid4()) for _ in range(10)]

# parametri di concurrency
MAX_IN_FLIGHT = 10  # massimo messaggi non confermati

async def publish_message(exchange, message_body, in_flight_counter):
    """Pubblica un singolo messaggio e aspetta conferma dal broker (ack/nack)"""
    in_flight_counter[0] += 1
    try:
        message = aio_pika.Message(
            body=json.dumps(message_body).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        # publish con attesa conferma (publisher confirms)
        await exchange.publish(message, routing_key=ROUTING_KEY, mandatory=True)
    finally:
        in_flight_counter[0] -= 1

async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    async with connection:
        # abilitare publisher confirms
        channel = await connection.channel(publisher_confirms=True)
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

        in_flight = [0]  # messaggi non ancora confermati
        tasks = []

        for i in range(NUM_MESSAGES):
            message = {
                "id": random.choice(uuid_pool),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"event-{i}"
            }

            # se ci sono troppi messaggi in-flight → attendi prima di inviare
            while in_flight[0] >= MAX_IN_FLIGHT:
                await asyncio.sleep(0.05)

            task = asyncio.create_task(publish_message(exchange, message, in_flight))
            tasks.append(task)

        await asyncio.gather(*tasks)
        print(f"Sent {NUM_MESSAGES} messages with real backpressure via publisher confirms")

if __name__ == "__main__":
    asyncio.run(main())