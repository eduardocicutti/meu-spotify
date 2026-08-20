# app/library/router.py
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, get_spotify_client
from app.database import get_db
from app.library.schemas import LibraryIssues, LibraryStats
from app.library.service import (
    get_library_issues,
    get_library_stats,
    sync_library,
)
from app.spotify.client import SpotifyClient
from app.users.models import User

router = APIRouter()


@router.get("/stats", response_model=LibraryStats)
async def get_library_stats_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Estatísticas da biblioteca do usuário."""
    stats = await get_library_stats(db, current_user.id)
    return LibraryStats.model_validate(stats)


@router.get("/issues", response_model=LibraryIssues)
async def get_library_issues_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resumo dos problemas detectados na biblioteca."""
    issues = await get_library_issues(db, current_user.id)
    return LibraryIssues.model_validate(issues)


@router.post("/sync", status_code=202)
async def trigger_library_sync(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    spotify: SpotifyClient = Depends(get_spotify_client),
):
    """Trigger sincronização completa da biblioteca (background)."""
    background_tasks.add_task(sync_library, current_user.id, spotify)
    return {"message": "Sincronização iniciada em background", "status": "accepted"}
