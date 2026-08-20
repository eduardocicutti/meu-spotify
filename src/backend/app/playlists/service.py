# app/playlists/service.py
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.playlists.models import Playlist, PlaylistTrack
from app.spotify.client import SpotifyClient
from app.spotify.endpoints import ENDPOINTS, FIELDS

logger = logging.getLogger(__name__)


async def get_user_playlists(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
    offset: int = 0
) -> list[Playlist]:
    """Lista playlists do usuário do banco."""
    stmt = (
        select(Playlist)
        .where(Playlist.user_id == user_id)
        .order_by(Playlist.last_modified.desc().nullslast())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_playlist_detail(
    db: AsyncSession,
    user_id: str,
    playlist_id: str
) -> Playlist | None:
    """Busca playlist com tracks do banco."""
    stmt = (
        select(Playlist)
        .where(Playlist.id == playlist_id, Playlist.user_id == user_id)
        .options(selectinload(Playlist.tracks))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_playlist_issues(
    db: AsyncSession,
    user_id: str,
    playlist_id: str
) -> dict:
    """Problemas de uma playlist específica."""
    from app.playlists.analysis import (
        find_duplicates_intra_playlist,
        find_unavailable_in_playlist,
    )

    duplicates = await find_duplicates_intra_playlist(db, user_id, playlist_id)
    unavailable = await find_unavailable_in_playlist(db, user_id, playlist_id)

    return {
        "duplicates_intra_count": len(duplicates),
        "unavailable_count": len(unavailable),
        "duplicates_intra": duplicates,
        "unavailable_tracks": unavailable,
    }


async def get_sorted_tracks(
    db: AsyncSession,
    user_id: str,
    playlist_id: str,
    sort_by: str
) -> dict:
    """Retorna tracks ordenadas (para API)."""
    playlist = await get_playlist_detail(db, user_id, playlist_id)
    if not playlist:
        return {"playlist_id": playlist_id, "tracks": [], "sort_by": sort_by}

    tracks = list(playlist.tracks)

    if sort_by == "artist":
        tracks.sort(key=lambda t: t.artist_names[0] if t.artist_names else "")
    elif sort_by == "album":
        tracks.sort(key=lambda t: t.album_name or "")
    elif sort_by == "duration":
        tracks.sort(key=lambda t: t.duration_ms)

    return {
        "playlist_id": playlist_id,
        "tracks": tracks,
        "sort_by": sort_by,
    }


async def sync_user_playlists(
    db: AsyncSession,
    user_id: str,
    spotify: SpotifyClient,
) -> dict:
    """Sincroniza playlists do usuário com Spotify API."""
    logger.info(f"Syncing playlists for user {user_id}")

    # Fetch all playlists from Spotify
    playlists_data = await spotify.paginate(
        ENDPOINTS["me_playlists"],
        params={"limit": 50}
    )

    synced = 0
    errors = 0

    for pl_data in playlists_data:
        try:
            await upsert_playlist(db, user_id, pl_data, spotify)
            synced += 1
        except Exception as e:
            logger.error(f"Error syncing playlist {pl_data.get('id')}: {e}")
            errors += 1

    # Update user last_sync
    from app.users.service import update_last_sync
    await update_last_sync(db, user_id)

    return {"synced": synced, "errors": errors, "total": len(playlists_data)}


async def upsert_playlist(
    db: AsyncSession,
    user_id: str,
    pl_data: dict,
    spotify: SpotifyClient,
) -> Playlist:
    """Cria/atualiza playlist e suas tracks."""
    playlist_id = pl_data["id"]
    snapshot_id = pl_data.get("snapshot_id")

    # Check if playlist exists and snapshot matches
    existing = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = existing.scalar_one_or_none()

    if playlist and playlist.snapshot_id == snapshot_id:
        # No changes, skip track fetching
        return playlist

    # Fetch tracks from Spotify
    tracks_data = await spotify.paginate(
        ENDPOINTS["playlist_items"].format(playlist_id=playlist_id),
        params={"limit": 100, "fields": FIELDS["playlist_items"]}
    )

    # Prepare track data
    track_objects = []
    for idx, item in enumerate(tracks_data):
        track = item.get("track")
        if not track or not track.get("id"):
            # Unavailable track
            track_objects.append({
                "track_id": f"unavailable_{item.get('added_at', idx)}",
                "track_name": item.get("track", {}).get("name", "Faixa indisponível"),
                "artist_names": [a.get("name", "Desconhecido") for a in item.get("track", {}).get("artists", [])],
                "artist_ids": [a.get("id", "") for a in item.get("track", {}).get("artists", [])],
                "album_name": item.get("track", {}).get("album", {}).get("name"),
                "album_id": item.get("track", {}).get("album", {}).get("id"),
                "duration_ms": item.get("track", {}).get("duration_ms", 0),
                "added_at": item.get("added_at"),
                "is_available": False,
                "release_year": extract_year(item.get("track", {}).get("album", {}).get("release_date")),
                "position": idx,
            })
            continue

        track_objects.append({
            "track_id": track["id"],
            "track_name": track["name"],
            "artist_names": [a["name"] for a in track.get("artists", [])],
            "artist_ids": [a["id"] for a in track.get("artists", [])],
            "album_name": track.get("album", {}).get("name"),
            "album_id": track.get("album", {}).get("id"),
            "duration_ms": track.get("duration_ms", 0),
            "added_at": item.get("added_at"),
            "is_available": track.get("is_available", True),
            "release_year": extract_year(track.get("album", {}).get("release_date")),
            "position": idx,
        })

    # Upsert playlist
    if playlist:
        playlist.name = pl_data.get("name", "")
        playlist.description = pl_data.get("description")
        playlist.track_count = len(track_objects)
        playlist.snapshot_id = snapshot_id
        playlist.last_modified = parse_iso_datetime(pl_data.get("updated_at")) if pl_data.get("updated_at") else None
    else:
        playlist = Playlist(
            id=playlist_id,
            user_id=user_id,
            name=pl_data.get("name", ""),
            description=pl_data.get("description"),
            track_count=len(track_objects),
            snapshot_id=snapshot_id,
            last_modified=parse_iso_datetime(pl_data.get("updated_at")) if pl_data.get("updated_at") else None,
        )
        db.add(playlist)

    await db.flush()

    # Delete old tracks and insert new ones
    await db.execute(
        PlaylistTrack.__table__.delete().where(PlaylistTrack.playlist_id == playlist_id)
    )

    for track_data in track_objects:
        track_data["playlist_id"] = playlist_id
        db.add(PlaylistTrack(**track_data))

    await db.commit()
    await db.refresh(playlist)

    return playlist


def extract_year(release_date: str | None) -> int | None:
    """Extrai ano do release_date do Spotify."""
    if not release_date:
        return None
    try:
        return int(release_date[:4])
    except (ValueError, IndexError):
        return None


def parse_iso_datetime(date_str: str) -> datetime | None:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None
