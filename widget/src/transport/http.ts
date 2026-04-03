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
  /** Optional admin auth token (user API key or session token).
   *  When present, the middleware identifies the caller as a team member,
   *  enabling Co-pilot routing and agent access enforcement. */
  authToken?: string;
  /** Auth type: determines which header carries the auth token.
   *  'api_key' → X-API-Key, 'session_token' → X-Session-Token.
   *  Default: 'api_key' for backward compatibility. */
  authType?: 'api_key' | 'session_token';
  /** Tenant ID for SPEC-1644 partition-scoped auth.
   *  When set, appended as ?tenant= to API calls so the middleware can
   *  scope non-SPA API key lookups to a single Cosmos partition. */
  tenantId?: string;
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

/** Status codes that are transient and worth retrying. */
const RETRYABLE_STATUSES = new Set([429, 502, 503, 504]);

/** Default retry configuration. */
const DEFAULT_MAX_RETRIES = 0;  // No retries by default (opt-in per call)

interface RequestOptions {
  /** Number of retry attempts for transient failures (429/5xx/network).
   *  Default: 0 (no retries). Config fetch uses 3. */
  maxRetries?: number;
  /** Initial delay in ms before the first retry. Doubles each attempt. */
  retryBaseDelayMs?: number;
}

/** Sleep helper for retry backoff. */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: RequestOptions,
): Promise<ApiResponse<T>> {
  const { apiBaseUrl, widgetKey, authToken, authType, tenantId } = getTransportConfig();
  const maxRetries = options?.maxRetries ?? DEFAULT_MAX_RETRIES;
  const retryBaseDelay = options?.retryBaseDelayMs ?? 1000;

  // Build URL with ?tenant= for SPEC-1644 partition-scoped auth
  let url = `${apiBaseUrl}${path}`;
  if (tenantId && !url.includes('tenant=')) {
    url += url.includes('?') ? `&tenant=${tenantId}` : `?tenant=${tenantId}`;
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Widget-Key': widgetKey,
  };

  // When loaded in admin console, include the admin's auth credential
  // using the correct header based on auth type. Middleware checks
  // X-API-Key / X-Session-Token before X-Widget-Key, so the caller is
  // authenticated as a team member with role-based routing.
  if (authToken) {
    if (authType === 'session_token') {
      headers['X-Session-Token'] = authToken;
    } else {
      headers['X-API-Key'] = authToken;
    }
  }

  let lastError: ApiResponse<T> | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    // Exponential backoff: 1s, 2s, 4s (for retries, not the first attempt)
    if (attempt > 0) {
      const delay = retryBaseDelay * Math.pow(2, attempt - 1);
      await sleep(delay);
    }

    try {
      const res = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!res.ok) {
        const errorText = await res.text().catch(() => 'Unknown error');
        lastError = { ok: false, status: res.status, data: null, error: errorText };

        // Retry on transient errors, break on permanent ones (4xx except 429)
        if (RETRYABLE_STATUSES.has(res.status) && attempt < maxRetries) {
          // Respect Retry-After header if present
          const retryAfter = res.headers.get('Retry-After');
          if (retryAfter) {
            const retryMs = parseInt(retryAfter, 10) * 1000;
            if (!isNaN(retryMs) && retryMs > 0 && retryMs <= 30000) {
              await sleep(retryMs);
              // Skip the normal backoff delay on next iteration
              continue;
            }
          }
          continue;
        }

        return lastError;
      }

      const data = await res.json() as T;
      return { ok: true, status: res.status, data, error: null };
    } catch (err) {
      lastError = {
        ok: false,
        status: 0,
        data: null,
        error: err instanceof Error ? err.message : 'Network error',
      };
      // Network errors are retryable (CORS blocked, server unreachable, etc.)
      if (attempt < maxRetries) continue;
    }
  }

  return lastError!;
}

// ---------------------------------------------------------------------------
// API methods
// ---------------------------------------------------------------------------

/**
 * Fetch the widget configuration for this tenant.
 *
 * When `pageType` is provided, the server includes contextual quick action
 * buttons assigned to that page type in the response (WI #227).
 */
export async function fetchWidgetConfig(
  pageType?: string,
  pageHandle?: string,
): Promise<WidgetConfig | null> {
  let path = '/api/config';
  const params: string[] = [];
  if (pageType) params.push(`page_type=${encodeURIComponent(pageType)}`);
  if (pageHandle) params.push(`page_handle=${encodeURIComponent(pageHandle)}`);
  if (params.length > 0) path += `?${params.join('&')}`;

  // Config fetch is critical — retry up to 3 times with exponential backoff.
  // Handles transient 429 (rate limit), 503 (cold start), and network errors
  // (CORS failures, server unreachable). Without config, the widget cannot
  // initialize at all.
  const resp = await request<{
    config: WidgetConfig;
    quick_actions?: Array<{ id: string; label: string; prompt_template: string; icon?: string | null }>;
  }>('GET', path, undefined, { maxRetries: 3, retryBaseDelayMs: 1500 });

  if (!resp.ok || !resp.data) return null;

  // Merge quick_actions from response root into the config object
  const cfg = resp.data.config;
  if (resp.data.quick_actions) {
    cfg.widget_quick_actions = resp.data.quick_actions;
  }
  return cfg;
}

/** Start a new conversation. Returns conversation_id.
 *
 * Builds a ``visitor`` identity object from available customer data:
 *   - Shopify keys (shopify_customer_id, shopify_customer_hmac) → AUTH-4
 *   - Pre-chat email/name → used as customer_id fallback for PCM
 *   - OTP customer token → proves verified identity (AUTH-3/AUTH-5)
 *
 * The backend uses ``visitor`` for _resolve_customer_id() which feeds
 * the Layer 1 PCM profile loading chain. Without visitor, the conversation
 * is anonymous and PCM is unavailable.
 */
export async function startConversation(
  customerData?: Record<string, string>,
  customerToken?: string | null,
): Promise<string | null> {
  const body: Record<string, unknown> = {};

  if (customerData) {
    // Separate Shopify identity keys from regular pre-chat fields
    const visitor: Record<string, string> = {};
    const regular: Record<string, string> = {};

    for (const [key, value] of Object.entries(customerData)) {
      if (key === 'shopify_customer_id') visitor.customer_id = value;
      else if (key === 'shopify_customer_hmac') visitor.hmac = value;
      else regular[key] = value;
    }

    // Populate visitor email/name from regular pre-chat fields
    if (regular.email) visitor.email = regular.email;
    if (regular.name) visitor.name = regular.name;

    if (Object.keys(regular).length > 0) body.customer_data = regular;

    // AUTH-5: Send visitor whenever we have ANY identity signal
    // (customer_id from Shopify OR email from pre-chat/OTP).
    // Previously only sent when customer_id existed — breaking PCM
    // for all non-Shopify customers.
    if (visitor.customer_id || visitor.email) body.visitor = visitor;
  }

  // AUTH-5: Attach OTP customer token for server-side verification
  if (customerToken) {
    body.customer_token = customerToken;
  }

  // Conversation start is critical — retry up to 2 times with backoff.
  // Handles transient 429 (rate limit) and 503 (cold start).
  const resp = await request<{ conversation_id: string }>(
    'POST',
    '/api/chat/conversations',
    body,
    { maxRetries: 2, retryBaseDelayMs: 1000 },
  );
  return resp.ok && resp.data ? resp.data.conversation_id : null;
}

/** Result of sending a customer message. */
export interface SendMessageResult {
  ok: boolean;
  /** HTTP status code — 409 means conversation is no longer active (e.g. escalated). */
  status: number;
  /** Server-assigned message ID (present on success). */
  message_id?: string;
  /** Structured error code from server (e.g. "in_flight_response", "transfer_to_human"). */
  code?: string;
  /** Server-suggested retry delay in milliseconds. */
  retry_after_ms?: number;
}

/**
 * Generate a UUID v4 idempotency key.
 * P1-2: Used by sendMessage to prevent duplicate message creation on retry.
 */
function generateIdempotencyKey(): string {
  // crypto.randomUUID is available in all modern browsers and Web Workers
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older environments
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

/** Send a customer message with idempotency key for retry safety. */
export async function sendMessage(
  conversationId: string,
  content: string,
  idempotencyKey?: string,
): Promise<SendMessageResult> {
  const key = idempotencyKey || generateIdempotencyKey();
  const resp = await request('POST', '/api/chat/message', {
    conversation_id: conversationId,
    content,
    idempotency_key: key,
  });

  // Parse structured error body for 409 responses
  if (!resp.ok && resp.status === 409 && resp.error) {
    try {
      const body = JSON.parse(resp.error);
      return {
        ok: false,
        status: resp.status,
        code: body.code,
        retry_after_ms: body.retry_after_ms,
      };
    } catch {
      // Plain-text 409 (legacy path)
      return { ok: false, status: resp.status };
    }
  }

  if (resp.ok && resp.data) {
    const data = resp.data as Record<string, unknown>;
    return {
      ok: true,
      status: resp.status,
      message_id: data.message_id as string | undefined,
    };
  }

  return { ok: resp.ok, status: resp.status };
}

/** End a conversation. */
export async function endConversation(conversationId: string): Promise<boolean> {
  const resp = await request('POST', `/api/chat/conversations/${conversationId}/end`, {});
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

/** Submit per-message feedback (thumbs up/down) on an AI response (SPEC-1836). */
export async function submitMessageFeedback(
  conversationId: string,
  messageId: string,
  rating: 'positive' | 'negative',
  comment?: string,
): Promise<boolean> {
  const resp = await request(
    'POST',
    `/api/chat/conversations/${conversationId}/messages/${messageId}/feedback`,
    { rating, comment },
  );
  return resp.ok;
}

/** Report an issue with the conversation (C7). */
export async function reportIssue(
  conversationId: string,
  issueType: string,
  details: string,
): Promise<boolean> {
  const resp = await request('POST', `/api/chat/conversations/${conversationId}/issue`, {
    issue_type: issueType,
    details,
  });
  return resp.ok;
}

// ---------------------------------------------------------------------------
// Consent collection (WI #87)
// ---------------------------------------------------------------------------

/** Submit customer consent choice for Persistent Customer Memory. */
export async function submitConsent(
  conversationId: string,
  consentGranted: boolean,
): Promise<boolean> {
  const resp = await request('POST', `/api/chat/conversations/${conversationId}/consent`, {
    consent_status: consentGranted ? 'granted' : 'denied',
  });
  return resp.ok;
}

// ---------------------------------------------------------------------------
// OTP verification (AUTH-3)
// ---------------------------------------------------------------------------

/** Send a 6-digit OTP to the customer's email. */
export async function sendOtp(
  email: string,
  name?: string,
): Promise<boolean> {
  const resp = await request<{ sent: boolean }>('POST', '/api/chat/otp/send', {
    email,
    name: name ?? '',
  });
  return resp.ok;
}

/** Verify a 6-digit OTP code. Returns customer_token on success. */
export async function verifyOtp(
  email: string,
  code: string,
): Promise<{ verified: boolean; customerToken: string | null }> {
  const resp = await request<{ verified: boolean; customer_token: string | null }>(
    'POST', '/api/chat/otp/verify',
    { email, code },
  );
  if (resp.ok && resp.data?.verified) {
    return { verified: true, customerToken: resp.data.customer_token ?? null };
  }
  return { verified: false, customerToken: null };
}

// ---------------------------------------------------------------------------
// Transcript restore (SPEC-1868)
// ---------------------------------------------------------------------------

interface BackendMessage {
  message_id: string;
  role: string;
  content: string;
  timestamp: string; // ISO 8601
  metadata?: Record<string, unknown>;
}

interface ConversationRestoreResponse {
  conversation_id: string;
  status: string;
  messages: BackendMessage[];
}

export type RestoreResult =
  | { ok: true; data: ConversationRestoreResponse }
  | { ok: false; reason: 'not_found' | 'not_active' | 'transient' };

/**
 * Fetch a conversation for transcript restoration.
 *
 * Returns a discriminated result so callers can distinguish
 * permanent failures (clear storage) from transient ones (keep storage).
 */
export async function fetchConversation(
  conversationId: string,
): Promise<RestoreResult> {
  const resp = await request<ConversationRestoreResponse>(
    'GET', `/api/chat/conversations/${conversationId}`,
  );
  if (!resp.ok || !resp.data) {
    // 404/403 = conversation gone, clear storage
    if (resp.status === 404 || resp.status === 403) {
      return { ok: false, reason: 'not_found' };
    }
    // 5xx / network error = transient, keep storage
    return { ok: false, reason: 'transient' };
  }
  // Status policy: restore only active conversations
  if (resp.data.status !== 'active') {
    return { ok: false, reason: 'not_active' };
  }
  return { ok: true, data: resp.data };
}
