/**
 * Storybook main configuration (SPEC-1845/WI-1501).
 *
 * Uses @storybook/preact-vite for the Preact widget components.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import type { StorybookConfig } from '@storybook/preact-vite';
import { resolve } from 'path';

const config: StorybookConfig = {
  stories: ['../src/components/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
  ],
  framework: {
    name: '@storybook/preact-vite',
    options: {},
  },
  viteFinal: async (config) => {
    // Inherit path aliases from the main Vite config (resolve() works on Windows)
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': resolve(__dirname, '../src'),
    };
    return config;
  },
};

export default config;
