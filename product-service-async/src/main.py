from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from api.health_controller import health_router
from api.product_controller import router as product_router
from core.config import settings
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()  # async DB init
    yield


# Create FastAPI
app = FastAPI(title="Product Service with DB", lifespan=lifespan)

# App endpoint
app.include_router(product_router)

# Health endpoint
app.include_router(health_router)

# Metrics endpoint
Instrumentator().instrument(app).expose(app)

# Run directly with uvicorn if needed
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
