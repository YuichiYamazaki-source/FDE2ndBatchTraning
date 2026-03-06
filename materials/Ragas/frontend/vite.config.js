import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',   // コンテナ外 (localhost) からアクセス可能にする
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',  // docker-compose 内部のサービス名
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
  },
})
