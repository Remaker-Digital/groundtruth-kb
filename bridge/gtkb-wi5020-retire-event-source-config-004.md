GO
author_identity: claude
author_harness_id: B
author_session_context_id: 2026-07-05T12-57-52Z-loyal-opposition-B-aca1d3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker (resolved_role=loyal-opposition); dispatch id 2026-07-05T12-57-52Z-loyal-opposition-B-aca1d3

# Loyal Opposition Review - GO - WI-5020 neutralize vestigial harness event-source configuration

bridge_kind: lo_verdict
Document: gtkb-wi5020-retire-event-source-config
Version: 004
Date: 2026-07-05 UTC
Responds to: bridge/gtkb-wi5020-retire-event-source-config-003.md (REVISED, prime_proposal, Codex/A)

## Verdict

GO. The REVISED proposal resolves every finding from the -002 NO-GO. It selects
Option B (neutralize configured event-source state; retain the honest
compatibility schema fields), which dissolves the F1 parser-break hazard, makes
the acceptance criteria achievable within the declared target_paths, and keeps
the shared receive-dispatch fallback intact. I verified the load-bearing
achievability claims against live source (the manifest parser and the manifest's
current A/B/E state) rather than accepting the proposal's self-report; they hold.
Both mandatory preflights are clean on the operative REVISED file. The scope is
bounded, in-root, and correctly defers full schema/API removal to a separate
future slice.

## Review Independence

This verdict is authored from harness B (Claude), dispatch session
2026-07-05T12-57-52Z-loyal-opposition-B-aca1d3. The reviewed REVISED proposal
(-003) was authored from harness A (Codex), author session context
2026-07-05T12-48-36Z-prime-builder-A-a1ef5d. Author and reviewer session
contexts differ; the session-context independence gate is satisfied. (The prior
-002 NO-GO in this chain was authored by harness B in a distinct earlier dispatch
session; the artifact under review here is -003, authored by A, so independence
is not implicated by the shared harness label.)

## Applicability Preflight

- packet_hash: `sha256:ec4c8753ecc80ba14c5eb5b929412fe8d0c3acc19a9b523cd5ffcc6c992d8127`
- bridge_document_name: `gtkb-wi5020-retire-event-source-config`
- operative_file: `bridge/gtkb-wi5020-retire-event-source-config-003.md`
- operative_version_status: `REVISED` (version 3)
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

The mechanical spec-linkage floor is clean. This GO rests on the substantive
finding-resolution assessment below, which the applicability preflight does not
evaluate.

## Clause Applicability

- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (pass)

All registered must_apply ADR/DCL clauses (CLAUSE-IN-ROOT, NUMBERED-FILE-CHAIN,
CONCRETE-LINKS, SPEC-TO-TEST-MAPPING) show satisfying evidence. No blocking gap.

## Prior Deliberations

The REVISED proposal replaced the -001 helper placeholder with a substantive
section citing DELIB-20265888 (2026-06-25 dispatch-storm root cause; the
harness-must-not-trigger-dispatch invariant behind ADR-DISPATCHER-ARCHITECTURE-001's
Failed Approach) and DELIB-202665470 (the resume decision naming the vestigial
can_fire_events / event_driven_hooks cleanup as separate follow-on work), plus
bridge-thread precedents and a note that live semantic searches returned empty
while direct-ID reads supplied the records. The mandatory Prior Deliberations
gate (codex-review-gate.md / file-bridge-protocol.md) is satisfied. The proposal
does not revisit any previously rejected approach; its direction is consistent
with the ADR of record.

## Findings Resolution Assessment

### F1 - target_paths insufficient / in-scope YAML edit breaks out-of-scope parser: RESOLVED (verified)

- Option B keeps every harness's `can_fire_events` key present (valued `false`)
  instead of removing it. Verified against `agent_role_manifest.py:304-308`:
  `_bool_field` does `value = data.get(field); if not isinstance(value, bool): raise`.
  A present `false` is a bool and passes; only an absent/non-bool value raises.
  The manifest edit therefore no longer breaks the out-of-scope parser.
- The companion `dispatch_mode: event_source -> other` transition is achievable
  in-scope. Verified `VALID_DISPATCH_MODES = frozenset({"dispatch_target",
  "event_source", "manual_only", "unavailable"})` at `agent_role_manifest.py:14`;
  A and E can move to `dispatch_target` (already used by harness D) while
  preserving `can_receive_dispatch: true`, with `VALID_DISPATCH_MODES` unchanged,
  so the parser source stays correctly out of scope.
- The manifest regression test `groundtruth-kb/tests/test_agent_role_manifest.py`
  is correctly added to target_paths: the `event_sources` property
  (`agent_role_manifest.py:97-98`) filters on `can_fire_events`, so its expected
  set changes when A and E flip to false. Confirmed the file exists on disk.
- Scoping the parser TEST but not the parser SOURCE is the right call because the
  parser's behavior is unchanged under Option B.

### F2 - "retire" ambiguity / Acceptance Criterion 2 unachievable in-scope: RESOLVED

- The revision explicitly selects Option B and renames the work to "Neutralize
  vestigial harness event-source configuration." The Acceptance Criteria are
  rewritten to a configured-state form ("no currently configured harness has
  event-source ..."; "every harness still declares an explicit boolean
  can_fire_events: false") that is achievable within the declared target_paths
  and no longer promises full field removal.

### F3 - dead reader in dispatcher_runtime.py not scoped: RESOLVED (consistent with Option B)

- F3 was conditional on Option A. Under Option B, `scripts/dispatcher_runtime.py`
  is correctly excluded (listed under Out Of Scope) and acknowledged as a future
  cleanup candidate. The `_record_can_fire_events` reader remains dead (0 callers,
  confirmed in the -002 review), so its retention carries no functional risk.

### F4 - event_driven_hooks double-duty entanglement: RESOLVED

- The Revised Scope explicitly preserves the receive-dispatch fallback: "No
  implementation may remove the event_driven_hooks fallback used by
  scripts/dispatcher_runtime.py or groundtruth-kb/src/groundtruth_kb/project/doctor.py
  in this slice." Because current projected records all carry
  `can_receive_dispatch`, setting `event_driven_hooks: false` in configured data
  does not exercise the absent-key fallback and cannot regress receive-dispatch
  back-compat. Sound.

### F5 - premise precision (only B named; A/B/E diverge): RESOLVED

- The revision reconciles all event-source-tagged surfaces, not only B. Confirmed
  the manifest's current state: A (dispatch_mode: event_source, can_fire_events:
  true) and E (dispatch_mode: event_source, can_fire_events: true) are the two
  event-source entries; B is already false. The proposal cites a live
  `gt bridge dispatch health --json` run returning routing-config PASS with
  `consistency_findings: []` (the nonzero exit attributed to unrelated
  supervisor/watchdog scheduled-task lifecycle failures). Scope now targets A, B,
  and E across rules.toml, the manifest, and the registry projection.

### Prior Deliberations placeholder (independent mandatory-NO-GO condition in -001): RESOLVED

- See the Prior Deliberations section above; the -001 placeholder is replaced
  with substantive precedent.

## Positive Confirmations

- Both mandatory preflights are clean on the operative REVISED file
  (applicability `preflight_passed: true`, no missing specs; clause gate exit 0,
  0 blocking gaps).
- Both newly-added target paths exist:
  `groundtruth-kb/tests/test_agent_role_manifest.py` and
  `groundtruth-kb/tests/test_harness_projection.py`.
- All 12 declared target paths are inside `E:\GT-KB`; CLAUSE-IN-ROOT satisfied.
- The revision correctly bounds scope: full removal of the `can_fire_events`,
  `event_driven_hooks`, and `event_source` schema/API fields (and edits to the
  six field-plumbing source surfaces surfaced in the -002 NO-GO) are explicitly
  out of scope, which is what makes Option B internally consistent.
- No scope element was dropped from -001; the two test paths were added, and the
  expansion remains inside the existing PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION /
  WI-5020 authorization (no new owner decision implicated).

## Residual Risks / Verification Gaps (implementation report must demonstrate)

These are post-implementation verification obligations, not proposal defects.
The eventual implementation report should show:

1. The manifest still loads after A/E move off `event_source` (invoke
   `load_agent_role_manifest`), and A/E are absent from `event_sources`; A/E's
   replacement dispatch_mode is a valid member (e.g., `dispatch_target`) and
   preserves `can_receive_dispatch: true`.
2. Every harness in the regenerated `harness-state/harness-registry.json`
   projects `can_fire_events: false` and `event_driven_hooks: false`, while
   `can_receive_dispatch`, selected PB/LO dispatch targets, reviewer precedence,
   and cost/quality/availability ranking are unchanged. Because A (active Codex)
   is a live dispatch target, confirm A still receives dispatch after the change.
3. Runtime status/report output (the in-scope `state_report.py` surface) no
   longer presents any harness as an active event source, and the out-of-scope
   plumbing surfaces (`cli.py` `gt bridge dispatch config`, `doctor.py`) still
   round-trip the retained schema field valued `false` without error (they plumb
   the field but do not gate dispatch on it).
4. The AC clause "no ... event-source in dispatch tags" for the registry: the
   `event-source` tag lives in `config/dispatcher/rules.toml`; verification
   should confirm both the rules.toml tag removal for A/B/E AND the registry
   boolean neutralization are addressed (minor wording nuance; not a blocker).
5. `gt bridge dispatch health` returns routing-config PASS with empty
   consistency findings after the change (the WI-5020 motivating B WARN clears
   and no new A/E divergence is introduced).

## Methodology Trail

- Files inspected: `bridge/gtkb-wi5020-retire-event-source-config-001.md`,
  `-002.md`, `-003.md`; `groundtruth-kb/src/groundtruth_kb/agent_role_manifest.py`
  (lines 1-120 and 238-319, covering `VALID_DISPATCH_MODES`, the
  `event_sources`/`dispatch_targets` properties, `_parse_harness`, and
  `_bool_field`); `config/agent-control/declarative-agent-role-manifest.yaml`
  (harness A/B/C/D/E/F inventory block); glob confirmation of
  `groundtruth-kb/tests/test_agent_role_manifest.py` and
  `groundtruth-kb/tests/test_harness_projection.py`.
- Commands run:
  `bridge_applicability_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config --json`
  (preflight_passed true; operative resolved to -003 REVISED v3);
  `adr_dcl_clause_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config`
  (exit 0; 0 blocking gaps); bridge work-intent session-id resolver check.
- Not run (approval-gated in this dispatched worker): `gt bridge dispatch health`
  and `gt harness roles`. Registry/manifest/rules file reads and the -002
  methodology were used in their place; the live routing reconciliation is a
  post-implementation verification obligation per the Residual Risks section.

## Owner Decisions / Input

None required to act on this GO. Prime Builder proceeds to implementation within
the existing PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION / WI-5020 authorization
(implementation-start packet from this GO, then post-implementation report for
verification). The REVISED scope expansion is inside that authorization; no new
owner decision is implicated.

## Recommended Commit Type (agreement)

The proposal's `fix` recommendation is appropriate for the eventual
implementation commit: this corrects configuration drift (harnesses configured
as event sources under a rejected trigger model) without adding a new capability
surface. The implementation report will carry the final recommendation.
