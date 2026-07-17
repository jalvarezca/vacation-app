import { useEffect, useState } from 'react';
import { api } from '../api';
import { Badge, LeaveChip, fmt } from '../components/shared';

export default function Admin() {
  const [tab, setTab] = useState('requests');
  return (
    <div className="page">
      <h1>Administración</h1>
      <p className="sub">Solicitudes de todo el equipo, accesos y bitácora.</p>
      <div className="tabs">
        <button className={tab === 'requests' ? 'active' : ''} onClick={() => setTab('requests')}>Solicitudes</button>
        <button className={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}>Usuarios</button>
        <button className={tab === 'report' ? 'active' : ''} onClick={() => setTab('report')}>Reporte de días</button>
        <button className={tab === 'audit' ? 'active' : ''} onClick={() => setTab('audit')}>Bitácora</button>
      </div>
      {tab === 'requests' && <AdminRequests />}
      {tab === 'users' && <AdminUsers />}
      {tab === 'report' && <AdminReport />}
      {tab === 'audit' && <AdminAudit />}
    </div>
  );
}

/* ---- Solicitudes con filtros (req. Admin 1-2) ---- */
function AdminRequests() {
  const [rows, setRows] = useState([]);
  const [cats, setCats] = useState({ countries: [], cities: [] });
  const [flt, setFlt] = useState({ country_id: '', city_id: '', status: '', first_name: '', last_name: '' });

  useEffect(() => {
    Promise.all([api.get('/api/catalogs/countries'), api.get('/api/catalogs/cities')])
      .then(([countries, cities]) => setCats({ countries, cities }));
  }, []);

  useEffect(() => {
    const q = Object.entries(flt).filter(([, v]) => v)
      .map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join('&');
    api.get('/api/admin/requests' + (q ? `?${q}` : '')).then(setRows).catch(() => {});
  }, [flt]);

  const set = (k) => (e) => setFlt({ ...flt, [k]: e.target.value });

  return (
    <div className="card">
      <div className="filters">
        <select value={flt.country_id} onChange={set('country_id')}>
          <option value="">País: todos</option>
          {cats.countries.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={flt.city_id} onChange={set('city_id')}>
          <option value="">Ciudad: todas</option>
          {cats.cities.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={flt.status} onChange={set('status')}>
          <option value="">Estado: todos</option>
          <option value="draft">Borrador</option>
          <option value="approved">Aprobada</option>
          <option value="canceled">Cancelada</option>
        </select>
        <input placeholder="Nombre" value={flt.first_name} onChange={set('first_name')} />
        <input placeholder="Apellido" value={flt.last_name} onChange={set('last_name')} />
      </div>
      <table>
        <thead>
          <tr><th>Empleado</th><th>Tipo</th><th>Fechas</th><th>Días</th><th>Estado</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.user.first_name} {r.user.last_name}<br />
                  <span className="mono">{r.user.employee_code}</span></td>
              <td><LeaveChip lt={r.leave_type} /></td>
              <td className="mono">{fmt(r.start_date)} → {fmt(r.end_date)}</td>
              <td>{r.business_days}</td>
              <td><Badge value={r.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <div className="empty">Sin resultados con estos filtros.</div>}
    </div>
  );
}

/* ---- Usuarios: aprobar/rechazar, habilitar/deshabilitar (req. Admin 4-5) ---- */
function AdminUsers() {
  const [users, setUsers] = useState([]);
  const load = () => api.get('/api/admin/users').then(setUsers);
  useEffect(() => { load(); }, []);

  async function act(u, action) {
    try {
      if (action === 'approve') await api.post(`/api/admin/users/${u.id}/approve`);
      if (action === 'reject') await api.post(`/api/admin/users/${u.id}/reject`);
      if (action === 'disable') await api.patch(`/api/admin/users/${u.id}`, { status: 'disabled' });
      if (action === 'enable') await api.patch(`/api/admin/users/${u.id}`, { status: 'active' });
      await load();
    } catch (e) {
      alert(e.message);
    }
  }

  return (
    <div className="card">
      <table>
        <thead>
          <tr><th>Empleado</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.first_name} {u.last_name}<br />
                  <span className="mono">{u.employee_code}</span></td>
              <td>{u.email}</td>
              <td>{u.role === 'admin' ? 'Administrador' : 'Empleado'}</td>
              <td><Badge value={u.status} /></td>
              <td>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {u.status === 'pending' && (
                    <>
                      <button className="ghost" onClick={() => act(u, 'approve')}>Aprobar</button>
                      <button className="ghost danger" onClick={() => act(u, 'reject')}>Rechazar</button>
                    </>
                  )}
                  {u.status === 'active' && u.role !== 'admin' && (
                    <button className="ghost danger" onClick={() => act(u, 'disable')}>Deshabilitar</button>
                  )}
                  {(u.status === 'disabled' || u.status === 'rejected') && (
                    <button className="ghost" onClick={() => act(u, 'enable')}>Habilitar</button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---- Reporte de días por rango (req. Admin 3) ---- */
function AdminReport() {
  const [range, setRange] = useState({ start: '2026-01-01', end: '2026-12-31' });
  const [report, setReport] = useState(null);

  async function run() {
    const r = await api.get(`/api/admin/reports/days?start_date=${range.start}&end_date=${range.end}`);
    setReport(r);
  }
  useEffect(() => { run().catch(() => {}); }, []);

  return (
    <div className="card">
      <div className="filters">
        <input type="date" value={range.start} onChange={(e) => setRange({ ...range, start: e.target.value })} />
        <input type="date" value={range.end} onChange={(e) => setRange({ ...range, end: e.target.value })} />
        <button className="ghost" onClick={run}>Calcular</button>
      </div>
      {report && (
        <div>
          <div className="report-num">{report.total_business_days}</div>
          <div className="sub">
            días hábiles solicitados en {report.total_requests} solicitud{report.total_requests !== 1 && 'es'} activas
            (borradores y aprobadas) entre {fmt(report.start_date)} y {fmt(report.end_date)}.
          </div>
        </div>
      )}
    </div>
  );
}

/* ---- Bitácora global (req. Admin 6) ---- */
function AdminAudit() {
  const [rows, setRows] = useState([]);
  useEffect(() => { api.get('/api/admin/audit').then(setRows); }, []);
  return (
    <div className="card">
      <table>
        <thead>
          <tr><th>Fecha y hora</th><th>Acción</th><th>Entidad</th><th>Detalle</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td className="mono">{new Date(r.timestamp + 'Z').toLocaleString('es')}</td>
              <td className="mono">{r.action}</td>
              <td className="mono">{r.entity}#{r.entity_id}</td>
              <td>{r.detail || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <div className="empty">Sin movimientos registrados.</div>}
    </div>
  );
}
