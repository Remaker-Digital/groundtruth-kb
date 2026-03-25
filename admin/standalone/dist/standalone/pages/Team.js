import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Title, Text } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { TeamManager } from '../../shared/TeamManager';
import { LoadingState } from '../../shared/LoadingState';
export const TeamPage = () => {
    const { tenantContext, apiFetch, onNotify, loading } = useAppContext();
    if (loading || !tenantContext) {
        return _jsx(LoadingState, { text: "Loading team" });
    }
    return (_jsxs("div", { children: [_jsx(Title, { order: 2, mb: "xs", children: "Team members" }), _jsx(Text, { size: "sm", c: "dimmed", mb: "lg", children: "Manage team members, assign roles, and configure escalation categories." }), _jsx(TeamManager, { tenantContext: tenantContext, apiFetch: apiFetch, onNotify: onNotify })] }));
};
//# sourceMappingURL=Team.js.map