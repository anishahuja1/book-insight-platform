const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = {
  books: {
    list: async (params?: Record<string, string>) => {
      const qs = params ? `?${new URLSearchParams(params)}` : '';
      const r = await fetch(`${API_BASE}/books/${qs}`);
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
    detail: async (id: string | number) => {
      const r = await fetch(`${API_BASE}/books/${id}/`);
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
    recommendations: async (id: string | number) => {
      const r = await fetch(`${API_BASE}/books/${id}/recommendations/`);
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
    scrape: async (url: string, pages: number) => {
      const r = await fetch(`${API_BASE}/books/scrape/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, pages })
      });
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
    genres: async () => {
      const r = await fetch(`${API_BASE}/books/genres/`);
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
  },
  qa: {
    ask: async (question: string, sessionId?: string) => {
      const r = await fetch(`${API_BASE}/qa/ask/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId })
      });
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
    history: async () => {
      const r = await fetch(`${API_BASE}/chat/history/`);
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
  },
  tasks: {
    status: async (taskId: string) => {
      const r = await fetch(`${API_BASE}/tasks/${taskId}/status/`);
      if (!r.ok) throw new Error('API Error');
      return r.json();
    },
  }
};
