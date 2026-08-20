# Features, Processos e Otimização — Meu Spotify

## 1. Features Detalhadas por Versão

### V1 — MVP (Foco: Leitura, Análise, Ações Simples)

#### 1.1 Autenticação
- **Login Spotify**: Botão "Entrar com Spotify" → redirect para OAuth → callback → sessão criada
- **Logout**: Botão no header → invalida cookie + Redis → redirect para login
- **Persistência**: Tokens criptografados no Postgres; sessão em cookie HttpOnly (7 dias)

#### 1.2 Dashboard (`/`)
| Componente | Fonte de Dados | Cache |
|------------|----------------|-------|
| Stat cards (músicas, artistas, horas) | `GET /library/stats` | 15 min |
| Top artista | `GET /library/stats` → `top_artist` | 15 min |
| Distribuição gênero (barras) | `GET /library/stats` → `genre_distribution` | 15 min |
| Distribuição década (barras) | `GET /library/stats` → `decade_distribution` | 15 min |
| Alertas de problemas | `GET /library/issues` → resumo | 5 min |

#### 1.3 Playlists (`/playlists`)
- Lista paginada do banco (servido via `GET /playlists`)
- Busca local (filtro por nome, `useMemo` no frontend)
- Ordenação: nome, nº faixas, última modificação
- Cards com badge: `⚠ N duplicatas`, `● 2y abandonada`, `✓ ok`

#### 1.4 Playlist Detalhe (`/playlists/:id`)
- Faixas do banco (`GET /playlists/{id}`)
- Ordenação client-side: artista (A-Z), álbum (A-Z), duração (cresc/decresc)
- Colunas: Artista, Música, Álbum, Duração, Adicionada em
- Badge de problemas no header da página

#### 1.5 Issues — "Arrume seu Spotify" (`/issues`)
Quatro seções expansíveis (accordion):

| Seção | Query Backend | Exibição |
|-------|---------------|----------|
| Músicas duplicadas (intra-playlist) | `GET /library/issues?type=duplicates_intra` | Lista: faixa → playlists onde aparece |
| Músicas em múltiplas playlists (cross) | `GET /library/issues?type=duplicates_cross` | Lista: faixa → N playlists |
| Playlists abandonadas | `GET /library/issues?type=abandoned` | Lista: playlist → última modificação |
| Faixas indisponíveis | `GET /library/issues?type=unavailable` | Lista: faixa (nome indisponível) → playlist |

#### 1.6 Ações de Organização (Leitura + Criação)
| Ação | Endpoint | Parâmetros | Resultado |
|------|----------|------------|-----------|
| Criar playlist por filtros | `POST /actions/create-from-filter` | `genres[]`, `decades[]`, `artists[]`, `max_duration_ms`, `name?` | Nova playlist criada no Spotify + snapshot no banco |
| Juntar playlists | `POST /actions/merge-playlists` | `playlist_id_1`, `playlist_id_2`, `name?` | Nova playlist (union por track_id) |
| Inverter playlist | `POST /actions/reverse-playlist` | `playlist_id`, `name?` | Nova playlist invertida |

> **Nota V1**: Ações criam **novas playlists** — não modificam as originais. Remoção/ordenação in-place ficam para V2 (escrita requer scopes `playlist-modify-*`).

#### 1.7 Sincronização
- `POST /library/sync` — background task: busca `/me/playlists` + `/me/tracks`, compara `snapshot_id`, atualiza Postgres
- Progresso via polling ou SSE (opcional V1)

---

### V2 — Expansão (Escrita + Histórico + Compartilhamento)

| Feature | Endpoint | Complexidade |
|---------|----------|--------------|
| Remover duplicatas in-place | `POST /actions/remove-duplicates` | Média (confirmação + diff) |
| Reordenar e salvar playlist | `PUT /actions/reorder-playlist` | Média (calcular nova ordem + PUT `/items`) |
| Comparar duas playlists | `GET /playlists/compare?id1=X&id2=Y` | Baixa (set operations) |
| Evolução do gosto (timeline) | `GET /library/history` | Alta (precisa armazenar snapshots temporais) |
| Compartilhar stats (imagem) | `POST /actions/share-stats` | Média (gerar PNG/og:image) |
| Exportar biblioteca (JSON/CSV) | `GET /library/export` | Baixa |

---

### V3 — Spotify Manager (Produto Completo)

| Feature | Descrição |
|---------|-----------|
| Gerador por contexto | "Playlist para estudar 3h" → filtra por audio features (energy < 0.4, instrumentalness > 0.5, sem vocal) + duração alvo |
| Análise de dominância | Artistas que aparecem em > 50% das playlists; "bolha de gosto" |
| Smart shuffle | Reordenar playlist variando artista/gênero (não duas do mesmo artista seguidas) |
| Backup automático | Export semanal agendado para GitHub Gist / Google Drive |
| Multi-conta | Gerenciar playlists de múltiplas contas (family) |

---

## 2. Processos de Dados

### 2.1 Pipeline de Sync Inicial
```
Login (primeira vez)
    │
    ▼
POST /library/sync (background)
    │
    ├── GET /me/playlists (paginado, max 50/page)
    │       │
    │       ▼
    │   Para cada playlist:
    │       ├── GET /playlists/{id}/items (paginado, 100/page)
    │       ├── Extrair: track_id, name, artists[], album, duration_ms, added_at, is_available
    │       ├── Persistir em playlists + playlist_tracks (upsert por snapshot_id)
    │       └── Cache Redis (TTL 10 min)
    │
    ├── GET /me/tracks (paginado, 50/page)
    │       └── Persistir library_tracks (para stats globais)
    │
    ├── GET /me/top/artists (long_term, medium_term, short_term)
    ├── GET /me/top/tracks (long_term, medium_term, short_term)
    │
    ▼
Atualizar users.last_sync_at
Invalidar cache Redis relacionado
Retornar contadores para UI
```

### 2.2 Sync Incremental (Subsequentes)
```
GET /playlists (do banco) → para cada:
    GET /playlists/{id} (só metadata) → comparar snapshot_id
    Se mudou: GET /playlists/{id}/items → upsert tracks
    Se não mudou: pular
```

### 2.3 Detecção de Duplicatas (Algoritmo)
```python
# Intra-playlist: mesmo track_id na mesma playlist
SELECT playlist_id, track_id, COUNT(*) as cnt
FROM playlist_tracks
GROUP BY playlist_id, track_id
HAVING COUNT(*) > 1

# Cross-playlist: track_id em múltiplas playlists
SELECT track_id, ARRAY_AGG(playlist_id) as playlists, COUNT(DISTINCT playlist_id) as playlist_count
FROM playlist_tracks
GROUP BY track_id
HAVING COUNT(DISTINCT playlist_id) > 1
```

### 2.4 Detecção de Abandono
```sql
-- Playlist não modificada há > 1 ano
SELECT * FROM playlists
WHERE last_modified < NOW() - INTERVAL '1 year'
   OR (synced_at < NOW() - INTERVAL '1 year' AND snapshot_id IS NOT NULL)
```

### 2.5 Detecção de Indisponíveis
```sql
-- Faixas marcadas is_available = false
SELECT * FROM playlist_tracks WHERE is_available = false
-- OU faixas que a API retorna sem metadata (track is null)
```

### 2.6 Estimativa de Gênero por Faixa
```python
# A API não retorna gênero da faixa diretamente
# Estratégia: usar artist.genres do artista principal da faixa
# Cache: artist_id → genres[] (TTL 24h)

async def get_track_genres(track: Track) -> List[str]:
    primary_artist_id = track.artists[0].id
    genres = await redis.get(f"artist_genres:{primary_artist_id}")
    if not genres:
        artist = await spotify.get(f"/artists/{primary_artist_id}")
        genres = artist.get("genres", [])
        await redis.setex(f"artist_genres:{primary_artist_id}", 86400, genres)
    return genres
```

---

## 3. Otimizações

### 3.1 Backend

| Área | Otimização | Implementação |
|------|------------|---------------|
| **Rate Limit** | Token bucket local + respeito a `Retry-After` | `SpotifyClient.get()` com retry automático; semaphore para limitar concorrência (ex: 5 req/s) |
| **Paginação** | Iterador assíncrono que segue `next` | `async def paginate(path): while url: yield from page` |
| **Cache** | Redis com TTLs diferenciados + invalidação por tag | `cache_key = f"spotify:{user_id}:playlists"`; `DELETE` no sync |
| **DB** | Índices compostos + `snapshot_id` para sync inteligente | `CREATE INDEX ON playlist_tracks (playlist_id, track_id)` |
| **Background Tasks** | FastAPI `BackgroundTasks` para sync pesado | `background_tasks.add_task(sync_library, user_id)` |
| **Connection Pool** | SQLAlchemy `pool_size=10, max_overflow=20` | Config em `database.py` |
| **Compressão** | Gzip responses > 1KB | `app.add_middleware(GZipMiddleware, minimum_size=1000)` |

### 3.2 Frontend

| Área | Otimização | Implementação |
|------|------------|---------------|
| **Data Fetching** | TanStack Query com `staleTime` adequado | playlists: 5min; stats: 15min; playlist detail: 10min |
| **Prefetch** | `queryClient.prefetchQuery` ao hover no link da playlist | `onMouseEnter={() => prefetchPlaylist(id)}` |
| **Virtualização** | `react-window` para listas > 200 faixas | `FixedSizeList` no `PlaylistTracks` |
| **Memoização** | `useMemo` para ordenações/filtros client-side | `sortedTracks = useMemo(() => sort(tracks, by), [tracks, by])` |
| **Code Splitting** | `React.lazy` + `Suspense` por página | `const Dashboard = lazy(() => import('./pages/Dashboard'))` |
| **Bundle** | Vite + tree-shaking; analisar com `rollup-plugin-visualizer` | `npm run build -- --report` |
| **Imagens** | Spotify artwork via CDN (já otimizado); lazy load nativo | `<img loading="lazy" src={track.album.images[0]?.url} />` |

### 3.3 Algoritmos de Ordenação (Client-side)
```typescript
// Em hooks/usePlaylist.ts
export function useSortedTracks(tracks: Track[], sortBy: 'artist' | 'album' | 'duration') {
  return useMemo(() => {
    const sorted = [...tracks];
    switch (sortBy) {
      case 'artist':
        return sorted.sort((a, b) => a.artists[0].name.localeCompare(b.artists[0].name, 'pt-BR'));
      case 'album':
        return sorted.sort((a, b) => a.album.name.localeCompare(b.album.name, 'pt-BR'));
      case 'duration':
        return sorted.sort((a, b) => a.duration_ms - b.duration_ms);
      default:
        return sorted;
    }
  }, [tracks, sortBy]);
}
```

### 3.4 Criação de Playlist por Filtros (Backend)
```python
# POST /actions/create-from-filter
async def create_playlist_from_filter(
    user_id: str,
    genres: List[str] = None,
    decades: List[str] = None,
    artist_ids: List[str] = None,
    max_duration_ms: int = None,
    name: str = None,
) -> Playlist:
    # 1. Buscar todas as faixas do usuário (library + playlists) — do banco
    candidate_tracks = await get_user_all_tracks(user_id)
    
    # 2. Aplicar filtros em memória (rápido, evita N calls à API)
    filtered = candidate_tracks
    if genres:
        filtered = [t for t in filtered if any(g in t.artist_genres for g in genres)]
    if decades:
        filtered = [t for t in filtered if t.decade in decades]
    if artist_ids:
        filtered = [t for t in filtered if any(a.id in artist_ids for a in t.artists)]
    if max_duration_ms:
        filtered = [t for t in filtered if t.duration_ms <= max_duration_ms]
    
    # 3. Limitar a 10k tracks (limite API Spotify por playlist)
    track_uris = [f"spotify:track:{t.id}" for t in filtered[:10000]]
    
    # 4. Criar playlist no Spotify
    playlist = await spotify.post("/me/playlists", {
        "name": name or f"Meu Spotify — Filtro — {date.today().isoformat()}",
        "public": False,
        "description": "Criada via Meu Spotify"
    })
    
    # 5. Adicionar faixas em batches de 100
    for batch in chunks(track_uris, 100):
        await spotify.post(f"/playlists/{playlist['id']}/items", {"uris": batch})
    
    # 6. Invalidar cache e retornar
    await invalidate_cache(user_id, "playlists")
    return playlist
```

---

## 4. Métricas de Sucesso (KPIs)

| Métrica | Target V1 | Target V2+ |
|---------|-----------|------------|
| Tempo de sync inicial (5k faixas) | < 30s | < 20s |
| Dashboard load (cache hit) | < 500ms | < 300ms |
| Taxa de erro Spotify API | < 1% | < 0.5% |
| Cobertura de testes | > 80% | > 90% |
| Build time (CI) | < 5 min | < 3 min |
| Lighthouse Performance | > 90 | > 95 |

---

## 5. Riscos Técnicos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Spotify API muda endpoints novamente | Média | Alto | Wrapper `SpotifyClient` isolado; testes de integração mockados; monitorar changelog |
| Rate limit 429 frequente | Alta | Médio | Backoff exponencial + cache agressivo + semaphore concorrência |
| Token expira durante sync longo | Baixa | Alto | Refresh proativo antes de expirar (verificar `expires_at` antes de cada batch) |
| Biblioteca muito grande (>50k faixas) | Baixa | Médio | Paginação + streaming response; virtualização no frontend |
| Dev Mode 5 usuários limita testes | Certa | Baixo | Aceitar para V1; documentar limitação |
| `artist.genres` vazio para muitos artistas | Média | Baixo | Fallback: "Desconhecido"; não quebrar UI |

---

*Documento versionado. Última atualização: 2026-08-20*