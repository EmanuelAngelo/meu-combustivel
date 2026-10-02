import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
export default defineConfig(({ mode }) => {
 const env = loadEnv(mode, '.', '')
 return {
  plugins: [vue(), tailwindcss()],
  // Demo is opt-in through --mode demo, even with old .env.local files.
  define: { 'import.meta.env.VITE_API_MODE': JSON.stringify(mode === 'demo' ? 'demo' : 'django') },
  server: {
   host: '0.0.0.0', port: 4173, strictPort: true,
   proxy: { '/api': { target: env.DEV_API_TARGET || 'http://127.0.0.1:8000', changeOrigin: true } }
  }
 }
})
