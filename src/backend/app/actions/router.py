# app/actions/router.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.schemas import (
    ActionResponse,
    CreateFilterRequest,
    MergeRequest,
    ReverseRequest,
)
from app.actions.service import (
    create_playlist_from_filter,
    merge_playlists,
    reverse_playlist,
)
from app.auth.dependencies import get_current_user, get_spotify_client
from app.database import get_db
from app.spotify.client import SpotifyClient
from app.users.models import User

router = APIRouter()


@router.post("/create-from-filter", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist_filter(
    request: CreateFilterRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    spotify: SpotifyClient = Depends(get_spotify_client),
    db: AsyncSession = Depends(get_db),
):
    """Cria nova playlist baseada em filtros (gênero, década, artista, duração)."""
    playlist = await create_playlist_from_filter(
        user_id=current_user.id,
        spotify=spotify,
        db=db,
        genres=request.genres,
        decades=request.decades,
        artist_ids=request.artist_ids,
        max_duration_ms=request.max_duration_ms,
        name=request.name,
    )
    return ActionResponse.model_validate(playlist)


@router.post("/merge-playlists", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def merge_two_playlists(
    request: MergeRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    spotify: SpotifyClient = Depends(get_spotify_client),
    db: AsyncSession = Depends(get_db),
):
    """Junta duas playlists em uma nova (union por track_id)."""
    # Verify both playlists belong to user
    from app.playlists.service import get_playlist_detail
    pl1 = await get_playlist_detail(db, current_user.id, request.playlist_id_1)
    pl2 = await get_playlist_detail(db, current_user.id, request.playlist_id_2)
    if not pl1 or not pl2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uma ou ambas playlists não encontradas")

    playlist = await merge_playlists(
        user_id=current_user.id,
        spotify=spotify,
        db=db,
        playlist_id_1=request.playlist_id_1,
        playlist_id_2=request.playlist_id_2,
        name=request.name,
    )
    return ActionResponse.model_validate(playlist)


@router.post("/reverse-playlist", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def reverse_playlist_endpoint(
    request: ReverseRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    spotify: SpotifyClient = Depends(get_spotify_client),
    db: AsyncSession = Depends(get_db),
):
    """Cria nova playlist com ordem invertida."""
    from app.playlists.service import get_playlist_detail
    pl = await get_playlist_detail(db, current_user.id, request.playlist_id)
    if not pl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist não encontrada")

    playlist = await reverse_playlist(
        user_id=current_user.id,
        spotify=spotify,
        db=db,
        playlist_id=request.playlist_id,
        name=request.name,
    )
    return ActionResponse.model_validate(playlist)
