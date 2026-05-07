// @ts-check

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Agent Red Customer Experience',
  tagline: 'AI-powered customer service that remembers every shopper',
  favicon: 'img/favicon.ico',

  future: {
    // v4: true — disabled; causes build failures with theme swizzling
    // in Docusaurus 3.9.x. Re-enable when migrating to Docusaurus 4.
  },

  // Production URL
  url: 'https://agentredcx.com',
  baseUrl: '/',

  organizationName: 'Remaker-Digital',
  projectName: 'agent-red-customer-engagement',
  trailingSlash: false,
  deploymentBranch: 'gh-pages',

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
          routeBasePath: 'docs',
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
        logo: {
          alt: 'Agent Red Logo',
          src: 'img/logo.svg',
          srcDark: 'img/logo-dark.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            to: '/docs/changelog',
            label: 'Changelog',
            position: 'left',
          },
          {
            to: '/docs/integrations/shopify',
            label: 'Get Started with Shopify',
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
                label: 'Getting started',
                to: '/docs/getting-started/overview',
              },
              {
                label: 'Admin guide',
                to: '/docs/admin-guide',
              },
              {
                label: 'Shopify integration',
                to: '/docs/integrations/shopify',
              },
              {
                label: 'Billing',
                to: '/docs/billing/billable-conversation-spec',
              },
            ],
          },
          {
            title: 'Product',
            items: [
              {
                label: 'Changelog',
                to: '/docs/changelog',
              },
              {
                label: 'Get Started with Shopify',
                to: '/docs/integrations/shopify',
              },
            ],
          },
          {
            title: 'Legal',
            items: [
              {
                label: 'Privacy policy',
                href: 'https://www.iubenda.com/privacy-policy/51316355',
              },
              {
                label: 'Terms of service',
                to: '/docs/legal/terms',
              },
            ],
          },
          {
            title: 'Support',
            items: [
              {
                label: 'Contact us',
                href: 'mailto:support@remakerdigital.com',
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
            primaryColor: '#ff3621',
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
