/**
 * Storybook stories for MessageBubble (SPEC-1845/WI-1502).
 *
 * Covers: user message, agent message, long message, streaming, retracted,
 * and system message variants.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { MessageBubble } from './MessageBubble';
import type { Message } from '@/state/store';
import { resolveTokens } from '@/theme/tokens';

// Default tokens for stories (light mode, Agent Red brand)
const tokens = resolveTokens({} as any);

const makeMessage = (overrides: Partial<Message>): Message => ({
  id: 'msg-001',
  role: 'customer',
  content: 'Hello, I need help with my order.',
  timestamp: Date.now(),
  ...overrides,
});

export default {
  title: 'Chat/MessageBubble',
  component: MessageBubble,
};

export const UserMessage = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({ role: 'customer', content: 'Hello, I need help with my order.' })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={true}
  />
);

export const AgentMessage = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({ role: 'agent', content: 'I can help you with that! What is your order number?' })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={true}
  />
);

export const LongMessage = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({
      role: 'agent',
      content: 'A'.repeat(500) + ' — this tests overflow handling for very long messages.',
    })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={true}
  />
);

export const StreamingMessage = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({ role: 'agent', content: 'Looking up your order...', streaming: true })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={true}
  />
);

export const RetractedMessage = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({ role: 'agent', content: 'This message was retracted.', retracted: true })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={true}
  />
);

export const SystemMessage = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({ role: 'system', content: 'Conversation has been escalated to a human agent.' })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={false}
  />
);

export const MessageWithMarkdownLink = () => (
  <MessageBubble
    tokens={tokens}
    message={makeMessage({
      role: 'agent',
      content: 'Please visit [our help center](https://help.example.com) for more information.',
    })}
    agentAvatarUrl={null}
    agentName="Agent Red"
    showAvatar={true}
  />
);
