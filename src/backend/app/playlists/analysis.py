# app/playlists/analysis.py
import logging
from datetime import UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.playlists.models import Playlist, PlaylistTrack

logger = logging.getLogger(__name__)


async def find_duplicates_intra(
    db: AsyncSession,
    user_id: str,
    playlist_id: str | None = None
) -> list[dict]:
    """
    Faixas duplicadas DENTRO da mesma playlist (mesmo track_id, posições diferentes).
    Se playlist_id não for fornecido, busca em todas as playlists do usuário.
    """
    base_query = (
        select(
            PlaylistTrack.playlist_id,
            PlaylistTrack.track_id,
            PlaylistTrack.track_name,
            func.array_agg(PlaylistTrack.position).label("positions"),
            func.count().label("count"),
            PlaylistTrack.artist_names,
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id)
    )

    if playlist_id:
        base_query = base_query.where(PlaylistTrack.playlist_id == playlist_id)

    stmt = base_query.group_by(
        PlaylistTrack.playlist_id,
        PlaylistTrack.track_id,
        PlaylistTrack.track_name,
        PlaylistTrack.artist_names,
    ).having(func.count() > 1)

    result = await db.execute(stmt)
    return [
        {
            "playlist_id": row.playlist_id,
            "track_id": row.track_id,
            "track_name": row.track_name,
            "artist_names": row.artist_names,
            "positions": row.positions,
            "count": row.count,
        }
        for row in result
    ]


async def find_duplicates_cross(
    db: AsyncSession,
    user_id: str
) -> list[dict]:
    """
    Faixas que aparecem em MÚLTIPLAS playlists do usuário.
    """
    stmt = (
        select(
            PlaylistTrack.track_id,
            PlaylistTrack.track_name,
            PlaylistTrack.artist_names,
            func.array_agg(PlaylistTrack.playlist_id).label("playlist_ids"),
            func.count(PlaylistTrack.playlist_id.distinct()).label("playlist_count"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id)
        .group_by(
            PlaylistTrack.track_id,
            PlaylistTrack.track_name,
            PlaylistTrack.artist_names,
        )
        .having(func.count(PlaylistTrack.playlist_id.distinct()) > 1)
        .order_by(func.count(PlaylistTrack.playlist_id.distinct()).desc())
    )
    result = await db.execute(stmt)
    return [
        {
            "track_id": row.track_id,
            "track_name": row.track_name,
            "artist_names": row.artist_names,
            "playlist_ids": row.playlist_ids,
            "playlist_count": row.playlist_count,
        }
        for row in result
    ]


async def find_abandoned_playlists(
    db: AsyncSession,
    user_id: str,
    days: int = 365
) -> list[dict]:
    """Playlists sem modificação há > N dias."""
    from datetime import datetime, timedelta
    cutoff = datetime.now(UTC) - timedelta(days=days)

    stmt = (
        select(Playlist)
        .where(
            Playlist.user_id == user_id,
            Playlist.last_modified < cutoff,
        )
        .order_by(Playlist.last_modified.asc())
    )
    result = await db.execute(stmt)
    playlists = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "track_count": p.track_count,
            "last_modified": p.last_modified.isoformat() if p.last_modified else None,
            "days_abandoned": (datetime.now(UTC) - p.last_modified).days if p.last_modified else None,
        }
        for p in playlists
    ]


async def find_unavailable_tracks(
    db: AsyncSession,
    user_id: str,
    playlist_id: str | None = None
) -> list[dict]:
    """Faixas marcadas como indisponíveis (removidas do catálogo)."""
    base_query = (
        select(PlaylistTrack, Playlist.name.label("playlist_name"))
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(
            Playlist.user_id == user_id,
            not PlaylistTrack.is_available,
        )
        .order_by(PlaylistTrack.added_at.desc())
    )

    if playlist_id:
        base_query = base_query.where(PlaylistTrack.playlist_id == playlist_id)

    result = await db.execute(base_query)
    return [
        {
            "track_id": row.PlaylistTrack.track_id,
            "track_name": row.PlaylistTrack.track_name,
            "artist_names": row.PlaylistTrack.artist_names,
            "playlist_id": row.PlaylistTrack.playlist_id,
            "playlist_name": row.playlist_name,
            "added_at": row.PlaylistTrack.added_at.isoformat(),
        }
        for row in result
    ]


async def find_unavailable_in_playlist(
    db: AsyncSession,
    user_id: str,
    playlist_id: str
) -> list[dict]:
    """Faixas indisponíveis em uma playlist específica."""
    return await find_unavailable_tracks(db, user_id, playlist_id)


async def find_duplicates_intra_playlist(
    db: AsyncSession,
    user_id: str,
    playlist_id: str
) -> list[dict]:
    """Alias para find_duplicates_intra com playlist específica."""
    return await find_duplicates_intra(db, user_id, playlist_id)


async def get_library_issues_summary(
    db: AsyncSession,
    user_id: str
) -> dict:
    """Resumo agregado para o dashboard."""
    dup_intra = await find_duplicates_intra(db, user_id)
    dup_cross = await find_duplicates_cross(db, user_id)
    abandoned = await find_abandoned_playlists(db, user_id)
    unavailable = await find_unavailable_tracks(db, user_id)

    return {
        "duplicates_intra_count": sum(d["count"] - 1 for d in dup_intra),
        "duplicates_intra_playlists_affected": len({d["playlist_id"] for d in dup_intra}),
        "duplicates_cross_count": len(dup_cross),
        "abandoned_playlists_count": len(abandoned),
        "unavailable_tracks_count": len(unavailable),
    }
