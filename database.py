import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Purpose: This module sets up the connection to the database using SQLAlchemy.
# It provides the SQLAlchemy engine, a session factory (SessionLocal),
# and the declarative base class (Base) for defining ORM models.

# Load environment variables from a .env file if it exists.
# This is good practice for managing configuration, especially secrets,
# although in this setup, the DATABASE_URL is primarily set by docker-compose.
# Create a .env file in the project root (and add it to .gitignore!) if you need
# to override settings or manage other environment-specific variables.
# Example .env content:
# DATABASE_URL=postgresql://localuser:localpassword@localhost:5432/localdb
if load_dotenv():
    logger.info(".env file loaded.")
else:
    logger.info("No .env file found, relying on system environment variables.")

# Get the database connection URL from environment variables.
# It defaults to a typical local setup if DATABASE_URL is not set,
# but docker-compose.yml explicitly sets this for the containerized environment.
DATABASE_URL = os.getenv("DATABASE_URL") 

if not DATABASE_URL:
    # If DATABASE_URL is not set via .env or system environment (like docker-compose),
    # raise an error to prevent the application from starting with incorrect config.
    logger.error("DATABASE_URL environment variable is not set. Application cannot connect to the database.")
    raise ValueError("DATABASE_URL environment variable is not set")
else:
    # Mask password in logs
    try:
        from urllib.parse import urlparse, urlunparse
        parsed_url = urlparse(DATABASE_URL)
        safe_netloc = f"{parsed_url.username}:***@{parsed_url.hostname}:{parsed_url.port}"
        safe_url_parts = parsed_url._replace(netloc=safe_netloc)
        safe_url = urlunparse(safe_url_parts)
        logger.info(f"Database URL configured: {safe_url}")
    except Exception:
        logger.info("Database URL configured (details hidden).")

# Create the SQLAlchemy engine.
# The engine is the starting point for any SQLAlchemy application.
# It represents the core interface to the database.
# connect_args are specific to the underlying DBAPI driver (psycopg2 here).
# For SQLite, you might need: connect_args={"check_same_thread": False}
engine = create_engine(DATABASE_URL) 

# Create a configured "Session" class.
# sessionmaker is a factory that generates new Session objects.
# - autocommit=False: Sessions won't automatically commit changes; you must call db.commit().
# - autoflush=False: Sessions won't automatically flush changes (send pending SQL to DB) before queries.
# - bind=engine: Associates this session factory with our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions.
# Any model class we create will inherit from this Base.
# It allows SQLAlchemy to map our Python classes to database tables.
Base = declarative_base()

# Dependency for FastAPI endpoints to get a database session.
# This function is designed to be used with FastAPI's dependency injection system.
# It ensures that a database session is created for each request and closed afterward,
# even if errors occur.
def get_db():
    """FastAPI dependency that provides a SQLAlchemy database session."""
    db = SessionLocal() # Create a new session.
    try:
        yield db # Provide the session to the endpoint function.
    finally:
        db.close() # Ensure the session is closed after the request is finished.
