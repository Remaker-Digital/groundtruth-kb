import { jsx as _jsx } from "react/jsx-runtime";
import { Navigate, useLocation } from 'react-router-dom';
export const NavigateWithQuery = ({ to, replace }) => {
    const location = useLocation();
    const target = to.includes('?') ? to : `${to}${location.search}`;
    return _jsx(Navigate, { to: target, replace: replace });
};
//# sourceMappingURL=NavigateWithQuery.js.map