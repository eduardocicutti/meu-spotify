// src/hooks/useLibraryIssues.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { LibraryIssues } from '@/types';

export function useLibraryIssues() {
  return useQuery<LibraryIssues>({
    queryKey: ['library', 'issues'],
    queryFn: () => apiClient.get<LibraryIssues>('/library/issues'),
    staleTime: 1000 * 60 * 5, // 5 min
  });
}