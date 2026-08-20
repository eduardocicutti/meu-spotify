# app/library/schemas.py

from pydantic import BaseModel


class GenreDistributionItem(BaseModel):
    genre: str
    count: int
    percentage: float


class DecadeDistributionItem(BaseModel):
    decade: str
    count: int
    percentage: float


class LibraryStats(BaseModel):
    total_tracks: int
    total_artists: int
    total_hours: int
    top_artist: dict | None = None
    genre_distribution: dict[str, int] = {}
    decade_distribution: dict[str, int] = {}


class LibraryIssues(BaseModel):
    duplicates_intra_count: int = 0
    duplicates_intra_playlists_affected: int = 0
    duplicates_cross_count: int = 0
    abandoned_playlists_count: int = 0
    unavailable_tracks_count: int = 0

    # Detailed items (optional, for Issues page)
    duplicates_intra: list[dict] | None = None
    duplicates_cross: list[dict] | None = None
    abandoned_playlists: list[dict] | None = None
    unavailable_tracks: list[dict] | None = None
