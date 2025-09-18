from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engines
# Writer engine (for write operations)
writer_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# Reader engine (for read-only operations)
reader_engine = create_engine(settings.SQLALCHEMY_READER_URI, pool_pre_ping=True)

# Create SessionLocal classes for database sessions
# For write operations
WriterSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=writer_engine)
# For read operations
ReaderSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=reader_engine)

# Create Base class for database models
Base = declarative_base()


def get_db():
    """
    Dependency to get a database session for write operations (primary endpoint)
    """
    db = WriterSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    """
    Dependency to get a read-only database session (reader endpoint)
    When using Aurora, this will connect to the reader endpoint for better read scalability
    """
    db = ReaderSessionLocal()
    try:
        yield db
    finally:
        db.close()