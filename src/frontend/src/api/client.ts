// src/api/client.ts
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

class ApiClient {
  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (res.status === 401) {
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      throw new Error('Não autenticado');
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: `Erro ${res.status}` }));
      throw new Error(error.detail || `Erro ${res.status}`);
    }

    if (res.status === 204) {
      return undefined as T;
    }

    return res.json();
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'POST', body: JSON.stringify(body) });
  }

  put<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'PUT', body: JSON.stringify(body) });
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();