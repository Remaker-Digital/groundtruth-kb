NEW

# WI-4683: Runtime Topic Router Six-Member Vocabulary Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4683-router-runtime-six-member-vocabulary
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef0d4-5474-7af3-af31-4c8ab4cf4f7a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive Prime Builder; owner init ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4683

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal is the source/test follow-on for WI-4683 after the router
formal-artifact cycle reached GO and the v2 router specifications became live.
It reconciles the runtime topic-envelope vocabulary with the current
six-member set `{ops, deliberation, build, test, spec, project}`.

The change is intentionally narrow: add `ops` to the runtime topic-envelope
enumerations and strict `::open` / `::close` parser, add the minimal route and
preload stub required by `DCL-TOPIC-ENVELOPE-ROUTING-001` v2, and update the
focused tests that assert parser/runtime behavior. The substantive operations
status acquisition, decision criteria, and AUQ emission for `ops` remain owned
by WI-4687 and are out of scope.

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` - v2 defines the canonical `::open <type>` and `::close <type>` command surface over `{ops, deliberation, build, test, spec, project}`.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` - v2 requires the router dispatch map to include `ops` and the six-member typed-close grammar.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - A1 requires each canonical activity, including `ops`, to have a profile record; the router runtime must accept the same vocabulary.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - establishes the activity-envelope disposition model this runtime surface implements.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Codex UserPromptSubmit hook imports the same topic parser, so source changes must preserve hook parity behavior.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited 2026-06-23 PAUTH is snapshot-bound to WI-4683 and allows source/test mutations only.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state and numbered files are the implementation/review authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing source, routing, project, and verification constraints.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project id, work item id, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each governing requirement to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4683 is the canonical backlog item authorizing this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets are in-root GT-KB platform source/test paths.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the code follow-on preserves traceability from owner decisions to specs, bridge, tests, and implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal continues the explicit lifecycle from formal amendment to source/test implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - concrete requirements and implementation evidence remain represented as durable artifacts.

## Prior Deliberations

- `DELIB-20265287` - D10 classifies activity-vocabulary drift as a defect; F1 re-admits `ops` and defines its later substantive handler.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - DEC-4 locks the six-member vocabulary `{ops, deliberation, build, test, spec, project}`.
- `DELIB-20260638` - earlier topic-envelope content goal, superseded for vocabulary count by the later six-member decision.
- `DELIB-20260637` - envelope meta-model and topic-envelope terminology lineage.
- `DELIB-2500` - prior envelope convention and close/dispatch semantics.
- `bridge/gtkb-wi4683-activity-vocabulary-reconcile-ops-006.md` - LO GO approving the router formal-amendment split and requiring a separate source/test bridge after the v2 rows are live.

## Owner Decisions / Input

- Owner decision `DELIB-20265586` authorized the 2026-06-23 snapshot-bound implementation PAUTH for the 13 currently-open member WIs, including WI-4683, with allowed mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.
- The v2 formal router specs are already live in MemBase and record owner formal-artifact ratification on 2026-06-22.
- No new owner decision is required for this proposal because it performs source/test alignment to existing live specifications and does not mutate GOV/SPEC/ADR/DCL/PB/REQ records.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 and
`DCL-TOPIC-ENVELOPE-ROUTING-001` v2 define the six-member parser grammar and
routing map. `DCL-ACTIVITY-DISPOSITION-PROFILE-001` establishes `ops` as a
canonical activity whose substantive profile work continues in WI-4687. This
bridge only aligns runtime source and focused tests to those live requirements.

## Proposed Implementation

1. Update `groundtruth-kb/src/groundtruth_kb/session/envelope.py`:
   - add `ops` to `TOPIC_TYPES`;
   - add an `ops` route target such as `operations-status-decision-service`;
   - add an `ops` preload-state stub that names operations status, support/user activity, and ops feedback inputs without implementing the full WI-4687 handler.
2. Update `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`:
   - update `TOPIC_COMMAND_RE` to strict-match `ops|deliberation|build|test|spec|project` for both `::open` and `::close`;
   - keep spacing and first-nonblank-line behavior unchanged.
3. Update `platform_tests/scripts/test_session_envelope_runtime.py`:
   - assert the six-member `TOPIC_TYPES` set;
   - assert `open_topic(..., "ops")` returns the `ops` route/preload stub;
   - assert duplicate `ops` open still fails while existing topic behavior remains unchanged;
   - assert `parse_topic_command("::open ops")` and `parse_topic_command("::close ops")` are accepted.
4. Update `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`:
   - assert the Codex hook parser recognizes `::open ops` through the imported topic parser;
   - keep strict spacing and unknown-topic rejection tests.

## Out Of Scope

- No MemBase mutation.
- No formal-artifact approval packet.
- No change to `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`; it imports the shared parser.
- No implementation of the substantive `ops` activity handler; WI-4687 owns deployed-app status acquisition, decision criteria, and AUQ option emission.
- No single-active-envelope or bare `::close` behavior; WI-4685 requires a separate specification reconciliation before source work.

## Spec-Derived Verification Plan

| Linked spec / requirement | Verification | Expected result |
| --- | --- | --- |
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 six-member command surface | `test_wrap_and_topic_command_parsers_are_strict` plus new `ops` parser assertions | `::open ops` and `::close ops` accepted; malformed spacing and unknown topic rejected. |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 six-member dispatch map | `test_topic_open_close_is_strict_and_one_per_type` / new `ops` assertions in `test_session_envelope_runtime.py` | `TOPIC_TYPES` includes `ops`; `open_topic("ops")` returns route/preload stub. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A1 activity coverage | exact set assertion over `TOPIC_TYPES` | runtime activity vocabulary is `{ops, deliberation, build, test, spec, project}`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` hook parser parity | `test_hook_recognizes_strict_topic_commands` in `test_session_wrapup_trigger_dispatch.py` | hook recognizes `::open ops` via shared parser and keeps strict rejection behavior. |
| No regression for existing five topics | existing focused tests plus added six-member set coverage | existing `spec`, `build`, `test`, `deliberation`, and `project` behavior still passes. |

Implementation report commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short --basetemp .gtkb-state/pytest-wi4683-router-vocab
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
```

## Pre-Filing Preflight Subsection

Pre-filing preflights were run against this completed draft before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4683-router-runtime-six-member-vocabulary --content-file .gtkb-state/propose-drafts/gtkb-wi4683-router-runtime-six-member-vocabulary-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4683-router-runtime-six-member-vocabulary --content-file .gtkb-state/propose-drafts/gtkb-wi4683-router-runtime-six-member-vocabulary-001.md
```

Results:

- Applicability preflight passed: `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `packet_hash: sha256:575ed1efa02bc911d243a002960d9f5e0f837d0a6dca6313912705a7668db773`.
- Clause preflight passed: 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`,
  0 `not_applicable`, 0 evidence gaps in `must_apply`, and 0 blocking gaps.
- Phantom-spec sweep passed: all 15 cited specs were found in
  `current_specifications`; `missing: []`.
- `target_paths` parsed as valid inline JSON and the draft had no remaining
  `TODO:` placeholders.

## Risk / Rollback

Risk is moderate-low. The parser/runtime change is additive for `ops`; the main
risk is leaving a hardcoded five-member expectation in a focused test or hook
surface. The proposed target-path scan found the Codex hook imports the shared
parser, so direct hook edits are not needed.

Rollback is a single git revert of the source/test commit plus the associated
implementation report. No KB or formal artifact rollback is needed because this
proposal does not mutate MemBase.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi4683-router-runtime-six-member-vocabulary`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - reconciles a runtime vocabulary-drift defect between source/tests and
the live router specifications.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
