// src/hooks/usePlaylist.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { PlaylistDetail } from '@/types';

export function usePlaylist(id: string) {
  return useQuery<PlaylistDetail>({
    queryKey: ['playlists', id],
    queryFn: () => apiClient.get<PlaylistDetail>(`/playlists/${id}`),
    enabled: !!id,
    staleTime: 1000 * 60 * 10, // 10 min
  });
}