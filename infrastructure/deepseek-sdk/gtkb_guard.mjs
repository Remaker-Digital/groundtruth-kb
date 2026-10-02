// GT-KB native effect guard for the official DeepSeek Harness SDK runtime.
//
// Loaded as a local plugin through the launcher's patch file. Every native tool
// effect (editor create/replace/insert, PowerShell command) is checked by the
// shared GT-KB effect gate, which resolves the current binding, registered
// checkout, exact artifact claim and scratch scope through the native CLI.
// Editor views go to the same gate as reads, which refuses credential material
// (c117) and allows every other read.
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
      if (command === 'view') {
        payload = { tool_name: 'Read', tool_input: { file_path: input.arguments?.path } };
      } else if (!EDITOR_EFFECTS.has(command)) {
        return 'GT-KB guard: unknown editor effect';
      } else {
        payload = { tool_name: 'Write', tool_input: { file_path: input.arguments?.path } };
      }
    } else if (input.name === 'pwsh') {
      // c123 (owner decision A6): the sdk-minimal profile mounts this tool from
      // @deepseek-ai/dsh-tool-pwsh-persistent, whose shell keeps its working
      // directory across calls, while this guard reports a fixed cwd. The mark
      // tells the gate, which then refuses a top-level change of directory.
      payload = { tool_name: 'Bash', tool_input: { command: input.arguments?.command }, persistent_shell: true };
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
