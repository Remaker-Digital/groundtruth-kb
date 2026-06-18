NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Suppress non-activatable GO from Prime Builder actionable scans (deterministic activatability diagnostic)

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4618

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

## Summary

WI-4618 (P2, defect, component `bridge-dispatch`). Live Prime Builder actionable
scans keep surfacing a latest-`GO` (the concrete case:
`gtkb-bridge-index-retirement-cleanout`) as implementable, even though
`scripts/implementation_authorization.py begin --bridge-id <id> --no-write`
fails closed — the implementation-start packet cannot be created (missing
parser-recognized Specification Links, a project-authorization/project mismatch,
and missing `## Requirement Sufficiency`). PB automation and interactive sessions
therefore repeatedly select work that cannot legally start.

This proposal adds a deterministic, read-only activatability check to the PB
actionable scan: for each latest-`GO` that would otherwise be Prime-actionable,
the scan validates whether an implementation-start packet *could* be created
(validate-only, no write). A `GO` that fails this check is moved out of the
implementable list into a clearly-labeled "blocked (non-activatable)" diagnostic
bucket, with the begin-gate failure reasons. PB scans no longer present an
un-startable `GO` as implementable.

## Problem

`begin` fails closed for `gtkb-bridge-index-retirement-cleanout` for three
independent reasons (missing recognized Specification Links; the cited
`PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI` does
not match the proposal's project `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`;
missing `## Requirement Sufficiency`). The implementation-start gate correctly
refuses to create a packet — no illegal implementation happens — but the PB
actionable scan still lists the `GO` as implementable, so each PB session/scan
re-selects the same dead-end. The missing piece is a scan-time signal that the
`GO` is non-activatable.

## Proposed fix (scan-layer activatability diagnostic; headless core untouched)

In `.claude/skills/bridge/helpers/scan_bridge.py` (the canonical PB actionable
scan surface), add a deterministic predicate and wire it into the
Prime-Builder result:

1. New predicate `_go_activatable(project_root, bridge_id) -> tuple[bool, list[str]]`:
   calls `implementation_authorization.create_authorization_packet(project_root,
   bridge_id)` inside `try/except AuthorizationError`. On success returns
   `(True, [])`; on `AuthorizationError` returns `(False, reasons)` where
   `reasons` is the gate's accumulated `"; "`-joined message split back into a
   list. This reuses the EXACT validation the begin gate runs (the gate raises
   the aggregated errors at `implementation_authorization.py:973-974`) and is
   write-free: `create_authorization_packet` only builds + validates the packet;
   `write_packet` (the persisting step) is never called.
2. For each latest-`GO` thread that is already Prime-actionable and NOT
   dispatch-terminal (the existing `_is_dispatch_terminal_go` filter is applied
   first, unchanged), evaluate `_go_activatable`. A `GO` that is non-activatable
   is removed from the implementable `GO` list and placed in a new
   `blocked_non_activatable` result bucket carrying `{bridge_id, go_file,
   reasons}`.
3. The markdown and JSON scan outputs gain a clearly-labeled
   "Blocked (non-activatable GO)" section listing each suppressed `GO` and its
   begin-gate reasons, so the diagnostic is visible (not silently dropped).

**Explicit non-goal (scope boundary).** This slice does NOT modify the
headless-dispatch core (`groundtruth_kb.bridge.notify._derive_dispatchable` /
`compute_actionable_pending`). The headless dispatcher already fails closed at
`begin` time (no illegal implementation occurs), and its dispatch is bounded by
actionable-signature stability. The WI's surfaced symptom is specifically that
"Live PB scans keep surfacing" the dead-end `GO`; the scan-layer diagnostic
addresses that symptom directly with minimal blast radius. Headless-dispatch
suppression (touching `_derive_dispatchable`) is intentionally deferred as a
separate, higher-risk change if later required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge protocol's GO/actionability
  model; this corrects how a non-activatable GO is presented to Prime Builder.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the
  implementation-start gate is the write-time enforcement layer; this adds a
  review/scan-time diagnostic consistent with the two-layer model.
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start
  Authorization Metadata + § Mechanical Implementation-Start Gate — defines the
  packet-creation validation this predicate reuses.
- `.claude/rules/codex-review-gate.md` — Prime acts only on actionable GO/NO-GO;
  a non-activatable GO must not be presented as implementable.
- `.claude/rules/project-root-boundary.md` — both target paths are in-root.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- Deliberation search (`gt deliberations search "suppress non-activatable GO
  prime scan implementation-start packet cannot be created"`) returned no
  on-topic prior decision; the nearest matches (DELIB-2287, DELIB-20261502,
  DELIB-20261537) concern unrelated topics (W4 enforcement calibration, CLAUDE.md
  scope clarification, work-intent registry integration).
- In-code context: the implementation-start gate and `create_authorization_packet`
  validation are the VERIFIED machinery this predicate reuses (the
  `gtkb-impl-auth-*` thread family, e.g.
  `bridge/gtkb-impl-auth-verification-heading-gate-alignment-004.md`). The
  existing `scan_bridge.py` already suppresses dispatch-terminal GOs via
  `_is_dispatch_terminal_go`; this proposal adds a complementary
  non-activatable-GO suppression at the same scan layer, matching that
  established pattern.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1063` — seed=search; lo_review; Codex Poller Visibility Session Wrap
- DA: `DELIB-1198` — seed=search; bridge_thread; Bridge thread: gtkb-hook-scanner-safe-writer (12 versions, ORPHAN)
- DA: `DELIB-0736` — seed=search; bridge_thread; Bridge thread: gtkb-hook-scanner-safe-writer (12 versions, VERIFIED)
- DA: `DELIB-20263896` — seed=search; bridge_thread; Loyal Opposition Review - Claude AXIS 2 UserPromptSubmit Bridge Surface REVISED-
- DA: `DELIB-20262539` — seed=search; owner_conversation; Where should the GTKB-WRAPUP-ENHANCEMENTS work item live relative to the existin

## Requirement Sufficiency

Existing requirements are sufficient. WI-4618 prescribes the behavior ("PB
actionable scans do not present a GO as implementable when the
implementation-start packet cannot be created"), and the implementation-start
gate (`.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start
Gate) already defines packet-creation validation as the authoritative
activatability predicate. No new or revised requirement is needed before
implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — each clause maps to a test in
`platform_tests/scripts/test_scan_bridge.py`:

- Non-activatable GO is suppressed (WI symptom):
  `test_non_activatable_go_moved_to_blocked_bucket` builds a fixture bridge
  thread with a latest GO whose proposal is missing recognized Specification
  Links / Requirement Sufficiency, runs the PB scan, and asserts the GO is
  absent from the implementable GO list and present in `blocked_non_activatable`
  with non-empty reasons.
- Activatable GO is preserved (no false suppression):
  `test_activatable_go_remains_actionable` builds a fixture thread with a GO
  whose proposal passes packet validation and asserts the GO stays in the
  implementable list and is NOT in the blocked bucket.
- Reason fidelity: `test_blocked_go_carries_begin_gate_reasons` asserts the
  recorded reasons match the `AuthorizationError` message the begin gate raises
  (e.g., missing spec links / requirement sufficiency).
- Dispatch-terminal precedence unchanged:
  `test_dispatch_terminal_go_still_filtered_before_activatability` asserts a
  dispatch-terminal GO is filtered by the existing `_is_dispatch_terminal_go`
  path and never reaches the activatability check.
- NO-GO / ADVISORY unaffected:
  `test_nogo_and_advisory_actionability_unchanged` asserts the activatability
  check applies only to GO entries and leaves NO-GO/ADVISORY Prime
  actionability unchanged.

Commands (resolved against the GT-KB venv interpreter, which carries `ruff`):

    .venv/Scripts/python.exe -m pytest platform_tests/scripts/test_scan_bridge.py -q
    .venv/Scripts/python.exe -m ruff check .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
    .venv/Scripts/python.exe -m ruff format --check .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py

Expected: all tests pass; `ruff check` and `ruff format --check` clean on both
changed files.

## Acceptance Criteria

1. A latest-`GO` whose implementation-start packet cannot be created is removed
   from the PB scan's implementable GO list and surfaced in a labeled
   "blocked (non-activatable)" bucket with the begin-gate reasons.
2. An activatable `GO` is unaffected and remains implementable.
3. The existing dispatch-terminal GO filter runs first and is unchanged.
4. The headless-dispatch core (`notify._derive_dispatchable`) is NOT modified.
5. The activatability check is read-only (validate-only; no packet is written,
   no bridge/MemBase/git mutation).
6. `ruff check` and `ruff format --check` clean on both changed files.

## Risk and Rollback

- Risk: LOW–MEDIUM. The change is additive at the PB scan surface and read-only
  (reuses validate-only `create_authorization_packet`; never calls
  `write_packet`). It does not alter headless dispatch. The main risk is a
  false suppression of an activatable GO; the
  `test_activatable_go_remains_actionable` test guards that, and the predicate
  uses the exact begin-gate validation so its verdict matches `begin` itself.
- Performance: bounded — the check runs once per latest-`GO` Prime-actionable
  thread (a small set), and only after the cheaper dispatch-terminal filter.
- Blast radius: two files (`scan_bridge.py` + its test). No change to
  `implementation_authorization.py`, `notify.py`, hooks, or dispatch state.
- Rollback: revert the two-file diff; the scan returns to listing all
  non-terminal GOs as implementable. No state or schema change.

## Owner Decisions / Input

None required. Implementation authority derives from the active,
owner-decision-backed project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`). WI-4618 is an
unimplemented work item in PROJECT-GTKB-MAY29-HYGIENE, and the WI text prescribes
the behavior. No AskUserQuestion decision is needed.

## Recommended Commit Type

`fix:` — repairs a defect (PB scans presenting un-startable GOs as implementable)
with no new user-facing capability surface.
