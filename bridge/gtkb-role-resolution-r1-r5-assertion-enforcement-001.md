NEW

bridge_kind: prime_proposal
Document: gtkb-role-resolution-r1-r5-assertion-enforcement
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC

target_paths: ["platform_tests/scripts/test_dcl_role_resolution_authority_001.py"]

# Implementation Proposal — Executable R1–R5 Enforcement for DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001

> PARKED DRAFT. Filed to disk during active multi-session INDEX contention (S436+ concurrency).
> This file is intentionally NOT yet listed in `bridge/INDEX.md`. Per the Parked-Draft Pattern
> in `.claude/rules/file-bridge-protocol.md`, an un-indexed bridge file does not enter the Loyal
> Opposition review queue and does not trigger dispatch. Promotion = add a single
> `NEW: bridge/gtkb-role-resolution-r1-r5-assertion-enforcement-001.md` line to the top of INDEX,
> with a promotion commit message tagging `gtkb-role-resolution-r1-r5-assertion-enforcement:
> parked draft promoted to NEW`. The applicability preflight will return `ERR_NO_INDEX_ENTRY`
> while parked; that is expected, not a defect.

## Summary

`DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` (v1, `specified`) formalizes the owner's
declared-not-detected role-authority model as five mandatory rules R1–R5 and lists four
"machine-checkable" assertions in its body. Those assertions are currently **prose only** — there
is no executable enforcement that fails when the role-resolution surfaces regress away from R1–R5.

This proposal adds that enforcement as a single new pytest module,
`platform_tests/scripts/test_dcl_role_resolution_authority_001.py`, mirroring the proven pattern
of `platform_tests/scripts/test_canonical_init_keyword_assertions.py` (the backing test for the
sibling `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`). The module reads the live role-resolution
source surfaces and asserts the R1–R5 invariants with a mix of behavioral tests (import + exercise
the resolver) and structural grep / grep_absent checks.

**Framing: this is a regression guard on already-conforming code, not a fix.** Investigation
confirms the code already satisfies R1–R5:
- R1/R2 — `scripts/session_role_resolution.py::resolve_interactive_session_role` resolves
  `marker > durable` (the envelope-hint-derived session marker wins; the registry is consulted only
  when the marker is absent/invalid/stale).
- R3 — `scripts/cross_harness_bridge_trigger.py` routes via `load_harness_projection()` +
  `_resolve_dispatch_target()` (registry-authoritative).
- R4 — the mismatch surface is a warning/audit (`_audit_log_misdirected_dispatch` →
  `dispatch-failures.jsonl`); doctor's role-topology check is WARN severity.
- R5 — no gate today invalidates/rejects/parks a verdict or dispatch on a registry role/status
  mismatch alone (a clean grep_absent target to be locked against future regression).

If any assertion fails on first run, that reveals a genuine conformance gap and triggers a scoped
REVISED proposal that adds the specific source fix (and its `target_paths` entry) — not a silent
scope expansion.

## Specification Links

Domain (subject + directly governing):
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` — the constraint whose R1–R5 + four declared
  assertions this proposal makes executable.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` — the decision the DCL derives from (two-layer
  authority split; declared-not-detected; the S436 harness-C over-detection this prevents).
- `DCL-SESSION-ROLE-RESOLUTION-001` — the deterministic interactive resolution table implemented by
  `scripts/session_role_resolution.py`; R1/R2 enforcement reuses/extends its existing tests.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable-vs-session-stated authority split (headless dispatch
  routing stays registry-keyed per R3).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — interactive override via the canonical init keyword.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — the proven assertion+test pattern this proposal
  mirrors (`platform_tests/scripts/test_canonical_init_keyword_assertions.py`).

Cross-cutting (applicability preflight, expected required-set on promotion):
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge path authority (`path:bridge/**`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives tests from R1–R5.

Cross-cutting (advisory):
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

How the proposed tests derive from the linked specs: each test function maps 1:1 to a rule clause
(R1–R5) of `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`, plus the DCL's four declared assertions
(envelope-hint-before-registry; dispatcher-registry-authoritative; warn-not-override; no-invalidation
grep_absent). See `## Spec-to-Test Mapping`.

## Prior Deliberations

- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` — "Role authority is owner-DECLARED
  (registry + envelope hints), not agent-DETECTED." The owner decision that produced
  `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` and `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`
  in S436. (Note: the ChromaDB semantic index has not yet ingested this fresh DELIB —
  `gt deliberations search` returned no match on three phrasings; the record was confirmed by direct
  MemBase fetch. A separate DA-index-freshness follow-up may be warranted but is out of scope here.)
- `bridge/gtkb-role-authority-declared-not-detected-004.md` (VERIFIED) — the S436 ceremony thread
  that inserted the ADR + DCL.
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (Codex GO) / `-009.md` — the exemplar
  assertion-enforcement thread whose test module structure this proposal mirrors.

## Requirement Sufficiency

Existing requirements sufficient. R1–R5 and the four machine-checkable assertions are fully and
unambiguously specified in `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` v1. No new or revised
requirement is needed before implementation; this proposal only adds executable enforcement of the
already-approved constraint.

## Implementation Design

Single new file: `platform_tests/scripts/test_dcl_role_resolution_authority_001.py`.

Path constants (resolved from `Path(__file__).resolve().parents[2]`):
- `RESOLVER_PATH = scripts/session_role_resolution.py`
- `TRIGGER_PATH = scripts/cross_harness_bridge_trigger.py`
- `CORE_PATH = scripts/session_start_dispatch_core.py`
- `DOCTOR_PATH = groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- Gate set for the R5 grep_absent sweep: `.claude/hooks/lo-file-safety-gate.py`,
  `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`,
  `scripts/session_start_dispatch_core.py`, `scripts/cross_harness_bridge_trigger.py`.

Test functions (each maps to a rule + the DCL's declared assertion):

- **R1 — `test_r1_marker_role_wins_over_mismatched_durable` (behavioral).** Import
  `resolve_interactive_session_role`; in a temp project write a marker `{role: prime-builder,
  session_id: S}` while the durable role would resolve to `loyal-opposition`; call with
  `current_session_id=S`; assert it returns `("prime-builder", "marker")`. Proves the envelope-hint
  marker overrides the registry (R1; DCL assertion 2). This asserts marker-**wins** semantics, not
  mere read order.
- **R1 — `test_r1_resolver_reads_marker_before_durable_fallback` (structural grep).** Assert
  `resolve_interactive_session_role` exists, calls `_read_marker(`, and contains the marker-wins
  return `return role, "marker"`; assert the only `_durable_role(`-sourced returns are the
  `durable_marker_absent | durable_marker_invalid_role | durable_marker_stale_session` branches.
- **R2 — `test_r2_registry_is_fallback_only` (behavioral).** Assert marker-absent →
  `(durable, "durable_marker_absent")`; invalid role → `durable_marker_invalid_role`; stale
  session_id → `durable_marker_stale_session`. Proves registry consulted only when no valid hint
  (R2).
- **R3 — `test_r3_dispatcher_routes_via_registry_projection` (structural grep).** On `TRIGGER_PATH`
  assert `load_harness_projection(` is used and `_resolve_dispatch_target(` exists; assert routing
  does not read the interactive session marker (`active-session-role.json` absent from the routing
  path). Proves dispatch is registry-authoritative (R3; DCL assertion 3). Complements the
  init-keyword test's identity-inversion check.
- **R4 — `test_r4_mismatch_is_warning_surface_not_override` (structural).** Assert
  `_audit_log_misdirected_dispatch(` exists in `CORE_PATH` and targets `dispatch-failures.jsonl`;
  assert `resolve_interactive_session_role` never `raise`s on a marker/durable disagreement (its
  mismatch branches `return` a durable fallback with a `source` tag); assert the doctor's
  `_check_role_set_topology_consistency` mismatch path is WARN-severity (grep for the WARN status
  constant in that check). Proves mismatch → warn+suggest, not override (R4; DCL assertion 4, code
  portion).
- **R5 — `test_r5_no_gate_invalidates_on_registry_mismatch_alone` (grep_absent).** Sweep the gate
  set for the anti-pattern: code that reads a registry `status` (`suspended`/`non-functional`) or a
  registry-vs-declared role disagreement and then rejects/raises/drops/DEFERs a verdict, dispatch,
  or work product **solely** on that basis. Assert absent. Explicitly allow the existing
  `STRICT_DROP` path (keyed to `keyword_mode not in own_role_set` — durable-role enforcement of the
  dispatched init keyword, NOT a registry status/role-mismatch invalidation) via a documented
  carve-out so the guard does not false-positive. Proves R5 stays clean (DCL assertion 1).
- **Meta — `test_dcl_role_resolution_authority_001_spec_present` (sanity).** Assert the DCL row
  exists in MemBase with R1–R5 present in its body, anchoring the test to the live spec.

### Assertion expressibility (honest scope)

- R1, R2: behavioral + structural grep — strong mechanical enforcement.
- R3: structural grep — strong.
- R4: structural grep covers the **code** portion (warn/audit surface exists; resolver never
  raises; doctor check is WARN). The "an *agent* renders a mismatch observation as warning+suggestion"
  portion is agent-behavior governed by R4 as rule-cited soft authority and is **not** mechanically
  testable on agent prose; this is stated, not hidden (consistent with operating-model §3
  implemented-vs-intended discipline).
- R5: grep_absent covers the **code/gate** portion (no gate invalidates on mismatch alone). The "no
  *agent* parks work on registry mismatch alone" portion is the S436 lesson and remains rule-cited
  soft authority (the incident was agent behavior, not codified logic), backed by the
  `ADR`/`DCL` + this guard against the failure mode being *codified*.

## Spec-to-Test Mapping

| Rule / DCL assertion | Test function | Type | Code surface |
|---|---|---|---|
| R1 (envelope hint authoritative) / assertion 2 | `test_r1_marker_role_wins_over_mismatched_durable` + `test_r1_resolver_reads_marker_before_durable_fallback` | behavioral + grep | `scripts/session_role_resolution.py` |
| R2 (registry fallback only) | `test_r2_registry_is_fallback_only` | behavioral | `scripts/session_role_resolution.py` |
| R3 (dispatcher registry-authoritative) / assertion 3 | `test_r3_dispatcher_routes_via_registry_projection` | grep | `scripts/cross_harness_bridge_trigger.py` |
| R4 (warn, do not override) / assertion 4 | `test_r4_mismatch_is_warning_surface_not_override` | grep + structural | `scripts/session_start_dispatch_core.py`, `doctor.py` |
| R5 (no invalidation on mismatch alone) / assertion 1 | `test_r5_no_gate_invalidates_on_registry_mismatch_alone` | grep_absent | gate set (5 files) |
| DCL presence | `test_dcl_role_resolution_authority_001_spec_present` | behavioral (MemBase read) | `groundtruth.db` |

## Verification Plan (commands)

```
python -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short
python -m ruff check platform_tests/scripts/test_dcl_role_resolution_authority_001.py
python -m ruff format --check platform_tests/scripts/test_dcl_role_resolution_authority_001.py
```

Expected: all tests PASS (confirming current conformance), ruff lint + format clean. On promotion to
INDEX, the applicability preflight is expected to report `preflight_passed: true` with
`missing_required_specs: []` given the Specification Links above.

## Scope Boundaries & Future Work

IN SCOPE (this slice): the pytest enforcement module only. No source file changes (R1–R3 already
conform; R4 surface exists; R5 is a stay-clean guard). `target_paths` is exactly the one new test
file.

OUT OF SCOPE / FUTURE (owner-gated): populating the `assertions[]` field on the
`DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` spec row so `gt assert` surfaces R1–R5 at session start
in addition to pytest/CI. That is a **DCL new-version** and therefore requires a
formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.
Offered as an optional follow-on if the owner wants session-start surfacing; deliberately excluded
here to keep this slice off the packet-gated path.

## Risk & Rollback

Low risk. New test-only file; no behavior, source, config, or KB mutation. Worst case: a test fails
on first run, which surfaces a real R1–R5 conformance gap — handled by a scoped REVISED proposal,
not by weakening the test. Rollback = delete the test file. No protected behaviors removed or
altered.

## Recommended Commit Type

`test:` — test-only addition (one new pytest module, no production-code change).

## Owner Decisions / Input

No owner decision gates this slice: the test module proceeds through the standard bridge path
(GO → impl-start packet → implement → report → VERIFIED) with no formal-artifact mutation and no
destructive or deployment action. The only owner-gated element is the optional Future-Work item
above (DCL `assertions[]` population), which—if the owner elects it—requires a separate
formal-artifact-approval packet for the DCL new-version and would be filed as its own thread. That
election is deferred and is explicitly **not** part of this proposal's authorized scope.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
