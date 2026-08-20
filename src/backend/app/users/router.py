# app/users/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User
from app.users.schemas import UserRead, UserStats

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Retorna perfil do usuário autenticado."""
    return UserRead.model_validate(current_user)


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna estatísticas rápidas do usuário."""
    from app.library.service import get_library_stats
    stats = await get_library_stats(db, current_user.id)
    return UserStats.model_validate(stats)
