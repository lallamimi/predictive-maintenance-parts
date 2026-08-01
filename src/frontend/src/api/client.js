const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getAccessToken() {
  return localStorage.getItem("access_token");
}

/**
 * Client API minimal (fetch natif, pas de dependance supplementaire).
 * Ajoute automatiquement le jeton JWT si present, et gere les erreurs
 * de maniere uniforme pour que les composants n'aient pas a repeter la logique.
 */
export async function apiFetch(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getAccessToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    // reponse sans corps JSON (ex: 204/205)
  }

  if (!response.ok) {
    const message = data?.detail || data?.non_field_errors?.[0] || `Erreur ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const authApi = {
  login: (username, password) =>
    apiFetch("/api/auth/login/", { method: "POST", body: { username, password }, auth: false }),
  register: (payload) => apiFetch("/api/auth/register/", { method: "POST", body: payload, auth: false }),
  profile: () => apiFetch("/api/auth/profile/"),
};

export const dataApi = {
  kpi: () => apiFetch("/api/data/interventions/kpi/"),
  pieces: () => apiFetch("/api/data/pieces/"),
  piecesSousSeuil: () => apiFetch("/api/data/pieces/sous_seuil/"),
  ajusterStock: (pieceId, nouveauStock) =>
    apiFetch(`/api/data/pieces/${pieceId}/ajuster-stock/`, {
      method: "PATCH",
      body: { nouveau_stock: nouveauStock },
    }),
};

export const mlApi = {
  predictFailure: (payload) => apiFetch("/api/ml/predict-failure/", { method: "POST", body: payload }),
  predictDemand: (pieceId) => apiFetch("/api/ml/predict-demand/", { method: "POST", body: { piece_id: pieceId } }),
};

export const recommendationsApi = {
  get: () => apiFetch("/api/recommendations/"),
};
