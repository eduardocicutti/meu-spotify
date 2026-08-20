# app/library/service.py
import json
import logging

import redis.asyncio as redis
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decrypt_token
from app.playlists.models import Playlist, PlaylistTrack
from app.spotify.client import SpotifyClient
from app.users.service import get_user_by_id

logger = logging.getLogger(__name__)


async def get_library_stats(db: AsyncSession, user_id: str) -> dict:
    """Calcula estatísticas da biblioteca do usuário."""

    # Total de faixas únicas na biblioteca
    stmt = (
        select(
            func.count(distinct(PlaylistTrack.track_id)).label("unique_tracks"),
            func.count(distinct(PlaylistTrack.artist_ids[0])).label("unique_artists"),
            func.sum(PlaylistTrack.duration_ms).label("total_duration_ms"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id, PlaylistTrack.is_available)
    )
    result = await db.execute(stmt)
    row = result.one()

    unique_tracks = row.unique_tracks or 0
    unique_artists = row.unique_artists or 0
    total_duration_ms = row.total_duration_ms or 0
    total_hours = round(total_duration_ms / 3_600_000)

    # Top artista (mais faixas)
    stmt_top = (
        select(
            PlaylistTrack.artist_ids[0].label("artist_id"),
            PlaylistTrack.artist_names[0].label("artist_name"),
            func.count().label("track_count"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id, PlaylistTrack.is_available)
        .group_by("artist_id", "artist_name")
        .order_by(func.count().desc())
        .limit(1)
    )
    top_result = await db.execute(stmt_top)
    top_artist = top_result.first()

    # Distribuição por década
    stmt_decade = (
        select(
            (PlaylistTrack.release_year // 10 * 10).label("decade"),
            func.count().label("count"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(
            Playlist.user_id == user_id,
            PlaylistTrack.is_available == True,
            PlaylistTrack.release_year.is_not(None),
        )
        .group_by("decade")
        .order_by("decade")
    )
    decade_result = await db.execute(stmt_decade)
    decades = {f"{row.decade}s": row.count for row in decade_result}

    # Distribuição por gênero (via artist_genres cache)
    genre_distribution = await calculate_genre_distribution(db, user_id)

    return {
        "total_tracks": unique_tracks,
        "total_artists": unique_artists,
        "total_hours": total_hours,
        "top_artist": {"name": top_artist.artist_name, "track_count": top_artist.track_count} if top_artist else None,
        "genre_distribution": genre_distribution,
        "decade_distribution": decades,
    }


async def calculate_genre_distribution(db: AsyncSession, user_id: str) -> dict[str, int]:
    """Calcula distribuição por gênero usando cache Redis de artist_genres."""
    from app.config import get_settings
    settings = get_settings()

    # Buscar artist_ids e contagens
    stmt = (
        select(
            PlaylistTrack.artist_ids[0].label("artist_id"),
            func.count().label("track_count"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id, PlaylistTrack.is_available)
        .group_by("artist_id")
    )
    result = await db.execute(stmt)
    artist_counts = {row.artist_id: row.track_count for row in result}

    # Buscar gêneros via cache Redis + Spotify API
    genre_counter = {}
    r = redis.from_url(settings.REDIS_URL)

    user = await get_user_by_id(db, user_id)
    if not user:
        return {}

    spotify = SpotifyClient(decrypt_token(user.access_token_encrypted))

    try:
        for artist_id, count in artist_counts.items():
            cache_key = f"artist_genres:{artist_id}"

            cached = await r.get(cache_key)
            if cached:
                genres = json.loads(cached)
            else:
                try:
                    artist = await spotify.get(f"/artists/{artist_id}")
                    genres = artist.get("genres", [])
                    await r.setex(cache_key, settings.CACHE_TTL_ARTIST_GENRES, json.dumps(genres))
                except Exception as e:
                    logger.warning(f"Failed to fetch genres for artist {artist_id}: {e}")
                    genres = []

            for g in genres:
                genre_counter[g] = genre_counter.get(g, 0) + count

    finally:
        await spotify.close()
        await r.close()

    # Top 10 gêneros
    return dict(sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)[:10])


async def get_library_issues(db: AsyncSession, user_id: str) -> dict:
    """Resumo dos problemas da biblioteca."""
    from app.playlists.analysis import get_library_issues_summary
    return await get_library_issues_summary(db, user_id)


async def sync_library(
    user_id: str,
    spotify: SpotifyClient,
) -> dict:
    """Sincronização completa da biblioteca (chamada em background)."""
    from app.database import AsyncSessionLocal
    from app.playlists.service import sync_user_playlists

    logger.info(f"Starting full library sync for user {user_id}")

    async with AsyncSessionLocal() as db:
        try:
            result = await sync_user_playlists(db, user_id, spotify)
            logger.info(f"Library sync completed for user {user_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Library sync failed for user {user_id}: {e}")
            raise
