# Frontend — Meu Spotify (React + TypeScript + Tailwind v4)

## 1. Stack e Versões

| Componente | Versão | Justificativa |
|------------|--------|---------------|
| React | 19 | Concurrent features, Server Components ready |
| TypeScript | 5.6+ | Strict mode, type safety |
| Vite | 5.x | Build rápido, HMR, otimizado |
| Tailwind CSS | 4.0 | Zero-config, CSS-first, performance |
| TanStack Query | 5.x | Server state, cache, staleTime, prefetch |
| React Router | 7 | File-based routing, data loading |
| Recharts | 2.12+ | Gráficos declarativos, responsivos |
| Lucide React | 0.45+ | Ícones SVG leves, tree-shakable |
| Vitest | 2.x | Testes unitários rápidos |
| ESLint | 9.x | Flat config, TypeScript support |
| Prettier | 3.x | Formatação consistente |

---

## 2. Estrutura de Pastas (Detalhada)

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── main.tsx                    # Entry point, providers
│   ├── App.tsx                     # Router raiz, AuthGuard, layout
│   ├── vite-env.d.ts
│   │
│   ├── pages/                      # Páginas (route components)
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Playlists.tsx
│   │   ├── PlaylistDetail.tsx
│   │   └── Issues.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── PageShell.tsx       # Wrapper com sidebar + header
│   │   ├── ui/                     # Primitivos próprios (sem UI kit)
│   │   │   ├── Button.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── StatCard.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── Accordion.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Select.tsx
│   │   │   └── Input.tsx
│   │   ├── charts/
│   │   │   ├── GenreBars.tsx       # Barras horizontais de gênero
│   │   │   └── DecadeBars.tsx      # Barras horizontais de década
│   │   └── playlists/
│   │       ├── PlaylistCard.tsx
│   │       ├── TrackRow.tsx
│   │       ├── TrackTable.tsx
│   │       └── IssueItem.tsx
│   │
│   ├── hooks/                      # Custom hooks (TanStack Query wrappers)
│   │   ├── useAuth.ts
│   │   ├── useLibraryStats.ts
│   │   ├── usePlaylists.ts
│   │   ├── usePlaylist.ts
│   │   ├── usePlaylistIssues.ts
│   │   └── useLibraryIssues.ts
│   │
│   ├── api/
│   │   ├── client.ts               # Fetch wrapper + 401 handling
│   │   └── endpoints.ts            # Constantes de paths
│   │
│   ├── store/                      # Estado global mínimo (AuthContext)
│   │   └── AuthContext.tsx
│   │
│   ├── types/
│   │   └── index.ts                # Interfaces TypeScript compartilhadas
│   │
│   ├── utils/
│   │   ├── format.ts               # formatDuration, formatNumber, formatDate
│   │   ├── constants.ts            # Cores, breakpoints, config
│   │   └── cn.ts                   # clsx + tailwind-merge helper
│   │
│   └── styles/
│       ├── globals.css             # Tailwind v4 @import + variáveis CSS
│       └── variables.css           # Design tokens (cores, spacing, typography)
│
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.ts              # v4 usa CSS, mas pode ter config opcional
├── eslint.config.js                # Flat config
├── prettier.config.js
├── vitest.config.ts
└── .env.example
```

---

## 3. Design System (Tokens)

### 3.1 Cores (CSS Variables)

```css
/* src/styles/variables.css */
:root {
  /* Base */
  --bg-base: #0f0f0f;        /* fundo principal */
  --bg-surface: #1a1a1a;     /* cards, sidebar */
  --bg-elevated: #242424;    /* hover, modais */
  --border: #2e2e2e;         /* divisores */
  
  /* Texto */
  --text-primary: #f0f0f0;   /* títulos, valores */
  --text-secondary: #b0b0b0; /* corpo */
  --text-muted: #888888;     /* labels, metadados */
  --text-inverse: #0f0f0f;   /* texto sobre accent */
  
  /* Accent (Spotify Green - uso parcimonioso) */
  --accent: #1ed760;
  --accent-dim: #1a9e47;     /* hover */
  --accent-bg: rgba(30, 215, 96, 0.1);
  
  /* Semantic */
  --danger: #e5534b;
  --danger-bg: rgba(229, 83, 75, 0.1);
  --warning: #e8a44a;
  --warning-bg: rgba(232, 164, 74, 0.1);
  --success: #1ed760;
  --success-bg: rgba(30, 215, 96, 0.1);
  
  /* Tipografia */
  --font-display: 'DM Sans', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Escala tipográfica */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  --text-5xl: 3rem;      /* 48px */
  
  /* Spacing */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  
  /* Border Radius */
  --radius-sm: 0.375rem;  /* 6px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}

/* Dark mode é padrão; light mode se necessário no futuro */
@media (prefers-color-scheme: light) {
  :root {
    --bg-base: #ffffff;
    --bg-surface: #f5f5f5;
    --bg-elevated: #ffffff;
    --border: #e0e0e0;
    --text-primary: #181818;
    --text-secondary: #333333;
    --text-muted: #666666;
  }
}
```

### 3.2 Globals CSS (Tailwind v4)

```css
/* src/styles/globals.css */
@import "tailwindcss";
@import "./variables.css";

/* Base */
* {
  box-sizing: border-box;
}

html {
  color-scheme: dark;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-body);
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.5;
  min-height: 100vh;
}

/* Tipografia display */
.font-display {
  font-family: var(--font-display);
}

/* Scrollbar sutil */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: var(--bg-base);
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: var(--radius-full);
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* Focus visible para acessibilidade */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

/* Animações */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Utility classes customizadas */
@utility container-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

@utility card-base {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

@utility text-gradient {
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-muted) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
```

---

## 4. Componentes UI Primitivos

### 4.1 Button
```tsx
// src/components/ui/Button.tsx
import { forwardRef, ButtonHTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, disabled, children, ...props }, ref) => {
    const base = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg-base)] disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      primary: 'bg-[var(--accent)] text-[var(--text-inverse)] hover:bg-[var(--accent-dim)] focus-visible:ring-[var(--accent)]',
      secondary: 'bg-[var(--bg-elevated)] text-[var(--text-primary)] border border-[var(--border)] hover:bg-[var(--border)] focus-visible:ring-[var(--border)]',
      ghost: 'text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)] focus-visible:ring-[var(--border)]',
      danger: 'bg-[var(--danger)] text-white hover:opacity-90 focus-visible:ring-[var(--danger)]',
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-base gap-2',
      lg: 'px-6 py-3 text-lg gap-2.5',
    };
    
    return (
      <button
        ref={ref}
        className={cn(base, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

### 4.2 StatCard
```tsx
// src/components/ui/StatCard.tsx
import { cn } from '@/utils/cn';

interface StatCardProps {
  value: string | number;
  label: string;
  trend?: { value: number; label: string };
  className?: string;
}

export function StatCard({ value, label, trend, className }: StatCardProps) {
  return (
    <div className={cn('card-base p-6', className)}>
      <p className="font-display text-5xl font-bold text-[var(--text-primary)] tracking-tight">
        {value}
      </p>
      <p className="mt-2 text-sm text-[var(--text-muted)] font-medium">{label}</p>
      {trend && (
        <p className="mt-3 text-xs font-medium flex items-center gap-1">
          <span className={trend.value >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}>
            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
          <span className="text-[var(--text-muted)]">{trend.label}</span>
        </p>
      )}
    </div>
  );
}
```

### 4.3 Skeleton
```tsx
// src/components/ui/Skeleton.tsx
import { cn } from '@/utils/cn';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded bg-[var(--bg-elevated)]', className)}
      {...props}
    />
  );
}

// Usage examples:
// <Skeleton className="h-10 w-24" />        // StatCard value
// <Skeleton className="h-4 w-16 mt-2" />    // StatCard label
// <Skeleton className="h-12 w-full" />      // Playlist card
// <Skeleton className="h-8 w-3/4" />        // Track row
```

### 4.4 Accordion (para página Issues)
```tsx
// src/components/ui/Accordion.tsx
import { useState, forwardRef } from 'react';
import { cn } from '@/utils/cn';
import { ChevronDown } from 'lucide-react';

interface AccordionProps {
  title: string;
  count?: number;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export const Accordion = forwardRef<HTMLDivElement, AccordionProps>(
  ({ title, count, children, defaultOpen = false, className, ...props }, ref) => {
    const [open, setOpen] = useState(defaultOpen);
    
    return (
      <div ref={ref} className={cn('card-base overflow-hidden', className)} {...props}>
        <button
          className="w-full px-6 py-4 flex items-center justify-between text-left gap-4"
          onClick={() => setOpen(!open)}
          aria-expanded={open}
        >
          <div className="flex items-center gap-3">
            <h3 className="font-display text-xl font-semibold text-[var(--text-primary)]">
              {title}
            </h3>
            {count !== undefined && (
              <span className="px-2 py-0.5 text-xs font-medium bg-[var(--bg-elevated)] text-[var(--text-secondary)] rounded-full">
                {count}
              </span>
            )}
          </div>
          <ChevronDown
            className={cn('h-5 w-5 text-[var(--text-muted)] transition-transform', open && 'rotate-180')}
            aria-hidden="true"
          />
        </button>
        <div
          className={cn('transition-all duration-200 overflow-hidden', open ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0')}
        >
          <div className="px-6 pb-6 border-t border-[var(--border)]">
            {children}
          </div>
        </div>
      </div>
    );
  }
);

Accordion.displayName = 'Accordion';
```

---

## 5. Páginas

### 5.1 Login
```tsx
// src/pages/Login.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Music } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { apiClient } from '@/api/client';

export function Login() {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Se já autenticado, redirect para dashboard
    apiClient.get('/auth/me').then(() => navigate('/')).catch(() => {});
  }, [navigate]);
  
  const handleLogin = () => {
    window.location.href = '/auth/login';
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg-base)] px-4">
      <div className="w-full max-w-md text-center">
        <div className="mb-10">
          <Music className="h-16 w-16 mx-auto text-[var(--accent)]" aria-hidden="true" />
        </div>
        <h1 className="font-display text-4xl font-bold text-[var(--text-primary)] mb-3">
          Meu Spotify
        </h1>
        <p className="text-[var(--text-muted)] mb-10">
          Seu Spotify, do seu jeito.
        </p>
        <Button onClick={handleLogin} size="lg" className="w-full">
          Entrar com Spotify
        </Button>
        <p className="mt-6 text-xs text-[var(--text-muted)]">
          Você será redirecionado para autorizar o acesso aos seus dados.
        </p>
      </div>
    </div>
  );
}
```

### 5.2 Dashboard
```tsx
// src/pages/Dashboard.tsx
import { useLibraryStats } from '@/hooks/useLibraryStats';
import { useLibraryIssues } from '@/hooks/useLibraryIssues';
import { StatCard } from '@/components/ui/StatCard';
import { GenreBars } from '@/components/charts/GenreBars';
import { DecadeBars } from '@/components/charts/DecadeBars';
import { Accordion } from '@/components/ui/Accordion';
import { IssueItem } from '@/components/playlists/IssueItem';
import { Link } from 'react-router';
import { AlertTriangle, Clock, Music, Users, TrendingUp } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useLibraryStats();
  const { data: issues, isLoading: issuesLoading } = useLibraryIssues();
  
  if (statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-28 card-base p-6" />
          <Skeleton className="h-28 card-base p-6" />
          <Skeleton className="h-28 card-base p-6" />
        </div>
        <Skeleton className="h-64 card-base p-6" />
        <Skeleton className="h-64 card-base p-6" />
      </div>
    );
  }
  
  const userName = 'Eduardo'; // TODO: do auth context
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-[var(--text-primary)]">
            Olá, {userName} 👋
          </h1>
          <p className="text-[var(--text-muted)] mt-1">
            Visão geral da sua biblioteca
          </p>
        </div>
      </div>
      
      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          value={stats?.total_tracks?.toLocaleString('pt-BR') ?? '—'}
          label="músicas"
        />
        <StatCard
          value={stats?.total_artists?.toLocaleString('pt-BR') ?? '—'}
          label="artistas"
        />
        <StatCard
          value={`${stats?.total_hours ?? '—'}h`}
          label="ouvindo"
        />
      </div>
      
      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card-base p-6">
          <h2 className="font-display text-xl font-semibold mb-6">Seu gosto musical</h2>
          <GenreBars data={stats?.genre_distribution ?? {}} />
        </div>
        <div className="card-base p-6">
          <h2 className="font-display text-xl font-semibold mb-6">Por década</h2>
          <DecadeBars data={stats?.decade_distribution ?? {}} />
        </div>
      </div>
      
      {/* Issues Summary */}
      <div className="card-base p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-display text-xl font-semibold flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-[var(--warning)]" />
            Problemas encontrados
          </h2>
          <Link to="/issues" className="text-sm text-[var(--accent)] hover:underline">
            Ver tudo →
          </Link>
        </div>
        
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <IssueSummaryCard
            icon={Music}
            count={issues?.duplicates_cross_count ?? 0}
            label="Músicas em múltiplas playlists"
            color="warning"
          />
          <IssueSummaryCard
            icon={AlertTriangle}
            count={issues?.duplicates_intra_count ?? 0}
            label="Duplicatas dentro de playlists"
            color="danger"
          />
          <IssueSummaryCard
            icon={Clock}
            count={issues?.abandoned_playlists_count ?? 0}
            label="Playlists abandonadas (>1 ano)"
            color="warning"
          />
          <IssueSummaryCard
            icon={TrendingUp}
            count={issues?.unavailable_tracks_count ?? 0}
            label="Faixas indisponíveis"
            color="danger"
          />
        </div>
      </div>
    </div>
  );
}

function IssueSummaryCard({ icon: Icon, count, label, color }: { icon: React.ComponentType; count: number; label: string; color: 'warning' | 'danger' }) {
  const colors = {
    warning: 'text-[var(--warning)] bg-[var(--warning-bg)]',
    danger: 'text-[var(--danger)] bg-[var(--danger-bg)]',
  };
  
  return (
    <div className="card-base p-4 hover:border-[var(--accent)] transition-colors">
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-lg', colors[color])}>
          <Icon className="h-5 w-5" aria-hidden="true" />
        </div>
        <div>
          <p className="font-display text-2xl font-bold text-[var(--text-primary)]">{count}</p>
          <p className="text-sm text-[var(--text-muted)]">{label}</p>
        </div>
      </div>
    </div>
  );
}
```

### 5.3 Playlists (Lista)
```tsx
// src/pages/Playlists.tsx
import { usePlaylists } from '@/hooks/usePlaylists';
import { PlaylistCard } from '@/components/playlists/PlaylistCard';
import { Skeleton } from '@/components/ui/Skeleton';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Search, Filter } from 'lucide-react';
import { useMemo, useState } from 'react';

export function Playlists() {
  const { data: playlists, isLoading, refetch } = usePlaylists();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'tracks' | 'date'>('date');
  
  const filtered = useMemo(() => {
    let result = playlists ?? [];
    if (search) {
      result = result.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));
    }
    result = [...result].sort((a, b) => {
      switch (sortBy) {
        case 'name': return a.name.localeCompare(b.name, 'pt-BR');
        case 'tracks': return b.track_count - a.track_count;
        case 'date': return new Date(b.last_modified || 0).getTime() - new Date(a.last_modified || 0).getTime();
      }
    });
    return result;
  }, [playlists, search, sortBy]);
  
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex gap-4">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-10 w-40" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-32 card-base" />)}
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold">Suas playlists</h1>
          <p className="text-[var(--text-muted)]">{filtered.length} playlists</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-muted)]" />
            <Input
              placeholder="Buscar playlists..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select
            value={sortBy}
            onValueChange={setSortBy}
            options={[
              { value: 'date', label: 'Mais recentes' },
              { value: 'name', label: 'Nome (A-Z)' },
              { value: 'tracks', label: 'Mais faixas' },
            ]}
            className="w-full sm:w-40"
          />
        </div>
      </div>
      
      {filtered.length === 0 ? (
        <div className="card-base p-12 text-center">
          <p className="text-[var(--text-muted)]">Nenhuma playlist encontrada.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map(playlist => (
            <PlaylistCard key={playlist.id} playlist={playlist} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### 5.4 Playlist Detail
```tsx
// src/pages/PlaylistDetail.tsx
import { useParams, useNavigate } from 'react-router';
import { usePlaylist } from '@/hooks/usePlaylist';
import { usePlaylistIssues } from '@/hooks/usePlaylistIssues';
import { TrackTable } from '@/components/playlists/TrackTable';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router';
import { Skeleton } from '@/components/ui/Skeleton';
import { useMemo } from 'react';

export function PlaylistDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: playlist, isLoading } = usePlaylist(id!);
  const { data: issues } = usePlaylistIssues(id!);
  const [sortBy, setSortBy] = useState<'artist' | 'album' | 'duration'>('artist');
  
  const sortedTracks = useMemo(() => {
    if (!playlist?.tracks) return [];
    const tracks = [...playlist.tracks];
    switch (sortBy) {
      case 'artist':
        return tracks.sort((a, b) => a.artist_names[0].localeCompare(b.artist_names[0], 'pt-BR'));
      case 'album':
        return tracks.sort((a, b) => (a.album_name || '').localeCompare(b.album_name || '', 'pt-BR'));
      case 'duration':
        return tracks.sort((a, b) => a.duration_ms - b.duration_ms);
    }
  }, [playlist?.tracks, sortBy]);
  
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="flex gap-4">
          <Skeleton className="h-10 w-40" />
        </div>
        {[...Array(10)].map((_, i) => <Skeleton key={i} className="h-12 w-full card-base p-4" />)}
      </div>
    );
  }
  
  if (!playlist) {
    return (
      <div className="card-base p-12 text-center">
        <p className="text-[var(--text-muted)]">Playlist não encontrada.</p>
        <Button variant="secondary" onClick={() => navigate('/playlists')} className="mt-4">
          Voltar às playlists
        </Button>
      </div>
    );
  }
  
  const totalDuration = playlist.tracks.reduce((sum, t) => sum + t.duration_ms, 0);
  const formatDuration = (ms: number) => {
    const mins = Math.floor(ms / 60000);
    const secs = Math.floor((ms % 60000) / 1000);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Playlists
        </Button>
        <div className="flex-1">
          <h1 className="font-display text-3xl font-bold">{playlist.name}</h1>
          <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-[var(--text-muted)]">
            <span>{playlist.track_count} faixas</span>
            <span>•</span>
            <span>{formatDuration(totalDuration)}</span>
            {playlist.last_modified && (
              <>
                <span>•</span>
                <span>Atualizada {formatRelativeDate(playlist.last_modified)}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Select
            value={sortBy}
            onValueChange={setSortBy}
            options={[
              { value: 'artist', label: 'Artista' },
              { value: 'album', label: 'Álbum' },
              { value: 'duration', label: 'Duração' },
            ]}
            className="w-40"
          />
        </div>
      </div>
      
      {/* Issues badge */}
      {(issues?.duplicates_intra_count ?? 0) > 0 || (issues?.unavailable_count ?? 0) > 0 ? (
        <div className="card-base p-4 border-[var(--warning)] flex items-center justify-between">
          <div className="flex items-center gap-2 text-[var(--warning)]">
            <AlertTriangle className="h-5 w-5" />
            <span className="font-medium">
              {(issues?.duplicates_intra_count ?? 0) + (issues?.unavailable_count ?? 0)} problemas encontrados
            </span>
          </div>
          <Link to={`/issues?playlist=${id}`} className="text-sm text-[var(--accent)] hover:underline">
            Ver issues
          </Link>
        </div>
      ) : null}
      
      {/* Track Table */}
      <TrackTable tracks={sortedTracks} />
    </div>
  );
}

function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / 86400000);
  if (diffDays === 0) return 'hoje';
  if (diffDays === 1) return 'ontem';
  if (diffDays < 7) return `${diffDays}d atrás`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}sem atrás`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}m atrás`;
  return `${Math.floor(diffDays / 365)}a atrás`;
}
```

### 5.5 Issues ("Arrume seu Spotify")
```tsx
// src/pages/Issues.tsx
import { useLibraryIssues } from '@/hooks/useLibraryIssues';
import { Accordion } from '@/components/ui/Accordion';
import { IssueItem } from '@/components/playlists/IssueItem';
import { Skeleton } from '@/components/ui/Skeleton';
import { Music, AlertTriangle, Clock, TrendingUp } from 'lucide-react';

export function Issues() {
  const { data: issues, isLoading } = useLibraryIssues();
  
  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card-base p-6 animate-pulse">
            <Skeleton className="h-6 w-48 mb-4" />
            {[...Array(3)].map((_, j) => <Skeleton key={j} className="h-10 w-full mb-2" />)}
          </div>
        ))}
      </div>
    );
  }
  
  const sections = [
    {
      key: 'duplicates_cross',
      title: 'Músicas em múltiplas playlists',
      icon: Music,
      count: issues?.duplicates_cross?.length ?? 0,
      items: issues?.duplicates_cross ?? [],
      renderItem: (item: any) => (
        <IssueItem
          trackName={item.track_name}
          artistNames={item.artist_names}
          detail={`${item.playlist_count} playlists`}
          playlists={item.playlist_ids}
        />
      ),
    },
    {
      key: 'duplicates_intra',
      title: 'Músicas duplicadas na mesma playlist',
      icon: AlertTriangle,
      count: issues?.duplicates_intra?.length ?? 0,
      items: issues?.duplicates_intra ?? [],
      renderItem: (item: any) => (
        <IssueItem
          trackName={item.track_name}
          artistNames={item.artist_names}
          detail={`${item.count}x na mesma playlist`}
          playlistId={item.playlist_id}
        />
      ),
    },
    {
      key: 'abandoned',
      title: 'Playlists sem atualização há mais de 1 ano',
      icon: Clock,
      count: issues?.abandoned_playlists?.length ?? 0,
      items: issues?.abandoned_playlists ?? [],
      renderItem: (item: any) => (
        <IssueItem
          trackName={item.name}
          detail={`Última mudança: ${item.days_abandoned} dias atrás`}
          playlistId={item.id}
        />
      ),
    },
    {
      key: 'unavailable',
      title: 'Faixas indisponíveis (removidas do Spotify)',
      icon: TrendingUp,
      count: issues?.unavailable_tracks?.length ?? 0,
      items: issues?.unavailable_tracks ?? [],
      renderItem: (item: any) => (
        <IssueItem
          trackName={item.track_name || 'Faixa indisponível'}
          artistNames={item.artist_names}
          detail={`Em: ${item.playlist_name}`}
          playlistId={item.playlist_id}
        />
      ),
    },
  ];
  
  const totalIssues = sections.reduce((sum, s) => sum + s.count, 0);
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold">Arrume seu Spotify</h1>
        <p className="text-[var(--text-muted)] mt-1">
          {totalIssues > 0 
            ? `Encontramos ${totalIssues} problema${totalIssues !== 1 ? 's' : ''} na sua biblioteca.`
            : 'Sua biblioteca está organizada! 🎉'}
        </p>
      </div>
      
      {totalIssues === 0 ? (
        <div className="card-base p-12 text-center">
          <div className="text-6xl mb-4">✨</div>
          <h2 className="font-display text-xl font-semibold mb-2">Tudo em ordem</h2>
          <p className="text-[var(--text-muted)]">Nenhum problema detectado na sua biblioteca.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sections.map(section => 
            section.count > 0 && (
              <Accordion key={section.key} title={section.title} count={section.count} defaultOpen={true}>
                <div className="space-y-2">
                  {section.items.map((item, idx) => (
                    <section.renderItem(item) key={`${section.key}-${idx}`} />
                  ))}
                </div>
              </Accordion>
            )
          )}
        </div>
      )}
    </div>
  );
}
```

---

## 6. Hooks (TanStack Query)

```typescript
// src/hooks/useLibraryStats.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { LibraryStats } from '@/types';

export function useLibraryStats() {
  return useQuery<LibraryStats>({
    queryKey: ['library', 'stats'],
    queryFn: () => apiClient.get<LibraryStats>('/library/stats'),
    staleTime: 1000 * 60 * 15, // 15 minutos
  });
}

// src/hooks/usePlaylists.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { Playlist } from '@/types';

export function usePlaylists() {
  return useQuery<Playlist[]>({
    queryKey: ['playlists'],
    queryFn: () => apiClient.get<Playlist[]>('/playlists'),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

// src/hooks/usePlaylist.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { PlaylistDetail } from '@/types';

export function usePlaylist(id: string) {
  return useQuery<PlaylistDetail>({
    queryKey: ['playlists', id],
    queryFn: () => apiClient.get<PlaylistDetail>(`/playlists/${id}`),
    enabled: !!id,
    staleTime: 1000 * 60 * 10, // 10 minutos
  });
}

// src/hooks/useLibraryIssues.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { LibraryIssues } from '@/types';

export function useLibraryIssues() {
  return useQuery<LibraryIssues>({
    queryKey: ['library', 'issues'],
    queryFn: () => apiClient.get<LibraryIssues>('/library/issues'),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

// src/hooks/usePlaylistIssues.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { PlaylistIssues } from '@/types';

export function usePlaylistIssues(playlistId: string) {
  return useQuery<PlaylistIssues>({
    queryKey: ['playlists', playlistId, 'issues'],
    queryFn: () => apiClient.get<PlaylistIssues>(`/playlists/${playlistId}/issues`),
    enabled: !!playlistId,
    staleTime: 1000 * 60 * 5,
  });
}
```

---

## 7. API Client

```typescript
// src/api/client.ts
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

class ApiClient {
  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      credentials: 'include', // Importante: envia cookie de sessão
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (res.status === 401) {
      // Redireciona para login se não autenticado
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      throw new Error('Não autenticado');
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: `Erro ${res.status}` }));
      throw new Error(error.detail || `Erro ${res.status}`);
    }

    if (res.status === 204) {
      return undefined as T;
    }

    return res.json();
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'POST', body: JSON.stringify(body) });
  }

  put<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'PUT', body: JSON.stringify(body) });
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
```

---

## 8. Types (Compartilhados)

```typescript
// src/types/index.ts

export interface User {
  id: string;
  display_name: string | null;
  email: string | null;
  images: { url: string; height: number; width: number }[];
}

export interface Playlist {
  id: string;
  name: string;
  description: string | null;
  track_count: number;
  images: { url: string; height: number; width: number }[];
  last_modified: string | null;
  snapshot_id: string | null;
  has_issues: boolean;
  issues_count: number;
}

export interface PlaylistTrack {
  track_id: string;
  track_name: string;
  artist_names: string[];
  artist_ids: string[];
  album_name: string | null;
  album_id: string | null;
  duration_ms: number;
  added_at: string;
  is_available: boolean;
  release_year: number | null;
  position: number;
}

export interface PlaylistDetail extends Playlist {
  tracks: PlaylistTrack[];
}

export interface LibraryStats {
  total_tracks: number;
  total_artists: number;
  total_hours: number;
  top_artist: { name: string; track_count: number } | null;
  genre_distribution: Record<string, number>;
  decade_distribution: Record<string, number>;
}

export interface LibraryIssues {
  duplicates_intra_count: number;
  duplicates_intra_playlists_affected: number;
  duplicates_cross_count: number;
  abandoned_playlists_count: number;
  unavailable_tracks_count: number;
  // Detalhes (opcional, para página Issues)
  duplicates_intra?: IntraDuplicate[];
  duplicates_cross?: CrossDuplicate[];
  abandoned_playlists?: AbandonedPlaylist[];
  unavailable_tracks?: UnavailableTrack[];
}

export interface IntraDuplicate {
  playlist_id: string;
  track_id: string;
  track_name: string;
  positions: number[];
  count: number;
}

export interface CrossDuplicate {
  track_id: string;
  track_name: string;
  artist_names: string[];
  playlist_ids: string[];
  playlist_count: number;
}

export interface AbandonedPlaylist {
  id: string;
  name: string;
  track_count: number;
  last_modified: string | null;
  days_abandoned: number | null;
}

export interface UnavailableTrack {
  track_id: string;
  track_name: string | null;
  artist_names: string[];
  playlist_id: string;
  playlist_name: string;
  added_at: string;
}

export interface PlaylistIssues {
  duplicates_intra_count: number;
  unavailable_count: number;
  duplicates_intra?: IntraDuplicate[];
  unavailable_tracks?: UnavailableTrack[];
}

export interface ActionResponse {
  playlist_id: string;
  name: string;
  track_count: number;
}

export interface CreateFilterRequest {
  genres?: string[];
  decades?: string[];
  artist_ids?: string[];
  max_duration_ms?: number;
  name?: string;
}

export interface MergeRequest {
  playlist_id_1: string;
  playlist_id_2: string;
  name?: string;
}
```

---

## 9. Gráficos (Recharts)

```tsx
// src/components/charts/GenreBars.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { cn } from '@/utils/cn';

interface GenreBarsProps {
  data: Record<string, number>;
  className?: string;
}

const COLORS = [
  'var(--accent)',
  '#7c3aed', // purple
  '#ec4899', // pink
  '#f97316', // orange
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f43f5e', // rose
  '#6366f1', // indigo
  '#14b8a6', // teal
  '#eab308', // yellow
];

export function GenreBars({ data, className }: GenreBarsProps) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  
  if (entries.length === 0) {
    return (
      <div className={cn('h-64 flex items-center justify-center', className)}>
        <p className="text-[var(--text-muted)]">Nenhum dado de gênero disponível</p>
      </div>
    );
  }
  
  const chartData = entries.map(([name, value], i) => ({
    name: name.length > 20 ? name.slice(0, 18) + '…' : name,
    value,
    percentage: ((value / total) * 100).toFixed(1),
    color: COLORS[i % COLORS.length],
  }));
  
  return (
    <div className={cn('h-64', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <YAxis
            type="category"
            dataKey="name"
            width={140}
            tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-body)' }}
            axisLine={false}
            tickLine={false}
          />
          <XAxis
            type="number"
            hide={true}
            tick={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
            }}
            formatter={(value: number, name: string) => [value, name]}
            labelFormatter={(name: string) => {
              const item = chartData.find(d => d.name === name);
              return item ? `${item.name} — ${item.percentage}%` : name;
            }}
          />
          <Bar
            dataKey="value"
            radius={[0, 4, 4, 0]}
            maxBarSize={24}
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-2 mt-4" role="list" aria-label="Legenda de gêneros">
        {chartData.map((entry, i) => (
          <div key={i} className="flex items-center gap-1.5 text-xs" role="listitem">
            <span
              className="w-3 h-3 rounded"
              style={{ backgroundColor: entry.color }}
              aria-hidden="true"
            />
            <span className="text-[var(--text-secondary)]">{entry.name}</span>
            <span className="text-[var(--text-muted)]">{entry.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

```tsx
// src/components/charts/DecadeBars.tsx
// Similar a GenreBars mas ordenado cronologicamente
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { cn } from '@/utils/cn';

interface DecadeBarsProps {
  data: Record<string, number>;
  className?: string;
}

const DECADE_COLOR = 'var(--accent)';

export function DecadeBars({ data, className }: DecadeBarsProps) {
  const entries = Object.entries(data)
    .filter(([decade]) => decade !== 'undefined')
    .sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
  
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  
  if (entries.length === 0) {
    return (
      <div className={cn('h-64 flex items-center justify-center', className)}>
        <p className="text-[var(--text-muted)]">Nenhum dado de década disponível</p>
      </div>
    );
  }
  
  const chartData = entries.map(([decade, value]) => ({
    name: decade,
    value,
    percentage: ((value / total) * 100).toFixed(1),
  }));
  
  return (
    <div className={cn('h-64', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <YAxis
            type="category"
            dataKey="name"
            width={80}
            tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-body)' }}
            axisLine={false}
            tickLine={false}
          />
          <XAxis type="number" hide={true} tick={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-primary)',
            }}
            labelFormatter={(name: string) => {
              const item = chartData.find(d => d.name === name);
              return item ? `${item.name} — ${item.percentage}%` : name;
            }}
          />
          <Bar dataKey="value" fill={DECADE_COLOR} radius={[0, 4, 4, 0]} maxBarSize={24} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## 10. Utilitários

```typescript
// src/utils/cn.ts
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: (string | undefined | null | false | Record<string, boolean>)[]) {
  return twMerge(clsx(inputs));
}
```

```typescript
// src/utils/format.ts
export function formatDuration(ms: number): string {
  const mins = Math.floor(ms / 60000);
  const secs = Math.floor((ms % 60000) / 1000);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('pt-BR').format(num);
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffDays === 0) return 'hoje';
  if (diffDays === 1) return 'ontem';
  if (diffDays < 7) return `${diffDays}d atrás`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}sem atrás`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)}m atrás`;
  return `${Math.floor(diffDays / 365)}a atrás`;
}
```

---

## 11. Configurações

### 11.1 Vite
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/library': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/playlists': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/actions': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router'],
          charts: ['recharts'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
});
```

### 11.2 Tailwind v4 (via CSS)
```typescript
// tailwind.config.ts (opcional, v4 usa CSS)
import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
```

### 11.3 TypeScript
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 12. Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to backend (em produção usar domínio separado)
    location /auth/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /library/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /playlists/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /actions/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 13. Comandos Úteis

```bash
# Instalar deps
npm ci

# Dev server
npm run dev

# Build produção
npm run build

# Preview build
npm run preview

# Lint
npm run lint

# Type check
npm run typecheck

# Testes
npm run test

# Testes com coverage
npm run test:coverage
```

---

## 14. Package.json (Scripts Principais)

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

---

*Documento versionado. Última atualização: 2026-08-20*