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

import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import type {
  BaseComponentProps,
  InboxConversation,
  ConversationMessage,
  TeamMember,
  PipelineTrace,
  PipelineStage,
} from './types';
import {
  usePolling,
  useConversationMessages,
  useAssignConversation,
  useEscalateConversation,
  useResolveConversation,
  useArchiveConversation,
  useTeamMembers,
  useSearchConversations,
  useConversationTrace,
} from './hooks';
import type { SearchResult } from './hooks';
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

const STATUS_COLORS: Record<string, string> = {
  active: COLOR_SUCCESS,
  ended: COLOR_GRAY,
  escalated: COLOR_DANGER,
  resolved: '#6f42c1',
  timed_out: '#e36209',
  error: COLOR_DANGER,
};

const STATUS_LABELS: Record<string, string> = {
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

function formatRelativeTime(isoString: string | null): string {
  if (!isoString) return '--';
  const date = new Date(isoString);
  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return 'just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}h ago`;
  const diffDay = Math.floor(diffHour / 24);
  if (diffDay < 30) return `${diffDay}d ago`;
  return date.toLocaleDateString();
}

function formatTimestamp(ts: string | null): string {
  if (!ts) return '--';
  const d = new Date(ts);
  if (isNaN(d.getTime())) return '--';
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDateHeader(ts: string | null): string {
  if (!ts) return 'Unknown';
  const d = new Date(ts);
  if (isNaN(d.getTime())) return 'Unknown';
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return d.toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' });
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const StatusBadge: React.FC<{ status: string | null }> = ({ status }) => {
  const key = status ?? 'active';
  const color = STATUS_COLORS[key] ?? COLOR_GRAY;
  const label = STATUS_LABELS[key] ?? (status ?? 'Unknown');
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        fontSize: '12px',
        color,
        fontWeight: 500,
      }}
    >
      <span
        style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: color,
          display: 'inline-block',
          flexShrink: 0,
        }}
      />
      {label}
    </span>
  );
};

interface ConversationItemProps {
  conversation: InboxConversation;
  isSelected: boolean;
  onClick: () => void;
  memberMap?: Record<string, string>;
}

const ConversationItem: React.FC<ConversationItemProps> = ({ conversation, isSelected, onClick, memberMap }) => (
  <div
    onClick={onClick}
    role="button"
    tabIndex={0}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick();
      }
    }}
    style={{
      padding: '12px 16px',
      borderBottom: `1px solid ${COLOR_BORDER}`,
      backgroundColor: isSelected ? '#f1f5ff' : COLOR_WHITE,
      cursor: 'pointer',
      transition: 'background-color 0.15s ease',
    }}
    onMouseEnter={(e) => {
      if (!isSelected) (e.currentTarget as HTMLElement).style.backgroundColor = COLOR_LIGHT_GRAY;
    }}
    onMouseLeave={(e) => {
      (e.currentTarget as HTMLElement).style.backgroundColor = isSelected ? '#f1f5ff' : COLOR_WHITE;
    }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
      <span style={{ fontWeight: 600, fontSize: '14px', color: COLOR_TEXT }}>
        {conversation.customerName || conversation.customerId || 'Anonymous'}
      </span>
      <span style={{ fontSize: '11px', color: COLOR_TEXT_SECONDARY }}>
        {formatRelativeTime(conversation.lastActivityAt ?? conversation.startedAt)}
      </span>
    </div>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <StatusBadge status={conversation.status} />
      <span style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
        {conversation.isBillable && (
          <span style={{ display: 'inline-flex', alignItems: 'center' }}>
            <span
              style={{
                fontSize: '10px',
                fontWeight: 600,
                color: COLOR_SUCCESS,
                backgroundColor: COLOR_SUCCESS + '18',
                padding: '1px 5px',
                borderRadius: '4px',
              }}
            >
              Billable
            </span>
            <HelpTooltip text="Whether this conversation counts toward your monthly allowance." docLink="https://agentredcx.com/docs/billing/billable-conversation-spec" />
          </span>
        )}
        {conversation.messageCount} message{conversation.messageCount !== 1 ? 's' : ''}
      </span>
    </div>
    {(conversation.assignedTo || conversation.escalationCategory) && (
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px', flexWrap: 'wrap' }}>
        {conversation.escalationCategory && (
          <span
            style={{
              fontSize: '10px',
              fontWeight: 600,
              color: COLOR_DANGER,
              backgroundColor: COLOR_DANGER + '14',
              padding: '1px 6px',
              borderRadius: '4px',
              textTransform: 'capitalize',
            }}
          >
            {conversation.escalationCategory.replace(/_/g, ' ')}
          </span>
        )}
        {conversation.assignedTo && (
          <span style={{ fontSize: '11px', color: COLOR_TEXT_SECONDARY }}>
            Assigned to: {memberMap?.[conversation.assignedTo] ?? conversation.assignedTo}
          </span>
        )}
      </div>
    )}
  </div>
);

interface MessageBubbleProps {
  message: ConversationMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isCustomer = message.role === 'customer';
  const isSystem = message.role === 'system';

  const bubbleStyle: React.CSSProperties = isSystem
    ? {
        backgroundColor: COLOR_LIGHT_GRAY,
        color: COLOR_TEXT_SECONDARY,
        fontSize: '12px',
        fontStyle: 'italic',
        padding: '8px 12px',
        borderRadius: BORDER_RADIUS,
        maxWidth: '85%',
        margin: '4px auto',
        textAlign: 'center' as const,
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

  return (
    <div style={{ marginBottom: '8px' }}>
      {!isSystem && (
        <div
          style={{
            fontSize: '11px',
            color: COLOR_TEXT_SECONDARY,
            marginBottom: '2px',
            textAlign: isCustomer ? ('left' as const) : ('right' as const),
          }}
        >
          {isCustomer ? 'Customer' : 'Agent Red AI'} {' '}
          <span style={{ fontFamily: FONT_MONO, fontSize: '10px' }}>
            {formatTimestamp(message.timestamp)}
          </span>
        </div>
      )}
      <div style={bubbleStyle}>
        {message.content}
      </div>
    </div>
  );
};

interface AssignModalProps {
  conversationId: string;
  members: TeamMember[];
  onAssign: (conversationId: string, agentId: string) => Promise<void>;
  onClose: () => void;
  assigning: boolean;
}

const AssignModal: React.FC<AssignModalProps> = ({ conversationId, members, onAssign, onClose, assigning }) => {
  const [selectedAgent, setSelectedAgent] = useState('');

  return (
    <div
      style={{
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
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: COLOR_WHITE,
          borderRadius: BORDER_RADIUS,
          padding: '24px',
          width: '380px',
          maxWidth: '90vw',
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }}>
          Assign conversation
          <HelpTooltip text="Assign this conversation to a team member for follow-up." docLink="https://agentredcx.com/docs/admin-guide/conversations#conversation-detail" />
        </h3>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          style={{
            width: '100%',
            padding: '8px 12px',
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            fontSize: '14px',
            fontFamily: FONT_FAMILY,
            backgroundColor: COLOR_WHITE,
            marginBottom: '16px',
          }}
        >
          <option value="">Select team member...</option>
          {members
            .filter((m) => m.isActive)
            .map((m) => (
              <option key={m.id} value={m.id}>
                {m.displayName} ({m.role})
              </option>
            ))}
        </select>
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              border: `1px solid ${COLOR_BORDER}`,
              borderRadius: BORDER_RADIUS,
              backgroundColor: COLOR_WHITE,
              color: COLOR_TEXT,
              fontSize: '13px',
              fontFamily: FONT_FAMILY,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            disabled={!selectedAgent || assigning}
            onClick={async () => {
              if (selectedAgent) {
                await onAssign(conversationId, selectedAgent);
                onClose();
              }
            }}
            style={{
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
            }}
          >
            {assigning ? 'Assigning...' : 'Assign'}
          </button>
        </div>
      </div>
    </div>
  );
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

interface EscalateModalProps {
  conversationId: string;
  members: TeamMember[];
  onEscalate: (conversationId: string, opts: { category: string; agentId?: string }) => Promise<void>;
  onClose: () => void;
  escalating: boolean;
}

const EscalateModal: React.FC<EscalateModalProps> = ({ conversationId, members, onEscalate, onClose, escalating }) => {
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('');

  // All active team members — any member can be manually assigned.
  // Designated escalation agents for the selected category appear first.
  const availableAgents = useMemo(() => {
    if (!selectedCategory) return [];
    const active = members.filter((m) => m.isActive);
    // Sort: designated agents for this category first, then others
    return active.sort((a, b) => {
      const aMatch =
        a.role === 'escalation_agent' &&
        (a.escalationCategories ?? []).includes(selectedCategory)
          ? 0
          : 1;
      const bMatch =
        b.role === 'escalation_agent' &&
        (b.escalationCategories ?? []).includes(selectedCategory)
          ? 0
          : 1;
      return aMatch - bMatch;
    });
  }, [members, selectedCategory]);

  // Reset agent when category changes
  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
    setSelectedAgent('');
  };

  return (
    <div
      style={{
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
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: COLOR_WHITE,
          borderRadius: BORDER_RADIUS,
          padding: '24px',
          width: '420px',
          maxWidth: '90vw',
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }}>
          Escalate to human
          <HelpTooltip text="Choose a department and optionally assign to a specific agent." docLink="https://agentredcx.com/docs/admin-guide/conversations#escalation" />
        </h3>

        {/* Category selection */}
        <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: COLOR_TEXT, marginBottom: '6px' }}>
          Category <span style={{ color: COLOR_DANGER }}>*</span>
        </label>
        <select
          value={selectedCategory}
          onChange={(e) => handleCategoryChange(e.target.value)}
          style={{
            width: '100%',
            padding: '8px 12px',
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            fontSize: '14px',
            fontFamily: FONT_FAMILY,
            backgroundColor: COLOR_WHITE,
            marginBottom: '16px',
          }}
        >
          <option value="">Select category...</option>
          {ESCALATION_CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>

        {/* Agent selection (optional) */}
        <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: COLOR_TEXT, marginBottom: '6px' }}>
          Assign to agent <span style={{ fontSize: '11px', color: COLOR_GRAY }}>(optional)</span>
        </label>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          disabled={!selectedCategory}
          style={{
            width: '100%',
            padding: '8px 12px',
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            fontSize: '14px',
            fontFamily: FONT_FAMILY,
            backgroundColor: !selectedCategory ? COLOR_LIGHT_GRAY : COLOR_WHITE,
            marginBottom: availableAgents.length === 0 && selectedCategory ? '4px' : '16px',
            opacity: !selectedCategory ? 0.6 : 1,
          }}
        >
          <option value="">Auto-assign (best available)</option>
          {availableAgents.map((m) => (
            <option key={m.id} value={m.id}>
              {m.displayName}
            </option>
          ))}
        </select>
        {availableAgents.length === 0 && selectedCategory && (
          <p style={{ fontSize: '11px', color: COLOR_GRAY, margin: '0 0 16px 0' }}>
            No team members available. Add team members via the Team page to enable assignment.
          </p>
        )}

        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              border: `1px solid ${COLOR_BORDER}`,
              borderRadius: BORDER_RADIUS,
              backgroundColor: COLOR_WHITE,
              color: COLOR_TEXT,
              fontSize: '13px',
              fontFamily: FONT_FAMILY,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            disabled={!selectedCategory || escalating}
            onClick={async () => {
              if (selectedCategory) {
                await onEscalate(conversationId, {
                  category: selectedCategory,
                  agentId: selectedAgent || undefined,
                });
                onClose();
              }
            }}
            style={{
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
            }}
          >
            {escalating ? 'Escalating...' : 'Escalate'}
          </button>
        </div>
      </div>
    </div>
  );
};

interface NoteModalProps {
  conversationId: string;
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onClose: () => void;
  onSuccess: () => void;
}

const NoteModal: React.FC<NoteModalProps> = ({ conversationId, apiFetch, onClose, onSuccess }) => {
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = useCallback(async () => {
    if (!note.trim()) return;
    setSaving(true);
    try {
      const resp = await apiFetch(`/api/admin/conversations/${conversationId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: note.trim() }),
      });
      if (!resp.ok) throw new Error(`${resp.status}`);
      onSuccess();
      onClose();
    } catch {
      // error handled silently — shell notification used externally
    } finally {
      setSaving(false);
    }
  }, [note, conversationId, apiFetch, onSuccess, onClose]);

  return (
    <div
      style={{
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
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: COLOR_WHITE,
          borderRadius: BORDER_RADIUS,
          padding: '24px',
          width: '420px',
          maxWidth: '90vw',
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }}>
          Add internal note
          <HelpTooltip text="Private notes visible only to your team, not to customers." docLink="https://agentredcx.com/docs/admin-guide/conversations#conversation-detail" />
        </h3>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Write an internal note about this conversation..."
          rows={4}
          style={{
            width: '100%',
            padding: '10px 12px',
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            fontSize: '14px',
            fontFamily: FONT_FAMILY,
            resize: 'vertical',
            marginBottom: '16px',
            boxSizing: 'border-box',
          }}
        />
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              border: `1px solid ${COLOR_BORDER}`,
              borderRadius: BORDER_RADIUS,
              backgroundColor: COLOR_WHITE,
              color: COLOR_TEXT,
              fontSize: '13px',
              fontFamily: FONT_FAMILY,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            disabled={!note.trim() || saving}
            onClick={handleSave}
            style={{
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
            }}
          >
            {saving ? 'Saving...' : 'Save note'}
          </button>
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Empty / Loading / Error states
// ---------------------------------------------------------------------------

const LoadingSpinner: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 16px', color: COLOR_TEXT_SECONDARY }}>
    <div
      style={{
        width: '32px',
        height: '32px',
        border: `3px solid ${COLOR_BORDER}`,
        borderTopColor: BRAND_PRIMARY,
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        marginBottom: '12px',
      }}
    />
    <span style={{ fontSize: '14px' }}>{text}</span>
    <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

const EmptyState: React.FC<{ icon: string; title: string; subtitle?: string }> = ({ icon, title, subtitle }) => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 16px', color: COLOR_TEXT_SECONDARY }}>
    <span style={{ fontSize: '40px', marginBottom: '12px' }}>{icon}</span>
    <span style={{ fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }}>{title}</span>
    {subtitle && <span style={{ fontSize: '13px' }}>{subtitle}</span>}
  </div>
);

const ErrorBanner: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div
    style={{
      padding: '12px 16px',
      backgroundColor: '#ffeef0',
      border: `1px solid ${COLOR_DANGER}33`,
      borderRadius: BORDER_RADIUS,
      margin: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
    }}
  >
    <span style={{ fontSize: '13px', color: COLOR_DANGER }}>{message}</span>
    {onRetry && (
      <button
        onClick={onRetry}
        style={{
          padding: '4px 12px',
          border: `1px solid ${COLOR_DANGER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: 'transparent',
          color: COLOR_DANGER,
          fontSize: '12px',
          fontFamily: FONT_FAMILY,
          cursor: 'pointer',
          whiteSpace: 'nowrap',
        }}
      >
        Retry
      </button>
    )}
  </div>
);

// ---------------------------------------------------------------------------
// Pipeline Trace Panel (SPEC-1532)
// ---------------------------------------------------------------------------

const STAGE_COLORS: Record<string, string> = {
  intent_classifier: '#2563EB',
  knowledge_retriever: '#059669',
  response_generator: '#D97706',
  critic: '#7C3AED',
  escalation: '#DC2626',
  analytics: '#6366F1',
};

const STAGE_LABELS: Record<string, string> = {
  intent_classifier: 'Intent Classifier',
  knowledge_retriever: 'Knowledge Retriever',
  response_generator: 'Response Generator',
  critic: 'Critic',
  escalation: 'Escalation',
  analytics: 'Analytics',
};

interface PipelineTracePanelProps {
  trace: PipelineTrace | null;
  loading?: boolean;
}

const PipelineTracePanel: React.FC<PipelineTracePanelProps> = ({ trace, loading }) => {
  if (loading) {
    return (
      <div style={{ padding: '12px 16px', fontSize: '12px', color: COLOR_TEXT_SECONDARY }}>
        Loading trace...
      </div>
    );
  }

  if (!trace) return null;

  const totalMs = trace.totalLatencyMs ?? trace.stages.reduce((s, st) => s + st.elapsedMs, 0);
  const maxMs = Math.max(...trace.stages.map((s) => s.elapsedMs), 1);

  return (
    <div
      style={{
        borderTop: `1px solid ${COLOR_BORDER}`,
        backgroundColor: COLOR_WHITE,
        padding: '12px 16px',
      }}
    >
      <div
        style={{
          fontSize: '11px',
          fontWeight: 600,
          textTransform: 'uppercase' as const,
          letterSpacing: '0.05em',
          color: COLOR_TEXT_SECONDARY,
          marginBottom: '10px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={COLOR_TEXT_SECONDARY} strokeWidth="2">
          <polyline points="22,12 18,12 15,21 9,3 6,12 2,12" />
        </svg>
        Pipeline Trace
      </div>

      {/* Stage bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '10px' }}>
        {trace.stages.map((stage, idx) => {
          const color = STAGE_COLORS[stage.stage] ?? COLOR_GRAY;
          const label = STAGE_LABELS[stage.stage] ?? stage.stage.replace(/_/g, ' ');
          const widthPct = Math.max((stage.elapsedMs / maxMs) * 100, 4);
          return (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  width: '110px',
                  fontSize: '11px',
                  color: COLOR_TEXT_SECONDARY,
                  textOverflow: 'ellipsis',
                  overflow: 'hidden',
                  whiteSpace: 'nowrap' as const,
                  flexShrink: 0,
                }}
              >
                {label}
              </span>
              <div style={{ flex: 1, height: '14px', backgroundColor: COLOR_LIGHT_GRAY, borderRadius: '3px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${widthPct}%`,
                    height: '100%',
                    backgroundColor: color,
                    borderRadius: '3px',
                    opacity: stage.succeeded ? 1 : 0.4,
                  }}
                />
              </div>
              <span style={{ width: '50px', fontSize: '11px', color: COLOR_TEXT_SECONDARY, textAlign: 'right' as const, flexShrink: 0, fontFamily: FONT_MONO }}>
                {stage.elapsedMs}ms
              </span>
            </div>
          );
        })}
      </div>

      {/* Summary badges */}
      <div style={{ display: 'flex', flexWrap: 'wrap' as const, gap: '6px', fontSize: '11px' }}>
        {trace.intent && (
          <span style={{ padding: '2px 8px', borderRadius: '4px', backgroundColor: '#2563EB14', color: '#2563EB', fontWeight: 500 }}>
            {trace.intent}
          </span>
        )}
        {trace.criticPassed !== null && (
          <span
            style={{
              padding: '2px 8px',
              borderRadius: '4px',
              backgroundColor: trace.criticPassed ? '#05966914' : '#DC262614',
              color: trace.criticPassed ? '#059669' : '#DC2626',
              fontWeight: 500,
            }}
          >
            Critic: {trace.criticPassed ? 'PASS' : 'FAIL'}
          </span>
        )}
        {totalMs > 0 && (
          <span style={{ padding: '2px 8px', borderRadius: '4px', backgroundColor: COLOR_LIGHT_GRAY, color: COLOR_TEXT_SECONDARY, fontFamily: FONT_MONO }}>
            {totalMs}ms total
          </span>
        )}
        {trace.modelUsed && (
          <span style={{ padding: '2px 8px', borderRadius: '4px', backgroundColor: COLOR_LIGHT_GRAY, color: COLOR_TEXT_SECONDARY }}>
            {trace.modelUsed}
          </span>
        )}
      </div>

      {/* Trace ID */}
      {trace.traceId && (
        <div style={{ marginTop: '6px', fontSize: '10px', color: COLOR_GRAY, fontFamily: FONT_MONO }}>
          Trace: {trace.traceId}
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const ConversationInbox: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const searchTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Polling: fetch conversation list every 5 seconds
  const {
    data: inboxData,
    loading: inboxLoading,
    error: inboxError,
    refetch: refetchInbox,
  } = usePolling<{ conversations: InboxConversation[] }>(apiFetch, '/api/admin/conversations', 5000);

  const conversations = inboxData?.conversations ?? [];

  // Selected conversation messages
  const {
    data: messagesData,
    loading: messagesLoading,
    error: messagesError,
    refetch: refetchMessages,
  } = useConversationMessages(apiFetch, selectedId || '');

  const messages = messagesData?.messages ?? [];

  // Team members (for assign modal + name resolution)
  const { data: teamData } = useTeamMembers(apiFetch);
  const teamMembers = teamData?.members ?? [];
  const memberMap = useMemo(() => {
    const map: Record<string, string> = {};
    for (const m of teamMembers) {
      map[m.id] = m.displayName || m.email;
    }
    return map;
  }, [teamMembers]);

  // Search
  const { search: searchConversations, clearSearch, results: searchResults, loading: searchLoading } = useSearchConversations(apiFetch);

  const handleSearchInput = useCallback(
    (value: string) => {
      setSearchQuery(value);
      if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
      if (!value.trim()) {
        clearSearch();
        return;
      }
      searchTimerRef.current = setTimeout(() => {
        searchConversations(value);
      }, 350);
    },
    [searchConversations, clearSearch],
  );

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

  const handleAssign = useCallback(
    async (conversationId: string, agentId: string) => {
      try {
        await assign(conversationId, agentId);
        onNotify('Conversation assigned successfully', 'success');
        refetchInbox();
      } catch {
        onNotify('Failed to assign conversation', 'error');
      }
    },
    [assign, onNotify, refetchInbox],
  );

  const handleNoteSuccess = useCallback(() => {
    onNotify('Note added successfully', 'success');
    refetchMessages();
  }, [onNotify, refetchMessages]);

  const handleEscalateClick = useCallback(
    (_conversationId: string) => {
      setShowEscalateModal(true);
    },
    [],
  );

  const handleEscalateConfirm = useCallback(
    async (conversationId: string, opts: { category: string; agentId?: string }) => {
      try {
        await escalate(conversationId, opts);
        onNotify('Conversation escalated to human support', 'success');
        refetchInbox();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Escalation failed';
        onNotify(msg, 'error');
      }
    },
    [escalate, onNotify, refetchInbox],
  );

  const handleResolve = useCallback(
    async (conversationId: string) => {
      try {
        await resolve(conversationId);
        onNotify('Conversation marked as resolved', 'success');
        refetchInbox();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to resolve conversation';
        onNotify(msg, 'error');
      }
    },
    [resolve, onNotify, refetchInbox],
  );

  const handleArchive = useCallback(
    async (conversationId: string) => {
      try {
        await archive(conversationId);
        onNotify('Conversation archived', 'success');
        setSelectedId(null);
        refetchInbox();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to archive conversation';
        onNotify(msg, 'error');
      }
    },
    [archive, onNotify, refetchInbox],
  );

  // Group messages by date for day separators
  const groupedMessages: Array<{ dateLabel: string; messages: ConversationMessage[] }> = [];
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

  return (
    <div
      style={{
        display: 'flex',
        height: '100%',
        minHeight: '500px',
        fontFamily: FONT_FAMILY,
        border: `1px solid ${COLOR_BORDER}`,
        borderRadius: BORDER_RADIUS,
        overflow: 'hidden',
        backgroundColor: COLOR_WHITE,
      }}
    >
      {/* Left panel: conversation list */}
      <div
        style={{
          width: '340px',
          minWidth: '280px',
          borderRight: `1px solid ${COLOR_BORDER}`,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: COLOR_WHITE,
        }}
      >
        {/* List header */}
        <div
          style={{
            padding: '16px',
            borderBottom: `1px solid ${COLOR_BORDER}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: COLOR_TEXT, display: 'inline-flex', alignItems: 'center' }}>
            Conversations
            <HelpTooltip text="Real-time list of customer conversations. Filter by status to find active, escalated, or resolved chats." docLink="https://agentredcx.com/docs/admin-guide/conversations#conversation-list" />
          </h2>
          <span
            style={{
              fontSize: '12px',
              color: COLOR_TEXT_SECONDARY,
              backgroundColor: COLOR_LIGHT_GRAY,
              padding: '2px 8px',
              borderRadius: '12px',
            }}
          >
            {conversations.length}
          </span>
        </div>

        {/* Search bar */}
        <div style={{ padding: '8px 12px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearchInput(e.target.value)}
              placeholder="Search messages..."
              style={{
                width: '100%',
                padding: '7px 10px 7px 30px',
                border: `1px solid ${COLOR_BORDER}`,
                borderRadius: BORDER_RADIUS,
                fontSize: '13px',
                fontFamily: FONT_FAMILY,
                backgroundColor: COLOR_LIGHT_GRAY,
                boxSizing: 'border-box',
                outline: 'none',
              }}
              onFocus={(e) => { (e.currentTarget as HTMLInputElement).style.borderColor = ACTION_BLUE; }}
              onBlur={(e) => { (e.currentTarget as HTMLInputElement).style.borderColor = COLOR_BORDER; }}
            />
            <span style={{ position: 'absolute', left: '9px', top: '50%', transform: 'translateY(-50%)', fontSize: '14px', color: COLOR_TEXT_SECONDARY, pointerEvents: 'none' }}>
              {searchLoading ? '\u2026' : '\u{1F50D}'}
            </span>
            {searchQuery && (
              <button
                onClick={() => handleSearchInput('')}
                style={{ position: 'absolute', right: '6px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: COLOR_TEXT_SECONDARY, fontSize: '14px', padding: '2px' }}
              >
                \u2715
              </button>
            )}
          </div>
        </div>

        {/* Conversation list */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {/* Search results mode */}
          {isSearchActive && (
            <>
              <div style={{ padding: '8px 12px', fontSize: '12px', color: COLOR_TEXT_SECONDARY, borderBottom: `1px solid ${COLOR_BORDER}`, backgroundColor: '#fafbfc' }}>
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for &ldquo;{searchQuery}&rdquo;
              </div>
              {searchResults.length === 0 && !searchLoading && (
                <EmptyState icon={String.fromCodePoint(0x1F50E)} title="No results" subtitle="Try a different search term." />
              )}
              {searchResults.map((sr: SearchResult) => (
                <div
                  key={sr.conversation_id}
                  onClick={() => { setSelectedId(sr.conversation_id); }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === 'Enter') setSelectedId(sr.conversation_id); }}
                  style={{
                    padding: '10px 14px',
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    backgroundColor: sr.conversation_id === selectedId ? '#f1f5ff' : COLOR_WHITE,
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => { if (sr.conversation_id !== selectedId) (e.currentTarget as HTMLElement).style.backgroundColor = COLOR_LIGHT_GRAY; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.backgroundColor = sr.conversation_id === selectedId ? '#f1f5ff' : COLOR_WHITE; }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px', color: COLOR_TEXT }}>{sr.customer_name || 'Anonymous'}</span>
                    <StatusBadge status={sr.status} />
                  </div>
                  <div style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, lineHeight: '1.4', marginBottom: '2px' }}>
                    {sr.snippet}
                  </div>
                  <div style={{ fontSize: '11px', color: COLOR_GRAY }}>
                    Matched in {sr.matched_in} &middot; {sr.message_count} msg{sr.message_count !== 1 ? 's' : ''}
                  </div>
                </div>
              ))}
            </>
          )}

          {/* Normal list mode */}
          {!isSearchActive && (
            <>
              {inboxLoading && conversations.length === 0 && (
                <LoadingSpinner text="Loading conversations..." />
              )}
              {inboxError && conversations.length === 0 && (
                <ErrorBanner message={inboxError} onRetry={refetchInbox} />
              )}
              {!inboxLoading && !inboxError && conversations.length === 0 && (
                <EmptyState
                  icon={String.fromCodePoint(0x1F4AC)}
                  title="No conversations yet"
                  subtitle="Conversations will appear here when customers start chatting."
                />
              )}
              {conversations.map((conv) => (
                <ConversationItem
                  key={conv.conversationId}
                  conversation={conv}
                  isSelected={conv.conversationId === selectedId}
                  onClick={() => setSelectedId(conv.conversationId)}
                  memberMap={memberMap}
                />
              ))}
            </>
          )}
        </div>
      </div>

      {/* Right panel: message transcript */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: COLOR_LIGHT_GRAY,
        }}
      >
        {!selectedId ? (
          <EmptyState
            icon={String.fromCodePoint(0x1F4E8)}
            title="Select a conversation"
            subtitle="Choose a conversation from the list to view the message transcript."
          />
        ) : (
          <>
            {/* Transcript header */}
            <div
              style={{
                padding: '12px 16px',
                borderBottom: `1px solid ${COLOR_BORDER}`,
                backgroundColor: COLOR_WHITE,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <span style={{ fontWeight: 600, fontSize: '14px', color: COLOR_TEXT }}>
                  {selectedConversation?.customerName || selectedConversation?.customerId || 'Anonymous'}
                </span>
                {selectedConversation && (
                  <span style={{ marginLeft: '10px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <StatusBadge status={selectedConversation.status} />
                    {selectedConversation.escalationCategory && (
                      <span
                        style={{
                          fontSize: '11px',
                          fontWeight: 600,
                          color: COLOR_DANGER,
                          backgroundColor: COLOR_DANGER + '14',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          textTransform: 'capitalize',
                        }}
                      >
                        {selectedConversation.escalationCategory.replace(/_/g, ' ')}
                      </span>
                    )}
                    {selectedConversation.assignedTo && (
                      <span style={{ fontSize: '11px', color: COLOR_TEXT_SECONDARY }}>
                        {memberMap[selectedConversation.assignedTo] ?? selectedConversation.assignedTo}
                      </span>
                    )}
                    <HelpTooltip text="Conversation status, escalation category, and assigned agent." docLink="https://agentredcx.com/docs/admin-guide/conversations#conversation-list" />
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                {selectedConversation?.status !== 'escalated' && selectedConversation?.status !== 'resolved' && (
                  <button
                    disabled={escalating}
                    onClick={() => selectedId && handleEscalateClick(selectedId)}
                    style={{
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
                    }}
                  >
                    {escalating ? 'Escalating...' : 'Escalate'}
                  </button>
                )}
                {selectedConversation?.status !== 'resolved' && (
                  <button
                    disabled={resolving}
                    onClick={() => selectedId && handleResolve(selectedId)}
                    style={{
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
                    }}
                  >
                    {resolving ? 'Resolving...' : 'Mark resolved'}
                  </button>
                )}
                <button
                  onClick={() => setShowAssignModal(true)}
                  style={{
                    padding: '6px 12px',
                    border: `1px solid ${COLOR_BORDER}`,
                    borderRadius: BORDER_RADIUS,
                    backgroundColor: COLOR_WHITE,
                    color: COLOR_TEXT,
                    fontSize: '12px',
                    fontFamily: FONT_FAMILY,
                    cursor: 'pointer',
                    fontWeight: 500,
                  }}
                >
                  Assign
                </button>
                <button
                  onClick={() => setShowNoteModal(true)}
                  style={{
                    padding: '6px 12px',
                    border: `1px solid ${COLOR_BORDER}`,
                    borderRadius: BORDER_RADIUS,
                    backgroundColor: COLOR_WHITE,
                    color: COLOR_TEXT,
                    fontSize: '12px',
                    fontFamily: FONT_FAMILY,
                    cursor: 'pointer',
                    fontWeight: 500,
                  }}
                >
                  Add note
                </button>
                {(selectedConversation?.status === 'resolved' || selectedConversation?.status === 'ended') && (
                  <button
                    disabled={archiving}
                    onClick={() => selectedId && handleArchive(selectedId)}
                    style={{
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
                    }}
                  >
                    {archiving ? 'Archiving...' : 'Archive'}
                  </button>
                )}
              </div>
            </div>

            {/* Message transcript */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
              {messagesLoading && messages.length === 0 && (
                <LoadingSpinner text="Loading messages..." />
              )}
              {messagesError && messages.length === 0 && (
                <ErrorBanner message={messagesError} onRetry={refetchMessages} />
              )}
              {!messagesLoading && !messagesError && messages.length === 0 && (
                <EmptyState
                  icon={String.fromCodePoint(0x1F4DD)}
                  title="No messages"
                  subtitle="This conversation has no messages yet."
                />
              )}
              {groupedMessages.map((group) => (
                <div key={group.dateLabel}>
                  <div
                    style={{
                      textAlign: 'center',
                      margin: '16px 0 12px',
                      position: 'relative',
                    }}
                  >
                    <span
                      style={{
                        display: 'inline-block',
                        backgroundColor: COLOR_LIGHT_GRAY,
                        color: COLOR_TEXT_SECONDARY,
                        fontSize: '11px',
                        fontWeight: 500,
                        padding: '2px 10px',
                        borderRadius: '10px',
                        border: `1px solid ${COLOR_BORDER}`,
                      }}
                    >
                      {group.dateLabel}
                    </span>
                  </div>
                  {group.messages.map((msg, idx) => (
                    <MessageBubble key={msg.messageId ?? `msg-${idx}`} message={msg} />
                  ))}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Pipeline trace (SPEC-1532) */}
            <PipelineTracePanel trace={traceResult ?? null} />
          </>
        )}
      </div>

      {/* Modals */}
      {showAssignModal && selectedId && (
        <AssignModal
          conversationId={selectedId}
          members={teamMembers}
          onAssign={handleAssign}
          onClose={() => setShowAssignModal(false)}
          assigning={assigning}
        />
      )}
      {showNoteModal && selectedId && (
        <NoteModal
          conversationId={selectedId}
          apiFetch={apiFetch}
          onClose={() => setShowNoteModal(false)}
          onSuccess={handleNoteSuccess}
        />
      )}
      {showEscalateModal && selectedId && (
        <EscalateModal
          conversationId={selectedId}
          members={teamMembers}
          onEscalate={handleEscalateConfirm}
          onClose={() => setShowEscalateModal(false)}
          escalating={escalating}
        />
      )}
    </div>
  );
};

export default ConversationInbox;
