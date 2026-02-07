/**
 * Panel — the main conversation panel rendered inside an iframe.
 *
 * This is the root component inside the iframe. It composes:
 *   - Header (agent info, close button)
 *   - MessageList (scrollable messages, typing indicator)
 *   - InputBar (message input, send, file attach, branding)
 *   - Conditional views: PreChatForm, ChatRating, OfflineForm
 *   - Connection status banner (reconnecting, error)
 *
 * The Panel receives state from the parent frame via the Store singleton.
 * It communicates with the API via HTTP and receives streaming responses
 * via SSE. See transport/http.ts and transport/sse.ts.
 *
 * Architecture (Decision UI-3): iframe for full DOM isolation.
 * Same approach as Zendesk.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState, useEffect, useCallback, useRef } from 'preact/hooks';
import type { DesignTokens, WidgetConfig } from '@/theme/tokens';
import { resolveTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';
import { getStore } from '@/state/store';
import type { WidgetState } from '@/state/store';
import { Header } from './Header';
import { MessageList } from './MessageList';
import { InputBar } from './InputBar';
import { PreChatForm } from './PreChatForm';
import { ChatRating } from './ChatRating';
import { OfflineForm } from './OfflineForm';
import {
  startConversation as apiStartConversation,
  sendMessage as apiSendMessage,
  endConversation as apiEndConversation,
  submitRating as apiSubmitRating,
  getTransportConfig,
} from '@/transport/http';
import { SSEConnection } from '@/transport/sse';

// ---------------------------------------------------------------------------
// Props (passed from the iframe bootstrap)
// ---------------------------------------------------------------------------

interface PanelProps {
  config: WidgetConfig;
  locale: Locale;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// CSS animations injected into the iframe
// ---------------------------------------------------------------------------

const PANEL_STYLES = `
  @keyframes ar-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }
  @keyframes ar-typing-dot {
    0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
    30% { opacity: 1; transform: translateY(-3px); }
  }
  @keyframes ar-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  @keyframes ar-fade-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes ar-slide-up {
    from { opacity: 0; transform: translateY(100%); }
    to { opacity: 1; transform: translateY(0); }
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.15);
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(0,0,0,0.25);
  }
`;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const Panel: FunctionComponent<PanelProps> = ({
  config,
  locale,
  onClose,
}) => {
  const tokens = resolveTokens(config);

  // Subscribe to store for reactive updates
  const [state, setState] = useState<WidgetState>(getStore().getState());
  useEffect(() => {
    return getStore().subscribe(() => {
      setState({ ...getStore().getState() });
    });
  }, []);

  // SSE connection ref (lives for the lifetime of the conversation)
  const sseRef = useRef<SSEConnection | null>(null);

  // Derived state
  const agentName = config.widget_agent_display_name || 'AI Assistant';
  const agentTitle = config.widget_agent_title || '';
  const agentAvatarUrl = config.widget_agent_avatar_url || null;
  const logoUrl = config.widget_logo_url || null;
  const greetingMessage = config.greeting_message || null;
  const showBranding = config.widget_show_branding !== false;
  const fileUploadEnabled = config.widget_file_upload_enabled === true;
  const chatRatingEnabled = config.widget_chat_rating_enabled !== false;

  // ---- Conversation lifecycle ---------------------------------------------

  /** Start a new conversation (optionally with pre-chat data). */
  const beginConversation = useCallback(async (preChatData?: Record<string, string>) => {
    const store = getStore();
    store.setState({ isLoading: true, error: null });

    const conversationId = await apiStartConversation(preChatData);
    if (!conversationId) {
      store.setState({ isLoading: false, error: 'Failed to start conversation' });
      return;
    }

    store.setState({
      conversationId,
      isLoading: false,
      view: 'conversation',
      preChatData: preChatData || null,
    });

    // Connect SSE for streaming
    connectSSE(conversationId);
  }, []);

  const connectSSE = useCallback((conversationId: string) => {
    // Disconnect any existing connection
    if (sseRef.current) {
      sseRef.current.disconnect();
    }

    const store = getStore();
    const transportCfg = getTransportConfig();

    sseRef.current = new SSEConnection({
      apiBaseUrl: transportCfg.apiBaseUrl,
      widgetKey: transportCfg.widgetKey,
      conversationId,
      onConnectionLost: () => store.setState({ isReconnecting: true }),
      onConnectionRestored: () => store.setState({ isReconnecting: false, error: null }),
    });

    sseRef.current.connect();
  }, []);

  /** Send a customer message. */
  const handleSend = useCallback(async (content: string) => {
    const store = getStore();
    const { conversationId } = store.getState();

    // If no conversation yet, start one first
    if (!conversationId) {
      store.setState({ isLoading: true });
      const newId = await apiStartConversation();
      if (!newId) {
        store.setState({ isLoading: false, error: 'Failed to start conversation' });
        return;
      }
      store.setState({ conversationId: newId, isLoading: false });

      // Add the customer message to UI immediately (optimistic)
      store.addMessage({
        id: `msg_${Date.now()}_customer`,
        role: 'customer',
        content,
        timestamp: Date.now(),
      });

      // Send the message BEFORE opening SSE — the SSE stream endpoint
      // checks for the last customer message and returns 400 if none exists.
      // Previously connectSSE() fired first, causing a race condition.
      await apiSendMessage(newId, content);

      // Now connect SSE — the message is guaranteed to exist on the server
      connectSSE(newId);
      return;
    }

    // Add customer message to UI immediately (optimistic)
    store.addMessage({
      id: `msg_${Date.now()}_customer`,
      role: 'customer',
      content,
      timestamp: Date.now(),
    });

    const ok = await apiSendMessage(conversationId, content);
    if (!ok) {
      store.setState({ error: 'Failed to send message' });
      return;
    }

    // Reconnect SSE for this turn — the previous SSE connection closes
    // after the 'done' event to prevent duplicate pipeline runs. Each
    // new message needs a fresh SSE connection to receive the AI response.
    connectSSE(conversationId);
  }, [connectSSE]);

  /** End the current conversation. */
  /** End the current conversation (wired to Header close). */
  const handleEndConversation = useCallback(async () => {
    const store = getStore();
    const { conversationId } = store.getState();
    if (!conversationId) return;

    // Disconnect SSE
    if (sseRef.current) {
      sseRef.current.disconnect();
      sseRef.current = null;
    }

    await apiEndConversation(conversationId);

    if (chatRatingEnabled) {
      store.setState({ view: 'rating' });
    } else {
      store.resetConversation();
      store.setState({ view: 'conversation' });
    }
  }, [chatRatingEnabled]);

  /** Submit a rating for the ended conversation. */
  const handleRatingSubmit = useCallback(async (rating: 'positive' | 'negative', comment?: string) => {
    const store = getStore();
    const { conversationId } = store.getState();
    if (conversationId) {
      await apiSubmitRating(conversationId, rating, comment);
    }
  }, []);

  /** Start a new conversation after rating. */
  const handleNewConversation = useCallback(() => {
    const store = getStore();
    store.resetConversation();

    // If prechat form is configured, show it; otherwise go straight to conversation
    const hasPrechat = config.widget_prechat_form
      && (config.widget_prechat_form as { fields?: unknown[] }).fields?.length;
    store.setState({ view: hasPrechat ? 'prechat' : 'conversation' });
  }, [config.widget_prechat_form]);

  /** Handle pre-chat form submission. */
  const handlePreChatSubmit = useCallback((data: Record<string, string>) => {
    beginConversation(data);
  }, [beginConversation]);

  /** Handle offline form submission. */
  const handleOfflineSubmit = useCallback((_data: { name: string; email: string; message: string }) => {
    // In production this would POST to an offline message endpoint.
    // For now the OfflineForm handles its own success state internally.
  }, []);

  // Cleanup SSE on unmount
  useEffect(() => {
    return () => {
      if (sseRef.current) {
        sseRef.current.disconnect();
        sseRef.current = null;
      }
    };
  }, []);

  // Auto-start conversation if no pre-chat form
  useEffect(() => {
    const currentState = getStore().getState();
    if (currentState.view === 'conversation' && !currentState.conversationId) {
      // Don't auto-start if there's a prechat form configured
      if (!config.widget_prechat_form) {
        // No auto-start needed — user sends first message to begin
      }
    }
  }, [config.widget_prechat_form]);

  // ---- Render -------------------------------------------------------------

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: tokens.colorBackground,
        fontFamily: tokens.fontFamily,
        fontSize: tokens.fontSizeMd,
        color: tokens.colorText,
        overflow: 'hidden',
        borderRadius: tokens.borderRadiusLg,
      }}
    >
      {/* Inject animations */}
      <style>{PANEL_STYLES}</style>

      {/* Header */}
      <Header
        tokens={tokens}
        locale={locale}
        agentName={agentName}
        agentTitle={agentTitle}
        agentAvatarUrl={agentAvatarUrl}
        logoUrl={logoUrl}
        headerText={config.widget_header_text || null}
        onClose={() => { handleEndConversation(); onClose(); }}
      />

      {/* Connection status banner */}
      {state.isReconnecting && (
        <ConnectionBanner tokens={tokens} locale={locale} type="reconnecting" />
      )}
      {state.error && !state.isReconnecting && (
        <ConnectionBanner tokens={tokens} locale={locale} type="error" message={state.error} />
      )}

      {/* Main content area — switches based on view */}
      {state.view === 'conversation' && (
        <>
          <MessageList
            tokens={tokens}
            locale={locale}
            messages={state.messages}
            isAgentTyping={state.isAgentTyping}
            agentName={agentName}
            agentAvatarUrl={agentAvatarUrl}
            greetingMessage={greetingMessage}
          />
          <InputBar
            tokens={tokens}
            locale={locale}
            onSend={handleSend}
            isLoading={state.isLoading}
            disabled={false}
            fileUploadEnabled={fileUploadEnabled}
            showBranding={showBranding}
            inputPlaceholder={config.widget_input_placeholder || null}
          />
        </>
      )}

      {/* Pre-chat form */}
      {state.view === 'prechat' && config.widget_prechat_form && (
        <PreChatForm
          tokens={tokens}
          locale={locale}
          formConfig={config.widget_prechat_form as { fields: { name: string; label: string; type: 'text' | 'email' | 'textarea'; required: boolean; placeholder?: string }[] }}
          onSubmit={handlePreChatSubmit}
          isLoading={state.isLoading}
        />
      )}

      {/* Post-chat rating */}
      {state.view === 'rating' && (
        <ChatRating
          tokens={tokens}
          locale={locale}
          onSubmit={handleRatingSubmit}
          onNewConversation={handleNewConversation}
          isLoading={state.isLoading}
        />
      )}

      {/* Offline form */}
      {state.view === 'offline_form' && (
        <OfflineForm
          tokens={tokens}
          locale={locale}
          offlineMessage={config.widget_offline_message || null}
          onSubmit={handleOfflineSubmit}
          isLoading={state.isLoading}
        />
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Connection status banner
// ---------------------------------------------------------------------------

const ConnectionBanner: FunctionComponent<{
  tokens: DesignTokens;
  locale: Locale;
  type: 'reconnecting' | 'error';
  message?: string;
}> = ({ tokens, locale, type, message }) => {
  const isError = type === 'error';

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: tokens.space2,
        padding: `${tokens.space2} ${tokens.space4}`,
        backgroundColor: isError ? '#6B6B6B' : tokens.colorPrimary,
        color: '#FFFFFF',
        fontSize: tokens.fontSizeXs,
        fontFamily: tokens.fontFamily,
        fontWeight: tokens.fontWeightMedium,
        flexShrink: 0,
        animation: 'ar-fade-in 0.2s ease',
      }}
    >
      {!isError && (
        <svg
          width={12}
          height={12}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          style={{ animation: 'ar-spin 0.8s linear infinite' }}
        >
          <path d="M12 2a10 10 0 0 1 10 10" />
        </svg>
      )}
      {isError ? (message || 'An error occurred') : locale.connectionLost}
    </div>
  );
};
