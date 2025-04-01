from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from passlib.context import CryptContext
import re

app = FastAPI()

# --- Password Hashing Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Data Models (Items) ---
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class CreateItem(BaseModel):
    name: str
    description: Optional[str] = None

# --- Data Models (Users) ---
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        # Optional: Check for special characters
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]"), v):
        #     raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

# Represents user data stored in the 'database'
class UserInDB(UserBase):
    hashed_password: str


# --- In-Memory Databases ---
# Items DB
items_db: List[Item] = [
    Item(id=1, name="Laptop", description="High-performance laptop"),
    Item(id=2, name="Mouse", description="Wireless optical mouse"),
    Item(id=3, name="Keyboard", description="Mechanical keyboard")
]

# Users DB (Using username as key for simplicity)
users_db: Dict[str, UserInDB] = {}

# --- Utility Functions ---

# Item ID helper
def get_next_item_id():
    return max(item.id for item in items_db) + 1 if items_db else 1

# Password hashing helpers
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# User DB helpers (could be expanded for real DB interactions)
def get_user(username: str) -> Optional[UserInDB]:
    return users_db.get(username)

def create_user_in_db(user: UserCreate) -> UserInDB:
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(**user.model_dump(exclude={"password"}), hashed_password=hashed_password)
    users_db[user.username] = user_in_db
    return user_in_db


# --- API Endpoints (Items - BREAD) ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Item & User API! Go to /docs for details."}


# Browse (List all items)
@app.get("/items", response_model=List[Item])
def browse_items():
    return items_db

# Read (Get a specific item by ID)
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    item = next((item for item in items_db if item.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

# Add (Create a new item)
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def add_item(item_data: CreateItem):
    new_id = get_next_item_id()
    new_item = Item(id=new_id, **item_data.model_dump())
    items_db.append(new_item)
    return new_item

# Edit (Update an existing item by ID)
@app.put("/items/{item_id}", response_model=Item)
def edit_item(item_id: int, updated_item_data: CreateItem):
    item_index = next((index for index, item in enumerate(items_db) if item.id == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Keep the original ID, update other fields
    updated_item = Item(id=item_id, **updated_item_data.model_dump())
    items_db[item_index] = updated_item
    return updated_item

# Delete (Remove an item by ID)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    item_index = next((index for index, item in enumerate(items_db) if item.id == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del items_db[item_index]
    return None # Return None for 204 response

# --- API Endpoints (Users - Auth) ---

@app.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate):
    db_user = get_user(user_data.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    # You might want to add email uniqueness check here too in a real app
    created_user = create_user_in_db(user_data)
    # Return the UserBase model (without password info)
    return UserBase(**created_user.model_dump())

@app.post("/login")
def login_user(user_credentials: UserLogin):
    db_user = get_user(user_credentials.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}, # Often used with token-based auth
        )
    if not verify_password(user_credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real app, you would generate and return a token (e.g., JWT) here.
    # For this basic example, we just confirm login success.
    return {"message": f"Login successful for user: {db_user.username}"}
