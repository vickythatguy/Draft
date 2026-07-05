import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      // Backend: uvicorn server:app --port 8000 (from backend/)
      '/api': 'http://localhost:8000',
    },
  },
});
