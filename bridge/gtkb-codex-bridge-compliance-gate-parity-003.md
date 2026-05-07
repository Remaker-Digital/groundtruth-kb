REVISED

# Codex Bridge-Compliance-Gate Hook Parity (REVISED-1)

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal (REVISED after NO-GO)
Supersedes: `bridge/gtkb-codex-bridge-compliance-gate-parity-001.md` (NEW)
NO-GO findings: `bridge/gtkb-codex-bridge-compliance-gate-parity-002.md` (F1 + F2)
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (specification)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## NO-GO Acknowledgement

Codex `-002` correctly identified two structural gaps in `-001`:

- **F1 (P1):** the proposal didn't define the actual Codex write-hook surface; the canonical hook checks `tool_name in {"Write", "Edit"}` while Codex's `.codex/hooks.json` only exposes `PreToolUse:Bash` matcher.
- **F2 (P2):** adapter testing was conditional rather than mandatory.

Both are addressed in this REVISED-1 by (a) defining the concrete Codex surface and adapter contract upfront, (b) acknowledging the residual gap honestly, and (c) making adapter integration testing the central acceptance criterion.

## Concrete Codex Surface (F1 fix)

Codex's PreToolUse hook contract — verified by reading `.codex/hooks.json` — exposes only `matcher: "Bash"` groups. There is no `Write` or `Edit` matcher. This means:

1. **Bash-routed bridge writes ARE hookable.** When Codex executes a bridge file write through Bash (e.g., `cat > bridge/<thread>.md`, `printf ... > bridge/<thread>.md`, or `python -c "Path('bridge/x.md').write_text(...)"`), the `PreToolUse:Bash` hook fires before the command runs. An adapter can parse the Bash command for bridge-file-write patterns and emit a synthetic Claude-shape `tool_input` payload to the canonical hook.

2. **Native non-Bash writes are NOT hookable today.** If Codex's harness exposes a native file-write tool (e.g., `apply_patch`), the canonical PreToolUse mechanism doesn't intercept it without an additional matcher Codex's harness doesn't currently expose. This is a residual gap, declared explicitly here.

Mitigation for the residual gap:

- **Complementary `PostToolUse` audit hook (in this proposal's scope):** add a Codex-side `PostToolUse` shim that runs the canonical hook in audit mode against any newly-written bridge file. If preflight fails, the audit hook emits a non-blocking warning to stderr and writes a diagnostic file at `.codex/gtkb-hooks/last-bridge-audit.json`. This catches non-Bash writes after-the-fact rather than blocking them, but ensures no Codex-as-Prime bridge write goes unscanned.
- **Codex-side `bridge-propose` skill internal preflight (out of this proposal's scope; tracked as separate item):** Codex's existing `bridge-propose` skill can call the canonical hook's logic directly before emitting Bash commands. That's the cleanest fix for the native-write gap; tracked as `gtkb-codex-bridge-propose-skill-preflight-001` (NOT filed in this proposal — explicitly future work).

## Proposed Changes

### Change 1 — Codex Bash adapter

New file: `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`. Reads stdin in Codex's PreToolUse format; if the Bash command contains a bridge file write (regex-matched against `bridge/[^/]+-[0-9]{3}\.md`), constructs a synthetic Claude-shape payload (`tool_name="Write"`, `tool_input={"file_path": "<bridge-file-path>", "content": "<extracted-content>"}`) and pipes it to the canonical `.claude/hooks/bridge-compliance-gate.py`. Adapter exit code mirrors canonical hook exit code (deny → block, ask → block-pending-confirmation, pass → allow).

Bash-write patterns the adapter recognizes:

- `cat > <bridge-file>` / `cat >> <bridge-file>` (with EOF or other heredoc)
- `printf ... > <bridge-file>` / `printf ... >> <bridge-file>`
- `echo ... > <bridge-file>` / `echo ... >> <bridge-file>`
- `python -c "...Path('<bridge-file>').write_text(...)"`
- `python -c "...open('<bridge-file>', 'w').write(...)"`
- `tee <bridge-file>` (with stdin redirect)

If extraction fails (e.g., heredoc without closing marker, dynamic shell expansion), the adapter conservatively passes through the Bash command but writes a diagnostic file at `.codex/gtkb-hooks/last-bridge-audit-skipped.json` so the residual gap is auditable.

### Change 2 — Codex shim

New file: `.codex/gtkb-hooks/bridge-compliance-gate.cmd`. Pattern matches existing `.codex/gtkb-hooks/formal-artifact-approval.cmd`:

```cmd
@echo off
python "E:\GT-KB\.codex\gtkb-hooks\bridge-compliance-gate-bash-adapter.py"
```

(No BOM; in-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.)

### Change 3 — `.codex/hooks.json` wiring

Add a PreToolUse:Bash matcher entry pointing at the shim. Timeout 5 s (matches Claude side):

```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "cmd /d /s /c E:\\GT-KB\\.codex\\gtkb-hooks\\bridge-compliance-gate.cmd",
      "statusMessage": "Checking bridge compliance",
      "timeout": 5
    }
  ]
}
```

### Change 4 — Complementary PostToolUse audit

Add a `PostToolUse` shim invoking the canonical hook in audit-mode against any new file in `bridge/`. The audit-mode invocation uses a new `--audit-only` flag on the canonical hook (Change 5) which logs preflight failures without blocking. This catches non-Bash bridge writes that bypass the PreToolUse:Bash gate.

### Change 5 — Canonical hook `--audit-only` mode

Add an `--audit-only` flag to `.claude/hooks/bridge-compliance-gate.py`. When set, the hook runs the same preflight checks but emits results to `<project_root>/.codex/gtkb-hooks/last-bridge-audit.json` and exits 0 regardless of findings. Block-class behavior is preserved for the default no-flag invocation.

### Change 6 — Mandatory adapter integration tests (F2 fix)

New file: `tests/scripts/test_codex_bridge_compliance_gate.py`. Tests are MANDATORY, not conditional:

1. **Static config tests:** assert `.codex/hooks.json` PreToolUse:Bash entry references the shim; assert shim file exists.
2. **Adapter regex tests:** for each Bash-write pattern listed in Change 1, feed a sample command through the adapter and assert the synthetic Claude-shape payload is correctly extracted.
3. **End-to-end deny test (the test F2 specifically demanded):** feed an actual Codex PreToolUse Bash payload for a bridge proposal write whose content is missing required spec citations. Assert the adapter pipes the synthetic payload to the canonical hook AND the canonical hook returns the same deny/ask decision text it would for a Claude-side Write.
4. **End-to-end allow test:** symmetric to (3) but with a compliant bridge proposal; assert pass-through.
5. **Skipped-extraction diagnostic test:** feed a Bash command with a heredoc that has no closing marker; assert the adapter writes the skipped-extraction diagnostic file.
6. **PostToolUse audit-mode test:** invoke the canonical hook with `--audit-only`; assert it writes the audit JSON and exits 0 regardless of preflight result.

## Specification-Derived Verification

| Linked specification | Test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end deny test (Change 6 test 3) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Same — verifies the Codex-side gate emits the same governance message as Claude side |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | Static config test (Change 6 test 1) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All new files under `E:\GT-KB`; static path test |
| Residual-gap acknowledgement | Skipped-extraction diagnostic test (Change 6 test 5) |
| PostToolUse audit | Change 6 test 6 |

## Acceptance Criteria

1. `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py` exists, in-root, no BOM.
2. `.codex/gtkb-hooks/bridge-compliance-gate.cmd` exists, in-root, no BOM.
3. `.codex/hooks.json` declares the PreToolUse:Bash matcher entry; declares the PostToolUse audit-mode entry.
4. Canonical hook supports `--audit-only` flag and emits audit JSON.
5. End-to-end deny test produces identical governance error text vs the Claude-side gate.
6. All 6 tests in `tests/scripts/test_codex_bridge_compliance_gate.py` pass.
7. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.
8. `python scripts/check_codex_hook_parity.py` continues to report `PASS`.

## Residual Gap (declared explicitly)

The PreToolUse:Bash adapter does not intercept Codex's native non-Bash file writes (if any exist in Codex's harness contract). The PostToolUse audit hook catches these after-the-fact with a non-blocking warning. Closing the residual gap requires either:

- Codex harness exposing a `Write`/`Edit` PreToolUse matcher (out of this project's scope), or
- Internal preflight in Codex's `bridge-propose` skill (tracked as separate future work item `gtkb-codex-bridge-propose-skill-preflight-001`).

## Risk And Rollback

- Risk: Bash command parsing edge cases (dynamic expansion, shell quoting) — addressed by skipped-extraction diagnostic + PostToolUse audit safety net.
- Risk: Codex tool-name matcher might evolve — adapter is keyed on Bash command pattern, not tool-name string, so it remains robust to non-tool-name changes.
- Rollback: delete adapter + shim + `.codex/hooks.json` entries + canonical hook `--audit-only` flag. All isolated.

## Owner Decisions / Input

- Owner directive S333: "Full autonomy under prior pre-approval" — authorizes filing this REVISED-1.
- Prior owner directive S333: "do not defer anything; max quality" — the residual gap is declared rather than ignored, consistent with quality goal.
- No additional owner approval requested.

## Pre-Filing Preflight Subsection

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited.
2. KB-search — `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX update.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
