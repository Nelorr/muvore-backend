from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread":False}
)

def init_db():
    """Creates database tables based on SQL metadata"""

    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI Dependency:Yields a fresh database per session then closes it"""
    
    with Session (engine) as session:
        yield session


