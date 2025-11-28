from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from prometheus_fastapi_instrumentator import Instrumentator
from api.product_controller import router as product_router
from core.database import init_db, engine
from models.product import Product
from schemas.product import ProductCreate
from core.config import settings
from api.health_controller import health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB
    init_db()

    # Sample products to preload
    sample_products = [
        ProductCreate(uuid="uuid-1", name="Widget", weight=1.2),
        ProductCreate(uuid="uuid-2", name="Gadget", weight=0.8),
        ProductCreate(uuid="uuid-3", name="Thingamajig", weight=2.5),
        ProductCreate(uuid="uuid-4", name="Doohickey", weight=3.0),
        ProductCreate(uuid="uuid-5", name="Contraption", weight=2.0),
    ]

    # Insert sample products if DB is empty
    with Session(engine) as session:
        existing = session.exec(select(Product)).first()
        if not existing:
            for p in sample_products:
                product = Product(uuid=p.uuid, name=p.name, weight=p.weight)
                session.add(product)
            session.commit()

    yield
    # Shutdown: nothing to do

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
