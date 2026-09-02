import base64
import hashlib
import logging
from cryptography.fernet import Fernet
from core.config import settings

logger = logging.getLogger(__name__)

_cipher = None

def _get_cipher():
    """Maxfiy ENCRYPTION_KEY dan Fernet shifrlash obyektini yaratish (singleton)"""
    global _cipher
    if _cipher is None:
        raw_key = settings.ENCRYPTION_KEY
        # Agar kalit allaqachon Fernet formatida bo'lsa, to'g'ridan-to'g'ri ishlatamiz
        try:
            _cipher = Fernet(raw_key.encode())
        except Exception:
            # Aks holda SHA-256 orqali hosil qilamiz
            key = hashlib.sha256(raw_key.encode()).digest()
            fernet_key = base64.urlsafe_b64encode(key)
            _cipher = Fernet(fernet_key)
    return _cipher


def encrypt_data(text: str) -> str:
    """Matnni AES shifrlash"""
    if not text:
        return ""
    try:
        cipher = _get_cipher()
        return cipher.encrypt(text.encode()).decode()
    except Exception as e:
        logger.error(f"Shifrlash xatosi: {e}")
        return ""


def decrypt_data(token_encrypted: str) -> str:
    """Shifrlangan matnni ochish"""
    if not token_encrypted:
        return ""
    try:
        cipher = _get_cipher()
        return cipher.decrypt(token_encrypted.encode()).decode()
    except Exception as e:
        logger.error(f"Deshifrlash xatosi: {e}")
        return ""
