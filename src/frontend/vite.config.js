import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Sans ce reglage, Vitest transforme le JSX des fichiers de test en mode
  // "classic" via esbuild (React.createElement non importe automatiquement),
  // contrairement au code applicatif deja transforme en runtime "automatic"
  // par @vitejs/plugin-react - d'ou "React is not defined" dans les tests.
  esbuild: {
    jsx: 'automatic',
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    globals: true,
  },
})
