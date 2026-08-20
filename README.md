# Meu Spotify

Um painel pessoal para organizar, analisar e gerenciar sua conta do Spotify com foco na experiência do usuário brasileira.

> **Seu Spotify, do seu jeito.**

---

## 🎯 Visão Geral

O Meu Spotify resolve o problema que o app nativo não resolve: **organização real da sua biblioteca**. Com o tempo, playlists duplicadas, músicas repetidas em múltiplas playlists, playlists abandonadas e faixas removidas do catálogo viram um caos. Este projeto detecta esses problemas e dá ações diretas para corrigi-los.

---

## ✨ Funcionalidades (V1 - MVP)

### 📊 Dashboard Pessoal
- Total de músicas, artistas, álbuns e horas de música
- Distribuição por gênero e década (gráficos)
- Top artista da biblioteca

### 🔍 Detecção de Problemas
- Músicas duplicadas dentro de uma playlist
- Músicas que aparecem em múltiplas playlists
- Playlists sem atualização há mais de 1 ano
- Faixas removidas do catálogo do Spotify (indisponíveis)

### 🎵 Organização de Playlists
- Visualização ordenada por artista, álbum ou duração
- Criação de nova playlist a partir de filtros (gênero, década, artista)
- Junção de duas playlists
- Inversão de ordem de playlist

---

## 🛠 Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| **Frontend** | React 19 + TypeScript + Vite + Tailwind CSS v4 + Recharts + TanStack Query |
| **Backend** | FastAPI (Python 3.12) + SQLAlchemy 2.x + PostgreSQL 16 + Redis 7 |
| **Auth** | Spotify OAuth 2.0 (Authorization Code Flow) |
| **Deploy** | Docker Compose (dev) • GitHub Actions CI/CD |

---

## 🚀 Quick Start

### Pré-requisitos
- Docker + Docker Compose
- Conta no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Spotify Premium (obrigatório para o owner do app em Dev Mode)

### 1. Clone e configure
```bash
git clone https://github.com/SEU_USUARIO/meu-spotify.git
cd meu-spotify
cp .env.example .env
```

### 2. Configure as variáveis no `.env`
```bash
# Spotify (pegue no Developer Dashboard)
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback

# Gere chaves seguras:
# SECRET_KEY: openssl rand -base64 32
# FERNET_KEY: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
SECRET_KEY=sua_secret_key_aqui
FERNET_KEY=sua_fernet_key_aqui
```

### 3. Configure o Spotify App
No [Developer Dashboard](https://developer.spotify.com/dashboard):
- Crie um app (ou use existente)
- **Redirect URI**: `http://127.0.0.1:8000/auth/callback` (exato, com `127.0.0.1`)
- Scopes: `user-read-private user-read-email user-library-read playlist-read-private playlist-read-collaborative`
- O **owner do app deve ter Spotify Premium ativo**

### 4. Suba a infraestrutura
```bash
docker-compose up -d
```

### 5. Rode as migrations
```bash
docker-compose exec api alembic upgrade head
```

### 6. Inicie os servidores de desenvolvimento
```bash
# Terminal 1 - Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm install && npm run dev
```

### 7. Acesse
- Frontend: http://127.0.0.1:5173
- Backend API: http://127.0.0.1:8000
- Docs Swagger: http://127.0.0.1:8000/docs

---

## 📁 Estrutura do Projeto

```
meu-spotify/
├── .github/workflows/          # GitHub Actions CI/CD
├── docs/                       # Documentação completa (7 arquivos .md)
├── src/
│   ├── backend/                # FastAPI application
│   │   ├── app/
│   │   │   ├── auth/           # OAuth flow, tokens, sessão
│   │   │   ├── spotify/        # Cliente API Spotify (rate limit, retry, paginação)
│   │   │   ├── users/          # Modelo User + tokens criptografados
│   │   │   ├── playlists/      # CRUD + análise (duplicatas, abandono)
│   │   │   ├── library/        # Stats + issues
│   │   │   └── actions/        # Operações de escrita (V1: cria novas playlists)
│   │   ├── tests/
│   │   └── Dockerfile
│   └── frontend/               # React application
│       ├── src/
│       │   ├── pages/          # Login, Dashboard, Playlists, PlaylistDetail, Issues
│       │   ├── components/     # UI primitives, charts, playlist components
│       │   ├── hooks/          # TanStack Query wrappers
│       │   ├── api/            # Fetch client + endpoints
│       │   └── types/          # Interfaces TypeScript
│       └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📚 Documentação

| Arquivo | Descrição |
|---------|-----------|
| `docs/architecture.md` | Arquitetura geral, pastas, versionamento, GitHub Actions |
| `docs/requirements.md` | Requisitos funcionais/não-funcionais, regras de negócio, monetização |
| `docs/features.md` | Features detalhadas por versão, processos de dados, otimizações |
| `docs/version-history.md` | Roadmap, checklists, bugs, ADRs, changelog |
| `docs/spotify-api.md` | Referência da API Spotify pós-fev/2026 (endpoints, mudanças, rate limit) |
| `docs/backend.md` | Backend completo: models, client, auth, análise, stats, endpoints |
| `docs/frontend.md` | Frontend completo: design system, componentes, páginas, hooks, gráficos |

---

## ⚠️ Restrições Importantes (Spotify API 2026)

| Restrição | Detalhe |
|-----------|---------|
| **Premium obrigatório** | Owner do app no Dashboard precisa ter Premium ativo |
| **5 usuários/app** | Dev Mode limita a 5 usuários autorizados |
| **Endpoints removidos** | `GET /users/{id}/playlists` removido → use `GET /me/playlists` |
| **Campo renomeado** | `tracks` → `items` em playlists |
| **Redirect URI** | Use `127.0.0.1` (não `localhost`) |
| **Search limitado** | Máx 10 resultados por request |

> Para V1 (uso pessoal/portfólio), as restrições de 5 usuários e Premium são **irrelevantes** — é exatamente o escopo correto.

---

## 🧪 Testes e Qualidade

```bash
# Backend
cd backend
pytest --cov=app --cov-report=term-missing
ruff check . && ruff format . --check
mypy app/

# Frontend
cd frontend
npm run lint
npm run typecheck
npm run test
npm run build
```

---

## 📦 Deploy (Produção)

1. **Backend**: Render, Fly.io ou VPS com Docker
2. **Frontend**: Vercel ou Netlify
3. **Banco**: PostgreSQL gerenciado (Neon, Supabase, RDS)
4. **Cache**: Redis gerenciado (Upstash, Redis Cloud)
5. **Variáveis de produção**: Configure no GitHub Secrets / painel da plataforma
6. **Atualize no Spotify Dashboard**: `SPOTIFY_REDIRECT_URI` para URL de produção

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m "feat: descrição da feature"`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

Commits seguem [Conventional Commits](https://www.conventionalcommits.org/).

---

## 📄 Licença

MIT License — uso comercial, modificação e distribuição permitidos.

---

## 🙋‍♂️ Autor

**Eduardo Cicutti**  
Estudante CC CEUNES/UFES • Adapti Soluções Web  
[LinkedIn](https://www.linkedin.com/in/eduardo-cicutti/)

---

*Feito com 💚 para a comunidade brasileira de desenvolvedores e amantes de música.*