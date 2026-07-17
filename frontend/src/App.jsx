import { useEffect, useState } from 'react';
import { api, getToken, setToken } from './api';
import Login from './pages/Login';
import Register from './pages/Register';
import Requests from './pages/Requests';
import Admin from './pages/Admin';

export default function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('login');       // login | register | requests | admin
  const [checking, setChecking] = useState(!!getToken());

  // Si hay token guardado, recuperar la sesión
  useEffect(() => {
    if (!getToken()) return;
    api.get('/api/auth/me')
      .then((u) => { setUser(u); setView('requests'); })
      .catch(() => setToken(null))
      .finally(() => setChecking(false));
  }, []);

  function logout() {
    setToken(null);
    setUser(null);
    setView('login');
  }

  if (checking) return null;
  if (!user) {
    return view === 'register'
      ? <Register goLogin={() => setView('login')} />
      : <Login onLogin={(u) => { setUser(u); setView('requests'); }}
               goRegister={() => setView('register')} />;
  }

  return (
    <>
      <header className="topbar">
        <div className="brand">Vacation Planner <span>· DXC</span></div>
        <nav>
          <button className={`link ${view === 'requests' ? 'active' : ''}`}
                  onClick={() => setView('requests')}>Mis solicitudes</button>
          {user.role === 'admin' && (
            <button className={`link ${view === 'admin' ? 'active' : ''}`}
                    onClick={() => setView('admin')}>Administración</button>
          )}
        </nav>
        <div className="who">
          {user.first_name} {user.last_name}
          <button className="link" onClick={logout}>Salir</button>
        </div>
      </header>
      {view === 'requests' && <Requests />}
      {view === 'admin' && user.role === 'admin' && <Admin />}
    </>
  );
}
