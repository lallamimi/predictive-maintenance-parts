import { useEffect, useState } from "react";
import { dataApi, mlApi } from "../api/client";
import { useAuth } from "../contexts/AuthContext";

const ROLES_GESTION_STOCK = ["gestionnaire_stock", "admin"];

export default function PredictDemandPanel() {
  const { user } = useAuth();
  const peutGererStock = ROLES_GESTION_STOCK.includes(user?.role);

  const [pieces, setPieces] = useState([]);
  const [pieceId, setPieceId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const [nouveauStock, setNouveauStock] = useState("");
  const [stockMessage, setStockMessage] = useState(null);
  const [stockError, setStockError] = useState(null);

  function chargerPieces() {
    return dataApi
      .pieces()
      .then((data) => {
        const list = data.results || data;
        setPieces(list);
        return list;
      })
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    chargerPieces().then((list) => {
      if (list?.length > 0) setPieceId(String(list[0].id));
    });
  }, []);

  const pieceSelectionnee = pieces.find((p) => String(p.id) === pieceId);

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

  async function handleAjusterStock(event) {
    event.preventDefault();
    setStockError(null);
    setStockMessage(null);
    try {
      await dataApi.ajusterStock(Number(pieceId), Number(nouveauStock));
      setStockMessage("Stock mis à jour.");
      setNouveauStock("");
      await chargerPieces();
    } catch (err) {
      setStockError(err.message || "Ajustement refusé.");
    }
  }

  return (
    <section aria-labelledby="predict-demand-title" className="panel">
      <h2 id="predict-demand-title"><span aria-hidden="true">📦</span> Prévision de demande de pièces</h2>

      <label htmlFor="piece-select">Pièce de rechange</label>
      <select id="piece-select" value={pieceId} onChange={(e) => setPieceId(e.target.value)}>
        {pieces.map((p) => (
          <option key={p.id} value={p.id}>
            {p.nom} ({p.categorie}) — stock : {p.stock_actuel}
          </option>
        ))}
      </select>

      <button type="button" onClick={handlePredict} disabled={loading || !pieceId}>
        {loading ? "Calcul..." : "📈 Prévoir la demande du mois prochain"}
      </button>

      {error && <p role="alert" className="error-message">{error}</p>}

      {result && (
        <div className="predict-result" role="status">
          <span className="result-icon" aria-hidden="true">📦</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p>
              <strong>{result.nom_piece}</strong> : demande prévue ≈ <strong>{result.demande_prevue}</strong> unités le
              mois prochain.
            </p>
            {result.avertissement && <p className="warning">{result.avertissement}</p>}
          </div>
        </div>
      )}

      {peutGererStock && pieceSelectionnee && (
        <form onSubmit={handleAjusterStock} className="stock-form" aria-labelledby="stock-form-title">
          <h3 id="stock-form-title"><span aria-hidden="true">✏️</span> Ajuster le stock — {pieceSelectionnee.nom}</h3>
          <label htmlFor="nouveau-stock">Nouveau stock (actuel : {pieceSelectionnee.stock_actuel})</label>
          <input
            id="nouveau-stock"
            type="number"
            min="0"
            value={nouveauStock}
            onChange={(e) => setNouveauStock(e.target.value)}
            required
          />
          <button type="submit">💾 Enregistrer</button>
          {stockMessage && <p role="status">✅ {stockMessage}</p>}
          {stockError && <p role="alert" className="error-message">{stockError}</p>}
        </form>
      )}
    </section>
  );
}
