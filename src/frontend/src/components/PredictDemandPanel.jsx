import { useEffect, useState } from "react";
import { dataApi, mlApi } from "../api/client";

export default function PredictDemandPanel() {
  const [pieces, setPieces] = useState([]);
  const [pieceId, setPieceId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    dataApi
      .pieces()
      .then((data) => {
        const list = data.results || data;
        setPieces(list);
        if (list.length > 0) setPieceId(String(list[0].id));
      })
      .catch((err) => setError(err.message));
  }, []);

  async function handlePredict() {
    if (!pieceId) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await mlApi.predictDemand(Number(pieceId));
      setResult(data);
    } catch (err) {
      setError(err.message || "Erreur lors de la prévision.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section aria-labelledby="predict-demand-title" className="panel">
      <h2 id="predict-demand-title">Prévision de demande de pièces</h2>

      <label htmlFor="piece-select">Pièce de rechange</label>
      <select id="piece-select" value={pieceId} onChange={(e) => setPieceId(e.target.value)}>
        {pieces.map((p) => (
          <option key={p.id} value={p.id}>
            {p.nom} ({p.categorie})
          </option>
        ))}
      </select>

      <button type="button" onClick={handlePredict} disabled={loading || !pieceId}>
        {loading ? "Calcul..." : "Prévoir la demande du mois prochain"}
      </button>

      {error && <p role="alert" className="error-message">{error}</p>}

      {result && (
        <div className="predict-result" role="status">
          <p>
            <strong>{result.nom_piece}</strong> : demande prévue ≈ <strong>{result.demande_prevue}</strong> unités le
            mois prochain.
          </p>
          {result.avertissement && <p className="warning">{result.avertissement}</p>}
        </div>
      )}
    </section>
  );
}
