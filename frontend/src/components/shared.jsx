// Componentes compartidos.

export function Badge({ value }) {
  return <span className={`badge ${value}`}>{translate(value)}</span>;
}

const ES = {
  draft: 'borrador', approved: 'aprobada', canceled: 'cancelada',
  pending: 'pendiente', active: 'activo', disabled: 'deshabilitado', rejected: 'rechazado',
};
function translate(v) { return ES[v] || v; }

/* Firma visual: una celda por día del rango, coloreada con el color del
   tipo de ausencia (tab Legend del Excel). Fines de semana en gris. */
export function DayStrip({ start, end, color }) {
  const days = [];
  const d = new Date(start + 'T00:00:00');
  const last = new Date(end + 'T00:00:00');
  let guard = 0;
  while (d <= last && guard < 40) {
    const weekend = d.getDay() === 0 || d.getDay() === 6;
    days.push(
      <span
        key={d.toISOString()}
        className={`day ${weekend ? 'off' : ''}`}
        style={weekend ? undefined : { background: color }}
        title={d.toLocaleDateString('es', { weekday: 'short', day: 'numeric', month: 'short' })}
      />
    );
    d.setDate(d.getDate() + 1);
    guard++;
  }
  return <div className="strip">{days}{guard >= 40 && <span className="mono">…</span>}</div>;
}

export function LeaveChip({ lt }) {
  return (
    <span className="chip" title={lt.name}>
      <span className="dot" style={{ background: lt.color }} />
      {lt.code}
    </span>
  );
}

export function fmt(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('es', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}
