// @ts-check

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Agent Red Documentation',
  tagline: 'AI-Powered Customer Engagement Platform',
  favicon: 'img/favicon.ico',

  future: {
    // v4: true — disabled; causes build failures with theme swizzling
    // in Docusaurus 3.9.x. Re-enable when migrating to Docusaurus 4.
  },

  // Production URL — update when domain is finalized
  url: 'https://docs.agentred.com',
  baseUrl: '/',

  organizationName: 'Remaker-Digital',
  projectName: 'agent-red-customer-engagement',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',
  onDuplicateRoutes: 'throw',

  // Mermaid diagrams in code blocks
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: '/', // Docs as the landing page
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: false, // No blog for now
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: 'light',
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Agent Red',
        // logo: {
        //   alt: 'Agent Red Logo',
        //   src: 'img/logo.svg',
        // },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            href: 'https://agentred.com',
            label: 'Website',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/getting-started/overview',
              },
              {
                label: 'Integrations',
                to: '/integrations/shopify',
              },
            ],
          },
          {
            title: 'Product',
            items: [
              {
                label: 'Website',
                href: 'https://agentred.com',
              },
              {
                label: 'Pricing',
                href: 'https://agentred.com/pricing',
              },
            ],
          },
          {
            title: 'Company',
            items: [
              {
                label: 'About',
                href: 'https://agentred.com/about',
              },
              {
                label: 'Contact',
                href: 'https://agentred.com/contact',
              },
            ],
          },
        ],
        copyright: `\u00a9 ${new Date().getFullYear()} Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.`,
      },
      mermaid: {
        theme: {light: 'base', dark: 'dark'},
        options: {
          themeVariables: {
            primaryColor: '#DC2626',
            primaryTextColor: '#ffffff',
            primaryBorderColor: '#991B1B',
            lineColor: '#64748B',
            secondaryColor: '#1E293B',
            tertiaryColor: '#F1F5F9',
          },
        },
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'json', 'python'],
      },
    }),
};

export default config;
