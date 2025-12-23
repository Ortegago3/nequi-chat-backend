from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# En SQLite se necesita check_same_thread=False para uso con FastAPI
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    """Base declarativa para modelos ORM."""
    pass

def init_db() -> None:
    """Crea tablas si no existen (sin migraciones)."""
    from app.models.message import Message  # import por side-effect de mapeo
    Base.metadata.create_all(bind=engine)
