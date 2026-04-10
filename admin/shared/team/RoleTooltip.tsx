// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * RoleTooltip — Hover tooltip showing role permission descriptions.
 *
 * Extracted from TeamManager.tsx. Displays a floating tooltip with all four
 * role definitions when hovering over the "Role" column header.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { RoleTooltipProps } from './types';
import { ROLES, getRoleColors } from './constants';

export const RoleTooltip: React.FC<RoleTooltipProps> = ({
  isDark,
  onMouseEnter,
  onMouseLeave,
}) => {
  const roleColors = getRoleColors(isDark);

  return (
    <div
      style={{
        position: 'absolute',
        top: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        marginTop: 8,
        background: '#1f2937',
        color: '#f9fafb',
        fontSize: 12,
        lineHeight: 1.5,
        padding: '12px 16px',
        borderRadius: 8,
        width: 340,
        maxWidth: 380,
        zIndex: 9999,
        boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
        pointerEvents: 'auto' as const,
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {/* Arrow pointing up */}
      <span style={{
        position: 'absolute',
        bottom: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '6px solid transparent',
        borderRight: '6px solid transparent',
        borderBottom: '6px solid #1f2937',
      }} />
      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 10 }}>Role permissions</div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <tbody>
          {ROLES.map((role) => (
            <tr key={role.value}>
              <td style={{ padding: '6px 12px 6px 0', verticalAlign: 'top', whiteSpace: 'nowrap' }}>
                <span style={{
                  display: 'inline-block',
                  padding: '1px 8px',
                  borderRadius: 10,
                  fontSize: 11,
                  fontWeight: 600,
                  background: (roleColors[role.value] || roleColors.viewer).bg,
                  color: (roleColors[role.value] || roleColors.viewer).text,
                }}>
                  {role.label}
                </span>
              </td>
              <td style={{
                padding: '6px 0',
                fontSize: 11,
                color: '#d1d5db',
                verticalAlign: 'top',
                textTransform: 'none',
                letterSpacing: 'normal',
                fontWeight: 400,
              }}>
                {role.description}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
