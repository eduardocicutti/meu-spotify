// src/hooks/useAuth.ts
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { User } from '@/types';

export function useAuth() {
  const { data: user, isLoading, error, refetch } = useQuery<User>({
    queryKey: ['auth', 'me'],
    queryFn: () => apiClient.get<User>('/auth/me'),
    staleTime: 1000 * 60 * 30, // 30 min
    retry: false,
  });
  
  const isAuthenticated = !!user && !error;
  
  return { user, isAuthenticated, isLoading, error, refetch };
}