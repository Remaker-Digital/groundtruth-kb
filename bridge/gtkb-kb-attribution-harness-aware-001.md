NEW

# KB Attribution Harness-Aware `changed_by` Implementation Proposal

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking) — touches `scripts/` paths under `E:\GT-KB`
- `GOV-HARNESS-ROLE-PORTABILITY-001` (governance) — role attaches to harness ID, not vendor name; `changed_by` attribution should reflect this contract.
- `.claude/rules/operating-model.md` §1 — "MemBase records distinguish current state from historical versions and avoid fields that encode misleading lifecycle concepts." Hardcoded attribution violates the spirit of this rule.
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `harness-state/harness-identities.json` — persistent harness identity authority.
- `harness-state/role-assignments.json` — role assignment authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Claim

KB-write helper scripts hardcode `changed_by="prime-builder/claude-code"`
regardless of which harness is currently Prime Builder. During the
Codex-as-Prime period (2026-05-03 → 2026-05-05), this caused 39 spec
mutations and 20 deliberation inserts to be attributed to Claude when
Codex was the actual operator.

Evidence inventory (greppable):

- `scripts/_archive_delib_s327_backlog_directive.py:87`
- `scripts/_archive_delib_s328_isolation_017_slice4_decisions.py:111`
- `scripts/_archive_delib_s328_isolation_017_slice5_overlay_scope.py:117`
- `scripts/_archive_delib_s328_role_intent_sentinel.py:127`
- (Plus several `.tmp/` ad-hoc scripts that should not be committed at all.)

This proposal introduces harness-aware attribution and patches the helpers.

## Proposed Changes

### Change 1 — Resolver helper

New module: `scripts/_kb_attribution.py` exposing
`resolve_changed_by(action: str = "prime-builder") -> str` which:

1. Reads `harness-state/harness-identities.json` to get the current
   harness's `harness_name`.
2. Reads `harness-state/role-assignments.json` to get the current role.
3. Returns `f"{role}/{harness_name}"`, e.g., `prime-builder/codex`.
4. Falls back to a documented default (`prime-builder/unknown`) and
   logs a warning if either identity file is unreadable; raises a
   testable exception if both are missing.

### Change 2 — Helper-script refactor

For each of the 4 archive helpers (and the KB-touching `.tmp/`
scripts, if any survive the cleanup proposal): replace the hardcoded
literal with a call to `resolve_changed_by()`. Existing tests for
those helpers (if any) updated.

### Change 3 — Historical mis-attribution capture

Insert a deliberation `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT`
documenting the historical 39+20 mis-attribution as `source_type='audit_finding'`,
`outcome='resolved'` linking to this bridge thread, the audit findings
report at `.claude/audit-2026-05-03-to-2026-05-06/99-findings-report.md`,
and the helper-script patch list. No retroactive `UPDATE` to historical KB
rows — append-only discipline is preserved.

### Change 4 — Tests

`tests/scripts/test_kb_attribution.py`:

- `resolve_changed_by()` returns the expected `f"{role}/{harness_name}"`
  for each role-mapping fixture (prime-builder Claude, prime-builder Codex,
  loyal-opposition Codex, etc.).
- Helper scripts (when invoked in dry-run mode) emit the resolved
  attribution, not a hardcoded literal.
- An integration smoke test confirms the helper fails closed when both
  identity artifacts are unreadable.

## Specification-Derived Verification

Spec-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Test |
|---|---|
| `GOV-HARNESS-ROLE-PORTABILITY-001` | `resolve_changed_by()` returns the active role + harness name pair from the role-mapping artifact |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | New module lives under `E:\GT-KB\scripts\`; static path test |
| Helper-script refactor | Greppable absence of literal `prime-builder/claude-code` in patched scripts; presence of `resolve_changed_by` calls |
| Append-only discipline | No `UPDATE` against historical rows; new DELIB row is an INSERT only |

## Acceptance Criteria

1. New `scripts/_kb_attribution.py` exists and tests pass.
2. The 4 archive helpers no longer contain the literal `prime-builder/claude-code`; they call `resolve_changed_by()`.
3. `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` is inserted with `source_type='audit_finding'`, `outcome='resolved'`, linking to the audit findings file and this bridge thread.
4. New tests pass under the GT-KB platform pytest lane.
5. `python scripts/check_harness_parity.py --all --markdown` continues to report `PASS`.

## Risk And Rollback

- Risk: helper invocation order matters if another helper imports a patched archive helper. Mitigation: archive helpers are leaf scripts not imported by others.
- Risk: identity artifacts could be missing in fresh-clone scenarios. Mitigation: fail-closed exception with documented default `prime-builder/unknown` for graceful-degradation tests.
- Rollback: revert the 4 helper script edits; delete the resolver module; remove the DELIB insert (would require a follow-on append-only entry recording the rollback).

## Owner Decisions / Input

- Owner directive S333: "I believe these are all acceptable. Do not defer anything." — authorizes scope.
- Owner directive S333: "I give you pre-approval to make changes wherever required" — authorizes filing.
- No additional owner approval requested by this proposal beyond standard Loyal Opposition `GO`/`NO-GO`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above.
2. KB-search — `GOV-HARNESS-ROLE-PORTABILITY-001` cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX entry filed.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
