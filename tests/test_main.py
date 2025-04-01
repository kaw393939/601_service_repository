from fastapi.testclient import TestClient
from fastapi import status

# The client fixture is imported automatically by pytest from conftest.py
# No need for explicit import here if using the fixture name 'client'

# Keep track of the ID for the item created during tests
created_item_id = None

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the Item & User API! Go to /docs for details."}

def test_browse_items_initial(client: TestClient):
    """Test browsing items when the app starts (initial state)."""
    response = client.get("/items")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3 # Assuming 3 initial items from main.py
    assert data[0]["name"] == "Laptop"

def test_add_item(client: TestClient):
    """Test adding a new item."""
    global created_item_id
    item_data = {"name": "Monitor", "description": "4K UHD Monitor"}
    response = client.post("/items", json=item_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert "id" in data
    created_item_id = data["id"] # Save the ID for later tests
    assert created_item_id > 3 # Should be the next ID after initial ones

def test_browse_items_after_add(client: TestClient):
    """Test browsing items after adding one."""
    response = client.get("/items")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 4 # Initial 3 + 1 added
    # Check if the newly added item is in the list
    assert any(item["id"] == created_item_id for item in data)

def test_read_specific_item(client: TestClient):
    """Test reading the newly added item by its ID."""
    assert created_item_id is not None, "Item ID should have been set by test_add_item"
    response = client.get(f"/items/{created_item_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_item_id
    assert data["name"] == "Monitor"

def test_read_nonexistent_item(client: TestClient):
    """Test reading an item that does not exist."""
    response = client.get("/items/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

def test_edit_item(client: TestClient):
    """Test editing the newly added item."""
    assert created_item_id is not None, "Item ID should have been set by test_add_item"
    updated_data = {"name": "Monitor Pro", "description": "Professional 4K Monitor"}
    response = client.put(f"/items/{created_item_id}", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_item_id # ID should remain the same
    assert data["name"] == updated_data["name"]
    assert data["description"] == updated_data["description"]

def test_edit_nonexistent_item(client: TestClient):
    """Test editing an item that does not exist."""
    updated_data = {"name": "Ghost Item", "description": "Should not exist"}
    response = client.put("/items/9999", json=updated_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

def test_delete_item(client: TestClient):
    """Test deleting the newly added item."""
    assert created_item_id is not None, "Item ID should have been set by test_add_item"
    response = client.delete(f"/items/{created_item_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Verify the item is actually gone
    get_response = client.get(f"/items/{created_item_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_nonexistent_item(client: TestClient):
    """Test deleting an item that does not exist."""
    response = client.delete("/items/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

def test_browse_items_after_delete(client: TestClient):
    """Test browsing items after deleting the added one."""
    response = client.get("/items")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3 # Should be back to the initial 3 items
    assert not any(item["id"] == created_item_id for item in data)
