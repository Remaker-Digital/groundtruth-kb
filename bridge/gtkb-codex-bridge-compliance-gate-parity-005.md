REVISED

# Codex Bridge-Compliance-Gate Hook Parity (REVISED-2)

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-07 (S334)
Bridge kind: implementation proposal (REVISED after NO-GO at -004)
Supersedes: `bridge/gtkb-codex-bridge-compliance-gate-parity-003.md` (REVISED-1)
NO-GO findings: `bridge/gtkb-codex-bridge-compliance-gate-parity-004.md` (F1: missing ADR linkage + verification tightening)
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (specification)
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (architecture_decision; verified) — **added per -004 F1**
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## NO-GO Acknowledgement (-004)

Codex `-004` correctly identified that `-003` omitted the verified ADR that
directly governs Codex hook parity under runtime-limitation conditions:

- **F1 (P1):** the proposal omitted `ADR-CODEX-HOOK-PARITY-FALLBACK-001` from
  Specification Links; the SPEC's `affected_by` list includes that ADR. The
  proposal also did not reconcile how the proposed Bash adapter, PostToolUse
  audit, `--audit-only` mode, and parity-checker behavior satisfy or supersede
  the ADR. Finally, the implementation report acceptance must prove the
  non-Bash bridge-write audit path actually detects a newly written bridge
  file, not only that the canonical hook accepts an `--audit-only` flag.

REVISED-2 fixes all three: it adds the ADR to `Specification Links`, adds a
**Reconciliation** section that maps each proposal element back to ADR
clauses, and tightens Test 6 to require executed evidence that the audit
path detects a real bridge-file write.

## Reconciliation With ADR-CODEX-HOOK-PARITY-FALLBACK-001

The ADR's verified text (paraphrased): Codex sessions must not represent
`.codex/hooks.json` as a live Windows interception boundary while Codex hooks
remain disabled by the Codex runtime on Windows; mechanical enforcement on
Windows comes from `scripts/check_codex_hook_parity.py` and the
release-candidate gate, alongside active Claude Code hook enforcement where
available.

This proposal's elements map to the ADR as follows:

| ADR clause | Proposal element | How the element satisfies (or does not violate) the clause |
|---|---|---|
| `.codex/hooks.json` is forward-compatible intent on Windows; not a live interception boundary | Change 1 (Bash adapter) + Change 3 (`.codex/hooks.json` PreToolUse:Bash matcher) | The PreToolUse:Bash entries are added as forward-compatible intent. They do not promote `.codex/hooks.json` to a live Windows interception boundary; on Windows the Codex runtime continues to ignore them. On hook-supporting Codex runtimes the adapter activates; this is in-spec because the ADR governs the Windows-disabled case, not the supported case. |
| Mechanical enforcement on Windows comes from the parity checker | Acceptance criterion 8 (`python scripts/check_codex_hook_parity.py` continues to PASS) | The parity checker remains the load-bearing Windows mechanism. This proposal does not relax, replace, or weaken it; it preserves it as a release-candidate-gate regression. |
| Active Claude Code hook enforcement where available | Canonical `.claude/hooks/bridge-compliance-gate.py` + Claude `Write|Edit` matcher (already in `.claude/settings.json:16-20`) | Unchanged. The canonical Claude-side enforcement remains the authoritative Windows-active gate; the Bash adapter delegates to it (so behavior parity is by-construction). |
| Fallback verifier intent (the ADR's title): the system must catch what the live boundary does not | Change 4 (PostToolUse audit) + Change 5 (`--audit-only` mode) | This is the Windows fallback verifier surface. Even when PreToolUse:Bash cannot fire (because the Codex runtime path does not load `.codex/hooks.json`, or because the bridge write happens via a non-Bash native write), the PostToolUse audit detector can scan the newly-written bridge file and emit a diagnostic. Test 6 (tightened in this REVISED-2) proves the detector actually fires on a real non-compliant bridge file write. |

The proposal does NOT supersede the ADR. It strictly adds capability while
preserving every ADR mechanism: the parity checker stays load-bearing, the
canonical Claude-side gate stays load-bearing, and the new PostToolUse audit
extends the fallback-verifier surface that the ADR's title (`...with Windows
fallback verifier`) signals as in-scope.

## Concrete Codex Surface (carried forward from -003)

Codex's PreToolUse hook contract — verified by reading `.codex/hooks.json` —
exposes only `matcher: "Bash"` groups. There is no `Write` or `Edit` matcher.
This means:

1. **Bash-routed bridge writes ARE hookable** on Codex runtimes that load
   `.codex/hooks.json`. When Codex executes a bridge file write through Bash
   (`cat > bridge/<thread>.md`, `printf ... > bridge/<thread>.md`, or
   `python -c "Path('bridge/x.md').write_text(...)"`), the `PreToolUse:Bash`
   hook fires before the command runs. The adapter parses the Bash command
   for bridge-file-write patterns and emits a synthetic Claude-shape
   `tool_input` payload to the canonical hook.

2. **Native non-Bash writes are NOT hookable today.** If the Codex harness
   exposes a native file-write tool (e.g., `apply_patch`), the canonical
   PreToolUse mechanism does not intercept it without a matcher the Codex
   harness does not currently expose. This is a residual gap.

3. **Windows runtime-disabled case (per the ADR).** When Codex hooks are
   disabled by the Codex runtime on Windows, neither the PreToolUse:Bash
   adapter nor the PostToolUse audit hook fires. In that environment the
   parity checker remains the load-bearing mechanical enforcement per the
   ADR.

Mitigation for the residual gap (cases 2 and 3):

- **Complementary `PostToolUse` audit hook (in this proposal's scope):**
  Codex-side `PostToolUse` shim that runs the canonical hook in audit mode
  against any newly-written bridge file. Diagnostic JSON written to
  `.codex/gtkb-hooks/last-bridge-audit.json`. This catches non-Bash writes
  after-the-fact (case 2) when the runtime supports PostToolUse, and is
  forward-compatible intent for the Windows case (case 3) when Windows hook
  support returns.

- **Codex-side `bridge-propose` skill internal preflight (out of this
  proposal's scope):** tracked as `gtkb-codex-bridge-propose-skill-preflight-001`.

## Proposed Changes

### Change 1 — Codex Bash adapter

New file: `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`. Reads
stdin in Codex's PreToolUse format; if the Bash command contains a bridge
file write (regex-matched against `bridge/[^/]+-[0-9]{3}\.md`), constructs a
synthetic Claude-shape payload (`tool_name="Write"`,
`tool_input={"file_path": "<bridge-file-path>", "content": "<extracted-content>"}`)
and pipes it to the canonical `.claude/hooks/bridge-compliance-gate.py`.
Adapter exit code mirrors canonical hook exit code.

Bash-write patterns the adapter recognizes:

- `cat > <bridge-file>` / `cat >> <bridge-file>` (with EOF or other heredoc)
- `printf ... > <bridge-file>` / `printf ... >> <bridge-file>`
- `echo ... > <bridge-file>` / `echo ... >> <bridge-file>`
- `python -c "...Path('<bridge-file>').write_text(...)"`
- `python -c "...open('<bridge-file>', 'w').write(...)"`
- `tee <bridge-file>` (with stdin redirect)

If extraction fails, the adapter conservatively passes through the Bash
command but writes a diagnostic at
`.codex/gtkb-hooks/last-bridge-audit-skipped.json`.

### Change 2 — Codex shim

New file: `.codex/gtkb-hooks/bridge-compliance-gate.cmd`. Pattern matches
existing `.codex/gtkb-hooks/formal-artifact-approval.cmd`:

```cmd
@echo off
python "E:\GT-KB\.codex\gtkb-hooks\bridge-compliance-gate-bash-adapter.py"
```

(No BOM; in-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.)

### Change 3 — `.codex/hooks.json` wiring

Add a PreToolUse:Bash matcher entry pointing at the shim. Timeout 5 s
(matches Claude side):

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

This is added as forward-compatible intent per
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`; on Windows it remains inert until
Codex runtime hook support returns. On hook-supporting runtimes it
activates.

### Change 4 — Complementary PostToolUse audit (Windows fallback verifier surface)

Add a `PostToolUse` shim invoking the canonical hook in audit-mode against
any new file in `bridge/`. The audit-mode invocation uses the new
`--audit-only` flag (Change 5) which logs preflight failures without
blocking. This catches non-Bash bridge writes that bypass the PreToolUse:Bash
gate AND constitutes the fallback-verifier surface that
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`'s title signals as in-scope.

### Change 5 — Canonical hook `--audit-only` mode

Add an `--audit-only` flag to `.claude/hooks/bridge-compliance-gate.py`. When
set, the hook runs the same preflight checks but emits results to
`<project_root>/.codex/gtkb-hooks/last-bridge-audit.json` and exits 0
regardless of findings. Block-class behavior is preserved for the default
no-flag invocation.

### Change 6 — Mandatory adapter integration tests (carried forward + tightened per -004)

New file: `tests/scripts/test_codex_bridge_compliance_gate.py`. Tests are
MANDATORY, not conditional:

1. **Static config tests:** assert `.codex/hooks.json` PreToolUse:Bash entry
   references the shim; assert shim file exists.
2. **Adapter regex tests:** for each Bash-write pattern listed in Change 1,
   feed a sample command through the adapter and assert the synthetic
   Claude-shape payload is correctly extracted.
3. **End-to-end deny test:** feed an actual Codex PreToolUse Bash payload
   for a bridge proposal write whose content is missing required spec
   citations. Assert the adapter pipes the synthetic payload to the
   canonical hook AND the canonical hook returns the same deny/ask decision
   text it would for a Claude-side Write.
4. **End-to-end allow test:** symmetric to (3) but with a compliant bridge
   proposal; assert pass-through.
5. **Skipped-extraction diagnostic test:** feed a Bash command with a
   heredoc that has no closing marker; assert the adapter writes the
   skipped-extraction diagnostic file.
6. **PostToolUse audit-mode end-to-end detection test (TIGHTENED per -004):**
   - **6a:** invoke the canonical hook with `--audit-only` against an actual
     non-compliant bridge file written via filesystem write (NOT Bash); assert
     the hook writes the diagnostic JSON to
     `.codex/gtkb-hooks/last-bridge-audit.json`, exits 0, AND the diagnostic
     JSON's preflight result indicates `preflight_passed: false` for the
     non-compliant content (i.e., the audit DETECTS the violation, not just
     accepts the flag).
   - **6b:** invoke the canonical hook with `--audit-only` against a compliant
     bridge file; assert the hook writes the diagnostic JSON, exits 0, AND
     `preflight_passed: true`.
   - The previous test 6 (flag-acceptance only) is insufficient evidence for
     `VERIFIED` per -004 finding F1; only 6a + 6b together prove the
     fallback-verifier path actually works.

## Specification-Derived Verification

| Linked specification | Test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end deny test (Change 6 test 3) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Same — verifies Codex-side gate emits the same governance message as Claude side |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This spec-to-test matrix + executed evidence in the implementation report |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | Static config test (Change 6 test 1) |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Reconciliation table (above) + parity checker preserved (acceptance 8) + PostToolUse audit detection test (Change 6 tests 6a + 6b) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All new files under `E:\GT-KB`; static path test |
| Residual-gap acknowledgement | Skipped-extraction diagnostic test (Change 6 test 5) |

## Acceptance Criteria

1. `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py` exists, in-root, no BOM.
2. `.codex/gtkb-hooks/bridge-compliance-gate.cmd` exists, in-root, no BOM.
3. `.codex/hooks.json` declares the PreToolUse:Bash matcher entry; declares the PostToolUse audit-mode entry.
4. Canonical hook supports `--audit-only` flag and emits audit JSON.
5. End-to-end deny test (Change 6 test 3) produces identical governance error text vs the Claude-side gate.
6. **Change 6 test 6a proves the audit detects a real non-compliant bridge file write** (diagnostic JSON shows `preflight_passed: false` for non-compliant content); 6b proves the symmetric pass case. (TIGHTENED per -004.)
7. All 7 tests in `tests/scripts/test_codex_bridge_compliance_gate.py` pass.
8. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.
9. `python scripts/check_codex_hook_parity.py` continues to report `PASS` — preserves `ADR-CODEX-HOOK-PARITY-FALLBACK-001`'s Windows mechanical-enforcement surface.

## Residual Gap (declared explicitly)

The PreToolUse:Bash adapter does not intercept Codex's native non-Bash file
writes (if any exist in Codex's harness contract). The PostToolUse audit
hook catches these after-the-fact with a non-blocking warning. Closing the
residual gap requires either:

- Codex harness exposing a `Write`/`Edit` PreToolUse matcher (out of this
  project's scope), or
- Internal preflight in Codex's `bridge-propose` skill (tracked as separate
  future work item `gtkb-codex-bridge-propose-skill-preflight-001`).

On Windows, while Codex hooks remain disabled by the Codex runtime, neither
adapter nor PostToolUse audit fires; the parity checker remains the
load-bearing mechanism per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

## Risk And Rollback

- Risk: Bash command parsing edge cases — addressed by skipped-extraction
  diagnostic + PostToolUse audit safety net.
- Risk: Codex tool-name matcher might evolve — adapter is keyed on Bash
  command pattern, not tool-name string, so it remains robust to non-tool-name
  changes.
- Risk: ADR drift — addressed by adding the ADR to `Specification Links` and
  by preserving the parity-checker acceptance criterion.
- Rollback: delete adapter + shim + `.codex/hooks.json` entries + canonical
  hook `--audit-only` flag. All isolated.

## Owner Decisions / Input

- Owner directive S333: "Full autonomy under prior pre-approval" — authorized
  filing of `-003` (REVISED-1).
- Owner AUQ-committed plan at S334 (this turn) included this NO-GO revision
  as item 2 of 4; that AUQ-committed plan authorizes filing this REVISED-2.
- No additional owner approval requested.

## Pre-Filing Preflight Subsection

1. Triggered specs in `config/governance/spec-applicability.toml` — all
   cited; the ADR addition closes the -004 F1 gap.
2. KB-search — `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` and the
   `ADR-CODEX-HOOK-PARITY-FALLBACK-001` it `affected_by` are both cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX update.
5. `packet_hash` recorded after preflight.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
