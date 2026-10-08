import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiProxy = { target: 'http://127.0.0.1:8001', changeOrigin: true };
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/auth': apiProxy, '/users': apiProxy, '/projects': apiProxy, '/tasks': apiProxy } },
});
