from fastapi import FastAPI
import requests
import httpx
import time

app = FastAPI()

TEST_URL = "https://postman-echo.com/delay/1"  # Simulates 1s network latency

# ---------------------------
# Blocking I/O endpoint
# ---------------------------
@app.get("/blocking")
def blocking_request():
    start = time.perf_counter()
    r = requests.get(TEST_URL)  # Blocks the thread
    elapsed = time.perf_counter() - start
    return {"status": r.status_code, "time": elapsed}


# ---------------------------
# Non-blocking async endpoint
# ---------------------------
@app.get("/async")
async def async_request():
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        r = await client.get(TEST_URL)  # Non-blocking
    elapsed = time.perf_counter() - start
    return {"status": r.status_code, "time": elapsed}
