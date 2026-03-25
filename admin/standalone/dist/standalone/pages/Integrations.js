import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Title, Text, Loader, useComputedColorScheme } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { IntegrationsManager } from '../../shared/IntegrationsManager';
export const IntegrationsPage = () => {
    const { tenantContext, apiFetch, onNotify, loading } = useAppContext();
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    if (loading || !tenantContext) {
        return (_jsx("div", { style: { padding: 40, textAlign: 'center' }, children: _jsx(Loader, { size: "sm" }) }));
    }
    return (_jsxs("div", { style: { maxWidth: 900, margin: '0 auto' }, children: [_jsx(Title, { order: 2, mb: "xs", children: "Integrations" }), _jsx(Text, { size: "sm", c: "dimmed", mb: "lg", children: "Connect third-party services to extend your AI agent's capabilities." }), _jsx(IntegrationsManager, { tenantContext: tenantContext, apiFetch: apiFetch, onNotify: onNotify, isDark: isDark, basePath: "/admin/standalone" })] }));
};
//# sourceMappingURL=Integrations.js.map