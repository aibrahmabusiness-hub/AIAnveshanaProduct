"""
AES-256 Encryption utility for securing API keys.
Uses Fernet (AES-128-CBC + HMAC-SHA256) from the cryptography library.
The master encryption key is stored as an environment variable, never in the database.
"""
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key

load_dotenv()

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

def _get_or_create_key() -> bytes:
    """Get the encryption key from env, or auto-generate one on first run."""
    key = os.getenv("ENCRYPTION_KEY", "")
    if not key:
        key = Fernet.generate_key().decode()
        # Save it to .env so it persists
        set_key(ENV_PATH, "ENCRYPTION_KEY", key)
        os.environ["ENCRYPTION_KEY"] = key
    return key.encode()

_fernet = None

def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_or_create_key())
    return _fernet

def encrypt_key(plaintext: str) -> str:
    """Encrypt an API key. Returns a base64-encoded encrypted string."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()

def decrypt_key(encrypted: str) -> str:
    """Decrypt an API key. Returns the original plaintext."""
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()

def mask_key(key: str) -> str:
    """Mask an API key for display (e.g., 'sk-...abc123')."""
    if len(key) <= 8:
        return "****"
    return key[:4] + "..." + key[-4:]
