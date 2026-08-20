# app/spotify/client.py
import asyncio
import logging

import httpx

from app.config import get_settings
from app.spotify.endpoints import BASE_URL, FIELDS
from app.spotify.exceptions import (
    InsufficientScopeError,
    NotFoundError,
    SpotifyAPIError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Cliente assíncrono para Spotify Web API com rate limit, retry e paginação."""

    def __init__(self, access_token: str):
        self.token = access_token
        self.base_url = BASE_URL
        self.settings = get_settings()
        self._semaphore = asyncio.Semaphore(int(self.settings.SPOTIFY_RATE_LIMIT))
        self._client = httpx.AsyncClient(timeout=30.0)

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        use_fields: bool = True,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        request_headers = {"Authorization": f"Bearer {self.token}", **(headers or {})}

        # Adicionar fields para reduzir payload se for GET
        request_params = params or {}
        if use_fields and method == "GET" and "fields" not in request_params:
            # Tentar usar field mask conhecido
            for key, fields_value in FIELDS.items():
                if key in path or path.endswith(key):
                    request_params["fields"] = fields_value
                    break

        async with self._semaphore:
            for attempt in range(3):
                try:
                    resp = await self._client.request(
                        method, url, headers=request_headers, params=request_params, json=json
                    )
                except httpx.RequestError as e:
                    logger.warning(f"Request error (attempt {attempt + 1}/3): {e}")
                    if attempt == 2:
                        raise SpotifyAPIError(f"Erro de rede após 3 tentativas: {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue

                # Rate limit
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                    logger.warning(f"Rate limited, waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue

                # Token expirado
                if resp.status_code == 401:
                    raise TokenExpiredError("Access token expirado ou inválido")

                # Scope insuficiente
                if resp.status_code == 403:
                    raise InsufficientScopeError("Scope insuficiente para esta operação")

                # Não encontrado
                if resp.status_code == 404:
                    raise NotFoundError("Recurso não encontrado")

                # Erro do servidor
                if 500 <= resp.status_code < 600:
                    logger.warning(f"Server error {resp.status_code}, retry {attempt + 1}/3")
                    await asyncio.sleep(2 ** attempt)
                    continue

                return resp

            raise SpotifyAPIError(f"Max retries exceeded for {method} {path}")

    async def get(self, path: str, params: dict | None = None) -> dict:
        resp = await self._request("GET", path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, json: dict | None = None) -> dict:
        resp = await self._request("POST", path, json=json)
        resp.raise_for_status()
        return resp.json()

    async def put(self, path: str, json: dict | None = None) -> dict:
        resp = await self._request("PUT", path, json=json)
        resp.raise_for_status()
        return resp.json()

    async def delete(self, path: str, params: dict | None = None) -> dict:
        resp = await self._request("DELETE", path, params=params)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    async def paginate(
        self,
        path: str,
        params: dict | None = None,
        limit: int | None = None,
        max_pages: int | None = None,
    ) -> list[dict]:
        """Percorre todas as páginas de um endpoint paginado."""
        results = []
        url = f"{self.base_url}{path}"
        fetched = 0
        pages = 0

        while url and (limit is None or fetched < limit) and (max_pages is None or pages < max_pages):
            # Se url já é absoluta (next), usar direto
            if url.startswith("http"):
                full_url = url
                # Extrair path relativo para _request
                if full_url.startswith(self.base_url):
                    local_path = full_url[len(self.base_url):]
                    data = await self._request("GET", local_path)
                else:
                    # URL externa inesperada
                    resp = await self._client.get(full_url, headers={"Authorization": f"Bearer {self.token}"})
                    resp.raise_for_status()
                    data = resp.json()
            else:
                data = await self._request("GET", url, params=params)

            items = data.get("items", [])
            results.extend(items)
            fetched += len(items)

            url = data.get("next")
            params = None  # 'next' já inclui os params
            pages += 1

            if limit and fetched >= limit:
                results = results[:limit]
                break

        return results

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
