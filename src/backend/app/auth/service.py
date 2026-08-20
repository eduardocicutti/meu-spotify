# app/auth/service.py
import secrets
from urllib.parse import urlencode
import httpx
from datetime import datetime, timedelta, timezone
from app.config import get_settings
from app.auth.security import encrypt_token, decrypt_token, create_session_token
from app.users.service import upsert_user
from app.database import AsyncSessionLocal

settings = get_settings()


def get_authorize_url(state: str) -> str:
    """Gera URL de autorização do Spotify OAuth."""
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": settings.SPOTIFY_SCOPES,
        "state": state,
        "show_dialog": "true",
    }
    return f"{settings.SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    """Troca authorization code por access_token e refresh_token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """Renova access_token usando refresh_token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.SPOTIFY_TOKEN_URL,
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
        )
        resp.raise_for_status()
        return resp.json()


async def handle_callback(code: str, state: str) -> str:
    """
    Processa callback do OAuth:
    1. Troca code por tokens
    2. Busca perfil do usuário
    3. Cria/atualiza user no banco
    4. Retorna session token (JWT)
    """
    token_data = await exchange_code_for_tokens(code)
    
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data["expires_in"]
    
    # Buscar perfil do usuário
    from app.spotify.client import SpotifyClient
    spotify = SpotifyClient(access_token)
    profile = await spotify.get("/me")
    await spotify.close()
    
    user_id = profile["id"]
    
    # Criptografar tokens
    enc_access = encrypt_token(access_token)
    enc_refresh = encrypt_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    
    # Upsert user no banco
    async with AsyncSessionLocal() as db:
        await upsert_user(db, user_id, profile, enc_access, enc_refresh, expires_at)
    
    # Criar session token (JWT)
    session_token = create_session_token(user_id)
    
    return session_token


async def refresh_user_token(user_id: str) -> str:
    """Renova token de um usuário específico."""
    from app.users.service import get_user_by_id, update_user_tokens
    
    async with AsyncSessionLocal() as db:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        refresh_token = decrypt_token(user.refresh_token_encrypted)
        token_data = await refresh_access_token(refresh_token)
        
        new_access = token_data["access_token"]
        new_expires_in = token_data["expires_in"]
        new_refresh = token_data.get("refresh_token", refresh_token)  # Pode não vir novo
        
        enc_access = encrypt_token(new_access)
        enc_refresh = encrypt_token(new_refresh)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=new_expires_in)
        
        await update_user_tokens(db, user_id, enc_access, enc_refresh, expires_at)
        
        return new_access