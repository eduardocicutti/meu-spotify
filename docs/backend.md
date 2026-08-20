# Backend — Meu Spotify (FastAPI)

## 1. Stack e Versões

| Componente | Versão | Justificativa |
|------------|--------|---------------|
| Python | 3.12 | LTS, performance, typing moderno |
| FastAPI | 0.115+ | Async nativo, OpenAPI automático, validação Pydantic |
| Uvicorn | 0.30+ | ASGI server produção |
| PostgreSQL | 16 | JSONB, índices compostos, confiabilidade |
| SQLAlchemy | 2.0.x | Async ORM, 2.0 style, type hints |
| Alembic | 1.13+ | Migrations versionadas |
| Redis | 7 | Cache + sessões, TTL, pub/sub |
| Pydantic | 2.x | Validação, settings, serialization |
| python-jose | 3.3+ | JWT para cookies assinados |
| cryptography | 42+ | Fernet para criptografar tokens |
| httpx | 0.27+ | Async HTTP client para Spotify API |
| pytest | 8.x | Testes async, fixtures, coverage |
| ruff | 0.5+ | Lint + format (substitui flake8, black, isort) |
| mypy | 1.10+ | Type checking strict |

---

## 2. Estrutura de Pastas (Detalhada)

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory, middleware, routers
│   ├── config.py               # Settings (pydantic-settings, .env)
│   ├── database.py             # Engine, SessionLocal, Base, init_db
│   ├── dependencies.py         # FastAPI dependencies (DB, user atual, Spotify client)
│   │
│   ├── auth/
│   │   ├── router.py           # GET /login, GET /callback, POST /logout, GET /me
│   │   ├── service.py          # OAuth flow, token exchange, refresh, revoke
│   │   ├── schemas.py          # Pydantic: TokenResponse, UserResponse
│   │   ├── dependencies.py     # get_current_user, require_auth
│   │   └── security.py         # Fernet encryption, cookie signing, JWT
│   │
│   ├── spotify/
│   │   ├── client.py           # SpotifyClient: rate limit, retry, paginate, raw requests
│   │   ├── schemas.py          # Pydantic models para responses da API Spotify
│   │   ├── endpoints.py        # Constantes de URLs, scopes, field masks
│   │   └── exceptions.py       # SpotifyAPIError, RateLimitError, TokenExpiredError
│   │
│   ├── users/
│   │   ├── router.py           # GET /users/me (perfil + stats rápidos)
│   │   ├── models.py           # User (SQLAlchemy)
│   │   ├── schemas.py          # UserRead, UserStats
│   │   └── service.py          # CRUD user, token management
│   │
│   ├── playlists/
│   │   ├── router.py           # GET /playlists, GET /playlists/{id}, GET /playlists/{id}/issues
│   │   ├── models.py           # Playlist, PlaylistTrack (SQLAlchemy)
│   │   ├── schemas.py          # PlaylistRead, PlaylistTrackRead, PlaylistIssues
│   │   ├── service.py          # Fetch + cache + sync playlists
│   │   └── analysis.py         # Lógica: duplicatas, abandono, indisponíveis
│   │
│   ├── library/
│   │   ├── router.py           # GET /library/stats, GET /library/issues, POST /library/sync
│   │   ├── service.py          # Agregações: contagens, horas, distribuições
│   │   ├── stats.py            # Funções puras de cálculo (testáveis)
│   │   └── schemas.py          # LibraryStats, LibraryIssues, GenreDistribution, DecadeDistribution
│   │
│   └── actions/
│       ├── router.py           # POST /actions/create-from-filter, POST /actions/merge-playlists, POST /actions/reverse-playlist
│       ├── service.py          # Operações de escrita no Spotify (V1: cria novas playlists)
│       └── schemas.py          # CreateFilterRequest, MergeRequest, ActionResponse
│
├── migrations/                 # Alembic (gerado)
├── tests/
│   ├── conftest.py             # Fixtures: db, client, mock_spotify, auth_headers
│   ├── unit/
│   │   ├── test_auth.py
│   │   ├── test_spotify_client.py
│   │   ├── test_analysis.py
│   │   └── test_stats.py
│   └── integration/
│       ├── test_auth_flow.py
│       └── test_sync.py
│
├── scripts/
│   ├── seed_dev.py             # Seed para desenvolvimento
│   └── generate_fernet_key.py  # Utilitário
│
├── requirements.txt            # Produção
├── requirements-dev.txt        # Dev (pytest, ruff, mypy, etc.)
├── pyproject.toml              # Config: ruff, mypy, pytest, coverage
├── Dockerfile
├── .env.example
└── alembic.ini
```

---

## 3. Configuração (config.py)

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    ENVIRONMENT: str = "development"
    SECRET_KEY: str  # para assinar cookies JWT
    FERNET_KEY: str  # 32 bytes base64 para criptografar tokens

    # Spotify
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8000/auth/callback"
    SPOTIFY_SCOPES: str = "user-read-private user-read-email user-library-read playlist-read-private playlist-read-collaborative"

    # Database
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@localhost:5432/meuSpotify

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Frontend (CORS)
    FRONTEND_URL: str = "http://127.0.0.1:5173"

    # Cache TTLs (segundos)
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
```

---

## 4. Models (SQLAlchemy 2.0)

```python
# app/users/models.py
from sqlalchemy import String, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Spotify user ID
    display_name: Mapped[str | None] = mapped_column(String(256))
    email: Mapped[str | None] = mapped_column(String(256))
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_sync_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
```

```python
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
```

---

## 5. Spotify Client (Core)

```python
# app/spotify/client.py
import asyncio
import logging
from typing import Any
import httpx
from app.config import get_settings
from app.spotify.exceptions import SpotifyAPIError, RateLimitError, TokenExpiredError

logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self, access_token: str):
        self.token = access_token
        self.base_url = "https://api.spotify.com/v1"
        self.settings = get_settings()
        self._semaphore = asyncio.Semaphore(int(self.settings.SPOTIFY_RATE_LIMIT))
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.token}", **kwargs.pop("headers", {})}
        
        async with self._semaphore:
            for attempt in range(3):
                resp = await self._client.request(method, url, headers=headers, **kwargs)
                
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                    logger.warning(f"Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                
                if resp.status_code == 401:
                    raise TokenExpiredError("Access token expired")
                
                if 500 <= resp.status_code < 600:
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                return resp
            
            raise SpotifyAPIError(f"Max retries exceeded for {method} {path}")

    async def get(self, path: str, params: dict = None) -> dict:
        resp = await self._request("GET", path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, json: dict = None) -> dict:
        resp = await self._request("POST", path, json=json)
        resp.raise_for_status()
        return resp.json()

    async def put(self, path: str, json: dict = None) -> dict:
        resp = await self._request("PUT", path, json=json)
        resp.raise_for_status()
        return resp.json()

    async def delete(self, path: str, params: dict = None) -> dict:
        resp = await self._request("DELETE", path, params=params)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    async def paginate(self, path: str, params: dict = None, limit: int = None) -> list[dict]:
        """Percorre todas as páginas de um endpoint paginado."""
        results = []
        url = f"{self.base_url}{path}"
        fetched = 0
        
        while url and (limit is None or fetched < limit):
            # Se url já é absoluta, não usar base_url
            if url.startswith("http"):
                full_url = url
            else:
                full_url = f"{self.base_url}{url}"
            
            # Para URLs absolutas, extrair path e params do next
            if full_url.startswith(self.base_url):
                local_path = full_url[len(self.base_url):]
                # O 'next' já inclui query params
                data = await self._request("GET", local_path)
            else:
                data = await self._request("GET", full_url)
            
            items = data.get("items", [])
            results.extend(items)
            fetched += len(items)
            
            url = data.get("next")
            if limit and fetched >= limit:
                results = results[:limit]
                break
        
        return results

    async def close(self):
        await self._client.aclose()
```

---

## 6. Autenticação (OAuth Flow)

```python
# app/auth/service.py
import secrets
from urllib.parse import urlencode
import httpx
from app.config import get_settings
from app.auth.security import encrypt_token, decrypt_token
from app.users.service import upsert_user
from app.database import SessionLocal

settings = get_settings()

def get_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": settings.SPOTIFY_SCOPES,
        "state": state,
        "show_dialog": "true",
    }
    return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

async def exchange_code_for_tokens(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            },
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

async def refresh_access_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
        )
        resp.raise_for_status()
        return resp.json()

async def handle_callback(code: str, state: str) -> str:
    """Troca code por tokens, busca perfil, cria/atualiza user, retorna session_id."""
    token_data = await exchange_code_for_tokens(code)
    
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data["expires_in"]
    
    # Buscar perfil do usuário
    from app.spotify.client import SpotifyClient
    spotify = SpotifyClient(access_token)
    profile = await spotify.get("/me")
    await spotify.close()
    
    user_id = profile["id"]
    
    # Criptografar tokens
    enc_access = encrypt_token(access_token)
    enc_refresh = encrypt_token(refresh_token)
    
    # Upsert user no banco
    async with SessionLocal() as db:
        user = await upsert_user(db, user_id, profile, enc_access, enc_refresh, expires_in)
    
    # Criar sessão (JWT em cookie HttpOnly)
    from app.auth.security import create_session_cookie
    session_cookie = create_session_cookie(user_id)
    
    return session_cookie
```

```python
# app/auth/security.py
import base64
import time
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from jose import jwt
from app.config import get_settings

settings = get_settings()

# Fernet para tokens do Spotify
_fernet = Fernet(settings.FERNET_KEY.encode())

def encrypt_token(token: str) -> str:
    return _fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return _fernet.decrypt(encrypted.encode()).decode()

# JWT para sessão do usuário (cookie)
def create_session_cookie(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 7 * 24 * 3600,  # 7 dias
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def verify_session_cookie(cookie: str) -> str | None:
    try:
        payload = jwt.decode(cookie, settings.SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.JWTError:
        return None
```

---

## 7. Dependencies (FastAPI)

```python
# app/dependencies.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.auth.security import verify_session_cookie
from app.users.service import get_user_by_id
from app.spotify.client import SpotifyClient
from app.config import get_settings

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user_id(request: Request) -> str:
    cookie = request.cookies.get("session")
    if not cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    user_id = verify_session_cookie(cookie)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")
    return user_id

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return user

async def get_spotify_client(user: User = Depends(get_current_user)) -> SpotifyClient:
    from app.auth.security import decrypt_token
    access_token = decrypt_token(user.access_token_encrypted)
    return SpotifyClient(access_token)
```

---

## 8. Análise de Playlists (Duplicatas, Abandono, Indisponíveis)

```python
# app/playlists/analysis.py
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.playlists.models import Playlist, PlaylistTrack
from typing import List, Dict, Any
from collections import Counter

async def find_duplicates_intra(db: AsyncSession, user_id: str) -> List[Dict]:
    """Faixas duplicadas DENTRO da mesma playlist (mesmo track_id, posições diferentes)."""
    stmt = (
        select(
            PlaylistTrack.playlist_id,
            PlaylistTrack.track_id,
            PlaylistTrack.track_name,
            func.array_agg(PlaylistTrack.position).label("positions"),
            func.count().label("count"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id)
        .group_by(PlaylistTrack.playlist_id, PlaylistTrack.track_id, PlaylistTrack.track_name)
        .having(func.count() > 1)
    )
    result = await db.execute(stmt)
    return [
        {
            "playlist_id": row.playlist_id,
            "track_id": row.track_id,
            "track_name": row.track_name,
            "positions": row.positions,
            "count": row.count,
        }
        for row in result
    ]

async def find_duplicates_cross(db: AsyncSession, user_id: str) -> List[Dict]:
    """Faixas que aparecem em MÚLTIPLAS playlists do usuário."""
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
        .group_by(PlaylistTrack.track_id, PlaylistTrack.track_name, PlaylistTrack.artist_names)
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

async def find_abandoned_playlists(db: AsyncSession, user_id: str, days: int = 365) -> List[Dict]:
    """Playlists sem modificação há > N dias."""
    from datetime import datetime, timedelta, timezone
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
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
            "days_abandoned": (datetime.now(timezone.utc) - p.last_modified).days if p.last_modified else None,
        }
        for p in playlists
    ]

async def find_unavailable_tracks(db: AsyncSession, user_id: str) -> List[Dict]:
    """Faixas marcadas como indisponíveis (removidas do catálogo)."""
    stmt = (
        select(PlaylistTrack, Playlist.name.label("playlist_name"))
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(
            Playlist.user_id == user_id,
            PlaylistTrack.is_available == False,
        )
        .order_by(PlaylistTrack.added_at.desc())
    )
    result = await db.execute(stmt)
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

async def get_library_issues_summary(db: AsyncSession, user_id: str) -> Dict[str, Any]:
    """Resumo agregado para o dashboard."""
    dup_intra = await find_duplicates_intra(db, user_id)
    dup_cross = await find_duplicates_cross(db, user_id)
    abandoned = await find_abandoned_playlists(db, user_id)
    unavailable = await find_unavailable_tracks(db, user_id)
    
    return {
        "duplicates_intra_count": sum(d["count"] - 1 for d in dup_intra),  # quantas faixas extras
        "duplicates_intra_playlists_affected": len(set(d["playlist_id"] for d in dup_intra)),
        "duplicates_cross_count": len(dup_cross),
        "abandoned_playlists_count": len(abandoned),
        "unavailable_tracks_count": len(unavailable),
    }
```

---

## 9. Estatísticas da Biblioteca

```python
# app/library/stats.py
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from app.playlists.models import PlaylistTrack
from typing import List, Dict
from collections import Counter

async def calculate_library_stats(db: AsyncSession, user_id: str) -> Dict:
    # Total de faixas únicas na biblioteca (union de saved tracks + playlists)
    # Para simplificar V1: contar distinct track_id em playlist_tracks do usuário
    stmt = (
        select(
            func.count(distinct(PlaylistTrack.track_id)).label("unique_tracks"),
            func.count(distinct(PlaylistTrack.artist_ids[0])).label("unique_artists"),  # primeiro artista
            func.sum(PlaylistTrack.duration_ms).label("total_duration_ms"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id, PlaylistTrack.is_available == True)
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
        .where(Playlist.user_id == user_id, PlaylistTrack.is_available == True)
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
    
    # Distribuição por gênero (precisa de artist_genres cacheado)
    # Simplificado: usar cache Redis artist_genres
    from app.spotify.client import SpotifyClient
    from app.auth.security import decrypt_token
    from app.users.service import get_user_by_id
    
    user = await get_user_by_id(db, user_id)
    spotify = SpotifyClient(decrypt_token(user.access_token_encrypted))
    
    # Buscar todas as faixas com artist_id principal
    stmt_genres = (
        select(
            PlaylistTrack.artist_ids[0].label("artist_id"),
            func.count().label("track_count"),
        )
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .where(Playlist.user_id == user_id, PlaylistTrack.is_available == True)
        .group_by("artist_id")
    )
    genre_result = await db.execute(stmt_genres)
    artist_counts = {row.artist_id: row.track_count for row in genre_result}
    
    genre_counter = Counter()
    for artist_id, count in artist_counts.items():
        # Cache Redis: artist_genres:{artist_id}
        # Se não tiver, buscar /artists/{id}
        genres = await get_artist_genres_cached(spotify, artist_id)
        for g in genres:
            genre_counter[g] += count
    
    await spotify.close()
    
    top_genres = dict(genre_counter.most_common(10))
    
    return {
        "total_tracks": unique_tracks,
        "total_artists": unique_artists,
        "total_hours": total_hours,
        "top_artist": {"name": top_artist.artist_name, "track_count": top_artist.track_count} if top_artist else None,
        "genre_distribution": top_genres,
        "decade_distribution": decades,
    }

async def get_artist_genres_cached(spotify: SpotifyClient, artist_id: str) -> List[str]:
    import redis.asyncio as redis
    from app.config import get_settings
    settings = get_settings()
    
    r = redis.from_url(settings.REDIS_URL)
    cache_key = f"artist_genres:{artist_id}"
    
    cached = await r.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    
    try:
        artist = await spotify.get(f"/artists/{artist_id}")
        genres = artist.get("genres", [])
        await r.setex(cache_key, settings.CACHE_TTL_ARTIST_GENRES, json.dumps(genres))
        return genres
    except Exception:
        return []
```

---

## 10. Endpoints da API (Resumo)

### Auth
```
GET  /auth/login           → Redirect para Spotify OAuth
GET  /auth/callback        → Troca code por tokens, cria sessão, redirect para frontend
POST /auth/logout          → Invalida sessão
GET  /auth/me              → Retorna usuário atual (id, display_name, email)
```

### Library
```
GET  /library/stats        → LibraryStats (contagens, horas, top artist, genre/decade dist)
GET  /library/issues       → LibraryIssuesSummary (contadores de cada problema)
POST /library/sync         → Trigger sync completo (background), retorna task_id
```

### Playlists
```
GET  /playlists            → List[PlaylistRead] (paginado, do banco)
GET  /playlists/{id}       → PlaylistDetail (com tracks, do banco)
GET  /playlists/{id}/issues → PlaylistIssues (duplicatas intra + indisponíveis dessa playlist)
GET  /playlists/{id}/sorted?by=artist|album|duration → Ordenado (client-side no front, mas endpoint existe para consistência)
```

### Actions (V1 - cria novas playlists)
```
POST /actions/create-from-filter
  Body: {genres?: string[], decades?: string[], artist_ids?: string[], max_duration_ms?: int, name?: string}
  → ActionResponse {playlist_id, name, track_count}

POST /actions/merge-playlists
  Body: {playlist_id_1: string, playlist_id_2: string, name?: string}
  → ActionResponse

POST /actions/reverse-playlist
  Body: {playlist_id: string, name?: string}
  → ActionResponse
```

---

## 11. Cache Strategy (Redis)

```python
# app/cache.py
import redis.asyncio as redis
import json
from app.config import get_settings

settings = get_settings()
_redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_key(user_id: str, resource: str, resource_id: str = None) -> str:
    return f"spotify:{user_id}:{resource}:{resource_id or 'list'}"

async def get_cached(user_id: str, resource: str, resource_id: str = None) -> dict | None:
    key = cache_key(user_id, resource, resource_id)
    data = await _redis.get(key)
    return json.loads(data) if data else None

async def set_cached(user_id: str, resource: str, data: dict, resource_id: str = None, ttl: int = 300):
    key = cache_key(user_id, resource, resource_id)
    await _redis.setex(key, ttl, json.dumps(data))

async def invalidate_user_cache(user_id: str, resource: str = None):
    pattern = f"spotify:{user_id}:*" if not resource else f"spotify:{user_id}:{resource}:*"
    keys = []
    async for key in _redis.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await _redis.delete(*keys)
```

---

## 12. Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 13. Testes (Exemplos)

```python
# tests/unit/test_analysis.py
import pytest
from app.playlists.analysis import find_duplicates_intra, find_duplicates_cross
from app.playlists.models import Playlist, PlaylistTrack
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_find_duplicates_intra(db_session: AsyncSession):
    # Setup: playlist com 3 faixas, uma duplicada
    playlist = Playlist(id="pl1", user_id="u1", name="Test", track_count=3)
    db_session.add(playlist)
    db_session.add_all([
        PlaylistTrack(playlist_id="pl1", track_id="t1", position=0, track_name="A", artist_names=["Art"], artist_ids=["ar1"], duration_ms=200000, added_at=datetime.now(timezone.utc)),
        PlaylistTrack(playlist_id="pl1", track_id="t2", position=1, track_name="B", artist_names=["Art"], artist_ids=["ar1"], duration_ms=200000, added_at=datetime.now(timezone.utc)),
        PlaylistTrack(playlist_id="pl1", track_id="t1", position=2, track_name="A", artist_names=["Art"], artist_ids=["ar1"], duration_ms=200000, added_at=datetime.now(timezone.utc)),  # duplicata
    ])
    await db_session.commit()
    
    dups = await find_duplicates_intra(db_session, "u1")
    assert len(dups) == 1
    assert dups[0]["track_id"] == "t1"
    assert dups[0]["count"] == 2
```

---

## 14. Variáveis de Ambiente (.env.example)

```bash
# App
ENVIRONMENT=development
SECRET_KEY=gere-uma-chave-forte-com-openssl-rand-base64-32
FERNET_KEY=gere-com-python-cryptography-fernet-Fernet.generate_key()

# Spotify (Developer Dashboard)
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
SPOTIFY_SCOPES=user-read-private user-read-email user-library-read playlist-read-private playlist-read-collaborative

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/meuSpotify

# Redis
REDIS_URL=redis://localhost:6379/0

# Frontend
FRONTEND_URL=http://127.0.0.1:5173
```

---

## 15. Comandos Úteis

```bash
# Gerar Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Subir infra
docker-compose up -d

# Migrations
alembic revision --autogenerate -m "init"
alembic upgrade head

# Dev server
uvicorn app.main:app --reload

# Testes
pytest --cov=app --cov-report=term-missing

# Lint
ruff check . && ruff format . --check

# Type check
mypy app/
```

---

*Documento versionado. Última atualização: 2026-08-20*