import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import { Paper, TextInput, SegmentedControl, Badge, Group, Stack, Text, ScrollArea, ActionIcon, Tooltip, Divider, Avatar, Box, Loader, useComputedColorScheme, Notification, Modal, Select, Button, } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useInboxConversations, useConversationMessages, useConversationTrace, useEscalateConversation, useResolveConversation, useArchiveConversation, useSearchConversations, useTeamMembers, } from '../../shared/hooks/index';
import { tokens } from '../../shared/theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const BRAND_RED = tokens.brand;
const HEADER_HEIGHT = 56;
const PAGE_PADDING = 16;
const STATUS_COLORS = {
    active: 'blue',
    ended: 'green',
    resolved: 'green',
    escalated: 'red',
    idle: 'yellow',
    timed_out: 'yellow',
    error: 'red',
};
const AVATAR_PALETTE = ['#ff3621', '#2563EB', '#059669', '#D97706', '#7C3AED', '#DB2777'];
// Escalation categories matching backend ESCALATION_CATEGORIES
const ESCALATION_CATEGORY_OPTIONS = [
    { value: 'service', label: 'Service' },
    { value: 'support', label: 'Support' },
    { value: 'sales', label: 'Sales' },
    { value: 'account', label: 'Account' },
    { value: 'technical_assistance', label: 'Technical Assistance' },
    { value: 'general_inquiry', label: 'General Inquiry' },
];
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function getInitials(name) {
    if (!name)
        return '?';
    return name
        .split(' ')
        .map((n) => n[0])
        .filter(Boolean)
        .join('')
        .toUpperCase()
        .slice(0, 2);
}
function avatarColor(name) {
    if (!name)
        return AVATAR_PALETTE[0];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length];
}
function timeAgo(dateString) {
    if (!dateString)
        return '--';
    const now = Date.now();
    const then = new Date(dateString).getTime();
    if (isNaN(then))
        return '--';
    const seconds = Math.floor((now - then) / 1000);
    if (seconds < 0)
        return 'just now';
    if (seconds < 60)
        return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60)
        return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24)
        return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
}
function formatTimestampString(ts) {
    if (!ts)
        return '';
    const d = new Date(ts);
    if (isNaN(d.getTime()))
        return '';
    return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}
// ---------------------------------------------------------------------------
// Inline SVG Icons
// ---------------------------------------------------------------------------
const SearchIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("circle", { cx: "11", cy: "11", r: "8" }), _jsx("line", { x1: "21", y1: "21", x2: "16.65", y2: "16.65" })] }));
const EscalateIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" }), _jsx("line", { x1: "12", y1: "9", x2: "12", y2: "13" }), _jsx("line", { x1: "12", y1: "17", x2: "12.01", y2: "17" })] }));
const CheckIcon = () => (_jsx("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: _jsx("polyline", { points: "20 6 9 17 4 12" }) }));
const ArchiveIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "21 8 21 21 3 21 3 8" }), _jsx("rect", { x: "1", y: "3", width: "22", height: "5" }), _jsx("line", { x1: "10", y1: "12", x2: "14", y2: "12" })] }));
const UnarchiveIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "21 8 21 21 3 21 3 8" }), _jsx("rect", { x: "1", y: "3", width: "22", height: "5" }), _jsx("polyline", { points: "12 15 12 9" }), _jsx("polyline", { points: "9 12 12 9 15 12" })] }));
// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------
/** Left panel: single conversation row */
function ConversationItem({ conversation, isSelected, onClick, selectedBgColor, hoverBgColor, }) {
    const displayName = conversation.customerName || conversation.conversationId?.slice(0, 12) || 'Session';
    const initials = getInitials(displayName);
    const color = avatarColor(displayName);
    const isUnread = conversation.status === 'active' || conversation.status === 'escalated';
    return (_jsx(Box, { onClick: onClick, style: {
            padding: '10px 12px',
            borderRadius: 8,
            cursor: 'pointer',
            background: isSelected ? selectedBgColor : 'transparent',
            borderLeft: isSelected ? `3px solid ${BRAND_RED}` : '3px solid transparent',
            transition: 'background 0.15s',
        }, onMouseEnter: (e) => {
            if (!isSelected)
                e.currentTarget.style.background = hoverBgColor;
        }, onMouseLeave: (e) => {
            if (!isSelected)
                e.currentTarget.style.background = 'transparent';
        }, children: _jsxs(Group, { gap: 10, align: "flex-start", wrap: "nowrap", children: [_jsx(Box, { style: { flexShrink: 0 }, children: _jsx(Avatar, { size: 38, radius: "xl", color: color, style: { background: color, color: '#fff', fontWeight: 600, fontSize: 14 }, children: initials }) }), _jsxs(Box, { style: { flex: 1, minWidth: 0 }, children: [_jsxs(Group, { justify: "space-between", wrap: "nowrap", gap: 4, children: [_jsx(Text, { size: "sm", fw: isUnread ? 700 : 500, truncate: true, style: { flex: 1 }, children: displayName }), _jsx(Text, { size: "xs", c: "dimmed", style: { flexShrink: 0 }, children: timeAgo(conversation.lastActivityAt ?? conversation.startedAt) })] }), _jsxs(Text, { size: "xs", c: "dimmed", truncate: true, mt: 2, children: [(conversation.messageCount ?? 0), " messages"] }), _jsxs(Group, { gap: 6, mt: 4, children: [_jsx(Badge, { size: "xs", variant: "light", color: STATUS_COLORS[conversation.status ?? ''] ?? 'gray', style: { textTransform: 'capitalize' }, children: conversation.status }), conversation.assignedTo && (_jsx(Text, { size: "xs", c: "dimmed", children: conversation.assignedTo })), isUnread && (_jsx(Box, { style: {
                                        marginLeft: 'auto',
                                        width: 8,
                                        height: 8,
                                        borderRadius: '50%',
                                        background: BRAND_RED,
                                        flexShrink: 0,
                                    } }))] })] })] }) }));
}
/** Center panel: single message bubble */
function MessageBubble({ message, agentBubbleBg, customerBubbleBg, }) {
    if (message.role === 'system') {
        return (_jsxs(Box, { style: { textAlign: 'center', padding: '8px 0' }, children: [_jsx(Text, { size: "xs", c: "dimmed", fs: "italic", children: message.content }), _jsx(Text, { size: "xs", c: "dimmed", mt: 2, children: formatTimestampString(message.timestamp) })] }));
    }
    const isAgent = message.role === 'ai';
    const senderName = isAgent
        ? 'Agent Red AI'
        : 'Customer';
    return (_jsx(Box, { style: {
            display: 'flex',
            justifyContent: isAgent ? 'flex-end' : 'flex-start',
            padding: '4px 0',
        }, children: _jsxs(Box, { style: { maxWidth: '75%' }, children: [isAgent ? (_jsxs(Group, { gap: 6, justify: "flex-end", mb: 2, children: [_jsx(Text, { size: "xs", c: "dimmed", children: senderName }), _jsx("img", { src: "/admin/standalone/icon-master.svg", alt: "Agent Red", style: { height: 16, width: 16, display: 'block', opacity: 0.85, borderRadius: 2 } })] })) : (_jsx(Text, { size: "xs", c: "dimmed", mb: 2, ta: "left", children: senderName })), _jsx(Paper, { p: "sm", radius: "lg", style: {
                        background: isAgent ? agentBubbleBg : customerBubbleBg,
                        borderBottomRightRadius: isAgent ? 4 : undefined,
                        borderBottomLeftRadius: !isAgent ? 4 : undefined,
                    }, children: _jsx(Text, { size: "sm", style: { whiteSpace: 'pre-wrap', lineHeight: 1.55 }, children: message.content }) }), _jsx(Group, { gap: 6, mt: 4, justify: isAgent ? 'flex-end' : 'flex-start', children: _jsx(Text, { size: "xs", c: "dimmed", children: formatTimestampString(message.timestamp) }) })] }) }));
}
// ---------------------------------------------------------------------------
// Escalation Modal (Mantine)
// ---------------------------------------------------------------------------
function EscalationModal({ opened, onClose, onConfirm, escalating, members, }) {
    const [category, setCategory] = useState(null);
    const [agentId, setAgentId] = useState(null);
    // All active team members — any member can be manually assigned.
    // Designated escalation agents for the selected category appear first.
    const agentOptions = useMemo(() => {
        if (!category)
            return [];
        const active = members.filter((m) => m.isActive);
        // Sort: designated agents for this category first, then others
        const sorted = [...active].sort((a, b) => {
            const aMatch = a.role === 'escalation_agent' &&
                (a.escalationCategories ?? []).includes(category)
                ? 0
                : 1;
            const bMatch = b.role === 'escalation_agent' &&
                (b.escalationCategories ?? []).includes(category)
                ? 0
                : 1;
            return aMatch - bMatch;
        });
        return sorted.map((m) => ({ value: m.id, label: m.displayName }));
    }, [members, category]);
    // Reset agent when category changes
    const handleCategoryChange = (value) => {
        setCategory(value);
        setAgentId(null);
    };
    // Reset on close
    const handleClose = () => {
        setCategory(null);
        setAgentId(null);
        onClose();
    };
    return (_jsx(Modal, { opened: opened, onClose: handleClose, title: "Escalate to human", size: "sm", centered: true, children: _jsxs(Stack, { gap: "md", children: [_jsx(Select, { label: "Category", placeholder: "Select category...", data: ESCALATION_CATEGORY_OPTIONS, value: category, onChange: handleCategoryChange, withAsterisk: true, allowDeselect: false }), _jsx(Select, { label: "Assign to agent", description: agentOptions.length === 0 && category
                        ? 'No team members available — add members via the Team page'
                        : 'Optional — leave empty for auto-assignment', placeholder: "Auto-assign (best available)", data: agentOptions, value: agentId, onChange: setAgentId, disabled: !category, clearable: true }), _jsxs(Group, { justify: "flex-end", mt: "sm", children: [_jsx(Button, { variant: "default", onClick: handleClose, children: "Cancel" }), _jsx(Button, { color: "red", disabled: !category, loading: escalating, onClick: async () => {
                                if (category) {
                                    await onConfirm({
                                        category,
                                        agentId: agentId || undefined,
                                    });
                                }
                            }, children: "Escalate" })] })] }) }));
}
// ---------------------------------------------------------------------------
// Pipeline Trace Visualization (SPEC-1532)
// ---------------------------------------------------------------------------
const TraceIcon = () => (_jsx("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: _jsx("polyline", { points: "22 12 18 12 15 21 9 3 6 12 2 12" }) }));
/** Stage colors for the pipeline trace visualization. */
const STAGE_COLORS = {
    'intent-classifier': '#2563EB',
    'knowledge-retrieval': '#059669',
    'response-generator': '#D97706',
    'critic-reviewer': '#7C3AED',
};
function PipelineTracePanel({ trace, loading, isDark, }) {
    if (loading) {
        return (_jsxs(Box, { p: "md", children: [_jsxs(Group, { gap: 6, mb: 8, children: [_jsx(TraceIcon, {}), _jsx(Text, { size: "xs", fw: 600, c: "dimmed", children: "Pipeline trace" })] }), _jsx(Box, { ta: "center", py: "sm", children: _jsx(Loader, { size: 14, color: "gray" }) })] }));
    }
    if (!trace) {
        return (_jsxs(Box, { p: "md", children: [_jsxs(Group, { gap: 6, mb: 8, children: [_jsx(TraceIcon, {}), _jsx(Text, { size: "xs", fw: 600, c: "dimmed", children: "Pipeline trace" })] }), _jsx(Text, { size: "xs", c: "dimmed", fs: "italic", children: "No pipeline trace available for this conversation." })] }));
    }
    const stages = trace.stages || [];
    const totalMs = trace.totalLatencyMs ?? 0;
    const barBg = isDark ? 'rgba(255,255,255,0.06)' : '#f1f3f5';
    return (_jsxs(Box, { p: "md", children: [_jsxs(Group, { gap: 6, mb: 8, children: [_jsx(TraceIcon, {}), _jsx(Text, { size: "xs", fw: 600, c: "dimmed", children: "Pipeline trace" })] }), _jsxs(Group, { gap: 8, mb: 8, children: [trace.intent && (_jsx(Badge, { size: "xs", variant: "light", color: "blue", children: trace.intent })), trace.criticPassed !== null && (_jsx(Badge, { size: "xs", variant: "light", color: trace.criticPassed ? 'green' : 'red', children: trace.criticPassed ? 'Approved' : 'Retracted' })), totalMs > 0 && (_jsxs(Text, { size: "xs", c: "dimmed", ff: "monospace", children: [totalMs, "ms"] }))] }), _jsx(Stack, { gap: 4, children: stages.map((s, idx) => {
                    const color = STAGE_COLORS[s.stage] ?? '#868e96';
                    const widthPct = totalMs > 0 ? Math.max(4, (s.elapsedMs / totalMs) * 100) : 25;
                    const label = s.stage.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
                    return (_jsxs(Box, { children: [_jsxs(Group, { gap: 6, justify: "space-between", wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 90, flexShrink: 0, textTransform: 'capitalize' }, children: label }), _jsxs(Text, { size: "xs", ff: "monospace", c: "dimmed", style: { flexShrink: 0 }, children: [s.elapsedMs, "ms"] })] }), _jsx(Box, { mt: 2, style: {
                                    height: 6,
                                    borderRadius: 3,
                                    background: barBg,
                                    overflow: 'hidden',
                                }, children: _jsx(Box, { style: {
                                        height: '100%',
                                        width: `${widthPct}%`,
                                        borderRadius: 3,
                                        background: color,
                                        opacity: s.succeeded ? 1 : 0.4,
                                        transition: 'width 0.3s ease',
                                    } }) })] }, s.stage || idx));
                }) }), _jsxs(Stack, { gap: 4, mt: 8, children: [trace.modelUsed && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 50, flexShrink: 0 }, children: "Model" }), _jsx(Text, { size: "xs", ff: "monospace", children: trace.modelUsed })] })), trace.traceId && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 50, flexShrink: 0 }, children: "Trace" }), _jsxs(Text, { size: "xs", ff: "monospace", style: { opacity: 0.7 }, children: [trace.traceId.slice(0, 16), "..."] })] }))] })] }));
}
// ---------------------------------------------------------------------------
// Main Inbox Page
// ---------------------------------------------------------------------------
export function InboxPage() {
    const { apiFetch } = useAppContext();
    const computedColorScheme = useComputedColorScheme('dark');
    const isDark = computedColorScheme === 'dark';
    // ---- State ----
    const [selectedId, setSelectedId] = useState('');
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');
    const [notification, setNotification] = useState(null);
    const [showEscalateModal, setShowEscalateModal] = useState(false);
    const messageEndRef = useRef(null);
    const searchTimerRef = useRef(null);
    // ---- API hooks ----
    const isArchivedTab = filter === 'archived';
    const convResult = useInboxConversations(apiFetch, isArchivedTab ? 'only' : undefined);
    const conversations = convResult.data?.conversations ?? [];
    const msgResult = useConversationMessages(apiFetch, selectedId);
    const messages = msgResult.data?.messages ?? [];
    const { escalate, loading: escalating } = useEscalateConversation(apiFetch);
    const { resolve, loading: resolving } = useResolveConversation(apiFetch);
    const { archive, unarchive, loading: archiving } = useArchiveConversation(apiFetch);
    const { search: searchApi, clearSearch, results: searchResults, loading: searching } = useSearchConversations(apiFetch);
    const traceResult = useConversationTrace(apiFetch, selectedId);
    const teamResult = useTeamMembers(apiFetch);
    const memberMap = React.useMemo(() => {
        const map = {};
        for (const m of (teamResult.data?.members ?? [])) {
            map[m.id] = m.displayName;
        }
        return map;
    }, [teamResult.data]);
    // Auto-select first conversation when list loads
    useEffect(() => {
        if (!selectedId && conversations.length > 0) {
            setSelectedId(conversations[0].conversationId);
        }
    }, [conversations, selectedId]);
    // Scroll to bottom of messages when conversation changes
    useEffect(() => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [selectedId, messages.length]);
    // Auto-dismiss notification after 4 seconds
    useEffect(() => {
        if (!notification)
            return;
        const t = setTimeout(() => setNotification(null), 4000);
        return () => clearTimeout(t);
    }, [notification]);
    // ---- Dark mode colors (Mazel design revision) ----
    const panelBg = isDark ? tokens.chrome : '#fff';
    const centerBg = isDark ? tokens.chrome : '#fafafa';
    const borderColor = isDark ? tokens.border : 'var(--mantine-color-gray-2)';
    const hoverBg = isDark ? 'rgba(255,255,255,0.04)' : '#f8f9fa';
    const selectedBg = isDark ? tokens.surface : '#FFF1F2';
    const bubbleAgentBg = isDark ? tokens.surface : '#f1f3f5';
    const bubbleCustomerBg = isDark ? tokens.surface : '#f1f3f5';
    // ---- Debounced backend search ----
    const handleSearchChange = useCallback((value) => {
        setSearch(value);
        if (searchTimerRef.current)
            clearTimeout(searchTimerRef.current);
        if (!value.trim()) {
            clearSearch();
            return;
        }
        searchTimerRef.current = setTimeout(() => {
            searchApi(value.trim());
        }, 350);
    }, [searchApi, clearSearch]);
    // ---- Escalate / Resolve handlers ----
    const handleEscalateClick = useCallback(() => {
        if (!selectedId || escalating)
            return;
        setShowEscalateModal(true);
    }, [selectedId, escalating]);
    const handleEscalateConfirm = useCallback(async (opts) => {
        if (!selectedId)
            return;
        try {
            await escalate(selectedId, opts);
            setNotification({ message: 'Conversation escalated to human agent.', color: 'orange' });
            setShowEscalateModal(false);
            // Brief delay before refetch to allow Cosmos read-after-write propagation
            setTimeout(() => convResult.refetch(), 500);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Escalation failed';
            setNotification({ message: msg, color: 'red' });
        }
    }, [selectedId, escalate, convResult]);
    const handleResolve = useCallback(async () => {
        if (!selectedId || resolving)
            return;
        try {
            await resolve(selectedId);
            setNotification({ message: 'Conversation marked as resolved.', color: 'green' });
            setTimeout(() => convResult.refetch(), 500);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Resolve failed';
            setNotification({ message: msg, color: 'red' });
        }
    }, [selectedId, resolving, resolve, convResult]);
    const handleArchive = useCallback(async () => {
        if (!selectedId || archiving)
            return;
        try {
            await archive(selectedId);
            setNotification({ message: 'Conversation archived.', color: 'gray' });
            setTimeout(() => convResult.refetch(), 500);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Archive failed';
            setNotification({ message: msg, color: 'red' });
        }
    }, [selectedId, archiving, archive, convResult]);
    const handleUnarchive = useCallback(async () => {
        if (!selectedId || archiving)
            return;
        try {
            await unarchive(selectedId);
            setNotification({ message: 'Conversation unarchived.', color: 'blue' });
            setTimeout(() => convResult.refetch(), 500);
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Unarchive failed';
            setNotification({ message: msg, color: 'red' });
        }
    }, [selectedId, archiving, unarchive, convResult]);
    // ---- Filtering (status filter applied to conversation list; search uses backend) ----
    const isSearchActive = searchResults !== null;
    const filteredConversations = isSearchActive
        ? [] // When searching, we show searchResults instead
        : conversations.filter((c) => {
            // "archived" tab: API already returns only archived conversations
            if (isArchivedTab)
                return true;
            if (filter !== 'all' && c.status !== filter)
                return false;
            return true;
        });
    // Clear reader pane when search/filter yields no results (Issue 3a)
    useEffect(() => {
        const hasResults = isSearchActive ? (searchResults?.length ?? 0) > 0 : filteredConversations.length > 0;
        if (!hasResults && (search || filter !== 'all')) {
            setSelectedId('');
        }
    }, [isSearchActive, searchResults?.length, filteredConversations.length, search, filter]);
    // ---- Counts per filter ----
    const counts = {
        all: conversations.length,
        active: conversations.filter((c) => c.status === 'active').length,
        escalated: conversations.filter((c) => c.status === 'escalated').length,
        resolved: conversations.filter((c) => c.status === 'resolved').length,
    };
    // ---- Selected conversation ----
    // Look up in the inbox list first; fall back to building a partial object
    // from the search results so clicking a search hit always populates the
    // center + right panels (the search may return conversations beyond the
    // first inbox page).
    const selectedConversation = (() => {
        const fromInbox = conversations.find((c) => c.conversationId === selectedId);
        if (fromInbox)
            return fromInbox;
        if (isSearchActive && searchResults) {
            const sr = searchResults.find((r) => r.conversation_id === selectedId);
            if (sr) {
                return {
                    conversationId: sr.conversation_id,
                    customerId: sr.customer_id,
                    customerName: sr.customer_name,
                    status: sr.status,
                    assignedTo: null,
                    messageCount: sr.message_count,
                    turnCount: 0,
                    startedAt: sr.started_at,
                    endedAt: null,
                    lastActivityAt: sr.last_activity_at,
                    isBillable: false,
                    agentsInvoked: [],
                    modelUsed: null,
                    criticPassed: null,
                    escalationCategory: null,
                    archivedAt: null,
                    customerVerified: false,
                    identityEmail: null,
                    pipelineTrace: null,
                };
            }
        }
        return null;
    })();
    const selectedDisplayName = selectedConversation?.customerName || selectedConversation?.conversationId?.slice(0, 12) || 'Session';
    const layoutHeight = `calc(100vh - ${HEADER_HEIGHT}px - ${PAGE_PADDING * 2}px)`;
    return (_jsxs(Box, { style: {
            display: 'flex',
            gap: 0,
            height: layoutHeight,
            marginTop: -PAGE_PADDING,
            marginLeft: -PAGE_PADDING,
            marginRight: -PAGE_PADDING,
            marginBottom: -PAGE_PADDING,
        }, children: [_jsxs(Box, { style: {
                    width: 320,
                    flexShrink: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    borderRight: `1px solid ${borderColor}`,
                    background: panelBg,
                }, children: [_jsx(Box, { p: "sm", pb: 0, children: _jsx(TextInput, { placeholder: "Search conversations...", leftSection: searching ? _jsx(Loader, { size: 14, color: "gray" }) : _jsx(SearchIcon, {}), size: "sm", value: search, onChange: (e) => handleSearchChange(e.currentTarget.value), styles: {
                                input: { borderColor: isDark ? tokens.border : 'var(--mantine-color-gray-3)' },
                            } }) }), _jsx(Box, { px: 6, py: "xs", children: _jsx(SegmentedControl, { value: filter, onChange: setFilter, size: "xs", fullWidth: true, data: [
                                { label: `All (${counts.all})`, value: 'all' },
                                { label: `Active (${counts.active})`, value: 'active' },
                                { label: `Esc (${counts.escalated})`, value: 'escalated' },
                                { label: `Resolved (${counts.resolved})`, value: 'resolved' },
                                { label: 'Archived', value: 'archived' },
                            ], styles: {
                                root: { background: isDark ? 'rgba(255,255,255,0.04)' : 'var(--mantine-color-gray-0)' },
                                label: { padding: '4px 6px', fontSize: 11 },
                            } }) }), _jsx(Divider, {}), _jsx(ScrollArea, { style: { flex: 1 }, type: "auto", offsetScrollbars: true, children: _jsxs(Stack, { gap: 0, p: 4, children: [convResult.loading && conversations.length === 0 && (_jsxs(Box, { py: "xl", ta: "center", children: [_jsx(Loader, { size: "sm", color: "gray" }), _jsx(Text, { size: "xs", c: "dimmed", mt: "sm", children: "Loading conversations..." })] })), convResult.error && (_jsxs(Box, { py: "xl", px: "sm", children: [_jsx(Text, { size: "sm", c: "red", ta: "center", children: "Failed to load conversations" }), _jsx(Text, { size: "xs", c: "dimmed", ta: "center", mt: 4, children: convResult.error })] })), !convResult.loading && !convResult.error && !isSearchActive && filteredConversations.length === 0 && (_jsxs(Box, { py: 40, px: "sm", ta: "center", children: [_jsx("svg", { width: "48", height: "48", viewBox: "0 0 24 24", fill: "none", stroke: isDark ? tokens.textTertiary : '#adb5bd', strokeWidth: "1.5", strokeLinecap: "round", strokeLinejoin: "round", style: { margin: '0 auto 12px', display: 'block', opacity: 0.7 }, children: _jsx("path", { d: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" }) }), _jsx(Text, { size: "sm", fw: 500, c: "dimmed", mb: 4, children: filter !== 'all' ? 'No matching conversations' : 'No conversations yet' }), _jsx(Text, { size: "xs", c: "dimmed", children: filter !== 'all'
                                                ? 'Try adjusting your filter.'
                                                : 'Conversations will appear here once customers start chatting with your AI agent.' })] })), isSearchActive && !searching && searchResults.length === 0 && (_jsxs(Box, { py: 40, px: "sm", ta: "center", children: [_jsx(Text, { size: "sm", fw: 500, c: "dimmed", mb: 4, children: "No matching conversations" }), _jsx(Text, { size: "xs", c: "dimmed", children: "Try adjusting your search or filter." })] })), isSearchActive && searchResults.map((sr) => (_jsx(Box, { onClick: () => setSelectedId(sr.conversation_id), style: {
                                        padding: '10px 12px',
                                        borderRadius: 8,
                                        cursor: 'pointer',
                                        background: sr.conversation_id === selectedId ? selectedBg : 'transparent',
                                        borderLeft: sr.conversation_id === selectedId ? `3px solid ${BRAND_RED}` : '3px solid transparent',
                                        transition: 'background 0.15s',
                                    }, onMouseEnter: (e) => {
                                        if (sr.conversation_id !== selectedId)
                                            e.currentTarget.style.background = hoverBg;
                                    }, onMouseLeave: (e) => {
                                        if (sr.conversation_id !== selectedId)
                                            e.currentTarget.style.background = 'transparent';
                                    }, children: _jsxs(Group, { gap: 10, align: "flex-start", wrap: "nowrap", children: [_jsx(Box, { style: { flexShrink: 0 }, children: _jsx(Avatar, { size: 38, radius: "xl", style: { background: avatarColor(sr.customer_name ?? sr.conversation_id), color: '#fff', fontWeight: 600, fontSize: 14 }, children: getInitials(sr.customer_name ?? sr.conversation_id?.slice(0, 8)) }) }), _jsxs(Box, { style: { flex: 1, minWidth: 0 }, children: [_jsxs(Group, { justify: "space-between", wrap: "nowrap", gap: 4, children: [_jsx(Text, { size: "sm", fw: 600, truncate: true, style: { flex: 1 }, children: sr.customer_name || sr.conversation_id?.slice(0, 12) || 'Session' }), _jsx(Text, { size: "xs", c: "dimmed", style: { flexShrink: 0 }, children: timeAgo(sr.last_activity_at ?? sr.started_at) })] }), _jsx(Text, { size: "xs", c: "dimmed", truncate: true, mt: 2, children: sr.snippet }), _jsxs(Group, { gap: 6, mt: 4, children: [_jsx(Badge, { size: "xs", variant: "light", color: STATUS_COLORS[sr.status ?? ''] ?? 'gray', style: { textTransform: 'capitalize' }, children: sr.status }), _jsx(Badge, { size: "xs", variant: "outline", color: "gray", children: sr.matched_in }), _jsxs(Text, { size: "xs", c: "dimmed", children: [sr.message_count, " msg"] })] })] })] }) }, sr.conversation_id))), !isSearchActive && filteredConversations.map((conv) => (_jsx(ConversationItem, { conversation: conv, isSelected: conv.conversationId === selectedId, onClick: () => setSelectedId(conv.conversationId), selectedBgColor: selectedBg, hoverBgColor: hoverBg }, conv.conversationId)))] }) })] }), _jsxs(Box, { style: {
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    background: centerBg,
                    minWidth: 0,
                }, children: [_jsx(Box, { px: "md", py: "sm", style: {
                            background: panelBg,
                            borderBottom: `1px solid ${borderColor}`,
                        }, children: selectedConversation ? (_jsxs(Group, { justify: "space-between", wrap: "nowrap", children: [_jsxs(Box, { style: { minWidth: 0 }, children: [_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "md", fw: 600, truncate: true, children: selectedDisplayName }), _jsx(Badge, { size: "sm", variant: "light", color: STATUS_COLORS[selectedConversation.status ?? ''] ?? 'gray', style: { textTransform: 'capitalize' }, children: selectedConversation.status })] }), _jsxs(Text, { size: "xs", c: "dimmed", mt: 2, truncate: true, children: [(selectedConversation.messageCount ?? 0), " messages", selectedConversation.assignedTo && (_jsxs(_Fragment, { children: [" \u00B7 Assigned to ", selectedConversation.assignedTo] }))] })] }), _jsxs(Group, { gap: 4, style: { flexShrink: 0 }, children: [selectedConversation.status !== 'escalated' && selectedConversation.status !== 'resolved' && (_jsx(Tooltip, { label: "Escalate to human", children: _jsx(ActionIcon, { variant: "subtle", color: "orange", size: "md", onClick: handleEscalateClick, loading: escalating, disabled: escalating || resolving, children: _jsx(EscalateIcon, {}) }) })), selectedConversation.status !== 'resolved' && (_jsx(Tooltip, { label: "Resolve conversation", children: _jsx(ActionIcon, { variant: "subtle", color: "green", size: "md", onClick: handleResolve, loading: resolving, disabled: escalating || resolving, children: _jsx(CheckIcon, {}) }) })), !selectedConversation.archivedAt && (selectedConversation.status === 'resolved' || selectedConversation.status === 'timed_out') && (_jsx(Tooltip, { label: "Archive conversation", children: _jsx(ActionIcon, { variant: "subtle", color: "gray", size: "md", onClick: handleArchive, loading: archiving, disabled: archiving, children: _jsx(ArchiveIcon, {}) }) })), selectedConversation.archivedAt && (_jsx(Tooltip, { label: "Unarchive conversation", children: _jsx(ActionIcon, { variant: "subtle", color: "blue", size: "md", onClick: handleUnarchive, loading: archiving, disabled: archiving, children: _jsx(UnarchiveIcon, {}) }) }))] })] })) : (_jsx(Text, { size: "sm", c: "dimmed", children: "Select a conversation" })) }), _jsx(ScrollArea, { style: { flex: 1 }, type: "auto", offsetScrollbars: true, children: _jsxs(Box, { px: "md", py: "sm", children: [!selectedId && (_jsx(Box, { style: { textAlign: 'center', paddingTop: 80 }, children: _jsx(Text, { c: "dimmed", size: "sm", children: "Select a conversation from the list to view messages." }) })), selectedId && msgResult.loading && messages.length === 0 && (_jsxs(Box, { style: { textAlign: 'center', paddingTop: 80 }, children: [_jsx(Loader, { size: "sm", color: "gray" }), _jsx(Text, { c: "dimmed", size: "xs", mt: "sm", children: "Loading messages..." })] })), selectedId && msgResult.error && (_jsxs(Box, { style: { textAlign: 'center', paddingTop: 80 }, children: [_jsx(Text, { c: "red", size: "sm", children: "Failed to load messages" }), _jsx(Text, { c: "dimmed", size: "xs", mt: 4, children: msgResult.error })] })), selectedId && !msgResult.loading && !msgResult.error && messages.length === 0 && (_jsx(Box, { style: { textAlign: 'center', paddingTop: 80 }, children: _jsx(Text, { c: "dimmed", size: "sm", children: "No messages in this conversation yet." }) })), messages.length > 0 && (_jsxs(Stack, { gap: 8, children: [messages.map((msg, idx) => (_jsx(MessageBubble, { message: msg, agentBubbleBg: bubbleAgentBg, customerBubbleBg: bubbleCustomerBg }, msg.messageId ?? `msg-${idx}`))), _jsx("div", { ref: messageEndRef })] }))] }) })] }), _jsx(Box, { style: {
                    width: 320,
                    flexShrink: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    borderLeft: `1px solid ${borderColor}`,
                    background: panelBg,
                }, children: _jsx(ScrollArea, { style: { flex: 1 }, type: "auto", offsetScrollbars: true, children: _jsx(Stack, { gap: 0, children: selectedConversation ? (_jsxs(_Fragment, { children: [_jsxs(Box, { p: "md", style: { textAlign: 'center' }, children: [_jsx(Avatar, { size: 64, radius: "xl", mx: "auto", style: {
                                                background: avatarColor(selectedDisplayName),
                                                color: '#fff',
                                                fontWeight: 700,
                                                fontSize: 22,
                                            }, children: getInitials(selectedDisplayName) }), _jsx(Text, { size: "md", fw: 600, mt: 8, children: selectedDisplayName }), selectedConversation.customerId && (_jsxs(Text, { size: "xs", c: "dimmed", mt: 2, children: ["ID: ", selectedConversation.customerId] })), _jsx(Badge, { size: "xs", variant: "light", color: STATUS_COLORS[selectedConversation.status ?? ''] ?? 'gray', mt: 6, style: { textTransform: 'capitalize' }, children: selectedConversation.status })] }), _jsx(Divider, {}), _jsxs(Box, { p: "md", children: [_jsx(Text, { size: "xs", fw: 600, c: "dimmed", mb: 8, children: "Conversation info" }), _jsxs(Stack, { gap: 6, children: [_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Messages" }), _jsx(Text, { size: "sm", children: selectedConversation.messageCount ?? 0 })] }), _jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Started" }), _jsx(Text, { size: "sm", children: selectedConversation.startedAt
                                                                ? new Date(selectedConversation.startedAt).toLocaleString('en-US', {
                                                                    month: 'short',
                                                                    day: 'numeric',
                                                                    hour: 'numeric',
                                                                    minute: '2-digit',
                                                                    hour12: true,
                                                                })
                                                                : '--' })] }), _jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Last activity" }), _jsx(Text, { size: "sm", children: selectedConversation.lastActivityAt
                                                                ? timeAgo(selectedConversation.lastActivityAt)
                                                                : '--' })] }), selectedConversation.assignedTo && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Assigned to" }), _jsx(Text, { size: "sm", children: memberMap[selectedConversation.assignedTo] || selectedConversation.assignedTo })] })), selectedConversation.escalationCategory && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Category" }), _jsx(Badge, { size: "xs", variant: "light", color: "blue", children: selectedConversation.escalationCategory.replace(/_/g, ' ') })] })), selectedConversation.status === 'escalated' && (_jsx(Badge, { size: "xs", variant: "filled", color: "red", mt: 4, children: "Escalated" })), selectedConversation.archivedAt && (_jsxs(Group, { gap: 8, wrap: "nowrap", mt: 4, children: [_jsx(Badge, { size: "xs", variant: "light", color: "gray", children: "Archived" }), _jsx(Text, { size: "xs", c: "dimmed", children: new Date(selectedConversation.archivedAt).toLocaleDateString('en-US', {
                                                                month: 'short',
                                                                day: 'numeric',
                                                                year: 'numeric',
                                                            }) })] }))] })] }), _jsx(Divider, {}), _jsxs(Box, { p: "md", children: [_jsx(Text, { size: "xs", fw: 600, c: "dimmed", mb: 8, children: "Customer profile" }), _jsxs(Stack, { gap: 6, children: [selectedConversation.customerName && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Name" }), _jsx(Text, { size: "sm", style: { overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0 }, children: selectedConversation.customerName })] })), selectedConversation.identityEmail && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Email" }), _jsx(Text, { size: "sm", style: { overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0 }, children: selectedConversation.identityEmail })] })), selectedConversation.customerId && (_jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Customer ID" }), _jsx(Text, { size: "sm", ff: "monospace", style: { fontSize: 11, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', minWidth: 0 }, children: selectedConversation.customerId })] })), _jsxs(Group, { gap: 8, wrap: "nowrap", children: [_jsx(Text, { size: "xs", c: "dimmed", style: { width: 80, flexShrink: 0 }, children: "Verified" }), _jsx(Badge, { size: "xs", variant: "light", color: selectedConversation.customerVerified ? 'green' : 'gray', children: selectedConversation.customerVerified ? 'Verified' : 'Anonymous' })] }), !selectedConversation.customerName && !selectedConversation.customerId && !selectedConversation.identityEmail && (_jsx(Text, { size: "xs", c: "dimmed", fs: "italic", children: "No customer identity collected in this conversation." }))] })] }), _jsx(Divider, {}), _jsx(PipelineTracePanel, { trace: traceResult.data ?? null, loading: traceResult.loading, isDark: isDark })] })) : (_jsx(Box, { p: "md", children: _jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "xl", children: "Select a conversation to view details." }) })) }) }) }), _jsx(EscalationModal, { opened: showEscalateModal, onClose: () => setShowEscalateModal(false), onConfirm: handleEscalateConfirm, escalating: escalating, members: (teamResult.data?.members ?? []) }), notification && (_jsx(Notification, { color: notification.color, onClose: () => setNotification(null), withCloseButton: true, style: {
                    position: 'fixed',
                    bottom: 24,
                    right: 24,
                    zIndex: 1000,
                    maxWidth: 360,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                }, children: notification.message }))] }));
}
//# sourceMappingURL=Inbox.js.map