# app/auth/security.py
import time
from cryptography.fernet import Fernet
from jose import jwt
from app.config import get_settings

settings = get_settings()

# Fernet for encrypting Spotify tokens
_fernet = Fernet(settings.FERNET_KEY.encode())


def encrypt_token(token: str) -> str:
    """Criptografa token do Spotify para armazenamento no banco."""
    return _fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    """Descriptografa token do Spotify do banco."""
    return _fernet.decrypt(encrypted.encode()).decode()


# JWT para sessão do usuário (cookie HttpOnly)
def create_session_token(user_id: str) -> str:
    """Cria JWT para cookie de sessão (7 dias)."""
    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 7 * 24 * 3600,  # 7 dias
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_session_token(token: str) -> str | None:
    """Verifica JWT do cookie e retorna user_id se válido."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.JWTError:
        return None