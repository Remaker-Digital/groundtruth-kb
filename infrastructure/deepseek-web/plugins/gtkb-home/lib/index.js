// GT-KB Home, host side (DeepSeek Harness Cordis plugin; owner rulings D58, D59).
//
// - Serves the Remaker Digital marks from this package's assets at exact routes (public static images), including the
//   tab icon /favicon.svg, a GT-KB web manifest, and the third-party notices at /gtkb-home/notices.
// - Rewrites the page title to "GT-KB Home" (the client keeps it that way at run time).
// - Registers the authenticated RPC channel /gtkb behind the shell's Host/Origin fence and the owner's browser cookie.
//   Every endpoint runs one fixed `gt` argument vector (no shell string) with a scrubbed environment and returns its
//   JSON: status, services status/start/stop (not the Home itself), controls show, and a configuration change as
//   propose (a complete proposed artifact plus its diff) then apply (`gt controls set` against the previewed digest).
//   These controls are browser actions of the signed-in owner, never model tools.
// - Registers a loopback control route for GT-KB's Home service: POST /gtkb-home/control/shutdown with the per-start
//   secret runs the harness's own teardown (the harness has no HTTP shutdown and Windows cannot deliver SIGTERM).
import { spawn } from 'node:child_process';
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { mkdirSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';

export const name = 'gtkb-home';
export const inject = ['connection', 'webServer'];

const SECRET_NAME = /KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL/i;
const ASSETS = {
  '/favicon.svg': 'mark.svg',
  '/gtkb-home/mark.svg': 'mark.svg',
  '/gtkb-home/logo.svg': 'logo-dark.svg',
  '/gtkb-home/logo-light.svg': 'logo-light.svg',
};
const MANIFEST = JSON.stringify({
  id: '/',
  name: 'GT-KB Home',
  short_name: 'GT-KB',
  start_url: '/',
  scope: '/',
  display: 'fullscreen',
  icons: [{ src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }],
});
// Start and stop are offered for these; the Home never starts or stops itself from its own page (gt services can).
const CONTROLLABLE = new Set(['authority', 'dashboard', 'ollama', 'postgresql']);
const CONTROL_ID = /^[A-Za-z0-9_.-]{1,160}$/;
const CONTROL_VALUE = /^[0-9]{1,30}(\.[0-9]{1,30})?$/;
const CATALOG_SHA = /^sha256:[0-9a-f]{64}$/;

class BadRequest extends Error {}

function failure(code, message) {
  return { ok: false, error: { code, message, details: {} } };
}

function service(payload) {
  if (typeof payload.name !== 'string' || !CONTROLLABLE.has(payload.name)) throw new BadRequest('unknown or disallowed service');
  return payload.name;
}

// One outstanding configuration proposal at a time: a complete proposed artifact in the Home state folder, named by
// an unguessable handle. `gt controls set` later applies exactly that file, and only if the live artifact still has the
// digest the owner previewed against.
class Proposals {
  constructor(folder) {
    this.folder = folder;
    this.current = undefined;
    rmSync(folder, { recursive: true, force: true });
  }

  create() {
    this.discard();
    mkdirSync(this.folder, { recursive: true });
    const handle = randomBytes(16).toString('hex');
    this.current = { handle, path: join(this.folder, `${handle}.toml`) };
    return this.current;
  }

  find(handle) {
    return this.current !== undefined && this.current.handle === handle ? this.current : undefined;
  }

  discard() {
    if (this.current !== undefined) rmSync(this.current.path, { force: true });
    this.current = undefined;
  }
}

// Endpoint -> plan: one fixed argument vector for `gt` (inputs validated, never interpolated into a shell string), an
// optional completion step, and an optional reshaping of the command's JSON for the browser.
function endpoints(proposals) {
  return {
    status: () => ({ argv: ['status', '--json'] }),
    'services/status': () => ({ argv: ['services', 'status', '--json'] }),
    'services/start': (payload) => ({ argv: ['services', 'start', service(payload), '--json'] }),
    'services/stop': (payload) => ({ argv: ['services', 'stop', service(payload), '--json'] }),
    'controls/show': () => ({ argv: ['controls', 'show'] }),
    'controls/propose': (payload) => {
      const controlId = String(payload.control_id ?? '');
      const value = String(payload.value ?? '');
      if (!CONTROL_ID.test(controlId) || !CONTROL_VALUE.test(value)) throw new BadRequest('invalid control id or value');
      const { handle, path } = proposals.create();
      return {
        argv: ['controls', 'propose', '--control', controlId, '--value', value, '--output', path],
        done: (ok) => { if (!ok) proposals.discard(); },
        shape: ({ proposal, ...diff }) => ({ ...diff, handle }),
      };
    },
    'controls/apply': (payload) => {
      const found = proposals.find(String(payload.handle ?? ''));
      const expected = String(payload.expected_sha256 ?? '');
      if (found === undefined || !CATALOG_SHA.test(expected)) throw new BadRequest('unknown proposal or invalid expected digest');
      return {
        argv: ['controls', 'set', '--input', found.path, '--expected-sha256', expected],
        done: () => proposals.discard(),
      };
    },
  };
}

function childEnvironment() {
  const env = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (!SECRET_NAME.test(key)) env[key] = value;
  }
  return env;
}

function runGt(config, args, timeoutMs) {
  return new Promise((resolve) => {
    const [command, ...prefix] = config.gtArgv;
    const child = spawn(command, [...prefix, ...args], { cwd: config.gtCwd, env: childEnvironment(), windowsHide: true });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill(), timeoutMs);
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => { clearTimeout(timer); resolve({ code: -1, stdout, stderr: String(error) }); });
    child.on('close', (code) => { clearTimeout(timer); resolve({ code, stdout, stderr }); });
  });
}

function sameSecret(offered, expected) {
  const a = Buffer.from(String(offered ?? ''));
  const b = Buffer.from(String(expected ?? ''));
  return a.length === b.length && a.length > 0 && timingSafeEqual(a, b);
}

function loopback(req) {
  const address = req.socket?.remoteAddress ?? '';
  return address === '127.0.0.1' || address === '::1' || address === '::ffff:127.0.0.1';
}

export function apply(ctx, config = {}) {
  if (!Array.isArray(config.gtArgv) || config.gtArgv.some((part) => typeof part !== 'string' || part.length === 0)
      || typeof config.gtCwd !== 'string' || config.gtCwd.length === 0) {
    throw new Error('gtkb-home: config.gtArgv and config.gtCwd are required');
  }
  for (const [route, file] of Object.entries(ASSETS)) {
    const bytes = readFileSync(new URL(`../assets/${file}`, import.meta.url));
    ctx.webServer.register({
      kind: 'exact',
      path: route,
      handler: (req, res) => {
        res.writeHead(200, { 'content-type': 'image/svg+xml', 'cache-control': 'no-cache' });
        res.end(bytes);
      },
    });
  }
  const publicText = (path, type, body) => ctx.webServer.register({
    kind: 'exact',
    path,
    handler: (req, res) => {
      res.writeHead(200, { 'content-type': type, 'cache-control': 'no-cache' });
      res.end(body);
    },
  });
  publicText('/manifest.webmanifest', 'application/manifest+json', MANIFEST);
  publicText('/gtkb-home/notices', 'text/plain; charset=utf-8', readFileSync(new URL('../../../THIRD-PARTY-NOTICES.md', import.meta.url)));
  ctx.webServer.tapIndex((html) => html.replace(/<title>[^<]*<\/title>/, '<title>GT-KB Home</title>'));
  ctx.webServer.register({
    kind: 'exact',
    path: '/gtkb-home/control/shutdown',
    handler: (req, res) => {
      if (req.method !== 'POST' || !loopback(req) || !sameSecret(req.headers['x-gtkb-control'], process.env.GTKB_HOME_CONTROL_SECRET)) {
        res.writeHead(403);
        res.end('forbidden');
        return;
      }
      res.writeHead(202);
      res.end('stopping');
      setImmediate(() => process.emit('SIGTERM', 'SIGTERM'));
    },
  });
  if (typeof process.env.DSH_HOME !== 'string' || process.env.DSH_HOME.length === 0) {
    throw new Error('gtkb-home: DSH_HOME must name the Home state folder');
  }
  const table = endpoints(new Proposals(join(process.env.DSH_HOME, 'run', 'controls-proposals')));
  // The Connection contract: every failure carries code, message and a details object, or the browser rejects it.
  ctx.connection.rpc.handle('/gtkb', async (endpoint, payload) => {
    const build = Object.hasOwn(table, endpoint) ? table[endpoint] : undefined;
    if (build === undefined) return failure('gtkb/unknown-endpoint', `unknown endpoint ${endpoint}`);
    let plan;
    try {
      plan = build(payload !== null && typeof payload === 'object' ? payload : {});
    } catch (error) {
      if (error instanceof BadRequest) return failure('gtkb/bad-request', error.message);
      return failure('gtkb/internal', String(error));
    }
    const result = await runGt(config, plan.argv, config.timeoutMs ?? 300000);
    plan.done?.(result.code === 0);
    if (result.code !== 0) return failure('gtkb/command-failed', (result.stderr || result.stdout).trim().slice(-2000));
    let value;
    try {
      value = JSON.parse(result.stdout);
    } catch {
      return failure('gtkb/not-json', result.stdout.slice(0, 500));
    }
    return { ok: true, value: plan.shape ? plan.shape(value) : value };
  });
  process.stderr.write('gtkb-home active\n');
}
