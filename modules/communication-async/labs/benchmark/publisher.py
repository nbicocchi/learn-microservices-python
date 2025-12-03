import pika

RABBIT_URL = "amqp://guest:guest@localhost/"

params = pika.URLParameters(RABBIT_URL)
conn = pika.BlockingConnection(params)
ch = conn.channel()

exchange_name = "app.events"
routing_key = "event.key"

# declare exchange
ch.exchange_declare(exchange=exchange_name, exchange_type="topic", durable=True)

for i in range(100):
    ch.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=f"event-{i}".encode()
    )

print("Sent messages to exchange")
conn.close()
