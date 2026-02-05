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
  },
  base: '/admin/standalone/',
  build: {
    outDir: 'dist',
    sourcemap: true,
    target: 'es2020',
    reportCompressedSize: true,
    rollupOptions: {
      input: resolve(__dirname, 'index.html'),
    },
  },
  server: {
    port: 3300,
  },
});
