# Asynchronous programming

## Asynchronous Message Handling Models

### Synchronous, Single-Threaded Handler

* Fully sequential
* Processes *one message at a time*
* Simplest possible model
* Low throughput, no concurrency
* No threads, no async, no parallelism

```python
import pika
import time

def process_message(body):
    print(f"[SYNC] Processing: {body.decode()}")
    time.sleep(2)  # Blocking work
    print(f"[SYNC] Done: {body.decode()}")

def on_message(channel, method_frame, header_frame, body):
    process_message(body)  # Sequential processing
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='tasks')
channel.basic_consume(queue='tasks', on_message_callback=on_message)

print(" [*] Waiting for messages (sync, single-thread)...")
channel.start_consuming()
```

---

### Synchronous Handler with Threads

* Still blocking code, but each message handled in a separate thread
* Scheduling is **preemptive** (OS manages threads)
* Concurrency works well for I/O-bound tasks
* Limited by GIL for CPU-bound tasks

```python
import pika
import time
import threading

def process_message(body):
    print(f"[SYNC] Processing: {body.decode()}")
    time.sleep(2)  # Simulated I/O-bound work
    print(f"[SYNC] Done: {body.decode()}")

def on_message(channel, method_frame, header_frame, body):
    threading.Thread(target=process_message, args=(body,)).start()
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='tasks')
channel.basic_consume(queue='tasks', on_message_callback=on_message)

print(" [*] Waiting for messages (sync + threads)...")
channel.start_consuming()
```

### Asynchronous Handler

* Uses **cooperative concurrency**
* Each message is scheduled as an `async` task
* Excellent for I/O-bound workloads
* Very high throughput with minimal overhead
* No thread creation, no context-switching cost

```python
import asyncio
import aio_pika

async def process_message(body):
    print(f"[ASYNC] Processing: {body.decode()}")
    await asyncio.sleep(2)  # Non-blocking I/O
    print(f"[ASYNC] Done: {body.decode()}")

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("tasks")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    asyncio.create_task(process_message(message.body))
                    # Task scheduled, not blocking the consumer loop

if __name__ == "__main__":
    asyncio.run(main())
```

## Backpressure

Backpressure is a mechanism that **prevents fast producers from overwhelming slow consumers**.
* Producers can be extremely fast (network bursts, Kafka topics, sensor streams, parallel tasks).
* Consumers may be slow (I/O, database inserts, CPU-bound computation).

Without backpressure, the gap accumulates, leading to:

* Out-of-memory errors (buffers grow indefinitely)
* Queue explosion (message queues fill up)
* Crashes or unresponsiveness
* Microservice overload cascades
  (one slow service slows down upstream services too)

Example ("retry storm" or "death spiral"):
* A keeps sending requests at full speed
* B's queue grows (Kafka/RabbitMQ internal buffer, HTTP thread pool, DB connections)
* B reaches resource limits
* B slows down or crashes
* A interprets B’s slowness as errors
* Retries start happening (worsens traffic)
* Load balancers become saturated
* Entire service mesh becomes unstable


## Backpressure strategies
Whenever a producer is able to generate data faster than the consumer can process, there must be a strategy to:

* slow down
* temporarily store
* drop

```python
queue = asyncio.Queue(maxsize=10)  # max pending requests implies backpressure

async def producer(items):
    for item in items:
        await queue.put(item)  # waits if queue is full → backpressure

async def consumer():
    async with httpx.AsyncClient() as client:
        while True:
            item = await queue.get()
            await client.post("http://consumer-service/items", json=item)
            queue.task_done()

@app.post("/produce")
async def produce_endpoint(items: list):
    # start consumer task
    consumer_task = asyncio.create_task(consumer())
    await producer(items)
    await queue.join()  # wait until all items processed
    consumer_task.cancel()
    return {"status": "done"}
```
---

## References
