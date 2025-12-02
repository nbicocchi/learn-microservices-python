from fastapi import APIRouter
from core.database import get_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Simple health check
def simple_check() -> bool:
    return True

# Database health check
def db_check() -> bool:
    try:
        # get the session generator
        session_gen = get_session()
        session = next(session_gen)   # get the session object
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except SQLAlchemyError as e:
        print(e)
        return False  # fastapi-health will report 503 if any check returns False

health_router = APIRouter()

@health_router.get("/health")
def health_status():
    results = {
        "simple": simple_check(),
        "db": db_check(),
    }
    return results
