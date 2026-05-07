NEW

# Codex Bridge-Compliance-Gate Hook Parity Implementation Proposal

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking) — bridge-mediated work honors file bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking) — proposals must cite governing specs; the gate hook mechanically enforces this contract.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking) — verification derived from linked specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking) — new files live under `E:\GT-KB`.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (specification) — Codex harness governance parity baseline.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol that the gate enforces.
- `.claude/rules/codex-review-gate.md` — counterpart review gate.
- `.claude/rules/project-root-boundary.md` — root boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Claim

The bridge-compliance-gate hook (`.claude/hooks/bridge-compliance-gate.py`)
is currently wired only into `.claude/settings.json` as PreToolUse for
Write|Edit. `.codex/hooks.json` has no equivalent gate. As a result, every
bridge proposal Codex files goes through Codex's Write equivalent without
the mechanical applicability-preflight gate firing.

This is a **structural parity defect** that produced multiple downstream
findings during the S333 audit:

- `gtkb-harness-parity-baseline-001` (Codex-as-Prime filing) had a preflight
  failure that Codex (now LO) caught at review time only because the gate
  did not fire at Write time.
- `gtkb-bridge-propose-helper-caller-migration-2026-05-02` and
  `gtkb-bridge-propose-helper-index-parity-2026-05-02` similarly have
  preflight failures with no Write-time gate intervention.
- ISOLATION-017 Slices 4-8 reached VERIFIED with operative-file preflight
  failures that pre-date the gate hook on the Claude side and never had a
  gate on the Codex side.

This proposal closes the gap by adding a Codex-side shim that invokes the
existing canonical Python hook, wired through `.codex/hooks.json` as a
PreToolUse matcher on Codex's file-write tool.

## Proposed Changes

### Change 1 — Codex shim invoking the canonical hook

New file: `.codex/gtkb-hooks/bridge-compliance-gate.cmd`. Pattern matches
the existing Codex `.cmd` shims (e.g.,
`.codex/gtkb-hooks/formal-artifact-approval.cmd`), which invoke the
canonical Python hook at `.claude/hooks/<name>.py`. This avoids
duplicating ~500 lines of Python and keeps a single canonical
implementation.

Shim contents:

```cmd
@echo off
python "E:\GT-KB\.claude\hooks\bridge-compliance-gate.py"
```

(No BOM. Mirrors the formal-artifact-approval shim's pattern.)

### Change 2 — `.codex/hooks.json` wiring

Add a PreToolUse matcher entry pointing at the shim. The exact tool name
that triggers the matcher depends on Codex's tool contract for file writes
(equivalent of Claude's `Write|Edit`). Loyal Opposition review should
confirm the Codex-side matcher token; the proposal scopes the wiring to
"whatever Codex tool emits file-write/file-edit operations comparable to
Claude's `Write` and `Edit`," and binds the timeout to the same `5` s
ceiling the Claude side already uses.

Suggested wiring (subject to LO confirmation of matcher token):

```json
{
  "matcher": "<Codex-write-tool-token>",
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

If Codex's hook contract does NOT expose tool input via stdin in the same
shape Claude does (the canonical hook reads `tool_name` and `tool_input`
from JSON stdin), then a small adapter inside the shim converts Codex's
stdin format to the Claude shape before invoking the Python hook. The
adapter, if needed, lives at `.codex/gtkb-hooks/bridge-compliance-gate-adapter.py`
(in-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`).

### Change 3 — Tests

New file: `tests/scripts/test_codex_bridge_compliance_gate.py`.

Tests:

- Parse `.codex/hooks.json` and assert a PreToolUse entry exists pointing
  at the new shim.
- Assert `.codex/gtkb-hooks/bridge-compliance-gate.cmd` exists and resolves
  under `E:\GT-KB`.
- Adapter integration test (if adapter is added): feed a sample Codex-shape
  stdin payload through the shim and assert the canonical Python hook
  produces the expected ask/deny output.

The existing canonical hook already has its own tests at
`tests/scripts/test_bridge_compliance_gate_hard_block_workspace.py`; this
proposal does not modify them.

## Specification-Derived Verification

Spec-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Codex-side gate fires on bridge file write attempts (integration test) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Same hook block-message text emitted by both shims |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` | `.codex/hooks.json` declares a PreToolUse entry with bridge-compliance-gate; `.claude/settings.json` and `.codex/hooks.json` both have the gate present |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All new files under `E:\GT-KB`; static path test |

## Acceptance Criteria

1. `.codex/gtkb-hooks/bridge-compliance-gate.cmd` exists, has no BOM, and resolves under `E:\GT-KB`.
2. `.codex/hooks.json` declares a PreToolUse entry invoking the shim.
3. A controlled write of a bridge proposal lacking required spec citations through Codex's harness produces the same governance error message that the Claude-side gate produces.
4. New tests pass under the GT-KB platform pytest lane.
5. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.

## Risk And Rollback

- Risk: Codex's hook tool contract may not match Claude's exactly. Mitigation: the proposal includes a fallback adapter step. Rollback: delete the shim and the `.codex/hooks.json` entry; both isolated.
- Risk: the hook fires on legitimate non-bridge writes if the matcher token is too broad. Mitigation: the canonical hook already short-circuits on non-bridge files via `_is_bridge_markdown_file()`; same protection applies.

## Owner Decisions / Input

- Owner directive S333: "I believe these are all acceptable. Do not defer anything. Our design goals are maximum quality (elegant simplicity, reliability, sustainability) and fit-for-purpose, not cost." — authorizes scope.
- Owner directive S333: "I give you pre-approval to make changes wherever required in order for you to complete this review." — authorizes filing this remediation.
- No additional owner decision requested by this proposal beyond standard Loyal Opposition `GO`/`NO-GO`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Read `config/governance/spec-applicability.toml` — triggered: `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-match on rule files), `GOV-FILE-BRIDGE-AUTHORITY-001` (always-blocking, doc:*), `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (content match), `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (content match), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory). All cited.
2. KB-search — `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` is the directly relevant Codex parity spec, cited.
3. Bridge proposal triggers always-blocking bridge-governance set — cited.
4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-bridge-compliance-gate-parity` — to be run after INDEX entry filed.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
