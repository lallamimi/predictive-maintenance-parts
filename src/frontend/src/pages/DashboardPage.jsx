import { useEffect, useState } from "react";
import { dataApi } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import KpiCard from "../components/KpiCard";
import CoutParPieceChart from "../components/CoutParPieceChart";
import PredictFailureForm from "../components/PredictFailureForm";
import PredictDemandPanel from "../components/PredictDemandPanel";
import RecommendationPanel from "../components/RecommendationPanel";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [kpi, setKpi] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    dataApi.kpi().then(setKpi).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="dashboard">
      <header>
        <h1>Tableau de bord — Maintenance prédictive</h1>
        <div className="header-actions">
          <span>{user?.username} ({user?.role})</span>
          <button type="button" onClick={logout}>Déconnexion</button>
        </div>
      </header>

      <main id="main-content">
        {error && <p role="alert" className="error-message">{error}</p>}

        {kpi && (
          <section aria-label="Indicateurs clés de performance" className="kpi-row">
            <KpiCard label="Lectures capteur" value={kpi.nb_lectures_total} />
            <KpiCard label="Pannes détectées" value={kpi.nb_pannes} tone={kpi.taux_panne_pct > 5 ? "alert" : "ok"} />
            <KpiCard label="Taux de panne" value={`${kpi.taux_panne_pct}%`} />
            <KpiCard label="Interventions" value={kpi.nb_interventions} />
            <KpiCard label="Coût cumulé" value={`${Math.round(kpi.cout_total_interventions)} €`} />
          </section>
        )}

        {kpi && (
          <section aria-labelledby="chart-title" className="panel">
            <h2 id="chart-title">Coût cumulé par pièce</h2>
            <CoutParPieceChart data={kpi.top_pieces_par_cout} />
          </section>
        )}

        <div className="predict-grid">
          <PredictFailureForm />
          <PredictDemandPanel />
        </div>

        <RecommendationPanel />
      </main>
    </div>
  );
}
