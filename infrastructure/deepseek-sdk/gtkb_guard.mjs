// GT-KB native effect guard for the official DeepSeek Harness SDK runtime.
//
// Loaded as a local plugin through the launcher's patch file. Every native tool
// effect (editor create/replace/insert, PowerShell command) is checked by the
// shared GT-KB effect gate, which resolves the current binding, registered
// checkout, exact artifact claim and scratch scope through the native CLI.
// The guard is monotonic: a later allowing pre-execution listener cannot
// override a denial. Anything but a clean empty decision denies.
import { spawnSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';

export const name = 'gtkb-effect-guard';
export const inject = ['tools'];

const EDITOR_EFFECTS = new Set(['create', 'str_replace', 'insert']);

function required(variable) {
  const value = process.env[variable];
  if (!value) throw new Error(`GT-KB guard: ${variable} is not set`);
  return value;
}

export function apply(ctx) {
  const python = required('GTKB_GUARD_PYTHON');
  const gate = required('GTKB_GUARD_GATE');
  const root = required('GT_PROJECT_ROOT');
  const cwd = required('GTKB_GUARD_CWD');
  const context = required('GTKB_NATIVE_CONTEXT_ID');
  const log = process.env.GTKB_GUARD_LOG;
  ctx.tools.guard(input => {
    let payload;
    if (input.name === 'str_replace_editor') {
      const command = input.arguments?.command;
      if (command === 'view') return undefined;
      if (!EDITOR_EFFECTS.has(command)) return 'GT-KB guard: unknown editor effect';
      payload = { tool_name: 'Write', tool_input: { file_path: input.arguments?.path } };
    } else if (input.name === 'pwsh') {
      payload = { tool_name: 'Bash', tool_input: { command: input.arguments?.command } };
    } else {
      return 'GT-KB guard: unsupported native tool';
    }
    payload.cwd = cwd;
    payload.project_root = root;
    payload.session_id = context;
    const result = spawnSync(python, ['-B', gate], {
      input: JSON.stringify(payload), encoding: 'utf8', timeout: 20000, cwd: root, windowsHide: true,
      env: { ...process.env, GTKB_NATIVE_CONTEXT_ID: context, GT_PROJECT_ROOT: root },
    });
    let parsed;
    try { parsed = JSON.parse(result.stdout); } catch { parsed = undefined; }
    const allowed = result.status === 0 && parsed !== null && typeof parsed === 'object' &&
      !Array.isArray(parsed) && Object.keys(parsed).length === 0;
    const reason = allowed ? null :
      (parsed?.hookSpecificOutput?.permissionDecisionReason || result.error?.message || 'GT-KB guard: native effect check failed');
    if (log) {
      try {
        appendFileSync(log, JSON.stringify({ time: new Date().toISOString(), tool: input.name, status: result.status, allowed, reason }) + '\n');
      } catch { /* diagnostics only */ }
    }
    return allowed ? undefined : reason;
  });
}
