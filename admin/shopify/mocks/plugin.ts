// @ts-nocheck
/**
 * Shopify Vite mock API plugin — configureServer hook that intercepts /api/* requests.
 *
 * Registered only in mock mode (vite --mode mock). Intercepts all API requests
 * before they reach the Vite proxy, returning mock data from the in-memory store.
 *
 * KEY DIFFERENCE from Standalone plugin:
 *   - Injects a fake App Bridge (`window.shopify.idToken()`) so ShopifyAppLayout
 *     can resolve session tokens without being inside a real Shopify iframe.
 *   - Injects `?shop=mock-store.myshopify.com` URL param so `getShopifyConfig()`
 *     finds a valid shop domain.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type { Plugin, ViteDevServer } from 'vite';

import { registerTenantHandlers } from './handlers/tenant';
import { registerDashboardHandlers } from './handlers/dashboard';
import { registerTeamHandlers } from './handlers/team';
import { registerInboxHandlers } from './handlers/inbox';
import { registerConfigHandlers } from './handlers/config';
import { registerKnowledgeHandlers } from './handlers/knowledge';
import { registerQuickActionHandlers } from './handlers/quick-actions';
import { registerWidgetHandlers } from './handlers/widget';
import { registerBillingHandlers } from './handlers/billing';

let handlersRegistered = false;
function ensureHandlers(): void {
  if (handlersRegistered) return;
  registerTenantHandlers();
  registerDashboardHandlers();
  registerTeamHandlers();
  registerInboxHandlers();
  registerConfigHandlers();
  registerKnowledgeHandlers();
  registerQuickActionHandlers();
  registerWidgetHandlers();
  registerBillingHandlers();
  handlersRegistered = true;
}

import { matchRoute } from './router';
import type { MockRequest } from './router';

/** Collect request body from Node IncomingMessage. */
function readBody(req: import('http').IncomingMessage): Promise<unknown> {
  return new Promise((resolve) => {
    const chunks: Buffer[] = [];
    req.on('data', (chunk: Buffer) => chunks.push(chunk));
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString('utf-8');
      if (!raw) { resolve(undefined); return; }
      try { resolve(JSON.parse(raw)); } catch { resolve(raw); }
    });
    req.on('error', () => resolve(undefined));
  });
}

/** Parse URL query string into a Record. */
function parseQuery(url: string): Record<string, string> {
  const idx = url.indexOf('?');
  if (idx === -1) return {};
  const params = new URLSearchParams(url.slice(idx + 1));
  const result: Record<string, string> = {};
  params.forEach((v, k) => { result[k] = v; });
  return result;
}

/**
 * App Bridge mock script — injected into the HTML so that ShopifyAppLayout's
 * `window.shopify.idToken()` resolves immediately with a mock JWT.
 *
 * Also injects `?shop=mock-store.myshopify.com` into the URL (if not present)
 * so `getShopifyConfig()` in index.tsx can find a valid shop domain.
 */
const APP_BRIDGE_MOCK_SCRIPT = `
<script>
  // --- Mock Shopify App Bridge ---
  window.shopify = {
    idToken: function() {
      return Promise.resolve('mock-shopify-session-token');
    },
    navigation: {
      dispatch: function() {}
    }
  };
  // Inject ?shop= param if missing (getShopifyConfig reads it)
  if (!new URLSearchParams(window.location.search).get('shop')) {
    var url = new URL(window.location.href);
    url.searchParams.set('shop', 'mock-store.myshopify.com');
    url.searchParams.set('host', btoa('mock-store.myshopify.com/admin'));
    window.history.replaceState({}, '', url.toString());
  }
</script>
`;

export function mockApiPlugin(): Plugin {
  return {
    name: 'agent-red-shopify-mock-api',

    // Inject App Bridge mock into the HTML and remove the real CDN script
    // so the real App Bridge doesn't overwrite our mock window.shopify.
    transformIndexHtml(html: string) {
      // Strip the real App Bridge CDN script
      const stripped = html.replace(
        /<script\s+src="https:\/\/cdn\.shopify\.com\/shopifycloud\/app-bridge\.js"><\/script>/,
        '<!-- App Bridge CDN removed in mock mode -->'
      );
      return stripped.replace('<head>', '<head>' + APP_BRIDGE_MOCK_SCRIPT);
    },

    configureServer(server: ViteDevServer) {
      ensureHandlers();

      server.middlewares.use(async (req, res, next) => {
        const url = req.url || '/';
        const pathname = url.split('?')[0];

        if (!pathname.startsWith('/api/') && pathname !== '/api') {
          next();
          return;
        }

        const method = (req.method || 'GET').toUpperCase();
        const matched = matchRoute(method, pathname);

        if (!matched) {
          res.writeHead(404, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ detail: 'Mock endpoint not registered: ' + method + ' ' + pathname }));
          return;
        }

        try {
          const body = method !== 'GET' ? await readBody(req) : undefined;
          const mockReq: MockRequest = {
            method,
            path: pathname,
            params: matched.params,
            query: parseQuery(url),
            body,
          };

          const mockRes = await matched.handler(mockReq);

          const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            'X-Mock': 'true',
            'X-Product-Version': '1.82.0-mock',
            ...mockRes.headers,
          };

          res.writeHead(mockRes.status, headers);
          res.end(JSON.stringify(mockRes.body));
        } catch (err) {
          console.error('[mock] Handler error:', err);
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ detail: 'Mock handler error: ' + String(err) }));
        }
      });

      console.log('[mock] Shopify API mock plugin active — App Bridge mocked, /api/* intercepted');
    },
  };
}
