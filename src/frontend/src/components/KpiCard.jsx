export default function KpiCard({ label, value, tone = "neutral", icon }) {
  return (
    <div className={`kpi-card kpi-${tone}`} role="group" aria-label={label}>
      {icon && (
        <span className="kpi-icon" aria-hidden="true">
          {icon}
        </span>
      )}
      <div className="kpi-body">
        <div className="kpi-value">{value}</div>
        <div className="kpi-label">{label}</div>
      </div>
    </div>
  );
}
