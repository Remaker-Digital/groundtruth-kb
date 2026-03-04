/**
 * Agent Red Customer Experience — Standalone admin build configuration.
 *
 * SPA build for the standalone admin shell (Stripe-direct merchants).
 * No UI framework dependency — uses inline styles throughout.
 * Shared components from admin/shared/ are bundled in.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': resolve(__dirname, '../shared'),
    },
    // Ensure imports from admin/shared/ resolve deps from this project's node_modules
    dedupe: ['@mantine/core', '@mantine/hooks', '@mantine/notifications', 'react', 'react-dom'],
  },
  base: '/admin/standalone/',
  build: {
    outDir: 'dist',
    sourcemap: false,
    target: 'es2020',
    reportCompressedSize: true,
    rollupOptions: {
      input: resolve(__dirname, 'index.html'),
    },
  },
  server: {
    port: 3300,
    proxy: {
      '/api': {
        // Dev proxy target: API_PROXY_TARGET (server-side only, not exposed to
        // browser) or VITE_API_URL from .env.local.  API_PROXY_TARGET is preferred
        // by the E2E test conftest so the SPA uses relative URLs through the proxy
        // (avoids cross-origin CORS issues with X-API-Key headers).
        target: process.env.API_PROXY_TARGET || process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: !!(process.env.API_PROXY_TARGET || process.env.VITE_API_URL),
      },
      // Widget served from public/widget.js in dev mode (see StandaloneLayout.tsx)
      // '/widget.js': {
      //   target: process.env.VITE_API_URL || 'http://localhost:8000',
      //   changeOrigin: true,
      //   secure: !!process.env.VITE_API_URL,
      // },
    },
  },
});
