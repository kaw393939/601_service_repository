import pytest
from sqlalchemy.orm import Session
from repositories import UserRepository
from models import User # Import your User model

# Purpose: Contains unit/integration tests for the UserRepository.
# These tests verify that the repository methods interact correctly with the
# (test) database for CRUD operations.

# --- Test Data --- #
# Reusable test data reduces duplication in tests.
TEST_USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

TEST_USER_UPDATE_DATA = {
    "username": "updateduser",
    "email": "updated@example.com",
    "password": "newpassword",
    "full_name": "Updated User",
    "is_active": True
}

# --- Test Functions --- #
# Test functions use fixtures (like user_repository and db_session) defined in conftest.py.
# Pytest automatically injects these fixtures based on the function argument names.

@pytest.fixture(scope="function")
def user_repo(db_session: Session) -> UserRepository:
    """Fixture to provide a UserRepository instance with the test session."""
    return UserRepository(db_session)

def test_add_user(user_repo: UserRepository):
    """Tests successfully adding a new user."""
    # Arrange: Data is in TEST_USER_DATA
    
    # Act: Call the repository method to add the user.
    user = user_repo.add(**TEST_USER_DATA)

    # Assert: Check if the returned user object has the correct attributes.
    assert user is not None
    assert user.id is not None # DB should assign an ID
    assert user.username == TEST_USER_DATA["username"]
    assert user.email == TEST_USER_DATA["email"]
    # Optionally check if password was hashed (don't compare plain text)
    assert user.hashed_password != TEST_USER_DATA["password"]

def test_add_user_duplicate_email(user_repo: UserRepository):
    """Tests that adding a user with a duplicate email raises IntegrityError."""
    # Arrange: Add the first user.
    user_repo.add(**TEST_USER_DATA)
    
    # Arrange: Prepare data for a second user with the same email.
    duplicate_data = TEST_USER_DATA.copy()
    duplicate_data["username"] = "anotheruser" # Different username

    # Act & Assert: Use pytest.raises to check if the expected exception occurs.
    with pytest.raises(Exception): # Catching general Exception, ideally IntegrityError
        user_repo.add(**duplicate_data)
        user_repo.db.flush() # Force the DB interaction to trigger constraint

def test_get_user_by_id(user_repo: UserRepository):
    """Tests retrieving a user by their ID."""
    # Arrange: Add a user first.
    added_user = user_repo.add(**TEST_USER_DATA)
    assert added_user.id is not None

    # Act: Retrieve the user using the generated ID.
    fetched_user = user_repo.get_by_id(added_user.id)

    # Assert: Check if the correct user was retrieved.
    assert fetched_user is not None
    assert fetched_user.id == added_user.id
    assert fetched_user.username == TEST_USER_DATA["username"]

def test_get_user_by_id_not_found(user_repo: UserRepository):
    """Tests retrieving a non-existent user by ID returns None."""
    # Arrange: No user added with ID 999.
    non_existent_id = 999

    # Act: Attempt to retrieve the user.
    fetched_user = user_repo.get_by_id(non_existent_id)

    # Assert: Check that None was returned.
    assert fetched_user is None

def test_get_user_by_username(user_repo: UserRepository):
    """Tests retrieving a user by their username."""
    # Arrange: Add a user.
    user_repo.add(**TEST_USER_DATA)

    # Act: Retrieve the user by username.
    fetched_user = user_repo.get_by_username(TEST_USER_DATA["username"])

    # Assert: Check if the correct user was retrieved.
    assert fetched_user is not None
    assert fetched_user.username == TEST_USER_DATA["username"]
    assert fetched_user.email == TEST_USER_DATA["email"]

def test_get_user_by_email(user_repo: UserRepository):
    """Tests retrieving a user by their email."""
    # Arrange: Add user.
    user_repo.add(**TEST_USER_DATA)

    # Act: Retrieve.
    fetched_user = user_repo.get_by_email(TEST_USER_DATA["email"])

    # Assert: Check correctness.
    assert fetched_user is not None
    assert fetched_user.email == TEST_USER_DATA["email"]
    assert fetched_user.username == TEST_USER_DATA["username"]

def test_browse_users(user_repo: UserRepository):
    """Tests retrieving a list of users (browsing)."""
    # Arrange: Add multiple users.
    user1 = user_repo.add(username="user1", email="user1@test.com", password="pw1")
    user2 = user_repo.add(username="user2", email="user2@test.com", password="pw2")
    users = user_repo.browse()

    # Assert: Check if the correct number of users is returned.
    assert len(users) == 2
    # Check if user IDs are in the fetched list
    user_ids = [u.id for u in users]
    assert user1.id in user_ids
    assert user2.id in user_ids

def test_browse_users_pagination(user_repo: UserRepository):
    """Tests pagination (skip and limit) when browsing users."""
    # Arrange: Add several users.
    for i in range(5):
        user_repo.add(username=f"user{i}", email=f"user{i}@test.com", password="pw")
    
    # Get first page
    users_page1 = user_repo.browse(skip=0, limit=3)
    assert len(users_page1) == 3
    # Get second page
    users_page2 = user_repo.browse(skip=3, limit=3)
    assert len(users_page2) == 2 # Only 2 remaining

def test_edit_user(user_repo: UserRepository):
    """Tests editing an existing user's attributes."""
    # Arrange: Add the initial user.
    added_user = user_repo.add(**TEST_USER_DATA)
    user_id = added_user.id

    # Act: Update the user with new data using the update method.
    updated_user = user_repo.update(
        added_user, # Pass the user object
        username=TEST_USER_UPDATE_DATA["username"],
        email=TEST_USER_UPDATE_DATA["email"],
        full_name=TEST_USER_UPDATE_DATA["full_name"],
        is_active=TEST_USER_UPDATE_DATA["is_active"]
    )

    # Assert: Verify the returned user and database state reflect the updates.
    assert updated_user is not None
    assert updated_user.id == user_id
    assert updated_user.username == TEST_USER_UPDATE_DATA["username"]
    assert updated_user.email == TEST_USER_UPDATE_DATA["email"]
    # Verify password hasn't changed if not provided
    assert updated_user.hashed_password == added_user.hashed_password

def test_edit_user_password(user_repo: UserRepository):
    """Tests editing only the user password."""
    # Arrange: Add the initial user.
    added_user = user_repo.add(**TEST_USER_DATA)
    original_hash = added_user.hashed_password

    # Act: Update only the password
    updated_user = user_repo.update(
        added_user, # Pass the user object
        password=TEST_USER_UPDATE_DATA["password"]
    )

    # Assert: Check that only the password changed.
    assert updated_user is not None
    assert updated_user.hashed_password != original_hash
    assert updated_user.username == added_user.username # Ensure other fields didn't change

def test_delete_user(user_repo: UserRepository):
    """Tests successfully deleting a user."""
    # Arrange: Add a user to delete.
    user_to_delete = user_repo.add(**TEST_USER_DATA)
    user_id = user_to_delete.id

    # Act: Delete the user.
    delete_result = user_repo.delete(user_id)

    # Assert: Check that deletion was reported as successful.
    assert delete_result is True

    # Assert: Verify the user is actually gone from the database.
    fetched_user = user_repo.get_by_id(user_id)
    assert fetched_user is None

def test_delete_user_not_found(user_repo: UserRepository):
    """Tests attempting to delete a non-existent user returns False."""
    # Arrange: No user with this ID exists.
    non_existent_id = 999

    # Act: Attempt to delete.
    delete_result = user_repo.delete(non_existent_id)

    # Assert: Check that deletion was reported as unsuccessful.
    assert delete_result is False
