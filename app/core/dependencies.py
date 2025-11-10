from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from ..models.domain import Base

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Simple auto-create; replace with Alembic for migrations in real deployments.
    Base.metadata.create_all(bind=engine)
