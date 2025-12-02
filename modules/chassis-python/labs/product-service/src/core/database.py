from sqlmodel import SQLModel, create_engine, Session
from core.config import settings

# Use DATABASE_URL from settings
engine = create_engine(settings.database_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
