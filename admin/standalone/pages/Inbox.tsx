// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useRef, useEffect } from 'react';
import {
  Paper,
  TextInput,
  SegmentedControl,
  Badge,
  Group,
  Stack,
  Text,
  ScrollArea,
  ActionIcon,
  Tooltip,
  Divider,
  Avatar,
  Box,
  Loader,
  useComputedColorScheme,
} from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useInboxConversations, useConversationMessages } from '../../shared/hooks/index';
import type { InboxConversation, ConversationMessage } from '../../shared/types/index';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND_RED = '#ff3621';
const HEADER_HEIGHT = 56;
const PAGE_PADDING = 16;

const STATUS_COLORS: Record<string, string> = {
  active: 'blue',
  ended: 'green',
  escalated: 'red',
  idle: 'yellow',
  timed_out: 'yellow',
  error: 'red',
};

const AVATAR_PALETTE = ['#ff3621', '#2563EB', '#059669', '#D97706', '#7C3AED', '#DB2777'];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getInitials(name: string | null | undefined): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map((n) => n[0])
    .filter(Boolean)
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function avatarColor(name: string | null | undefined): string {
  if (!name) return AVATAR_PALETTE[0];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length];
}

function timeAgo(dateString: string | null | undefined): string {
  if (!dateString) return '--';
  const now = Date.now();
  const then = new Date(dateString).getTime();
  if (isNaN(then)) return '--';
  const seconds = Math.floor((now - then) / 1000);
  if (seconds < 0) return 'just now';
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

function formatTimestampString(ts: string | null | undefined): string {
  if (!ts) return '';
  const d = new Date(ts);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}

// ---------------------------------------------------------------------------
// Inline SVG Icons
// ---------------------------------------------------------------------------

const SearchIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);


const EscalateIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** Left panel: single conversation row */
function ConversationItem({
  conversation,
  isSelected,
  onClick,
  selectedBgColor,
  hoverBgColor,
}: {
  conversation: InboxConversation;
  isSelected: boolean;
  onClick: () => void;
  selectedBgColor: string;
  hoverBgColor: string;
}) {
  const displayName = conversation.customerName || conversation.conversationId?.slice(0, 12) || 'Session';
  const initials = getInitials(displayName);
  const color = avatarColor(displayName);
  const isUnread = conversation.status === 'active' || conversation.status === 'escalated';

  return (
    <Box
      onClick={onClick}
      style={{
        padding: '10px 12px',
        borderRadius: 8,
        cursor: 'pointer',
        background: isSelected ? selectedBgColor : 'transparent',
        borderLeft: isSelected ? `3px solid ${BRAND_RED}` : '3px solid transparent',
        transition: 'background 0.15s',
      }}
      onMouseEnter={(e: React.MouseEvent<HTMLDivElement>) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = hoverBgColor;
      }}
      onMouseLeave={(e: React.MouseEvent<HTMLDivElement>) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = 'transparent';
      }}
    >
      <Group gap={10} align="flex-start" wrap="nowrap">
        {/* Avatar */}
        <Box style={{ flexShrink: 0 }}>
          <Avatar
            size={38}
            radius="xl"
            color={color}
            style={{ background: color, color: '#fff', fontWeight: 600, fontSize: 14 }}
          >
            {initials}
          </Avatar>
        </Box>

        {/* Content */}
        <Box style={{ flex: 1, minWidth: 0 }}>
          <Group justify="space-between" wrap="nowrap" gap={4}>
            <Text size="sm" fw={isUnread ? 700 : 500} truncate style={{ flex: 1 }}>
              {displayName}
            </Text>
            <Text size="xs" c="dimmed" style={{ flexShrink: 0 }}>
              {timeAgo(conversation.lastActivityAt ?? conversation.startedAt)}
            </Text>
          </Group>
          <Text size="xs" c="dimmed" truncate mt={2}>
            {(conversation.messageCount ?? 0)} messages
          </Text>
          <Group gap={6} mt={4}>
            <Badge
              size="xs"
              variant="light"
              color={STATUS_COLORS[conversation.status ?? ''] ?? 'gray'}
              style={{ textTransform: 'capitalize' }}
            >
              {conversation.status}
            </Badge>
            {conversation.assignedTo && (
              <Text size="xs" c="dimmed">
                {conversation.assignedTo}
              </Text>
            )}
            {isUnread && (
              <Box
                style={{
                  marginLeft: 'auto',
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: BRAND_RED,
                  flexShrink: 0,
                }}
              />
            )}
          </Group>
        </Box>
      </Group>
    </Box>
  );
}

/** Center panel: single message bubble */
function MessageBubble({
  message,
  agentBubbleBg,
  customerBubbleBg,
}: {
  message: ConversationMessage;
  agentBubbleBg: string;
  customerBubbleBg: string;
}) {
  if (message.role === 'system') {
    return (
      <Box style={{ textAlign: 'center', padding: '8px 0' }}>
        <Text size="xs" c="dimmed" fs="italic">
          {message.content}
        </Text>
        <Text size="xs" c="dimmed" mt={2}>
          {formatTimestampString(message.timestamp)}
        </Text>
      </Box>
    );
  }

  const isAgent = message.role === 'agent';
  const senderName = isAgent
    ? 'Agent Red AI'
    : 'Customer';

  return (
    <Box
      style={{
        display: 'flex',
        justifyContent: isAgent ? 'flex-end' : 'flex-start',
        padding: '4px 0',
      }}
    >
      <Box style={{ maxWidth: '75%' }}>
        {/* Sender name */}
        {isAgent ? (
          <Group gap={6} justify="flex-end" mb={2}>
            <Text size="xs" c="dimmed">
              {senderName}
            </Text>
            <img
              src="/admin/standalone/icon-master.svg"
              alt="Agent Red"
              style={{ height: 16, width: 16, display: 'block', opacity: 0.85, borderRadius: 2 }}
            />
          </Group>
        ) : (
          <Text size="xs" c="dimmed" mb={2} ta="left">
            {senderName}
          </Text>
        )}

        {/* Bubble */}
        <Paper
          p="sm"
          radius="lg"
          style={{
            background: isAgent ? agentBubbleBg : customerBubbleBg,
            borderBottomRightRadius: isAgent ? 4 : undefined,
            borderBottomLeftRadius: !isAgent ? 4 : undefined,
          }}
        >
          <Text size="sm" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.55 }}>
            {message.content}
          </Text>
        </Paper>

        {/* Timestamp */}
        <Group
          gap={6}
          mt={4}
          justify={isAgent ? 'flex-end' : 'flex-start'}
        >
          <Text size="xs" c="dimmed">
            {formatTimestampString(message.timestamp)}
          </Text>
        </Group>
      </Box>
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Main Inbox Page
// ---------------------------------------------------------------------------

export function InboxPage() {
  const { apiFetch } = useAppContext();
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // ---- State ----
  const [selectedId, setSelectedId] = useState<string>('');
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const messageEndRef = useRef<HTMLDivElement>(null);

  // ---- API hooks ----
  const convResult = useInboxConversations(apiFetch);
  const conversations: InboxConversation[] = convResult.data?.conversations ?? [];

  const msgResult = useConversationMessages(apiFetch, selectedId);
  const messages: ConversationMessage[] = msgResult.data?.messages ?? [];

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

  // ---- Dark mode colors (Mazel design revision) ----
  const panelBg = isDark ? '#0a0a0a' : '#fff';
  const centerBg = isDark ? '#0a0a0a' : '#fafafa';
  const borderColor = isDark ? '#272727' : 'var(--mantine-color-gray-2)';
  const hoverBg = isDark ? 'rgba(255,255,255,0.04)' : '#f8f9fa';
  const selectedBg = isDark ? '#1f1f1f' : '#FFF1F2';
  const bubbleAgentBg = isDark ? '#1f1f1f' : '#f1f3f5';
  const bubbleCustomerBg = isDark ? '#1f1f1f' : '#f1f3f5';

  // ---- Filtering ----
  const filteredConversations = conversations.filter((c) => {
    if (filter !== 'all' && c.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      const name = (c.customerName ?? '').toLowerCase();
      const id = (c.conversationId ?? '').toLowerCase();
      return name.includes(q) || id.includes(q);
    }
    return true;
  });

  // Clear reader pane when search/filter yields no results (Issue 3a)
  useEffect(() => {
    if (filteredConversations.length === 0 && (search || filter !== 'all')) {
      setSelectedId('');
    }
  }, [filteredConversations.length, search, filter]);

  // ---- Counts per filter ----
  const counts = {
    all: conversations.length,
    active: conversations.filter((c) => c.status === 'active').length,
    escalated: conversations.filter((c) => c.status === 'escalated').length,
    idle: conversations.filter((c) => c.status === 'idle').length,
  };

  // ---- Selected conversation ----
  const selectedConversation = conversations.find((c) => c.conversationId === selectedId) ?? null;
  const selectedDisplayName = selectedConversation?.customerName || selectedConversation?.conversationId?.slice(0, 12) || 'Session';

  const layoutHeight = `calc(100vh - ${HEADER_HEIGHT}px - ${PAGE_PADDING * 2}px)`;

  return (
    <Box
      style={{
        display: 'flex',
        gap: 0,
        height: layoutHeight,
        marginTop: -PAGE_PADDING,
        marginLeft: -PAGE_PADDING,
        marginRight: -PAGE_PADDING,
        marginBottom: -PAGE_PADDING,
      }}
    >
      {/* ================================================================= */}
      {/* LEFT PANEL: Conversation List                                      */}
      {/* ================================================================= */}
      <Box
        style={{
          width: 280,
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
          borderRight: `1px solid ${borderColor}`,
          background: panelBg,
        }}
      >
        {/* Search */}
        <Box p="sm" pb={0}>
          <TextInput
            placeholder="Search conversations..."
            leftSection={<SearchIcon />}
            size="sm"
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            styles={{
              input: { borderColor: isDark ? '#272727' : 'var(--mantine-color-gray-3)' },
            }}
          />
        </Box>

        {/* Filter tabs */}
        <Box px={6} py="xs">
          <SegmentedControl
            value={filter}
            onChange={setFilter}
            size="xs"
            fullWidth
            data={[
              { label: `All (${counts.all})`, value: 'all' },
              { label: `Active (${counts.active})`, value: 'active' },
              { label: `Esc (${counts.escalated})`, value: 'escalated' },
              { label: `Idle (${counts.idle})`, value: 'idle' },
            ]}
            styles={{
              root: { background: isDark ? 'rgba(255,255,255,0.04)' : 'var(--mantine-color-gray-0)' },
              label: { padding: '4px 6px', fontSize: 11 },
            }}
          />
        </Box>

        <Divider />

        {/* Conversation list */}
        <ScrollArea style={{ flex: 1 }} type="auto" offsetScrollbars>
          <Stack gap={0} p={4}>
            {convResult.loading && conversations.length === 0 && (
              <Box py="xl" ta="center">
                <Loader size="sm" color="gray" />
                <Text size="xs" c="dimmed" mt="sm">Loading conversations...</Text>
              </Box>
            )}
            {convResult.error && (
              <Box py="xl" px="sm">
                <Text size="sm" c="red" ta="center">
                  Failed to load conversations
                </Text>
                <Text size="xs" c="dimmed" ta="center" mt={4}>
                  {convResult.error}
                </Text>
              </Box>
            )}
            {!convResult.loading && !convResult.error && filteredConversations.length === 0 && (
              <Box py={40} px="sm" ta="center">
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={isDark ? '#5C5C5C' : '#adb5bd'}
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ margin: '0 auto 12px', display: 'block', opacity: 0.7 }}
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <Text size="sm" fw={500} c="dimmed" mb={4}>
                  {search || filter !== 'all' ? 'No matching conversations' : 'No conversations yet'}
                </Text>
                <Text size="xs" c="dimmed">
                  {search || filter !== 'all'
                    ? 'Try adjusting your search or filter.'
                    : 'Conversations will appear here once customers start chatting with your AI agent.'}
                </Text>
              </Box>
            )}
            {filteredConversations.map((conv) => (
              <ConversationItem
                key={conv.conversationId}
                conversation={conv}
                isSelected={conv.conversationId === selectedId}
                onClick={() => setSelectedId(conv.conversationId)}
                selectedBgColor={selectedBg}
                hoverBgColor={hoverBg}
              />
            ))}
          </Stack>
        </ScrollArea>
      </Box>

      {/* ================================================================= */}
      {/* CENTER PANEL: Message Thread                                       */}
      {/* ================================================================= */}
      <Box
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          background: centerBg,
          minWidth: 0,
        }}
      >
        {/* Thread header */}
        <Box
          px="md"
          py="sm"
          style={{
            background: panelBg,
            borderBottom: `1px solid ${borderColor}`,
          }}
        >
          {selectedConversation ? (
            <Group justify="space-between" wrap="nowrap">
              <Box style={{ minWidth: 0 }}>
                <Group gap={8} wrap="nowrap">
                  <Text size="md" fw={600} truncate>
                    {selectedDisplayName}
                  </Text>
                  <Badge
                    size="sm"
                    variant="light"
                    color={STATUS_COLORS[selectedConversation.status ?? ''] ?? 'gray'}
                    style={{ textTransform: 'capitalize' }}
                  >
                    {selectedConversation.status}
                  </Badge>
                </Group>
                <Text size="xs" c="dimmed" mt={2} truncate>
                  {(selectedConversation.messageCount ?? 0)} messages
                  {selectedConversation.assignedTo && (
                    <> &middot; Assigned to {selectedConversation.assignedTo}</>
                  )}
                </Text>
              </Box>
              <Group gap={4} style={{ flexShrink: 0 }}>
                <Tooltip label="Escalate to human">
                  <ActionIcon variant="subtle" color="orange" size="md">
                    <EscalateIcon />
                  </ActionIcon>
                </Tooltip>
                <Tooltip label="Resolve conversation">
                  <ActionIcon variant="subtle" color="green" size="md">
                    <CheckIcon />
                  </ActionIcon>
                </Tooltip>
              </Group>
            </Group>
          ) : (
            <Text size="sm" c="dimmed">
              Select a conversation
            </Text>
          )}
        </Box>

        {/* Messages */}
        <ScrollArea style={{ flex: 1 }} type="auto" offsetScrollbars>
          <Box px="md" py="sm">
            {!selectedId && (
              <Box style={{ textAlign: 'center', paddingTop: 80 }}>
                <Text c="dimmed" size="sm">
                  Select a conversation from the list to view messages.
                </Text>
              </Box>
            )}
            {selectedId && msgResult.loading && messages.length === 0 && (
              <Box style={{ textAlign: 'center', paddingTop: 80 }}>
                <Loader size="sm" color="gray" />
                <Text c="dimmed" size="xs" mt="sm">Loading messages...</Text>
              </Box>
            )}
            {selectedId && msgResult.error && (
              <Box style={{ textAlign: 'center', paddingTop: 80 }}>
                <Text c="red" size="sm">
                  Failed to load messages
                </Text>
                <Text c="dimmed" size="xs" mt={4}>
                  {msgResult.error}
                </Text>
              </Box>
            )}
            {selectedId && !msgResult.loading && !msgResult.error && messages.length === 0 && (
              <Box style={{ textAlign: 'center', paddingTop: 80 }}>
                <Text c="dimmed" size="sm">
                  No messages in this conversation yet.
                </Text>
              </Box>
            )}
            {messages.length > 0 && (
              <Stack gap={8}>
                {messages.map((msg, idx) => (
                  <MessageBubble
                    key={msg.messageId ?? `msg-${idx}`}
                    message={msg}
                    agentBubbleBg={bubbleAgentBg}
                    customerBubbleBg={bubbleCustomerBg}
                  />
                ))}
                <div ref={messageEndRef} />
              </Stack>
            )}
          </Box>
        </ScrollArea>

      </Box>

      {/* ================================================================= */}
      {/* RIGHT PANEL: Customer Details                                      */}
      {/* ================================================================= */}
      <Box
        style={{
          width: 320,
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
          borderLeft: `1px solid ${borderColor}`,
          background: panelBg,
        }}
      >
        <ScrollArea style={{ flex: 1 }} type="auto" offsetScrollbars>
          <Stack gap={0}>
            {/* Customer header */}
            {selectedConversation ? (
              <>
                <Box p="md" style={{ textAlign: 'center' }}>
                  <Avatar
                    size={64}
                    radius="xl"
                    mx="auto"
                    style={{
                      background: avatarColor(selectedDisplayName),
                      color: '#fff',
                      fontWeight: 700,
                      fontSize: 22,
                    }}
                  >
                    {getInitials(selectedDisplayName)}
                  </Avatar>
                  <Text size="md" fw={600} mt={8}>
                    {selectedDisplayName}
                  </Text>
                  {selectedConversation.customerId && (
                    <Text size="xs" c="dimmed" mt={2}>
                      ID: {selectedConversation.customerId}
                    </Text>
                  )}
                  <Badge
                    size="xs"
                    variant="light"
                    color={STATUS_COLORS[selectedConversation.status ?? ''] ?? 'gray'}
                    mt={6}
                    style={{ textTransform: 'capitalize' }}
                  >
                    {selectedConversation.status}
                  </Badge>
                </Box>

                <Divider />

                {/* Conversation info */}
                <Box p="md">
                  <Text size="xs" fw={600} c="dimmed" mb={8}>
                    Conversation info
                  </Text>
                  <Stack gap={6}>
                    <Group gap={8} wrap="nowrap">
                      <Text size="xs" c="dimmed" style={{ width: 80, flexShrink: 0 }}>Messages</Text>
                      <Text size="sm">{selectedConversation.messageCount ?? 0}</Text>
                    </Group>
                    <Group gap={8} wrap="nowrap">
                      <Text size="xs" c="dimmed" style={{ width: 80, flexShrink: 0 }}>Started</Text>
                      <Text size="sm">
                        {selectedConversation.startedAt
                          ? new Date(selectedConversation.startedAt).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: 'numeric',
                              minute: '2-digit',
                              hour12: true,
                            })
                          : '--'}
                      </Text>
                    </Group>
                    <Group gap={8} wrap="nowrap">
                      <Text size="xs" c="dimmed" style={{ width: 80, flexShrink: 0 }}>Last activity</Text>
                      <Text size="sm">
                        {selectedConversation.lastActivityAt
                          ? timeAgo(selectedConversation.lastActivityAt)
                          : '--'}
                      </Text>
                    </Group>
                    {selectedConversation.assignedTo && (
                      <Group gap={8} wrap="nowrap">
                        <Text size="xs" c="dimmed" style={{ width: 80, flexShrink: 0 }}>Assigned to</Text>
                        <Text size="sm">{selectedConversation.assignedTo}</Text>
                      </Group>
                    )}
                    {selectedConversation.status === 'escalated' && (
                      <Badge size="xs" variant="filled" color="red" mt={4}>
                        Escalated
                      </Badge>
                    )}
                  </Stack>
                </Box>

                <Divider />

                {/* Customer profile placeholder */}
                <Box p="md">
                  <Text size="xs" fw={600} c="dimmed" mb={8}>
                    Customer profile
                  </Text>
                  <Text size="xs" c="dimmed" fs="italic">
                    Customer details will be available once the customer profile API is connected.
                  </Text>
                </Box>
              </>
            ) : (
              <Box p="md">
                <Text size="sm" c="dimmed" ta="center" py="xl">
                  Select a conversation to view details.
                </Text>
              </Box>
            )}
          </Stack>
        </ScrollArea>
      </Box>
    </Box>
  );
}
