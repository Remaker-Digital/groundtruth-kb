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

import React, { useState, useCallback, useEffect, useRef } from 'react';
import type {
  BaseComponentProps,
  InboxConversation,
  ConversationMessage,
  ConversationStatus,
  TeamMember,
} from '../types';
import {
  usePolling,
  useConversationMessages,
  useAssignConversation,
  useTeamMembers,
} from '../hooks';

// ---------------------------------------------------------------------------
// Style constants
// ---------------------------------------------------------------------------

const BRAND_PRIMARY = '#C41E2A';
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

const STATUS_COLORS: Record<ConversationStatus, string> = {
  active: COLOR_SUCCESS,
  ended: COLOR_GRAY,
  escalated: COLOR_DANGER,
  idle: '#e36209',
};

const STATUS_LABELS: Record<ConversationStatus, string> = {
  active: 'Active',
  ended: 'Ended',
  escalated: 'Escalated',
  idle: 'Idle',
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

function formatTimestamp(ts: number): string {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDateHeader(ts: number): string {
  const d = new Date(ts);
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

const StatusBadge: React.FC<{ status: ConversationStatus }> = ({ status }) => (
  <span
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '5px',
      fontSize: '12px',
      color: STATUS_COLORS[status],
      fontWeight: 500,
    }}
  >
    <span
      style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: STATUS_COLORS[status],
        display: 'inline-block',
        flexShrink: 0,
      }}
    />
    {STATUS_LABELS[status]}
  </span>
);

interface ConversationItemProps {
  conversation: InboxConversation;
  isSelected: boolean;
  onClick: () => void;
}

const ConversationItem: React.FC<ConversationItemProps> = ({ conversation, isSelected, onClick }) => (
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
        {formatRelativeTime(conversation.lastMessageAt)}
      </span>
    </div>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <StatusBadge status={conversation.status} />
      <span style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY }}>
        {conversation.messageCount} message{conversation.messageCount !== 1 ? 's' : ''}
      </span>
    </div>
    {conversation.assignedTo && (
      <div style={{ fontSize: '11px', color: COLOR_TEXT_SECONDARY, marginTop: '4px' }}>
        Assigned to: {conversation.assignedTo}
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
          {isCustomer ? 'Customer' : message.agentName || 'Agent'} {' '}
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
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT }}>
          Assign Conversation
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
            .filter((m) => m.status === 'active')
            .map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.role})
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
              backgroundColor: !selectedAgent || assigning ? COLOR_GRAY : BRAND_PRIMARY,
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
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: COLOR_TEXT }}>
          Add Internal Note
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
              backgroundColor: !note.trim() || saving ? COLOR_GRAY : BRAND_PRIMARY,
              color: COLOR_WHITE,
              fontSize: '13px',
              fontFamily: FONT_FAMILY,
              fontWeight: 500,
              cursor: !note.trim() || saving ? 'not-allowed' : 'pointer',
              opacity: saving ? 0.7 : 1,
            }}
          >
            {saving ? 'Saving...' : 'Save Note'}
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  // Team members (for assign modal)
  const { data: teamData } = useTeamMembers(apiFetch);
  const teamMembers = teamData?.members ?? [];

  // Assign conversation
  const { assign, loading: assigning } = useAssignConversation(apiFetch);

  // Auto-scroll to bottom of messages when selected or messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const selectedConversation = conversations.find((c) => c.id === selectedId) || null;

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

  // Group messages by date for day separators
  const groupedMessages: Array<{ dateLabel: string; messages: ConversationMessage[] }> = [];
  let currentDateStr = '';
  for (const msg of messages) {
    const dateStr = new Date(msg.timestamp).toDateString();
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
          <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: COLOR_TEXT }}>
            Conversations
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

        {/* Conversation list */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {inboxLoading && conversations.length === 0 && (
            <LoadingSpinner text="Loading conversations..." />
          )}
          {inboxError && conversations.length === 0 && (
            <ErrorBanner message={inboxError} onRetry={refetchInbox} />
          )}
          {!inboxLoading && !inboxError && conversations.length === 0 && (
            <EmptyState
              icon="\u{1F4AC}"
              title="No conversations yet"
              subtitle="Conversations will appear here when customers start chatting."
            />
          )}
          {conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              isSelected={conv.id === selectedId}
              onClick={() => setSelectedId(conv.id)}
            />
          ))}
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
            icon="\u{1F4E8}"
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
                  <span style={{ marginLeft: '10px' }}>
                    <StatusBadge status={selectedConversation.status} />
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
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
                  Add Note
                </button>
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
                  icon="\u{1F4DD}"
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
                  {group.messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                  ))}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
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
    </div>
  );
};

export default ConversationInbox;
