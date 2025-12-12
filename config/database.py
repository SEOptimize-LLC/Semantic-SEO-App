"""Database configuration and initialization."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import will be done after models are created
_engine = None
_SessionLocal = None


def get_database_url(db_path: Optional[str] = None) -> str:
    """
    Get SQLite database URL.
    
    Args:
        db_path: Optional custom database path
    
    Returns:
        SQLite connection URL
    """
    if db_path is None:
        # Default path relative to config directory
        base_path = Path(__file__).parent.parent
        db_path = base_path / "data" / "semantic_seo.db"
    else:
        db_path = Path(db_path)
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    return f"sqlite:///{db_path}"


def get_engine(db_path: Optional[str] = None):
    """
    Get or create SQLAlchemy engine.
    
    Args:
        db_path: Optional custom database path
    
    Returns:
        SQLAlchemy engine
    """
    global _engine
    
    if _engine is None:
        database_url = get_database_url(db_path)
        
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,  # Set to True for SQL logging
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    return _engine


def get_session_local():
    """Get SessionLocal class for creating sessions."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    
    return _SessionLocal


def get_db() -> Session:
    """
    Get database session.
    
    Yields:
        Database session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(db_path: Optional[str] = None):
    """
    Initialize database and create all tables.
    
    Args:
        db_path: Optional custom database path
    """
    from utils.database import Base
    
    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)
    
    return engine


def reset_db(db_path: Optional[str] = None):
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    
    Args:
        db_path: Optional custom database path
    """
    from utils.database import Base
    
    engine = get_engine(db_path)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    return engine