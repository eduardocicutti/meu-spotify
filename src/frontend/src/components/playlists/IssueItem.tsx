// src/components/playlists/IssueItem.tsx
import { cn } from '@/utils/cn';
import { formatRelativeDate } from '@/utils/format';

interface IssueItemProps {
  trackName: string;
  artistNames?: string[];
  detail: string;
  playlistId?: string;
  playlists?: string[];
}

export function IssueItem({ trackName, artistNames, detail, playlistId, playlists }: IssueItemProps) {
  return (
    <div className="flex items-center justify-between px-4 py-3 hover:bg-[var(--bg-elevated)] rounded-lg transition-colors">
      <div className="flex-1 min-w-0">
        <p className="font-medium text-[var(--text-primary)] truncate">{trackName}</p>
        {artistNames && artistNames.length > 0 && (
          <p className="text-sm text-[var(--text-muted)] truncate">{artistNames.join(', ')}</p>
        )}
        <p className="text-xs text-[var(--text-secondary)] mt-0.5">{detail}</p>
      </div>
      {playlistId && (
        <button
          className="ml-4 px-3 py-1.5 text-sm text-[var(--accent)] hover:bg-[var(--accent-bg)] rounded-lg transition-colors"
          onClick={() => window.open(`https://open.spotify.com/playlist/${playlistId}`, '_blank')}
        >
          Abrir no Spotify
        </button>
      )}
    </div>
  );
}