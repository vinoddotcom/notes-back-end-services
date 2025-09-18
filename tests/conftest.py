import os
import pytest
from typing import Any, Generator
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app

# Load test environment variables
env_test_path = Path('.env.test')
if env_test_path.exists():
    load_dotenv('.env.test')

# Determine database URL based on environment variables
USE_SQLITE = os.getenv("USE_SQLITE", "").lower() in ("true", "1", "yes")

if USE_SQLITE:
    # Use SQLite for testing (faster for CI)
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False}
else:
    # Use PostgreSQL for more production-like testing
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
    SQLALCHEMY_TEST_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    connect_args = {}

# Create the database engine with appropriate arguments
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args=connect_args
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a fresh database for each test
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
        # For SQLite, we can drop all tables after each test
        # For PostgreSQL, we'll just truncate the tables to avoid schema recreation overhead
        if USE_SQLITE:
            Base.metadata.drop_all(bind=engine)
        else:
            # Truncate all tables but keep the schema
            connection = engine.raw_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
            tables = cursor.fetchall()
            
            # Disable foreign key checks, truncate all tables, then re-enable foreign keys
            cursor.execute("SET session_replication_role = 'replica';")  # Disable triggers temporarily
            
            for table in tables:
                table_name = table[0]
                # Skip alembic_version table
                if table_name != 'alembic_version':
                    cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE;')
                    
            cursor.execute("SET session_replication_role = 'origin';")  # Re-enable triggers
            connection.commit()
            cursor.close()
            connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Create a FastAPI TestClient that uses the `db` fixture to override
    the dependency injection
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c