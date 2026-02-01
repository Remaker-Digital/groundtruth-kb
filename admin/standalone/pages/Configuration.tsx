/**
 * Configuration page — Standalone admin.
 *
 * Shows OnboardingWizard on first visit, ConfigEditor on subsequent visits.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useAppContext } from '../layouts/StandaloneLayout';
import { OnboardingWizard } from '../../shared/OnboardingWizard';
import { ConfigEditor } from '../../shared/ConfigEditor';

export const ConfigurationPage: React.FC = () => {
  const { tenantContext, apiFetch, onNotify } = useAppContext();
  const [showOnboarding, setShowOnboarding] = useState<boolean | null>(null);

  useEffect(() => {
    if (!tenantContext) return;
    apiFetch('/api/config')
      .then(async (resp) => {
        if (!resp.ok) { setShowOnboarding(true); return; }
        const data = await resp.json();
        setShowOnboarding(!data.version || data.version === 0);
      })
      .catch(() => setShowOnboarding(true));
  }, [tenantContext, apiFetch]);

  const handleComplete = useCallback(() => {
    setShowOnboarding(false);
    onNotify('Configuration saved!', 'success');
  }, [onNotify]);

  if (!tenantContext || showOnboarding === null) return null;
  const baseProps = { tenantContext, apiFetch, onNotify };

  return (
    <div>
      <h1 style={{ margin: '0 0 24px', fontSize: '24px', fontWeight: 600, color: '#1a1a1a' }}>
        {showOnboarding ? 'Setup Wizard' : 'Configuration'}
      </h1>
      {showOnboarding ? (
        <OnboardingWizard {...baseProps} onComplete={handleComplete} />
      ) : (
        <ConfigEditor {...baseProps} />
      )}
    </div>
  );
};
