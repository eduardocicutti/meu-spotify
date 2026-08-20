# Histórico de Versões, Checklists e Bugs — Meu Spotify

## 1. Versionamento

**Esquema**: Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH)
**Tags**: `vX.Y.Z` (ex: `v1.0.0`)
**Branches**: `main` (produção), `develop` (integração), `feature/*`, `bugfix/*`, `release/*`

---

## 2. Roadmap de Versões

### v0.1.0 — Scaffold & Dev Environment (Semana 1)
- [x] Estrutura de pastas criada
- [x] `docker-compose.yml` (Postgres + Redis + API)
- [x] `.env.example` com todas as variáveis
- [x] FastAPI app skeleton (main, config, database, auth router)
- [x] React + Vite + TypeScript + Tailwind v4 scaffold
- [x] GitHub Actions CI (lint + test + build)
- [x] README com instruções de setup

### v0.2.0 — Auth & Spotify Client (Semana 2)
- [ ] Spotify OAuth flow completo (login, callback, logout, refresh)
- [ ] `SpotifyClient` com rate limit, retry, paginação
- [ ] Tokens criptografados (Fernet) no Postgres
- [ ] Sessão via cookie HttpOnly + Redis
- [ ] Testes de integração auth

### v0.3.0 — Sync & Database (Semana 3)
- [ ] Models: User, Playlist, PlaylistTrack, LibraryTrack
- [ ] Alembic migrations
- [ ] Sync completo no primeiro login (background task)
- [ ] Sync incremental com `snapshot_id`
- [ ] Cache Redis com TTLs

### v0.4.0 — Dashboard & Stats (Semana 4)
- [ ] `GET /library/stats` endpoint
- [ ] Dashboard frontend (stat cards, genre/decade bars, top artist)
- [ ] Recharts integration
- [ ] Loading skeletons
- [ ] Empty states

### v0.5.0 — Playlists List & Detail (Semana 5)
- [ ] `GET /playlists`, `GET /playlists/{id}`
- [ ] Página Playlists (lista, busca, ordenação, badges)
- [ ] Página Playlist Detail (tabela, ordenação client-side)
- [ ] Virtualização para listas grandes

### v0.6.0 — Issues Detection (Semana 6)
- [ ] `GET /library/issues` (4 tipos)
- [ ] Algoritmos: duplicatas intra, cross, abandonadas, indisponíveis
- [ ] Página Issues (accordion sections)
- [ ] Resumo no dashboard

### v0.7.0 — Actions (Create/Merge) (Semana 7)
- [ ] `POST /actions/create-from-filter`
- [ ] `POST /actions/merge-playlists`
- [ ] `POST /actions/reverse-playlist`
- [ ] UI para ações (modais, confirmações)

### v0.8.0 — Polish & Hardening (Semana 8)
- [ ] Testes > 80% cobertura
- [ ] Lint zero warnings
- [ ] Error boundaries + Sentry
- [ ] Health check endpoint
- [ ] Documentação API (OpenAPI/Swagger)
- [ ] Deploy staging

### v1.0.0 — MVP Release 🎉
- [ ] Tag `v1.0.0`
- [ ] Release notes
- [ ] Demo video/gif para README

---

## 3. Checklists por Fase

### Setup Inicial (Pre-dev)
- [ ] Conta Spotify Developer criada
- [ ] App no Dashboard: `Redirect URI = http://127.0.0.1:8000/auth/callback`
- [ ] Scopes configurados: `user-read-private user-read-email user-library-read playlist-read-private playlist-read-collaborative`
- [ ] Owner tem Spotify Premium ativo
- [ ] `.env` preenchido com `CLIENT_ID`, `CLIENT_SECRET`, `SECRET_KEY`, `FERNET_KEY`, `DATABASE_URL`, `REDIS_URL`
- [ ] `docker-compose up -d` sobe Postgres + Redis saudáveis
- [ ] `alembic upgrade head` roda sem erro
- [ ] `uvicorn app.main:app --reload` inicia na porta 8000
- [ ] `npm run dev` inicia Vite na porta 5173
- [ ] Login funciona end-to-end no browser

### Backend Quality Gate (por PR)
- [ ] `ruff check .` passa
- [ ] `ruff format .` passa
- [ ] `pytest --cov=app --cov-report=term-missing` > 80%
- [ ] `mypy app/` passa (strict mode)
- [ ] Nenhum `print()` em código de produção (usar `logging`)
- [ ] Docstrings em funções públicas
- [ ] Type hints em todas as funções
- [ ] Exceções específicas capturadas (nunca `except:`)
- [ ] Logs estruturados (JSON) com `request_id`

### Frontend Quality Gate (por PR)
- [ ] `npm run lint` passa (eslint + prettier)
- [ ] `npm run typecheck` passa (tsc --noEmit)
- [ ] `npm run test` passa (vitest)
- [ ] `npm run build` gera bundle < 500KB gzipped
- [ ] Nenhum `any` sem justificativa em comentário
- [ ] Componentes com `React.memo` onde apropriado
- [ ] `useMemo`/`useCallback` em callbacks passados a filhos
- [ ] Acessibilidade: `aria-label`, `role`, focus visible
- [ ] Dark mode funciona (Tailwind `dark:`)

### Deploy Checklist
- [ ] CI pipeline verde na `main`
- [ ] Variáveis de produção no GitHub Secrets / Vercel / Render
- [ ] `FRONTEND_URL` aponta para domínio de produção
- [ ] `SPOTIFY_REDIRECT_URI` atualizado no Dashboard
- [ ] HTTPS forçado (HSTS)
- [ ] Health check `/health` responde 200
- [ ] Sentry DSN configurado
- [ ] Backup automático Postgres configurado

---

## 4. Bugs Conhecidos / Technical Debt

| ID | Descrição | Severidade | Status | Mitigação / Plano |
|----|-----------|------------|--------|-------------------|
| BUG-001 | `artist.genres` vazio para ~30% dos artistas | Baixa | Aberto | Fallback "Desconhecido"; não quebrar UI |
| BUG-002 | Search API limitado a 10 results/page | Média | Aceito | Paginação obrigatória; documentar |
| BUG-003 | Dev Mode: só 5 usuários | Baixa | Aceito | V1 é pessoal/portfolio |
| BUG-004 | `/me/top/artists` não retorna `genres` | Baixa | Aberto | Buscar `/artists/{id}` separado (cache 24h) |
| BUG-005 | Playlist colaborativa: `items` pode vir `null` se não owner | Média | Aberto | Tratar `playlist.items?.items ?? []` |
| BUG-006 | `snapshot_id` não muda ao reordenar tracks via UI Spotify | Média | Investigado | Usar `last_modified` como fallback |
| BUG-007 | Faixa removida do catálogo: API retorna `track: null` | Média | Aberto | Marcar `is_available=false` no sync |
| BUG-008 | Rate limit 429 em sync inicial de bibliotecas grandes | Alta | Mitigado | Semaphore 5 req/s + backoff exponencial |
| BUG-009 | Token expira durante sync longo (> 1h) | Baixa | Mitigado | Refresh proativo antes de cada batch |
| BUG-010 | Frontend: flicker no dark mode no primeiro load | Baixa | Aberto | `color-scheme: dark` no `:root` + script inline |

---

## 5. Decisões Técnicas Registradas (ADR Lite)

| Data | Decisão | Contexto | Alternativas Rejeitadas |
|------|---------|----------|------------------------|
| 2026-08-20 | FastAPI over Node/Express | Stack atual do Eduardo (FastAPI + Tauri) | NestJS, Express — curva de aprendizado |
| 2026-08-20 | PostgreSQL + SQLAlchemy over MongoDB | Dados relacionais (user ↔ playlist ↔ track); `snapshot_id` comparison | MongoDB — menos adequado para joins |
| 2026-08-20 | Redis para cache + sessão | TTLs diferenciados; invalidação por tag; session revogação fácil | In-memory (não escala), JWT stateless (revogação difícil) |
| 2026-08-20 | TanStack Query over SWR / RTK Query | Cache server-state; staleTime; prefetch; devtools | SWR (menos features), RTK Query (acopla ao Redux) |
| 2026-08-20 | Tailwind v4 over CSS Modules / Styled Components | Design system próprio; sem UI kit; performance | CSS Modules (verbose), Styled (runtime overhead) |
| 2026-08-20 | Componentes UI próprios (sem shadcn/MUI) | Evitar visual genérico; controle total; PT-BR nativo | shadcn (popular mas genérico), MUI (pesado) |
| 2026-08-20 | Criar novas playlists (não modificar originais) no V1 | Segurança: escopos de leitura apenas; UX: usuário não perde nada | Modificar in-place (precisa `playlist-modify-*`) |
| 2026-08-20 | Gênero via `artist.genres` (não track) | API não expõe gênero da faixa | Audio features (energy, valence) — proxy impreciso |
| 2026-08-20 | Sync background + snapshot_id | Performance; não rebuscar tudo a cada request | Sync a cada request (lento, gasta cota) |

---

## 6. Log de Mudanças (Changelog)

### [Unreleased] — Develop Branch
#### Added
- Scaffold completo do projeto (backend + frontend + docker + CI)
- Documentação: architecture.md, requirements.md, features.md, version-history.md

#### Changed
- N/A

#### Fixed
- N/A

### v0.1.0 — 2026-08-20
#### Added
- Estrutura de pastas padrão
- Docker Compose (Postgres 16, Redis 7)
- FastAPI skeleton com config, database, auth router
- React + Vite + TS + Tailwind v4 + Recharts + TanStack Query + Lucide
- GitHub Actions CI (ruff, pytest, eslint, typecheck, build)
- .env.example documentado
- README com setup instructions

---

## 7. Próximas Tarefas Imediatas (This Week)

| Task | Owner | Estimativa | Status |
|------|-------|------------|--------|
| Criar models SQLAlchemy (User, Playlist, PlaylistTrack) | Eduardo + Hermes | 2h | ⬜ |
| Implementar SpotifyClient com rate limit/retry/paginate | Eduardo + Hermes | 3h | ⬜ |
| OAuth flow: /auth/login, /auth/callback, /auth/logout | Eduardo + Hermes | 3h | ⬜ |
| Criptografia Fernet para tokens | Eduardo + Hermes | 1h | ⬜ |
| Alembic migration inicial | Eduardo + Hermes | 30min | ⬜ |
| Testes unitários auth + spotify client | Eduardo + Hermes | 2h | ⬜ |
| Frontend: Login page + AuthContext + apiClient | Eduardo + Hermes | 2h | ⬜ |
| Frontend: Layout (Sidebar, Header, PageShell) | Eduardo + Hermes | 2h | ⬜ |

---

## 8. Como Atualizar Este Documento

- **Nova versão**: Adicionar entrada no §2 e §6 (changelog)
- **Bug novo**: Adicionar no §4 com ID sequencial
- **Decisão técnica**: Adicionar no §5 (ADR)
- **Checklist item concluído**: Marcar `[x]` no §3
- **Tarefa da semana**: Atualizar §7

> **Regra**: Este arquivo é a fonte de verdade do estado do projeto. Atualize **imediatamente** quando algo mudar. Não espere "fim da sprint".

---
*Documento versionado. Última atualização: 2026-08-20*