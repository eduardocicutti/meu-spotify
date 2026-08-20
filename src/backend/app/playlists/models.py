# app/playlists/models.py
from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey, Index, Text, func, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Spotify playlist ID
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    track_count: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_id: Mapped[str | None] = mapped_column(String(256))
    last_modified: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    synced_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="playlists")
    tracks: Mapped[list["PlaylistTrack"]] = relationship(back_populates="playlist", lazy="selectin")

    __table_args__ = (Index("ix_playlists_user_synced", "user_id", "synced_at"),)


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[str] = mapped_column(String(64), ForeignKey("playlists.id"), primary_key=True)
    track_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)  # permite duplicatas na mesma playlist
    track_name: Mapped[str] = mapped_column(String(512), nullable=False)
    artist_names: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    artist_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    album_name: Mapped[str | None] = mapped_column(String(512))
    album_id: Mapped[str | None] = mapped_column(String(64))
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer)  # extraído do album.release_date

    playlist: Mapped["Playlist"] = relationship(back_populates="tracks")

    __table_args__ = (
        Index("ix_playlist_tracks_track_id", "track_id"),
        Index("ix_playlist_tracks_artist_ids", "artist_ids", postgresql_using="gin"),
    )