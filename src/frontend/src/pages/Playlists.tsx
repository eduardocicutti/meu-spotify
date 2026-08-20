// src/pages/Playlists.tsx
import { useState, useMemo } from 'react';
import { usePlaylists } from '@/hooks/usePlaylists';
import { PlaylistCard } from '@/components/playlists/PlaylistCard';
import { Skeleton } from '@/components/ui/Skeleton';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Search, Filter } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  className?: string;
}

function Select({ value, onValueChange, options, className }: SelectProps) {
  return (
    <select
      value={value}
      onChange={e => onValueChange(e.target.value)}
      className={cn(
        'w-full px-3 py-2 text-sm bg-[var(--bg-elevated)] border border-[var(--border)] text-[var(--text-primary)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent)]',
        className
      )}
    >
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

function Input({ className, ...props }: InputProps) {
  return (
    <input
      className={cn(
        'w-full px-3 py-2 text-sm bg-[var(--bg-elevated)] border border-[var(--border)] text-[var(--text-primary)] placeholder-[var(--text-muted)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent)]',
        className
      )}
      {...props}
    />
  );
}

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