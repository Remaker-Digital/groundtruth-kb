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
import { PhoneOtpVerification } from './PhoneOtpVerification';
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
  sendPhoneOtp as apiSendPhoneOtp,
  verifyPhoneOtp as apiVerifyPhoneOtp,
  submitConsent as apiSubmitConsent,
  fetchConversation,
  getTransportConfig,
} from '@/transport/http';
import { SSEConnection } from '@/transport/sse';
import { detectPageContext, resolveTemplate } from '@/utils/templateVars';
import { ConsentBanner } from './ConsentBanner';
import { loadTranscript, saveTranscript, clearTranscript } from '@/persistence/transcript';

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
  @keyframes ar-stream-progress {
    0% { transform: translateX(-100%); }
    50% { transform: translateX(150%); }
    100% { transform: translateX(350%); }
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
  const agentName = activeConfig.widget_agent_display_name || _locale.defaultAgentName;
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
      store.setState({ isLoading: false, error: _locale.errorStartConversation });
      return;
    }

    store.setState({
      conversationId,
      isLoading: false,
      view: 'conversation',
      preChatData: preChatData || null,
    });

    // SPEC-1868: Persist conversation_id for transcript continuity
    const continuity = activeConfig.widget_transcript_continuity || 'none';
    if (continuity !== 'none') {
      const { widgetKey } = getTransportConfig();
      saveTranscript(widgetKey, conversationId, continuity);
    }

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
      authToken: transportCfg.authToken,
      authType: transportCfg.authType,
      tenantId: transportCfg.tenantId,
      conversationId,
      onConnectionLost: () => store.setState({
        isReconnecting: true,
        connectionError: 'transient',
      }),
      onConnectionRestored: () => store.setState({
        isReconnecting: false,
        reconnectAttempt: 0,
        connectionError: null,
        error: null,
      }),
      onReconnectAttempt: (attempt: number) => store.setState({
        reconnectAttempt: attempt,
      }),
      // WI-0931: When all reconnect attempts fail, clear the reconnecting
      // banner and show a final error instead of leaving it stuck forever.
      onMaxReconnectsExhausted: () => store.setState({
        isReconnecting: false,
        reconnectAttempt: 0,
        connectionError: 'permanent',
        error: activeLocale.connectionFailedPermanent,
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
        store.setState({ isLoading: false, error: _locale.errorStartConversation });
        return;
      }
      store.setState({ conversationId: newId, isLoading: false });

      // SPEC-1868: Persist conversation_id for transcript continuity
      const continuityMode = activeConfig.widget_transcript_continuity || 'none';
      if (continuityMode !== 'none') {
        const { widgetKey } = getTransportConfig();
        saveTranscript(widgetKey, newId, continuityMode);
      }

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

    // P1-2: Generate stable idempotency key for retry safety
    const idempotencyKey = crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
    let result = await apiSendMessage(conversationId, content, idempotencyKey);

    // P1-2: Handle retryable 409 (in-flight response) with backoff
    if (!result.ok && result.status === 409 && result.code === 'in_flight_response') {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        const delay = result.retry_after_ms ?? 2000;
        await new Promise(resolve => setTimeout(resolve, delay));
        result = await apiSendMessage(conversationId, content, idempotencyKey);
        if (result.ok || result.code !== 'in_flight_response') break;
      }
    }

    if (!result.ok) {
      if (result.status === 409 && result.code !== 'in_flight_response') {
        // Terminal 409: conversation transferred to human agent
        store.addMessage({
          id: `msg_${Date.now()}_system`,
          role: 'system',
          content: _locale.escalationNotice,
          timestamp: Date.now(),
        });
        store.setState({ error: null });
      } else if (result.status === 409 && result.code === 'in_flight_response') {
        // Retries exhausted — response still in flight
        store.setState({ error: _locale.waitForResponse });
      } else {
        store.setState({ error: _locale.errorSendMessage });
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
    if (store.getState().isLoading) return; // Double-submit guard (all paths)
    const verificationMode = (activeConfig as Record<string, unknown>).customer_email_verification as string ?? 'required';
    const email = data.email || '';
    const phone = data.phone || '';

    // If verification is disabled, go straight to conversation
    if (verificationMode === 'disabled') {
      beginConversation(data);
      return;
    }

    // Email OTP path (takes precedence over phone when both present)
    if (email) {
      store.setState({
        preChatData: data,
        customerEmail: email,
        isLoading: true,
        otpError: null,
      });
      await apiSendOtp(email, data.name || '');
      store.setState({ view: 'otp', isLoading: false });
      return;
    }

    // Phone SMS OTP path (SPEC-1879 Phase 3)
    // Backend SmsSendResponse always returns sent=true (anti-enumeration).
    // Uses structured `reason` field for programmatic branching.
    if (phone) {
      store.setState({
        preChatData: data,
        customerPhone: phone,
        isLoading: true,
        phoneOtpError: null,
      });
      const sendResult = await apiSendPhoneOtp(phone, data.name || '');
      const isTierBlocked = sendResult.reason === 'tier_blocked'
        || (sendResult.sent && sendResult.message?.toLowerCase().includes('not available'));

      if (sendResult.sent && !isTierBlocked) {
        // SMS actually sent — transition to OTP entry screen
        store.setState({ view: 'phone_otp', isLoading: false });
      } else if (isTierBlocked) {
        // Tier-gated — business decision: proceed without verification
        store.setState({ isLoading: false, phoneOtpError: null });
        beginConversation(data);
      } else {
        // Transport/network failure — do NOT bypass verification.
        // Show error and stay on pre-chat form so customer can retry.
        store.setState({
          isLoading: false,
          phoneOtpError: activeLocale.phoneSendFailed ?? 'Unable to send verification code. Please try again.',
        });
      }
      return;
    }

    // No email or phone — go straight to conversation
    beginConversation(data);
  }, [beginConversation, activeConfig, activeLocale]);

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

  /** Verify phone SMS OTP code (SPEC-1879 Phase 3). */
  const handlePhoneOtpVerify = useCallback(async (code: string) => {
    const store = getStore();
    const { customerPhone, preChatData, isLoading } = store.getState();
    if (!customerPhone || isLoading) return; // Double-submit guard

    store.setState({ isLoading: true, phoneOtpError: null });

    const result = await apiVerifyPhoneOtp(customerPhone, code);

    if (result.verified) {
      store.setState({ isLoading: false });
      // Phone verified — start conversation (no customer_token for phone in Phase 2A)
      beginConversation(preChatData || undefined);
    } else {
      store.setState({
        isLoading: false,
        phoneOtpError: activeLocale.phoneOtpInvalid,
      });
    }
  }, [beginConversation, activeLocale]);

  /** Resend phone SMS OTP code (SPEC-1879 Phase 3).
   * Returns true if cooldown should start (success or intentional tier-gate),
   * false if a transport error occurred (error is surfaced; cooldown suppressed). */
  const handlePhoneOtpResend = useCallback(async (): Promise<boolean> => {
    const store = getStore();
    const { customerPhone, preChatData, isLoading } = store.getState();
    if (!customerPhone || isLoading) return false;

    store.setState({ isLoading: true, phoneOtpError: null });

    const result = await apiSendPhoneOtp(customerPhone, preChatData?.name || '');
    // Tier-gate: prefer structured reason field, fall back to message string
    const isBlocked = result.reason === 'tier_blocked'
      || (result.message && result.message.toLowerCase().includes('not available'));
    if (isBlocked) {
      store.setState({ isLoading: false, phoneOtpError: result.message });
      return true; // intentional outcome — start cooldown to prevent hammering
    }
    if (!result.sent) {
      // Transport/network failure — surface error, do not start cooldown
      store.setState({
        isLoading: false,
        phoneOtpError: activeLocale.phoneSendFailed ?? 'Unable to send verification code. Please try again.',
      });
      return false;
    }
    store.setState({ isLoading: false, phoneOtpError: null });
    return true;
  }, [activeLocale]);

  /** Skip phone OTP verification (SPEC-1879, optional mode only). */
  const handlePhoneOtpSkip = useCallback(() => {
    const store = getStore();
    const { preChatData } = store.getState();
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

  // SPEC-1868: Transcript continuity — restore previous conversation on mount.
  // P3-3: Extracted into a callable function so the retry button can re-trigger.
  const restoreTranscript = useCallback(() => {
    const continuity = activeConfig.widget_transcript_continuity || 'none';
    if (continuity === 'none') return;

    const { widgetKey } = getTransportConfig();
    const ttl = activeConfig.widget_transcript_ttl_hours ?? 24;
    const storedId = loadTranscript(widgetKey, continuity, ttl);
    if (!storedId) return;

    const store = getStore();
    store.setState({ isRestoring: true, restoreError: null });

    fetchConversation(storedId).then((result) => {
      if (!result.ok) {
        if (result.reason === 'transient') {
          // Transient — keep storage, show retry UI
          store.setState({ isRestoring: false, restoreError: 'transient' });
        } else {
          // Permanent (not_found, not_active) — clear storage
          clearTranscript(widgetKey, continuity);
          store.setState({ isRestoring: false, restoreError: null });
        }
        return;
      }
      if (!result.data.messages || result.data.messages.length === 0) {
        clearTranscript(widgetKey, continuity);
        store.setState({ isRestoring: false, restoreError: null });
        return;
      }
      store.restoreMessages(result.data.conversation_id, result.data.messages);
      store.setState({ view: 'conversation', isRestoring: false, restoreError: null });
    }).catch(() => {
      // Network-level errors are transient — keep storage, show retry
      store.setState({ isRestoring: false, restoreError: 'transient' });
    });
  }, [activeConfig.widget_transcript_continuity, activeConfig.widget_transcript_ttl_hours]);

  // Run restore once on mount
  const transcriptRestored = useRef(false);
  useEffect(() => {
    if (transcriptRestored.current) return;
    transcriptRestored.current = true;
    restoreTranscript();
  }, [restoreTranscript]);

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

  // ---- Keyboard handlers (WCAG 2.1 — dialog dismissal + focus trap) -------
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape closes the dialog
      if (e.key === 'Escape') {
        handleCloseWidget();
        return;
      }
      // Tab/Shift+Tab containment — wrap focus within the dialog.
      // The iframe boundary already constrains Tab in most browsers, but
      // this explicit trap ensures WCAG 2.4.3 compliance universally.
      if (e.key === 'Tab') {
        const focusable = document.querySelectorAll<HTMLElement>(
          'button:not([disabled]), textarea:not([disabled]), input:not([disabled]), ' +
          'a[href], [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleCloseWidget]);

  // ---- Render -------------------------------------------------------------

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="ar-panel-heading"
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

      {/* Connection status banner (P3-4: enhanced with attempt counter + retry/dismiss) */}
      {state.isReconnecting && (
        <ConnectionBanner
          tokens={tokens}
          locale={activeLocale}
          type="reconnecting"
          reconnectAttempt={state.reconnectAttempt}
        />
      )}
      {state.error && !state.isReconnecting && (
        <ConnectionBanner
          tokens={tokens}
          locale={activeLocale}
          type="error"
          message={state.error}
          connectionError={state.connectionError}
          onRetry={() => {
            getStore().setState({ error: null, connectionError: null, isReconnecting: true });
            if (sseRef.current) {
              // Reuse existing instance to preserve lastEventId + partial content
              sseRef.current.retry();
            }
          }}
          onDismiss={() => getStore().setState({ error: null, connectionError: null })}
        />
      )}

      {/* Skeleton loader for conversation restore (P3-3) */}
      {state.isRestoring && (
        <RestoreSkeleton tokens={tokens} locale={activeLocale} />
      )}
      {state.restoreError === 'transient' && !state.isRestoring && (
        <div
          role="alert"
          style={{
            padding: `${tokens.space3} ${tokens.space4}`,
            textAlign: 'center',
            color: tokens.colorTextMuted,
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
          }}
        >
          <span>{activeLocale.errorGeneric}</span>
          {' '}
          <button
            type="button"
            onClick={() => { transcriptRestored.current = false; restoreTranscript(); }}
            style={{
              background: 'none',
              border: 'none',
              color: tokens.colorPrimary,
              cursor: 'pointer',
              fontFamily: tokens.fontFamily,
              fontSize: tokens.fontSizeXs,
              textDecoration: 'underline',
              padding: 0,
            }}
          >
            {activeLocale.retryConnection}
          </button>
        </div>
      )}

      {/* Stream progress indicator (P3-5) */}
      {state.isStreaming && (
        <StreamProgress tokens={tokens} />
      )}

      {/* Consent banner (WI #87) — shown when consent collection is enabled.
          S259 D14: Admin users have implicit consent — banner suppressed. */}
      {state.view === 'conversation'
        && (activeConfig as Record<string, unknown>).consent_collection_enabled === true
        && !state.consentCollected
        && !state.isAdminContext
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
            restoredMessageCount={state.restoredMessageCount}
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
            phoneError={state.phoneOtpError ?? undefined}
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

      {/* Phone SMS OTP verification (SPEC-1879 Phase 3) */}
      {state.view === 'phone_otp' && state.customerPhone && (
        <div style={{ display: 'contents', animation: 'ar-fade-in 0.2s ease-out' }}>
          <PhoneOtpVerification
            tokens={tokens}
            locale={activeLocale}
            phone={state.customerPhone}
            onVerify={handlePhoneOtpVerify}
            onSkip={
              ((activeConfig as Record<string, unknown>).customer_email_verification as string) === 'optional'
                ? handlePhoneOtpSkip
                : undefined
            }
            onResend={handlePhoneOtpResend}
            isLoading={state.isLoading}
            error={state.phoneOtpError ?? undefined}
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
  reconnectAttempt?: number;
  connectionError?: 'transient' | 'permanent' | null;
  onRetry?: () => void;
  onDismiss?: () => void;
}> = ({ tokens, locale, type, message, reconnectAttempt, connectionError, onRetry, onDismiss }) => {
  const isError = type === 'error';
  const isPermanent = connectionError === 'permanent';

  // P3-4: Interpolate attempt number into locale string
  const bannerText = !isError && reconnectAttempt
    ? locale.reconnectingAttempt.replace('{n}', String(reconnectAttempt))
    : isError
      ? (isPermanent ? locale.connectionFailedPermanent : (message || locale.errorGeneric))
      : locale.connectionLost;

  return (
    <div
      role="alert"
      aria-live="assertive"
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
      <span>{bannerText}</span>
      {isPermanent && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          style={{
            background: 'rgba(255,255,255,0.2)',
            border: '1px solid rgba(255,255,255,0.4)',
            borderRadius: '4px',
            color: '#FFFFFF',
            cursor: 'pointer',
            fontSize: tokens.fontSizeXs,
            fontFamily: tokens.fontFamily,
            padding: `2px ${tokens.space2}`,
            marginLeft: tokens.space2,
          }}
        >
          {locale.retryConnection}
        </button>
      )}
      {isError && onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label={locale.dismissError}
          style={{
            background: 'none',
            border: 'none',
            color: 'rgba(255,255,255,0.7)',
            cursor: 'pointer',
            fontSize: '14px',
            lineHeight: 1,
            padding: '2px',
            marginLeft: tokens.space2,
          }}
        >
          ×
        </button>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Restore skeleton loader (P3-3)
// ---------------------------------------------------------------------------

const RestoreSkeleton: FunctionComponent<{
  tokens: DesignTokens;
  locale: Locale;
}> = ({ tokens, locale }) => {
  const bubbleStyle = (isAgent: boolean, width: string) => ({
    width,
    height: '40px',
    borderRadius: tokens.borderRadius,
    background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
    backgroundSize: '200% 100%',
    animation: 'ar-shimmer 1.5s infinite',
    alignSelf: isAgent ? 'flex-start' : 'flex-end',
  });

  return (
    <div
      role="status"
      aria-label={locale.restoringConversation}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: tokens.space3,
        padding: `${tokens.space4} ${tokens.space4}`,
      }}
    >
      <div style={bubbleStyle(true, '70%')} />
      <div style={bubbleStyle(false, '50%')} />
      <div style={bubbleStyle(true, '60%')} />
      <div style={bubbleStyle(true, '45%')} />
      <div style={{ textAlign: 'center', color: tokens.colorTextMuted, fontSize: tokens.fontSizeXs, fontFamily: tokens.fontFamily }}>
        {locale.restoringConversation}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Stream progress indicator (P3-5)
// ---------------------------------------------------------------------------

const StreamProgress: FunctionComponent<{
  tokens: DesignTokens;
}> = ({ tokens }) => (
  <div
    style={{
      height: '2px',
      width: '100%',
      overflow: 'hidden',
      flexShrink: 0,
    }}
  >
    <div
      style={{
        height: '100%',
        width: '40%',
        backgroundColor: tokens.colorPrimary,
        animation: 'ar-stream-progress 1.2s ease-in-out infinite',
      }}
    />
  </div>
);
