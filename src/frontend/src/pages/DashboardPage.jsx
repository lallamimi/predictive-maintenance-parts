import { useEffect, useState } from "react";
import { BarChart3, LogOut, Moon, Radio, Sun, TrendingDown, User, Wrench, AlertTriangle, Euro, Hammer } from "lucide-react";
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
          <span className="brand-icon" aria-hidden="true">
            <Wrench size={22} strokeWidth={2} />
          </span>
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
            {theme === "dark" ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}
          </button>
          <span className="user-badge">
            <User size={14} aria-hidden="true" /> <strong>{user?.username}</strong> · {user?.role}
          </span>
          <button type="button" className="btn-ghost" onClick={logout}>
            <LogOut size={16} aria-hidden="true" /> Déconnexion
          </button>
        </div>
      </header>

      <main id="main-content">
        {error && <p role="alert" className="error-message">{error}</p>}

        {kpi && (
          <section aria-label="Indicateurs clés de performance" className="kpi-row">
            <KpiCard icon={<Radio size={20} aria-hidden="true" />} label="Lectures capteur" value={kpi.nb_lectures_total} />
            <KpiCard
              icon={<AlertTriangle size={20} aria-hidden="true" />}
              label="Pannes détectées"
              value={kpi.nb_pannes}
              tone={kpi.taux_panne_pct > 5 ? "alert" : "ok"}
            />
            <KpiCard icon={<TrendingDown size={20} aria-hidden="true" />} label="Taux de panne" value={`${kpi.taux_panne_pct}%`} />
            <KpiCard icon={<Hammer size={20} aria-hidden="true" />} label="Interventions" value={kpi.nb_interventions} />
            <KpiCard icon={<Euro size={20} aria-hidden="true" />} label="Coût cumulé" value={`${Math.round(kpi.cout_total_interventions)} €`} />
          </section>
        )}

        {kpi && (
          <section aria-labelledby="chart-title" className="panel">
            <h2 id="chart-title"><BarChart3 size={19} aria-hidden="true" /> Coût cumulé par pièce</h2>
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
