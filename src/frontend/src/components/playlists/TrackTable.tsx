// src/components/playlists/TrackTable.tsx
import { cn } from '@/utils/cn';
import { TrackRow } from './TrackRow';
import { Skeleton } from '@/ui/Skeleton';
import type { PlaylistTrack } from '@/types';

interface TrackTableProps {
  tracks: PlaylistTrack[];
  sortBy?: 'artist' | 'album' | 'duration';
  onSortChange?: (sortBy: 'artist' | 'album' | 'duration') => void;
  showPlaylistColumn?: boolean;
  isLoading?: boolean;
}

export function TrackTable({ 
  tracks, 
  sortBy, 
  onSortChange, 
  showPlaylistColumn = false,
  isLoading = false 
}: TrackTableProps) {
  if (isLoading) {
    return (
      <div className="card-base overflow-hidden">
        <div className="px-6 py-4 border-b border-[var(--border)]">
          <Skeleton className="h-8 w-1/4" />
        </div>
        {[...Array(8)].map((_, i) => (
          <div key={i} className="px-6 py-4 border-b border-[var(--border)]">
            <div className="grid grid-cols-[40px_1fr_200px_80px_100px] gap-4 items-center">
              <Skeleton className="h-5 w-8" />
              <div className="flex flex-col gap-1">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-32" />
              </div>
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-5 w-16" />
              <Skeleton className="h-4 w-24" />
            </div>
          </div>
        ))}
      </div>
    );
  }
  
  if (tracks.length === 0) {
    return (
      <div className="card-base p-12 text-center">
        <p className="text-[var(--text-muted)]">Nenhuma faixa encontrada.</p>
      </div>
    );
  }
  
  return (
    <div className="card-base overflow-hidden">
      {/* Table Header */}
      <div className="px-6 py-3 border-b border-[var(--border)] bg-[var(--bg-elevated)]">
        <div className="grid grid-cols-[40px_1fr_200px_80px_100px] gap-4 items-center text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
          <span>#</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onSortChange?.('artist')}
              className={cn('flex items-center gap-1 hover:text-[var(--text-primary)] transition-colors', sortBy === 'artist' && 'text-[var(--accent)]')}
              aria-pressed={sortBy === 'artist'}
            >
              Artista {sortBy === 'artist' ? '↑' : ''}
            </button>
          </div>
          <button
            onClick={() => onSortChange?.('album')}
            className={cn('flex items-center gap-1 hover:text-[var(--text-primary)] transition-colors', sortBy === 'album' && 'text-[var(--accent)]')}
            aria-pressed={sortBy === 'album'}
          >
            Álbum {sortBy === 'album' ? '↑' : ''}
          </button>
          <button
            onClick={() => onSortChange?.('duration')}
            className={cn('flex items-center gap-1 hover:text-[var(--text-primary)] transition-colors', sortBy === 'duration' && 'text-[var(--accent)]')}
            aria-pressed={sortBy === 'duration'}
          >
            Duração {sortBy === 'duration' ? '↑' : ''}
          </button>
          <span>Adicionada</span>
          {showPlaylistColumn && <span>Playlist</span>}
        </div>
      </div>
      
      {/* Table Body */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse" role="table">
          <tbody>
            {tracks.map((track, index) => (
              <TrackRow key={`${track.playlist_id}-${track.track_id}-${track.position}`} track={track} index={index} showPlaylist={showPlaylistColumn} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}