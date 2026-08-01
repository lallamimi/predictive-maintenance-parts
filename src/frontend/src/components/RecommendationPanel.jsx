import { useEffect, useState } from "react";
import { recommendationsApi } from "../api/client";

export default function RecommendationPanel() {
  const [reco, setReco] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    recommendationsApi
      .get()
      .then(setReco)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const isGroq = reco?.source === "groq";

  return (
    <section aria-labelledby="reco-title" className="panel reco-panel">
      <h2 id="reco-title"><span aria-hidden="true">💡</span> Recommandation</h2>
      {loading && <p>Chargement de la recommandation...</p>}
      {error && <p role="alert" className="error-message">{error}</p>}
      {reco && (
        <div className="reco-body">
          <span className="reco-icon" aria-hidden="true">{isGroq ? "🤖" : "📐"}</span>
          <div className="reco-text">
            <p>{reco.recommandation}</p>
            <span className="reco-source">
              {isGroq ? "🤖 IA générative (Groq)" : "📐 Règles automatiques (service IA non configuré)"}
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
