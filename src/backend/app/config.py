# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    FERNET_KEY: str

    # Spotify
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/auth/callback"
    SPOTIFY_SCOPES: str = "user-read-private user-read-email user-library-read playlist-read-private playlist-read-collaborative"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Frontend (CORS)
    FRONTEND_URL: str = "http://127.0.0.1:5173"

    # Cache TTLs (seconds)
    CACHE_TTL_USER_PROFILE: int = 3600
    CACHE_TTL_PLAYLISTS: int = 300
    CACHE_TTL_PLAYLIST_TRACKS: int = 600
    CACHE_TTL_LIBRARY_STATS: int = 900
    CACHE_TTL_ARTIST_GENRES: int = 86400

    # Rate limit Spotify (req/s)
    SPOTIFY_RATE_LIMIT: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()