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
import type { WidgetConfig } from '@/theme/tokens';
import { resolveTokens } from '@/theme/tokens';
import { en } from '@/locale/en';
import type { Locale } from '@/locale/en';
import { createStore } from '@/state/store';
import { configureTransport, fetchWidgetConfig } from '@/transport/http';
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
  const apiBaseUrl = scriptTag.getAttribute('data-api-url') || 'https://api.agentred.io';

  if (!widgetKey) {
    console.warn('[AgentRed] data-widget-key attribute is required.');
    return;
  }

  // Read inline overrides from data attributes (set by Shopify Liquid template)
  const dataOverrides: Record<string, string | boolean> = {};
  const attrMap: Record<string, string> = {
    'data-color': 'widget_primary_color',
    'data-position': 'widget_position',
    'data-auto-open': 'widget_auto_open',
    'data-auto-open-delay': 'widget_auto_open_delay',
    'data-mobile-enabled': 'widget_mobile_enabled',
    'data-sound-enabled': 'widget_sound_enabled',
    'data-greeting': 'greeting_message',
    'data-header-text': 'widget_header_text',
    'data-agent-name': 'widget_agent_display_name',
    'data-context': 'widget_context',
    'data-customer-name': 'widget_customer_name',
  };
  for (const [attr, configKey] of Object.entries(attrMap)) {
    const val = scriptTag.getAttribute(attr);
    if (val !== null) {
      // Convert boolean-like strings
      if (val === 'true') dataOverrides[configKey] = true;
      else if (val === 'false') dataOverrides[configKey] = false;
      else dataOverrides[configKey] = val;
    }
  }

  // Configure transport
  configureTransport({ apiBaseUrl, widgetKey });

  // Fetch config and initialize
  init(widgetKey, apiBaseUrl, dataOverrides).catch((err) => {
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
): Promise<void> {
  // Fetch widget configuration from the API
  const fetchedConfig = await fetchWidgetConfig();
  if (!fetchedConfig) {
    console.warn('[AgentRed] Failed to fetch widget configuration. Widget will not load.');
    return;
  }
  // Merge data-attribute overrides from the script tag (Shopify Liquid template)
  // These take precedence over API-fetched config so merchants can configure
  // basic settings directly in the Shopify theme editor.
  const config: WidgetConfig = dataOverrides
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

  // Determine initial view
  const hasPrechat = config.widget_prechat_form
    && (config.widget_prechat_form as { fields?: unknown[] }).fields?.length;
  const initialView = hasPrechat ? 'prechat' : 'conversation';

  // Mount launcher in Shadow DOM
  const { shadowHost, shadowRoot } = mountLauncherHost();

  // State for tracking panel iframe
  let panelIframe: HTMLIFrameElement | null = null;

  // Resolve tokens for launcher
  const tokens = resolveTokens(config);

  // ---- Launcher rendering -------------------------------------------------

  function renderLauncher() {
    const state = store.getState();
    render(
      h(Launcher, {
        tokens,
        position: config.widget_position || 'bottom-right',
        offsetX: config.widget_offset_x ?? 20,
        offsetY: config.widget_offset_y ?? 20,
        isOpen: state.view !== 'closed',
        unreadCount: state.unreadCount,
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
    const position = config.widget_position || 'bottom-right';
    const offsetX = config.widget_offset_x ?? 20;
    const offsetY = config.widget_offset_y ?? 20;
    const launcherSize = 60;
    const gap = 12;

    iframe.style.cssText = [
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

  function showPanel() {
    if (!panelIframe) {
      panelIframe = createPanelIframe();
    }

    // Double-rAF ensures the browser has painted the initial opacity:0 state
    // before we transition to opacity:1. A single rAF often fires in the same
    // paint frame as the DOM insertion, causing the transition to be skipped.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (panelIframe) {
          panelIframe.style.opacity = '1';
          panelIframe.style.transform = 'translateY(0) scale(1)';
          panelIframe.style.pointerEvents = 'auto';
        }
      });
    });
  }

  function hidePanel() {
    if (panelIframe) {
      panelIframe.style.opacity = '0';
      panelIframe.style.transform = 'translateY(12px) scale(0.95)';
      panelIframe.style.pointerEvents = 'none';
    }
  }

  // ---- Widget control functions -------------------------------------------

  function openWidget() {
    store.setState({ view: initialView, unreadCount: 0 });
    showPanel();
  }

  function closeWidget() {
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
      delete (window as unknown as Record<string, unknown>).AgentRed;
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

/** Check if the current page matches the widget's page rules. */
function shouldShowOnPage(config: WidgetConfig): boolean {
  const rules = config.widget_page_rules;
  if (!rules || rules.length === 0) return true; // no rules = show everywhere

  const currentPath = window.location.pathname;

  for (const rule of rules) {
    // Simple glob matching: * matches anything
    const regex = new RegExp(
      '^' + rule.replace(/\*/g, '.*').replace(/\?/g, '.') + '$',
    );
    if (regex.test(currentPath)) return true;
  }

  return false;
}

/** Detect mobile devices. */
function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent,
  );
}

/** Build locale with merchant overrides applied. */
function buildLocale(config: WidgetConfig): Locale {
  return {
    ...en,
    ...(config.widget_header_text ? { headerTitle: config.widget_header_text } : {}),
    ...(config.widget_input_placeholder ? { inputPlaceholder: config.widget_input_placeholder } : {}),
    ...(config.widget_offline_message ? { offlineMessage: config.widget_offline_message } : {}),
  };
}
