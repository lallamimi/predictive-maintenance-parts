import { useEffect, useState } from "react";
import { dataApi } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";
import KpiCard from "../components/KpiCard";
import CoutParPieceChart from "../components/CoutParPieceChart";
import PredictFailureForm from "../components/PredictFailureForm";
import PredictDemandPanel from "../components/PredictDemandPanel";
import RecommendationPanel from "../components/RecommendationPanel";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [kpi, setKpi] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    dataApi.kpi().then(setKpi).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="dashboard">
      <header>
        <div className="header-title">
          <span className="brand-icon" aria-hidden="true">🔧</span>
          <h1>Maintenance Prédictive</h1>
        </div>
        <div className="header-actions">
          <button
            type="button"
            className="btn-icon theme-toggle"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Activer le thème clair" : "Activer le thème sombre"}
            title={theme === "dark" ? "Thème clair" : "Thème sombre"}
          >
            <span aria-hidden="true">{theme === "dark" ? "☀️" : "🌙"}</span>
          </button>
          <span className="user-badge">
            👤 <strong>{user?.username}</strong> · {user?.role}
          </span>
          <button type="button" className="btn-ghost" onClick={logout}>
            🚪 Déconnexion
          </button>
        </div>
      </header>

      <main id="main-content">
        {error && <p role="alert" className="error-message">{error}</p>}

        {kpi && (
          <section aria-label="Indicateurs clés de performance" className="kpi-row">
            <KpiCard icon="📡" label="Lectures capteur" value={kpi.nb_lectures_total} />
            <KpiCard
              icon="⚠️"
              label="Pannes détectées"
              value={kpi.nb_pannes}
              tone={kpi.taux_panne_pct > 5 ? "alert" : "ok"}
            />
            <KpiCard icon="📉" label="Taux de panne" value={`${kpi.taux_panne_pct}%`} />
            <KpiCard icon="🛠️" label="Interventions" value={kpi.nb_interventions} />
            <KpiCard icon="💶" label="Coût cumulé" value={`${Math.round(kpi.cout_total_interventions)} €`} />
          </section>
        )}

        {kpi && (
          <section aria-labelledby="chart-title" className="panel">
            <h2 id="chart-title"><span aria-hidden="true">📊</span> Coût cumulé par pièce</h2>
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
