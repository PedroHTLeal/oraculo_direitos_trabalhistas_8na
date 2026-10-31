import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Encaminha as chamadas /api para o backend FastAPI em desenvolvimento
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
