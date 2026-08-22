import { useEffect, useState } from "react";
import { Bot, Cog, Lightbulb } from "lucide-react";
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
  const SourceIcon = isGroq ? Bot : Cog;

  return (
    <section aria-labelledby="reco-title" className="panel reco-panel">
      <h2 id="reco-title"><Lightbulb size={19} aria-hidden="true" /> Recommandation</h2>
      {loading && <p>Chargement de la recommandation...</p>}
      {error && <p role="alert" className="error-message">{error}</p>}
      {reco && (
        <div className="reco-body">
          <span className="reco-icon" aria-hidden="true">
            <SourceIcon size={18} />
          </span>
          <div className="reco-text">
            <p>{reco.recommandation}</p>
            <span className="reco-source">
              <SourceIcon size={13} aria-hidden="true" />
              {isGroq ? "IA générative (Groq)" : "Règles automatiques (service IA non configuré)"}
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
