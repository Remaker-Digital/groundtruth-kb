// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * NavigateWithQuery — declarative redirect that preserves URL search params.
 *
 * Drop-in replacement for React Router's <Navigate> in route definitions.
 * Reads the current location.search and appends it to the `to` prop so that
 * ?tenant= (SPEC-1617) survives catch-all and alias redirects.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

interface NavigateWithQueryProps {
  to: string;
  replace?: boolean;
}

export const NavigateWithQuery: React.FC<NavigateWithQueryProps> = ({ to, replace }) => {
  const location = useLocation();
  const target = to.includes('?') ? to : `${to}${location.search}`;
  return <Navigate to={target} replace={replace} />;
};
