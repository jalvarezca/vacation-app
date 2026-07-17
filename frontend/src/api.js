// Cliente del API. El token JWT se guarda en memoria + localStorage
// y se envía en Authorization: Bearer en cada llamada.
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let token = localStorage.getItem('token') || null;

export function setToken(t) {
  token = t;
  if (t) localStorage.setItem('token', t);
  else localStorage.removeItem('token');
}

export function getToken() {
  return token;
}

async function call(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch { /* sin cuerpo */ }
  if (!res.ok) {
    const msg = data?.detail
      ? (typeof data.detail === 'string' ? data.detail : data.detail[0]?.msg)
      : `Error ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  get: (p) => call('GET', p),
  post: (p, b) => call('POST', p, b),
  patch: (p, b) => call('PATCH', p, b),
};
