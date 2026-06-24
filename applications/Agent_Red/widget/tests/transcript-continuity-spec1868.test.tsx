/**
 * SPEC-1868: Transcript continuity live-module coverage.
 *
 * Covers the restore transport and rendered continuation separator using
 * the production widget modules instead of mirrored logic.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h } from 'preact';
import { cleanup, render, screen } from '@testing-library/preact';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { MessageList } from '../src/components/MessageList';
import { en } from '../src/locale/en';
import { createStore } from '../src/state/store';
import { configureTransport, fetchConversation } from '../src/transport/http';
import { resolveTokens, type WidgetConfig } from '../src/theme/tokens';

const API_BASE_URL = 'https://api.agentred.test';
const WIDGET_KEY = 'pk_live_transcript_continuity';

const config = { widget_header_text: 'Agent Red Test' } as WidgetConfig;
const tokens = resolveTokens(config);

const backendMessages = [
  {
    message_id: 'msg-restored-customer',
    role: 'customer',
    content: 'Can I continue where I left off?',
    timestamp: '2026-04-01T10:00:00Z',
    metadata: {},
  },
  {
    message_id: 'msg-restored-agent',
    role: 'ai',
    content: 'Yes, here is the previous context.',
    timestamp: '2026-04-01T10:00:05Z',
    metadata: {},
  },
];

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

function errorResponse(status: number): Response {
  return new Response('restore failed', { status });
}

function stubFetch() {
  const fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

function renderMessageList() {
  const store = createStore(config, en);
  store.restoreMessages('conv-restore', backendMessages);
  store.addMessage({
    id: 'msg-live-customer',
    role: 'customer',
    content: 'This is a live follow-up.',
    timestamp: new Date('2026-04-01T10:05:00Z').getTime(),
  });

  const state = store.getState();
  render(
    <MessageList
      tokens={tokens}
      locale={en}
      messages={state.messages}
      isAgentTyping={false}
      agentName="AI Assistant"
      agentAvatarUrl={null}
      greetingMessage={null}
      restoredMessageCount={state.restoredMessageCount}
    />,
  );
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('SPEC-1868 fetchConversation transport', () => {
  beforeEach(() => {
    configureTransport({
      apiBaseUrl: API_BASE_URL,
      widgetKey: WIDGET_KEY,
    });
  });

  it('requests the conversation endpoint with the configured widget key', async () => {
    const fetchMock = stubFetch();
    fetchMock.mockResolvedValueOnce(jsonResponse({
      conversation_id: 'conv-restore',
      status: 'active',
      messages: backendMessages,
    }));

    const result = await fetchConversation('conv-restore');

    expect(result).toMatchObject({
      ok: true,
      data: {
        conversation_id: 'conv-restore',
        status: 'active',
        messages: backendMessages,
      },
    });
    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/chat/conversations/conv-restore`,
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'X-Widget-Key': WIDGET_KEY,
        }),
      }),
    );
  });

  it.each([
    [403, 'not_found'],
    [404, 'not_found'],
    [500, 'transient'],
  ] as const)('maps HTTP %s restore failures to %s', async (status, reason) => {
    const fetchMock = stubFetch();
    fetchMock.mockResolvedValueOnce(errorResponse(status));

    await expect(fetchConversation('conv-restore')).resolves.toEqual({
      ok: false,
      reason,
    });
  });

  it('maps network failures to transient restore failures', async () => {
    const fetchMock = stubFetch();
    fetchMock.mockRejectedValueOnce(new Error('network unavailable'));

    await expect(fetchConversation('conv-restore')).resolves.toEqual({
      ok: false,
      reason: 'transient',
    });
  });

  it('rejects non-active conversation-state responses', async () => {
    const fetchMock = stubFetch();
    fetchMock.mockResolvedValueOnce(jsonResponse({
      conversation_id: 'conv-restore',
      status: 'ended',
      messages: backendMessages,
    }));

    await expect(fetchConversation('conv-restore')).resolves.toEqual({
      ok: false,
      reason: 'not_active',
    });
  });
});

describe('SPEC-1868 MessageList restore separator', () => {
  it('renders the localized separator between restored and live messages', () => {
    renderMessageList();

    expect(screen.getByText('Yes, here is the previous context.')).toBeTruthy();
    expect(screen.getByText(en.previousConversation)).toBeTruthy();
    expect(screen.getAllByText('This is a live follow-up.').length).toBeGreaterThanOrEqual(1);
  });

  it('does not render a separator when every message was restored', () => {
    const store = createStore(config, en);
    store.restoreMessages('conv-restore', backendMessages);
    const state = store.getState();

    render(
      <MessageList
        tokens={tokens}
        locale={en}
        messages={state.messages}
        isAgentTyping={false}
        agentName="AI Assistant"
        agentAvatarUrl={null}
        greetingMessage={null}
        restoredMessageCount={state.restoredMessageCount}
      />,
    );

    expect(screen.queryByText(en.previousConversation)).toBeNull();
  });

  it('does not render a separator when no messages were restored', () => {
    const store = createStore(config, en);
    store.addMessage({
      id: 'msg-live-customer',
      role: 'customer',
      content: 'A brand new conversation.',
      timestamp: new Date('2026-04-01T10:05:00Z').getTime(),
    });
    const state = store.getState();

    render(
      <MessageList
        tokens={tokens}
        locale={en}
        messages={state.messages}
        isAgentTyping={false}
        agentName="AI Assistant"
        agentAvatarUrl={null}
        greetingMessage={null}
        restoredMessageCount={state.restoredMessageCount}
      />,
    );

    expect(screen.queryByText(en.previousConversation)).toBeNull();
  });
});
