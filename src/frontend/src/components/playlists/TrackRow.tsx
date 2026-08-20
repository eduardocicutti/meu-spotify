// src/components/playlists/TrackRow.tsx
import { cn } from '@/utils/cn';
import { formatDuration } from '@/utils/format';
import type { PlaylistTrack } from '@/types';

interface TrackRowProps {
  track: PlaylistTrack;
  index: number;
  showPlaylist?: boolean;
  playlistName?: string;
}

export function TrackRow({ track, index, showPlaylist, playlistName }: TrackRowProps) {
  const isUnavailable = !track.is_available;
  
  return (
    <tr className={cn('border-b border-[var(--border)] hover:bg-[var(--bg-elevated)] transition-colors', isUnavailable && 'opacity-50')}>
      <td className="px-4 py-3 text-[var(--text-muted)] text-sm font-mono w-12">
        {index + 1}
      </td>
      <td className="px-4 py-3">
        <div className="font-medium text-[var(--text-primary)] truncate max-w-xs">
          {track.track_name || 'Faixa indisponível'}
        </div>
        {track.artist_names.length > 0 && (
          <div className="text-sm text-[var(--text-muted)] truncate max-w-xs">
            {track.artist_names.join(', ')}
          </div>
        )}
      </td>
      <td className="px-4 py-3 hidden md:table-cell text-sm text-[var(--text-secondary)] truncate max-w-xs">
        {track.album_name || '—'}
      </td>
      <td className="px-4 py-3 text-sm text-[var(--text-muted)] font-mono w-20 text-right">
        {formatDuration(track.duration_ms)}
      </td>
      <td className="px-4 py-3 hidden lg:table-cell text-xs text-[var(--text-muted)]">
        {track.added_at ? formatRelativeDate(track.added_at) : '—'}
      </td>
      {showPlaylist && playlistName && (
        <td className="px-4 py-3 text-sm text-[var(--text-secondary)] truncate max-w-xs">
          {playlistName}
        </td>
      )}
      {isUnavailable && (
        <td className="px-4 py-3 text-xs">
          <span className="px-2 py-0.5 bg-[var(--danger-bg)] text-[var(--danger)] rounded-full">
            Indisponível
          </span>
        </td>
      )}
    </tr>
  );
}

function formatRelativeDate(dateStr: string): string {
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