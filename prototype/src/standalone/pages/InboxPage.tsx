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
  useComputedColorScheme,
} from '@mantine/core';
import { CONVERSATIONS, MESSAGES, CUSTOMERS } from '../../data/mockData';
import type { Conversation, Message, Customer } from '../../data/mockData';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const BRAND = '#C41E2A';
const BRAND_LIGHT = '#FFF1F2';
const HEADER_HEIGHT = 56;
const PAGE_PADDING = 16; // Mantine "md" padding

const STATUS_COLORS: Record<Conversation['status'], string> = {
  active: 'blue',
  waiting: 'yellow',
  escalated: 'red',
  resolved: 'green',
};

const PRIORITY_COLORS: Record<Conversation['priority'], string> = {
  low: '#94a3b8',
  medium: '#f59e0b',
  high: '#f97316',
  urgent: '#ef4444',
};

const AVATAR_PALETTE = ['#C41E2A', '#2563EB', '#059669', '#D97706', '#7C3AED', '#DB2777'];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();
}

function avatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length];
}

function timeAgo(dateString: string): string {
  const now = new Date('2026-02-02T15:35:00Z'); // fixed "now" matching mock data context
  const then = new Date(dateString);
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days}d`;
}

function formatTimestamp(dateString: string): string {
  const d = new Date(dateString);
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}

function truncate(text: string, max: number): string {
  return text.length > max ? text.slice(0, max) + '...' : text;
}

function findCustomer(conversation: Conversation): Customer | undefined {
  return CUSTOMERS.find((c) => c.email === conversation.customerEmail);
}

// ---------------------------------------------------------------------------
// Inline SVG Icons (consistent with StandaloneApp pattern)
// ---------------------------------------------------------------------------

const SearchIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const UserAssignIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="8.5" cy="7" r="4" />
    <line x1="20" y1="8" x2="20" y2="14" />
    <line x1="23" y1="11" x2="17" y2="11" />
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

const MapPinIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

const ShoppingBagIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
    <line x1="3" y1="6" x2="21" y2="6" />
    <path d="M16 10a4 4 0 0 1-8 0" />
  </svg>
);

const StarIcon = ({ filled }: { filled: boolean }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill={filled ? '#f59e0b' : 'none'} stroke={filled ? '#f59e0b' : '#94a3b8'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);

const MemoryChipIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="4" width="16" height="16" rx="2" ry="2" />
    <rect x="9" y="9" width="6" height="6" />
    <line x1="9" y1="1" x2="9" y2="4" />
    <line x1="15" y1="1" x2="15" y2="4" />
    <line x1="9" y1="20" x2="9" y2="23" />
    <line x1="15" y1="20" x2="15" y2="23" />
    <line x1="20" y1="9" x2="23" y2="9" />
    <line x1="20" y1="14" x2="23" y2="14" />
    <line x1="1" y1="9" x2="4" y2="9" />
    <line x1="1" y1="14" x2="4" y2="14" />
  </svg>
);

const CheckCircleIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

const XCircleIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="15" y1="9" x2="9" y2="15" />
    <line x1="9" y1="9" x2="15" y2="15" />
  </svg>
);

const MessageSquareIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
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
  conversation: Conversation;
  isSelected: boolean;
  onClick: () => void;
  selectedBgColor?: string;
  hoverBgColor?: string;
}) {
  const initials = getInitials(conversation.customerName);
  const color = avatarColor(conversation.customerName);
  const isUnread = conversation.status === 'active' || conversation.status === 'escalated';
  const selBg = selectedBgColor || BRAND_LIGHT;
  const hovBg = hoverBgColor || '#f8f9fa';

  return (
    <Box
      onClick={onClick}
      style={{
        padding: '10px 12px',
        borderRadius: 8,
        cursor: 'pointer',
        background: isSelected ? selBg : 'transparent',
        borderLeft: isSelected ? `3px solid ${BRAND}` : '3px solid transparent',
        transition: 'background 0.15s',
      }}
      onMouseEnter={(e: React.MouseEvent<HTMLDivElement>) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = hovBg;
      }}
      onMouseLeave={(e: React.MouseEvent<HTMLDivElement>) => {
        if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = 'transparent';
      }}
    >
      <Group gap={10} align="flex-start" wrap="nowrap">
        {/* Avatar */}
        <Box style={{ position: 'relative', flexShrink: 0 }}>
          <Avatar size={38} radius="xl" color={color} style={{ background: color, color: '#fff', fontWeight: 600, fontSize: 14 }}>
            {initials}
          </Avatar>
          {/* Priority dot */}
          <Box
            style={{
              position: 'absolute',
              bottom: -1,
              right: -1,
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: PRIORITY_COLORS[conversation.priority],
              border: '2px solid #fff',
            }}
          />
        </Box>

        {/* Content */}
        <Box style={{ flex: 1, minWidth: 0 }}>
          <Group justify="space-between" wrap="nowrap" gap={4}>
            <Text size="sm" fw={isUnread ? 700 : 500} truncate style={{ flex: 1 }}>
              {conversation.customerName}
            </Text>
            <Text size="xs" c="dimmed" style={{ flexShrink: 0 }}>
              {timeAgo(conversation.updatedAt)}
            </Text>
          </Group>
          <Text size="xs" c="dimmed" truncate mt={2}>
            {truncate(conversation.lastMessage, 55)}
          </Text>
          <Group gap={6} mt={4}>
            <Badge
              size="xs"
              variant="light"
              color={STATUS_COLORS[conversation.status]}
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
                  background: BRAND,
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
function MessageBubble({ message, agentBubbleBg, customerBubbleBg }: { message: Message; agentBubbleBg?: string; customerBubbleBg?: string }) {
  if (message.sender === 'system') {
    return (
      <Box style={{ textAlign: 'center', padding: '8px 0' }}>
        <Text size="xs" c="dimmed" fs="italic">
          {message.text}
        </Text>
        <Text size="xs" c="dimmed" mt={2}>
          {formatTimestamp(message.timestamp)}
        </Text>
      </Box>
    );
  }

  const isAgent = message.sender === 'agent';
  const agentBg = agentBubbleBg || BRAND_LIGHT;
  const custBg = customerBubbleBg || '#f1f3f5';
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
              {message.senderName}
            </Text>
            <img
              src="/logo/icon-master.svg"
              alt="Agent Red"
              style={{ height: 16, width: 16, display: 'block', opacity: 0.85 }}
            />
          </Group>
        ) : (
          <Text size="xs" c="dimmed" mb={2} ta="left">
            {message.senderName}
          </Text>
        )}

        {/* Bubble */}
        <Paper
          p="sm"
          radius="lg"
          style={{
            background: isAgent ? agentBg : custBg,
            borderBottomRightRadius: isAgent ? 4 : undefined,
            borderBottomLeftRadius: !isAgent ? 4 : undefined,
          }}
        >
          <Text size="sm" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.55 }}>
            {message.text}
          </Text>
        </Paper>

        {/* Metadata row */}
        <Group
          gap={6}
          mt={4}
          justify={isAgent ? 'flex-end' : 'flex-start'}
          wrap="wrap"
        >
          <Text size="xs" c="dimmed">
            {formatTimestamp(message.timestamp)}
          </Text>
          {isAgent && message.agentConfidence != null && (
            <Tooltip label={`AI confidence: ${Math.round(message.agentConfidence * 100)}%`}>
              <Badge
                size="xs"
                variant="light"
                color={message.agentConfidence >= 0.9 ? 'green' : message.agentConfidence >= 0.8 ? 'yellow' : 'red'}
              >
                {Math.round(message.agentConfidence * 100)}%
              </Badge>
            </Tooltip>
          )}
          {isAgent && message.memoryUsed && (
            <Tooltip label="Response used Persistent Customer Memory">
              <Badge size="xs" variant="light" color="violet" leftSection={<MemoryChipIcon />}>
                Memory
              </Badge>
            </Tooltip>
          )}
          {isAgent &&
            message.knowledgeSources &&
            message.knowledgeSources.map((src) => (
              <Badge key={src} size="xs" variant="outline" color="gray">
                {src}
              </Badge>
            ))}
        </Group>
      </Box>
    </Box>
  );
}

/** Right panel: memory profile section */
function MemoryProfileSection({ customer }: { customer: Customer }) {
  const layers: { key: keyof Customer['memoryProfile']; label: string }[] = [
    { key: 'purchaseHistory', label: 'Purchase History' },
    { key: 'productQuestions', label: 'Product Questions' },
    { key: 'geography', label: 'Geography' },
    { key: 'marketingSegments', label: 'Marketing Segments' },
    { key: 'jurisdictionCodes', label: 'Jurisdiction Codes' },
    { key: 'cartData', label: 'Cart Data' },
  ];

  return (
    <Stack gap={4}>
      {layers.map(({ key, label }) => (
        <Group key={key} gap={8} wrap="nowrap">
          {customer.memoryProfile[key] ? <CheckCircleIcon /> : <XCircleIcon />}
          <Text size="xs" c={customer.memoryProfile[key] ? undefined : 'dimmed'}>
            {label}
          </Text>
        </Group>
      ))}
    </Stack>
  );
}

/** Right panel: star rating */
function StarRating({ rating }: { rating: number }) {
  const stars = [];
  for (let i = 1; i <= 5; i++) {
    stars.push(<StarIcon key={i} filled={i <= Math.round(rating)} />);
  }
  return (
    <Group gap={2}>
      {stars}
      <Text size="xs" c="dimmed" ml={4}>
        {rating.toFixed(1)}
      </Text>
    </Group>
  );
}

// ---------------------------------------------------------------------------
// Main InboxPage Component
// ---------------------------------------------------------------------------

export function InboxPage() {
  const [selectedId, setSelectedId] = useState('conv-001');
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const messageEndRef = useRef<HTMLDivElement>(null);
  const computedColorScheme = useComputedColorScheme('dark');
  const isDark = computedColorScheme === 'dark';

  // Dark-mode-aware colors
  const panelBg = isDark ? '#1E1E1E' : '#fff';
  const centerBg = isDark ? '#111111' : '#fafafa';
  const borderColor = isDark ? 'rgba(255,255,255,0.06)' : 'var(--mantine-color-gray-2)';
  const hoverBg = isDark ? 'rgba(255,255,255,0.04)' : '#f8f9fa';
  const selectedBg = isDark ? 'rgba(196, 30, 42, 0.1)' : BRAND_LIGHT;
  const bubbleAgentBg = isDark ? 'rgba(255,255,255,0.08)' : '#f1f3f5';
  const bubbleCustomerBg = isDark ? 'rgba(255,255,255,0.06)' : '#f1f3f5';

  const selectedConversation = CONVERSATIONS.find((c) => c.id === selectedId) || CONVERSATIONS[0];
  const selectedMessages = MESSAGES[selectedId] || [];
  const selectedCustomer = findCustomer(selectedConversation);

  // Filter conversations
  const filteredConversations = CONVERSATIONS.filter((c) => {
    if (filter !== 'all' && c.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        c.customerName.toLowerCase().includes(q) ||
        c.lastMessage.toLowerCase().includes(q) ||
        c.subject.toLowerCase().includes(q)
      );
    }
    return true;
  });

  // Scroll to bottom of messages when conversation changes
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedId]);

  // Unread count per filter
  const counts = {
    all: CONVERSATIONS.length,
    active: CONVERSATIONS.filter((c) => c.status === 'active').length,
    waiting: CONVERSATIONS.filter((c) => c.status === 'waiting').length,
    escalated: CONVERSATIONS.filter((c) => c.status === 'escalated').length,
  };

  // Conversations that belong to this customer (for right panel history)
  const customerConversations = selectedCustomer
    ? CONVERSATIONS.filter((c) => c.customerEmail === selectedCustomer.email)
    : [];

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
              input: { borderColor: 'var(--mantine-color-gray-3)' },
            }}
          />
        </Box>

        {/* Filter tabs */}
        <Box p="sm" pb="xs">
          <SegmentedControl
            value={filter}
            onChange={setFilter}
            size="xs"
            fullWidth
            data={[
              { label: `All (${counts.all})`, value: 'all' },
              { label: `Active (${counts.active})`, value: 'active' },
              { label: `Waiting (${counts.waiting})`, value: 'waiting' },
              { label: `Escalated (${counts.escalated})`, value: 'escalated' },
            ]}
            styles={{
              root: { background: isDark ? 'rgba(255,255,255,0.04)' : 'var(--mantine-color-gray-0)' },
            }}
          />
        </Box>

        <Divider />

        {/* Conversation list */}
        <ScrollArea style={{ flex: 1 }} type="auto" offsetScrollbars>
          <Stack gap={0} p={4}>
            {filteredConversations.length === 0 ? (
              <Text size="sm" c="dimmed" ta="center" py="xl">
                No conversations found
              </Text>
            ) : (
              filteredConversations.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isSelected={conv.id === selectedId}
                  onClick={() => setSelectedId(conv.id)}
                  selectedBgColor={selectedBg}
                  hoverBgColor={hoverBg}
                />
              ))
            )}
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
          <Group justify="space-between" wrap="nowrap">
            <Box style={{ minWidth: 0 }}>
              <Group gap={8} wrap="nowrap">
                <Text size="md" fw={600} truncate>
                  {selectedConversation.customerName}
                </Text>
                <Badge
                  size="sm"
                  variant="light"
                  color={STATUS_COLORS[selectedConversation.status]}
                  style={{ textTransform: 'capitalize' }}
                >
                  {selectedConversation.status}
                </Badge>
                {selectedConversation.priority === 'high' || selectedConversation.priority === 'urgent' ? (
                  <Badge size="sm" variant="filled" color={selectedConversation.priority === 'urgent' ? 'red' : 'orange'}>
                    {selectedConversation.priority}
                  </Badge>
                ) : null}
              </Group>
              <Text size="xs" c="dimmed" mt={2} truncate>
                {selectedConversation.subject}
                {selectedConversation.assignedTo && (
                  <> &middot; Assigned to {selectedConversation.assignedTo}</>
                )}
              </Text>
            </Box>
            <Group gap={4} style={{ flexShrink: 0 }}>
              <Tooltip label="Assign to agent">
                <ActionIcon variant="subtle" color="gray" size="md">
                  <UserAssignIcon />
                </ActionIcon>
              </Tooltip>
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
        </Box>

        {/* Messages */}
        <ScrollArea style={{ flex: 1 }} type="auto" offsetScrollbars>
          <Box px="md" py="sm">
            {selectedMessages.length === 0 ? (
              <Box style={{ textAlign: 'center', paddingTop: 80 }}>
                <Text c="dimmed" size="sm">
                  No messages loaded for this conversation.
                </Text>
                <Text c="dimmed" size="xs" mt={4}>
                  Prototype only includes messages for conv-001 and conv-004.
                </Text>
              </Box>
            ) : (
              <Stack gap={8}>
                {selectedMessages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} agentBubbleBg={bubbleAgentBg} customerBubbleBg={bubbleCustomerBg} />
                ))}
                <div ref={messageEndRef} />
              </Stack>
            )}
          </Box>
        </ScrollArea>

        {/* Message input */}
        <Box
          px="md"
          py="sm"
          style={{
            background: panelBg,
            borderTop: `1px solid ${borderColor}`,
          }}
        >
          <Group gap={8} wrap="nowrap">
            <TextInput
              placeholder="Type a message... (prototype - disabled)"
              size="sm"
              disabled
              style={{ flex: 1 }}
              styles={{
                input: {
                  borderColor: 'var(--mantine-color-gray-3)',
                  '&:disabled': { background: '#fafafa' },
                },
              }}
            />
            <Tooltip label="Send (disabled in prototype)">
              <ActionIcon
                size="lg"
                variant="filled"
                color="brand"
                disabled
                radius="md"
              >
                <SendIcon />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Box>
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
            <Box p="md" style={{ textAlign: 'center' }}>
              <Avatar
                size={64}
                radius="xl"
                mx="auto"
                style={{
                  background: selectedCustomer
                    ? avatarColor(selectedCustomer.name)
                    : '#94a3b8',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: 22,
                }}
              >
                {selectedCustomer
                  ? getInitials(selectedCustomer.name)
                  : getInitials(selectedConversation.customerName)}
              </Avatar>
              <Text size="md" fw={600} mt={8}>
                {selectedCustomer?.name || selectedConversation.customerName}
              </Text>
              <Text size="xs" c="dimmed">
                {selectedCustomer?.email || selectedConversation.customerEmail}
              </Text>
              {selectedCustomer && (
                <Badge size="xs" variant="light" color="blue" mt={6}>
                  {selectedCustomer.segment}
                </Badge>
              )}
            </Box>

            <Divider />

            {/* Customer Info */}
            {selectedCustomer && (
              <>
                <Box p="md">
                  <Text size="xs" fw={600} tt="uppercase" c="dimmed" mb={8}>
                    Customer Info
                  </Text>
                  <Stack gap={8}>
                    <Group gap={8} wrap="nowrap">
                      <MapPinIcon />
                      <Text size="sm">{selectedCustomer.location}</Text>
                    </Group>
                    <Group gap={8} wrap="nowrap">
                      <ShoppingBagIcon />
                      <Text size="sm">
                        {selectedCustomer.totalOrders} orders &middot; ${selectedCustomer.totalSpent.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </Text>
                    </Group>
                    <Group gap={8} wrap="nowrap">
                      <Box style={{ width: 14, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Box
                          style={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            background: '#059669',
                          }}
                        />
                      </Box>
                      <Text size="sm">
                        Last order: {new Date(selectedCustomer.lastOrder).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </Text>
                    </Group>
                    <Group gap={8} wrap="nowrap">
                      <MessageSquareIcon />
                      <Text size="sm">
                        {selectedCustomer.conversationCount} conversations
                      </Text>
                    </Group>
                  </Stack>
                </Box>

                <Divider />

                {/* Memory Profile */}
                <Box p="md">
                  <Text size="xs" fw={600} tt="uppercase" c="dimmed" mb={8}>
                    Memory Profile
                  </Text>
                  <MemoryProfileSection customer={selectedCustomer} />
                </Box>

                <Divider />

                {/* Satisfaction */}
                <Box p="md">
                  <Text size="xs" fw={600} tt="uppercase" c="dimmed" mb={8}>
                    Satisfaction
                  </Text>
                  <StarRating rating={selectedCustomer.satisfaction} />
                  <Text size="xs" c="dimmed" mt={4}>
                    Preferred: {selectedCustomer.communicationStyle}
                  </Text>
                </Box>

                <Divider />

                {/* Tags */}
                <Box p="md">
                  <Text size="xs" fw={600} tt="uppercase" c="dimmed" mb={8}>
                    Tags
                  </Text>
                  <Group gap={6}>
                    {selectedCustomer.tags.map((tag) => (
                      <Badge key={tag} size="sm" variant="outline" color="gray">
                        {tag}
                      </Badge>
                    ))}
                  </Group>
                </Box>

                <Divider />

                {/* Conversation History */}
                <Box p="md">
                  <Text size="xs" fw={600} tt="uppercase" c="dimmed" mb={8}>
                    Conversation History
                  </Text>
                  <Stack gap={6}>
                    {customerConversations.map((conv) => (
                      <Paper
                        key={conv.id}
                        p="xs"
                        radius="sm"
                        style={{
                          background: conv.id === selectedId
                            ? (isDark ? 'rgba(196, 30, 42, 0.12)' : BRAND_LIGHT)
                            : (isDark ? 'rgba(255,255,255,0.04)' : 'var(--mantine-color-gray-0)'),
                          cursor: 'pointer',
                          border: conv.id === selectedId
                            ? `1px solid ${isDark ? 'rgba(196, 30, 42, 0.25)' : BRAND + '40'}`
                            : '1px solid transparent',
                        }}
                        onClick={() => setSelectedId(conv.id)}
                      >
                        <Text size="xs" fw={500} truncate>
                          {conv.subject}
                        </Text>
                        <Group gap={6} mt={2}>
                          <Badge
                            size="xs"
                            variant="light"
                            color={STATUS_COLORS[conv.status]}
                            style={{ textTransform: 'capitalize' }}
                          >
                            {conv.status}
                          </Badge>
                          <Text size="xs" c="dimmed">
                            {timeAgo(conv.updatedAt)}
                          </Text>
                        </Group>
                      </Paper>
                    ))}
                    {customerConversations.length === 0 && (
                      <Text size="xs" c="dimmed">
                        No previous conversations
                      </Text>
                    )}
                  </Stack>
                </Box>
              </>
            )}

            {/* Fallback when customer record not found */}
            {!selectedCustomer && (
              <Box p="md">
                <Text size="sm" c="dimmed" ta="center">
                  Customer details not available.
                </Text>
                <Text size="xs" c="dimmed" ta="center" mt={4}>
                  Profile data exists for Sarah Chen and James Wilson only.
                </Text>
              </Box>
            )}
          </Stack>
        </ScrollArea>
      </Box>
    </Box>
  );
}
