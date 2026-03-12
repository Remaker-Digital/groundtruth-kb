/**
 * Agent Red Customer Experience — Shopify embedded admin build configuration.
 *
 * SPA build for the Shopify embedded admin shell. Uses Polaris + App Bridge
 * for native Shopify UX. Shared components from admin/shared/ are bundled in.
 *
 * In mock mode (vite --mode mock), the mock API plugin is loaded to intercept
 * /api/* requests and inject a fake App Bridge for local development.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig(async ({ mode }) => {
  const isMock = mode === 'mock';

  // Build plugin list — mock plugin only in mock mode
  const plugins: any[] = [react()];
  if (isMock) {
    const { mockApiPlugin } = await import('./mocks/plugin');
    plugins.push(mockApiPlugin());
  }

  return {
    // Explicit root so Vite resolves node_modules correctly even when
    // invoked from the project root (e.g. via .claude/launch.json).
    root: __dirname,
    base: '/admin/shopify/',
    plugins,
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
  };
});
