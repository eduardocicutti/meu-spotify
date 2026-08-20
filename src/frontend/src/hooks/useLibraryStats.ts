// src/hooks/useLibraryStats.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { LibraryStats } from '@/types';

export function useLibraryStats() {
  return useQuery<LibraryStats>({
    queryKey: ['library', 'stats'],
    queryFn: () => apiClient.get<LibraryStats>('/library/stats'),
    staleTime: 1000 * 60 * 15, // 15 min
  });
}