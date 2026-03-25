import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ActivationDialog — Modal for validating and activating draft configuration.
 *
 * Triggered by the [Activate] button on ActivationBanner. Shows:
 *   1. Validation status — green checks / red X / yellow warnings
 *   2. Change summary grouped by category
 *   3. [Activate now] button (disabled if hard-block validation fails)
 *   4. [Cancel] button
 *
 * API endpoints consumed:
 *   GET  /api/config/draft          — Full draft state + diff
 *   POST /api/config/draft/activate — Execute activation
 *
 * Props:
 *   - apiFetch  — shell-provided fetch wrapper
 *   - onNotify  — shell toast callback
 *   - onClose   — close the dialog
 *   - onSuccess — called after successful activation (trigger banner refresh)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useCallback, useEffect, useState } from 'react';
import { tokens, dialog, button } from './theme/styles';
// ---------------------------------------------------------------------------
// Field grouping
// ---------------------------------------------------------------------------
/** Map page slugs from preflight validation to human-readable labels. */
function pageLabel(page) {
    const map = {
        'agent-configuration': 'Agent configuration',
        'knowledge-base': 'Knowledge base',
        'quick-actions': 'Quick actions',
        'widget-configuration': 'Widget configuration',
        'system': 'System',
    };
    return map[page] ?? page.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
/** Map config field prefixes to human-readable group names. */
function groupField(field) {
    if (field === 'kb_modified_at')
        return 'Knowledge base';
    if (field === 'qa_modified_at')
        return 'Quick actions';
    if (field.startsWith('widget_'))
        return 'Widget configuration';
    if (field.startsWith('retrieval_') || field.startsWith('intent_'))
        return 'Retrieval & intent';
    if (field.startsWith('escalation_'))
        return 'Escalation rules';
    if (['brand_name', 'brand_voice', 'brand_tagline', 'greeting_message',
        'greeting_follow_up'].includes(field))
        return 'Brand & tone';
    if (['response_length', 'formality_level', 'use_emoji', 'cite_sources_in_response',
        'custom_instructions'].includes(field))
        return 'Response style';
    if (field.startsWith('memory_') || field.startsWith('data_retention_'))
        return 'Memory & privacy';
    return 'Agent configuration';
}
/** Human-readable label for signal fields and config fields. */
function fieldLabel(field) {
    if (field === 'kb_modified_at')
        return 'articles modified';
    if (field === 'qa_modified_at')
        return 'prompts or assignments modified';
    return field.replace(/_/g, ' ');
}
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ActivationDialog({ apiFetch, onNotify, onClose, onSuccess, }) {
    const [draft, setDraft] = useState(null);
    const [preflight, setPreflight] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activating, setActivating] = useState(false);
    const [confirmed, setConfirmed] = useState(false);
    const [activateErrors, setActivateErrors] = useState([]);
    const [activateWarnings, setActivateWarnings] = useState([]);
    // Fetch draft state + preflight validation on mount (D35: show errors immediately)
    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const [draftRes, preflightRes] = await Promise.all([
                    apiFetch('/api/config/draft'),
                    apiFetch('/api/config/draft/preflight'),
                ]);
                if (!cancelled) {
                    if (draftRes.ok)
                        setDraft(await draftRes.json());
                    if (preflightRes.ok)
                        setPreflight(await preflightRes.json());
                }
            }
            catch {
                // handled
            }
            finally {
                if (!cancelled)
                    setLoading(false);
            }
        })();
        return () => { cancelled = true; };
    }, [apiFetch]);
    // Activate handler
    const handleActivate = useCallback(async () => {
        setActivating(true);
        setActivateErrors([]);
        setActivateWarnings([]);
        try {
            const res = await apiFetch('/api/config/draft/activate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: '{}',
            });
            if (res.ok) {
                const result = await res.json();
                if (result.warnings?.length) {
                    setActivateWarnings(result.warnings);
                }
                onNotify(`Configuration activated (v${result.version})`, 'success');
                onSuccess();
                onClose();
            }
            else {
                const body = await res.json().catch(() => ({ detail: 'Activation failed' }));
                const errors = body.detail?.errors ?? [{ field: '_system', message: body.detail ?? 'Activation failed' }];
                setActivateErrors(errors);
                onNotify('Activation blocked — see errors below', 'error');
            }
        }
        catch {
            onNotify('Network error during activation', 'error');
        }
        finally {
            setActivating(false);
        }
    }, [apiFetch, onNotify, onClose, onSuccess]);
    // Group changed fields
    const groups = {};
    if (draft?.changed_fields) {
        for (const field of draft.changed_fields) {
            const group = groupField(field);
            if (!groups[group])
                groups[group] = [];
            groups[group].push(field);
        }
    }
    return (_jsx("div", { style: dialog.overlay, onClick: onClose, children: _jsxs("div", { style: dialogPanel, onClick: e => e.stopPropagation(), children: [_jsxs("div", { style: headerStyle, children: [_jsx("h2", { style: dialog.title, children: "Activate configuration" }), _jsx("button", { onClick: onClose, style: dialog.closeButton, children: "\u2715" })] }), _jsxs("div", { style: bodyStyle, children: [loading && _jsx("div", { style: mutedCentered, children: "Loading\u2026" }), !loading && preflight && preflight.hard_errors.length > 0 && (_jsxs("div", { style: dialog.errorSection, children: [_jsx("h3", { style: dialog.errorSectionTitle, children: "Required before activation" }), _jsx("div", { style: { ...summaryStyle, marginBottom: '12px' }, children: "The following fields must be configured before your AI assistant can be activated:" }), preflight.hard_errors.map((e, i) => (_jsxs("div", { style: dialog.errorText, children: [_jsxs("strong", { children: [e.page ? pageLabel(e.page) : e.field, ":"] }), " ", e.message] }, i)))] })), !loading && preflight && preflight.warnings.length > 0 && (_jsxs("div", { style: warningSectionStyle, children: [_jsx("h3", { style: dialog.warningSectionTitle, children: "Recommendations" }), preflight.warnings.map((w, i) => (_jsxs("div", { style: warningItemStyle, children: [_jsxs("strong", { children: [w.page ? pageLabel(w.page) : w.field, ":"] }), " ", w.message] }, i)))] })), !loading && draft?.has_pending_changes && preflight?.can_activate && (_jsxs("div", { style: sectionStyle, children: [_jsx("h3", { style: sectionTitleStyle, children: "Changes to activate" }), _jsxs("div", { style: summaryStyle, children: [draft.changed_fields.length, " field", draft.changed_fields.length !== 1 ? 's' : '', " changed", draft.draft_version != null && ` (draft v${draft.draft_version})`] }), Object.entries(groups).map(([group, fields]) => (_jsxs("div", { style: groupStyle, children: [_jsx("div", { style: groupLabelStyle, children: group }), _jsx("div", { style: fieldListStyle, children: fields.map(f => (_jsx("span", { style: fieldChipStyle, children: fieldLabel(f) }, f))) })] }, group)))] })), activateErrors.length > 0 && (_jsxs("div", { style: dialog.errorSection, children: [_jsx("h3", { style: dialog.errorSectionTitle, children: "Activation blocked" }), activateErrors.map((e, i) => (_jsxs("div", { style: dialog.errorText, children: [_jsxs("strong", { children: [e.field, ":"] }), " ", e.message] }, i)))] })), !loading && !draft?.has_pending_changes && preflight?.can_activate && (_jsx("div", { style: mutedCentered, children: "Draft configuration is ready to activate." })), confirmed && preflight?.can_activate && activateErrors.length === 0 && (_jsx("div", { style: confirmSectionStyle, children: "Are you sure you want to activate these changes? This will make them live immediately." }))] }), _jsxs("div", { style: footerStyle, children: [_jsx("button", { onClick: onClose, style: dialog.cancelButton, children: preflight && !preflight.can_activate ? 'Close' : 'Cancel' }), preflight?.can_activate && !confirmed ? (_jsx("button", { onClick: () => setConfirmed(true), disabled: loading, style: {
                                ...button.activate,
                                ...(loading ? button.disabled : {}),
                            }, children: "Activate now" })) : preflight?.can_activate && confirmed ? (_jsx("button", { onClick: handleActivate, disabled: activating, style: {
                                ...button.activate,
                                ...(activating ? button.disabled : {}),
                            }, children: activating ? 'Activating…' : 'Yes, activate' })) : null] })] }) }));
}
// ---------------------------------------------------------------------------
// Local style overrides
// ---------------------------------------------------------------------------
const dialogPanel = {
    ...dialog.panel(560),
    maxHeight: '80vh',
    display: 'flex',
    flexDirection: 'column',
};
const headerStyle = {
    ...dialog.header,
    padding: '20px 24px 16px',
};
const bodyStyle = {
    padding: '16px 24px',
    overflowY: 'auto',
    flex: 1,
};
const mutedCentered = {
    color: tokens.textMuted,
    textAlign: 'center',
    padding: '24px',
};
const sectionStyle = { marginBottom: '16px' };
const sectionTitleStyle = {
    color: tokens.textSecondary,
    fontSize: '14px',
    fontWeight: 600,
    marginBottom: '8px',
};
const summaryStyle = {
    color: tokens.textMuted,
    fontSize: '13px',
    marginBottom: '12px',
};
const groupStyle = { marginBottom: '10px' };
const groupLabelStyle = {
    color: tokens.textMuted,
    fontSize: '12px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '6px',
};
const fieldListStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '4px',
};
const fieldChipStyle = {
    backgroundColor: tokens.border,
    color: tokens.textSecondary,
    fontSize: '12px',
    padding: '2px 8px',
    borderRadius: '4px',
};
const warningSectionStyle = {
    ...dialog.warningBox,
    borderRadius: '8px',
    padding: '12px 16px',
    marginBottom: '12px',
};
const warningItemStyle = {
    color: '#ffcc66',
    fontSize: '13px',
    marginTop: '4px',
};
const footerStyle = {
    ...dialog.footer,
    padding: '16px 24px',
};
const confirmSectionStyle = {
    backgroundColor: 'rgba(43, 138, 62, 0.1)',
    borderRadius: '8px',
    padding: '12px 16px',
    marginTop: '12px',
    color: '#a0d0b0',
    fontSize: '14px',
    lineHeight: '1.5',
};
//# sourceMappingURL=ActivationDialog.js.map