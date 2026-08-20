// src/hooks/usePlaylists.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { Playlist } from '@/types';

export function usePlaylists() {
  return useQuery<Playlist[]>({
    queryKey: ['playlists'],
    queryFn: () => apiClient.get<Playlist[]>('/playlists'),
    staleTime: 1000 * 60 * 5, // 5 min
  });
}