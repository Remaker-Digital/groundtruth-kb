// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * WebSocket transport — bidirectional channel for typing and presence.
 *
 * Used for:
 *   - Customer typing indicator (client → server)
 *   - Human agent typing indicator (server → client, post-escalation)
 *   - Presence detection (online/offline status)
 *   - Human agent chat messages (post-escalation, bidirectional)
 *
 * Architecture (Decision UI-4):
 *   HTTP POST for client→server messages (see http.ts)
 *   SSE for server→client AI streaming (see sse.ts)
 *   WebSocket for bidirectional typing/presence (this file)
 *
 * The WebSocket connects to /api/chat/ws/{conversation_id} and
 * authenticates via the widget key query parameter. Messages are
 * JSON-encoded with a `type` field.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { getStore } from '@/state/store';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface WSOptions {
  apiBaseUrl: string;
  widgetKey: string;
  conversationId: string;
  onConnectionLost?: () => void;
  onConnectionRestored?: () => void;
  /** Called when all reconnect attempts are exhausted (WI-0931). */
  onMaxReconnectsExhausted?: () => void;
}

interface WSMessage {
  type: string;
  data?: unknown;
}

// ---------------------------------------------------------------------------
// WebSocket connection
// ---------------------------------------------------------------------------

export class WSConnection {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectBaseDelay = 2000; // 2s, exponential backoff
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private closed = false;
  private pingTimer: ReturnType<typeof setInterval> | null = null;

  // Typing indicator debounce
  private typingTimer: ReturnType<typeof setTimeout> | null = null;
  private isTyping = false;

  constructor(private options: WSOptions) {}

  connect(): void {
    if (this.closed) return;

    // Convert http(s) URL to ws(s)
    const wsBase = this.options.apiBaseUrl
      .replace(/^https:/, 'wss:')
      .replace(/^http:/, 'ws:');

    const url = new URL(
      `${wsBase}/api/chat/ws/${this.options.conversationId}`,
    );
    url.searchParams.set('widget_key', this.options.widgetKey);

    this.ws = new WebSocket(url.toString());

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      if (this.options.onConnectionRestored) {
        this.options.onConnectionRestored();
      }
      // Start ping keepalive (30s interval)
      this.startPing();
    };

    this.ws.onclose = () => {
      this.stopPing();
      if (this.closed) return;

      if (this.options.onConnectionLost) {
        this.options.onConnectionLost();
      }
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      // onerror always followed by onclose — no action needed here
    };

    this.ws.onmessage = (event: MessageEvent) => {
      this.handleMessage(event.data as string);
    };
  }

  disconnect(): void {
    this.closed = true;
    this.stopPing();

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.typingTimer) {
      clearTimeout(this.typingTimer);
      this.typingTimer = null;
    }
    if (this.ws) {
      this.ws.close(1000, 'Widget closed');
      this.ws = null;
    }
  }

  // ---- Outbound messages --------------------------------------------------

  /** Notify the server that the customer is typing. Debounced: sends at
   *  most once every 3 seconds and auto-stops after 5 seconds of silence. */
  sendTyping(): void {
    if (!this.isTyping) {
      this.isTyping = true;
      this.send({ type: 'customer_typing', data: { typing: true } });
    }

    // Reset the stop-typing timer
    if (this.typingTimer) clearTimeout(this.typingTimer);
    this.typingTimer = setTimeout(() => {
      this.isTyping = false;
      this.send({ type: 'customer_typing', data: { typing: false } });
    }, 5000);
  }

  /** Send a customer stopped typing event (e.g., on message send). */
  sendStoppedTyping(): void {
    if (this.typingTimer) {
      clearTimeout(this.typingTimer);
      this.typingTimer = null;
    }
    if (this.isTyping) {
      this.isTyping = false;
      this.send({ type: 'customer_typing', data: { typing: false } });
    }
  }

  // ---- Inbound messages ---------------------------------------------------

  private handleMessage(raw: string): void {
    let msg: WSMessage;
    try {
      msg = JSON.parse(raw) as WSMessage;
    } catch {
      return; // ignore malformed messages
    }

    const store = getStore();

    switch (msg.type) {
      case 'agent_typing': {
        // Human agent is typing (post-escalation)
        store.setState({ isAgentTyping: true });
        break;
      }

      case 'agent_stopped_typing': {
        store.setState({ isAgentTyping: false });
        break;
      }

      case 'agent_message': {
        // Human agent message (post-escalation)
        const data = msg.data as { content?: string; agent_name?: string } | undefined;
        if (data?.content) {
          store.addMessage({
            id: `msg_${Date.now()}_agent`,
            role: 'agent',
            content: data.content,
            timestamp: Date.now(),
          });
          store.setState({ isAgentTyping: false });
        }
        break;
      }

      case 'conversation_ended': {
        // Server-initiated conversation end (e.g., agent closed the chat)
        store.setState({ view: 'rating' });
        break;
      }

      case 'pong': {
        // Response to our ping — connection is alive
        break;
      }

      default:
        break;
    }
  }

  // ---- Internal -----------------------------------------------------------

  private send(msg: WSMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg));
    }
  }

  private startPing(): void {
    this.stopPing();
    this.pingTimer = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000);
  }

  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.closed) return;

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      // WI-0931: Max attempts exhausted — stop reconnecting and notify.
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
