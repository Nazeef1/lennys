import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings
from backend.app.db.models import Base

logger = logging.getLogger("lenny_assistant.db")

def _create_db_engine():
    db_url = settings.sanitized_database_url
    engine_kwargs = {}

    if db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        if "/tmp/" in db_url:
            try:
                os.makedirs("/tmp", exist_ok=True)
            except Exception:
                pass

    try:
        return create_engine(db_url, **engine_kwargs)
    except Exception as e:
        logger.error(f"[DB] Primary database engine creation failed for '{db_url}': {e}. Falling back to SQLite.")
        fallback_url = "sqlite:////tmp/lenny_assistant.db" if os.getenv("VERCEL") else "sqlite:///./lenny_assistant.db"
        if "/tmp/" in fallback_url:
            try:
                os.makedirs("/tmp", exist_ok=True)
            except Exception:
                pass
        return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = _create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"[DB] Database initialization notice: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

