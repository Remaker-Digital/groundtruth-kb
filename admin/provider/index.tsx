/**
 * Provider Admin Console — entry point.
 *
 * Service Provider Administration console for managing all tenants,
 * monitoring health, and viewing cross-tenant analytics.
 * Requires Service Provider Administrator (SPA) API key (SUPERADMIN role).
 * Supports optional MFA/TOTP verification after API key login.
 *
 * Architecture:
 *   This is a separate SPA from the standalone admin. The standalone admin
 *   is per-tenant (merchant-facing); this console is platform-wide
 *   (operator-facing) and consumes /api/superadmin/* endpoints.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '../shared/theme/tokens.css';

import { agentRedTheme } from '../shared/theme/agentRedTheme';
import { ProviderLayout } from './layouts/ProviderLayout';
import { ApiKeyLogin, LoginResult } from './login/ApiKeyLogin';
import { MfaChallenge } from './login/MfaChallenge';
import { HealthDashboardPage } from './pages/HealthDashboard';
import { TenantDirectoryPage } from './pages/TenantDirectory';
import { BillingHealthPage } from './pages/BillingHealth';
import { SLATrendsPage } from './pages/SLATrends';
import { QueueHealthPage } from './pages/QueueHealth';
import { ComplianceDashboardPage } from './pages/ComplianceDashboard';
import { SecretPosturePage } from './pages/SecretPosture';
import { IntegrationHealthPage } from './pages/IntegrationHealth';
import { StatusPageManagement } from './pages/StatusPage';
import { AlertConfigPage } from './pages/AlertConfig';
import { MfaSettingsPage } from './pages/MfaSettings';
import { UserManagementPage } from './pages/UserManagement';
import { SupportDiagnosticsPage } from './pages/SupportDiagnostics';
import { CostAnalyticsPage } from './pages/CostAnalytics';
import { AbuseDetectionPage } from './pages/AbuseDetection';
import { CopilotKnowledgePage } from './pages/CopilotKnowledge';
import { PipelineObservatoryPage } from './pages/PipelineObservatory';
import { ContactMessagesPage } from './pages/ContactMessages';
import { ServiceMessagesPage } from './pages/ServiceMessages';
import { EntitlementConfigPage } from './pages/EntitlementConfig';
import { BlocklistConfigPage } from './pages/BlocklistConfig';
import { RetryConfigPage } from './pages/RetryConfig';
import { AlertThresholdConfigPage } from './pages/AlertThresholdConfig';
import { NotificationChannelConfigPage } from './pages/NotificationChannelConfig';

import { DeploymentManagementPage } from './pages/DeploymentManagement';
import { TestExecutionPage } from './pages/TestExecution';
import { TestRunDetailPage } from './pages/TestRunDetail';
import { MaintenanceModePage } from './pages/MaintenanceMode';
import { ExperimentManagementPage } from './pages/ExperimentManagement';

// ---------------------------------------------------------------------------
// Auth state (sessionStorage — SUPERADMIN key + MFA token)
// ---------------------------------------------------------------------------

function getStoredApiKey(): string | null {
  try {
    return sessionStorage.getItem('agentred_provider_key');
  } catch {
    return null;
  }
}

function storeApiKey(key: string): void {
  try {
    sessionStorage.setItem('agentred_provider_key', key);
  } catch {
    // sessionStorage unavailable
  }
}

function clearApiKey(): void {
  try {
    sessionStorage.removeItem('agentred_provider_key');
    sessionStorage.removeItem('agentred_provider_mfa_token');
  } catch {
    // sessionStorage unavailable
  }
}

function storeMfaToken(token: string): void {
  try {
    sessionStorage.setItem('agentred_provider_mfa_token', token);
  } catch {
    // sessionStorage unavailable
  }
}

// ---------------------------------------------------------------------------
// App — three-state auth: login → (mfa challenge) → main
// ---------------------------------------------------------------------------

type AuthState = 'login' | 'mfa_challenge' | 'authenticated';

const App: React.FC = () => {
  const [apiKey, setApiKey] = React.useState<string | null>(getStoredApiKey);
  const [authState, setAuthState] = React.useState<AuthState>(
    apiKey ? 'authenticated' : 'login',
  );

  const handleLogin = React.useCallback((result: LoginResult) => {
    storeApiKey(result.apiKey);
    setApiKey(result.apiKey);

    if (result.mfaRequired) {
      setAuthState('mfa_challenge');
    } else {
      setAuthState('authenticated');
    }
  }, []);

  const handleMfaSuccess = React.useCallback((mfaToken: string) => {
    storeMfaToken(mfaToken);
    setAuthState('authenticated');
  }, []);

  const handleMfaCancel = React.useCallback(() => {
    clearApiKey();
    setApiKey(null);
    setAuthState('login');
  }, []);

  const handleLogout = React.useCallback(() => {
    clearApiKey();
    setApiKey(null);
    setAuthState('login');
  }, []);

  if (authState === 'login' || !apiKey) {
    return <ApiKeyLogin onLogin={handleLogin} />;
  }

  if (authState === 'mfa_challenge') {
    return (
      <MfaChallenge
        apiKey={apiKey}
        onSuccess={handleMfaSuccess}
        onCancel={handleMfaCancel}
      />
    );
  }

  return (
    <>
      <Notifications position="top-right" />
      <BrowserRouter basename="/admin/provider">
        <ProviderLayout apiKey={apiKey} onLogout={handleLogout}>
          <Routes>
            {/* Overview */}
            <Route path="/" element={<HealthDashboardPage />} />
            <Route path="/tenants" element={<TenantDirectoryPage />} />
            {/* Operations */}
            <Route path="/deployments" element={<DeploymentManagementPage />} />
            <Route path="/queues" element={<QueueHealthPage />} />
            <Route path="/integrations" element={<IntegrationHealthPage />} />
            <Route path="/status" element={<StatusPageManagement />} />
            <Route path="/alerts" element={<AlertConfigPage />} />
            <Route path="/diagnostics" element={<SupportDiagnosticsPage />} />
            <Route path="/copilot-knowledge" element={<CopilotKnowledgePage />} />
            <Route path="/pipeline" element={<PipelineObservatoryPage />} />
            <Route path="/contact-messages" element={<ContactMessagesPage />} />
            <Route path="/service-messages" element={<ServiceMessagesPage />} />
            {/* Control Plane (Phase C) */}
            <Route path="/entitlements" element={<EntitlementConfigPage />} />
            <Route path="/blocklists" element={<BlocklistConfigPage />} />
            <Route path="/rate-limits" element={<RetryConfigPage />} />
            <Route path="/alert-thresholds" element={<AlertThresholdConfigPage />} />
            <Route path="/notification-channels" element={<NotificationChannelConfigPage />} />

            <Route path="/test-execution" element={<TestExecutionPage />} />
            <Route path="/test-execution/:runId" element={<TestRunDetailPage />} />
            <Route path="/maintenance" element={<MaintenanceModePage />} />
            <Route path="/experiments" element={<ExperimentManagementPage />} />
            {/* Compliance & Security */}
            <Route path="/compliance" element={<ComplianceDashboardPage />} />
            <Route path="/secrets" element={<SecretPosturePage />} />
            <Route path="/billing" element={<BillingHealthPage />} />
            <Route path="/costs" element={<CostAnalyticsPage />} />
            <Route path="/sla" element={<SLATrendsPage />} />
            <Route path="/abuse" element={<AbuseDetectionPage />} />
            {/* Account */}
            <Route path="/users" element={<UserManagementPage />} />
            <Route path="/mfa" element={<MfaSettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ProviderLayout>
      </BrowserRouter>
    </>
  );
};

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

const root = document.getElementById('app');
if (root) {
  createRoot(root).render(
    <MantineProvider theme={agentRedTheme} defaultColorScheme="dark">
      <App />
    </MantineProvider>,
  );
}
