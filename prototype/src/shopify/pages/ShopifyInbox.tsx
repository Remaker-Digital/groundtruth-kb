// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useRef, useEffect } from 'react';
import {
  Page,
  LegacyCard,
  TextField,
  Tabs,
  Badge,
  Button,
  Tag,
  Text,
  Divider,
  Box,
  InlineStack,
  BlockStack,
} from '@shopify/polaris';
import { CONVERSATIONS, MESSAGES, CUSTOMERS } from '../../data/mockData';
import type { Conversation, Message, Customer } from '../../data/mockData';

// ---------------------------------------------------------------------------
// Constants & Helpers
// ---------------------------------------------------------------------------

const AVATAR_PALETTE = ['#C41E2A', '#2563EB', '#059669', '#D97706', '#7C3AED', '#DB2777'];

const STATUS_BADGE_MAP: Record<Conversation['status'], { tone: 'info' | 'warning' | 'critical' | 'success'; label: string }> = {
  active: { tone: 'info', label: 'Active' },
  waiting: { tone: 'warning', label: 'Waiting' },
  escalated: { tone: 'critical', label: 'Escalated' },
  resolved: { tone: 'success', label: 'Resolved' },
};

function getInitials(name: string): string {
  return name.split(' ').map((n) => n[0]).join('').toUpperCase();
}

function avatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length];
}

function timeAgo(dateString: string): string {
  const now = new Date('2026-02-02T15:35:00Z');
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
// Sub-components
// ---------------------------------------------------------------------------

function AvatarCircle({ name, size = 36 }: { name: string; size?: number }) {
  const bg = avatarColor(name);
  const initials = getInitials(name);
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: bg,
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 600,
        fontSize: size * 0.36,
        flexShrink: 0,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      {initials}
    </div>
  );
}

function ConversationRow({
  conversation,
  isSelected,
  onClick,
}: {
  conversation: Conversation;
  isSelected: boolean;
  onClick: () => void;
}) {
  const badge = STATUS_BADGE_MAP[conversation.status];

  return (
    <div
      onClick={onClick}
      style={{
        padding: '12px 16px',
        cursor: 'pointer',
        background: isSelected ? '#f4f6f8' : 'transparent',
        borderLeft: isSelected ? '3px solid #2c6ecb' : '3px solid transparent',
        transition: 'background 0.1s',
      }}
      onMouseEnter={(e) => {
        if (!isSelected) e.currentTarget.style.background = '#f9fafb';
      }}
      onMouseLeave={(e) => {
        if (!isSelected) e.currentTarget.style.background = 'transparent';
      }}
    >
      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
        <AvatarCircle name={conversation.customerName} size={36} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 4 }}>
            <Text as="span" variant="bodyMd" fontWeight="semibold" truncate>
              {conversation.customerName}
            </Text>
            <Text as="span" variant="bodySm" tone="subdued">
              {timeAgo(conversation.updatedAt)}
            </Text>
          </div>
          <div style={{ marginTop: 2 }}>
            <Text as="span" variant="bodySm" tone="subdued" truncate>
              {truncate(conversation.lastMessage, 50)}
            </Text>
          </div>
          <div style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Badge tone={badge.tone} size="small">{badge.label}</Badge>
            {conversation.assignedTo && (
              <Text as="span" variant="bodySm" tone="subdued">{conversation.assignedTo}</Text>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  if (message.sender === 'system') {
    return (
      <div style={{ textAlign: 'center', padding: '12px 0' }}>
        <Text as="p" variant="bodySm" tone="subdued" alignment="center">
          <em>{message.text}</em>
        </Text>
        <Text as="p" variant="bodySm" tone="subdued" alignment="center">
          {formatTimestamp(message.timestamp)}
        </Text>
      </div>
    );
  }

  const isAgent = message.sender === 'agent';

  return (
    <div style={{ display: 'flex', justifyContent: isAgent ? 'flex-end' : 'flex-start', padding: '4px 0' }}>
      <div style={{ maxWidth: '75%' }}>
        <div style={{ marginBottom: 4, textAlign: isAgent ? 'right' : 'left' }}>
          <Text as="span" variant="bodySm" tone="subdued">{message.senderName}</Text>
        </div>
        <div
          style={{
            padding: '10px 14px',
            borderRadius: 12,
            background: isAgent ? '#e3f1df' : '#f4f6f8',
            borderBottomRightRadius: isAgent ? 4 : 12,
            borderBottomLeftRadius: !isAgent ? 4 : 12,
          }}
        >
          <Text as="p" variant="bodyMd">
            {message.text.split('\n').map((line, i) => (
              <React.Fragment key={i}>
                {i > 0 && <br />}
                {line}
              </React.Fragment>
            ))}
          </Text>
        </div>
        <div
          style={{
            marginTop: 4,
            display: 'flex',
            gap: 6,
            flexWrap: 'wrap',
            justifyContent: isAgent ? 'flex-end' : 'flex-start',
            alignItems: 'center',
          }}
        >
          <Text as="span" variant="bodySm" tone="subdued">{formatTimestamp(message.timestamp)}</Text>
          {isAgent && message.agentConfidence != null && (
            <Badge
              tone={message.agentConfidence >= 0.9 ? 'success' : message.agentConfidence >= 0.8 ? 'warning' : 'critical'}
              size="small"
            >
              {`${Math.round(message.agentConfidence * 100)}% confidence`}
            </Badge>
          )}
          {isAgent && message.memoryUsed && (
            <Badge tone="info" size="small">Memory</Badge>
          )}
          {isAgent && message.knowledgeSources && message.knowledgeSources.map((src) => (
            <Badge key={src} size="small">{src}</Badge>
          ))}
        </div>
      </div>
    </div>
  );
}

function MemoryProfileChecklist({ customer }: { customer: Customer }) {
  const layers: { key: keyof Customer['memoryProfile']; label: string }[] = [
    { key: 'purchaseHistory', label: 'Purchase History' },
    { key: 'productQuestions', label: 'Product Questions' },
    { key: 'geography', label: 'Geography' },
    { key: 'marketingSegments', label: 'Marketing Segments' },
    { key: 'jurisdictionCodes', label: 'Jurisdiction Codes' },
    { key: 'cartData', label: 'Cart Data' },
  ];

  return (
    <BlockStack gap="100">
      {layers.map(({ key, label }) => (
        <InlineStack key={key} gap="200" blockAlign="center" wrap={false}>
          <span style={{ color: customer.memoryProfile[key] ? '#059669' : '#8c9196', fontSize: 14 }}>
            {customer.memoryProfile[key] ? '\u2713' : '\u2715'}
          </span>
          <Text as="span" variant="bodySm" tone={customer.memoryProfile[key] ? undefined : 'subdued'}>
            {label}
          </Text>
        </InlineStack>
      ))}
    </BlockStack>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export function ShopifyInbox() {
  const [selectedId, setSelectedId] = useState('conv-001');
  const [activeTab, setActiveTab] = useState(0);
  const [search, setSearch] = useState('');
  const messageEndRef = useRef<HTMLDivElement>(null);

  const selectedConversation = CONVERSATIONS.find((c) => c.id === selectedId) || CONVERSATIONS[0];
  const selectedMessages = MESSAGES[selectedId] || [];
  const selectedCustomer = findCustomer(selectedConversation);

  // Filter map: tab index -> status filter
  const tabFilters: (string | null)[] = [null, 'active', 'waiting', 'escalated'];

  const filteredConversations = CONVERSATIONS.filter((c) => {
    const statusFilter = tabFilters[activeTab];
    if (statusFilter && c.status !== statusFilter) return false;
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

  // Counts for tabs
  const counts = {
    all: CONVERSATIONS.length,
    active: CONVERSATIONS.filter((c) => c.status === 'active').length,
    waiting: CONVERSATIONS.filter((c) => c.status === 'waiting').length,
    escalated: CONVERSATIONS.filter((c) => c.status === 'escalated').length,
  };

  // Scroll to bottom when conversation changes
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedId]);

  const tabs = [
    { id: 'all', content: `All (${counts.all})` },
    { id: 'active', content: `Active (${counts.active})` },
    { id: 'waiting', content: `Waiting (${counts.waiting})` },
    { id: 'escalated', content: `Escalated (${counts.escalated})` },
  ];

  const badge = STATUS_BADGE_MAP[selectedConversation.status];

  return (
    <Page
      title="Inbox"
      primaryAction={{ content: 'New conversation', disabled: true }}
    >
      <div style={{ display: 'flex', gap: 0, height: 'calc(100vh - 140px)', border: '1px solid #e1e3e5', borderRadius: 12, overflow: 'hidden', background: '#fff' }}>

        {/* ============================================================== */}
        {/* LEFT PANEL: Conversation List (280px)                           */}
        {/* ============================================================== */}
        <div style={{ width: 280, flexShrink: 0, display: 'flex', flexDirection: 'column', borderRight: '1px solid #e1e3e5', background: '#fff' }}>
          {/* Search */}
          <div style={{ padding: '12px 12px 0' }}>
            <TextField
              label=""
              labelHidden
              placeholder="Search conversations..."
              value={search}
              onChange={setSearch}
              autoComplete="off"
              clearButton
              onClearButtonClick={() => setSearch('')}
            />
          </div>

          {/* Tabs */}
          <div style={{ padding: '0 4px' }}>
            <Tabs tabs={tabs} selected={activeTab} onSelect={setActiveTab} fitted />
          </div>

          {/* Conversation list */}
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {filteredConversations.length === 0 ? (
              <div style={{ padding: 24, textAlign: 'center' }}>
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  No conversations found
                </Text>
              </div>
            ) : (
              filteredConversations.map((conv) => (
                <ConversationRow
                  key={conv.id}
                  conversation={conv}
                  isSelected={conv.id === selectedId}
                  onClick={() => setSelectedId(conv.id)}
                />
              ))
            )}
          </div>
        </div>

        {/* ============================================================== */}
        {/* CENTER PANEL: Message Thread (flex: 1)                          */}
        {/* ============================================================== */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#fafbfb', minWidth: 0 }}>
          {/* Thread header */}
          <div style={{ padding: '12px 20px', background: '#fff', borderBottom: '1px solid #e1e3e5' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'nowrap' }}>
              <div style={{ minWidth: 0, flex: 1 }}>
                <InlineStack gap="200" blockAlign="center" wrap={false}>
                  <Text as="span" variant="headingSm" fontWeight="semibold" truncate>
                    {selectedConversation.customerName}
                  </Text>
                  <Badge tone={badge.tone} size="small">{badge.label}</Badge>
                </InlineStack>
                <div style={{ marginTop: 2 }}>
                  <Text as="span" variant="bodySm" tone="subdued" truncate>
                    {selectedConversation.subject}
                    {selectedConversation.assignedTo && ` \u00B7 Assigned to ${selectedConversation.assignedTo}`}
                  </Text>
                </div>
              </div>
              <InlineStack gap="200">
                <Button size="slim" variant="secondary" disabled>Assign</Button>
                <Button size="slim" variant="secondary" tone="critical" disabled>Escalate</Button>
                <Button size="slim" variant="secondary" disabled>Resolve</Button>
              </InlineStack>
            </div>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>
            {selectedMessages.length === 0 ? (
              <div style={{ textAlign: 'center', paddingTop: 80 }}>
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  No messages loaded for this conversation.
                </Text>
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  Prototype includes messages for conv-001 and conv-004.
                </Text>
              </div>
            ) : (
              <BlockStack gap="200">
                {selectedMessages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
                <div ref={messageEndRef} />
              </BlockStack>
            )}
          </div>

          {/* Message input */}
          <div style={{ padding: '12px 20px', background: '#fff', borderTop: '1px solid #e1e3e5' }}>
            <InlineStack gap="200" blockAlign="end" wrap={false}>
              <div style={{ flex: 1 }}>
                <TextField
                  label=""
                  labelHidden
                  placeholder="Type a message... (prototype - disabled)"
                  value=""
                  onChange={() => {}}
                  autoComplete="off"
                  disabled
                />
              </div>
              <Button variant="primary" disabled>Send</Button>
            </InlineStack>
          </div>
        </div>

        {/* ============================================================== */}
        {/* RIGHT PANEL: Customer Details (300px)                           */}
        {/* ============================================================== */}
        <div style={{ width: 300, flexShrink: 0, borderLeft: '1px solid #e1e3e5', background: '#fff', overflowY: 'auto' }}>
          <LegacyCard>
            {/* Customer header */}
            <LegacyCard.Section>
              <div style={{ textAlign: 'center' }}>
                <AvatarCircle name={selectedCustomer?.name || selectedConversation.customerName} size={56} />
                <div style={{ marginTop: 8 }}>
                  <Text as="p" variant="headingSm" fontWeight="semibold" alignment="center">
                    {selectedCustomer?.name || selectedConversation.customerName}
                  </Text>
                </div>
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  {selectedCustomer?.email || selectedConversation.customerEmail}
                </Text>
                {selectedCustomer && (
                  <div style={{ marginTop: 6, display: 'flex', justifyContent: 'center' }}>
                    <Badge tone="info" size="small">{selectedCustomer.segment}</Badge>
                  </div>
                )}
              </div>
            </LegacyCard.Section>

            {selectedCustomer && (
              <>
                {/* Customer Info */}
                <LegacyCard.Section title="Customer Info">
                  <BlockStack gap="200">
                    <InlineStack gap="200" blockAlign="center">
                      <Text as="span" variant="bodySm" tone="subdued">Location:</Text>
                      <Text as="span" variant="bodySm">{selectedCustomer.location}</Text>
                    </InlineStack>
                    <InlineStack gap="200" blockAlign="center">
                      <Text as="span" variant="bodySm" tone="subdued">Orders:</Text>
                      <Text as="span" variant="bodySm">
                        {selectedCustomer.totalOrders} orders &middot; ${selectedCustomer.totalSpent.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </Text>
                    </InlineStack>
                    <InlineStack gap="200" blockAlign="center">
                      <Text as="span" variant="bodySm" tone="subdued">Last order:</Text>
                      <Text as="span" variant="bodySm">
                        {new Date(selectedCustomer.lastOrder).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </Text>
                    </InlineStack>
                    <InlineStack gap="200" blockAlign="center">
                      <Text as="span" variant="bodySm" tone="subdued">Satisfaction:</Text>
                      <Text as="span" variant="bodySm">{selectedCustomer.satisfaction.toFixed(1)} / 5.0</Text>
                    </InlineStack>
                    <InlineStack gap="200" blockAlign="center">
                      <Text as="span" variant="bodySm" tone="subdued">Style:</Text>
                      <Text as="span" variant="bodySm">{selectedCustomer.communicationStyle}</Text>
                    </InlineStack>
                  </BlockStack>
                </LegacyCard.Section>

                {/* Memory Profile */}
                <LegacyCard.Section title="Memory Profile">
                  <MemoryProfileChecklist customer={selectedCustomer} />
                </LegacyCard.Section>

                {/* Tags */}
                <LegacyCard.Section title="Tags">
                  <InlineStack gap="200" wrap>
                    {selectedCustomer.tags.map((tag) => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </InlineStack>
                </LegacyCard.Section>

                {/* Recent Activity */}
                <LegacyCard.Section title="Recent Activity">
                  <BlockStack gap="200">
                    {CONVERSATIONS.filter((c) => c.customerEmail === selectedCustomer.email).map((conv) => {
                      const convBadge = STATUS_BADGE_MAP[conv.status];
                      return (
                        <div
                          key={conv.id}
                          style={{
                            padding: '8px 10px',
                            borderRadius: 8,
                            background: conv.id === selectedId ? '#f4f6f8' : '#fafbfb',
                            cursor: 'pointer',
                            border: conv.id === selectedId ? '1px solid #c9cccf' : '1px solid transparent',
                          }}
                          onClick={() => setSelectedId(conv.id)}
                        >
                          <Text as="p" variant="bodySm" fontWeight="medium" truncate>
                            {conv.subject}
                          </Text>
                          <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                            <Badge tone={convBadge.tone} size="small">{convBadge.label}</Badge>
                            <Text as="span" variant="bodySm" tone="subdued">{timeAgo(conv.updatedAt)}</Text>
                          </div>
                        </div>
                      );
                    })}
                  </BlockStack>
                </LegacyCard.Section>
              </>
            )}

            {!selectedCustomer && (
              <LegacyCard.Section>
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  Customer details not available.
                </Text>
                <Text as="p" variant="bodySm" tone="subdued" alignment="center">
                  Profile data exists for Sarah Chen and James Wilson only.
                </Text>
              </LegacyCard.Section>
            )}
          </LegacyCard>
        </div>
      </div>
    </Page>
  );
}
