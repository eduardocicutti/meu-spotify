# app/users/schemas.py
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: str
    display_name: str | None = None
    email: EmailStr | None = None


class UserRead(UserBase):
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_tracks: int
    total_artists: int
    total_hours: int
    top_artist: dict | None = None
    genre_distribution: dict = {}
    decade_distribution: dict = {}
