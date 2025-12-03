# rpc_client_topic.py
import pika
import uuid
import json

RABBIT_URL = "amqp://guest:guest@localhost/"
EXCHANGE = "rpc.topic"
REQUEST_KEY = "rpc.request"

class RpcClientTopic:
    def __init__(self):
        params = pika.URLParameters(RABBIT_URL)
        self.conn = pika.BlockingConnection(params)
        self.ch = self.conn.channel()

        self.ch.exchange_declare(EXCHANGE, "topic", durable=True)

        self.response = None

    def on_response(self, ch, method, props, body):
        if props.correlation_id == self.correlation_id:
            self.response = json.loads(body)

    def call(self, value):
        # create a unique correlation ID
        self.correlation_id = str(uuid.uuid4())
        reply_routing_key = f"rpc.reply.{self.correlation_id}"

        # create a reply queue for this request
        result = self.ch.queue_declare("", exclusive=True)
        reply_queue = result.method.queue
        self.ch.queue_bind(reply_queue, EXCHANGE, reply_routing_key)

        # subscribe to reply queue
        self.ch.basic_consume(
            queue=reply_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        # send request
        request = {"value": value}

        self.ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=REQUEST_KEY,
            body=json.dumps(request).encode(),
            properties=pika.BasicProperties(
                correlation_id=self.correlation_id
            )
        )

        print(f"[RPC CLIENT] Sent request {request}, waiting for reply...")

        # wait for response
        while self.response is None:
            self.conn.process_data_events()

        return self.response

if __name__ == "__main__":
    rpc = RpcClientTopic()

    print("[RPC CLIENT] Requesting 21 * 2")
    reply = rpc.call(21)
    print(f"[RPC CLIENT] RPC Reply: {reply}")
