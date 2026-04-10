// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
// @ts-nocheck
/**
 * Mock API router — Express-style path matching for Vite dev server middleware.
 *
 * Converts route patterns like `/api/admin/team/:id` to regex,
 * extracts named params, and dispatches to registered handlers.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export type MockRequest = {
  method: string;
  path: string;
  params: Record<string, string>;
  query: Record<string, string>;
  body: unknown;
};

export type MockResponse = {
  status: number;
  body: unknown;
  headers?: Record<string, string>;
};

export type MockHandler = (req: MockRequest) => MockResponse | Promise<MockResponse>;

interface Route {
  method: string;
  pattern: RegExp;
  paramNames: string[];
  handler: MockHandler;
}

const routes: Route[] = [];

/**
 * Convert an Express-style path pattern to a regex.
 * e.g. `/api/admin/team/:id` -> /^\/api\/admin\/team\/([^/]+)$/
 */
function patternToRegex(pattern: string): { regex: RegExp; paramNames: string[] } {
  const paramNames: string[] = [];
  const regexStr = pattern
    .replace(/:([a-zA-Z_][a-zA-Z0-9_]*)/g, (_match, name) => {
      paramNames.push(name);
      return '([^/]+)';
    })
    // Support trailing wildcard: /api/analytics/*
    .replace(/\/\*$/, '(?:/.*)?');
  return { regex: new RegExp(`^${regexStr}$`), paramNames };
}

/** Register a route handler. */
export function route(method: string, pattern: string, handler: MockHandler): void {
  const { regex, paramNames } = patternToRegex(pattern);
  routes.push({ method: method.toUpperCase(), pattern: regex, paramNames, handler });
}

/** Convenience registration helpers. */
export const GET = (p: string, h: MockHandler) => route('GET', p, h);
export const POST = (p: string, h: MockHandler) => route('POST', p, h);
export const PUT = (p: string, h: MockHandler) => route('PUT', p, h);
export const DELETE = (p: string, h: MockHandler) => route('DELETE', p, h);
export const PATCH = (p: string, h: MockHandler) => route('PATCH', p, h);

/** Match a request against registered routes. Returns handler + params, or null. */
export function matchRoute(
  method: string,
  pathname: string,
): { handler: MockHandler; params: Record<string, string> } | null {
  const upperMethod = method.toUpperCase();
  for (const r of routes) {
    if (r.method !== upperMethod) continue;
    const match = r.pattern.exec(pathname);
    if (!match) continue;
    const params: Record<string, string> = {};
    r.paramNames.forEach((name, i) => {
      params[name] = decodeURIComponent(match[i + 1]);
    });
    return { handler: r.handler, params };
  }
  return null;
}

/** Clear all registered routes (useful for tests). */
export function clearRoutes(): void {
  routes.length = 0;
}
