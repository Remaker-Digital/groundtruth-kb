/**
 * Template variable substitution for quick action prompts (WI #229).
 *
 * Replaces {{variable}} placeholders in prompt templates with page context
 * values detected from the current page (Shopify data attributes + URL).
 *
 * Supported variables:
 *   {{page_type}}         — home, product, collection, cart, search, blog, page, other
 *   {{page_handle}}       — URL slug or Shopify handle
 *   {{page_title}}        — document.title
 *   {{page_url}}          — window.location.href
 *   {{product_title}}     — from data-product-title attribute
 *   {{collection_title}}  — from data-collection-title attribute
 *
 * Unresolved variables are left as-is (e.g. {{unknown}} stays literally).
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// ---------------------------------------------------------------------------
// Page context
// ---------------------------------------------------------------------------

export interface PageContext {
  page_type: string;
  page_handle: string;
  page_title: string;
  page_url: string;
  product_title?: string;
  collection_title?: string;
}

/**
 * Detect page context from Shopify data attributes and URL patterns.
 *
 * Shopify theme extensions can emit `data-page-type`, `data-page-handle`,
 * `data-product-title`, and `data-collection-title` on the widget script tag.
 * When those are absent, we fall back to URL-based detection.
 */
export function detectPageContext(): PageContext {
  const scriptTag = document.querySelector('script[data-widget-key]');

  return {
    page_type:
      scriptTag?.getAttribute('data-page-type') ||
      detectPageTypeFromUrl(window.location.pathname),
    page_handle:
      scriptTag?.getAttribute('data-page-handle') ||
      extractHandleFromUrl(window.location.pathname),
    page_title: document.title,
    page_url: window.location.href,
    product_title:
      scriptTag?.getAttribute('data-product-title') || undefined,
    collection_title:
      scriptTag?.getAttribute('data-collection-title') || undefined,
  };
}

// ---------------------------------------------------------------------------
// URL-based detection (fallback when no Shopify data attributes)
// ---------------------------------------------------------------------------

/**
 * Detect page type from the URL pathname.
 *
 * Shopify's `template.name` values map to:
 *   index → home, product → product, collection → collection,
 *   cart → cart, search → search, blog → blog, page → page
 */
export function detectPageTypeFromUrl(pathname: string): string {
  const p = pathname.replace(/\/$/, ''); // strip trailing slash
  if (p === '' || p === '/') return 'home';
  if (p.startsWith('/products/')) return 'product';
  if (p.startsWith('/collections/')) return 'collection';
  if (p.startsWith('/cart')) return 'cart';
  if (p.startsWith('/search')) return 'search';
  if (p.startsWith('/blogs/')) return 'blog';
  if (p.startsWith('/pages/')) return 'page';
  return 'other';
}

/**
 * Extract the URL handle (last path segment) from a pathname.
 */
export function extractHandleFromUrl(pathname: string): string {
  const segments = pathname.replace(/\/$/, '').split('/').filter(Boolean);
  return segments[segments.length - 1] || '';
}

// ---------------------------------------------------------------------------
// Template resolution
// ---------------------------------------------------------------------------

/**
 * Replace `{{variable}}` placeholders in a template string with values
 * from the page context.
 *
 * Supports simple dot-free keys only (e.g. `{{product_title}}`).
 * Unresolved variables are left as-is so the AI sees them as raw text
 * rather than receiving empty strings.
 */
export function resolveTemplate(
  template: string,
  context: PageContext,
): string {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key: string) => {
    const ctx = context as unknown as Record<string, unknown>;
    const value = ctx[key];
    return value !== undefined && value !== null ? String(value) : match;
  });
}
