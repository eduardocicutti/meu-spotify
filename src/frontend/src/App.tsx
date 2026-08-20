// src/App.tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { PageShell } from '@/components/layout/PageShell';
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
import { Playlists } from '@/pages/Playlists';
import { PlaylistDetail } from '@/pages/PlaylistDetail';
import { Issues } from '@/pages/Issues';

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-[var(--accent)] border-t-transparent" />
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-[var(--accent)] border-t-transparent" />
      </div>
    );
  }
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={
        <PublicRoute>
          <Login />
        </PublicRoute>
      } />
      
      {/* Protected routes */}
      <Route element={
        <AuthGuard>
          <PageShell />
        </AuthGuard>
      }>
        <Route path="/" element={<Dashboard />} />
        <Route path="/playlists" element={<Playlists />} />
        <Route path="/playlists/:id" element={<PlaylistDetail />} />
        <Route path="/issues" element={<Issues />} />
      </Route>
      
      {/* Redirect root to login if not authenticated, or dashboard if authenticated */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}