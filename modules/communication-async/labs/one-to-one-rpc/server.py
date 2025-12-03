# rpc_server_topic.py
import pika
import json
import time

RABBIT_URL = "amqp://guest:guest@localhost/"
EXCHANGE = "rpc.topic"
REQUEST_KEY = "rpc.request"

def on_request(ch, method, props, body):
    request = json.loads(body)
    print(f"[RPC SERVER] Received: {request}")

    # simulate work
    time.sleep(1)
    response = {"result": request["value"] * 2}

    # reply routing key: rpc.reply.<client-id>
    reply_key = f"rpc.reply.{props.correlation_id}"

    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key=reply_key,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=json.dumps(response).encode()
    )

    ch.basic_ack(method.delivery_tag)
    print(f"[RPC SERVER] Replied to {reply_key} with: {response}")

def main():
    params = pika.URLParameters(RABBIT_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.exchange_declare(EXCHANGE, "topic", durable=True)

    # queue for requests
    ch.queue_declare("rpc.server.queue", durable=False)
    ch.queue_bind("rpc.server.queue", EXCHANGE, REQUEST_KEY)

    print("[RPC SERVER] Waiting for RPC calls...")

    ch.basic_qos(prefetch_count=1)
    ch.basic_consume("rpc.server.queue", on_request)

    ch.start_consuming()

if __name__ == "__main__":
    main()
