// src/pages/Dashboard.tsx
import { useLibraryStats } from '@/hooks/useLibraryStats';
import { useLibraryIssues } from '@/hooks/useLibraryIssues';
import { StatCard } from '@/components/ui/StatCard';
import { GenreBars } from '@/components/charts/GenreBars';
import { DecadeBars } from '@/components/charts/DecadeBars';
import { Link } from 'react-router';
import { AlertTriangle, Clock, Music, Users, TrendingUp } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';
import { formatNumber } from '@/utils/format';

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

function cn(...inputs: (string | undefined | null | false | Record<string, boolean>)[]) {
  return inputs.filter(Boolean).join(' ');
}

export function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useLibraryStats();
  const { data: issues, isLoading: issuesLoading } = useLibraryIssues();
  
  if (statsLoading || issuesLoading) {
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
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-[var(--text-primary)]">
            Olá, Eduardo 👋
          </h1>
          <p className="text-[var(--text-muted)] mt-1">
            Visão geral da sua biblioteca
          </p>
        </div>
      </div>
      
      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          value={formatNumber(stats?.total_tracks ?? 0)}
          label="músicas"
        />
        <StatCard
          value={formatNumber(stats?.total_artists ?? 0)}
          label="artistas"
        />
        <StatCard
          value={`${stats?.total_hours ?? 0}h`}
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