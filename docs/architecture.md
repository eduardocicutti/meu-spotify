# Arquitetura do Projeto Meu Spotify

## Nome do Projeto
**Meu Spotify** - Um painel pessoal para organizar, analisar e gerenciar sua conta do Spotify com foco na experiência do usuário brasileira.

## Visão Geral
Aplicação full-stack com separação clara de responsabilidades:
- **Frontend**: Web application construída com React, TypeScript e Tailwind CSS.
- **Backend**: API RESTful desenvolvida com FastAPI (Python) ou Node.js/TypeScript (opcional).
- **Banco de Dados**: PostgreSQL para armazenar dados de usuários, playlists, estatísticas e histórico.
- **Autenticação**: OAuth 2.0 com Spotify (Authorization Code Flow).
- **Integração**: Comunicação segura com a Spotify Web API (endpoints atualizados pós-fevereiro/2026).
- **Deploy**: GitHub Actions para CI/CD, testes automatizados e deployment opcional em plataformas como Vercel (frontend) e Render/Heroku (backend) ou Docker.

## Estrutura de Pastas
```
meu-spotify/
├── .github/
│   └── workflows/            # GitHub Actions workflows
├── docs/                     # Documentação do projeto
├── src/
│   ├── backend/              # Código fonte do backend (FastAPI)
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── endpoints/
│   │   │   │   ├── dependencies/
│   │   │   │   └── routers/
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── security.py
│   │   │   │   └── db.py
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   │   ├── spotify.py
│   │   │   │   └── playlist_service.py
│   │   │   ├── utils/
│   │   │   └── main.py
│   │   ├── tests/            # Testes unitários e de integração
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/             # Código fonte do frontend (React)
│       ├── public/
│       ├── src/
│       │   ├── assets/
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── pages/
│       │   ├── services/
│       │   ├── store/        # (opcional) Redux ou Context API
│       │   ├── styles/       # Tailwind CSS config
│       │   ├── utils/
│       │   ├── App.tsx
│       │   └── index.tsx
│       ├── package.json
│       └── tsconfig.json
├── tests/                    # Testes end-to-end (Cypress ou Playwright)
├── scripts/                  # Scripts auxiliares (migração, seed, etc.)
├── .env.example              # Exemplo de variáveis de ambiente
├── .gitignore
├── README.md
└── docker-compose.yml        # Para desenvolvimento local com PostgreSQL
```

## Regras de Versionamento
- Utilizamos **Semantic Versioning 2.0.0** (MAJOR.MINOR.PATCH).
- Tags no formato `vX.Y.Z` (ex: `v1.0.0`).
- Branches principais:
  - `main` ou `master`: código de produção estável.
  - `develop`: branch de integração para próximas releases.
  - `feature/*`: para novas funcionalidades.
  - `bugfix/*`: para correções.
  - `release/*`: preparação para release.
- Commits seguem o padrão **Conventional Commits**:
  - `feat:` para novas funcionalidades
  - `fix:` para correções de bug
  - `docs:` para alterações na documentação
  - `style:` para formatação, ponto e vírgula, etc.
  - `refactor:` para refatoração de código
  - `test:` para adicionar ou modificar testes
  - `chore:` para tarefas de manutenção
  - Exemplo: `feat: adicionar endpoint de estatísticas de artista`

## Regras de Programação e Comentários de Código
### Geral
- Código deve ser legível e autoexplicativo; comentários adicionais apenas quando a intenção não é óbvia.
- Use linguagem inglesa para nomes de variáveis, funções, classes e comentários (padrão internacional).
- Linha máxima: 100 caracteres (configurável via editorconfig/.editorconfig).
- Indentation: 2 espaços (não usar tabs).

### Python (Backend)
- Follow **PEP 8** e **PEP 257** (docstrings).
- Utilize type hints (PEP 484) em todas as funções e métodos.
- Docstrings no estilo **Google** ou **NumPy**.
- Evite imports circulares; use dependency injection quando necessário.
- Tratamento de exceções: capturar exceções específicas, nunca use `except:` genérico.
- Logs: utilize o módulo `logging` com níveis apropriados (DEBUG, INFO, WARNING, ERROR).
- Testes: escreva testes unitários com `pytest`; objetivo de cobertura >80%.

### TypeScript (Frontend)
- Follow **Airbnb JavaScript Style Guide** adaptado para TypeScript (via `eslint-config-airbnb-typescript`).
- Utilize `strict` mode no `tsconfig.json`.
- Nomenclatura:
  - Componentes: PascalCase (ex: `ArtistCard.tsx`)
  - Funções e variáveis: camelCase
  - Constantes: UPPER_SNAKE_CASE
  - Interfaces e types: PascalCase com prefixo `I` opcional (ex: `IArtist` ou `Artist`)
- Comentários:
  - Use `//` para comentários de linha.
  - Use `/** ... */` para JSDoc em funções exportáveis e componentes.
- Evite `any`; quando necessário, descreva o motivo em comentário.
- Componentes funcionais com hooks; evitar componentes de classe salvo exceções.
- Gerenciamento de estado: preferir Context API ou Zustand/Jotai para estado global; evitar Redux exceto se justificado.

### Git Commits
- Mensagem no formato: `<tipo>(<escopo>): <descrição>`
  - Exemplo: `feat(backend): adicionar endpoint /me/playlists`
- Corpo opcional, separado por linha em branco.
- Rodapé opcional para referências a issues (ex: `Fixes #123`).

## GitHub Actions (CI/CD)
Arquivos em `.github/workflows/`:

### `ci.yml` - Integração Contínua
- Disparado em pull_request e push para branches `main` e `develop`.
- Jobs:
  1. **Setup**: configurar cache de dependências (pip, npm).
  2. **Backend**:
     - Instalar dependências (`pip install -r requirements.txt`).
     - Executar linter (`flake8` ou `ruff`).
     - Executar testes (`pytest --cov=app --cov-report=xml`).
  3. **Frontend**:
     - Instalar dependências (`npm ci`).
     - Executar linter (`eslint`).
     - Executar testes unitários (`npm test` ou `vitest run`).
     - Build de produção (`npm run build`).
  4. **Security** (opcional):
     - Rodar `bandit` (Python) e `npm audit` ou `snyk test`.

### `cd.yml` - Deploy Contínuo (exemplo)
- Disparado em push para tag `v*` ou merges em `main` após CI aprovada.
- Jobs:
  1. **Backend**: build Docker image, push para registry (ex: GitHub Packages, Docker Hub), deploy em serviço escolhido (Render, Fly.io, VPS).
  2. **Frontend**: build artifacts, deploy em Vercel/Netlify ou bucket S3 + CloudFront.
  3. **Notificação**: enviar mensagem para Slack/Discord/Telegram com status.

### Outras workflows úteis
- `stale.yml`: marcar issues e PRs antigos como stale.
- `dependabot.yml`: atualizar dependências automáticamente.
- `release.yml`: criar release no GitHub ao fazer push de tag.

## Considerações de Escalabilidade e Performance
- **Rate Limiting da Spotify API**: implementar mecanismo de retry com backoff exponencial e respectar cabeçalhos `Retry-After`.
- **Cache**: utilizar Redis (opcional) para cache de dados de perfil e playlists que mudam raramente.
- **Processamento Assíncrono**: para tarefas pesadas (reorganização de playlists, geração de estatísticas) usar filas (Celery com RabbitMQ/Redis ou BullMQ no Node).
- **Paginação**: respeitar limites de paginação da Spotify API (máximo 50 ou 100 items por request) e implementar iteradores internos.
- **Segurança**: nunca armazenar tokens de acesso ou refresh em plain text; usar criptografia (ex: Fernet) no banco ou vault dedicado.
- **Monitoramento**: integrar com Sentry ou LogRocket para capturar erros; usar Prometheus + Grafana para métricas de backend (latência, taxa de erro).

## Licença
MIT License - permite uso comercial, modificação e distribuição.

---
*Documento versionado junto ao código. Última atualização: $(date +%Y-%m-%d)*