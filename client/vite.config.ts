import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    exclude: ['date-fns'],
  },
  build: {
    rollupOptions: {
      external: ['date-fns', 'date-fns/locale']
    }
  }
})