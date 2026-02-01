/**
 * HTTP transport — client→server message delivery.
 *
 * All widget HTTP calls go through this module. Handles:
 *   - Widget key authentication (pk_live_... header)
 *   - Config fetching from /api/config
 *   - Conversation lifecycle (start, message, end)
 *   - Pre-chat form submission
 *   - Chat rating submission
 *   - Error handling and retry
 *
 * Architecture (Decision UI-4):
 *   HTTP POST for client→server messages
 *   SSE for server→client AI streaming (see sse.ts)
 *   WebSocket for bidirectional typing/presence (see ws.ts)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { WidgetConfig } from '@/theme/tokens';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

export interface TransportConfig {
  /** Base URL of the Agent Red API (e.g. https://api.agentred.io). */
  apiBaseUrl: string;
  /** Publishable widget key (pk_live_...). */
  widgetKey: string;
}

let _config: TransportConfig | null = null;

export function configureTransport(config: TransportConfig): void {
  _config = config;
}

export function getTransportConfig(): TransportConfig {
  if (!_config) throw new Error('Transport not configured. Call configureTransport() first.');
  return _config;
}

// ---------------------------------------------------------------------------
// HTTP helper
// ---------------------------------------------------------------------------

interface ApiResponse<T> {
  ok: boolean;
  status: number;
  data: T | null;
  error: string | null;
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<ApiResponse<T>> {
  const { apiBaseUrl, widgetKey } = getTransportConfig();
  const url = `${apiBaseUrl}${path}`;

  try {
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Widget-Key': widgetKey,
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!res.ok) {
      const errorText = await res.text().catch(() => 'Unknown error');
      return { ok: false, status: res.status, data: null, error: errorText };
    }

    const data = await res.json() as T;
    return { ok: true, status: res.status, data, error: null };
  } catch (err) {
    return {
      ok: false,
      status: 0,
      data: null,
      error: err instanceof Error ? err.message : 'Network error',
    };
  }
}

// ---------------------------------------------------------------------------
// API methods
// ---------------------------------------------------------------------------

/** Fetch the widget configuration for this tenant. */
export async function fetchWidgetConfig(): Promise<WidgetConfig | null> {
  const resp = await request<{ config: WidgetConfig }>('GET', '/api/config');
  return resp.ok && resp.data ? resp.data.config : null;
}

/** Start a new conversation. Returns conversation_id. */
export async function startConversation(
  customerData?: Record<string, string>,
): Promise<string | null> {
  const resp = await request<{ conversation_id: string }>(
    'POST',
    '/api/chat/conversations',
    customerData ? { customer_data: customerData } : undefined,
  );
  return resp.ok && resp.data ? resp.data.conversation_id : null;
}

/** Send a customer message. */
export async function sendMessage(
  conversationId: string,
  content: string,
): Promise<boolean> {
  const resp = await request('POST', '/api/chat/message', {
    conversation_id: conversationId,
    content,
  });
  return resp.ok;
}

/** End a conversation. */
export async function endConversation(conversationId: string): Promise<boolean> {
  const resp = await request('POST', `/api/chat/conversations/${conversationId}/end`);
  return resp.ok;
}

/** Submit a chat rating. */
export async function submitRating(
  conversationId: string,
  rating: 'positive' | 'negative',
  comment?: string,
): Promise<boolean> {
  const resp = await request('POST', `/api/chat/conversations/${conversationId}/rating`, {
    rating,
    comment,
  });
  return resp.ok;
}
