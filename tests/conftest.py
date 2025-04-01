import pytest
from fastapi.testclient import TestClient
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import the Base from your models to create tables
from database import Base, get_db
from main import app # Your FastAPI app instance

# Purpose: This file sets up shared fixtures for pytest tests.
# Fixtures are functions that provide a fixed baseline state or data for tests.
# Using fixtures promotes code reuse and makes tests cleaner and more maintainable.

# --- In-Memory SQLite Database Setup for Testing ---
# Use an in-memory SQLite database for tests. This is much faster than hitting a real DB
# and ensures tests run in isolation without affecting a development/production database.
# The URL "sqlite:///:memory:" signifies an in-memory database.
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a SQLAlchemy engine specifically for testing.
# connect_args={"check_same_thread": False}: Required only for SQLite to allow usage across threads (pytest might use them).
# poolclass=StaticPool: Ensures the same connection is used for the lifespan of the test session,
# which is necessary for in-memory databases as data is lost when the connection closes.
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite
    poolclass=StaticPool, # Use StaticPool for in-memory DB
)

# Create a session factory for the test database.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Pytest Fixtures ---

# Create tables before tests run
Base.metadata.create_all(bind=engine)

# Override the get_db dependency for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function") # Use function scope for session to reset between tests
def db_session() -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for test functions."""
    # This fixture runs for every test function (default scope="function").
    # It simulates the get_db dependency used in the main application.
    # Create tables for each test function to ensure isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after test if needed, though drop/create handles most cases
        # Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Yield a TestClient instance that uses the testing database session."""
    # app already has the dependency override applied
    with TestClient(app) as c:
        yield c
