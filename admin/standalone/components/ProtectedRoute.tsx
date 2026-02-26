/**
 * ProtectedRoute — Role-based route guard for standalone admin.
 *
 * Wraps child routes and redirects non-matching roles to /inbox.
 * Uses the AppContext userRole resolved from /api/admin/team/whoami.
 *
 * Usage:
 *   <ProtectedRoute allowedRoles={['superadmin', 'admin']}>
 *     <ConfigurationPage />
 *   </ProtectedRoute>
 *
 * If userRole is null (still loading), renders nothing to avoid flash.
 * If userRole doesn't match allowedRoles, redirects to /inbox.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import { Navigate } from 'react-router-dom';

import type { TeamRole } from '../../shared/types';
import { useAppContext } from '../layouts/StandaloneLayout';

interface ProtectedRouteProps {
  /** Roles permitted to view this route. */
  allowedRoles: TeamRole[];
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  allowedRoles,
  children,
}) => {
  const { userRole, loading } = useAppContext();

  // Still resolving auth — render nothing to prevent flash
  if (loading || userRole === null) {
    return null;
  }

  // Role doesn't match — redirect to inbox (accessible to all roles)
  if (!allowedRoles.includes(userRole)) {
    return <Navigate to="/inbox" replace />;
  }

  return <>{children}</>;
};
