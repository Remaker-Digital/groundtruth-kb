/**
 * SSE transport — server→client AI response streaming.
 *
 * Connects to GET /api/chat/stream/{conversation_id} and receives
 * Server-Sent Events as the AI generates tokens. Events:
 *
 *   stage           — Pipeline stage progress (started/completed with latency)
 *   token           — Individual token chunk (append to current message)
 *   validated       — Critic approved the response (finalize message)
 *   done            — Stream complete for this turn
 *   retracted       — Critic rejected the response (replace with fallback)
 *   error           — Pipeline error (with code, recoverable flag)
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
  /** Admin API key for Co-pilot mode (SPEC-1562). */
  adminApiKey?: string;
  onConnectionLost?: () => void;
  onConnectionRestored?: () => void;
  /** Called when all reconnect attempts are exhausted (WI-0931). */
  onMaxReconnectsExhausted?: () => void;
}

type StreamEventType =
  | 'stage'
  | 'token'
  | 'validated'
  | 'done'
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
  private streamComplete = false; // Set true after 'done' — prevents reconnect
  private currentStreamContent = '';
  private tabId: string;

  constructor(private options: SSEOptions) {
    this.tabId = getTabId();
  }

  connect(): void {
    if (this.closed) return;

    // Reset stream-complete flag for new turn
    this.streamComplete = false;

    const url = new URL(
      `${this.options.apiBaseUrl}/api/chat/stream/${this.options.conversationId}`,
    );

    // EventSource doesn't support custom headers, so we pass authentication
    // as a query parameter. The backend accepts both header and query param.
    // SPEC-1562: When adminApiKey is set, use it for Co-pilot mode auth.
    if (this.options.adminApiKey) {
      url.searchParams.set('api_key', this.options.adminApiKey);
    } else {
      url.searchParams.set('widget_key', this.options.widgetKey);
    }

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

      // If the stream completed normally ('done' received), don't reconnect.
      // EventSource fires onerror when the server closes the connection,
      // which happens after the 'done' event. Reconnecting would re-run
      // the pipeline and create duplicate/retracted messages.
      if (this.streamComplete) return;

      if (this.options.onConnectionLost) {
        this.options.onConnectionLost();
      }

      this.scheduleReconnect();
    };

    // Listen for each event type (matching server StreamEventType enum)
    this.eventSource.addEventListener('stage', (e: MessageEvent) => {
      this.handleEvent({ type: 'stage', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('token', (e: MessageEvent) => {
      this.handleEvent({ type: 'token', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('validated', (e: MessageEvent) => {
      this.handleEvent({ type: 'validated', data: e.data, id: e.lastEventId });
    });

    this.eventSource.addEventListener('done', (e: MessageEvent) => {
      this.handleEvent({ type: 'done', data: e.data, id: e.lastEventId });
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
      case 'stage': {
        // Pipeline stage progress — when response-generator starts,
        // create the empty agent message bubble for token streaming.
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.stage === 'response-generator' && parsed.status === 'started') {
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
          }
        } catch { /* ignore malformed stage events */ }
        break;
      }

      case 'token': {
        // Append token to the current streaming message
        try {
          const parsed = JSON.parse(event.data);
          this.currentStreamContent += parsed.text || '';
        } catch {
          // Fallback: treat raw data as text
          this.currentStreamContent += event.data;
        }
        store.updateLastAgentMessage(this.currentStreamContent, true);
        break;
      }

      case 'validated': {
        // Critic approved — mark the streaming message as complete
        store.updateLastAgentMessage(this.currentStreamContent, false);
        this.currentStreamContent = '';
        break;
      }

      case 'done': {
        // Stream complete for this turn — ensure message is finalized
        if (this.currentStreamContent) {
          store.updateLastAgentMessage(this.currentStreamContent, false);
          this.currentStreamContent = '';
        }
        // Mark stream as complete and close the EventSource to prevent
        // auto-reconnect. The server runs the pipeline on every SSE
        // connection, so reconnecting after 'done' would trigger a
        // duplicate pipeline run, creating ghost messages and retractions.
        this.streamComplete = true;
        if (this.eventSource) {
          this.eventSource.close();
          this.eventSource = null;
        }
        break;
      }

      case 'retracted': {
        // Critic rejected — replace with safe fallback (Decision UI-5)
        let fallback = 'I apologize, but I need to rephrase my response. How else can I help you?';
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.fallback_text) fallback = parsed.fallback_text;
          else if (parsed.fallback) fallback = parsed.fallback;
        } catch { /* use default */ }
        store.retractLastAgentMessage(fallback);
        this.currentStreamContent = '';
        break;
      }

      case 'error': {
        let errorMsg = 'An error occurred';
        try {
          const parsed = JSON.parse(event.data);
          errorMsg = parsed.message || errorMsg;
        } catch {
          errorMsg = event.data || errorMsg;
        }
        store.setState({ error: errorMsg });
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
    if (this.closed) return;

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      // WI-0931: Max attempts exhausted — stop reconnecting and notify.
      // Without this, isReconnecting stays true forever (stuck banner).
      if (this.options.onMaxReconnectsExhausted) {
        this.options.onMaxReconnectsExhausted();
      }
      return;
    }

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
