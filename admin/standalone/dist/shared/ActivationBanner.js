import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ActivationBanner — Persistent banner for pending configuration changes.
 *
 * Displayed below the header and above page content when draft (unsaved)
 * config changes exist.  Polls GET /api/config/activation-status every
 * 30 seconds to detect changes made on other tabs or by other admins.
 *
 * Actions:
 *   - [Activate] — opens the ActivationDialog
 *   - [Discard]  — discards all draft changes
 *
 * Props (from layout shell):
 *   - apiFetch     — shell-provided fetch wrapper with auth headers
 *   - onNotify     — shell toast callback
 *   - onActivate   — callback to open the ActivationDialog
 *   - refreshKey   — increment to force immediate re-poll after save/discard
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useCallback, useEffect, useState } from 'react';
import { tokens, button } from './theme/styles';
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ActivationBanner({ apiFetch, onNotify, onActivate, refreshKey = 0, }) {
    const [status, setStatus] = useState(null);
    const [discarding, setDiscarding] = useState(false);
    // Poll activation status
    const fetchStatus = useCallback(async () => {
        try {
            const res = await apiFetch('/api/config/activation-status');
            if (res.ok) {
                const data = await res.json();
                setStatus(data);
            }
        }
        catch {
            // Silently ignore polling errors
        }
    }, [apiFetch]);
    // Initial fetch + polling every 30s
    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, [fetchStatus, refreshKey]);
    // Discard handler
    const handleDiscard = useCallback(async () => {
        if (!confirm('Discard all draft changes? This cannot be undone.'))
            return;
        setDiscarding(true);
        try {
            const res = await apiFetch('/api/config/draft/discard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: '{}',
            });
            if (res.ok) {
                onNotify('Draft changes discarded', 'info');
                setStatus(null);
                fetchStatus();
            }
            else {
                onNotify('Failed to discard draft', 'error');
            }
        }
        catch {
            onNotify('Network error discarding draft', 'error');
        }
        finally {
            setDiscarding(false);
        }
    }, [apiFetch, onNotify, fetchStatus]);
    // Don't render if no pending changes
    if (!status?.has_pending_changes)
        return null;
    return (_jsx("div", { style: bannerStyle, children: _jsxs("div", { style: contentStyle, children: [_jsxs("div", { style: textStyle, children: [_jsx("span", { style: iconStyle, children: "\u25CF" }), "You have configuration changes that are not yet live.", status.draft_version != null && (_jsxs("span", { style: versionStyle, children: [" (draft v", status.draft_version, ")"] }))] }), _jsxs("div", { style: actionsStyle, children: [_jsx("button", { onClick: onActivate, style: activateButtonSmall, children: "Activate" }), _jsx("button", { onClick: handleDiscard, disabled: discarding, style: discardButtonStyle, children: discarding ? 'Discarding…' : 'Discard' })] })] }) }));
}
// ---------------------------------------------------------------------------
// Styles (using centralized tokens)
// ---------------------------------------------------------------------------
const bannerStyle = {
    backgroundColor: tokens.page,
    borderBottom: `1px solid ${tokens.action}`,
    padding: '10px 20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
};
const contentStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    maxWidth: '1200px',
    gap: '16px',
};
const textStyle = {
    color: tokens.textPrimary,
    fontSize: '14px',
    lineHeight: '1.4',
};
const iconStyle = {
    color: tokens.action,
    marginRight: '8px',
    fontSize: '10px',
};
const versionStyle = {
    color: tokens.textMuted,
    fontSize: '12px',
};
const actionsStyle = {
    display: 'flex',
    gap: '8px',
    flexShrink: 0,
};
const activateButtonSmall = {
    ...button.activate,
    ...button.sm,
};
const discardButtonStyle = {
    ...button.cancel,
    ...button.sm,
};
//# sourceMappingURL=ActivationBanner.js.map