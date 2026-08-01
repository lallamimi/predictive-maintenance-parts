import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function CoutParPieceChart({ data }) {
  const chartData = (data || []).map((d) => ({ nom: d.piece__nom, cout: Math.round(d.cout) }));

  return (
    <div role="img" aria-label="Graphique du coût cumulé des interventions par pièce de rechange">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 40 }}>
          <defs>
            <linearGradient id="coutGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4f46e5" />
              <stop offset="100%" stopColor="#22d3ee" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.25)" />
          <XAxis dataKey="nom" angle={-25} textAnchor="end" interval={0} height={60} stroke="rgba(148, 163, 184, 0.6)" />
          <YAxis stroke="rgba(148, 163, 184, 0.6)" />
          <Tooltip
            formatter={(value) => [`${value} €`, "Coût cumulé"]}
            contentStyle={{
              background: "var(--surface-solid)",
              border: "1px solid var(--border)",
              borderRadius: 12,
              color: "var(--text)",
            }}
          />
          <Bar dataKey="cout" fill="url(#coutGradient)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
