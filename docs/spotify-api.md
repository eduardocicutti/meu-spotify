# Documentação da API do Spotify (Referência para o Projeto)

> Baseado na **Spotify Web API** pós-migração de **fevereiro de 2026**.  
> Fonte oficial: https://developer.spotify.com/documentation/web-api

---

## 1. Autenticação

### Authorization Code Flow (usado no projeto)
```
GET https://accounts.spotify.com/authorize
  ?client_id={CLIENT_ID}
  &response_type=code
  &redirect_uri={REDIRECT_URI}  (ex: http://127.0.0.1:8000/auth/callback)
  &scope={SCOPES_SPACE_SEPARATED}
  &state={RANDOM_STRING}
  &show_dialog=true
```

**Troca de código por tokens:**
```
POST https://accounts.spotify.com/api/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

grant_type=authorization_code
&code={AUTH_CODE}
&redirect_uri={REDIRECT_URI}
```

**Resposta:**
```json
{
  "access_token": "BQ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "AQ...",
  "scope": "user-read-private user-read-email ..."
}
```

**Refresh token:**
```
POST https://accounts.spotify.com/api/token
grant_type=refresh_token
&refresh_token={REFRESH_TOKEN}
```

---

## 2. Escopos Necessários (V1)

| Scope | Descrição | Endpoints Habilitados |
|-------|-----------|----------------------|
| `user-read-private` | Perfil básico do usuário | `GET /me` |
| `user-read-email` | Email do usuário | `GET /me` |
| `user-library-read` | Músicas/álbuns salvos | `GET /me/tracks`, `GET /me/albums` |
| `playlist-read-private` | Playlists privadas | `GET /me/playlists`, `GET /playlists/{id}/items` |
| `playlist-read-collaborative` | Playlists colaborativas | `GET /me/playlists` (inclui colaborativas) |

**V2+ (escrita):**
- `playlist-modify-public`
- `playlist-modify-private`
- `user-library-modify`

---

## 3. Endpoints Utilizados no V1

### 3.1 Perfil do Usuário
```
GET https://api.spotify.com/v1/me
Authorization: Bearer {ACCESS_TOKEN}
```
**Resposta relevante:**
```json
{
  "id": "usuario123",
  "display_name": "Eduardo",
  "email": "eduardo@email.com",
  "images": [{ "url": "https://...", "height": 300, "width": 300 }],
  "country": "BR",
  "product": "premium"
}
```

### 3.2 Playlists do Usuário
```
GET https://api.spotify.com/v1/me/playlists?limit=50&offset=0
Authorization: Bearer {ACCESS_TOKEN}
```
**Paginação:** `next` / `previous` no response. Máximo 50 por page.

**Resposta:**
```json
{
  "items": [
    {
      "id": "playlist_id",
      "name": "Minha Playlist",
      "description": "Descrição",
      "public": false,
      "collaborative": false,
      "owner": { "id": "usuario123", "display_name": "Eduardo" },
      "tracks": { "total": 42, "href": "https://api.spotify.com/v1/playlists/playlist_id/items" },
      "images": [{ "url": "https://i.scdn.co/image/...", "height": 300, "width": 300 }],
      "snapshot_id": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=",
      "external_urls": { "spotify": "https://open.spotify.com/playlist/..." }
    }
  ],
  "total": 15,
  "next": "https://api.spotify.com/v1/me/playlists?offset=50&limit=50",
  "previous": null
}
```

### 3.3 Itens de uma Playlist (NOVO: `/items` não `/tracks`)
```
GET https://api.spotify.com/v1/playlists/{playlist_id}/items?limit=100&offset=0&fields=items(track(id,name,artists,album,duration_ms,is_available,added_at)),next,total
Authorization: Bearer {ACCESS_TOKEN}
```
**Parâmetros importantes:**
- `fields` — filtrar resposta (recomendado para reduzir payload)
- `market` — `BR` ou `from_token`
- `additional_types` — `track,episode`

**Resposta (estrutura pós-fev/2026):**
```json
{
  "items": [
    {
      "added_at": "2024-01-15T10:30:00Z",
      "added_by": { "id": "usuario123" },
      "is_local": false,
      "track": {
        "id": "track_id",
        "name": "Do I Wanna Know?",
        "duration_ms": 272000,
        "is_available": true,
        "explicit": true,
        "artists": [
          { "id": "artist_id", "name": "Arctic Monkeys", "external_urls": {...} }
        ],
        "album": {
          "id": "album_id",
          "name": "AM",
          "release_date": "2013-09-09",
          "release_date_precision": "day",
          "images": [{ "url": "https://i.scdn.co/image/...", "height": 640, "width": 640 }],
          "artists": [{ "id": "artist_id", "name": "Arctic Monkeys" }]
        },
        "external_urls": { "spotify": "https://open.spotify.com/track/..." }
      }
    }
  ],
  "next": "https://api.spotify.com/v1/playlists/playlist_id/items?offset=100&limit=100",
  "total": 42
}
```

> **⚠️ CRÍTICO**: O campo era `tracks` (com `tracks.items[].track`). Agora é **`items`** direto com `items[].track`.  
> **Track pode ser `null`** se removida do catálogo → `is_available: false`.

### 3.4 Músicas Salvas (Library)
```
GET https://api.spotify.com/v1/me/tracks?limit=50&offset=0
Authorization: Bearer {ACCESS_TOKEN}
```
**Resposta:**
```json
{
  "items": [
    {
      "added_at": "2024-01-15T10:30:00Z",
      "track": { ... mesmo objeto track de cima ... }
    }
  ],
  "next": "...",
  "total": 1842
}
```

### 3.5 Top Items (Artistas e Faixas)
```
GET https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=20
GET https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=20
```
**time_range:** `short_term` (~4 semanas), `medium_term` (~6 meses), `long_term` (anos)

**Resposta artista:**
```json
{
  "items": [
    {
      "id": "artist_id",
      "name": "Arctic Monkeys",
      "genres": ["alternative rock", "indie rock", "garage rock revival"],
      "popularity": 82,
      "followers": { "total": 12345678 },
      "images": [{ "url": "...", "height": 640, "width": 640 }],
      "external_urls": { "spotify": "..." }
    }
  ]
}
```

### 3.6 Artista (para buscar gêneros)
```
GET https://api.spotify.com/v1/artists/{artist_id}
Authorization: Bearer {ACCESS_TOKEN}
```
**Resposta:** Inclui `genres` array — essencial para distribuição por gênero.

### 3.7 Vários Artistas (batch)
```
GET https://api.spotify.com/v1/artists?ids=id1,id2,id3
```
Máximo 50 IDs por request.

### 3.8 Histórico Recente
```
GET https://api.spotify.com/v1/me/player/recently-played?limit=50
```
**Resposta:** Array de `{ track, played_at, context }` — útil para "horário que mais ouve".

---

## 4. Endpoints REMOVIDOS (Fevereiro 2026) — NÃO USAR

| Endpoint Removido | Substituição / Workaround |
|-------------------|---------------------------|
| `GET /users/{user_id}/playlists` | Use `GET /me/playlists` (apenas usuário atual) |
| `GET /playlists/{id}/tracks` | Use `GET /playlists/{id}/items` |
| `PUT /playlists/{id}/tracks` | Use `PUT /playlists/{id}/items` |
| `POST /playlists/{id}/tracks` | Use `POST /playlists/{id}/items` |
| `DELETE /playlists/{id}/tracks` | Use `DELETE /playlists/{id}/items` |
| `GET /artists/{id}/top-tracks` | **Removido sem substituição** |
| `GET /browse/new-releases` | **Removido sem substituição** |
| `GET /artists/{id}/albums` (com `include_groups`) | Parcialmente removido |
| `GET /search` com `limit>10` | Máximo 10 por request; paginar |

---

## 5. Rate Limiting

| Limite | Valor |
|--------|-------|
| Requisições por segundo (app) | ~10-30 req/s (não documentado oficialmente) |
| Search por request | Máx 10 resultados |
| Playlist items por request | Máx 100 |
| Playlists por request | Máx 50 |
| Top items por request | Máx 50 |

**Headers de resposta:**
- `Retry-After: N` — segundos para esperar (em 429)
- `X-RateLimit-Limit`, `X-RateLimit-Remaining` — nem sempre presentes

**Estratégia no código:**
```python
async def get_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        resp = await client.get(url, headers=headers)
        if resp.status == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            await asyncio.sleep(wait)
            continue
        if resp.status == 401:
            # tentar refresh token uma vez
            await refresh_token()
            continue
        if 500 <= resp.status < 600:
            await asyncio.sleep(2 ** attempt)
            continue
        return resp
    raise RateLimitExceeded()
```

---

## 6. Estruturas de Dados Chave (TypeScript/Python)

### Track (simplificado)
```typescript
interface SpotifyTrack {
  id: string;
  name: string;
  duration_ms: number;
  is_available: boolean;
  explicit: boolean;
  artists: SpotifyArtist[];
  album: SpotifyAlbum;
  external_urls: { spotify: string };
}

interface SpotifyArtist {
  id: string;
  name: string;
  genres?: string[];  // só vem em /artists/{id} ou /me/top/artists
  external_urls: { spotify: string };
}

interface SpotifyAlbum {
  id: string;
  name: string;
  release_date: string;  // "2013-09-09" ou "2013"
  release_date_precision: "year" | "month" | "day";
  images: SpotifyImage[];
  artists: SpotifyArtist[];
}
```

### Playlist Item
```typescript
interface PlaylistItem {
  added_at: string;  // ISO 8601
  added_by: { id: string };
  is_local: boolean;
  track: SpotifyTrack | null;  // null se removida
}
```

### Paginated Response
```typescript
interface Paginated<T> {
  items: T[];
  next: string | null;
  previous: string | null;
  total: number;
  limit: number;
  offset: number;
}
```

---

## 7. Códigos de Erro Comuns

| Status | Significado | Ação |
|--------|-------------|------|
| 400 | Bad Request | Verificar parâmetros |
| 401 | Unauthorized | Token expirado → refresh |
| 403 | Forbidden | Scope faltando / app não autorizado |
| 404 | Not Found | Playlist/track não existe ou privada |
| 429 | Too Many Requests | Respeitar `Retry-After` |
| 500/502/503 | Server Error | Retry com backoff |

---

## 8. Boas Práticas para o Projeto

1. **Sempre usar `fields`** para reduzir payload (ex: `fields=items(track(id,name,artists,album,duration_ms,is_available))`)
2. **Cache agressivo** de `/artists/{id}` (genres mudam raramente) — TTL 24h
3. **Semaphore de concorrência** (max 5 req/s) para não estourar rate limit
4. **Tratar `track: null`** → marcar `is_available = false` no banco
5. **Comparar `snapshot_id`** antes de rebuscar faixas de playlist
6. **Nunca logar `access_token`** — usar `***` em logs
7. **Redirect URI exato** no Dashboard: `http://127.0.0.1:8000/auth/callback` (não localhost)

---

## 9. Referências Oficiais

- **Migration Guide Fev/2026**: https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide
- **Changelog Fev/2026**: https://developer.spotify.com/documentation/web-api/references/changes/february-2026
- **API Reference**: https://developer.spotify.com/documentation/web-api/reference
- **Policy (restrições IA/dados)**: https://developer.spotify.com/policy
- **Developer Dashboard**: https://developer.spotify.com/dashboard

---

*Documento versionado. Última atualização: 2026-08-20*