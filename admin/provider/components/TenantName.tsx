/**
 * TenantName — Human-readable tenant identifier with UUID tooltip.
 *
 * Renders the best available human-readable name (email → shop domain → UUID)
 * with a tooltip showing the full tenant UUID for operator reference.
 *
 * SPEC-1569 / WI-0883: Provider Console human-readable tenant identification.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { Text, Tooltip } from '@mantine/core';
import { tokens } from '../../shared/theme/styles';
import type { TenantDisplayInfo } from '../hooks/useTenantDirectory';

interface TenantNameProps {
  /** Raw tenant UUID */
  tenantId: string;
  /** Pre-resolved display info from useTenantDirectory (optional) */
  info?: TenantDisplayInfo;
  /** Text size (default: "xs") */
  size?: string;
}

/**
 * Renders a human-readable tenant name with UUID tooltip.
 *
 * If `info` is provided, uses it directly. Otherwise falls back to
 * displaying the raw tenantId in monospace.
 */
export const TenantName: React.FC<TenantNameProps> = ({
  tenantId,
  info,
  size = 'xs',
}) => {
  const displayName = info?.displayName ?? tenantId;
  const isUuid = info?.isUuid ?? true;

  if (isUuid) {
    // No human-readable name available — show truncated UUID
    return (
      <Tooltip label={tenantId} position="top" withArrow>
        <Text
          size={size}
          ff="monospace"
          c={tokens.textSecondary}
          style={{ cursor: 'help' }}
        >
          {tenantId.length > 12 ? `${tenantId.slice(0, 12)}…` : tenantId}
        </Text>
      </Tooltip>
    );
  }

  // Human-readable name with UUID in tooltip
  return (
    <Tooltip
      label={tenantId}
      position="top"
      withArrow
      multiline
      w={300}
    >
      <Text
        size={size}
        c={tokens.textPrimary}
        style={{ cursor: 'help' }}
        lineClamp={1}
      >
        {displayName}
      </Text>
    </Tooltip>
  );
};
