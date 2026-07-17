import { useState } from 'react';
import { api, setToken } from '../api';

export default function Login({ onLogin, goRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit() {
    setError('');
    setBusy(true);
    try {
      const data = await api.post('/api/auth/login', { email, password });
      setToken(data.access_token);
      onLogin(data.user);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="card auth-card">
        <div className="logo">Vacation Planner <span>· DXC</span></div>
        <p className="sub">Inicia sesión con tu correo corporativo</p>

        <label>Correo</label>
        <input type="email" value={email} placeholder="nombre.apellido@dxc.com"
               onChange={(e) => setEmail(e.target.value)} />

        <label>Contraseña</label>
        <input type="password" value={password}
               onChange={(e) => setPassword(e.target.value)}
               onKeyDown={(e) => e.key === 'Enter' && submit()} />

        {error && <div className="msg error">{error}</div>}

        <button className="primary" onClick={submit} disabled={busy || !email || !password}>
          {busy ? 'Entrando…' : 'Entrar'}
        </button>

        <div className="auth-switch">
          ¿Primera vez? <a onClick={goRegister}>Regístrate</a> — tu acceso lo aprueba un administrador.
        </div>
      </div>
    </div>
  );
}
