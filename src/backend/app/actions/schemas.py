# app/actions/schemas.py

from pydantic import BaseModel


class CreateFilterRequest(BaseModel):
    genres: list[str] | None = None
    decades: list[str] | None = None
    artist_ids: list[str] | None = None
    max_duration_ms: int | None = None
    name: str | None = None


class MergeRequest(BaseModel):
    playlist_id_1: str
    playlist_id_2: str
    name: str | None = None


class ReverseRequest(BaseModel):
    playlist_id: str
    name: str | None = None


class ActionResponse(BaseModel):
    playlist_id: str
    name: str
    track_count: int
