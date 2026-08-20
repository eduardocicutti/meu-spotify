# app/actions/service.py
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.playlists.models import Playlist, PlaylistTrack
from app.spotify.client import SpotifyClient
from app.spotify.endpoints import ENDPOINTS

logger = logging.getLogger(__name__)


async def create_playlist_from_filter(
    user_id: str,
    spotify: SpotifyClient,
    db: AsyncSession,
    genres: list[str] | None = None,
    decades: list[str] | None = None,
    artist_ids: list[str] | None = None,
    max_duration_ms: int | None = None,
    name: str | None = None,
) -> dict:
    """Cria nova playlist baseada em filtros aplicados à biblioteca do usuário."""

    # 1. Buscar todas as faixas do usuário (library + playlists) do banco
    candidate_tracks = await get_user_all_tracks(db, user_id)

    # 2. Aplicar filtros em memória
    filtered = candidate_tracks

    if genres:
        filtered = [t for t in filtered if any(g in t.get("artist_genres", []) for g in genres)]

    if decades:
        filtered = [t for t in filtered if t.get("decade") in decades]

    if artist_ids:
        filtered = [t for t in filtered if any(a in artist_ids for a in t.get("artist_ids", []))]

    if max_duration_ms:
        filtered = [t for t in filtered if t.get("duration_ms", 0) <= max_duration_ms]

    # 3. Limitar a 10k tracks (limite API Spotify por playlist)
    track_uris = [f"spotify:track:{t['track_id']}" for t in filtered[:10000]]

    if not track_uris:
        raise ValueError("Nenhuma faixa encontrada com os filtros selecionados")

    # 4. Criar playlist no Spotify
    from datetime import date
    playlist_name = name or f"Meu Spotify — Filtro — {date.today().isoformat()}"

    playlist = await spotify.post(ENDPOINTS["me_playlists"], {
        "name": playlist_name,
        "public": False,
        "description": f"Criada via Meu Spotify em {date.today().isoformat()}"
    })

    # 5. Adicionar faixas em batches de 100
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        await spotify.post(
            ENDPOINTS["playlist_items"].format(playlist_id=playlist["id"]),
            {"uris": batch}
        )

    # 6. Invalidar cache e retornar
    await invalidate_user_cache(user_id, "playlists")

    return {
        "playlist_id": playlist["id"],
        "name": playlist["name"],
        "track_count": len(track_uris),
    }


async def merge_playlists(
    user_id: str,
    spotify: SpotifyClient,
    db: AsyncSession,
    playlist_id_1: str,
    playlist_id_2: str,
    name: str | None = None,
) -> dict:
    """Junta duas playlists em uma nova (union por track_id)."""

    # Fetch both playlists from Spotify
    pl1 = await spotify.get(ENDPOINTS["playlist_items"].format(playlist_id=playlist_id_1))
    pl2 = await spotify.get(ENDPOINTS["playlist_items"].format(playlist_id=playlist_id_2))

    # Extract track URIs
    tracks_1 = {item["track"]["id"] for item in pl1.get("items", []) if item.get("track")}
    tracks_2 = {item["track"]["id"] for item in pl2.get("items", []) if item.get("track")}

    # Union
    all_track_ids = tracks_1 | tracks_2
    track_uris = [f"spotify:track:{tid}" for tid in all_track_ids]

    if not track_uris:
        raise ValueError("Nenhuma faixa encontrada nas playlists selecionadas")

    # Create new playlist
    from datetime import date
    playlist_name = name or f"Merge — {date.today().isoformat()}"

    playlist = await spotify.post(ENDPOINTS["me_playlists"], {
        "name": playlist_name,
        "public": False,
        "description": "Merge de playlists via Meu Spotify"
    })

    # Add tracks in batches
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        await spotify.post(
            ENDPOINTS["playlist_items"].format(playlist_id=playlist["id"]),
            {"uris": batch}
        )

    await invalidate_user_cache(user_id, "playlists")

    return {
        "playlist_id": playlist["id"],
        "name": playlist["name"],
        "track_count": len(track_uris),
    }


async def reverse_playlist(
    user_id: str,
    spotify: SpotifyClient,
    db: AsyncSession,
    playlist_id: str,
    name: str | None = None,
) -> dict:
    """Cria nova playlist com ordem invertida."""

    # Fetch playlist tracks
    pl_data = await spotify.get(ENDPOINTS["playlist_items"].format(playlist_id=playlist_id))
    items = pl_data.get("items", [])

    track_uris = [
        f"spotify:track:{item['track']['id']}"
        for item in reversed(items)
        if item.get("track")
    ]

    if not track_uris:
        raise ValueError("Playlist não tem faixas disponíveis")

    # Create new playlist
    from datetime import date
    playlist_name = name or f"Reverso — {date.today().isoformat()}"

    playlist = await spotify.post(ENDPOINTS["me_playlists"], {
        "name": playlist_name,
        "public": False,
        "description": "Playlist invertida via Meu Spotify"
    })

    # Add tracks in batches
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        await spotify.post(
            ENDPOINTS["playlist_items"].format(playlist_id=playlist["id"]),
            {"uris": batch}
        )

    await invalidate_user_cache(user_id, "playlists")

    return {
        "playlist_id": playlist["id"],
        "name": playlist["name"],
        "track_count": len(track_uris),
    }


async def get_user_all_tracks(db: AsyncSession, user_id: str) -> list[dict]:
    """Busca todas as faixas únicas do usuário (library + playlists)."""

    stmt = (
        select(
            PlaylistTrack.track_id,
            PlaylistTrack.track_name,
            PlaylistTrack.artist_names,
            PlaylistTrack.artist_ids,
            PlaylistTrack.album_name,
            PlaylistTrack.duration_ms,
            PlaylistTrack.release_year,
            PlaylistTrack.is_available,
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(
            Playlist.user_id == user_id,
            PlaylistTrack.is_available,
        )
        .distinct(PlaylistTrack.track_id)
    )
    result = await db.execute(stmt)

    tracks = []
    for row in result:
        tracks.append({
            "track_id": row.track_id,
            "track_name": row.track_name,
            "artist_names": row.artist_names,
            "artist_ids": row.artist_ids,
            "album_name": row.album_name,
            "duration_ms": row.duration_ms,
            "release_year": row.release_year,
            "decade": f"{(row.release_year // 10) * 10}s" if row.release_year else None,
            "is_available": row.is_available,
        })

    return tracks


async def invalidate_user_cache(user_id: str, resource: str = None):
    """Invalida cache Redis do usuário."""
    import redis.asyncio as redis

    from app.config import get_settings

    settings = get_settings()
    r = redis.from_url(settings.REDIS_URL)

    try:
        pattern = f"spotify:{user_id}:*" if not resource else f"spotify:{user_id}:{resource}:*"
        keys = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await r.delete(*keys)
    finally:
        await r.close()
