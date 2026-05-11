// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Storybook stories for MessageList (SPEC-1845/WI-1502).
 *
 * Covers: empty state, single message, conversation, typing indicator,
 * greeting message, and scroll overflow.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { MessageList } from './MessageList';
import type { Message } from '@/state/store';
import { resolveTokens } from '@/theme/tokens';
import { en } from '@/locale/en';

// Default tokens for stories (light mode, Agent Red brand)
const tokens = resolveTokens({} as any);

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------

const makeMsg = (id: string, role: 'customer' | 'agent' | 'system', content: string, minutesAgo = 0): Message => ({
  id,
  role,
  content,
  timestamp: Date.now() - minutesAgo * 60 * 1000,
});

const Wrapper = ({ children }: { children: any }) => (
  <div style={{ width: '380px', height: '500px', border: '1px solid #e0e0e0' }}>
    {children}
  </div>
);

export default {
  title: 'Chat/MessageList',
  component: MessageList,
};

// ---------------------------------------------------------------------------
// Story variants
// ---------------------------------------------------------------------------

export const Empty = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={[]}
      isAgentTyping={false}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage="Hi! How can I help you today?"
      quickActions={[]}
    />
  </Wrapper>
);

export const SingleMessage = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={[makeMsg('1', 'customer', 'Hello, I have a question about my order.')]}
      isAgentTyping={false}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage={null}
      quickActions={[]}
    />
  </Wrapper>
);

export const Conversation = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={[
        makeMsg('1', 'customer', 'Hello, I need help with order #12345.', 5),
        makeMsg('2', 'agent', 'I can help with that! Let me look up your order.', 4),
        makeMsg('3', 'agent', 'I found order #12345. It was shipped yesterday and should arrive by Friday.', 3),
        makeMsg('4', 'customer', 'Great, thanks! Can I change the delivery address?', 2),
        makeMsg('5', 'agent', 'Yes, I can update the delivery address for you. What is the new address?', 1),
      ]}
      isAgentTyping={false}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage={null}
      quickActions={[]}
    />
  </Wrapper>
);

export const WithTypingIndicator = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={[makeMsg('1', 'customer', 'What is your return policy?')]}
      isAgentTyping={true}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage={null}
      quickActions={[]}
    />
  </Wrapper>
);

export const WithGreeting = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={[]}
      isAgentTyping={false}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage="Welcome to Agent Red! Ask me anything about your orders, shipping, or returns."
      quickActions={[]}
    />
  </Wrapper>
);

export const ScrollOverflow = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={Array.from({ length: 30 }, (_, i) => makeMsg(
        `msg-${i}`,
        i % 2 === 0 ? 'customer' : 'agent',
        `Message ${i + 1}: ${'Lorem ipsum dolor sit amet. '.repeat(2)}`,
        30 - i,
      ))}
      isAgentTyping={false}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage={null}
      quickActions={[]}
    />
  </Wrapper>
);

export const WithQuickActions = () => (
  <Wrapper>
    <MessageList
      tokens={tokens}
      locale={en}
      messages={[]}
      isAgentTyping={false}
      agentName="Agent Red"
      agentAvatarUrl={null}
      greetingMessage="How can I help you today?"
      quickActions={[
        { id: 'qa1', label: 'Track my order', prompt_template: 'Where is my order?' },
        { id: 'qa2', label: 'Return an item', prompt_template: 'I want to return an item' },
        { id: 'qa3', label: 'Contact support', prompt_template: 'I need to speak to a human' },
      ]}
    />
  </Wrapper>
);
