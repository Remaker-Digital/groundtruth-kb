/**
 * SPEC-1867: Structured answer block widget coverage.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h } from 'preact';
import { cleanup, fireEvent, render, screen } from '@testing-library/preact';
import { afterEach, describe, expect, it } from 'vitest';
import { AnswerBlocks } from '../src/components/AnswerBlocks';
import { MessageBubble } from '../src/components/MessageBubble';
import { en } from '../src/locale/en';
import { createStore, type AnswerBlock, type Message } from '../src/state/store';
import { resolveTokens, type WidgetConfig } from '../src/theme/tokens';

const config = { widget_header_text: 'Agent Red Test' } as WidgetConfig;
const tokens = resolveTokens(config);

const blocks: AnswerBlock[] = [
  {
    type: 'steps',
    title: 'Return checklist',
    items: ['Find your order number', 'Print the return label'],
  },
  {
    type: 'faq',
    items: [
      {
        question: 'Can I exchange instead?',
        answer: 'Yes, choose exchange during the return flow.',
      },
    ],
  },
  {
    type: 'action',
    label: 'Start Return',
    url: 'https://example.com/returns',
    style: 'primary',
  },
];

afterEach(() => {
  cleanup();
});

describe('Store structured answer block preservation', () => {
  it('finalizes the streaming agent message with fallback text and blocks', () => {
    const store = createStore(config, en);
    store.addMessage({
      id: 'msg-streaming',
      role: 'agent',
      content: 'Thinking...',
      timestamp: Date.now(),
      streaming: true,
    });

    store.updateLastAgentMessage('Here are the return steps.', false, undefined, blocks);

    const [message] = store.getState().messages;
    expect(message.content).toBe('Here are the return steps.');
    expect(message.streaming).toBe(false);
    expect(message.blocks).toEqual(blocks);
  });
});

describe('AnswerBlocks rendering', () => {
  it('renders steps, FAQ interaction, and action link blocks', () => {
    render(<AnswerBlocks blocks={blocks} tokens={tokens} />);

    expect(screen.getByText('Return checklist')).toBeTruthy();
    expect(screen.getByText('Find your order number')).toBeTruthy();
    expect(screen.getByText('Print the return label')).toBeTruthy();

    fireEvent.click(screen.getByRole('button', { name: /Can I exchange instead/i }));
    expect(screen.getByText('Yes, choose exchange during the return flow.')).toBeTruthy();

    const actionLink = screen.getByRole('link', { name: /Start Return/i });
    expect(actionLink.getAttribute('href')).toBe('https://example.com/returns');
  });
});

describe('MessageBubble structured block rendering', () => {
  function renderBubble(message: Message) {
    render(
      <MessageBubble
        tokens={tokens}
        locale={en}
        message={message}
        agentAvatarUrl={null}
        agentName="AI Assistant"
        showAvatar={false}
      />,
    );
  }

  it('renders fallback text plus blocks for completed agent messages', () => {
    renderBubble({
      id: 'msg-agent',
      role: 'agent',
      content: 'Here are the return steps.',
      timestamp: Date.now(),
      streaming: false,
      blocks,
    });

    expect(screen.getByText('Here are the return steps.')).toBeTruthy();
    expect(screen.getByText('Return checklist')).toBeTruthy();
    expect(screen.getByText('Find your order number')).toBeTruthy();
    expect(screen.getByRole('link', { name: /Start Return/i })).toBeTruthy();
  });

  it('suppresses blocks for customer and still-streaming messages', () => {
    renderBubble({
      id: 'msg-customer',
      role: 'customer',
      content: 'I can see my own text.',
      timestamp: Date.now(),
      blocks,
    });
    expect(screen.getByText('I can see my own text.')).toBeTruthy();
    expect(screen.queryByText('Return checklist')).toBeNull();

    cleanup();

    renderBubble({
      id: 'msg-streaming-agent',
      role: 'agent',
      content: 'Still streaming.',
      timestamp: Date.now(),
      streaming: true,
      blocks,
    });
    expect(screen.getByText('Still streaming.')).toBeTruthy();
    expect(screen.queryByText('Return checklist')).toBeNull();
  });
});
