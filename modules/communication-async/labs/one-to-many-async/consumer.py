import asyncio
import aio_pika
import random

RABBIT_URL = "amqp://guest:guest@localhost/"
EXCHANGE_NAME = "app.events"
ROUTING_KEY = "event.#"

async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"[ASYNC] Received {message.body.decode()}")
        # simulate async processing
        await asyncio.sleep(random.uniform(0.1, 0.2))

async def main():
    # connect to RabbitMQ
    connection = await aio_pika.connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()

        # declare topic exchange
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

        # declare a temporary exclusive queue
        queue = await channel.declare_queue("", exclusive=True)
        print(f"Temporary exclusive queue '{queue.name}' declared")

        # bind queue to exchange with routing key
        await queue.bind(exchange, ROUTING_KEY)
        print(f"Queue '{queue.name}' bound to exchange '{EXCHANGE_NAME}' with routing key '{ROUTING_KEY}'")

        # start consuming messages
        await queue.consume(handle_message)
        print(" [*] Waiting for messages (ASYNC consumer)…")

        # keep the consumer running
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
