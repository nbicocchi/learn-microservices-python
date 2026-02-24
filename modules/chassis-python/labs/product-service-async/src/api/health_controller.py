from fastapi import APIRouter
from core.database import get_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

health_router = APIRouter()


# --- Simple health check ---
def simple_check() -> bool:
    return True


# --- Async database health check ---
async def db_check() -> bool:
    try:
        # get an async session from the generator
        async for session in get_session():
            await session.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError as e:
        print("DB health check failed:", e)
        return False


# --- Health endpoint ---
@health_router.get("/health")
async def health_status():
    results = {
        "simple": simple_check(),
        "db": await db_check(),
    }
    return results