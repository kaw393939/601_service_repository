from sqlalchemy.orm import Session
from repositories import UserRepository
from models import User
from typing import List, Optional
import logging # Example: for adding business logic logging

logger = logging.getLogger(__name__)

# Purpose: Defines the business logic layer (BLL) for user-related operations.
# This layer sits between the presentation layer (e.g., API endpoints in main.py)
# and the data access layer (UserRepository).

# --- Why a Service Layer? ---
# 1. Encapsulation of Business Logic: Centralizes rules and processes related to users
#    that go beyond simple data manipulation (e.g., complex validation, workflows,
#    coordinating multiple repository actions, interacting with external services).
# 2. Decoupling: The API layer interacts with the service, not directly with the repository.
#    This means the API doesn't need to know about database details, only about the available
#    business operations.
# 3. Reusability: Business logic defined here can be reused by different parts of the
#    application (e.g., API endpoints, background tasks, administrative interfaces).
# 4. Testability: Business logic can be unit tested by mocking the repository, isolating
#    the logic itself from database dependencies.
# 5. Orchestration: If an operation involves multiple steps or repositories (e.g., creating a user
#    and also adding them to a default group), the service layer coordinates these actions.

class UserService:
    """Service layer encapsulating business logic for User operations."""

    def __init__(self, db: Session):
        """Initializes the service with a database session and creates a UserRepository."""
        # The service takes the database session... 
        self.db = db 
        # ...and uses it to create an instance of the UserRepository.
        # This composition allows the service to delegate data persistence tasks.
        self.repository = UserRepository(self.db)

    def create_user(self, username: str, email: str, password: str, full_name: Optional[str] = None, is_active: bool = True) -> User:
        """Handles the business logic for creating a new user.
        
        Currently, this mostly delegates to the repository, but it's the place
        where more complex creation logic would reside.
        """
        # --- Business Logic Example --- #
        # 1. Validation (Beyond basic type hints or DB constraints):
        #    - Check password complexity rules?
        #    - Verify email format more strictly?
        #    - Check against a list of disallowed usernames?
        #    - Rate limiting checks?
        # Example: Simple check for existing user (though DB constraint also handles it)
        if self.repository.get_by_username(username):
             # In a real API, this check might be better handled in the API layer
             # before calling the service, returning a 4xx error.
             # Throwing an exception here allows the caller (API) to catch it.
             raise ValueError(f"Username '{username}' is already taken.")
        if self.repository.get_by_email(email):
             raise ValueError(f"Email '{email}' is already registered.")

        # 2. Data Preparation/Transformation (if needed beyond repository):
        #    - Normalize username (e.g., to lowercase)?
        #      username = username.lower() # Decide if this is business logic or repo logic

        # 3. Delegate to Repository: Pass validated/prepared data to the repository for persistence.
        logger.info(f"Attempting to create user: {username}")
        created_user = self.repository.add(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_active=is_active
        )
        logger.info(f"Successfully created user ID: {created_user.id}")

        # 4. Post-Creation Actions (Orchestration):
        #    - Send a welcome email?
        #    - Add user to a default group/role?
        #    - Log an audit event?
        #    self._send_welcome_email(email, username)
        #    self._log_user_creation_event(created_user.id)

        return created_user

    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieves a single user by ID. Simple passthrough to the repository."""
        logger.debug(f"Fetching user by ID: {user_id}")
        return self.repository.get_by_id(user_id)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieves a list of users. Simple passthrough to the repository."""
        logger.debug(f"Browsing users: skip={skip}, limit={limit}")
        return self.repository.browse(skip=skip, limit=limit)

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Handles the business logic for updating a user.
        
        Retrieves the user first, performs checks/logic, then delegates the update.
        """
        logger.info(f"Attempting to update user ID: {user_id} with data: {kwargs}")
        # 1. Retrieve the entity to update.
        user_to_update = self.repository.get_by_id(user_id)
        if not user_to_update:
            logger.warning(f"Update failed: User ID {user_id} not found.")
            return None # Or raise a specific NotFound exception for the API layer

        # 2. Business Logic / Validation before update:
        #    - Can this user be updated (e.g., is the requesting user authorized)?
        #    - If updating username/email, perform uniqueness checks similar to create?
        new_username = kwargs.get("username")
        if new_username and new_username != user_to_update.username:
            existing = self.repository.get_by_username(new_username)
            if existing and existing.id != user_id:
                raise ValueError(f"Username '{new_username}' is already taken.")
        
        new_email = kwargs.get("email")
        if new_email and new_email != user_to_update.email:
            existing = self.repository.get_by_email(new_email)
            if existing and existing.id != user_id:
                raise ValueError(f"Email '{new_email}' is already registered.")

        # 3. Delegate to Repository: Pass the retrieved object and changes.
        updated_user = self.repository.update(user_to_update, **kwargs)

        # 4. Post-Update Actions:
        #    - Send notification of changes?
        #    - Log audit event?
        logger.info(f"Successfully updated user ID: {user_id}")
        # self._log_user_update_event(user_id, list(kwargs.keys()))

        return updated_user

    def delete_user(self, user_id: int) -> bool:
        """Handles the business logic for deleting a user.
        
        Currently delegates directly, but could involve checks or related cleanup.
        """
        logger.info(f"Attempting to delete user ID: {user_id}")
        # 1. Business Logic / Validation before delete:
        #    - Can this user be deleted (e.g., not an admin, no outstanding tasks)?
        #    - Is the requesting user authorized?
        user_to_delete = self.repository.get_by_id(user_id)
        if not user_to_delete:
             logger.warning(f"Delete failed: User ID {user_id} not found.")
             return False
        # if user_to_delete.is_admin: # Example check
        #     raise PermissionError("Cannot delete admin users.")

        # 2. Perform related cleanup (Orchestration):
        #    - Delete related records (e.g., user preferences, session tokens)?
        #    self.preferences_repository.delete_by_user(user_id)

        # 3. Delegate to Repository:
        deleted = self.repository.delete(user_id)

        # 4. Post-Deletion Actions:
        #    - Log audit event?
        if deleted:
            logger.info(f"Successfully deleted user ID: {user_id}")
            # self._log_user_deletion_event(user_id)
        else:
            # This case should ideally be caught by the initial get_by_id check
            logger.error(f"Deletion failed unexpectedly for user ID: {user_id} after initial check.")

        return deleted

    # Example helper methods for potential business logic:
    # def _send_welcome_email(self, email: str, username: str):
    #     # Logic to connect to an email service and send a template
    #     logger.info(f"Simulating sending welcome email to {email}")
    #     pass

    # def _log_user_creation_event(self, user_id: int):
    #     # Logic to log important events to an audit trail
    #     logger.info(f"AUDIT: User created - ID {user_id}")
    #     pass
