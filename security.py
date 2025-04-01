from passlib.context import CryptContext

# --- Password Hashing Setup --- #

# Use CryptContext for password hashing.
# Schemes specifies the hashing algorithms to use (bcrypt is recommended).
# deprecated="auto" means it will use the default scheme (bcrypt) for hashing
# but can still verify passwords hashed with older algorithms if they were added.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password using bcrypt."""
    return pwd_context.hash(password)
