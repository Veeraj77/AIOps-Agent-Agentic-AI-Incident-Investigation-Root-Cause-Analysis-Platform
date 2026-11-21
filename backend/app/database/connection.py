"""
AIOps Agent – Database Connection & Models
==========================================
Uses SQLAlchemy with SQLite for investigation history persistence.

Why SQLite?
- Zero infrastructure – no separate database server needed.
- Perfect for a single-node application or demo project.
- File-based storage in ./storage/aiops.db.
- Easy to inspect with DB Browser for SQLite.

Why SQLAlchemy?
- ORM makes it easy to switch to PostgreSQL later.
- Handles connection pooling and session lifecycle.
- Async support via aiosqlite for non-blocking I/O.
"""

import os
import json
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ── Ensure storage directory exists ──────────────────────────────────────────
def _ensure_storage_dir() -> None:
    """Create the storage directory if it doesn't exist."""
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(db_dir, exist_ok=True)


_ensure_storage_dir()

# ── Synchronous Engine (for simple CRUD) ─────────────────────────────────────
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
    echo=settings.debug,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Async Engine (lazy-loaded – only when needed) ───────────────────────────
def get_async_engine():
    """Lazy-load the async engine to avoid greenlet import issues at startup."""
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    async_db_url = settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    return create_async_engine(async_db_url, echo=settings.debug)


# ── Base Model ────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── ORM Models ────────────────────────────────────────────────────────────────

class InvestigationRecord(Base):
    """
    Persists a completed investigation to the database.
    The full report is stored as JSON in the `report_json` column.
    """

    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, index=True)        # UUID
    incident_title = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)
    confidence = Column(String(20), nullable=False, default="MEDIUM")
    original_logs = Column(Text, nullable=False)                  # Raw log input
    question = Column(Text, nullable=True)                        # User's question
    report_json = Column(Text, nullable=False)                    # Full InvestigationReport as JSON
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    total_log_entries = Column(Integer, default=0)
    affected_services_json = Column(Text, default="[]")           # JSON array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def affected_services(self) -> list:
        try:
            return json.loads(self.affected_services_json)
        except Exception:
            return []

    @affected_services.setter
    def affected_services(self, value: list) -> None:
        self.affected_services_json = json.dumps(value)


class DocumentRecord(Base):
    """
    Tracks uploaded knowledge base documents.
    The actual vector embeddings are stored in ChromaDB – this is just metadata.
    """

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, index=True)        # UUID
    filename = Column(String(500), nullable=False)
    original_name = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)               # pdf / txt / md
    file_size_bytes = Column(Integer, nullable=False)
    chunk_count = Column(Integer, default=0)                     # Number of chunks stored in ChromaDB
    collection_name = Column(String(200), nullable=False)
    is_embedded = Column(Boolean, default=False)                 # True after embedding succeeds
    upload_path = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# ── Database Initialisation ───────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all database tables if they do not exist.
    Call once at application startup.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialised", database_url=settings.database_url)


from contextlib import contextmanager


@contextmanager
def get_db_context():
    """
    Context manager providing a database session for internal agent nodes and background tasks.

    Usage:
        with get_db_context() as db:
            db.add(record)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Session:
    """
    FastAPI dependency that provides a database session.

    Usage in a route:
        @router.get("/")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
