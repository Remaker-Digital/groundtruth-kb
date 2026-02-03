import React, { useState, useCallback } from 'react';
import {
  AppProvider,
  Frame,
  Navigation,
  TopBar,
  Page,
  Layout,
  LegacyCard,
  Text,
  Badge,
  Box,
} from '@shopify/polaris';
import {
  HomeIcon,
  ChatIcon,
  CollectionIcon,
  ChartVerticalFilledIcon,
  SettingsIcon,
  DesktopIcon,
  CreditCardIcon,
} from '@shopify/polaris-icons';
import enTranslations from '@shopify/polaris/locales/en.json';

import { ShopifyDashboard } from './pages/ShopifyDashboard';
import { ShopifyInbox } from './pages/ShopifyInbox';
import { ShopifyKnowledge } from './pages/ShopifyKnowledge';
import { ShopifyConfig } from './pages/ShopifyConfig';
import { ShopifyWidget } from './pages/ShopifyWidget';
import { ShopifyBilling } from './pages/ShopifyBilling';
import { ShopifyAnalytics } from './pages/ShopifyAnalytics';

type ShopifyPage = 'dashboard' | 'inbox' | 'knowledge' | 'config' | 'widget' | 'billing' | 'analytics';

export function ShopifyApp() {
  const [activePage, setActivePage] = useState<ShopifyPage>('dashboard');
  const [mobileNavActive, setMobileNavActive] = useState(false);

  const toggleMobileNav = useCallback(() => {
    setMobileNavActive((active) => !active);
  }, []);

  const navigationMarkup = (
    <Navigation location="/">
      <Navigation.Section
        title="Agent Red"
        items={[
          {
            label: 'Dashboard',
            icon: HomeIcon,
            selected: activePage === 'dashboard',
            onClick: () => setActivePage('dashboard'),
          },
          {
            label: 'Inbox',
            icon: ChatIcon,
            badge: '3',
            selected: activePage === 'inbox',
            onClick: () => setActivePage('inbox'),
          },
          {
            label: 'Knowledge Base',
            icon: CollectionIcon,
            selected: activePage === 'knowledge',
            onClick: () => setActivePage('knowledge'),
          },
          {
            label: 'Analytics',
            icon: ChartVerticalFilledIcon,
            selected: activePage === 'analytics',
            onClick: () => setActivePage('analytics'),
          },
        ]}
      />
      <Navigation.Section
        title="Settings"
        items={[
          {
            label: 'Configuration',
            icon: SettingsIcon,
            selected: activePage === 'config',
            onClick: () => setActivePage('config'),
          },
          {
            label: 'Widget',
            icon: DesktopIcon,
            selected: activePage === 'widget',
            onClick: () => setActivePage('widget'),
          },
          {
            label: 'Billing',
            icon: CreditCardIcon,
            selected: activePage === 'billing',
            onClick: () => setActivePage('billing'),
          },
        ]}
      />
    </Navigation>
  );

  const topBarMarkup = (
    <TopBar
      showNavigationToggle
      onNavigationToggle={toggleMobileNav}
      userMenu={
        <TopBar.UserMenu
          actions={[
            { items: [{ content: 'Help Center' }, { content: 'Contact Support' }] },
            { items: [{ content: 'Log out' }] },
          ]}
          name="Acme Outfitters"
          initials="AO"
          open={false}
          onToggle={() => {}}
        />
      }
      searchField={
        <TopBar.SearchField
          onChange={() => {}}
          value=""
          placeholder="Search conversations, articles..."
        />
      }
    />
  );

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': return <ShopifyDashboard />;
      case 'inbox': return <ShopifyInbox />;
      case 'knowledge': return <ShopifyKnowledge />;
      case 'config': return <ShopifyConfig />;
      case 'widget': return <ShopifyWidget />;
      case 'billing': return <ShopifyBilling />;
      case 'analytics': return <ShopifyAnalytics />;
      default: return <ShopifyDashboard />;
    }
  };

  // Shopify Polaris green color
  const shopifyTheme = {
    colors: { 'color-scheme': 'light' as const },
    logo: {
      width: 120,
      topBarSource: '',
      contextualSaveBarSource: '',
      accessibilityLabel: 'Agent Red',
    },
  };

  return (
    <div className="polaris-shell-wrapper" style={{ background: '#f6f6f7', minHeight: '100vh' }}>
      <AppProvider i18n={enTranslations}>
        <Frame
          topBar={topBarMarkup}
          navigation={navigationMarkup}
          showMobileNavigation={mobileNavActive}
          onNavigationDismiss={toggleMobileNav}
        >
          {renderPage()}
        </Frame>
      </AppProvider>
    </div>
  );
}
