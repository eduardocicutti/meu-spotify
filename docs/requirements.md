# Requisitos Funcionais e Não Funcionais — Meu Spotify

## 1. Requisitos Funcionais (RF)

### 1.1 Autenticação e Sessão
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-01 | Login via Spotify OAuth 2.0 (Authorization Code Flow) | Must |
| RF-02 | Callback em `http://127.0.0.1:8000/auth/callback` (não localhost) | Must |
| RF-03 | Armazenar `access_token` e `refresh_token` criptografados (Fernet) no PostgreSQL | Must |
| RF-04 | Sessão via cookie HttpOnly assinado (7 dias TTL) | Must |
| RF-05 | Refresh automático de token expirado (401 → retry 1x) | Must |
| RF-06 | Logout invalida sessão (cookie + Redis) | Must |

### 1.2 Dashboard e Estatísticas
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-07 | Exibir total de músicas salvas, artistas únicos, álbuns únicos | Must |
| RF-08 | Estimar horas totais de música (soma `duration_ms` / 3.6M) | Must |
| RF-09 | Distribuição por gênero (top 10, barras horizontais) | Must |
| RF-10 | Distribuição por década (1960s–2020s, barras horizontais) | Must |
| RF-11 | Artista mais presente na biblioteca (contagem de faixas) | Must |
| RF-12 | Top 5 artistas / Top 5 faixas (via `/me/top/artists`, `/me/top/tracks`) | Should |
| RF-13 | Músicas salvas vs playlists (venn diagram simples) | Could |

### 1.3 Listagem e Visualização de Playlists
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-14 | Listar todas as playlists do usuário (`GET /me/playlists` paginado) | Must |
| RF-15 | Busca local (filtro por nome, client-side) | Must |
| RF-16 | Ordenação: nome A-Z, nº faixas, data modificação | Must |
| RF-17 | Badge por playlist: duplicatas (⚠ N), abandonadas (● 2y), indisponíveis | Must |
| RF-18 | Detalhe da playlist: faixas com artista, álbum, duração, data adicionada | Must |
| RF-19 | Ordenação client-side da playlist: artista, álbum, duração | Must |

### 1.4 Detecção de Problemas ("Arrume seu Spotify")
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-20 | Detectar músicas duplicadas **dentro** de uma playlist (mesmo `track_id`) | Must |
| RF-21 | Detectar músicas que aparecem em **múltiplas** playlists (cross-playlist) | Must |
| RF-22 | Detectar playlists sem alteração > 1 ano (comparar `last_modified` / `snapshot_id`) | Must |
| RF-23 | Detectar faixas indisponíveis (`is_available: false` ou track removida) | Must |
| RF-24 | Resumo agregado no dashboard: contadores de cada problema | Must |
| RF-25 | Página dedicada "Issues" com seções expansíveis por tipo | Must |

### 1.5 Organização de Playlists (Leitura + Ações Simples)
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-26 | Criar nova playlist a partir de filtros: gênero, década, artista, duração | Must |
| RF-27 | Juntar duas playlists em uma nova (union, sem duplicatas) | Must |
| RF-28 | Inverter ordem de uma playlist | Should |
| RF-29 | Ordenar playlist e salvar nova versão ordenada | Should (V2) |
| RF-30 | Remover duplicatas de uma playlist (com confirmação) | Should (V2) |

### 1.6 Sincronização e Cache
| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-31 | Sync completo no primeiro login (persistir no Postgres) | Must |
| RF-32 | Servir dados do banco em requests subsequentes | Must |
| RF-33 | `POST /library/sync` para ressincronização manual | Must |
| RF-34 | Comparar `snapshot_id` — só rebuscar faixas se mudou | Must |
| RF-35 | Cache Redis com TTLs: playlists 5min, tracks 10min, stats 15min, profile 1h | Must |

---

## 2. Requisitos Não Funcionais (RNF)

| ID | Requisito | Detalhamento |
|----|-----------|--------------|
| RNF-01 | **Performance** | Dashboard carrega < 2s (cache hit); sync inicial < 30s para 5k faixas |
| RNF-02 | **Rate Limit** | Respeitar `Retry-After` (429); backoff exponencial máx 3 tentativas; não estourar cota |
| RNF-03 | **Segurança** | Tokens criptografados (Fernet); `client_secret` só no backend; HTTPS em produção; CORS restrito ao `FRONTEND_URL` |
| RNF-04 | **Disponibilidade** | 99% uptime em dev; graceful degradation se Spotify API cai (servir cache/banco) |
| RNF-05 | **Usabilidade** | PT-BR nativo; dark mode padrão; loading skeletons; empty states orientativos; acessibilidade (WCAG AA) |
| RNF-06 | **Manutenibilidade** | Cobertura de testes > 80%; linting (ruff, eslint); type hints (Python strict, TS strict); Conventional Commits |
| RNF-07 | **Escalabilidade** | Stateless backend (escala horizontal); Redis para sessão/cache; Postgres connection pooling |
| RNF-08 | **Observabilidade** | Logs estruturados (JSON); Sentry para erros; health check endpoint `/health` |
| RNF-09 | **Conformidade Spotify** | Não usar endpoints removidos (fev/2026); não treinar ML com dados do usuário; não sincronizar/download de conteúdo |
| RNF-10 | **Privacidade** | Dados do usuário só na sessão ativa; não persistir além do necessário; LGPD compliant |

---

## 3. Regras de Negócio

| Regra | Descrição |
|-------|-----------|
| RN-01 | Usuário só vê **suas** playlists e biblioteca (escopo `me`) |
| RN-02 | Playlists colaborativas aparecem na listagem (`playlist-read-collaborative`) |
| RN-03 | Duplicata = mesmo `track_id` (não comparar nome/artista) |
| RN-04 | Playlist "abandonada" = `last_modified` > 365 dias OU `snapshot_id` inalterado há > 1 ano |
| RN-05 | Faixa "indisponível" = `is_available: false` na resposta da API OU track retornada sem metadata |
| RN-06 | Nova playlist criada via app: privada por default, nome sugerido "Meu Spotify — {filtro} — {data}" |
| RN-07 | Merge de playlists: union por `track_id`, manter ordem da primeira + anexar únicas da segunda |
| RN-08 | Filtro por gênero: usar `artist.genres` (array) — faixa herda gêneros do artista principal |
| RN-09 | Filtro por década: extrair ano do `album.release_date` (primeiros 4 dígitos) |
| RN-10 | Estimativa de horas: `SUM(duration_ms) / 3_600_000` arredondado para inteiro |

---

## 4. Monetização (Visão Futura — Fora do V1)

> **Nota:** V1 é uso pessoal/portfólio (5 usuários Dev Mode). Monetização só faria sentido com **Extended Quota** (empresa registrada + 250k MAU).

| Modelo | Viabilidade | Comentário |
|--------|-------------|------------|
| **Freemium** | Baixa (Dev Mode limita a 5) | Só com Extended Quota |
| **Assinatura mensal (B2C)** | Média | Requer empresa, compliance, pagamentos |
| **Licença única (lifetime)** | Média | Mesmo acima |
| **Open source + doações** | Alta | GitHub Sponsors, Ko-fi; mantém como portfolio |
| **B2B (white label para selos/agências)** | Alta | Valor real: gestão de catálogo de artistas |
| **Feature flags pagas** | Baixa | Complexidade > receita provável |

**Recomendação:** Manter **open source (MIT)** no GitHub como portfolio. Se houver tração, avaliar B2B ou Extended Quota.

---

## 5. Fora do Escopo (Não Fazer)

- Reprodução de música (API não permite)
- Recomendações baseadas em ML próprio (viola ToS: "não usar dados para treinar IA")
- Sincronização/download de áudio (proibido nos termos)
- Transferência de dados para outro serviço (exceto exportação pessoal do usuário)
- Alteração de conteúdo visual (crop artwork, overlay)
- Streaming não-interativo / broadcast
- Qualquer uso comercial de streaming

---

## 6. Critérios de Aceitação do V1 (Definition of Done)

- [ ] Login/logout funciona end-to-end
- [ ] Dashboard carrega stats reais da conta
- [ ] Lista playlists com badges de problemas
- [ ] Detalhe de playlist com ordenação client-side
- [ ] Página Issues mostra: duplicatas intra-playlist, cross-playlist, abandonadas, indisponíveis
- [ ] Criar playlist por filtros (gênero, década, artista) funciona
- [ ] Merge de duas playlists funciona
- [ ] Sync manual (`POST /library/sync`) atualiza banco
- [ ] Testes unitários backend > 80% cobertura
- [ ] Lint passa (ruff, eslint)
- [ ] Build Docker sobe localmente (`docker-compose up`)
- [ ] README com instruções de setup
- [ ] Deploy em staging (opcional)

---
*Documento versionado. Última atualização: 2026-08-20*