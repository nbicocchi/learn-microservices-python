import asyncio
import aio_pika
import random

RABBIT_URL = "amqp://guest:guest@localhost/"

exchange_name = "app.events"
routing_key = "event.key"

async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"[ASYNC] Received {message.body.decode()}")
        await asyncio.sleep(random.uniform(0.5, 2))
        print(f"[ASYNC] Done {message.body.decode()}")


async def main():
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()

    # declare exchange and queue
    exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
    queue = await channel.declare_queue("", exclusive=True)  # auto-delete temp queue

    # bind queue to exchange via routing KEY
    await queue.bind(exchange, routing_key)

    print(" [*] Waiting for messages (ASYNC consumer)…")

    await queue.consume(handle_message, no_ack=False)

    await asyncio.Future()  # keep the service running

if __name__ == "__main__":
    asyncio.run(main())
