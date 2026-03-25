// @ts-nocheck
/**
 * Mock API router — Express-style path matching for Vite dev server middleware.
 *
 * Converts route patterns like `/api/admin/team/:id` to regex,
 * extracts named params, and dispatches to registered handlers.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
const routes = [];
/**
 * Convert an Express-style path pattern to a regex.
 * e.g. `/api/admin/team/:id` -> /^\/api\/admin\/team\/([^/]+)$/
 */
function patternToRegex(pattern) {
    const paramNames = [];
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
export function route(method, pattern, handler) {
    const { regex, paramNames } = patternToRegex(pattern);
    routes.push({ method: method.toUpperCase(), pattern: regex, paramNames, handler });
}
/** Convenience registration helpers. */
export const GET = (p, h) => route('GET', p, h);
export const POST = (p, h) => route('POST', p, h);
export const PUT = (p, h) => route('PUT', p, h);
export const DELETE = (p, h) => route('DELETE', p, h);
/** Match a request against registered routes. Returns handler + params, or null. */
export function matchRoute(method, pathname) {
    const upperMethod = method.toUpperCase();
    for (const r of routes) {
        if (r.method !== upperMethod)
            continue;
        const match = r.pattern.exec(pathname);
        if (!match)
            continue;
        const params = {};
        r.paramNames.forEach((name, i) => {
            params[name] = decodeURIComponent(match[i + 1]);
        });
        return { handler: r.handler, params };
    }
    return null;
}
/** Clear all registered routes (useful for tests). */
export function clearRoutes() {
    routes.length = 0;
}
//# sourceMappingURL=router.js.map