from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

# Purpose: Defines the structure of the 'users' table in the database using SQLAlchemy ORM.
# This class maps directly to the database table and its columns.

class User(Base):
    """SQLAlchemy User Model.

    Represents the 'users' table in the database.
    """
    # __tablename__: Specifies the actual name of the table in the database.
    __tablename__ = "users"

    # Define table columns using SQLAlchemy's Column object.
    # Column(<DataType>, primary_key=True/False, index=True/False, unique=True/False, nullable=False/True)

    # id: Primary key for the table. Automatically increments.
    id = Column(Integer, primary_key=True, index=True)
    # username: User's chosen username. Must be unique. Indexed for faster lookups.
    username = Column(String, unique=True, index=True, nullable=False)
    # email: User's email address. Must be unique. Indexed for faster lookups.
    email = Column(String, unique=True, index=True, nullable=False)
    # full_name: User's full name. Optional.
    full_name = Column(String, nullable=True)
    # hashed_password: Stores the secure hash of the user's password. Never store plain text passwords!
    hashed_password = Column(String, nullable=False)
    # is_active: Flag indicating if the user account is active. Defaults to True.
    is_active = Column(Boolean, default=True)
    # created_at: Timestamp when the user account was created.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at: Timestamp when the user account was last updated.
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # __repr__ is useful for debugging, providing a string representation of the object.
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', full_name='{self.full_name}')>"
