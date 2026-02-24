# Observability in FastAPI

## Monitoring with Instrumentator

```py
from prometheus_fastapi_instrumentator import Instrumentator

# Metrics endpoint
Instrumentator().instrument(app).expose(app)
```

**Explanation:**

* `Instrumentator` automatically collects metrics from your application.
* It adds a middleware that intercepts all HTTP requests.
* No need to manually track response times or request counts.
* The metrics are exposed in a format compatible with monitoring systems.

> [!TIP] This is a simple way to add **observability** to microservices without modifying existing routes.

---

## What Metrics Are Collected?

The middleware gathers important runtime information:

* Total number of HTTP requests.
* Request duration (latency).
* Status codes (200, 404, 500, etc.).
* Endpoint and HTTP method.
* Error rates and slow requests.

These metrics help identify:

* Performance bottlenecks.
* Unstable endpoints.
* Service degradation.

> [!TIP] Observability is essential in distributed systems and cloud-native architectures.

---

## Metrics Endpoint

After calling `expose(app)`, FastAPI provides:

```
GET /metrics
```

---

## Integration with Monitoring Stack

Typical architecture:

1. The FastAPI service exposes `/metrics`.
2. Prometheus periodically scrapes the endpoint.
3. Metrics are stored in a time-series database.
4. Grafana visualizes dashboards and alerts.

This enables:

* Real-time monitoring.
* Alerting on failures or latency spikes.
* Capacity planning and scaling.

---

## Why Use It?

* Minimal configuration.
* Works with synchronous and asynchronous endpoints.
* Production-ready monitoring.
* Supports custom metrics and extensions.
* Aligns with DevOps and Site Reliability Engineering practices.

> [!TIP] Combine metrics with logs and traces for full observability.
