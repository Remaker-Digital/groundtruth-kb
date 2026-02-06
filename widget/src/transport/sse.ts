/**
 * SSE transport — server→client AI response streaming.
 *
 * Connects to GET /api/chat/stream/{conversation_id} and receives
 * Server-Sent Events as the AI generates tokens. Events:
 *
 *   stream_start    — AI response generation begins
 *   token           — Individual token (append to current message)
 *   stream_end      — AI response complete
 *   retracted       — Critic rejected the response (replace with fallback)
 *   error           — Pipeline error
 *   agent_typing    — Human agent is typing (post-escalation)
 *
 * Supports Last-Event-ID for reconnection (SSEConnectionManager on backend
 * buffers events per conversation with monotonic sequence IDs).
 *
 * Architecture (Decision UI-4, UI-5):
 *   Stream-then-validate: tokens stream in real-time, Critic validates
 *   post-stream. Rejection triggers 'retracted' event replacing displayed
 *   text with safe fallback. ~800ms exposure window at P50.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { getStore } from '@/state/store';
import type { Message } from '@/state/store';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SSEOptions {
  apiBaseUrl: string;
  widgetKey: string;
  conversationId: string;
  onConnectionLost?: () => void;
  onConnectionRestored?: () => void;
}

type StreamEventType =
  | 'stream_start'
  | 'token'
  | 'stream_end'
  | 'retracted'
  | 'error'
  | 'agent_typing';

interface StreamEvent {
  type: StreamEventType;
  data: string;
  id?: string;
}

// ---------------------------------------------------------------------------
// SSE connection
// ---------------------------------------------------------------------------

/**
 * Generate a unique tab identifier for multi-tab coordination (WI #133).
 * Persisted in sessionStorage so reconnections from the same tab reuse
 * the same ID. Different tabs get different IDs.
 */
function getTabId(): string {
  const KEY = '__agentred_tab_id';
  let id = sessionStorage.getItem(KEY);
  if (!id) {
    id = `tab_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    sessionStorage.setItem(KEY, id);
  }
  return id;
}

export class SSEConnection {
  private eventSource: EventSource | null = null;
  private lastEventId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectBaseDelay = 1000; // 1s, exponential backoff
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private closed = false;
  private currentStreamContent = '';
  private tabId: string;

  constructor(private options: SSEOptions) {
    this.tabId = getTabId();
  }

  connect(): void {
    if (this.closed) return;

    const url = new URL(
      `${this.options.apiBaseUrl}/api/chat/stream/${this.options.conversationId}`,
    );

    // EventSource doesn't support custom headers, so we pass the widget key
    // as a query parameter. The backend accepts both header and query param.
    url.searchParams.set('widget_key', this.options.widgetKey);

    // WI #133: Pass tab_id for multi-tab coordination. The backend tracks
    // which tabs are streaming the same conversation and shares connection
    // slots so multiple tabs don't exhaust per-tenant concurrency limits.
    url.searchParams.set('tab_id', this.tabId);

    if (this.lastEventId) {
      url.searchParams.set('last_event_id', this.lastEventId);
    }

    this.eventSource = new EventSource(url.toString());

    this.eventSource.onopen = () => {
      this.reconnectAttempts = 0;
      if (this.options.onConnectionRestored) {
        this.options.onConnectionRestored();
      }
    };

    this.eventSource.onerror = () => {
      this.eventSource?.close();
      this.eventSource = null;

      if (this.closed) return;

      if (this.options.onConnectionLost) {
        this.options.onConnectionLost();
      }

      this.scheduleReconnect();
    };

    // Listen for each event type
    this.eventSource.addEventListener('stream_start', (e: MessageEvent) => {
      this.handleEvent({ type: 'stream_start', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('token', (e: MessageEvent) => {
      this.handleEvent({ type: 'token', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('stream_end', (e: MessageEvent) => {
      this.handleEvent({ type: 'stream_end', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('retracted', (e: MessageEvent) => {
      this.handleEvent({ type: 'retracted', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('error', (e: MessageEvent) => {
      this.handleEvent({ type: 'error', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('agent_typing', (e: MessageEvent) => {
      this.handleEvent({ type: 'agent_typing', data: e.data, id: e.lastEventId });
    });
  }

  disconnect(): void {
    this.closed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  // ---- Event handling ------------------------------------------------------

  private handleEvent(event: StreamEvent): void {
    if (event.id) {
      this.lastEventId = event.id;
    }

    const store = getStore();

    switch (event.type) {
      case 'stream_start': {
        // Add a new empty agent message in streaming state
        this.currentStreamContent = '';
        const msg: Message = {
          id: `msg_${Date.now()}_agent`,
          role: 'agent',
          content: '',
          timestamp: Date.now(),
          streaming: true,
        };
        store.addMessage(msg);
        store.setState({ isAgentTyping: false });
        break;
      }

      case 'token': {
        // Append token to the current streaming message
        this.currentStreamContent += event.data;
        store.updateLastAgentMessage(this.currentStreamContent, true);
        break;
      }

      case 'stream_end': {
        // Mark the streaming message as complete
        store.updateLastAgentMessage(this.currentStreamContent, false);
        this.currentStreamContent = '';
        break;
      }

      case 'retracted': {
        // Critic rejected — replace with safe fallback (Decision UI-5)
        let fallback = 'I apologize, but I need to rephrase my response. How else can I help you?';
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.fallback) fallback = parsed.fallback;
        } catch { /* use default */ }
        store.retractLastAgentMessage(fallback);
        this.currentStreamContent = '';
        break;
      }

      case 'error': {
        store.setState({ error: event.data || 'An error occurred' });
        break;
      }

      case 'agent_typing': {
        store.setState({ isAgentTyping: true });
        break;
      }
    }
  }

  // ---- Reconnection --------------------------------------------------------

  private scheduleReconnect(): void {
    if (this.closed || this.reconnectAttempts >= this.maxReconnectAttempts) return;

    const delay = Math.min(
      this.reconnectBaseDelay * Math.pow(2, this.reconnectAttempts),
      30000, // max 30s
    );
    this.reconnectAttempts++;

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }
}
