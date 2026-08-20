// src/components/layout/PageShell.tsx
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function PageShell() {
  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <Sidebar />
      <main className="ml-64 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}