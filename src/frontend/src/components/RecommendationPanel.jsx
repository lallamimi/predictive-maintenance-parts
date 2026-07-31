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

  return (
    <section aria-labelledby="reco-title" className="panel reco-panel">
      <h2 id="reco-title">Recommandation</h2>
      {loading && <p>Chargement de la recommandation...</p>}
      {error && <p role="alert" className="error-message">{error}</p>}
      {reco && (
        <>
          <p>{reco.recommandation}</p>
          <p className="reco-source">
            Source : {reco.source === "groq" ? "IA générative (Groq)" : "règles automatiques (service IA non configuré)"}
          </p>
        </>
      )}
    </section>
  );
}
