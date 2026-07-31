import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function CoutParPieceChart({ data }) {
  const chartData = (data || []).map((d) => ({ nom: d.piece__nom, cout: Math.round(d.cout) }));

  return (
    <div role="img" aria-label="Graphique du coût cumulé des interventions par pièce de rechange">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="nom" angle={-25} textAnchor="end" interval={0} height={60} />
          <YAxis />
          <Tooltip formatter={(value) => [`${value} €`, "Coût cumulé"]} />
          <Bar dataKey="cout" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
