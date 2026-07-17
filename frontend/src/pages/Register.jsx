import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Register({ goLogin }) {
  const [cat, setCat] = useState({ countries: [], cities: [], skills: [], projects: [] });
  const [f, setF] = useState({
    email: '', password: '', first_name: '', last_name: '', employee_code: '',
    country_id: '', city_id: '', skill_id: '', project_id: '', gender: '',
  });
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get('/api/catalogs/countries'),
      api.get('/api/catalogs/skills'),
      api.get('/api/catalogs/projects'),
    ]).then(([countries, skills, projects]) =>
      setCat((c) => ({ ...c, countries, skills, projects }))
    ).catch((e) => setError(e.message));
  }, []);

  // Ciudades dependientes del país seleccionado (lista precargada, req. 4)
  useEffect(() => {
    if (!f.country_id) return;
    api.get(`/api/catalogs/cities?country_id=${f.country_id}`)
      .then((cities) => setCat((c) => ({ ...c, cities })));
  }, [f.country_id]);

  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit() {
    setError('');
    setBusy(true);
    try {
      await api.post('/api/auth/register', {
        ...f,
        country_id: +f.country_id,
        city_id: +f.city_id,
        skill_id: f.skill_id ? +f.skill_id : null,
        project_id: f.project_id ? +f.project_id : null,
        gender: f.gender || null,
      });
      setDone(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div className="auth-wrap">
        <div className="card auth-card">
          <div className="logo">Registro enviado</div>
          <p>Te llegará un correo de confirmación. Podrás entrar cuando un
             administrador apruebe tu acceso.</p>
          <button className="primary" onClick={goLogin}>Volver al inicio de sesión</button>
        </div>
      </div>
    );
  }

  const ready = f.email && f.password && f.first_name && f.last_name &&
                f.employee_code && f.country_id && f.city_id;

  return (
    <div className="auth-wrap">
      <div className="card auth-card wide">
        <div className="logo">Crear cuenta <span>· Vacation Planner</span></div>
        <p className="sub">Solo correos @dxc.com. El acceso requiere aprobación de un administrador.</p>

        <div className="grid2">
          <div>
            <label>Nombre</label>
            <input value={f.first_name} onChange={set('first_name')} />
          </div>
          <div>
            <label>Apellido</label>
            <input value={f.last_name} onChange={set('last_name')} />
          </div>
          <div>
            <label>Correo corporativo</label>
            <input type="email" placeholder="nombre.apellido@dxc.com"
                   value={f.email} onChange={set('email')} />
          </div>
          <div>
            <label>Contraseña (mínimo 8 caracteres)</label>
            <input type="password" value={f.password} onChange={set('password')} />
          </div>
          <div>
            <label>Código de empleado DXC</label>
            <input value={f.employee_code} onChange={set('employee_code')} />
          </div>
          <div>
            <label>Género (opcional)</label>
            <select value={f.gender} onChange={set('gender')}>
              <option value="">Prefiero no decirlo</option>
              <option value="F">Femenino</option>
              <option value="M">Masculino</option>
              <option value="X">Otro</option>
            </select>
          </div>
          <div>
            <label>País</label>
            <select value={f.country_id} onChange={set('country_id')}>
              <option value="">Selecciona…</option>
              {cat.countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label>Ciudad</label>
            <select value={f.city_id} onChange={set('city_id')} disabled={!f.country_id}>
              <option value="">Selecciona…</option>
              {cat.cities.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label>Skill</label>
            <select value={f.skill_id} onChange={set('skill_id')}>
              <option value="">Selecciona…</option>
              {cat.skills.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>
          <div>
            <label>Proyecto</label>
            <select value={f.project_id} onChange={set('project_id')}>
              <option value="">Selecciona…</option>
              {cat.projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
        </div>

        {error && <div className="msg error">{error}</div>}

        <button className="primary" onClick={submit} disabled={busy || !ready}>
          {busy ? 'Enviando…' : 'Registrarme'}
        </button>
        <div className="auth-switch">
          ¿Ya tienes cuenta? <a onClick={goLogin}>Inicia sesión</a>
        </div>
      </div>
    </div>
  );
}
