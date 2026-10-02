// GT-KB native effect guard for the GT-KB Home server (DeepSeek Harness Web UI): many sessions per process.
//
// Every effect-bearing tool call of every Home session is checked by GT-KB's shared effect gate
// (scripts/implementation_start_gate.py) under that session's own native context identifier and workspace, read per call
// from execution.agent.session.header. File reads and searches reach the same gate as reads: it refuses credential material
// (c117) and allows the rest. Other non-effect tools pass without a gate call; network and unrecognized tools are denied.
// The gate runs asynchronously in the tools/pre-execute stage, and its approval is bound to the exact arguments. The
// monotonic ctx.tools.guard backstop denies any effect that reaches execution without that approval (a skipped or
// reordered stage, or arguments changed after approval). Anything but a clean empty gate answer denies: exit status,
// timeout, spawn error and malformed output all refuse. The SDK harness keeps its own single-context guard
// (infrastructure/deepseek-sdk/gtkb_guard.mjs).
// c123 (owner decision C1): one Home, one project. A session whose workspace lies outside the Home's project root is
// refused before any gate call, and so is a one-shot shell call whose workdir does; a workdir inside it is the folder
// the gate judges that command from. c123 (owner decision A6): a call to a shell whose directory persists across calls
// is marked persistent_shell for the gate.
import { spawn } from 'node:child_process';
import { appendFileSync, realpathSync } from 'node:fs';
import { isAbsolute, relative, resolve, sep } from 'node:path';

export const name = 'gtkb-home-effect-guard';
export const inject = ['tools'];

const GATE_TIMEOUT_MS = 20000;
const READ_ONLY = new Set([
  'skill', 'todo_write', 'ask_user_question', 'get_goal', 'create_goal',
  'update_goal', 'list_agents', 'job_list', 'job_output', 'job_kill', 'exit_plan_mode', 'send_message', 'interrupt_agent',
]);
// File reads and searches: gated as reads with every argument, so a credential path or glob is refused (c117).
const FILE_READS = { read: 'Read', read_image: 'Read', glob: 'Glob', grep: 'Grep' };
// Their own calls meet this same host-level guard, so launching them is not itself an effect.
const ORCHESTRATION = new Set(['subagent', 'subagent_fork', 'ralph']);
const NETWORK = new Set(['web_fetch', 'web_search']);
const EDITOR_EFFECTS = new Set(['create', 'str_replace', 'insert']);

function required(variable) {
  const value = process.env[variable];
  if (!value) throw new Error(`GroundTruth KB guard: ${variable} is not set`);
  return value;
}

function absolute(cwd, target) {
  if (typeof target !== 'string' || target.length === 0) return target;
  return isAbsolute(target) ? target : resolve(cwd, target);
}

// c123 (batch design WP3 3.1(a)): Windows paths compare without letter case.
const fold = (path) => (process.platform === 'win32' ? path.toLowerCase() : path);

// c123 (batch design WP3 3.1(a)): where a folder really is, resolved through junctions and links, and whether that lies
// inside the Home's resolved project root. A path that cannot be resolved is outside, with the reason it failed.
function placement(root, path) {
  if (typeof path !== 'string' || path.length === 0) return { inside: false, error: 'not a path' };
  let real;
  try { real = realpathSync.native(path); } catch (error) { return { inside: false, error: error?.code ?? 'unreadable' }; }
  if (typeof root !== 'string' || root.length === 0) return { inside: false, real };
  const rel = relative(fold(root), fold(real));
  return { inside: rel === '' || (rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel)), real };
}

// c123 (batch design WP3 3.1(a)): whether a workspace lies inside the Home's resolved project root; one that cannot be
// resolved is outside.
export function insideRoot(root, cwd) {
  return placement(root, cwd).inside;
}

// c123 (owner decision C1): 3.1's refusal. When the path resolves somewhere else, or not at all, it also says where it
// resolves or why it cannot be resolved.
function outsideRoot(subject, given, place, root, remedy) {
  const spelled = place.real !== undefined && isAbsolute(given) && fold(resolve(given)) === fold(place.real);
  const where = place.real === undefined ? ` (it cannot be resolved: ${place.error})` : spelled ? '' : ` (resolved: ${place.real})`;
  return `GroundTruth KB: workspace_outside_project_root: ${subject} ${given}${where} is outside the Home's project root ${root}, and the effect gate judges only that project. ${remedy}`;
}

// c123 (owner decision A6): the parameters a shell's definition declares, or undefined when it cannot be read.
// Upstream's one-shot shells take a per-call workdir because nothing persists between their calls (dsh-tool-pwsh and
// dsh-tool-bash 0.1.2-rc.1); the persistent shells take only a command and ignore any other argument
// (dsh-tool-pwsh-persistent and dsh-tool-bash-persistent, which the shipped minimal agent preset mounts).
function shellParameters(definition) {
  const properties = definition?.parameters?.properties;
  return properties !== null && typeof properties === 'object' ? properties : undefined;
}

// c123 (owner decision A6): whether the shell keeps its directory across calls. A definition this guard cannot read
// counts as persistent, the stricter case.
function persistentShell(definition) {
  const properties = shellParameters(definition);
  return properties === undefined || !Object.hasOwn(properties, 'workdir');
}

// c123 (owner decision C1): whether the shell runs a command in the workdir the call names. A definition this guard
// cannot read counts as one that does, so its workdir is judged.
function takesWorkdir(definition) {
  const properties = shellParameters(definition);
  return properties === undefined || Object.hasOwn(properties, 'workdir');
}

// Return {kind: 'allow'} | {kind: 'deny', reason} | {kind: 'gate', payload} for one call in one session.
// c123 (batch design WP3 3.1(a)): root is the Home's resolved project root. c123 (owner decision A6): definitionOf
// returns the tool definition the call resolves to; without it a shell counts as persistent and as running a command in
// the workdir the call names.
export function classify(execution, root, definitionOf = () => undefined) {
  const tool = execution.name;
  const args = execution.arguments ?? {};
  const header = execution.agent?.session?.header;
  if (READ_ONLY.has(tool) || ORCHESTRATION.has(tool)) return { kind: 'allow' };
  if (NETWORK.has(tool)) return { kind: 'deny', reason: 'GroundTruth KB: network tools are disabled in the Home until the owner enables them' };
  const context = header?.id;
  const cwd = header?.cwd;
  if (typeof context !== 'string' || context.length === 0 || typeof cwd !== 'string' || cwd.length === 0) {
    return { kind: 'deny', reason: 'GroundTruth KB: the tool call carries no session identity or workspace' };
  }
  // c123 (owner decision C1): the gate judges only the Home's project, so every gated call of a session whose workspace
  // lies outside the Home's root is refused here, reads included, before any gate call.
  const workspace = placement(root, cwd);
  if (!workspace.inside) {
    return {
      kind: 'deny',
      reason: outsideRoot("this session's workspace", cwd, workspace, root, `Start a new session in a workspace inside ${root}.`),
    };
  }
  let toolInput;
  let claudeTool;
  let persistent = false;
  let judgedFrom = cwd;
  if (Object.hasOwn(FILE_READS, tool)) {
    claudeTool = FILE_READS[tool];
    toolInput = { ...args };
  } else if (tool === 'write') {
    claudeTool = 'Write';
    toolInput = { file_path: absolute(cwd, args.file_path ?? args.path) };
  } else if (tool === 'edit') {
    claudeTool = 'Edit';
    toolInput = { file_path: absolute(cwd, args.file_path ?? args.path) };
  } else if (tool === 'str_replace_editor') {
    if (args.command === 'view') {
      claudeTool = 'Read';
    } else {
      if (!EDITOR_EFFECTS.has(args.command)) return { kind: 'deny', reason: 'GroundTruth KB: unknown editor effect' };
      claudeTool = args.command === 'create' ? 'Write' : 'Edit';
    }
    toolInput = { file_path: absolute(cwd, args.path) };
  } else if (tool === 'pwsh' || tool === 'bash') {
    claudeTool = 'Bash';
    toolInput = { command: args.command };
    const definition = definitionOf(execution);
    // c123 (owner decision A6): the gate refuses a top-level directory change in a shell whose directory persists.
    persistent = persistentShell(definition);
    // c123 (owner decision C1): a one-shot shell runs the command in the workdir the call names, absolute or relative to
    // the workspace (dsh-tool-pwsh 0.1.2-rc.1, resolveWorkdir). That folder must lie inside the root too, and the gate
    // judges the command from it. A persistent shell ignores a workdir, so its calls are judged from the workspace.
    if (args.workdir !== undefined && takesWorkdir(definition)) {
      const named = typeof args.workdir === 'string';
      const given = named ? args.workdir : JSON.stringify(args.workdir);
      const place = placement(root, named ? (isAbsolute(args.workdir) ? args.workdir : resolve(cwd, args.workdir)) : undefined);
      if (!place.inside) {
        return { kind: 'deny', reason: outsideRoot("this call's workdir", given, place, root, `Use a workdir inside ${root}, or none.`) };
      }
      judgedFrom = place.real;
    }
  } else {
    return { kind: 'deny', reason: `GroundTruth KB: the tool ${tool} is not recognized by the effect gate` };
  }
  const payload = { tool_name: claudeTool, tool_input: toolInput, cwd: judgedFrom, session_id: context };
  return { kind: 'gate', payload: persistent ? { ...payload, persistent_shell: true } : payload };
}

// c123 (batch design WP3 3.1(a)): the root every workspace is compared with, resolved once. A root that cannot be
// resolved throws, so the activation line never appears and home.py start fails closed.
function resolvedRoot(root) {
  try {
    return realpathSync.native(root);
  } catch (error) {
    throw new Error(`GroundTruth KB guard: the project root ${root} cannot be resolved: ${error.message}`);
  }
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
    const abort = () => { child.kill(); finish({ allowed: false, reason: 'GroundTruth KB guard: the call was cancelled' }); };
    const timer = setTimeout(() => { child.kill(); finish({ allowed: false, reason: 'GroundTruth KB guard: the effect gate timed out' }); }, GATE_TIMEOUT_MS);
    signal?.addEventListener?.('abort', abort, { once: true });
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.on('error', (error) => finish({ allowed: false, reason: `GroundTruth KB guard: ${error.message}` }));
    child.on('close', (status) => {
      let parsed;
      try { parsed = JSON.parse(stdout); } catch { parsed = undefined; }
      const allowed = status === 0 && parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed) && Object.keys(parsed).length === 0;
      finish({ allowed, status, reason: allowed ? null : (parsed?.hookSpecificOutput?.permissionDecisionReason || 'GroundTruth KB guard: native effect check failed') });
    });
    child.stdin.end(JSON.stringify({ ...payload, project_root: settings.root }));
  });
}

export function apply(ctx) {
  const settings = { python: required('GTKB_GUARD_PYTHON'), gate: required('GTKB_GUARD_GATE'), root: required('GT_PROJECT_ROOT') };
  // c123 (batch design WP3 3.1(a)): the gate still receives the root as configured; only the workspace comparison uses
  // the resolved root.
  const root = resolvedRoot(settings.root);
  // c123 (owner decision A6): the definition a call resolves to, as the calling agent sees it (the same lookup
  // upstream's call-timeout policy makes per call). A failed lookup reads as unknown: that shell counts as persistent,
  // and its workdir is judged.
  const definitionOf = (execution) => {
    try { return ctx.tools.get(execution.name, execution.agent); } catch { return undefined; }
  };
  const log = process.env.GTKB_GUARD_LOG;
  const approvals = new Map(); // callId -> the exact arguments the gate approved
  const record = (entry) => {
    if (!log) return;
    try { appendFileSync(log, JSON.stringify({ time: new Date().toISOString(), ...entry }) + '\n'); } catch { /* diagnostics only */ }
  };
  ctx.on('tools/pre-execute', async (execution, next) => {
    const plan = classify(execution, root, definitionOf);
    // c123 (batch design WP3 3.2): every line has the same keys and names the session's workspace, or for a gate verdict
    // the folder the gate judged the call from (a one-shot shell's workdir); the guard's own denial ran no gate, so its
    // status is null.
    const header = execution.agent?.session?.header;
    if (plan.kind === 'deny') {
      record({ tool: execution.name, session: header?.id ?? null, cwd: header?.cwd ?? null, status: null, allowed: false, reason: plan.reason });
      return { kind: 'deny', reason: plan.reason };
    }
    if (plan.kind === 'gate') {
      const verdict = await runGate(settings, plan.payload, execution.signal);
      record({ tool: execution.name, session: plan.payload.session_id, cwd: plan.payload.cwd, status: verdict.status ?? null, allowed: verdict.allowed, reason: verdict.reason });
      if (!verdict.allowed) return { kind: 'deny', reason: verdict.reason };
      approvals.set(execution.callId, JSON.stringify(execution.arguments ?? {}));
    }
    return next();
  });
  ctx.tools.guard((execution) => {
    // c123 (owner decision C1): whether a shell's workdir is judged depends on its definition, so the backstop resolves
    // the definition as the pre-execute stage does and reaches the same verdict.
    const plan = classify(execution, root, definitionOf);
    if (plan.kind === 'deny') return plan.reason;
    if (plan.kind === 'gate') {
      const approved = approvals.get(execution.callId);
      approvals.delete(execution.callId);
      if (approved === undefined) return 'GroundTruth KB guard: the effect was not checked by the effect gate';
      if (approved !== JSON.stringify(execution.arguments ?? {})) return 'GroundTruth KB guard: the arguments changed after the effect gate approved them';
    }
    return undefined;
  });
  process.stderr.write('gtkb-home-effect-guard active\n');
}
