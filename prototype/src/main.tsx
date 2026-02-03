import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
// Polaris CSS loaded BEFORE Mantine so Mantine styles take precedence
import '@shopify/polaris/build/esm/styles.css';
import '@mantine/core/styles.css';
import '@mantine/charts/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';
import { StandaloneApp } from './standalone/StandaloneApp';
import { ShopifyApp } from './shopify/ShopifyApp';

// Agent Red brand theme for Mantine — Option A (Inter single family)
// Colors from branding/colors/color-palette.html
const agentRedTheme = createTheme({
  primaryColor: 'brand',
  colors: {
    // Brand red scale: lightest → darkest, index 5 = primary #C41E2A
    brand: [
      '#FDE8E8', // 0 - error bg tint
      '#F2D4D6', // 1 - Soft Red (Primary Light)
      '#E8A3A7', // 2
      '#DC7278', // 3
      '#D14B52', // 4
      '#C41E2A', // 5 - Agent Red (Primary) ★
      '#B01824', // 6
      '#9B1420', // 7 - Deep Red (Primary Dark, hover)
      '#870E18', // 8
      '#720912', // 9
    ],
    // Neutral grey dark scale (no blue/purple tint)
    dark: [
      '#F5F5F5', // 0 - Light grey (text on dark bg)
      '#E0E0E0', // 1 - Borders (light)
      '#A0A0A0', // 2 - Muted text
      '#787878', // 3 - Secondary text
      '#5C5C5C', // 4 - Tertiary text
      '#3A3A3A', // 5 - Elevated surface (cards)
      '#2A2A2A', // 6 - Sidebar / panels
      '#1E1E1E', // 7 - Main background ★
      '#171717', // 8 - Deepest surface
      '#111111', // 9 - True dark
    ],
  },
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  fontFamilyMonospace: "'JetBrains Mono', ui-monospace, monospace",
  headings: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontWeight: '600',
  },
  defaultRadius: 'md',
  cursorType: 'pointer',
  components: {},
  other: {
    // Brand palette reference (for inline styles)
    colors: {
      primary: '#C41E2A',
      primaryDark: '#9B1420',
      primaryLight: '#F2D4D6',
      charcoal: '#1E1E1E',
      slate: '#3A3A3A',
      steel: '#5C5C5C',
      silver: '#E0E0E0',
      snow: '#F5F5F5',
      success: '#0D7C3E',
      warning: '#E5A100',
      error: '#D32F2F',
      info: '#1E3A5F',
    },
  },
});

function ShellSwitcher() {
  const [shell, setShell] = useState<'standalone' | 'shopify'>('standalone');

  return (
    <>
      {/* Floating shell switcher */}
      <div style={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        zIndex: 10000,
        display: 'flex',
        gap: 0,
        borderRadius: 8,
        overflow: 'hidden',
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
        border: '1px solid #e0e0e0',
      }}>
        <button
          onClick={() => setShell('standalone')}
          style={{
            padding: '10px 18px',
            border: 'none',
            cursor: 'pointer',
            fontSize: 13,
            fontWeight: 600,
            fontFamily: 'Inter, sans-serif',
            background: shell === 'standalone' ? '#C41E2A' : '#fff',
            color: shell === 'standalone' ? '#fff' : '#333',
            transition: 'all 0.2s',
          }}
        >
          Standalone (Mantine)
        </button>
        <button
          onClick={() => setShell('shopify')}
          style={{
            padding: '10px 18px',
            border: 'none',
            borderLeft: '1px solid #e0e0e0',
            cursor: 'pointer',
            fontSize: 13,
            fontWeight: 600,
            fontFamily: 'Inter, sans-serif',
            background: shell === 'shopify' ? '#008060' : '#fff',
            color: shell === 'shopify' ? '#fff' : '#333',
            transition: 'all 0.2s',
          }}
        >
          Shopify (Polaris)
        </button>
      </div>

      {shell === 'standalone' ? <StandaloneApp /> : <ShopifyApp />}
    </>
  );
}

function App() {
  return (
    <MantineProvider theme={agentRedTheme} defaultColorScheme="dark">
      <Notifications position="top-right" />
      <BrowserRouter>
        <ShellSwitcher />
      </BrowserRouter>
    </MantineProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
