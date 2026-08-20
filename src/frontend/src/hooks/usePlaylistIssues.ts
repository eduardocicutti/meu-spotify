// src/hooks/usePlaylistIssues.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { PlaylistIssues } from '@/types';

export function usePlaylistIssues(playlistId: string) {
  return useQuery<PlaylistIssues>({
    queryKey: ['playlists', playlistId, 'issues'],
    queryFn: () => apiClient.get<PlaylistIssues>(`/playlists/${playlistId}/issues`),
    enabled: !!playlistId,
    staleTime: 1000 * 60 * 5, // 5 min
  });
}