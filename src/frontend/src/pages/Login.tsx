// src/pages/Login.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Music } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { apiClient } from '@/api/client';

export function Login() {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Se já autenticado, redirect para dashboard
    apiClient.get('/auth/me').then(() => navigate('/')).catch(() => {});
  }, [navigate]);
  
  const handleLogin = () => {
    window.location.href = '/auth/login';
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg-base)] px-4">
      <div className="w-full max-w-md text-center">
        <div className="mb-10">
          <Music className="h-16 w-16 mx-auto text-[var(--accent)]" aria-hidden="true" />
        </div>
        <h1 className="font-display text-4xl font-bold text-[var(--text-primary)] mb-3">
          Meu Spotify
        </h1>
        <p className="text-[var(--text-muted)] mb-10">
          Seu Spotify, do seu jeito.
        </p>
        <Button onClick={handleLogin} size="lg" className="w-full">
          Entrar com Spotify
        </Button>
        <p className="mt-6 text-xs text-[var(--text-muted)]">
          Você será redirecionado para autorizar o acesso aos seus dados.
        </p>
      </div>
    </div>
  );
}