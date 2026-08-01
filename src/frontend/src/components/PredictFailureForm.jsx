import { useState } from "react";
import { AlertOctagon, AlertTriangle, CheckCircle2, Search } from "lucide-react";
import { mlApi } from "../api/client";

const DEFAULTS = {
  temperature_air_k: 300,
  temperature_process_k: 310,
  vitesse_rotation_rpm: 1500,
  couple_nm: 40,
  usure_outil_min: 100,
  type_produit: "M",
};

const RISK_LABELS = { eleve: "Élevé", moyen: "Moyen", faible: "Faible" };
const RISK_ICONS = { eleve: AlertOctagon, moyen: AlertTriangle, faible: CheckCircle2 };

export default function PredictFailureForm() {
  const [form, setForm] = useState(DEFAULTS);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const RiskIcon = result ? RISK_ICONS[result.niveau_risque] : null;

  function updateField(name, value) {
    setForm((prev) => ({ ...prev, [name]: name === "type_produit" ? value : Number(value) }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await mlApi.predictFailure(form);
      setResult(data);
    } catch (err) {
      setError(err.message || "Erreur lors de la prédiction.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section aria-labelledby="predict-failure-title" className="panel">
      <h2 id="predict-failure-title"><Search size={19} aria-hidden="true" /> Prédiction de panne</h2>
      <form onSubmit={handleSubmit} className="predict-form">
        <label htmlFor="temp_air">Température air (K)</label>
        <input
          id="temp_air"
          type="number"
          value={form.temperature_air_k}
          onChange={(e) => updateField("temperature_air_k", e.target.value)}
        />

        <label htmlFor="temp_process">Température process (K)</label>
        <input
          id="temp_process"
          type="number"
          value={form.temperature_process_k}
          onChange={(e) => updateField("temperature_process_k", e.target.value)}
        />

        <label htmlFor="vitesse">Vitesse de rotation (rpm)</label>
        <input
          id="vitesse"
          type="number"
          value={form.vitesse_rotation_rpm}
          onChange={(e) => updateField("vitesse_rotation_rpm", e.target.value)}
        />

        <label htmlFor="couple">Couple (Nm)</label>
        <input id="couple" type="number" value={form.couple_nm} onChange={(e) => updateField("couple_nm", e.target.value)} />

        <label htmlFor="usure">Usure outil (min)</label>
        <input
          id="usure"
          type="number"
          value={form.usure_outil_min}
          onChange={(e) => updateField("usure_outil_min", e.target.value)}
        />

        <label htmlFor="type_produit">Type de produit</label>
        <select id="type_produit" value={form.type_produit} onChange={(e) => updateField("type_produit", e.target.value)}>
          <option value="L">L</option>
          <option value="M">M</option>
          <option value="H">H</option>
        </select>

        <button type="submit" disabled={loading}>
          {loading ? "Analyse..." : (<><Search size={16} aria-hidden="true" /> Analyser le risque</>)}
        </button>
      </form>

      {error && <p role="alert" className="error-message">{error}</p>}

      {result && (
        <div className={`predict-result risk-${result.niveau_risque}`} role="status">
          <span className="result-icon" aria-hidden="true">
            <RiskIcon size={22} />
          </span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p>
              <strong>{result.panne_predite ? "Panne probable" : "Pas de panne prévue"}</strong> — probabilité{" "}
              {(result.probabilite * 100).toFixed(1)} % (risque {RISK_LABELS[result.niveau_risque]})
            </p>
            <div className="risk-bar-track">
              <div className="risk-bar-fill" style={{ width: `${Math.min(100, result.probabilite * 100)}%` }} />
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
