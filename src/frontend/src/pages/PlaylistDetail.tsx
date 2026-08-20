// src/pages/PlaylistDetail.tsx
import { useState, useMemo, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { usePlaylist } from '@/hooks/usePlaylist';
import { usePlaylistIssues } from '@/hooks/usePlaylistIssues';
import { TrackTable } from '@/components/playlists/TrackTable';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, AlertTriangle, ExternalLink } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';
import { formatDuration, formatRelativeDate } from '@/utils/format';
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
          <a
            href={`https://open.spotify.com/playlist/${playlist.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 text-[var(--text-muted)] hover:text-[var(--accent)] transition-colors"
            aria-label="Abrir no Spotify"
          >
            <ExternalLink className="h-5 w-5" />
          </a>
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
      <TrackTable tracks={sortedTracks} sortBy={sortBy} onSortChange={setSortBy} />
    </div>
  );
}