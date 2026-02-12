/**
 * Configuration page — Shopify embedded admin.
 *
 * Shows OnboardingWizard on first visit (no config saved yet),
 * ConfigEditor on subsequent visits.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Page } from '@shopify/polaris';
import { useAppContext } from '../layouts/ShopifyAppLayout';
import { OnboardingWizard } from '../../shared/OnboardingWizard';
import { ConfigEditor } from '../../shared/ConfigEditor';

export const ConfigurationPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  const [showOnboarding, setShowOnboarding] = useState<boolean | null>(null);

  useEffect(() => {
    if (!tenantContext) return;

    // Check if config exists — if version is 0 or missing, show onboarding
    apiFetch('/api/config')
      .then(async (resp) => {
        if (!resp.ok) {
          setShowOnboarding(true);
          return;
        }
        const data = await resp.json();
        setShowOnboarding(!data.version || data.version === 0);
      })
      .catch(() => setShowOnboarding(true));
  }, [tenantContext, apiFetch]);

  const handleOnboardingComplete = useCallback(() => {
    setShowOnboarding(false);
    onNotify('Configuration saved successfully!', 'success');
  }, [onNotify]);

  if (!tenantContext || showOnboarding === null) return null;

  const baseProps = { tenantContext, apiFetch, onNotify };

  return (
    <Page title={showOnboarding ? 'Setup Wizard' : 'Agent configuration'}>
      {showOnboarding ? (
        <OnboardingWizard {...baseProps} onComplete={handleOnboardingComplete} />
      ) : (
        <ConfigEditor {...baseProps} />
      )}
    </Page>
  );
};
