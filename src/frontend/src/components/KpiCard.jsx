export default function KpiCard({ label, value, tone = "neutral" }) {
  return (
    <div className={`kpi-card kpi-${tone}`} role="group" aria-label={label}>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
