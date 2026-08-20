// src/components/layout/Sidebar.tsx
import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/utils/cn';
import { Home, Music, AlertTriangle, LogOut, LayoutDashboard } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Início', icon: LayoutDashboard },
  { path: '/playlists', label: 'Playlists', icon: Music },
  { path: '/issues', label: 'Arrume seu Spotify', icon: AlertTriangle },
];

export function Sidebar() {
  const location = useLocation();
  
  return (
    <aside className="w-64 bg-[var(--bg-surface)] border-r border-[var(--border)] flex flex-col h-screen fixed left-0 top-0 z-40">
      {/* Logo */}
      <div className="p-6 border-b border-[var(--border)]">
        <h1 className="font-display text-xl font-bold text-[var(--accent)] flex items-center gap-2">
          <span className="text-2xl">🎧</span>
          Meu Spotify
        </h1>
        <p className="text-xs text-[var(--text-muted)] mt-1">Seu Spotify, do seu jeito.</p>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname === path || (path !== '/' && location.pathname.startsWith(path));
          return (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) => cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-[var(--accent-bg)] text-[var(--accent)]'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)]'
              )}
            >
              <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
              {label}
            </NavLink>
          );
        })}
      </nav>
      
      {/* User section */}
      <div className="p-4 border-t border-[var(--border)]">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center text-[var(--text-inverse)] font-bold text-sm">
            E
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[var(--text-primary)] truncate">Eduardo</p>
            <p className="text-xs text-[var(--text-muted)] truncate">eduardo@email.com</p>
          </div>
        </div>
        <button className="w-full mt-3 flex items-center justify-center gap-2 px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-elevated)] rounded-lg transition-colors">
          <LogOut className="h-4 w-4" aria-hidden="true" />
          Sair
        </button>
      </div>
    </aside>
  );
}