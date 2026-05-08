import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@pages': resolve(__dirname, './src/pages'),
      '@context': resolve(__dirname, './src/context'),
      '@api': resolve(__dirname, './src/api'),
    },
  },
  server: {
    port: 5173,
    strictPort: false, // Auto-increment port if 5173 is busy (→ 5174)
    proxy: {
      // Proxy API calls to backend — avoids CORS during local development
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
