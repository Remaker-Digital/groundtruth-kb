// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Vitest configuration for the provider admin console (SPEC-1585 coverage / WI-3221).
 *
 * Component tests run under happy-dom with React Testing Library. Mirrors the
 * widget app's Vitest runner; the @shared alias matches vite.config.ts so
 * shared-component imports resolve identically in tests.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': resolve(__dirname, '../shared'),
    },
    dedupe: ['@mantine/core', '@mantine/hooks', '@mantine/notifications', 'react', 'react-dom'],
  },
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
  },
});
