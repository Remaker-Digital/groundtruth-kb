/**
 * Agent Red Customer Experience — Shopify embedded admin build configuration.
 *
 * SPA build for the Shopify embedded admin shell. Uses Polaris + App Bridge
 * for native Shopify UX. Shared components from admin/shared/ are bundled in.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  base: '/admin/shopify/',
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': resolve(__dirname, '../shared'),
    },
  },
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
    port: 3200,
  },
});
