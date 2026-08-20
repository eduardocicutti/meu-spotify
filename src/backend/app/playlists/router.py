# app/playlists/router.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.playlists.schemas import (
    PlaylistDetail,
    PlaylistIssues,
    PlaylistRead,
    PlaylistSorted,
)
from app.playlists.service import (
    get_playlist_detail,
    get_playlist_issues,
    get_sorted_tracks,
    get_user_playlists,
)

router = APIRouter()


@router.get("", response_model=list[PlaylistRead])
async def list_playlists(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista playlists do usuário com paginação."""
    playlists = await get_user_playlists(db, current_user.id, limit, offset)
    return [PlaylistRead.model_validate(p) for p in playlists]


@router.get("/{playlist_id}", response_model=PlaylistDetail)
async def get_playlist(
    playlist_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detalhes de uma playlist com todas as faixas."""
    playlist = await get_playlist_detail(db, current_user.id, playlist_id)
    if not playlist:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist não encontrada")
    return PlaylistDetail.model_validate(playlist)


@router.get("/{playlist_id}/issues", response_model=PlaylistIssues)
async def get_playlist_issues_endpoint(
    playlist_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Problemas detectados em uma playlist específica."""
    issues = await get_playlist_issues(db, current_user.id, playlist_id)
    return PlaylistIssues.model_validate(issues)


@router.get("/{playlist_id}/sorted", response_model=PlaylistSorted)
async def get_sorted_playlist(
    playlist_id: str,
    by: str = Query("artist", pattern="^(artist|album|duration)$"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna faixas da playlist ordenadas (client-side sort via API)."""
    sorted_data = await get_sorted_tracks(db, current_user.id, playlist_id, by)
    return PlaylistSorted.model_validate(sorted_data)
