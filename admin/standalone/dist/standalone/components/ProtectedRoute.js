import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { useAppContext } from '../layouts/StandaloneLayout';
import { NavigateWithQuery } from './NavigateWithQuery';
export const ProtectedRoute = ({ allowedRoles, children, }) => {
    const { userRole, loading } = useAppContext();
    // Still resolving auth — render nothing to prevent flash
    if (loading || userRole === null) {
        return null;
    }
    // Role doesn't match — redirect to inbox (accessible to all roles)
    if (!allowedRoles.includes(userRole)) {
        return _jsx(NavigateWithQuery, { to: "/inbox", replace: true });
    }
    return _jsx(_Fragment, { children: children });
};
//# sourceMappingURL=ProtectedRoute.js.map