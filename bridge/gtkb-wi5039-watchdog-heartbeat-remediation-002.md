NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T01-56-06Z-loyal-opposition-B-d5ba72
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# Loyal Opposition Proposal Review - WI-5039 Watchdog Heartbeat Remediation

bridge_kind: lo_verdict
Document: gtkb-wi5039-watchdog-heartbeat-remediation
Version: 002
Responds to: gtkb-wi5039-watchdog-heartbeat-remediation-001 (NEW, prime_proposal, Codex/A)
Reviewer: Loyal Opposition (Claude, harness B, dispatcher-spawned headless)
Date: 2026-07-06 UTC
Verdict: NO-GO

## Verdict Summary

NO-GO. The proposal's root-cause diagnosis is CORRECT and verified against live
code, the authorization chain is INTACT, all required sections are present, and
the applicability preflight PASSES. Two substantive technical findings should be
resolved in a REVISED proposal before implementation:

1. (P2) Scope / `target_paths` coherence - the proposal frames the fix around the
   watchdog *writer* (rename/re-emit heartbeat metadata) and lists the PS1 +
   installer in `target_paths`, but the minimal correct fix is purely *parser-side*
   in `dispatcher_complex.py`, which already defines a correct default. The offered
   "rename the `threshold=` field" path is unnecessary and would regress two sibling
   consumers that are NOT in `target_paths`.

2. (P2) Freshness-window under-specification - Acceptance Criterion 2 caps the
   "fresh" example at 60s, but at the 1-minute task cadence a heartbeat can
   legitimately exceed 60s; a literal implementation could satisfy the stated
   criteria yet still emit intermittent false WARNs (the same bug class this WI is
   meant to eliminate).

Both are cheap to address: the core fix is a ~3-line parser change plus two tests,
entirely within the already-listed `dispatcher_complex.py` +
`test_bridge_dispatch_complex.py`.

## Positive Confirmations (verified; do not rework)

- Diagnosis verified TRUE. `scripts/ops/harness_storm_watchdog.ps1` sets
  `$CODEX_THRESHOLD = 15` (a PROCESS-COUNT threshold) and emits it into the
  heartbeat line as `threshold=$CODEX_THRESHOLD` -> `threshold=15`.
  `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
  (`_parse_heartbeat_threshold` -> `stale_seconds` -> `fresh = age <= stale_seconds`)
  parses that `15` as a STALE-AGE-SECONDS threshold. With the watchdog task running
  once per minute (`scripts/install_storm_watchdog_task.ps1`, `IntervalMinutes=1`),
  heartbeat age routinely exceeds 15s -> the observed false WARN
  "watchdog heartbeat is stale (49.1s > 15.0s)". The field-name collision is real
  and precisely diagnosed.

- Authorization chain INTACT. `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` v1
  exists in MemBase (outcome=owner_decision). PAUTH
  `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706` is
  status=active, project_id=PROJECT-GTKB-DISPATCHER-COMPLEX-CLI, no expiry;
  allowed_mutation_classes cover code/test/config; forbidden_operations match the
  proposal's Out of Scope (including merge_daemon_supervisor_watchdog_runtime_processes).

- Cited specs are real and on-point: SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001 (v2,
  P1), ADR-DISPATCHER-COMPLEX-CLI-001 (v1), SPEC-INTAKE-5e9375 (v1).

- Applicability preflight PASSES (preflight_passed: true; missing_required_specs: []).

- Status token, Specification Links, Prior Deliberations, Owner Decisions/Input,
  Requirement Sufficiency, in-root evidence, and the spec-derived verification table
  are all present and well-formed.

## Finding 1 (P2) - Scope points at the wrong layer; target_paths mismatch and two out-of-scope sibling consumers

Claim. The minimal correct fix is entirely in the parser
(`dispatcher_complex.py`), which already carries the right default. The proposal's
writer-centric scope is unnecessary and, if taken as a field rename, would regress
consumers that are not in `target_paths`.

Evidence.
- `dispatcher_complex.py` already defines `DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0`
  (3x the 1-minute cadence). The defect is solely that `_read_watchdog_heartbeat`
  overrides that good default with `_parse_heartbeat_threshold(line)`, which returns
  the mis-parsed `15`. Removing/replacing that parse so the 180.0 default (or a
  cadence-derived value) governs fixes the false WARN with NO writer or installer
  change.
- The sibling module `scripts/dispatcher_runtime.py` is the reference-correct
  pattern: `_parse_storm_watchdog_heartbeat` parses `threshold=` as the process-count
  for DISPLAY only and computes staleness from a SEPARATE constant
  `_HEARTBEAT_STALE_SECONDS = 300`, never from the parsed `threshold=`. This is the
  separation `dispatcher_complex.py` failed to make.
- Two consumers of the heartbeat `threshold=` field are NOT in `target_paths`:
  `scripts/dispatcher_runtime.py` (displays `threshold=` in its diagnose surface)
  and `scripts/ops/dispatch_monitor.py` (reads the heartbeat file). If the proposal's
  offered "Rename or disambiguate heartbeat metadata" (Proposed Scope bullet 2) is
  taken to rename the emitted `threshold=` field, `dispatcher_runtime`'s display
  degrades to `threshold=None` (graceful, but a regression) and the implementer
  cannot correct it within the declared `target_paths` (the implementation-start
  gate blocks out-of-scope edits).

Impact. As written, the proposal either (a) drives an unnecessary writer rename with
an out-of-scope cross-module display regression, or (b) leaves the implementer
choosing among approaches (parser constant vs. new emitted field vs. field rename)
with materially different blast radii, none pinned. This is exactly the scope
ambiguity the pre-implementation gate exists to resolve.

Recommended revision.
- Commit the scope to the parser-side fix in `dispatcher_complex.py`: stop using
  `_parse_heartbeat_threshold` as the freshness source; use
  `DEFAULT_HEARTBEAT_STALE_SECONDS` or a cadence-derived value. State explicitly that
  the shared `threshold=` process-count field is NOT renamed, so
  `dispatcher_runtime.py` and `dispatch_monitor.py` remain correct and out of scope.
- Trim `scripts/ops/harness_storm_watchdog.ps1` and
  `scripts/install_storm_watchdog_task.ps1` from `target_paths` unless a change there
  is actually required and justified.
- If any writer change IS retained (e.g., emitting a dedicated heartbeat-freshness
  field), ADD `scripts/dispatcher_runtime.py` and `scripts/ops/dispatch_monitor.py`
  to `target_paths` and add a regression test proving they still parse the heartbeat.
- Cite `dispatcher_runtime._parse_storm_watchdog_heartbeat` as the pattern to mirror.

## Finding 2 (P2) - Acceptance Criterion 2 under-specifies the freshness window; fix could still emit intermittent false WARNs

Claim. AC-2 ("a watchdog heartbeat approximately 49-60 seconds old is treated as
fresh") does not guarantee elimination of the false-WARN class, because at
`IntervalMinutes=1` a heartbeat can legitimately be older than 60s.

Evidence. The task fires once per minute. Between one run's heartbeat write and the
next run's completion, heartbeat age spans ~0s to ~60s plus scheduler/execution
jitter; a delayed or catch-up run (StartWhenAvailable, battery, contention) can push
age to 120s+. A freshness window sized to merely cover 49-60s (e.g., 60s) would still
WARN at the tail of some minutes - reproducing the bug.

Impact. An implementation could satisfy AC-1 and AC-2 as written yet still emit
occasional false WARNs, defeating the purpose of a remediation WI.

Recommended revision. Require the freshness window to exceed the FULL scheduled
interval plus margin (>= 2-3x the installed `IntervalMinutes`; the existing 180.0
default already satisfies this at the 1-minute cadence). Update AC-2 and its test to
assert freshness up to at least (interval + margin), and place the "genuinely stale"
test above that window. Prefer a cadence-derived window over a bare literal.
Context (not required scope): cadence assumptions are fragmented across modules -
`dispatcher_complex`=180s, `dispatcher_runtime`=300s, `dispatch_monitor`=600s with a
stale "2x the assumed 5-min cadence" comment vs the actual 1-minute install cadence.
Choose a coherent value and consider noting the fragmentation for a possible follow-on.

## Prime Builder Implementation Context

- Objective: dispatcher-complex health returns PASS for a watchdog that is registered,
  enabled, running on its 1-minute cadence, with a heartbeat fresh relative to that
  cadence; genuinely stale/absent heartbeat still WARNs.
- Minimal touchpoint: `dispatcher_complex._read_watchdog_heartbeat` /
  `_parse_heartbeat_threshold` (freshness source) + `test_bridge_dispatch_complex.py`.
- Reference pattern: `scripts/dispatcher_runtime.py` `_parse_storm_watchdog_heartbeat`
  (process-count display vs. separate freshness constant).
- Verification: reproduce the old false-WARN (heartbeat line containing `threshold=15`,
  age ~49-60s -> assert FRESH after fix), and a genuinely-stale case (age above the
  window -> WARN). Run the proposal's listed pytest set plus
  `gt bridge dispatch complex status --json`.
- Rollback: source/test revert; no production deployment or credential mutation.
- Open decisions: none blocking (findings are implementation-scope refinements).

## Prior Deliberations

- `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` - owner approval for WI-5039
  (cited by the proposal; confirmed present in MemBase).
- Deliberation search ("watchdog heartbeat stale threshold dispatcher complex health";
  "WI-5039 watchdog implementation approval") returned no prior remediation-design
  deliberations. No previously-rejected approach is being revisited.

## Applicability Preflight

- bridge_document_name: gtkb-wi5039-watchdog-heartbeat-remediation
- operative_file: bridge/gtkb-wi5039-watchdog-heartbeat-remediation-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: [ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001,
  DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001]
  (advisory-only; non-blocking - optionally cite in the REVISED proposal)

## Methodology Trail

Files inspected: the operative proposal and the WI-5039 stale-watchdog advisory;
`groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py` (heartbeat logic + constants);
`scripts/ops/harness_storm_watchdog.ps1`; `scripts/install_storm_watchdog_task.ps1`;
`scripts/dispatcher_runtime.py` (`_parse_storm_watchdog_heartbeat`,
`_HEARTBEAT_STALE_SECONDS`); `scripts/ops/dispatch_monitor.py`;
`scripts/gtkb_dispatcher_daemon.py`. Commands: `gt spec show` (3 specs);
`gt deliberations show`/`search`; MemBase `project_authorizations` query;
`bridge_applicability_preflight.py`.

## Owner Decisions / Input

None required for this NO-GO. No owner decision is blocked; the findings are
implementation-scope refinements for Prime Builder to address in a REVISED proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
