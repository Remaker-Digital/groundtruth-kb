/**
 * Agent Red Widget — entry point.
 *
 * This is the single entry point that merchants include via a <script> tag.
 * On load it:
 *   1. Reads the data attributes from the script tag (widget key, API URL)
 *   2. Fetches the widget configuration from the API
 *   3. Creates the store, configures transport
 *   4. Mounts the Launcher in a Shadow DOM (closed) in the merchant's page
 *   5. Prepares the conversation Panel iframe (created on first open)
 *   6. Exposes the AgentRed SDK on window.AgentRed for programmatic control
 *
 * Architecture (Decision UI-3):
 *   Shadow DOM (closed) for launcher — prevents merchant CSS leakage
 *   iframe for panel — full DOM isolation (same as Zendesk)
 *
 * Merchant embed code:
 *   <script src="https://cdn.agentred.io/widget.js"
 *     data-widget-key="pk_live_abc123"
 *     data-api-url="https://api.agentred.io"
 *   ></script>
 *
 * Or via Shopify Theme App Extension (app embed block):
 *   Liquid template injects the same script with tenant-specific attributes.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { h, render } from 'preact';
import type { WidgetConfig, DesignTokens } from '@/theme/tokens';
import { resolveTokens } from '@/theme/tokens';
import type { Locale } from '@/locale/en';
import type { LocaleCode } from '@/locale';
import { resolveLocaleCode, getLocalePack } from '@/locale';
import { createStore } from '@/state/store';
import { configureTransport, fetchWidgetConfig } from '@/transport/http';
import { detectPageContext } from '@/utils/templateVars';
import { Launcher } from '@/components/Launcher';
import { Panel } from '@/components/Panel';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AgentRedSDK {
  /** Open the widget panel. */
  open(): void;
  /** Close the widget panel. */
  close(): void;
  /** Toggle widget open/closed. */
  toggle(): void;
  /** Check if the widget is currently open. */
  isOpen(): boolean;
  /** Set the unread count badge. */
  setUnreadCount(count: number): void;
  /** Hide the widget entirely. */
  hide(): void;
  /** Show the widget (after hiding). */
  show(): void;
  /** Destroy the widget and clean up. */
  destroy(): void;
  /** Switch widget UI language at runtime (WI-0819). */
  setLocale(code: LocaleCode): void;
  /** Override design tokens at runtime (WI-0819). */
  setTheme(overrides: Partial<DesignTokens>): void;
  /** Merge partial config overrides at runtime (WI-0820). */
  setConfigPartial(overrides: Partial<WidgetConfig>): void;
  /** Update page targeting rules at runtime (WI-0820). */
  setTargetingRules(rules: string[]): void;
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

(function boot() {
  // Find our script tag to read data attributes
  const scriptTag = document.currentScript as HTMLScriptElement | null
    || document.querySelector('script[data-widget-key]') as HTMLScriptElement | null;

  if (!scriptTag) {
    console.warn('[AgentRed] Widget script tag not found. Missing data-widget-key attribute.');
    return;
  }

  const widgetKey = scriptTag.getAttribute('data-widget-key');
  const apiBaseUrl = scriptTag.getAttribute('data-api-url');

  if (!widgetKey) {
    console.warn('[AgentRed] data-widget-key attribute is required.');
    return;
  }

  if (!apiBaseUrl) {
    console.error('[AgentRed] data-api-url attribute is required. The widget install snippet must include data-api-url.');
    return;
  }

  // Read inline overrides from data attributes (set by Shopify Liquid template).
  // Only non-empty attributes are included — the Liquid template omits attributes
  // that match platform defaults, so API-fetched config is the source of truth
  // and data attributes only override when the merchant explicitly changed a value
  // in the Shopify theme editor.
  const dataOverrides: Record<string, string | boolean> = {};
  const attrMap: Record<string, string> = {
    'data-color': 'widget_primary_color',
    'data-position': 'widget_position',
    'data-auto-open': 'widget_auto_open',
    'data-auto-open-delay': 'widget_auto_open_delay',
    'data-mobile-enabled': 'widget_mobile_enabled',
    'data-mobile-fullscreen': 'widget_mobile_fullscreen',
    'data-sound-enabled': 'widget_sound_enabled',
    'data-greeting': 'widget_greeting_message',
    'data-header-text': 'widget_header_text',
    'data-agent-name': 'widget_agent_display_name',
    'data-context': 'widget_context',
    'data-customer-name': 'widget_customer_name',
  };
  for (const [attr, configKey] of Object.entries(attrMap)) {
    const val = scriptTag.getAttribute(attr);
    if (val !== null && val !== '') {
      // Convert boolean-like strings
      if (val === 'true') dataOverrides[configKey] = true;
      else if (val === 'false') dataOverrides[configKey] = false;
      else dataOverrides[configKey] = val;
    }
  }

  // Read Shopify customer identity passthrough data attributes (AUTH-4).
  // When a Shopify customer is logged in and the merchant has configured an
  // identity secret, the Liquid template injects HMAC-signed customer data.
  const shopifyCustomerId = scriptTag.getAttribute('data-shopify-customer-id');
  const shopifyCustomerHmac = scriptTag.getAttribute('data-shopify-customer-hmac');
  const shopifyCustomer = shopifyCustomerId && shopifyCustomerHmac
    ? {
        id: shopifyCustomerId,
        email: scriptTag.getAttribute('data-shopify-customer-email') || '',
        name: scriptTag.getAttribute('data-shopify-customer-name') || '',
        hmac: shopifyCustomerHmac,
      }
    : null;

  // SPEC-1562: Read admin API key for Co-pilot mode.
  // When the widget is embedded in the admin panel, the admin's per-user
  // API key is passed so chat messages authenticate as a team member.
  const adminApiKey = scriptTag.getAttribute('data-admin-key') || undefined;

  // Configure transport
  configureTransport({ apiBaseUrl, widgetKey, adminApiKey });

  // Fetch config and initialize
  init(widgetKey, apiBaseUrl, dataOverrides, shopifyCustomer).catch((err) => {
    console.error('[AgentRed] Widget initialization failed:', err);
  });
})();

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

async function init(
  _widgetKey: string,
  _apiBaseUrl: string,
  dataOverrides?: Record<string, string | boolean>,
  shopifyCustomer?: { id: string; email: string; name: string; hmac: string } | null,
): Promise<void> {
  // Detect page context for quick action filtering (WI #227)
  const pageCtx = detectPageContext();

  // Fetch widget configuration from the API (with page context for quick actions)
  const fetchedConfig = await fetchWidgetConfig(pageCtx.page_type, pageCtx.page_handle);
  if (!fetchedConfig) {
    console.warn('[AgentRed] Failed to fetch widget configuration. Widget will not load.');
    return;
  }
  // Merge data-attribute overrides from the script tag (Shopify Liquid template).
  // These take precedence over API-fetched config only when the merchant has
  // explicitly changed a setting in the Shopify theme editor. The Liquid template
  // omits attributes that match platform defaults, so this merge only applies
  // merchant-intentional overrides.
  const hasOverrides = dataOverrides && Object.keys(dataOverrides).length > 0;
  const config: WidgetConfig = hasOverrides
    ? { ...fetchedConfig, ...dataOverrides } as WidgetConfig
    : fetchedConfig;

  // Check page rules — should this page show the widget?
  if (!shouldShowOnPage(config)) return;

  // Check mobile — should the widget show on mobile?
  if (config.widget_mobile_enabled === false && isMobile()) return;

  // Merge locale overrides from config
  const locale = buildLocale(config);

  // Create the reactive store
  const store = createStore(config, locale);

  // Inject Shopify customer data into the store (AUTH-4).
  // When present, this signals the Panel to auto-start the conversation
  // with verified Shopify identity — skipping pre-chat form and OTP.
  if (shopifyCustomer) {
    store.setState({ shopifyCustomer });
  }

  // P0-AUTH-FIX: Always start in conversation view. Identity collection
  // happens in-conversation via the identity preprocessor, not via a
  // blocking pre-chat form. Shopify HMAC customers get auto-verified;
  // all others see the AI greeting + Quick Actions immediately.
  const initialView = 'conversation';

  // Mount launcher in Shadow DOM
  const { shadowHost, shadowRoot } = mountLauncherHost();

  // State for tracking panel iframe
  let panelIframe: HTMLIFrameElement | null = null;

  // Resolve tokens for launcher
  const tokens = resolveTokens(config);

  // ---- Drag-to-reposition state (WI #253) ----------------------------------

  const DRAG_STORAGE_KEY = 'ar_panel_position';

  /** Load persisted panel position from sessionStorage. */
  function loadDragPosition(): { left: number; top: number } | null {
    try {
      const raw = sessionStorage.getItem(DRAG_STORAGE_KEY);
      if (!raw) return null;
      const pos = JSON.parse(raw);
      if (typeof pos.left === 'number' && typeof pos.top === 'number') return pos;
    } catch { /* ignore */ }
    return null;
  }

  /** Save panel position to sessionStorage. */
  function saveDragPosition(left: number, top: number): void {
    try {
      sessionStorage.setItem(DRAG_STORAGE_KEY, JSON.stringify({ left, top }));
    } catch { /* ignore */ }
  }

  /** Clamp a position within the viewport. */
  function clampToViewport(left: number, top: number, w: number, _h: number): { left: number; top: number } {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const minVisible = 60; // at least 60px of the panel must remain visible
    return {
      left: Math.max(-w + minVisible, Math.min(vw - minVisible, left)),
      top: Math.max(0, Math.min(vh - minVisible, top)),
    };
  }

  /** Apply a left/top position to the panel iframe, clearing bottom/right anchoring. */
  function applyDragPosition(iframe: HTMLIFrameElement, left: number, top: number): void {
    iframe.style.left = `${left}px`;
    iframe.style.top = `${top}px`;
    iframe.style.right = 'auto';
    iframe.style.bottom = 'auto';
  }

  // ---- Launcher rendering -------------------------------------------------

  // Mobile detection for launcher positioning (SPEC-1510)
  const isMobileDevice = isMobile();

  function renderLauncher() {
    const state = store.getState();
    // Re-resolve tokens from current store config on each render so that
    // setConfigPartial() changes (e.g. launcher color) are reflected in
    // real-time without requiring widget re-initialization.
    const currentConfig = state.config;
    const liveTokens = resolveTokens(currentConfig);
    render(
      h(Launcher, {
        tokens: liveTokens,
        position: (isMobileDevice && currentConfig.widget_mobile_position) || currentConfig.widget_position || 'bottom-right',
        offsetX: isMobileDevice
          ? (currentConfig.widget_mobile_offset_x ?? currentConfig.widget_position_offset_x ?? currentConfig.widget_offset_x ?? 20)
          : (currentConfig.widget_position_offset_x ?? currentConfig.widget_offset_x ?? 20),
        offsetY: isMobileDevice
          ? (currentConfig.widget_mobile_offset_y ?? currentConfig.widget_position_offset_y ?? currentConfig.widget_offset_y ?? 20)
          : (currentConfig.widget_position_offset_y ?? currentConfig.widget_offset_y ?? 20),
        isOpen: state.view !== 'closed',
        unreadCount: state.unreadCount,
        launcherIcon: (currentConfig.widget_launcher_icon as 'chat' | 'headset' | 'help') || 'chat',
        onClick: toggleWidget,
      }),
      shadowRoot,
    );
  }

  // Re-render launcher when store changes
  store.subscribe(renderLauncher);
  renderLauncher();

  // ---- Panel (iframe) management ------------------------------------------

  function createPanelIframe(): HTMLIFrameElement {
    const iframe = document.createElement('iframe');
    const mobile = isMobile();
    // Mobile position/offset overrides (SPEC-1510) — fall back to desktop values
    const position = (mobile && config.widget_mobile_position) || config.widget_position || 'bottom-right';
    const offsetX = mobile
      ? (config.widget_mobile_offset_x ?? config.widget_position_offset_x ?? config.widget_offset_x ?? 20)
      : (config.widget_position_offset_x ?? config.widget_offset_x ?? 20);
    const offsetY = mobile
      ? (config.widget_mobile_offset_y ?? config.widget_position_offset_y ?? config.widget_offset_y ?? 20)
      : (config.widget_position_offset_y ?? config.widget_offset_y ?? 20);
    const launcherSize = 60;
    const gap = 12;

    // Mobile fullscreen: panel fills entire viewport (SPEC-1509)
    const mobileFullscreen = mobile && config.widget_mobile_fullscreen === true;

    iframe.style.cssText = mobileFullscreen
      ? [
          'position: fixed',
          'top: 0',
          'left: 0',
          'width: 100vw',
          'height: 100vh',
          'border: none',
          'border-radius: 0',
          'box-shadow: none',
          `z-index: ${tokens.zIndexPanel}`,
          'opacity: 0',
          'transform: translateY(12px)',
          `transition: opacity ${tokens.transitionNormal}, transform ${tokens.transitionNormal}`,
          'pointer-events: none',
          'overflow: hidden',
        ].join('; ')
      : [
          'position: fixed',
          `bottom: ${offsetY + launcherSize + gap}px`,
          position === 'bottom-right' ? `right: ${offsetX}px` : `left: ${offsetX}px`,
          `width: ${tokens.panelWidth}`,
          `height: ${tokens.panelHeight}`,
          'border: none',
          `border-radius: ${tokens.borderRadiusLg}`,
          `box-shadow: ${tokens.shadowLg}`,
          `z-index: ${tokens.zIndexPanel}`,
          'opacity: 0',
          'transform: translateY(12px) scale(0.95)',
          `transition: opacity ${tokens.transitionNormal}, transform ${tokens.transitionNormal}`,
          'pointer-events: none',
          'overflow: hidden',
        ].join('; ');

    iframe.setAttribute('title', 'Agent Red Chat');
    iframe.setAttribute('allow', 'microphone; camera');

    document.body.appendChild(iframe);

    // Write the panel into the iframe
    const iframeDoc = iframe.contentDocument;
    if (iframeDoc) {
      iframeDoc.open();
      iframeDoc.write('<!DOCTYPE html><html style="height:100%;margin:0"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="height:100%;margin:0;padding:0;overflow:hidden"><div id="ar-panel-root" style="height:100%"></div></body></html>');
      iframeDoc.close();

      // Render Panel component into iframe
      const root = iframeDoc.getElementById('ar-panel-root');
      if (root) {
        render(
          h(Panel, {
            config,
            locale,
            onClose: closeWidget,
          }),
          root,
        );
      }
    }

    return iframe;
  }

  // ---- Drag message handler (WI #253) -------------------------------------

  let dragOverlay: HTMLDivElement | null = null;
  let dragStartLeft = 0;
  let dragStartTop = 0;
  let dragStartScreenX = 0;
  let dragStartScreenY = 0;

  function onDragMove(ev: MouseEvent) {
    if (!panelIframe) return;
    const dx = ev.screenX - dragStartScreenX;
    const dy = ev.screenY - dragStartScreenY;
    const w = panelIframe.offsetWidth;
    const h = panelIframe.offsetHeight;
    const { left, top } = clampToViewport(dragStartLeft + dx, dragStartTop + dy, w, h);
    applyDragPosition(panelIframe, left, top);
  }

  function onDragEnd() {
    document.removeEventListener('mousemove', onDragMove);
    document.removeEventListener('mouseup', onDragEnd);

    // Remove the transparent overlay
    if (dragOverlay) {
      dragOverlay.remove();
      dragOverlay = null;
    }

    // Re-enable transition after drag
    if (panelIframe) {
      panelIframe.style.transition = `opacity ${tokens.transitionNormal}, transform ${tokens.transitionNormal}`;
      // Save position
      const left = parseInt(panelIframe.style.left, 10);
      const top = parseInt(panelIframe.style.top, 10);
      if (!isNaN(left) && !isNaN(top)) {
        saveDragPosition(left, top);
      }
    }
  }

  window.addEventListener('message', (ev) => {
    if (!ev.data || typeof ev.data.type !== 'string') return;

    if (ev.data.type === 'ar:drag-start' && panelIframe) {
      // Record the iframe's current position in viewport pixels
      const rect = panelIframe.getBoundingClientRect();
      dragStartLeft = rect.left;
      dragStartTop = rect.top;
      dragStartScreenX = ev.data.screenX;
      dragStartScreenY = ev.data.screenY;

      // Disable CSS transition during drag for instant feedback
      panelIframe.style.transition = 'none';

      // Switch from bottom/right anchoring to left/top so deltas work correctly
      applyDragPosition(panelIframe, rect.left, rect.top);

      // Create a transparent overlay covering the whole viewport.
      // This captures mousemove/mouseup events that would otherwise be
      // swallowed by the iframe (the mouse moves over the iframe during drag).
      dragOverlay = document.createElement('div');
      dragOverlay.style.cssText = [
        'position: fixed',
        'inset: 0',
        `z-index: ${tokens.zIndexPanel + 1}`,
        'cursor: grabbing',
        'user-select: none',
      ].join('; ');
      document.body.appendChild(dragOverlay);

      document.addEventListener('mousemove', onDragMove);
      document.addEventListener('mouseup', onDragEnd);
    }

    // WI-0868: Live config preview from admin WidgetConfigurator
    if (ev.data.type === 'ar:config-preview' && ev.data.payload) {
      store.setState({ config: { ...store.getState().config, ...ev.data.payload } });
    }
  });

  // Mobile fullscreen flag — computed once for panel lifecycle (SPEC-1509)
  const mobileFullscreen = isMobile() && config.widget_mobile_fullscreen === true;

  function showPanel() {
    if (!panelIframe) {
      panelIframe = createPanelIframe();

      // Restore persisted drag position from sessionStorage (WI #253)
      // Skip in mobile fullscreen — panel is fixed at 0,0
      if (!mobileFullscreen) {
        const saved = loadDragPosition();
        if (saved) {
          const w = panelIframe.offsetWidth || parseInt(tokens.panelWidth, 10);
          const h = panelIframe.offsetHeight || parseInt(tokens.panelHeight, 10);
          const { left, top } = clampToViewport(saved.left, saved.top, w, h);
          applyDragPosition(panelIframe, left, top);
        }
      }
    }

    // Double-rAF ensures the browser has painted the initial opacity:0 state
    // before we transition to opacity:1. A single rAF often fires in the same
    // paint frame as the DOM insertion, causing the transition to be skipped.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (panelIframe) {
          panelIframe.style.opacity = '1';
          panelIframe.style.transform = mobileFullscreen ? 'translateY(0)' : 'translateY(0) scale(1)';
          panelIframe.style.pointerEvents = 'auto';
        }
      });
    });
  }

  function hidePanel() {
    if (panelIframe) {
      panelIframe.style.opacity = '0';
      panelIframe.style.transform = mobileFullscreen ? 'translateY(12px)' : 'translateY(12px) scale(0.95)';
      panelIframe.style.pointerEvents = 'none';
    }
  }

  // ---- Widget control functions -------------------------------------------

  function openWidget() {
    store.setState({ view: initialView, unreadCount: 0 });
    showPanel();
  }

  // userManuallyClosedWidget — tracks whether the visitor has opened then closed
  // the widget during this page session, used by exit-intent and scroll-depth
  // triggers to avoid re-opening after the visitor dismissed the widget.
  let userManuallyClosedWidget = false;

  function closeWidget() {
    if (store.getState().view !== 'closed') {
      userManuallyClosedWidget = true;
    }
    store.setState({ view: 'closed' });
    hidePanel();
  }

  function toggleWidget() {
    if (store.getState().view === 'closed') {
      openWidget();
    } else {
      closeWidget();
    }
  }

  // ---- Auto-open logic ----------------------------------------------------

  if (config.widget_auto_open) {
    const delay = (config.widget_auto_open_delay ?? 3) * 1000;
    setTimeout(() => {
      if (store.getState().view === 'closed') {
        openWidget();
      }
    }, delay);
  }

  // ---- Exit-intent trigger (SPEC-1507) ------------------------------------
  // Desktop only — auto-open when mouse leaves viewport. Fires at most once.
  // Must NOT fire if widget was manually opened and closed.

  if (config.widget_exit_intent_enabled && !isMobile()) {
    const exitIntentHandler = () => {
      if (store.getState().view === 'closed' && !userManuallyClosedWidget) {
        openWidget();
      }
      document.documentElement.removeEventListener('mouseleave', exitIntentHandler);
    };
    document.documentElement.addEventListener('mouseleave', exitIntentHandler);
  }

  // ---- Scroll-depth trigger (SPEC-1508) ----------------------------------
  // Auto-open when visitor scrolls past configured % of document height.
  // Fires at most once. Must NOT fire if widget was manually opened and closed.

  const scrollThreshold = config.widget_scroll_depth_trigger;
  if (typeof scrollThreshold === 'number' && scrollThreshold >= 1 && scrollThreshold <= 100) {
    const scrollHandler = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight <= 0) return; // Not scrollable
      const scrollPercent = (scrollTop / docHeight) * 100;
      if (scrollPercent >= scrollThreshold) {
        if (store.getState().view === 'closed' && !userManuallyClosedWidget) {
          openWidget();
        }
        window.removeEventListener('scroll', scrollHandler);
      }
    };
    window.addEventListener('scroll', scrollHandler, { passive: true });
  }

  // ---- Sound notification -------------------------------------------------

  let notificationSound: HTMLAudioElement | null = null;
  if (config.widget_sound_enabled !== false) {
    // We'll create the audio element lazily on first use to comply with
    // browser autoplay policies (requires user interaction first).
    store.subscribe(() => {
      const state = store.getState();
      if (state.unreadCount > 0 && state.view === 'closed') {
        playNotification();
      }
    });
  }

  function playNotification() {
    try {
      if (!notificationSound) {
        // Simple notification beep using AudioContext
        const ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
        const oscillator = ctx.createOscillator();
        const gain = ctx.createGain();
        oscillator.connect(gain);
        gain.connect(ctx.destination);
        oscillator.frequency.value = 800;
        gain.gain.value = 0.1;
        oscillator.start();
        oscillator.stop(ctx.currentTime + 0.15);
      }
    } catch {
      // Audio not available — silently ignore
    }
  }

  // ---- Expose SDK on window -----------------------------------------------

  const sdk: AgentRedSDK = {
    open: openWidget,
    close: closeWidget,
    toggle: toggleWidget,
    isOpen: () => store.getState().view !== 'closed',
    setUnreadCount: (count: number) => store.setState({ unreadCount: Math.max(0, count) }),
    hide: () => {
      shadowHost.style.display = 'none';
      if (panelIframe) panelIframe.style.display = 'none';
    },
    show: () => {
      shadowHost.style.display = '';
      if (panelIframe) panelIframe.style.display = '';
    },
    destroy: () => {
      store.resetConversation();
      if (panelIframe) {
        panelIframe.remove();
        panelIframe = null;
      }
      shadowHost.remove();
      try { sessionStorage.removeItem(DRAG_STORAGE_KEY); } catch { /* ignore */ }
      delete (window as unknown as Record<string, unknown>).AgentRed;
    },
    setLocale: (code: LocaleCode) => {
      const pack = getLocalePack(code);
      const cfg = store.getState().config;
      // Merchant overrides always take precedence over locale pack
      store.setState({
        locale: {
          ...pack,
          ...(cfg.widget_header_text ? { headerTitle: cfg.widget_header_text } : {}),
          ...(cfg.widget_input_placeholder ? { inputPlaceholder: cfg.widget_input_placeholder } : {}),
          ...(cfg.widget_offline_message ? { offlineMessage: cfg.widget_offline_message } : {}),
        },
      });
    },
    setTheme: (overrides: Partial<DesignTokens>) => {
      store.setState({ tokenOverrides: overrides });
    },
    setConfigPartial: (overrides: Partial<WidgetConfig>) => {
      const current = store.getState().config;
      store.setState({ config: { ...current, ...overrides } });
    },
    setTargetingRules: (rules: string[]) => {
      const current = store.getState().config;
      const updated = { ...current, widget_page_rules: rules };
      store.setState({ config: updated });
      // Re-evaluate visibility with new rules
      if (!shouldShowOnPage(updated)) {
        shadowHost.style.display = 'none';
        if (panelIframe) panelIframe.style.display = 'none';
      } else {
        shadowHost.style.display = '';
        if (panelIframe) panelIframe.style.display = '';
      }
    },
  };

  (window as unknown as Record<string, unknown>).AgentRed = sdk;

  // Fire ready event
  window.dispatchEvent(new CustomEvent('agentred:ready', { detail: { sdk } }));
}

// ---------------------------------------------------------------------------
// Shadow DOM launcher host
// ---------------------------------------------------------------------------

function mountLauncherHost(): { shadowHost: HTMLElement; shadowRoot: ShadowRoot } {
  const host = document.createElement('div');
  host.id = 'agent-red-widget';
  host.setAttribute('aria-hidden', 'false');
  // Shopify Dawn (and many themes) hide empty divs via `div:empty { display: none }`.
  // A closed Shadow DOM has no light-DOM children, so the host matches `:empty`.
  // Force it visible so the shadow-rendered launcher button is not hidden.
  host.style.display = 'block';
  document.body.appendChild(host);

  const shadow = host.attachShadow({ mode: 'closed' });

  return { shadowHost: host, shadowRoot: shadow };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Check if the current page matches the widget's page rules (SPEC-1504, SPEC-1505).
 *
 * Rule prefixes:
 *   +  = include (show widget on matching pages)
 *   -  = exclude (hide widget on matching pages)
 *   no prefix = include (backward compat)
 *
 * Precedence: exclude wins over include.
 * Only-excludes list = show everywhere EXCEPT matches.
 * Only-includes list = show ONLY on matches.
 * Mixed = include unless also excluded.
 *
 * Match target: pathname + search (SPEC-1505), NOT just pathname.
 */
function shouldShowOnPage(config: WidgetConfig): boolean {
  const rules = config.widget_page_rules;
  if (!rules || rules.length === 0) return true; // no rules = show everywhere

  // SPEC-1505: Match against pathname + query string (not just pathname)
  const matchTarget = window.location.pathname + window.location.search;

  // Parse rules into include/exclude buckets
  const includes: RegExp[] = [];
  const excludes: RegExp[] = [];

  for (const raw of rules) {
    const trimmed = raw.trim();
    if (!trimmed) continue;

    let mode: 'include' | 'exclude' = 'include';
    let pattern = trimmed;

    // SPEC-1504: Parse +/- prefix
    if (trimmed.startsWith('-')) {
      mode = 'exclude';
      pattern = trimmed.slice(1);
    } else if (trimmed.startsWith('+')) {
      mode = 'include';
      pattern = trimmed.slice(1);
    }

    // SPEC-1504: Escape regex metacharacters, then convert glob * and ?
    const escaped = pattern
      .replace(/[.^${}()|[\]\\]/g, '\\$&')  // escape regex specials
      .replace(/\*/g, '.*')                   // glob * → regex .*
      .replace(/\?/g, '.');                   // glob ? → regex .
    const regex = new RegExp('^' + escaped + '$');

    if (mode === 'exclude') {
      excludes.push(regex);
    } else {
      includes.push(regex);
    }
  }

  // SPEC-1504: Exclude always wins
  for (const re of excludes) {
    if (re.test(matchTarget)) return false;
  }

  // Only-exclude rules: show everywhere except matches (already handled above)
  if (includes.length === 0) return true;

  // Include rules present: show only on matches
  for (const re of includes) {
    if (re.test(matchTarget)) return true;
  }

  return false;
}

/** Detect mobile devices. */
function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent,
  );
}

/** Build locale from config with auto-detect and merchant overrides. */
function buildLocale(config: WidgetConfig): Locale {
  const code = resolveLocaleCode(config.widget_locale);
  const pack = getLocalePack(code);
  return {
    ...pack,
    ...(config.widget_header_text ? { headerTitle: config.widget_header_text } : {}),
    ...(config.widget_input_placeholder ? { inputPlaceholder: config.widget_input_placeholder } : {}),
    ...(config.widget_offline_message ? { offlineMessage: config.widget_offline_message } : {}),
  };
}
