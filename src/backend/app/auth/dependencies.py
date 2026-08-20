# app/auth/dependencies.py
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decrypt_token, verify_session_token
from app.database import get_db
from app.spotify.client import SpotifyClient
from app.users.models import User
from app.users.service import get_user_by_id


async def get_current_user_id(request: Request) -> str:
    """Extrai user_id do cookie de sessão."""
    cookie = request.cookies.get("session")
    if not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    user_id = verify_session_token(cookie)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada"
        )
    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Retorna usuário autenticado completo."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    return user


async def get_spotify_client(user: User = Depends(get_current_user)) -> SpotifyClient:
    """Retorna cliente Spotify autenticado para o usuário atual."""
    access_token = decrypt_token(user.access_token_encrypted)
    return SpotifyClient(access_token)
