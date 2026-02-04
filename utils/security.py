import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a plain-text password against a stored SHA-256 hash.
    """
    return hash_password(password) == stored_hash
