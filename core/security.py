import base64
import hashlib
from cryptography.fernet import Fernet
from core.config import settings

# Maxfiy kalitdan shifrlash kalitini hosil qilish
def _get_cipher():
    key = hashlib.sha256(settings.QWEN_API_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)

def encrypt_data(text: str) -> str:
    if not text:
        return ""
    cipher = _get_cipher()
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(token_encrypted: str) -> str:
    if not token_encrypted:
        return ""
    try:
        cipher = _get_cipher()
        return cipher.decrypt(token_encrypted.encode()).decode()
    except Exception:
        return ""
