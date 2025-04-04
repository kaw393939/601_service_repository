#!/usr/bin/env python

# Purpose: This script populates the database with realistic-looking fake user data.
# It's useful for development and testing purposes, providing initial data to work with
# without needing to manually create users.

import argparse
import logging
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # To handle duplicate entries

# Import necessary components from our application
from database import SessionLocal, engine, Base
from services import UserService # Import the UserService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data(db: Session, num_users: int):
    """Seeds the database with fake user data."""
    logger.info("--- Starting Database Seeding --- ")

    # Create database tables if they don't exist.
    # Base.metadata.create_all() checks for existing tables before creating.
    logger.info("Creating database tables (if they don't exist)...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return # Stop seeding if table creation fails

    # Initialize Faker to generate fake data
    # Using 'en_US' locale for common English names/data
    faker = Faker('en_US')

    logger.info(f"Attempting to create {num_users} fake users...")
    
    # Create an instance of the UserService using the session
    user_service = UserService(db)
    users_created = 0
    users_skipped = 0

    for i in range(num_users):
        # Generate fake data for a user
        # Use unique usernames and emails generated by Faker
        username = faker.unique.user_name()
        email = faker.unique.email()
        # Generate a plausible password (for seeding purposes only - DO NOT use weak passwords in production)
        password = "password123" # Use a standard password for all seeded users

        try:
            # Use the UserService to add the user
            # This ensures hashing and other service logic is applied
            user_service.create_user(username=username, email=email, password=password)
            users_created += 1
            # Log progress periodically
            if (i + 1) % 10 == 0:
                logger.info(f"  Created user {i + 1}/{num_users} (Username: {username})")

        except IntegrityError:
            # This can happen if Faker somehow generates a duplicate username/email
            # despite the .unique modifier (unlikely but possible) or if seeding is run multiple times.
            logger.warning(f"  Skipping user {i + 1}/{num_users}: Username '{username}' or Email '{email}' likely already exists.")
            db.rollback() # Rollback the specific failed transaction
            # Reset Faker's unique provider for the fields that failed
            # This helps avoid repeated collisions if the script continues
            faker.unique.clear()
            users_skipped += 1
        except Exception as e:
            # Catch any other unexpected errors during user creation
            logger.error(f"  Error creating user {i + 1}/{num_users} (Username: {username}): {e}")
            db.rollback() # Rollback the failed transaction
            users_skipped += 1

    logger.info(f"--- Seeding Complete --- ")
    logger.info(f"Total users created: {users_created}")
    logger.info(f"Total users skipped (due to duplicates or errors): {users_skipped}")

def main():
    parser = argparse.ArgumentParser(description="Seed the database with fake users.")
    parser.add_argument("-n", "--num-users", type=int, default=50, help="Number of users to create.")
    args = parser.parse_args()

    logger.info("Initializing database...")
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_data(db, args.num_users)
    finally:
        db.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    main()
