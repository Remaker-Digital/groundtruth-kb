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
import { OtpVerification } from './OtpVerification';
import { ChatRating } from './ChatRating';
import { OfflineForm } from './OfflineForm';
import { IssueReport } from './IssueReport';
import {
  startConversation as apiStartConversation,
  sendMessage as apiSendMessage,
  submitRating as apiSubmitRating,
  reportIssue as apiReportIssue,
  sendOtp as apiSendOtp,
  verifyOtp as apiVerifyOtp,
  submitConsent as apiSubmitConsent,
  getTransportConfig,
} from '@/transport/http';
import { SSEConnection } from '@/transport/sse';
import { detectPageContext, resolveTemplate } from '@/utils/templateVars';
import { ConsentBanner } from './ConsentBanner';

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
  @keyframes ar-shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
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
  locale: _locale,
  onClose,
}) => {
  // Subscribe to store for reactive updates
  const [state, setState] = useState<WidgetState>(getStore().getState());
  useEffect(() => {
    return getStore().subscribe(() => {
      setState({ ...getStore().getState() });
    });
  }, []);

  // WI-0819: Reactive locale — prefer store value (updated by setLocale SDK method)
  const activeLocale: Locale = state.locale;

  // WI-0934: Use store config (updated by setConfigPartial) for reactive preview.
  // The `config` prop is frozen at iframe creation; `state.config` is updated
  // when the admin UI (or SDK) calls setConfigPartial(). Prefer the store value
  // so that draft-mode changes and post-activation refreshes take effect
  // without requiring a full page reload.
  const activeConfig = state.config || config;

  const baseTokens = resolveTokens(activeConfig);
  const tokens = state.tokenOverrides
    ? { ...baseTokens, ...state.tokenOverrides }
    : baseTokens;

  // SSE connection ref (lives for the lifetime of the conversation)
  const sseRef = useRef<SSEConnection | null>(null);

  // Derived state — use activeConfig for reactive preview
  const agentName = activeConfig.widget_agent_display_name || 'AI Assistant';
  const agentTitle = activeConfig.widget_agent_title || '';
  const agentAvatarUrl = activeConfig.widget_agent_avatar_url || null;
  const logoUrl = activeConfig.widget_logo_url || null;
  const greetingMessage = activeConfig.widget_greeting_message || null;
  const showBranding = activeConfig.widget_show_branding !== false;
  const fileUploadEnabled = activeConfig.widget_file_upload_enabled === true;
  const quickActions = activeConfig.widget_quick_actions || [];

  // ---- Conversation lifecycle ---------------------------------------------

  /** Start a new conversation (optionally with pre-chat data).
   *
   * AUTH-5: Passes the OTP customer token (if available) to the backend
   * for server-side verification. This proves the customer verified
   * their email, giving the conversation full PCM access.
   */
  const beginConversation = useCallback(async (preChatData?: Record<string, string>) => {
    const store = getStore();
    store.setState({ isLoading: true, error: null });

    // AUTH-5: Include customer token for verified identity
    const { customerToken } = store.getState();
    const conversationId = await apiStartConversation(preChatData, customerToken);
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

    // SSE is NOT connected here — the stream endpoint returns 400 when no
    // customer message exists yet. handleSend() connects SSE after the
    // first message is sent (line ~241), which is the correct sequence.
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
      adminApiKey: transportCfg.adminApiKey,
      onConnectionLost: () => store.setState({ isReconnecting: true }),
      onConnectionRestored: () => store.setState({ isReconnecting: false, error: null }),
      // WI-0931: When all reconnect attempts fail, clear the reconnecting
      // banner and show a final error instead of leaving it stuck forever.
      onMaxReconnectsExhausted: () => store.setState({
        isReconnecting: false,
        error: activeLocale.connectionFailed,
      }),
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

    const result = await apiSendMessage(conversationId, content);
    if (!result.ok) {
      if (result.status === 409) {
        // Conversation is no longer active (e.g. escalated to human agent).
        // Show a system message and disable further input.
        store.addMessage({
          id: `msg_${Date.now()}_system`,
          role: 'system',
          content: 'This conversation has been transferred to a human agent. Please wait for a support team member to respond.',
          timestamp: Date.now(),
        });
        store.setState({ error: null });
      } else {
        store.setState({ error: 'Failed to send message' });
      }
      return;
    }

    // Reconnect SSE for this turn — the previous SSE connection closes
    // after the 'done' event to prevent duplicate pipeline runs. Each
    // new message needs a fresh SSE connection to receive the AI response.
    connectSSE(conversationId);
  }, [connectSSE]);

  /** Handle quick action button click — resolve template vars and send (WI #228). */
  const handleQuickAction = useCallback((promptTemplate: string) => {
    const context = detectPageContext();
    const resolvedPrompt = resolveTemplate(promptTemplate, context);
    handleSend(resolvedPrompt);
  }, [handleSend]);

  /** Close the widget without ending the conversation.
   *
   * Disconnects SSE but preserves conversation state so the customer
   * can reopen the widget and resume where they left off.  The
   * conversation is NOT auto-resolved — only explicit "End conversation"
   * or idle-timeout should resolve it.
   */
  const handleCloseWidget = useCallback(() => {
    // Disconnect SSE — it will reconnect on reopen
    if (sseRef.current) {
      sseRef.current.disconnect();
      sseRef.current = null;
    }
    onClose();
  }, [onClose]);

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

    // P0-AUTH-FIX: Always go to conversation view. Identity collection
    // happens in-conversation, not via pre-chat form.
    store.setState({ view: 'conversation' });
  }, []);

  /** Handle pre-chat form submission — route through OTP if verification enabled. */
  const handlePreChatSubmit = useCallback(async (data: Record<string, string>) => {
    const store = getStore();
    const verificationMode = (activeConfig as Record<string, unknown>).customer_email_verification as string ?? 'required';
    const email = data.email || '';

    // If verification is disabled or no email provided, go straight to conversation
    if (verificationMode === 'disabled' || !email) {
      beginConversation(data);
      return;
    }

    // Store pre-chat data and email for OTP flow
    store.setState({
      preChatData: data,
      customerEmail: email,
      isLoading: true,
      otpError: null,
    });

    // Send OTP
    await apiSendOtp(email, data.name || '');

    // Transition to OTP screen
    store.setState({ view: 'otp', isLoading: false });
  }, [beginConversation, activeConfig]);

  /** Skip pre-chat form — continue as anonymous guest. */
  const handlePreChatSkip = useCallback(() => {
    const store = getStore();
    store.setState({ isAnonymous: true });
    beginConversation();
  }, [beginConversation]);

  /** Verify OTP code entered by customer (AUTH-3). */
  const handleOtpVerify = useCallback(async (code: string) => {
    const store = getStore();
    const { customerEmail, preChatData } = store.getState();
    if (!customerEmail) return;

    store.setState({ isLoading: true, otpError: null });

    const result = await apiVerifyOtp(customerEmail, code);

    if (result.verified) {
      store.setState({
        customerToken: result.customerToken,
        isLoading: false,
      });
      // Start conversation with pre-chat data
      beginConversation(preChatData || undefined);
    } else {
      store.setState({
        isLoading: false,
        otpError: activeLocale.otpInvalid,
      });
    }
  }, [beginConversation, activeLocale]);

  /** Resend OTP code (AUTH-3). */
  const handleOtpResend = useCallback(async () => {
    const store = getStore();
    const { customerEmail, preChatData } = store.getState();
    if (!customerEmail) return;

    await apiSendOtp(customerEmail, preChatData?.name || '');
    store.setState({ otpError: null });
  }, []);

  /** Skip OTP verification — continue without verifying (AUTH-3, optional mode only). */
  const handleOtpSkip = useCallback(() => {
    const store = getStore();
    const { preChatData } = store.getState();
    // Customer has email from pre-chat but didn't verify — partial identity
    beginConversation(preChatData || undefined);
  }, [beginConversation]);

  /** Handle offline form submission. */
  const handleOfflineSubmit = useCallback((_data: { name: string; email: string; message: string }) => {
    // In production this would POST to an offline message endpoint.
    // For now the OfflineForm handles its own success state internally.
  }, []);

  /** Open the issue report form (C7). */
  const handleOpenIssueReport = useCallback(() => {
    const store = getStore();
    store.setState({ view: 'issue_report' });
  }, []);

  /** Submit an issue report (C7). */
  const handleIssueSubmit = useCallback(async (issueType: string, details: string) => {
    const store = getStore();
    const { conversationId } = store.getState();
    if (conversationId) {
      await apiReportIssue(conversationId, issueType, details);
    }
  }, []);

  /** Cancel issue report and return to conversation (C7). */
  const handleIssueCancel = useCallback(() => {
    const store = getStore();
    store.setState({ view: 'conversation' });
  }, []);

  /** Handle consent acceptance (WI #87). */
  const handleConsentAccept = useCallback(async () => {
    const store = getStore();
    const { conversationId } = store.getState();
    store.setState({ consentCollected: true });
    if (conversationId) {
      await apiSubmitConsent(conversationId, true);
    }
  }, []);

  /** Handle consent decline (WI #87). */
  const handleConsentDecline = useCallback(async () => {
    const store = getStore();
    const { conversationId } = store.getState();
    store.setState({ consentCollected: true });
    if (conversationId) {
      await apiSubmitConsent(conversationId, false);
    }
  }, []);

  // ---- Drag-to-reposition (WI #253) ----------------------------------------

  /**
   * Initiate drag from the header. Posts the initial screen coordinates to the
   * parent frame, which takes over mousemove/mouseup handling via an overlay.
   * This avoids cross-frame coordinate feedback issues.
   */
  const handleDragStart = useCallback((e: MouseEvent) => {
    e.preventDefault();
    // Use screenX/Y which are consistent across frames
    window.parent.postMessage({
      type: 'ar:drag-start',
      screenX: e.screenX,
      screenY: e.screenY,
    }, '*');
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

  // Auto-start conversation for Shopify customers (AUTH-4).
  // When the widget opens with verified Shopify identity, skip pre-chat
  // and OTP entirely and begin the conversation immediately.
  const shopifyAutoStarted = useRef(false);
  useEffect(() => {
    const currentState = getStore().getState();
    if (
      currentState.shopifyCustomer
      && currentState.view === 'conversation'
      && !currentState.conversationId
      && !shopifyAutoStarted.current
    ) {
      shopifyAutoStarted.current = true;
      const { shopifyCustomer } = currentState;
      beginConversation({
        name: shopifyCustomer.name,
        email: shopifyCustomer.email,
        shopify_customer_id: shopifyCustomer.id,
        shopify_customer_hmac: shopifyCustomer.hmac,
      });
    }
  }, [state.view, beginConversation]);

  // Auto-start conversation if no pre-chat form (non-Shopify path)
  useEffect(() => {
    const currentState = getStore().getState();
    if (currentState.view === 'conversation' && !currentState.conversationId) {
      if (!activeConfig.widget_prechat_form && !currentState.shopifyCustomer) {
        // No auto-start needed — user sends first message to begin
      }
    }
  }, [activeConfig.widget_prechat_form]);

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
        locale={activeLocale}
        agentName={agentName}
        agentTitle={agentTitle}
        agentAvatarUrl={agentAvatarUrl}
        logoUrl={logoUrl}
        headerText={activeConfig.widget_header_text || null}
        headerSubtitle={activeConfig.widget_header_subtitle || null}
        gradientEnd={activeConfig.widget_header_gradient_enabled !== false && activeConfig.widget_header_gradient_end ? activeConfig.widget_header_gradient_end : null}
        onClose={handleCloseWidget}
        onDragStart={handleDragStart}
      />

      {/* Connection status banner */}
      {state.isReconnecting && (
        <ConnectionBanner tokens={tokens} locale={activeLocale} type="reconnecting" />
      )}
      {state.error && !state.isReconnecting && (
        <ConnectionBanner tokens={tokens} locale={activeLocale} type="error" message={state.error} />
      )}

      {/* Consent banner (WI #87) — shown when consent collection is enabled */}
      {state.view === 'conversation'
        && (activeConfig as Record<string, unknown>).consent_collection_enabled === true
        && !state.consentCollected
        && state.conversationId && (
        <ConsentBanner
          tokens={tokens}
          locale={activeLocale}
          onAccept={handleConsentAccept}
          onDecline={handleConsentDecline}
        />
      )}

      {/* Main content area — switches based on view with fade transition */}
      {state.view === 'conversation' && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <MessageList
            tokens={tokens}
            locale={activeLocale}
            messages={state.messages}
            isAgentTyping={state.isAgentTyping}
            agentName={agentName}
            agentAvatarUrl={agentAvatarUrl}
            greetingMessage={greetingMessage}
            quickActions={quickActions}
            onQuickAction={handleQuickAction}
          />

          {/* Report an Issue link (C7) — shown when conversation has messages */}
          {state.messages.length > 0 && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'center',
                padding: `${tokens.space1} ${tokens.space4}`,
                flexShrink: 0,
              }}
            >
              <button
                type="button"
                onClick={handleOpenIssueReport}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: tokens.space1,
                  padding: `${tokens.space1} ${tokens.space2}`,
                  fontSize: tokens.fontSizeXs,
                  fontFamily: tokens.fontFamily,
                  color: tokens.colorTextSecondary,
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  opacity: 0.7,
                }}
              >
                {/* Flag icon */}
                <svg
                  width={12}
                  height={12}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
                  <line x1="4" y1="22" x2="4" y2="15" />
                </svg>
                {activeLocale.reportIssue}
              </button>
            </div>
          )}

          <InputBar
            tokens={tokens}
            locale={activeLocale}
            onSend={handleSend}
            isLoading={state.isLoading}
            disabled={false}
            fileUploadEnabled={fileUploadEnabled}
            showBranding={showBranding}
            inputPlaceholder={activeConfig.widget_input_placeholder || null}
          />
        </div>
      )}

      {/* Pre-chat form */}
      {state.view === 'prechat' && activeConfig.widget_prechat_form && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <PreChatForm
            tokens={tokens}
            locale={activeLocale}
            formConfig={activeConfig.widget_prechat_form as { fields: { name: string; label: string; type: 'text' | 'email' | 'textarea'; required: boolean; placeholder?: string }[] }}
            onSubmit={handlePreChatSubmit}
            onSkip={handlePreChatSkip}
            isLoading={state.isLoading}
          />
        </div>
      )}

      {/* OTP verification (AUTH-3) */}
      {state.view === 'otp' && state.customerEmail && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <OtpVerification
            tokens={tokens}
            locale={activeLocale}
            email={state.customerEmail}
            onVerify={handleOtpVerify}
            onSkip={
              ((activeConfig as Record<string, unknown>).customer_email_verification as string) === 'optional'
                ? handleOtpSkip
                : undefined
            }
            onResend={handleOtpResend}
            isLoading={state.isLoading}
            error={state.otpError ?? undefined}
          />
        </div>
      )}

      {/* Post-chat rating */}
      {state.view === 'rating' && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <ChatRating
            tokens={tokens}
            locale={activeLocale}
            onSubmit={handleRatingSubmit}
            onNewConversation={handleNewConversation}
            isLoading={state.isLoading}
          />
        </div>
      )}

      {/* Issue report form (C7) */}
      {state.view === 'issue_report' && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <IssueReport
            tokens={tokens}
            locale={activeLocale}
            onSubmit={handleIssueSubmit}
            onCancel={handleIssueCancel}
            isLoading={state.isLoading}
          />
        </div>
      )}

      {/* Offline form */}
      {state.view === 'offline_form' && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <OfflineForm
            tokens={tokens}
            locale={activeLocale}
            offlineMessage={activeConfig.widget_offline_message || null}
            onSubmit={handleOfflineSubmit}
            isLoading={state.isLoading}
          />
        </div>
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
