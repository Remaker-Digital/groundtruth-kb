/**
 * Agent Red Customer Experience — Widget build configuration.
 *
 * Builds a single self-contained JS file that merchants embed on their
 * storefront. Target: ~15-20KB gzip.
 *
 * Architecture:
 *   - Preact for rendering (~4.5KB gzip)
 *   - Shadow DOM for launcher button (style isolation)
 *   - iframe for conversation panel (full DOM isolation)
 *   - No external CSS files — all styles are inlined via JS
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

/// <reference types="vitest" />
import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';
import { resolve } from 'path';

export default defineConfig({
  plugins: [preact()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  test: {
    environment: 'happy-dom',
    include: ['tests/**/*.test.{ts,tsx}'],
    globals: true,
  },
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'AgentRedWidget',
      fileName: 'agent-red-widget',
      formats: ['iife'],
    },
    rollupOptions: {
      output: {
        // Single file, no code splitting — must be one <script> tag
        inlineDynamicImports: true,
      },
    },
    // Aggressive minification for bundle size
    minify: 'terser',
    terserOptions: {
      compress: {
        // Keep console.warn and console.error for production diagnostics.
        // Only drop console.log and console.debug (verbose/dev-only).
        pure_funcs: ['console.log', 'console.debug'],
        drop_debugger: true,
      },
    },
    // Target modern browsers (same as Shopify storefront requirements)
    target: 'es2020',
    // Report gzip size in build output
    reportCompressedSize: true,
  },
  // Dev server for local testing
  server: {
    port: 3100,
    open: '/dev.html',
  },
});
