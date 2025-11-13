from passlib.context import CryptContext

# Use pbkdf2_sha256 as primary scheme - more reliable and no 72-byte limit
# This avoids bcrypt initialization issues while maintaining security
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],  # Try pbkdf2 first, fallback to bcrypt
    default="pbkdf2_sha256",
    deprecated="auto",
    pbkdf2_sha256__default_rounds=29000,  # Secure default rounds
)

def hash_password(password: str) -> str:
    """
    Hash a password using pbkdf2_sha256 (no 72-byte limit like bcrypt).
    Secure and reliable for passwords of any length.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    Works with both pbkdf2_sha256 and bcrypt hashes for backward compatibility.
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False
