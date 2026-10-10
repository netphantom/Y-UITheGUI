import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// In development the API runs on :8000; in production nginx proxies /api (same origin).
export default defineConfig({
  plugins: [svelte()],
  server: {
    host: true,
    proxy: { '/api': process.env.YUI_API_URL ?? 'http://localhost:8000' },
  },
});
