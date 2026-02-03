import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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
    // Semantic colors matching brand palette
    dark: [
      '#F8F8FA', // 0 - Snow (Background)
      '#E8E8ED', // 1 - Silver (Borders)
      '#B0B0BC', // 2
      '#8E8EA0', // 3
      '#6B6B80', // 4 - Steel (Tertiary text)
      '#3D3D56', // 5 - Slate (Secondary text)
      '#2D2D44', // 6
      '#1A1A2E', // 7 - Charcoal (Primary text) ★
      '#141425', // 8
      '#0E0E1C', // 9
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
  other: {
    // Brand palette reference (for inline styles)
    colors: {
      primary: '#C41E2A',
      primaryDark: '#9B1420',
      primaryLight: '#F2D4D6',
      charcoal: '#1A1A2E',
      slate: '#3D3D56',
      steel: '#6B6B80',
      silver: '#E8E8ED',
      snow: '#F8F8FA',
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
    <MantineProvider theme={agentRedTheme} defaultColorScheme="light">
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
