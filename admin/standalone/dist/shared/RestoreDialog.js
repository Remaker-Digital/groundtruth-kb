import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * RestoreDialog — Confirmation modal for restoring the previous activation snapshot.
 *
 * Shows the previous activation timestamp and a summary of what will change.
 * Accessible from a "Restore previous configuration" option in the settings area.
 *
 * API endpoints consumed:
 *   POST /api/config/restore — Execute restore
 *
 * Props:
 *   - apiFetch        — shell-provided fetch wrapper
 *   - onNotify        — shell toast callback
 *   - onClose         — close the dialog
 *   - onSuccess       — called after successful restore (trigger banner refresh)
 *   - activeVersion   — current active version number
 *   - activeActivatedAt — current active activation timestamp (ISO 8601)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useCallback, useState } from 'react';
import { tokens, dialog, button } from './theme/styles';
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function RestoreDialog({ apiFetch, onNotify, onClose, onSuccess, activeVersion, activeActivatedAt, }) {
    const [restoring, setRestoring] = useState(false);
    const handleRestore = useCallback(async () => {
        setRestoring(true);
        try {
            const res = await apiFetch('/api/config/restore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: '{}',
            });
            if (res.ok) {
                const result = await res.json();
                if (result.success) {
                    onNotify(`Restored to previous configuration (v${result.restored_version})`, 'success');
                    onSuccess();
                    onClose();
                }
                else {
                    onNotify(result.error ?? 'Restore failed', 'error');
                }
            }
            else {
                const body = await res.json().catch(() => ({ detail: 'Restore failed' }));
                onNotify(body.detail ?? 'Restore failed', 'error');
            }
        }
        catch {
            onNotify('Network error during restore', 'error');
        }
        finally {
            setRestoring(false);
        }
    }, [apiFetch, onNotify, onClose, onSuccess]);
    const formattedDate = activeActivatedAt
        ? new Date(activeActivatedAt).toLocaleString()
        : 'Unknown';
    return (_jsx("div", { style: dialog.overlay, onClick: onClose, children: _jsxs("div", { style: dialogPanel, onClick: e => e.stopPropagation(), children: [_jsxs("div", { style: headerStyle, children: [_jsx("h2", { style: dialog.title, children: "Restore previous configuration" }), _jsx("button", { onClick: onClose, style: dialog.closeButton, children: "\u2715" })] }), _jsxs("div", { style: bodyStyle, children: [_jsxs("div", { style: warningBoxStyle, children: [_jsx("div", { style: warningIconStyle, children: "\u26A0" }), _jsxs("div", { children: [_jsx("div", { style: dialog.warningText, children: "This will replace the current active configuration with the previously activated version." }), _jsxs("div", { style: detailTextStyle, children: ["Current active: v", activeVersion, activeActivatedAt && ` (activated ${formattedDate})`] })] })] }), _jsx("div", { style: noteStyle, children: "The current active configuration will become the \"previous\" snapshot, so you can restore again if needed." })] }), _jsxs("div", { style: footerStyle, children: [_jsx("button", { onClick: onClose, style: dialog.cancelButton, children: "Cancel" }), _jsx("button", { onClick: handleRestore, disabled: restoring, style: {
                                ...button.action,
                                ...(restoring ? button.disabled : {}),
                            }, children: restoring ? 'Restoring…' : 'Restore now' })] })] }) }));
}
// ---------------------------------------------------------------------------
// Local style overrides
// ---------------------------------------------------------------------------
const dialogPanel = {
    ...dialog.panel(480),
    display: 'flex',
    flexDirection: 'column',
};
const headerStyle = {
    ...dialog.header,
    padding: '20px 24px 16px',
};
const bodyStyle = {
    padding: '20px 24px',
};
const warningBoxStyle = {
    ...dialog.warningBox,
    display: 'flex',
    gap: '12px',
    padding: '14px 16px',
};
const warningIconStyle = {
    fontSize: '20px',
    lineHeight: '1.4',
    flexShrink: 0,
};
const detailTextStyle = {
    color: tokens.textMuted,
    fontSize: '13px',
    marginTop: '6px',
};
const noteStyle = {
    color: tokens.textMuted,
    fontSize: '13px',
    lineHeight: '1.5',
};
const footerStyle = {
    ...dialog.footer,
    padding: '16px 24px',
};
//# sourceMappingURL=RestoreDialog.js.map