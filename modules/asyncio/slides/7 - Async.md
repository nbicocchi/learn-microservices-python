# Asynchronous programming

In computer science, we often need to manage multiple tasks to improve efficiency. This is where the concepts of concurrency and parallelism come into play. While often used interchangeably, they are fundamentally different.

## Concurrency

**Concurrency** is about dealing with many things at once. It's a way of structuring a program so that it can handle multiple tasks seemingly at the same time, even if the computer's processor can only execute one instruction at a time.

A good analogy is a single *juggler*. The juggler is only catching and throwing one ball at a time, but by quickly switching between them, they keep all the balls in the air. This is a context-switching process. In a single-core CPU, concurrent tasks take turns using the processor.

## Parallelism

**Parallelism** is about doing *many things at the same time*. This requires multiple processors or processor cores.

Think of a team of chefs in a kitchen. Each chef is working on a different dish simultaneously. This is true simultaneous execution. Parallelism is essential for CPU-bound tasks, which are operations that are limited by the speed of the CPU, such as heavy computations or complex calculations.

## Is concurrency better than parallelism?

Concurrency is different than parallelism. And it is better on specific scenarios that involve a lot of waiting. Because of that, it generally is a lot better than parallelism for web application development. But not for everything.

## Synchronous vs Asynchronous

* **Synchronous:**

  * A task **waits for an operation to complete** before moving on.
  * Example: Reading a file synchronously — the program blocks until the file is fully read.
  * Works naturally with **blocking code** and **preemptive concurrency** if multiple threads are used.
  * Can be inefficient for I/O-bound tasks because the CPU sits idle while waiting.

* **Asynchronous:**

  * A task **does not block while waiting**; it can yield control so other tasks can run.
  * Example: Using `async/await` in Python to read multiple files concurrently.
  * Works well with **cooperative concurrency**, where tasks voluntarily yield while waiting.
  * Ideal for **I/O-bound workloads** or high-latency operations (network, disk, database).

### Synchronous I/O

In this version, each `accept()` call is **blocking**.
The server waits indefinitely for a connection on **sock1**, and only after completing that interaction does it move to **sock2**.
This means the server can only handle one port at a time and becomes unresponsive on the other port until the current accept completes.

```python
...

print("Server listening on ports 9001 and 9002...")

while True:
    # This call BLOCKS: execution stops here until someone connects to port 9001
    print("Waiting for client on port 9001...")
    client1, addr1 = sock1.accept()
    print(f"Connection from {addr1} on port 9001")
    client1.send(b"Hello from server port 9001!\n")
    client1.close()

    # Only after finishing with port 9001 does the server handle port 9002
    print("Waiting for client on port 9002...")
    client2, addr2 = sock2.accept()
    print(f"Connection from {addr2} on port 9002")
    client2.send(b"Hello from server port 9002!\n")
    client2.close()
```

```mermaid
sequenceDiagram
    participant Server
    participant Port9001
    participant Port9002

    Server->>Port9001: accept() (blocks)
    Note right of Server: Server is stuck here<br>until a client connects
    Port9001-->>Server: Client connects
    Server->>Port9001: Handle request

    Server->>Port9002: accept() (blocks)
    Note right of Server: Now stuck waiting<br>for client on port 9002
    Port9002-->>Server: Client connects
    Server->>Port9002: Handle request

    Server->>Server: Loop repeats

```

---

### Asynchronous I/O

Instead of blocking on a single `accept()`, it uses `select()` to wait for **any** socket to become readable.
This allows the server to react to whichever port receives a connection first, making it responsive on both ports concurrently.

```python
...

print("Server listening on ports 9001 and 9002...")

while True:
    # select() waits until *any* socket is ready.
    # It does NOT block on a specific socket.
    ready_to_read, _, _ = select.select(sockets, [], [], 1)

    # Handle all sockets that have incoming connections
    for s in ready_to_read:
        client, addr = s.accept()
        print(f"Connection from {addr} on port {s.getsockname()[1]}")
        client.send(b"Hello from server!\n")
        client.close()
```

```mermaid
sequenceDiagram
    participant Server
    participant Port9001
    participant Port9002

    Server->>Server: select(sock1, sock2)
    Note right of Server: Server waits for<br>any socket to be ready

    alt Port9001 ready first
        Port9001-->>Server: fd becomes readable
        Server->>Port9001: accept() + handle client
    end

    Server->>Server: select(sock1, sock2)

    alt Port9002 ready first
        Port9002-->>Server: fd becomes readable
        Server->>Port9002: accept() + handle client
    end

    Server->>Server: Loop repeats
```

## Limits of parallel blocking I/O (One thread per request)

```python
import time

def db_query(name, duration):
    print(f"Query {name} started")
    time.sleep(duration)  # Simulate blocking DB call
    print(f"Query {name} finished")

# Two database queries executed sequentially
db_query("A", 2)
db_query("B", 3)
print("All queries done")
```

* In traditional blocking code, each incoming request is handled by a dedicated thread.
* While the thread waits (e.g., for a database query, HTTP call, or file I/O), it **cannot do anything else**.
* Microservices often handle **thousands of concurrent requests**, so:

    * Blocking threads consume memory and CPU.
    * Thread pools can become exhausted, leading to request rejection or increased latency.

**Example:**

```text
Thread pool: 200 threads
Requests per second: 500
If each request blocks 2 seconds → threads saturate → new requests must wait → slow response
```


## Asyncio library

Python's asyncio library, introduced in Python 3.4, provides a framework for writing concurrent code using the asynchronous paradigm (in particular using an event loop). The `async` and `await` keywords are the core components of this framework.

`async` is used to define a function as a **coroutine**. A coroutine is a special type of generator that can be *paused and resumed*. When you call an async function, it does **not execute immediately**, but it **returns a coroutine object**.

```py
async def fetch_data():
    # This is a coroutine
    ...
```

`await` is used *within* an async function to pause its execution and "await" the result of another coroutine. When an await is encountered, the control is *yielded back* to the **event loop** (the asyncio scheduler), allowing other tasks to run. Once the awaited task is complete, the event loop resumes the coroutine from where it left off.


```py
async def main():
    data = await fetch_data() # Execution pauses here
    ...
```

Together, `async` and `await` enable a style of programming called cooperative multitasking. The coroutines voluntarily yield control to each other, allowing the program to perform multiple operations concurrently on a single thread without blocking. This is an excellent solution for building high-performance, scalable applications that deal with many I/O-bound operations, such as web servers and network clients.


### Event loop

The **event loop** is a fundamental component of asynchronous programming in Python. It's essentially a scheduler or an orchestrator for your asynchronous tasks. The event loop continuously monitors coroutines for completion and dispatches new tasks as soon as the CPU becomes available.

Here's how it works:

1. A task starts, and if it encounters an I/O-bound operation (e.g., waiting for a network request to complete), it awaits the result.
2. When a task awaits, it temporarily yields control back to the event loop.
3. The event loop then looks for other tasks that are ready to run and dispatches one of them.
4. Once the original I/O operation is complete, the event loop is notified. It then puts the original task back on the schedule to continue its execution from where it left off.

This continuous cycle allows the program to remain responsive and perform multiple operations concurrently on a single thread. The event loop is a core mechanism that prevents the program from being idle while waiting for slow operations to finish.


### Why asyncio?

The **Global Interpreter Lock** (GIL) is a mutex (mutual exclusion lock) that protects access to Python objects, preventing multiple native threads from executing Python bytecode at the same time. This means that even on a multi-core processor, only one thread can execute Python code at any given moment.

The GIL was implemented to simplify memory management and prevent race conditions when multiple threads try to access the same memory objects. While it's a simplification, the main takeaway is that the GIL is a bottleneck for CPU-bound tasks in multi-threaded applications. If your program is crunching numbers, adding more threads won't make it faster because they will all be fighting for the GIL.


> [!NOTE]
> GIL will be removed in version 3.14!

Since the GIL is a limitation for multi-threading, asyncio is considered a good way to work around it. Given that asyncio operates on a single thread, it completely sidesteps the GIL's limitations. When an async function awaits an I/O operation, it releases the event loop, allowing another coroutine to run. Since no Python bytecode is being executed during the wait, the GIL is not a concern. The program is not blocked; it's just switching between tasks that are all waiting for external resources.


### What is `async`?

* The `async` keyword is used to **define an asynchronous function**, also called a **coroutine** in Python.
* Calling an `async` function **does not immediately run it**. Instead, it returns a **coroutine object**, which represents the work that can be scheduled on an event loop.

**Example:**

```python
import asyncio

async def say_hello():
    print("Hello")
```

* `say_hello()` here is asynchronous.
* If you call `say_hello()` directly, it **does not execute yet**; it returns a coroutine object:

```python
coro = say_hello()
print(coro)
# <coroutine object say_hello at 0x...>
```

* To actually run it, you need to **schedule it on an event loop**, e.g., with `asyncio.run()`.

---

### What is `await`?

* The `await` keyword **pauses the coroutine until another async operation finishes**.
* Unlike `time.sleep()` (blocking), `await` is **non-blocking**: it tells the event loop, “I’m waiting, you can run other tasks in the meantime.”

**Example:**

```python
import asyncio

async def wait_and_print():
    print("Start waiting")
    await asyncio.sleep(2)  # Non-blocking sleep
    print("Done waiting")

asyncio.run(wait_and_print())
```

* Output:

```
Start waiting
(wait 2 seconds without blocking)
Done waiting
```

* During the `await asyncio.sleep(2)`, the event loop could run **other coroutines**.

---

### How `async` and `await` work together

* `async` defines a **coroutine**.
* `await` tells Python to **pause this coroutine until the awaited coroutine completes**, allowing other tasks to run in the meantime.

**Example with multiple tasks:**

```python
import asyncio

async def task(name, duration):
    print(f"{name} started")
    await asyncio.sleep(duration)  # Non-blocking
    print(f"{name} finished")

async def main():
    await asyncio.gather(
        task("A", 2),
        task("B", 3)
    )

asyncio.run(main())
```

* `task("A")` and `task("B")` start almost simultaneously.
* Total runtime ≈ 3 seconds, not 5, because `await` allows overlapping execution.


## HTTP Messages handling approaches

### Synchronous Handler with Threads
**Definition:** Each request is handled in a **dedicated thread** and blocks until the operation completes.  

**Technical Details / Limitations:**
- **Blocking I/O:** CPU waits while DB or HTTP call executes  
- **Thread-per-request model:** Memory usage grows linearly with concurrent requests  
- **Limited scalability:** Only as many simultaneous requests as available threads  
- **Poor support for long-lived connections:** Each WebSocket/SSE consumes a thread  
- **High latency under load:** Slow downstream calls block processing  

```java
@GetMapping("/items")
public List<String> getItems() {
    try { Thread.sleep(1000); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    return List.of("Item1","Item2","Item3");
}
```

```java
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import java.util.List;

@Path("/items")
public class ItemResource {

    @GET
    public List<String> getItems() {
        try { Thread.sleep(1000); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return List.of("Item1","Item2","Item3");
    }
}
```

```python
from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/items-sync")
def get_items_sync():
    time.sleep(1)  ## blocks thread
    return ["Item1","Item2","Item3"]
```

```python
from flask import Flask
import time

app = Flask(__name__)

@app.route("/items")
def get_items():
    time.sleep(1)  ## blocks thread
    return ["Item1","Item2","Item3"]
```

```python
import time
from django.http import JsonResponse

def items_view(request):
    time.sleep(1)  ## blocks thread
    return JsonResponse(["Item1","Item2","Item3"], safe=False)
```

---

### Asynchronous Handler
**Definition:** Tasks **yield control while awaiting I/O**; the **event loop** schedules pending operations.  

**Benefits:**
- Single thread handles thousands of connections efficiently  
- Better CPU utilization  
- Supports long-lived connections (WebSockets, streaming)  
- Reduces latency spikes under load  

```java
@GetMapping("/items")
public Mono<List<String>> getItems() {
    return Mono.delay(Duration.ofSeconds(1))
               .map(ignore -> List.of("Item1","Item2","Item3"));
}
```

```java
@Path("/items")
public class ItemResource {

    @GET
    public Uni<List<String>> getItems() {
        return Uni.createFrom().item(List.of("Item1","Item2","Item3"))
                  .onItem().delayIt().by(Duration.ofSeconds(1));
    }
}
```

```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/items-async")
async def get_items_async():
    await asyncio.sleep(1)  ## non-blocking
    return ["Item1","Item2","Item3"]
```

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
* or otherwise regulate

… the flow of data.

Without this regulation, systems become unstable.

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
- FastAPI docs: https://fastapi.tiangolo.com  
- Python asyncio: https://docs.python.org/3/library/asyncio.html  
- Spring WebFlux: https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html  
- Quarkus reactive guide: https://quarkus.io/guides/reactive  
- Reactive Streams spec: https://www.reactive-streams.org/
