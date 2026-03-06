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
    // Ensure imports from admin/shared/ resolve deps from this project's node_modules.
    // Without this, shared components import @mantine/core from admin/node_modules/
    // while index.tsx imports from admin/shopify/node_modules/, creating duplicate
    // React contexts and breaking MantineProvider detection.
    dedupe: ['@mantine/core', '@mantine/hooks', '@mantine/notifications', 'react', 'react-dom'],
  },
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
    port: 3200,
  },
});
