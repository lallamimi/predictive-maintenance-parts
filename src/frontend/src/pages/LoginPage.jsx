import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";

export default function LoginPage() {
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err.message || "Connexion impossible.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <button
        type="button"
        className="btn-icon theme-toggle login-theme-toggle"
        onClick={toggleTheme}
        aria-label={theme === "dark" ? "Activer le thème clair" : "Activer le thème sombre"}
        title={theme === "dark" ? "Thème clair" : "Thème sombre"}
      >
        <span aria-hidden="true">{theme === "dark" ? "☀️" : "🌙"}</span>
      </button>

      <form onSubmit={handleSubmit} aria-labelledby="login-title">
        <div className="login-brand">
          <span className="login-brand-icon" aria-hidden="true">🔧</span>
          <h1 id="login-title">Maintenance Prédictive</h1>
          <p>Aide à la décision — maintenance &amp; pièces de rechange</p>
        </div>

        <label htmlFor="username">Nom d'utilisateur</label>
        <input
          id="username"
          name="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />

        <label htmlFor="password">Mot de passe</label>
        <input
          id="password"
          name="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />

        {error && (
          <p role="alert" className="error-message">
            {error}
          </p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Connexion..." : "🔐 Se connecter"}
        </button>
      </form>
    </main>
  );
}
