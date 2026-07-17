import { useEffect, useState } from 'react';
import { api } from '../api';
import { Badge, DayStrip, LeaveChip, fmt } from '../components/shared';

export default function Requests() {
  const [reqs, setReqs] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [f, setF] = useState({ leave_type_id: '', start_date: '', end_date: '', comments: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function load() {
    const [r, lt] = await Promise.all([
      api.get('/api/requests'),
      api.get('/api/catalogs/leave-types'),
    ]);
    setReqs(r);
    setLeaveTypes(lt);
  }
  useEffect(() => { load().catch((e) => setError(e.message)); }, []);

  async function create() {
    setError('');
    setBusy(true);
    try {
      await api.post('/api/requests', { ...f, leave_type_id: +f.leave_type_id });
      setShowForm(false);
      setF({ leave_type_id: '', start_date: '', end_date: '', comments: '' });
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function changeStatus(req, status) {
    let comments = null;
    if (status === 'canceled') {
      comments = prompt('Comentario de cancelación (obligatorio):');
      if (!comments) return;
    } else if (!confirm('¿Marcar como aprobada? Esto refleja la aprobación del proceso externo.')) {
      return;
    }
    try {
      await api.patch(`/api/requests/${req.id}/status`, { status, comments });
      await load();
    } catch (e) {
      alert(e.message);
    }
  }

  return (
    <div className="page">
      <h1>Mis solicitudes</h1>
      <p className="sub">Los días hábiles descuentan fines de semana y feriados de tu país.</p>

      <div className="card">
        {!showForm ? (
          <button className="primary" style={{ marginTop: 0 }} onClick={() => setShowForm(true)}>
            Nueva solicitud
          </button>
        ) : (
          <>
            <div className="grid2">
              <div>
                <label>Tipo de ausencia</label>
                <select value={f.leave_type_id} onChange={(e) => setF({ ...f, leave_type_id: e.target.value })}>
                  <option value="">Selecciona…</option>
                  {leaveTypes.map((lt) => (
                    <option key={lt.id} value={lt.id}>{lt.code} — {lt.name}</option>
                  ))}
                </select>
              </div>
              <div />
              <div>
                <label>Desde</label>
                <input type="date" value={f.start_date} onChange={(e) => setF({ ...f, start_date: e.target.value })} />
              </div>
              <div>
                <label>Hasta</label>
                <input type="date" value={f.end_date} onChange={(e) => setF({ ...f, end_date: e.target.value })} />
              </div>
            </div>
            <label>Comentarios</label>
            <textarea rows="2" value={f.comments} onChange={(e) => setF({ ...f, comments: e.target.value })} />
            {error && <div className="msg error">{error}</div>}
            <div style={{ display: 'flex', gap: 10 }}>
              <button className="primary" onClick={create}
                      disabled={busy || !f.leave_type_id || !f.start_date || !f.end_date}>
                {busy ? 'Creando…' : 'Crear en borrador'}
              </button>
              <button className="primary" style={{ background: '#fff', color: 'var(--ink-soft)', border: '1px solid var(--border)' }}
                      onClick={() => setShowForm(false)}>
                Cancelar
              </button>
            </div>
          </>
        )}
      </div>

      <div className="card">
        {reqs.length === 0 && <div className="empty">Aún no tienes solicitudes. Crea la primera arriba.</div>}
        {reqs.map((r) => (
          <div className="req-row" key={r.id}>
            <div>
              <div className="req-dates">{fmt(r.start_date)} → {fmt(r.end_date)}</div>
              <DayStrip start={r.start_date} end={r.end_date} color={r.leave_type.color} />
            </div>
            <div className="req-meta">
              <div className="type">
                <LeaveChip lt={r.leave_type} /> · {r.business_days} día{r.business_days !== 1 && 's'} hábil{r.business_days !== 1 && 'es'}
              </div>
              {r.comments && <div className="comment">{r.comments}</div>}
              {r.cancel_comments && <div className="comment">Cancelación: {r.cancel_comments}</div>}
            </div>
            <div className="req-actions">
              <Badge value={r.status} />
              {r.status === 'draft' && (
                <button className="ghost" onClick={() => changeStatus(r, 'approved')}>Marcar aprobada</button>
              )}
              {(r.status === 'draft' || r.status === 'approved') && (
                <button className="ghost danger" onClick={() => changeStatus(r, 'canceled')}>Cancelar</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
