/**
 * Widget state management.
 *
 * Minimal reactive store using Preact signals. Components subscribe to
 * individual signals and re-render only when their dependencies change.
 *
 * State shape:
 *   - config: merchant widget configuration (from /api/config)
 *   - conversation: current conversation state (messages, status)
 *   - ui: presentation state (open/closed, view, loading indicators)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { WidgetConfig, DesignTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';

// ---------------------------------------------------------------------------
// Message types
// ---------------------------------------------------------------------------

export interface Message {
  id: string;
  role: 'customer' | 'agent' | 'system';
  content: string;
  timestamp: number;
  /** True while streaming (agent messages arrive token-by-token). */
  streaming?: boolean;
  /** Set if the Critic retracted this message post-stream. */
  retracted?: boolean;
  /** Per-message feedback rating: 'positive' or 'negative' (SPEC-1836). */
  feedbackRating?: 'positive' | 'negative' | null;
  /** Structured source attribution from validated event (B1). */
  sources?: Array<{ title: string; url?: string }>;
}

export interface PreChatData {
  [fieldName: string]: string;
}

/** Shopify customer identity data injected from Liquid template (AUTH-4). */
export interface ShopifyCustomer {
  /** Shopify customer ID (e.g. "7654321012345"). */
  id: string;
  /** Customer email from Shopify account. */
  email: string;
  /** Customer display name. */
  name: string;
  /** HMAC-SHA256(customer_id, identity_secret) for server verification. */
  hmac: string;
}

// ---------------------------------------------------------------------------
// Widget view states
// ---------------------------------------------------------------------------

export type WidgetView =
  | 'closed'           // Launcher button only
  | 'prechat'          // Pre-chat form (if configured)
  | 'otp'              // OTP email verification (AUTH-3)
  | 'conversation'     // Active chat
  | 'rating'           // Post-chat rating prompt
  | 'offline_form'     // Leave-a-message form
  | 'issue_report';    // Report an issue form (C7)

// ---------------------------------------------------------------------------
// Store state
// ---------------------------------------------------------------------------

export interface WidgetState {
  // Config (loaded once from /api/config via widget key)
  config: WidgetConfig;
  locale: Locale;

  // Conversation
  conversationId: string | null;
  messages: Message[];
  isAgentTyping: boolean;

  // UI
  view: WidgetView;
  isLoading: boolean;
  isReconnecting: boolean;
  error: string | null;
  unreadCount: number;

  // Pre-chat
  preChatData: PreChatData | null;

  // Identity (AUTH-1, AUTH-3, AUTH-4)
  isAnonymous: boolean;
  customerEmail: string | null;
  customerToken: string | null;
  otpError: string | null;

  // Shopify customer passthrough (AUTH-4)
  shopifyCustomer: ShopifyCustomer | null;

  // Consent (WI #87)
  consentCollected: boolean;

  // Runtime overrides (WI-0819)
  tokenOverrides: Partial<DesignTokens> | null;
}

// ---------------------------------------------------------------------------
// Simple reactive store
// ---------------------------------------------------------------------------

type Listener = () => void;

class Store {
  private state: WidgetState;
  private listeners: Set<Listener> = new Set();

  constructor(initialState: WidgetState) {
    this.state = initialState;
  }

  getState(): Readonly<WidgetState> {
    return this.state;
  }

  setState(partial: Partial<WidgetState>): void {
    this.state = { ...this.state, ...partial };
    this.notify();
  }

  /** Append a message to the conversation. */
  addMessage(msg: Message): void {
    const isOpen = this.state.view === 'conversation';
    this.state = {
      ...this.state,
      messages: [...this.state.messages, msg],
      unreadCount: isOpen ? 0 : this.state.unreadCount + (msg.role === 'agent' ? 1 : 0),
    };
    this.notify();
  }

  /** Update the last agent message (for streaming token append). */
  updateLastAgentMessage(
    content: string,
    streaming: boolean,
    sources?: Array<{ title: string; url?: string }>,
  ): void {
    const messages = [...this.state.messages];
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'agent' && messages[i].streaming) {
        messages[i] = {
          ...messages[i],
          content,
          streaming,
          ...(sources ? { sources } : {}),
        };
        break;
      }
    }
    this.state = { ...this.state, messages };
    this.notify();
  }

  /** Mark the last agent message as retracted (Critic rejection). */
  retractLastAgentMessage(fallbackContent: string): void {
    const messages = [...this.state.messages];
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'agent') {
        messages[i] = {
          ...messages[i],
          content: fallbackContent,
          retracted: true,
          streaming: false,
        };
        break;
      }
    }
    this.state = { ...this.state, messages };
    this.notify();
  }

  /** Reset conversation state for a new conversation. */
  resetConversation(): void {
    this.state = {
      ...this.state,
      conversationId: null,
      messages: [],
      isAgentTyping: false,
      error: null,
      unreadCount: 0,
      preChatData: null,
      isAnonymous: false,
      customerEmail: null,
      customerToken: null,
      otpError: null,
      // NOTE: shopifyCustomer is NOT reset — it persists for the browser session
    };
    this.notify();
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener();
    }
  }
}

// ---------------------------------------------------------------------------
// Store factory (called once during widget init)
// ---------------------------------------------------------------------------

let _store: Store | null = null;

export function createStore(config: WidgetConfig, locale: Locale): Store {
  _store = new Store({
    config,
    locale,
    conversationId: null,
    messages: [],
    isAgentTyping: false,
    view: 'closed',
    isLoading: false,
    isReconnecting: false,
    error: null,
    unreadCount: 0,
    preChatData: null,
    isAnonymous: false,
    customerEmail: null,
    customerToken: null,
    otpError: null,
    shopifyCustomer: null,
    consentCollected: false,
    tokenOverrides: null,
  });
  return _store;
}

export function getStore(): Store {
  if (!_store) throw new Error('Widget store not initialized. Call createStore() first.');
  return _store;
}
