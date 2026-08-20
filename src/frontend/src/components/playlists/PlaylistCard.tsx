// src/components/playlists/PlaylistCard.tsx
import { cn } from '@/utils/cn';
import { formatRelativeDate } from '@/utils/format';
import { Badge } from '@/ui/Badge';
import type { Playlist } from '@/types';

interface PlaylistCardProps {
  playlist: Playlist;
}

export function PlaylistCard({ playlist }: PlaylistCardProps) {
  const hasIssues = playlist.has_issues;
  const issueCount = playlist.issues_count;
  
  return (
    <article className="card-base p-4 hover:border-[var(--accent)] transition-colors group">
      <div className="flex items-start gap-3">
        {/* Cover image */}
        <div className="relative w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-[var(--bg-elevated)]">
          {playlist.images?.[0]?.url ? (
            <img
              src={playlist.images[0].url}
              alt=""
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-3xl">🎵</div>
          )}
        </div>
        
        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-[var(--text-primary)] truncate">{playlist.name}</h3>
          <div className="flex flex-wrap items-center gap-2 mt-1.5 text-xs text-[var(--text-muted)]">
            <span>{playlist.track_count} faixas</span>
            {playlist.last_modified && (
              <>
                <span>•</span>
                <span>Atualizada {formatRelativeDate(playlist.last_modified)}</span>
              </>
            )}
          </div>
          
          {/* Issues badge */}
          {hasIssues && issueCount > 0 && (
            <Badge variant="warning" size="sm" className="mt-2">
              ⚠ {issueCount} problema{issueCount !== 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      </div>
    </article>
  );
}