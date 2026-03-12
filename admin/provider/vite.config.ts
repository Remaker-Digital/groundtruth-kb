/**
 * Agent Red Customer Experience — Provider admin build configuration.
 *
 * SPA build for the provider (platform operator) admin console.
 * Shared components from admin/shared/ are bundled via @shared alias.
 *
 * Mock mode: `npm run dev:mock` (vite --mode mock) loads the mock API plugin
 * which intercepts all /api/* requests with in-memory fixture data.
 * Zero backend dependency, full HMR support.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig(async ({ mode }) => {
  const isMock = mode === 'mock';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const plugins: any[] = [react()];

  if (isMock) {
    const { mockApiPlugin } = await import('./mocks/plugin');
    plugins.push(mockApiPlugin());
  }

  return {
    root: __dirname,
    plugins,
    resolve: {
      alias: {
        '@shared': resolve(__dirname, '../shared'),
      },
      dedupe: ['@mantine/core', '@mantine/hooks', '@mantine/notifications', 'react', 'react-dom'],
    },
    base: '/admin/provider/',
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
      port: 3400,
      ...(isMock
        ? {}
        : {
            proxy: {
              '/api': {
                target: process.env.VITE_API_URL || 'http://localhost:8000',
                changeOrigin: true,
                secure: !!process.env.VITE_API_URL,
              },
            },
          }),
    },
  };
});
