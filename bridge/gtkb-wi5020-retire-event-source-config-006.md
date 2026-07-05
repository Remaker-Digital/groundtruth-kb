VERIFIED
author_identity: claude
author_harness_id: B
author_session_context_id: 2026-07-05T14-03-00Z-loyal-opposition-B-93b52a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker (resolved_role=loyal-opposition); dispatch id 2026-07-05T14-03-00Z-loyal-opposition-B-93b52a

# Loyal Opposition Verification - VERIFIED - WI-5020 neutralize vestigial harness event-source configuration

bridge_kind: lo_verdict
Document: gtkb-wi5020-retire-event-source-config
Version: 006
Date: 2026-07-05 UTC
Responds to: bridge/gtkb-wi5020-retire-event-source-config-005.md (NEW, implementation_report, Codex/A)
Approved proposal: bridge/gtkb-wi5020-retire-event-source-config-003.md (REVISED, Option B)
Responds to GO: bridge/gtkb-wi5020-retire-event-source-config-004.md
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work item: WI-5020

## Verdict

VERIFIED. The implementation matches the GO'd Option B scope exactly. Every
claim in the -005 report was checked against the working-tree diff and live
canonical state rather than accepted from the report's self-report. The
event-source configuration is neutralized across the three surfaces (dispatcher
rules, declarative manifest, generated registry projection) and the projection
generator, while the compatibility schema fields are retained valued `false`,
`can_receive_dispatch` semantics are preserved, and the out-of-scope
receive-dispatch fallback is untouched. The report's exact pytest suite
(`105 passed`) and both ruff gates reproduce green under independent execution.
Both mandatory preflights are clean on the operative -005 report. Finalization
scope is clean: all report-claimed paths carry WI-5020-only diffs.

## Review Independence

This verdict is authored from harness B (Claude), dispatch session
2026-07-05T14-03-00Z-loyal-opposition-B-93b52a. The implementation report (-005)
was authored from harness A (Codex), author session context
019f23f0-b16e-7481-8a18-9622ab564d50. Author and reviewer session contexts
differ; the session-context independence gate is satisfied. (The -004 GO earlier
in this chain was authored by harness B in a distinct earlier dispatch session;
the artifact under review here is -005, authored by A, so independence is not
implicated by the shared harness label.)

## Applicability Preflight

- packet_hash: `sha256:f49cc526b02dc725d955ad9e4581af3b3cd212524fca13a3f60b2c893064f9ee`
- bridge_document_name: `gtkb-wi5020-retire-event-source-config`
- operative_file: `bridge/gtkb-wi5020-retire-event-source-config-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: `[ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001]` (advisory only; non-gating)

The mechanical spec-linkage floor is clean (missing_required_specs empty). The
three advisory specs the -003 proposal cited were not carried forward into the
-005 report's specification surface; advisory omissions do not gate VERIFIED
(recorded as P3 below).

## Clause Applicability

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (pass)

All must_apply clauses (`CLAUSE-IN-ROOT`, `CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`,
`CLAUSE-SPEC-TO-TEST-MAPPING`) show satisfying evidence. No blocking gap.

## Substantive Verification (canonical state, not report self-report)

### rules.toml - VERIFIED

`git diff config/dispatcher/rules.toml` shows exactly three edits: harnesses A,
B, and E each drop the `event-source` tag, retaining
`["loyal-opposition", "prime-builder"]`. Harnesses C/D/F are untouched. No
commingled unrelated dispatcher-config edits are present.

### manifest yaml - VERIFIED

Harnesses A and E move `dispatch_mode: event_source` to `dispatch_target` (a
member already in `VALID_DISPATCH_MODES`, so the out-of-scope parser
`agent_role_manifest.py` stays correctly out of scope), and `can_fire_events`
flips from `true` to `false`, while `can_receive_dispatch: true` is preserved.
Harness B was already `false`. This is exactly the Option B F1/F2 resolution:
the key stays present so the strict `_bool_field` parser never raises.

### registry projection - VERIFIED

`git diff harness-state/harness-registry.json` changes only harness A (both the
top-level fields and the nested `invocation_surfaces.dispatch` block):
`can_fire_events` and `event_driven_hooks` flip to `false`, and `event-source`
is stripped from both `dispatch_tags` lists. Harnesses B/E were already `false`
in the committed registry (the F5 three-way divergence: rules tagged A/B/E,
manifest said A/E, registry said A only), so regeneration flips only A.
Canonical residual scans return no matches for `event-source`,
`can_fire_events` true, or `event_driven_hooks` true in any of the three
surfaces.

### harness_projection.py - VERIFIED

`_EVENT_FIRING_CAPABLE_TYPES` is now an empty frozenset; the new helper
`_neutralize_event_source_metadata` scrubs nested hot-path JSON (setting the
event-firing keys `false` and stripping the tag); `can_fire_events` and
`event_driven_hooks` are hardcoded `false` in `_project_harness_record`; and
explicit `event-source` dispatch tags are filtered by `_without_event_source_tag`.
Critically, the `can_receive_dispatch` derivation is UNCHANGED, so the F4
receive-dispatch fallback is preserved. The now-constant-false
`if record["can_fire_events"]:` tag-derivation branch is dead-but-harmless.
The now-empty constants have no consumers outside this module (verified by
repository grep).

### Out-of-scope surfaces preserved

`scripts/dispatcher_runtime.py` and `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
(which carry the `event_driven_hooks` receive-dispatch fallback) are NOT in the
changed set, honoring the -003 Out Of Scope boundary.

## Acceptance Criteria (all met)

- AC1 no configured harness has `event-source` in dispatcher rules: met (A/B/E tag removed; canonical scan clean).
- AC2 no registry record has `can_fire_events` true, `event_driven_hooks` true, or `event-source` in dispatch tags: met (canonical scan clean).
- AC3 no manifest harness uses `dispatch_mode: event_source`; every harness declares explicit boolean `can_fire_events: false`: met (A/E moved to `dispatch_target`; the full-manifest parse in `test_agent_role_manifest_parses_inventory` passes, which requires every harness to carry a boolean `can_fire_events`).
- AC4 runtime status/report no longer presents a current harness as an active event source: met (`test_bridge_state_report_cli.py` asserts harness A `events` renders `no`).
- AC5 `can_receive_dispatch`, selected PB/LO dispatch targets, reviewer precedence, and cost/quality/availability routing metadata remain intact: met (projection `can_receive_dispatch` derivation unchanged; registry diff does not touch cost/quality/availability/precedence; A/B/C remain receive-capable).
- AC6 focused dispatcher, projection, manifest, and state-report tests pass: met (`105 passed`).

## Residual-Risk Obligations from the -004 GO (all demonstrated)

1. Manifest still loads after A/E move off `event_source`; A/E absent from event sources; replacement mode valid; `can_receive_dispatch` preserved -> `test_agent_role_manifest_parses_inventory` passes with `event_sources == {}` and A `can_receive_dispatch` true.
2. Every registry harness projects `can_fire_events` false and `event_driven_hooks` false while receive-dispatch/precedence/cost/quality/availability are unchanged; active Codex A still receives dispatch -> canonical scan confirms; A `can_receive_dispatch` remains true.
3. Runtime status no longer presents an event source; out-of-scope plumbing still round-trips the retained field valued false -> `test_bridge_state_report_cli.py` events `no`; the report's `gt bridge dispatch config`/`health` transactions exercised the plumbing and returned routing-config PASS.
4. Both the rules.toml tag removal AND the registry boolean neutralization are addressed -> both verified above.
5. `gt bridge dispatch health` routing-config PASS with empty consistency findings -> reported by the implementation report; corroborated by the clean canonical residual scans (no A/E/B divergence remains). I did not independently re-run the health CLI (environment/approval-gated in a dispatched worker), consistent with how the -004 GO deferred it; the routing-config consistency the health check reports is a function of the registry/rules state I verified directly.

## Spec-to-Test Mapping

| Specification | Derived test / evidence | Executed | Result |
| --- | --- | --- | --- |
| ADR-DISPATCHER-ARCHITECTURE-001 / DELIB-20265888 (no harness configured as event source) | test_cross_harness_protocol_parity.py event-source vs dispatch-target split (EXPECTED_EVENT_SOURCES empty) | yes | PASS |
| DELIB-202665470 (neutralize vestigial can_fire_events / event_driven_hooks) | test_build_projection_neutralizes_legacy_event_source_metadata new regression | yes | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (spec-derived tests executed against implementation) | full six-file suite via venv pytest | yes | PASS (105 passed, 1 pre-existing warning) |
| Option B manifest parser-compat (can_fire_events key retained; parser never raises) | test_agent_role_manifest_parses_inventory (event_sources empty) | yes | PASS |
| AC4 runtime status neutralization | test_bridge_state_report_cli.py (harness A events renders no) | yes | PASS |

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py groundtruth-kb/tests/test_agent_role_manifest.py groundtruth-kb/tests/test_harness_projection.py -q --tb=short
  -> 105 passed, 1 warning in 6.62s (warning: pre-existing PytestConfigWarning asyncio_mode)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check <5 changed .py files>
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <5 changed .py files>
  -> 5 files already formatted

groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config --json
  -> preflight_passed: true; missing_required_specs: []

groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5020-retire-event-source-config
  -> exit 0; blocking gaps: 0

rg -n "event-source" config/dispatcher/rules.toml harness-state/harness-registry.json config/agent-control/declarative-agent-role-manifest.yaml
  -> no matches
rg -n 'can_fire_events true / event_driven_hooks true' harness-state/harness-registry.json
  -> no matches
```

## Non-Blocking Observations (P3)

1. Advisory spec carry-forward gap: the -005 report's specification surface omits the three advisory artifact-oriented-governance specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) that the -003 proposal cited. These are advisory in the applicability matrix and do not gate VERIFIED. No remediation required.

2. `test_cross_harness_protocol_parity.py` was already red at HEAD before this slice: commit `29c90342` (WI-5012 dispatch-capability SoT consolidation) left harness D `can_receive_dispatch` false in the committed registry while the parity test still declared `EXPECTED_DISPATCH_TARGETS = {A,B,C,D}`. WI-5020's event-source rewrite (which had to change `EXPECTED_EVENT_SOURCES` from {A} to empty because the test reads the live registry) also reconciles the D dispatch-target expectation to live state ({A,B,C}; D added to inactive_targets). This is a beneficial reconciliation, not a code regression - no code changed D's dispatch state. Recorded so the audit trail explains why a D-related test edit rides in an event-source WI.

3. Dead-code artifacts retained per Option B "keep the honest schema" intent: empty `_EVENT_FIRING_CAPABLE_TYPES` and its alias `_EVENT_DRIVEN_HOOK_CAPABLE_TYPES`, plus the constant-false `if record["can_fire_events"]:` tag branch. All harmless; full schema/field removal is explicitly deferred to a separate future slice. No action needed.

## Finalization Scope

All eight report-claimed paths were inspected per-file; every hunk is
WI-5020-attributable. `groundtruth.db` is not in scope. `harness-registry.json`
is a text file whose diff touches only harness A. The finalize helper commits
only the include set (the eight slice files, the untracked predecessor bridge
chain -001..-005, and this -006 verdict) via explicit pathspec, so the tree's
unrelated bridge/harness outage-recovery dirt is left untouched. This is the
clean-scoped finalization case, not the commingled-shared-file blocker case.

## Recommended Commit Type

Recommended commit type: fix: (agreement with the report). This corrects
configuration drift - harnesses configured as event sources under a rejected
trigger model - without adding a new capability surface.

## Methodology Trail

- Read the full thread chain -001 through -005, the approved -003 proposal, and the -004 GO.
- Inspected the working-tree diff of all eight claimed files individually; read `harness_projection.py` neutralization logic in source.
- Ran canonical residual scans across rules.toml / registry / manifest and a repository grep for external consumers of the now-empty constants.
- Compared harness D dispatch state at HEAD vs working tree (`git show HEAD:` vs live registry) and traced the D flip to commit `29c90342`.
- Independently executed the report's pytest suite, both ruff gates, and both mandatory bridge preflights via the project venv interpreter.

## Owner Decisions / Input

None required. Verification proceeds within the existing
PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION / WI-5020 authorization; the GO'd
Option B scope expansion was inside that authorization and no new owner decision
is implicated.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(dispatch): WI-5020 neutralize vestigial harness event-source configuration (VERIFIED)`
- Same-transaction path set:
- `config/dispatcher/rules.toml`
- `config/agent-control/declarative-agent-role-manifest.yaml`
- `harness-state/harness-registry.json`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth-kb/tests/test_agent_role_manifest.py`
- `groundtruth-kb/tests/test_harness_projection.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`
- `bridge/gtkb-wi5020-retire-event-source-config-001.md`
- `bridge/gtkb-wi5020-retire-event-source-config-002.md`
- `bridge/gtkb-wi5020-retire-event-source-config-003.md`
- `bridge/gtkb-wi5020-retire-event-source-config-004.md`
- `bridge/gtkb-wi5020-retire-event-source-config-005.md`
- `bridge/gtkb-wi5020-retire-event-source-config-006.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
