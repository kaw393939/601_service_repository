from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext
from typing import List, Optional

# Purpose: Implements the data access layer (DAL) for User entities.
# This class directly interacts with the database for User-related operations.
# It encapsulates all the SQL or ORM logic (e.g., SQLAlchemy queries) needed to
# perform CRUD (Create, Read, Update, Delete) operations on the 'users' table.

# --- Why a Repository Pattern? ---
# 1. Separation of Concerns: Isolates database interaction logic from the rest of the application
#    (like business logic in services or API handling in endpoints). This makes the codebase
#    cleaner and easier to understand.
# 2. Testability: Allows easy mocking of the data layer during unit tests. Services or API tests
#    can use a mock repository instead of needing a real database connection, making tests faster
#    and more reliable.
# 3. Maintainability: If the database schema changes or you switch ORMs/databases, the changes
#    are primarily contained within the repository layer, minimizing impact on other parts
#    of the application.
# 4. Reusability: Database queries related to Users are centralized here and can be reused by
#    multiple services or components if needed.

# Configure passlib for password hashing (same context as in models.py for consistency).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    """Repository for handling database operations for the User model.

    Methods correspond to BREAD operations (Browse, Read, Edit, Add, Delete).
    """

    def __init__(self, db: Session):
        """Initializes the repository with a database session."""
        # Dependency Injection: The database session (db) is "injected" into the repository
        # upon creation. This means the repository doesn't create its own session;
        # it receives one from the outside (typically managed by the service layer or
        # a request lifecycle mechanism like FastAPI's dependency injection).
        self.db = db

    def _hash_password(self, password: str) -> str:
        """Internal helper method to hash a plain text password."""
        return pwd_context.hash(password)

    # --- Add (Create) --- #
    def add(self, username: str, email: str, password: str, full_name: Optional[str] = None, is_active: bool = True) -> User:
        """Adds a new user to the database.

        Args:
            username: The user's username.
            email: The user's email address.
            password: The user's plain text password (will be hashed).
            full_name: Optional full name.
            is_active: Optional active status (defaults to True).

        Returns:
            The newly created User object.

        Raises:
            SQLAlchemyError (or specific subclasses like IntegrityError) if the database operation fails
            (e.g., unique constraint violation for username/email).
        """
        # 1. Prepare data: Hash the password.
        hashed_password = self._hash_password(password)
        # 2. Create ORM object: Instantiate the SQLAlchemy model.
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active
        )
        # 3. Stage changes: Add the new object to the session.
        self.db.add(db_user)
        # 4. Persist changes: Commit the transaction to the database.
        self.db.commit()
        # 5. Update object: Refresh the instance to get DB-generated values (like ID).
        self.db.refresh(db_user)
        return db_user

    # --- Read (Getters) --- #
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieves a single user by their primary key (ID)."""
        # Uses SQLAlchemy query syntax: self.db.query(<Model>).filter(<Condition>).<ResultMethod>()
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieves a single user by their unique username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a single user by their unique email address."""
        return self.db.query(User).filter(User.email == email).first()

    # --- Browse (List) --- #
    def browse(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieves a list of users, supporting pagination via skip and limit."""
        # .offset() and .limit() are used for database-level pagination.
        return self.db.query(User).offset(skip).limit(limit).all()

    # --- Edit (Update) --- #
    def update(self, user: User, **kwargs) -> User:
        """Updates attributes of an existing user model instance.

        Args:
            user: The SQLAlchemy User object (already retrieved from the DB) to update.
            **kwargs: Key-value pairs of attributes to update (e.g., email="new@example.com").
                      Handles password hashing if 'password' is in kwargs.

        Returns:
            The updated User object.
        """
        # Flag to track if changes were made
        updated = False
        # Iterate through the provided keyword arguments.
        for key, value in kwargs.items():
            # Special handling for password hashing needs to happen *before* hasattr check
            if key == "password":
                if value is not None:
                    new_hashed_password = self._hash_password(value)
                    # Only update if the new hash is different
                    if new_hashed_password != user.hashed_password:
                        user.hashed_password = new_hashed_password
                        updated = True
            # For other attributes, check if they exist on the model and if the value changed
            elif hasattr(user, key) and value is not None:
                current_value = getattr(user, key)
                if current_value != value:
                    setattr(user, key, value)
                    updated = True

        # Only commit if actual changes were made to avoid unnecessary DB interaction.
        if updated:
            # Add the modified user object to the session (marks it as dirty).
            self.db.add(user) # Mark the existing object as changed in the session
            # Commit the changes to the database.
            self.db.commit()
            # Refresh the instance to reflect the changes.
            self.db.refresh(user)
        return user

    # --- Delete --- #
    def delete(self, user_id: int) -> bool:
        """Deletes a user by their ID.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if a user was found and deleted, False otherwise.
        """
        # 1. Find the user first.
        db_user = self.get_by_id(user_id)
        if db_user:
            # 2. Stage deletion: Mark the object for deletion in the session.
            self.db.delete(db_user)
            # 3. Persist deletion: Commit the transaction.
            self.db.commit()
            return True
        # 4. Return False if user not found.
        return False
