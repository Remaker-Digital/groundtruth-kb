import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * ConversationInbox - Two-panel conversation inbox for the Admin dashboard.
 *
 * Left panel: conversation list with customer name, status badge, message count, last message time.
 * Right panel: full message transcript with customer/agent/system messages styled distinctly.
 * Supports assign-to-agent and internal notes. Polls for new conversations every 5 seconds.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 * Receives auth, API fetch, and notification callbacks from the shell.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { usePolling, useConversationMessages, useAssignConversation, useEscalateConversation, useResolveConversation, useArchiveConversation, useTeamMembers, useSearchConversations, useConversationTrace, } from './hooks';
import { HelpTooltip } from './HelpTooltip';
import { tokens } from './theme/styles';
// ---------------------------------------------------------------------------
// Style constants
// ---------------------------------------------------------------------------
const BRAND_PRIMARY = tokens.brand; // accent only — message bubbles, spinner
const ACTION_BLUE = tokens.action;
const COLOR_SUCCESS = '#22863a';
const COLOR_DANGER = '#d73a49';
const COLOR_GRAY = '#6a737d';
const COLOR_LIGHT_GRAY = '#f6f8fa';
const COLOR_BORDER = '#e1e4e8';
const COLOR_WHITE = '#ffffff';
const COLOR_TEXT = '#24292e';
const COLOR_TEXT_SECONDARY = '#586069';
const FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";
const FONT_MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, monospace";
const BORDER_RADIUS = '6px';
const STATUS_COLORS = {
    active: COLOR_SUCCESS,
    ended: COLOR_GRAY,
    escalated: COLOR_DANGER,
    resolved: '#6f42c1',
    timed_out: '#e36209',
    error: COLOR_DANGER,
};
const STATUS_LABELS = {
    active: 'Active',
    ended: 'Ended',
    escalated: 'Escalated',
    resolved: 'Resolved',
    timed_out: 'Timed out',
    error: 'Error',
};
// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function formatRelativeTime(isoString) {
    if (!isoString)
        return '--';
    const date = new Date(isoString);
    const now = Date.now();
    const diffMs = now - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    if (diffSec < 60)
        return 'just now';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60)
        return `${diffMin}m ago`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24)
        return `${diffHour}h ago`;
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay < 30)
        return `${diffDay}d ago`;
    return date.toLocaleDateString();
}
function formatTimestamp(ts) {
    if (!ts)
        return '--';
    const d = new Date(ts);
    if (isNaN(d.getTime()))
        return '--';
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function formatDateHeader(ts) {
    if (!ts)
        return 'Unknown';
    const d = new Date(ts);
    if (isNaN(d.getTime()))
        return 'Unknown';
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (d.toDateString() === today.toDateString())
        return 'Today';
    if (d.toDateString() === yesterday.toDateString())
        return 'Yesterday';
    return d.toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' });
}
// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------
const StatusBadge = ({ status }) => {
    const key = status ?? 'active';
    const color = STATUS_COLORS[key] ?? COLOR_GRAY;
    const label = STATUS_LABELS[key] ?? (status ?? 'Unknown');
    return (_jsxs("span", { style: {
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '12px',
            color,
            fontWeight: 500,
        }, children: [_jsx("span", { style: {
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: color,
                    display: 'inline-block',
                    flexShrink: 0,
                } }), label] }));
};
const ConversationItem = ({ conversation, isSelected, onClick, memberMap }) => (_jsxs("div", { onClick: onClick, role: "button", tabIndex: 0, onKeyDown: (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick();
        }
    }, style: {
        padding: '12px 16px',
        borderBottom: `1px solid ${COLOR_BORDER}`,
        backgroundColor: isSelected ? '#f1f5ff' : COLOR_WHITE,
        cursor: 'pointer',
        transition: 'background-color 0.15s ease',
    }, onMouseEnter: (e) => {
        if (!isSelected)
            e.currentTarget.style.backgroundColor = COLOR_LIGHT_GRAY;
    }, onMouseLeave: (e) => {
        e.currentTarget.style.backgroundColor = isSelected ? '#f1f5ff' : COLOR_WHITE;
    }, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }, children: [_jsx("span", { style: { fontWeight: 600, fontSize: '14px', color: COLOR_TEXT }, children: conversation.customerName || conversation.customerId || 'Anonymous' }), _jsx("span", { style: { fontSize: '11px', color: COLOR_TEXT_SECONDARY }, children: formatRelativeTime(conversation.lastActivityAt ?? conversation.startedAt) })] }), _jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' }, children: [_jsx(StatusBadge, { status: conversation.status }), _jsxs("span", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, display: 'inline-flex', alignItems: 'center', gap: '6px' }, children: [conversation.isBillable && (_jsxs("span", { style: { display: 'inline-flex', alignItems: 'center' }, children: [_jsx("span", { style: {
                                        fontSize: '10px',
                                        fontWeight: 600,
                                        color: COLOR_SUCCESS,
                                        backgroundColor: COLOR_SUCCESS + '18',
                                        padding: '1px 5px',
                                        borderRadius: '4px',
                                    }, children: "Billable" }), _jsx(HelpTooltip, { text: "Whether this conversation counts toward your monthly allowance.", docLink: "https://agentredcx.com/docs/billing/billable-conversation-spec" })] })), conversation.messageCount, " message", conversation.messageCount !== 1 ? 's' : ''] })] }), (conversation.assignedTo || conversation.escalationCategory) && (_jsxs("div", { style: { display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px', flexWrap: 'wrap' }, children: [conversation.escalationCategory && (_jsx("span", { style: {
                        fontSize: '10px',
                        fontWeight: 600,
                        color: COLOR_DANGER,
                        backgroundColor: COLOR_DANGER + '14',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        textTransform: 'capitalize',
                    }, children: conversation.escalationCategory.replace(/_/g, ' ') })), conversation.assignedTo && (_jsxs("span", { style: { fontSize: '11px', color: COLOR_TEXT_SECONDARY }, children: ["Assigned to: ", memberMap?.[conversation.assignedTo] ?? conversation.assignedTo] }))] }))] }));
const MessageBubble = ({ message }) => {
    const isCustomer = message.role === 'customer';
    const isSystem = message.role === 'system';
    const bubbleStyle = isSystem
        ? {
            backgroundColor: COLOR_LIGHT_GRAY,
            color: COLOR_TEXT_SECONDARY,
            fontSize: '12px',
            fontStyle: 'italic',
            padding: '8px 12px',
            borderRadius: BORDER_RADIUS,
            maxWidth: '85%',
            margin: '4px auto',
            textAlign: 'center',
        }
        : {
            backgroundColor: isCustomer ? '#e8eaf6' : BRAND_PRIMARY + '14',
            color: COLOR_TEXT,
            padding: '10px 14px',
            borderRadius: BORDER_RADIUS,
            maxWidth: '75%',
            marginLeft: isCustomer ? '0' : 'auto',
            marginRight: isCustomer ? 'auto' : '0',
            borderBottomLeftRadius: isCustomer ? '2px' : BORDER_RADIUS,
            borderBottomRightRadius: isCustomer ? BORDER_RADIUS : '2px',
        };
    return (_jsxs("div", { style: { marginBottom: '8px' }, children: [!isSystem && (_jsxs("div", { style: {
                    fontSize: '11px',
                    color: COLOR_TEXT_SECONDARY,
                    marginBottom: '2px',
                    textAlign: isCustomer ? 'left' : 'right',
                }, children: [isCustomer ? 'Customer' : 'Agent Red AI', " ", ' ', _jsx("span", { style: { fontFamily: FONT_MONO, fontSize: '10px' }, children: formatTimestamp(message.timestamp) })] })), _jsx("div", { style: bubbleStyle, children: message.content })] }));
};
const AssignModal = ({ conversationId, members, onAssign, onClose, assigning }) => {
    const [selectedAgent, setSelectedAgent] = useState('');
    return (_jsx("div", { style: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
        }, onClick: onClose, children: _jsxs("div", { style: {
                backgroundColor: COLOR_WHITE,
                borderRadius: BORDER_RADIUS,
                padding: '24px',
                width: '380px',
                maxWidth: '90vw',
                boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            }, onClick: (e) => e.stopPropagation(), children: [_jsxs("h3", { style: { margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }, children: ["Assign conversation", _jsx(HelpTooltip, { text: "Assign this conversation to a team member for follow-up.", docLink: "https://agentredcx.com/docs/admin-guide/conversations#conversation-detail" })] }), _jsxs("select", { value: selectedAgent, onChange: (e) => setSelectedAgent(e.target.value), style: {
                        width: '100%',
                        padding: '8px 12px',
                        border: `1px solid ${COLOR_BORDER}`,
                        borderRadius: BORDER_RADIUS,
                        fontSize: '14px',
                        fontFamily: FONT_FAMILY,
                        backgroundColor: COLOR_WHITE,
                        marginBottom: '16px',
                    }, children: [_jsx("option", { value: "", children: "Select team member..." }), members
                            .filter((m) => m.isActive)
                            .map((m) => (_jsxs("option", { value: m.id, children: [m.displayName, " (", m.role, ")"] }, m.id)))] }), _jsxs("div", { style: { display: 'flex', gap: '8px', justifyContent: 'flex-end' }, children: [_jsx("button", { onClick: onClose, style: {
                                padding: '8px 16px',
                                border: `1px solid ${COLOR_BORDER}`,
                                borderRadius: BORDER_RADIUS,
                                backgroundColor: COLOR_WHITE,
                                color: COLOR_TEXT,
                                fontSize: '13px',
                                fontFamily: FONT_FAMILY,
                                cursor: 'pointer',
                            }, children: "Cancel" }), _jsx("button", { disabled: !selectedAgent || assigning, onClick: async () => {
                                if (selectedAgent) {
                                    await onAssign(conversationId, selectedAgent);
                                    onClose();
                                }
                            }, style: {
                                padding: '8px 16px',
                                border: 'none',
                                borderRadius: BORDER_RADIUS,
                                backgroundColor: !selectedAgent || assigning ? COLOR_GRAY : ACTION_BLUE,
                                color: COLOR_WHITE,
                                fontSize: '13px',
                                fontFamily: FONT_FAMILY,
                                fontWeight: 500,
                                cursor: !selectedAgent || assigning ? 'not-allowed' : 'pointer',
                                opacity: assigning ? 0.7 : 1,
                            }, children: assigning ? 'Assigning...' : 'Assign' })] })] }) }));
};
// Escalation categories matching backend ESCALATION_CATEGORIES
const ESCALATION_CATEGORIES = [
    { value: 'service', label: 'Service' },
    { value: 'support', label: 'Support' },
    { value: 'sales', label: 'Sales' },
    { value: 'account', label: 'Account' },
    { value: 'technical_assistance', label: 'Technical Assistance' },
    { value: 'general_inquiry', label: 'General Inquiry' },
];
const EscalateModal = ({ conversationId, members, onEscalate, onClose, escalating }) => {
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedAgent, setSelectedAgent] = useState('');
    // All active team members — any member can be manually assigned.
    // Designated escalation agents for the selected category appear first.
    const availableAgents = useMemo(() => {
        if (!selectedCategory)
            return [];
        const active = members.filter((m) => m.isActive);
        // Sort: designated agents for this category first, then others
        return active.sort((a, b) => {
            const aMatch = a.role === 'escalation_agent' &&
                (a.escalationCategories ?? []).includes(selectedCategory)
                ? 0
                : 1;
            const bMatch = b.role === 'escalation_agent' &&
                (b.escalationCategories ?? []).includes(selectedCategory)
                ? 0
                : 1;
            return aMatch - bMatch;
        });
    }, [members, selectedCategory]);
    // Reset agent when category changes
    const handleCategoryChange = (value) => {
        setSelectedCategory(value);
        setSelectedAgent('');
    };
    return (_jsx("div", { style: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
        }, onClick: onClose, children: _jsxs("div", { style: {
                backgroundColor: COLOR_WHITE,
                borderRadius: BORDER_RADIUS,
                padding: '24px',
                width: '420px',
                maxWidth: '90vw',
                boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            }, onClick: (e) => e.stopPropagation(), children: [_jsxs("h3", { style: { margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }, children: ["Escalate to human", _jsx(HelpTooltip, { text: "Choose a department and optionally assign to a specific agent.", docLink: "https://agentredcx.com/docs/admin-guide/conversations#escalation" })] }), _jsxs("label", { style: { display: 'block', fontSize: '13px', fontWeight: 500, color: COLOR_TEXT, marginBottom: '6px' }, children: ["Category ", _jsx("span", { style: { color: COLOR_DANGER }, children: "*" })] }), _jsxs("select", { value: selectedCategory, onChange: (e) => handleCategoryChange(e.target.value), style: {
                        width: '100%',
                        padding: '8px 12px',
                        border: `1px solid ${COLOR_BORDER}`,
                        borderRadius: BORDER_RADIUS,
                        fontSize: '14px',
                        fontFamily: FONT_FAMILY,
                        backgroundColor: COLOR_WHITE,
                        marginBottom: '16px',
                    }, children: [_jsx("option", { value: "", children: "Select category..." }), ESCALATION_CATEGORIES.map((cat) => (_jsx("option", { value: cat.value, children: cat.label }, cat.value)))] }), _jsxs("label", { style: { display: 'block', fontSize: '13px', fontWeight: 500, color: COLOR_TEXT, marginBottom: '6px' }, children: ["Assign to agent ", _jsx("span", { style: { fontSize: '11px', color: COLOR_GRAY }, children: "(optional)" })] }), _jsxs("select", { value: selectedAgent, onChange: (e) => setSelectedAgent(e.target.value), disabled: !selectedCategory, style: {
                        width: '100%',
                        padding: '8px 12px',
                        border: `1px solid ${COLOR_BORDER}`,
                        borderRadius: BORDER_RADIUS,
                        fontSize: '14px',
                        fontFamily: FONT_FAMILY,
                        backgroundColor: !selectedCategory ? COLOR_LIGHT_GRAY : COLOR_WHITE,
                        marginBottom: availableAgents.length === 0 && selectedCategory ? '4px' : '16px',
                        opacity: !selectedCategory ? 0.6 : 1,
                    }, children: [_jsx("option", { value: "", children: "Auto-assign (best available)" }), availableAgents.map((m) => (_jsx("option", { value: m.id, children: m.displayName }, m.id)))] }), availableAgents.length === 0 && selectedCategory && (_jsx("p", { style: { fontSize: '11px', color: COLOR_GRAY, margin: '0 0 16px 0' }, children: "No team members available. Add team members via the Team page to enable assignment." })), _jsxs("div", { style: { display: 'flex', gap: '8px', justifyContent: 'flex-end' }, children: [_jsx("button", { onClick: onClose, style: {
                                padding: '8px 16px',
                                border: `1px solid ${COLOR_BORDER}`,
                                borderRadius: BORDER_RADIUS,
                                backgroundColor: COLOR_WHITE,
                                color: COLOR_TEXT,
                                fontSize: '13px',
                                fontFamily: FONT_FAMILY,
                                cursor: 'pointer',
                            }, children: "Cancel" }), _jsx("button", { disabled: !selectedCategory || escalating, onClick: async () => {
                                if (selectedCategory) {
                                    await onEscalate(conversationId, {
                                        category: selectedCategory,
                                        agentId: selectedAgent || undefined,
                                    });
                                    onClose();
                                }
                            }, style: {
                                padding: '8px 16px',
                                border: 'none',
                                borderRadius: BORDER_RADIUS,
                                backgroundColor: !selectedCategory || escalating ? COLOR_GRAY : COLOR_DANGER,
                                color: COLOR_WHITE,
                                fontSize: '13px',
                                fontFamily: FONT_FAMILY,
                                fontWeight: 500,
                                cursor: !selectedCategory || escalating ? 'not-allowed' : 'pointer',
                                opacity: escalating ? 0.7 : 1,
                            }, children: escalating ? 'Escalating...' : 'Escalate' })] })] }) }));
};
const NoteModal = ({ conversationId, apiFetch, onClose, onSuccess }) => {
    const [note, setNote] = useState('');
    const [saving, setSaving] = useState(false);
    const handleSave = useCallback(async () => {
        if (!note.trim())
            return;
        setSaving(true);
        try {
            const resp = await apiFetch(`/api/admin/conversations/${conversationId}/notes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: note.trim() }),
            });
            if (!resp.ok)
                throw new Error(`${resp.status}`);
            onSuccess();
            onClose();
        }
        catch {
            // error handled silently — shell notification used externally
        }
        finally {
            setSaving(false);
        }
    }, [note, conversationId, apiFetch, onSuccess, onClose]);
    return (_jsx("div", { style: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
        }, onClick: onClose, children: _jsxs("div", { style: {
                backgroundColor: COLOR_WHITE,
                borderRadius: BORDER_RADIUS,
                padding: '24px',
                width: '420px',
                maxWidth: '90vw',
                boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            }, onClick: (e) => e.stopPropagation(), children: [_jsxs("h3", { style: { margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }, children: ["Add internal note", _jsx(HelpTooltip, { text: "Private notes visible only to your team, not to customers.", docLink: "https://agentredcx.com/docs/admin-guide/conversations#conversation-detail" })] }), _jsx("textarea", { value: note, onChange: (e) => setNote(e.target.value), placeholder: "Write an internal note about this conversation...", rows: 4, style: {
                        width: '100%',
                        padding: '10px 12px',
                        border: `1px solid ${COLOR_BORDER}`,
                        borderRadius: BORDER_RADIUS,
                        fontSize: '14px',
                        fontFamily: FONT_FAMILY,
                        resize: 'vertical',
                        marginBottom: '16px',
                        boxSizing: 'border-box',
                    } }), _jsxs("div", { style: { display: 'flex', gap: '8px', justifyContent: 'flex-end' }, children: [_jsx("button", { onClick: onClose, style: {
                                padding: '8px 16px',
                                border: `1px solid ${COLOR_BORDER}`,
                                borderRadius: BORDER_RADIUS,
                                backgroundColor: COLOR_WHITE,
                                color: COLOR_TEXT,
                                fontSize: '13px',
                                fontFamily: FONT_FAMILY,
                                cursor: 'pointer',
                            }, children: "Cancel" }), _jsx("button", { disabled: !note.trim() || saving, onClick: handleSave, style: {
                                padding: '8px 16px',
                                border: 'none',
                                borderRadius: BORDER_RADIUS,
                                backgroundColor: !note.trim() || saving ? COLOR_GRAY : ACTION_BLUE,
                                color: COLOR_WHITE,
                                fontSize: '13px',
                                fontFamily: FONT_FAMILY,
                                fontWeight: 500,
                                cursor: !note.trim() || saving ? 'not-allowed' : 'pointer',
                                opacity: saving ? 0.7 : 1,
                            }, children: saving ? 'Saving...' : 'Save note' })] })] }) }));
};
// ---------------------------------------------------------------------------
// Empty / Loading / Error states
// ---------------------------------------------------------------------------
const LoadingSpinner = ({ text = 'Loading...' }) => (_jsxs("div", { style: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 16px', color: COLOR_TEXT_SECONDARY }, children: [_jsx("div", { style: {
                width: '32px',
                height: '32px',
                border: `3px solid ${COLOR_BORDER}`,
                borderTopColor: BRAND_PRIMARY,
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite',
                marginBottom: '12px',
            } }), _jsx("span", { style: { fontSize: '14px' }, children: text }), _jsx("style", { children: `@keyframes spin { to { transform: rotate(360deg); } }` })] }));
const EmptyState = ({ icon, title, subtitle }) => (_jsxs("div", { style: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 16px', color: COLOR_TEXT_SECONDARY }, children: [_jsx("span", { style: { fontSize: '40px', marginBottom: '12px' }, children: icon }), _jsx("span", { style: { fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }, children: title }), subtitle && _jsx("span", { style: { fontSize: '13px' }, children: subtitle })] }));
const ErrorBanner = ({ message, onRetry }) => (_jsxs("div", { style: {
        padding: '12px 16px',
        backgroundColor: '#ffeef0',
        border: `1px solid ${COLOR_DANGER}33`,
        borderRadius: BORDER_RADIUS,
        margin: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
    }, children: [_jsx("span", { style: { fontSize: '13px', color: COLOR_DANGER }, children: message }), onRetry && (_jsx("button", { onClick: onRetry, style: {
                padding: '4px 12px',
                border: `1px solid ${COLOR_DANGER}`,
                borderRadius: BORDER_RADIUS,
                backgroundColor: 'transparent',
                color: COLOR_DANGER,
                fontSize: '12px',
                fontFamily: FONT_FAMILY,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
            }, children: "Retry" }))] }));
// ---------------------------------------------------------------------------
// Pipeline Trace Panel (SPEC-1532)
// ---------------------------------------------------------------------------
const STAGE_COLORS = {
    intent_classifier: '#2563EB',
    knowledge_retriever: '#059669',
    response_generator: '#D97706',
    critic: '#7C3AED',
    escalation: '#DC2626',
    analytics: '#6366F1',
};
const STAGE_LABELS = {
    intent_classifier: 'Intent Classifier',
    knowledge_retriever: 'Knowledge Retriever',
    response_generator: 'Response Generator',
    critic: 'Critic',
    escalation: 'Escalation',
    analytics: 'Analytics',
};
const PipelineTracePanel = ({ trace, loading }) => {
    if (loading) {
        return (_jsx("div", { style: { padding: '12px 16px', fontSize: '12px', color: COLOR_TEXT_SECONDARY }, children: "Loading trace..." }));
    }
    if (!trace)
        return null;
    const totalMs = trace.totalLatencyMs ?? trace.stages.reduce((s, st) => s + st.elapsedMs, 0);
    const maxMs = Math.max(...trace.stages.map((s) => s.elapsedMs), 1);
    return (_jsxs("div", { style: {
            borderTop: `1px solid ${COLOR_BORDER}`,
            backgroundColor: COLOR_WHITE,
            padding: '12px 16px',
        }, children: [_jsxs("div", { style: {
                    fontSize: '11px',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: COLOR_TEXT_SECONDARY,
                    marginBottom: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                }, children: [_jsx("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: COLOR_TEXT_SECONDARY, strokeWidth: "2", children: _jsx("polyline", { points: "22,12 18,12 15,21 9,3 6,12 2,12" }) }), "Pipeline Trace"] }), _jsx("div", { style: { display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '10px' }, children: trace.stages.map((stage, idx) => {
                    const color = STAGE_COLORS[stage.stage] ?? COLOR_GRAY;
                    const label = STAGE_LABELS[stage.stage] ?? stage.stage.replace(/_/g, ' ');
                    const widthPct = Math.max((stage.elapsedMs / maxMs) * 100, 4);
                    return (_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '8px' }, children: [_jsx("span", { style: {
                                    width: '110px',
                                    fontSize: '11px',
                                    color: COLOR_TEXT_SECONDARY,
                                    textOverflow: 'ellipsis',
                                    overflow: 'hidden',
                                    whiteSpace: 'nowrap',
                                    flexShrink: 0,
                                }, children: label }), _jsx("div", { style: { flex: 1, height: '14px', backgroundColor: COLOR_LIGHT_GRAY, borderRadius: '3px', overflow: 'hidden' }, children: _jsx("div", { style: {
                                        width: `${widthPct}%`,
                                        height: '100%',
                                        backgroundColor: color,
                                        borderRadius: '3px',
                                        opacity: stage.succeeded ? 1 : 0.4,
                                    } }) }), _jsxs("span", { style: { width: '50px', fontSize: '11px', color: COLOR_TEXT_SECONDARY, textAlign: 'right', flexShrink: 0, fontFamily: FONT_MONO }, children: [stage.elapsedMs, "ms"] })] }, idx));
                }) }), _jsxs("div", { style: { display: 'flex', flexWrap: 'wrap', gap: '6px', fontSize: '11px' }, children: [trace.intent && (_jsx("span", { style: { padding: '2px 8px', borderRadius: '4px', backgroundColor: '#2563EB14', color: '#2563EB', fontWeight: 500 }, children: trace.intent })), trace.criticPassed !== null && (_jsxs("span", { style: {
                            padding: '2px 8px',
                            borderRadius: '4px',
                            backgroundColor: trace.criticPassed ? '#05966914' : '#DC262614',
                            color: trace.criticPassed ? '#059669' : '#DC2626',
                            fontWeight: 500,
                        }, children: ["Critic: ", trace.criticPassed ? 'PASS' : 'FAIL'] })), totalMs > 0 && (_jsxs("span", { style: { padding: '2px 8px', borderRadius: '4px', backgroundColor: COLOR_LIGHT_GRAY, color: COLOR_TEXT_SECONDARY, fontFamily: FONT_MONO }, children: [totalMs, "ms total"] })), trace.modelUsed && (_jsx("span", { style: { padding: '2px 8px', borderRadius: '4px', backgroundColor: COLOR_LIGHT_GRAY, color: COLOR_TEXT_SECONDARY }, children: trace.modelUsed }))] }), trace.traceId && (_jsxs("div", { style: { marginTop: '6px', fontSize: '10px', color: COLOR_GRAY, fontFamily: FONT_MONO }, children: ["Trace: ", trace.traceId] }))] }));
};
// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export const ConversationInbox = ({ tenantContext, apiFetch, onNotify, }) => {
    const [selectedId, setSelectedId] = useState(null);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [showNoteModal, setShowNoteModal] = useState(false);
    const [showEscalateModal, setShowEscalateModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const messagesEndRef = useRef(null);
    const searchTimerRef = useRef(null);
    // Polling: fetch conversation list every 5 seconds
    const { data: inboxData, loading: inboxLoading, error: inboxError, refetch: refetchInbox, } = usePolling(apiFetch, '/api/admin/conversations', 5000);
    const conversations = inboxData?.conversations ?? [];
    // Selected conversation messages
    const { data: messagesData, loading: messagesLoading, error: messagesError, refetch: refetchMessages, } = useConversationMessages(apiFetch, selectedId || '');
    const messages = messagesData?.messages ?? [];
    // Team members (for assign modal + name resolution)
    const { data: teamData } = useTeamMembers(apiFetch);
    const teamMembers = teamData?.members ?? [];
    const memberMap = useMemo(() => {
        const map = {};
        for (const m of teamMembers) {
            map[m.id] = m.displayName || m.email;
        }
        return map;
    }, [teamMembers]);
    // Search
    const { search: searchConversations, clearSearch, results: searchResults, loading: searchLoading } = useSearchConversations(apiFetch);
    const handleSearchInput = useCallback((value) => {
        setSearchQuery(value);
        if (searchTimerRef.current)
            clearTimeout(searchTimerRef.current);
        if (!value.trim()) {
            clearSearch();
            return;
        }
        searchTimerRef.current = setTimeout(() => {
            searchConversations(value);
        }, 350);
    }, [searchConversations, clearSearch]);
    const isSearchActive = searchResults !== null;
    // Assign conversation
    const { assign, loading: assigning } = useAssignConversation(apiFetch);
    // Escalate conversation
    const { escalate, loading: escalating } = useEscalateConversation(apiFetch);
    // Resolve conversation
    const { resolve, loading: resolving } = useResolveConversation(apiFetch);
    // Archive conversation
    const { archive, loading: archiving } = useArchiveConversation(apiFetch);
    // Auto-scroll to bottom of messages when selected or messages change
    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);
    const selectedConversation = conversations.find((c) => c.conversationId === selectedId) || null;
    // Pipeline trace for selected conversation (SPEC-1532)
    const { data: traceResult } = useConversationTrace(apiFetch, selectedId || '');
    const handleAssign = useCallback(async (conversationId, agentId) => {
        try {
            await assign(conversationId, agentId);
            onNotify('Conversation assigned successfully', 'success');
            refetchInbox();
        }
        catch {
            onNotify('Failed to assign conversation', 'error');
        }
    }, [assign, onNotify, refetchInbox]);
    const handleNoteSuccess = useCallback(() => {
        onNotify('Note added successfully', 'success');
        refetchMessages();
    }, [onNotify, refetchMessages]);
    const handleEscalateClick = useCallback((_conversationId) => {
        setShowEscalateModal(true);
    }, []);
    const handleEscalateConfirm = useCallback(async (conversationId, opts) => {
        try {
            await escalate(conversationId, opts);
            onNotify('Conversation escalated to human support', 'success');
            refetchInbox();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Escalation failed';
            onNotify(msg, 'error');
        }
    }, [escalate, onNotify, refetchInbox]);
    const handleResolve = useCallback(async (conversationId) => {
        try {
            await resolve(conversationId);
            onNotify('Conversation marked as resolved', 'success');
            refetchInbox();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Failed to resolve conversation';
            onNotify(msg, 'error');
        }
    }, [resolve, onNotify, refetchInbox]);
    const handleArchive = useCallback(async (conversationId) => {
        try {
            await archive(conversationId);
            onNotify('Conversation archived', 'success');
            setSelectedId(null);
            refetchInbox();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Failed to archive conversation';
            onNotify(msg, 'error');
        }
    }, [archive, onNotify, refetchInbox]);
    // Group messages by date for day separators
    const groupedMessages = [];
    let currentDateStr = '';
    for (const msg of messages) {
        const ts = msg.timestamp ?? '';
        const dateStr = ts ? new Date(ts).toDateString() : 'Unknown';
        if (dateStr !== currentDateStr) {
            currentDateStr = dateStr;
            groupedMessages.push({ dateLabel: formatDateHeader(msg.timestamp), messages: [] });
        }
        groupedMessages[groupedMessages.length - 1].messages.push(msg);
    }
    return (_jsxs("div", { style: {
            display: 'flex',
            height: '100%',
            minHeight: '500px',
            fontFamily: FONT_FAMILY,
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            overflow: 'hidden',
            backgroundColor: COLOR_WHITE,
        }, children: [_jsxs("div", { style: {
                    width: '340px',
                    minWidth: '280px',
                    borderRight: `1px solid ${COLOR_BORDER}`,
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: COLOR_WHITE,
                }, children: [_jsxs("div", { style: {
                            padding: '16px',
                            borderBottom: `1px solid ${COLOR_BORDER}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                        }, children: [_jsxs("h2", { style: { margin: 0, fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }, children: ["Conversations", _jsx(HelpTooltip, { text: "Real-time list of customer conversations. Filter by status to find active, escalated, or resolved chats.", docLink: "https://agentredcx.com/docs/admin-guide/conversations#conversation-list" })] }), _jsx("span", { style: {
                                    fontSize: '12px',
                                    color: COLOR_TEXT_SECONDARY,
                                    backgroundColor: COLOR_LIGHT_GRAY,
                                    padding: '2px 8px',
                                    borderRadius: '12px',
                                }, children: conversations.length })] }), _jsx("div", { style: { padding: '8px 12px', borderBottom: `1px solid ${COLOR_BORDER}` }, children: _jsxs("div", { style: { position: 'relative' }, children: [_jsx("input", { type: "text", value: searchQuery, onChange: (e) => handleSearchInput(e.target.value), placeholder: "Search messages...", style: {
                                        width: '100%',
                                        padding: '7px 10px 7px 30px',
                                        border: `1px solid ${COLOR_BORDER}`,
                                        borderRadius: BORDER_RADIUS,
                                        fontSize: '13px',
                                        fontFamily: FONT_FAMILY,
                                        backgroundColor: COLOR_LIGHT_GRAY,
                                        boxSizing: 'border-box',
                                        outline: 'none',
                                    }, onFocus: (e) => { e.currentTarget.style.borderColor = ACTION_BLUE; }, onBlur: (e) => { e.currentTarget.style.borderColor = COLOR_BORDER; } }), _jsx("span", { style: { position: 'absolute', left: '9px', top: '50%', transform: 'translateY(-50%)', fontSize: '14px', color: COLOR_TEXT_SECONDARY, pointerEvents: 'none' }, children: searchLoading ? '\u2026' : '\u{1F50D}' }), searchQuery && (_jsx("button", { onClick: () => handleSearchInput(''), style: { position: 'absolute', right: '6px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: COLOR_TEXT_SECONDARY, fontSize: '14px', padding: '2px' }, children: "\\u2715" }))] }) }), _jsxs("div", { style: { flex: 1, overflowY: 'auto' }, children: [isSearchActive && (_jsxs(_Fragment, { children: [_jsxs("div", { style: { padding: '8px 12px', fontSize: '12px', color: COLOR_TEXT_SECONDARY, borderBottom: `1px solid ${COLOR_BORDER}`, backgroundColor: '#fafbfc' }, children: [searchResults.length, " result", searchResults.length !== 1 ? 's' : '', " for \u201C", searchQuery, "\u201D"] }), searchResults.length === 0 && !searchLoading && (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F50E), title: "No results", subtitle: "Try a different search term." })), searchResults.map((sr) => (_jsxs("div", { onClick: () => { setSelectedId(sr.conversation_id); }, role: "button", tabIndex: 0, onKeyDown: (e) => { if (e.key === 'Enter')
                                            setSelectedId(sr.conversation_id); }, style: {
                                            padding: '10px 14px',
                                            borderBottom: `1px solid ${COLOR_BORDER}`,
                                            backgroundColor: sr.conversation_id === selectedId ? '#f1f5ff' : COLOR_WHITE,
                                            cursor: 'pointer',
                                        }, onMouseEnter: (e) => { if (sr.conversation_id !== selectedId)
                                            e.currentTarget.style.backgroundColor = COLOR_LIGHT_GRAY; }, onMouseLeave: (e) => { e.currentTarget.style.backgroundColor = sr.conversation_id === selectedId ? '#f1f5ff' : COLOR_WHITE; }, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }, children: [_jsx("span", { style: { fontWeight: 600, fontSize: '13px', color: COLOR_TEXT }, children: sr.customer_name || 'Anonymous' }), _jsx(StatusBadge, { status: sr.status })] }), _jsx("div", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, lineHeight: '1.4', marginBottom: '2px' }, children: sr.snippet }), _jsxs("div", { style: { fontSize: '11px', color: COLOR_GRAY }, children: ["Matched in ", sr.matched_in, " \u00B7 ", sr.message_count, " msg", sr.message_count !== 1 ? 's' : ''] })] }, sr.conversation_id)))] })), !isSearchActive && (_jsxs(_Fragment, { children: [inboxLoading && conversations.length === 0 && (_jsx(LoadingSpinner, { text: "Loading conversations..." })), inboxError && conversations.length === 0 && (_jsx(ErrorBanner, { message: inboxError, onRetry: refetchInbox })), !inboxLoading && !inboxError && conversations.length === 0 && (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F4AC), title: "No conversations yet", subtitle: "Conversations will appear here when customers start chatting." })), conversations.map((conv) => (_jsx(ConversationItem, { conversation: conv, isSelected: conv.conversationId === selectedId, onClick: () => setSelectedId(conv.conversationId), memberMap: memberMap }, conv.conversationId)))] }))] })] }), _jsx("div", { style: {
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: COLOR_LIGHT_GRAY,
                }, children: !selectedId ? (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F4E8), title: "Select a conversation", subtitle: "Choose a conversation from the list to view the message transcript." })) : (_jsxs(_Fragment, { children: [_jsxs("div", { style: {
                                padding: '12px 16px',
                                borderBottom: `1px solid ${COLOR_BORDER}`,
                                backgroundColor: COLOR_WHITE,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                            }, children: [_jsxs("div", { children: [_jsx("span", { style: { fontWeight: 600, fontSize: '14px', color: COLOR_TEXT }, children: selectedConversation?.customerName || selectedConversation?.customerId || 'Anonymous' }), selectedConversation && (_jsxs("span", { style: { marginLeft: '10px', display: 'inline-flex', alignItems: 'center', gap: '6px' }, children: [_jsx(StatusBadge, { status: selectedConversation.status }), selectedConversation.escalationCategory && (_jsx("span", { style: {
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        color: COLOR_DANGER,
                                                        backgroundColor: COLOR_DANGER + '14',
                                                        padding: '2px 8px',
                                                        borderRadius: '4px',
                                                        textTransform: 'capitalize',
                                                    }, children: selectedConversation.escalationCategory.replace(/_/g, ' ') })), selectedConversation.assignedTo && (_jsx("span", { style: { fontSize: '11px', color: COLOR_TEXT_SECONDARY }, children: memberMap[selectedConversation.assignedTo] ?? selectedConversation.assignedTo })), _jsx(HelpTooltip, { text: "Conversation status, escalation category, and assigned agent.", docLink: "https://agentredcx.com/docs/admin-guide/conversations#conversation-list" })] }))] }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [selectedConversation?.status !== 'escalated' && selectedConversation?.status !== 'resolved' && (_jsx("button", { disabled: escalating, onClick: () => selectedId && handleEscalateClick(selectedId), style: {
                                                padding: '6px 12px',
                                                border: `1px solid ${COLOR_DANGER}`,
                                                borderRadius: BORDER_RADIUS,
                                                backgroundColor: COLOR_WHITE,
                                                color: COLOR_DANGER,
                                                fontSize: '12px',
                                                fontFamily: FONT_FAMILY,
                                                cursor: escalating ? 'not-allowed' : 'pointer',
                                                fontWeight: 500,
                                                opacity: escalating ? 0.7 : 1,
                                            }, children: escalating ? 'Escalating...' : 'Escalate' })), selectedConversation?.status !== 'resolved' && (_jsx("button", { disabled: resolving, onClick: () => selectedId && handleResolve(selectedId), style: {
                                                padding: '6px 12px',
                                                border: '1px solid #6f42c1',
                                                borderRadius: BORDER_RADIUS,
                                                backgroundColor: COLOR_WHITE,
                                                color: '#6f42c1',
                                                fontSize: '12px',
                                                fontFamily: FONT_FAMILY,
                                                cursor: resolving ? 'not-allowed' : 'pointer',
                                                fontWeight: 500,
                                                opacity: resolving ? 0.7 : 1,
                                            }, children: resolving ? 'Resolving...' : 'Mark resolved' })), _jsx("button", { onClick: () => setShowAssignModal(true), style: {
                                                padding: '6px 12px',
                                                border: `1px solid ${COLOR_BORDER}`,
                                                borderRadius: BORDER_RADIUS,
                                                backgroundColor: COLOR_WHITE,
                                                color: COLOR_TEXT,
                                                fontSize: '12px',
                                                fontFamily: FONT_FAMILY,
                                                cursor: 'pointer',
                                                fontWeight: 500,
                                            }, children: "Assign" }), _jsx("button", { onClick: () => setShowNoteModal(true), style: {
                                                padding: '6px 12px',
                                                border: `1px solid ${COLOR_BORDER}`,
                                                borderRadius: BORDER_RADIUS,
                                                backgroundColor: COLOR_WHITE,
                                                color: COLOR_TEXT,
                                                fontSize: '12px',
                                                fontFamily: FONT_FAMILY,
                                                cursor: 'pointer',
                                                fontWeight: 500,
                                            }, children: "Add note" }), (selectedConversation?.status === 'resolved' || selectedConversation?.status === 'ended') && (_jsx("button", { disabled: archiving, onClick: () => selectedId && handleArchive(selectedId), style: {
                                                padding: '6px 12px',
                                                border: `1px solid ${COLOR_GRAY}`,
                                                borderRadius: BORDER_RADIUS,
                                                backgroundColor: COLOR_WHITE,
                                                color: COLOR_GRAY,
                                                fontSize: '12px',
                                                fontFamily: FONT_FAMILY,
                                                cursor: archiving ? 'not-allowed' : 'pointer',
                                                fontWeight: 500,
                                                opacity: archiving ? 0.7 : 1,
                                            }, children: archiving ? 'Archiving...' : 'Archive' }))] })] }), _jsxs("div", { style: { flex: 1, overflowY: 'auto', padding: '16px' }, children: [messagesLoading && messages.length === 0 && (_jsx(LoadingSpinner, { text: "Loading messages..." })), messagesError && messages.length === 0 && (_jsx(ErrorBanner, { message: messagesError, onRetry: refetchMessages })), !messagesLoading && !messagesError && messages.length === 0 && (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F4DD), title: "No messages", subtitle: "This conversation has no messages yet." })), groupedMessages.map((group) => (_jsxs("div", { children: [_jsx("div", { style: {
                                                textAlign: 'center',
                                                margin: '16px 0 12px',
                                                position: 'relative',
                                            }, children: _jsx("span", { style: {
                                                    display: 'inline-block',
                                                    backgroundColor: COLOR_LIGHT_GRAY,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    fontSize: '11px',
                                                    fontWeight: 500,
                                                    padding: '2px 10px',
                                                    borderRadius: '10px',
                                                    border: `1px solid ${COLOR_BORDER}`,
                                                }, children: group.dateLabel }) }), group.messages.map((msg, idx) => (_jsx(MessageBubble, { message: msg }, msg.messageId ?? `msg-${idx}`)))] }, group.dateLabel))), _jsx("div", { ref: messagesEndRef })] }), _jsx(PipelineTracePanel, { trace: traceResult ?? null })] })) }), showAssignModal && selectedId && (_jsx(AssignModal, { conversationId: selectedId, members: teamMembers, onAssign: handleAssign, onClose: () => setShowAssignModal(false), assigning: assigning })), showNoteModal && selectedId && (_jsx(NoteModal, { conversationId: selectedId, apiFetch: apiFetch, onClose: () => setShowNoteModal(false), onSuccess: handleNoteSuccess })), showEscalateModal && selectedId && (_jsx(EscalateModal, { conversationId: selectedId, members: teamMembers, onEscalate: handleEscalateConfirm, onClose: () => setShowEscalateModal(false), escalating: escalating }))] }));
};
export default ConversationInbox;
//# sourceMappingURL=ConversationInbox.js.map