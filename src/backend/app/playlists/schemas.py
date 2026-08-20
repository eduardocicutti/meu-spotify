# app/playlists/schemas.py
from datetime import datetime

from pydantic import BaseModel


class PlaylistBase(BaseModel):
    id: str
    name: str
    description: str | None = None
    track_count: int
    images: list[dict] = []
    last_modified: datetime | None = None
    snapshot_id: str | None = None
    has_issues: bool = False
    issues_count: int = 0

    class Config:
        from_attributes = True


class PlaylistRead(PlaylistBase):
    pass


class PlaylistTrackRead(BaseModel):
    track_id: str
    track_name: str
    artist_names: list[str]
    artist_ids: list[str]
    album_name: str | None = None
    album_id: str | None = None
    duration_ms: int
    added_at: datetime
    is_available: bool
    release_year: int | None = None
    position: int

    class Config:
        from_attributes = True


class PlaylistDetail(PlaylistBase):
    tracks: list[PlaylistTrackRead] = []


class PlaylistIssues(BaseModel):
    duplicates_intra_count: int = 0
    unavailable_count: int = 0
    duplicates_intra: list[dict] | None = None
    unavailable_tracks: list[dict] | None = None


class PlaylistSorted(BaseModel):
    playlist_id: str
    tracks: list[PlaylistTrackRead]
    sort_by: str
