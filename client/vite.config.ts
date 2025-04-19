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
  // Add base config if you're deploying to a subdirectory
  // If you're deploying to root, you can omit this
  base: '/',
  build: {
    outDir: 'dist',
  },
})