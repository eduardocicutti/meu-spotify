// src/pages/Issues.tsx
import { useLibraryIssues } from '@/hooks/useLibraryIssues';
import { Accordion } from '@/components/ui/Accordion';
import { IssueItem } from '@/components/playlists/IssueItem';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { Music, AlertTriangle, Clock, TrendingUp } from 'lucide-react';
import { cn } from '@/utils/cn';

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
        <EmptyState
          title="Tudo em ordem"
          description="Nenhum problema detectado na sua biblioteca."
          icon="✨"
        />
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