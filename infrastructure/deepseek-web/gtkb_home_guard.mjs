// GT-KB native effect guard for the GT-KB Home server (DeepSeek Harness Web UI): many sessions per process.
//
// Every effect-bearing tool call of every Home session is checked by GT-KB's shared effect gate
// (scripts/implementation_start_gate.py) under that session's own native context identifier and workspace, read per call
// from execution.agent.session.header. Reads pass without a gate call; network tools and unrecognized tools are denied.
// The gate runs asynchronously in the tools/pre-execute stage, and its approval is bound to the exact arguments. The
// monotonic ctx.tools.guard backstop denies any effect that reaches execution without that approval (a skipped or
// reordered stage, or arguments changed after approval). Anything but a clean empty gate answer denies: exit status,
// timeout, spawn error and malformed output all refuse. The SDK harness keeps its own single-context guard
// (infrastructure/deepseek-sdk/gtkb_guard.mjs).
import { spawn } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import { isAbsolute, resolve } from 'node:path';

export const name = 'gtkb-home-effect-guard';
export const inject = ['tools'];

const GATE_TIMEOUT_MS = 20000;
const READ_ONLY = new Set([
  'read', 'glob', 'grep', 'read_image', 'skill', 'todo_write', 'ask_user_question', 'get_goal', 'create_goal',
  'update_goal', 'list_agents', 'job_list', 'job_output', 'job_kill', 'exit_plan_mode', 'send_message', 'interrupt_agent',
]);
// Their own calls meet this same host-level guard, so launching them is not itself an effect.
const ORCHESTRATION = new Set(['subagent', 'subagent_fork', 'ralph']);
const NETWORK = new Set(['web_fetch', 'web_search']);
const EDITOR_EFFECTS = new Set(['create', 'str_replace', 'insert']);

function required(variable) {
  const value = process.env[variable];
  if (!value) throw new Error(`GT-KB Home guard: ${variable} is not set`);
  return value;
}

function absolute(cwd, target) {
  if (typeof target !== 'string' || target.length === 0) return target;
  return isAbsolute(target) ? target : resolve(cwd, target);
}

// Return {kind: 'allow'} | {kind: 'deny', reason} | {kind: 'gate', payload} for one call in one session.
export function classify(execution) {
  const tool = execution.name;
  const args = execution.arguments ?? {};
  const header = execution.agent?.session?.header;
  if (READ_ONLY.has(tool) || ORCHESTRATION.has(tool)) return { kind: 'allow' };
  if (NETWORK.has(tool)) return { kind: 'deny', reason: 'GT-KB: network tools are disabled in GT-KB Home until the owner enables them' };
  const context = header?.id;
  const cwd = header?.cwd;
  if (typeof context !== 'string' || context.length === 0 || typeof cwd !== 'string' || cwd.length === 0) {
    return { kind: 'deny', reason: 'GT-KB: the tool call carries no session identity or workspace' };
  }
  let toolInput;
  let claudeTool;
  if (tool === 'write') {
    claudeTool = 'Write';
    toolInput = { file_path: absolute(cwd, args.file_path ?? args.path) };
  } else if (tool === 'edit') {
    claudeTool = 'Edit';
    toolInput = { file_path: absolute(cwd, args.file_path ?? args.path) };
  } else if (tool === 'str_replace_editor') {
    if (args.command === 'view') return { kind: 'allow' };
    if (!EDITOR_EFFECTS.has(args.command)) return { kind: 'deny', reason: 'GT-KB: unknown editor effect' };
    claudeTool = args.command === 'create' ? 'Write' : 'Edit';
    toolInput = { file_path: absolute(cwd, args.path) };
  } else if (tool === 'pwsh' || tool === 'bash') {
    claudeTool = 'Bash';
    toolInput = { command: args.command };
  } else {
    return { kind: 'deny', reason: `GT-KB: the tool ${tool} is not recognized by the GT-KB gate` };
  }
  return { kind: 'gate', payload: { tool_name: claudeTool, tool_input: toolInput, cwd, session_id: context } };
}

const SECRET_NAME = /KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL/i;

// The gate needs no model credential or control secret: they never reach it.
function gateEnvironment(settings, context) {
  const env = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (!SECRET_NAME.test(key)) env[key] = value;
  }
  return { ...env, GTKB_NATIVE_CONTEXT_ID: context, GT_PROJECT_ROOT: settings.root };
}

function runGate(settings, payload, signal) {
  return new Promise((done) => {
    const child = spawn(settings.python, ['-B', settings.gate], {
      cwd: settings.root,
      windowsHide: true,
      env: gateEnvironment(settings, payload.session_id),
    });
    let stdout = '';
    let settled = false;
    const finish = (verdict) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      signal?.removeEventListener?.('abort', abort);
      done(verdict);
    };
    const abort = () => { child.kill(); finish({ allowed: false, reason: 'GT-KB guard: the call was cancelled' }); };
    const timer = setTimeout(() => { child.kill(); finish({ allowed: false, reason: 'GT-KB guard: the effect gate timed out' }); }, GATE_TIMEOUT_MS);
    signal?.addEventListener?.('abort', abort, { once: true });
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.on('error', (error) => finish({ allowed: false, reason: `GT-KB guard: ${error.message}` }));
    child.on('close', (status) => {
      let parsed;
      try { parsed = JSON.parse(stdout); } catch { parsed = undefined; }
      const allowed = status === 0 && parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed) && Object.keys(parsed).length === 0;
      finish({ allowed, status, reason: allowed ? null : (parsed?.hookSpecificOutput?.permissionDecisionReason || 'GT-KB guard: native effect check failed') });
    });
    child.stdin.end(JSON.stringify({ ...payload, project_root: settings.root }));
  });
}

export function apply(ctx) {
  const settings = { python: required('GTKB_GUARD_PYTHON'), gate: required('GTKB_GUARD_GATE'), root: required('GT_PROJECT_ROOT') };
  const log = process.env.GTKB_GUARD_LOG;
  const approvals = new Map(); // callId -> the exact arguments the gate approved
  const record = (entry) => {
    if (!log) return;
    try { appendFileSync(log, JSON.stringify({ time: new Date().toISOString(), ...entry }) + '\n'); } catch { /* diagnostics only */ }
  };
  ctx.on('tools/pre-execute', async (execution, next) => {
    const plan = classify(execution);
    if (plan.kind === 'deny') {
      record({ tool: execution.name, session: execution.agent?.session?.header?.id ?? null, allowed: false, reason: plan.reason });
      return { kind: 'deny', reason: plan.reason };
    }
    if (plan.kind === 'gate') {
      const verdict = await runGate(settings, plan.payload, execution.signal);
      record({ tool: execution.name, session: plan.payload.session_id, status: verdict.status ?? null, allowed: verdict.allowed, reason: verdict.reason });
      if (!verdict.allowed) return { kind: 'deny', reason: verdict.reason };
      approvals.set(execution.callId, JSON.stringify(execution.arguments ?? {}));
    }
    return next();
  });
  ctx.tools.guard((execution) => {
    const plan = classify(execution);
    if (plan.kind === 'deny') return plan.reason;
    if (plan.kind === 'gate') {
      const approved = approvals.get(execution.callId);
      approvals.delete(execution.callId);
      if (approved === undefined) return 'GT-KB guard: the effect was not checked by the GT-KB gate';
      if (approved !== JSON.stringify(execution.arguments ?? {})) return 'GT-KB guard: the arguments changed after the GT-KB gate approved them';
    }
    return undefined;
  });
  process.stderr.write('gtkb-home-effect-guard active\n');
}
