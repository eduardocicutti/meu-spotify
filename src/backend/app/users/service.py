# app/users/service.py
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User
from datetime import datetime, timezone


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Busca usuário por ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def upsert_user(
    db: AsyncSession,
    user_id: str,
    profile: dict,
    access_token_encrypted: str,
    refresh_token_encrypted: str,
    token_expires_at: datetime,
) -> User:
    """Cria ou atualiza usuário com tokens do Spotify."""
    user = await get_user_by_id(db, user_id)
    
    if user:
        # Atualizar existente
        user.display_name = profile.get("display_name")
        user.email = profile.get("email")
        user.access_token_encrypted = access_token_encrypted
        user.refresh_token_encrypted = refresh_token_encrypted
        user.token_expires_at = token_expires_at
    else:
        # Criar novo
        user = User(
            id=user_id,
            display_name=profile.get("display_name"),
            email=profile.get("email"),
            access_token_encrypted=access_token_encrypted,
            refresh_token_encrypted=refresh_token_encrypted,
            token_expires_at=token_expires_at,
        )
        db.add(user)
    
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_tokens(
    db: AsyncSession,
    user_id: str,
    access_token_encrypted: str,
    refresh_token_encrypted: str,
    token_expires_at: datetime,
) -> None:
    """Atualiza apenas os tokens do usuário."""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            access_token_encrypted=access_token_encrypted,
            refresh_token_encrypted=refresh_token_encrypted,
            token_expires_at=token_expires_at,
        )
    )
    await db.commit()


async def update_last_sync(db: AsyncSession, user_id: str) -> None:
    """Atualiza timestamp do último sync."""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(last_sync_at=datetime.now(timezone.utc))
    )
    await db.commit()