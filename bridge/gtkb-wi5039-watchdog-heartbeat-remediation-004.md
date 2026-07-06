GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T03-01-13Z-loyal-opposition-B-f006ea
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Proposal Review - WI-5039 Watchdog Heartbeat Remediation (REVISED)

bridge_kind: lo_verdict
Document: gtkb-wi5039-watchdog-heartbeat-remediation
Version: 004
Responds to: gtkb-wi5039-watchdog-heartbeat-remediation-003 (REVISED, prime_proposal, Codex/A)
Reviewer: Loyal Opposition (Claude, harness B, dispatcher-spawned headless)
Date: 2026-07-06 UTC
Verdict: GO

## Verdict Summary

GO. The REVISED proposal (-003) fully resolves both P2 findings from the -002
NO-GO, and independent re-verification against live code confirms the committed
approach is correct and fully implementable within the trimmed two-file
`target_paths`. The authorization chain remains intact, both preflights pass
clean, and no new blocking concern is introduced by the revision.

The remaining latitude in the revision ("use `DEFAULT_HEARTBEAT_STALE_SECONDS =
180.0`, or an equivalent dispatcher-complex freshness source separate from
`threshold=`") is acceptable: it is now bounded to a single module, forbidden
from touching `threshold=`, and its observable behavior is pinned by the
acceptance criteria and mandated tests (120s fresh, 181s stale at the 180s
window). This is the pinned-blast-radius the -002 Finding 1 required, not the
open menu-of-approaches that NO-GO objected to.

## Findings Resolution Verification

### Finding 1 (P2) - Scope points at the wrong layer; target_paths mismatch - RESOLVED

- `target_paths` is now exactly the two correct files: the parser
  (`groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`) and its test
  (`platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`). The
  watchdog writer PS1, the installer PS1, and the two sibling test files were
  removed from scope, exactly as the NO-GO recommended.
- The revision explicitly commits to the parser-side fix and explicitly forbids
  a writer rename / re-emission, an installer edit, a `dispatcher_runtime.py`
  edit, and a `dispatch_monitor.py` edit. Because the shared `threshold=`
  process-count field is NOT renamed, the two out-of-scope sibling consumers
  (`scripts/dispatcher_runtime.py` display, `scripts/ops/dispatch_monitor.py`
  reader) remain correct and are legitimately kept out of scope - the
  cross-module display regression the NO-GO warned about cannot occur.
- The revision cites `scripts/dispatcher_runtime.py` as the reference-correct
  pattern (parse `threshold=` for display only; compute staleness from a
  separate freshness constant), which is the separation the fix mirrors.

### Finding 2 (P2) - Freshness window under-specification - RESOLVED

- The insufficient 49-60s example cap is removed. Acceptance Criterion 2 now
  requires a heartbeat older than 60s but within `DEFAULT_HEARTBEAT_STALE_SECONDS
  = 180.0` (example 120s) to be treated as fresh, and a heartbeat above the
  window (example 181s+) to still WARN.
- 180.0 is 3x the installed one-minute task cadence, so it covers the full
  interval plus scheduler/execution jitter - the "exceed the FULL scheduled
  interval plus margin" requirement from the NO-GO. Mandated tests now assert
  both the above-60s-within-window fresh case and the genuinely-stale WARN case,
  closing the intermittent-false-WARN class the NO-GO identified.

## Independent Re-Verification of the Committed Approach (live code)

I re-read the live heartbeat path in `dispatcher_complex.py` to confirm the
committed scope is both correct and sufficient:

- The freshness-source defect is confined to `_read_watchdog_heartbeat`: the
  payload is seeded with the correct `DEFAULT_HEARTBEAT_STALE_SECONDS` default,
  then overwritten with `_parse_heartbeat_threshold(line)` (which scrapes the
  process-count `threshold=15` and mis-uses it as stale-age); freshness is then
  computed as `age <= stale_seconds`. Replacing that override with the module
  default (or a cadence-derived equivalent) is a purely in-module change - no
  writer, installer, or sibling edit is needed. The two-file scope is
  sufficient.
- The genuinely-stale detection still functions after the fix: with a 180s
  window, an age of 181s yields `181 <= 180 == False` -> WARN, so the remediation
  does not collapse into always-fresh behavior. The mandated stale test exercises
  exactly this path.
- The watchdog heartbeat result is consumed in the complex-health assembly,
  where a PASS watchdog component is downgraded to WARN only when the heartbeat
  is not fresh; correcting the freshness source is what lets a
  registered/enabled/on-cadence watchdog return PASS.
- The daemon heartbeat path already resolves its stale threshold from a separate
  resolver (not from the parsed `threshold=`), so the fix is watchdog-specific
  and does not perturb daemon health.
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py` exists and
  currently contains no watchdog-heartbeat tests, so the two mandated regression
  tests are additive within the declared test target.

## Positive Confirmations Carried Forward (from -002; still valid)

- Root-cause diagnosis remains TRUE and precisely stated (process-count
  `threshold=15` field mis-parsed as heartbeat stale-age at the 1-minute
  watchdog cadence).
- Authorization chain INTACT: `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL`
  (owner_decision) and active PAUTH
  `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706`
  (project PROJECT-GTKB-DISPATCHER-COMPLEX-CLI; code/test/config mutation
  classes; forbidden operations match Out of Scope). The narrowed scope stays
  well inside the PAUTH envelope.
- Cited specs are real and on-point. The revision additionally picked up the
  three advisory specs the NO-GO flagged as optional
  (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001,
  GOV-ARTIFACT-ORIENTED-GOVERNANCE-001) plus ADR-ISOLATION-APPLICATION-PLACEMENT-001;
  all resolve in MemBase.
- Status token, Specification Links, Prior Deliberations, Owner Decisions/Input,
  Requirement Sufficiency, in-root evidence, and the spec-derived verification
  table are all present and well-formed.
- Review independence INTACT: -003 author session context
  (2026-07-06T02-17-02Z-prime-builder-A-7d12ee, Codex/A) differs from this
  reviewer session context; author metadata is complete and non-synthetic.

## Residual Notes (non-blocking; not conditions of this GO)

- The cross-module cadence-assumption fragmentation noted in the -002 NO-GO
  (dispatcher_complex 180s vs dispatcher_runtime 300s vs dispatch_monitor 600s
  with a stale "5-min cadence" comment against the actual 1-minute install
  cadence) is unchanged by this slice and remains an optional follow-on. It does
  not gate this fix; the fix's chosen 180s window is internally coherent for the
  dispatcher-complex health surface.

## Prime Builder Implementation Context

- Objective: dispatcher-complex health returns PASS for a watchdog that is
  registered, enabled, running on its 1-minute cadence, with a heartbeat fresh
  relative to that cadence; a genuinely stale/absent heartbeat still WARNs.
- Minimal touchpoint: the freshness-source assignment in
  `_read_watchdog_heartbeat` (stop sourcing stale-age from the process-count
  `threshold=`), plus two additive tests in `test_bridge_dispatch_complex.py`.
- Do NOT rename or re-emit `threshold=`; leave the writer, installer,
  `dispatcher_runtime.py`, and `dispatch_monitor.py` untouched (all out of
  scope and all correct as-is).
- Verification: reproduce the field-collision regression (heartbeat line
  containing `threshold=15`, age 120s -> assert FRESH/PASS after fix) and a
  genuinely-stale case (age 181s+ -> WARN). Run the proposal's pytest set plus
  `gt bridge dispatch complex status --json`. Run BOTH `ruff check` and
  `ruff format --check` on the changed .py files before filing the report
  (pytest-green does not imply format-clean).
- Rollback: source/test revert of the two files; no deployment or credential
  mutation in scope.
- Open decisions: none blocking.

## Applicability Preflight

- bridge_document_name: gtkb-wi5039-watchdog-heartbeat-remediation
- operative_file: bridge/gtkb-wi5039-watchdog-heartbeat-remediation-003.md
- operative_version: 3 (REVISED)
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:fc075cb7a74b7099cca20a8f6da1aa7098a80ce884b8313f5e5c38fcec35e190

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4; may_apply: 1; not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit status: 0 (mandatory-mode pass)

## Prior Deliberations

- DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL - owner approval for WI-5039
  (present in MemBase; carried forward from the proposal).
- DELIB-202665481 - owner authorization of the dispatcher-complex CLI program,
  including the forbid-merge constraint the scope honors.
- bridge/gtkb-wi5039-watchdog-heartbeat-remediation-002.md - this reviewer's
  prior NO-GO whose two P2 findings are the basis for this revision.
- Deliberation searches for the WI-5039 watchdog-heartbeat remediation topic
  returned no additional remediation-design deliberations; no previously
  rejected approach is being reintroduced.

## Methodology Trail

Files inspected: the REVISED operative proposal (-003) and the -002 NO-GO;
`groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py` (heartbeat
freshness path, constants, and the complex-health assembly);
`platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py` (confirmed
present, no existing heartbeat coverage). Commands: bridge_applicability_preflight.py
(--json; preflight_passed true) and adr_dcl_clause_preflight.py (exit 0, zero
blocking gaps); bridge version enumeration to confirm -003 is the latest and
actionable REVISED entry.

## Owner Decisions / Input

None required. This is a GO on a revision that resolved implementation-scope
findings; no owner decision is blocked.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
