REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 019f664e-c30a-7a21-aac0-877b56e5e9fe
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; Prime Builder; collaboration_mode=Default

# GT-KB Bridge Revision - Advisory Proposal Envelope Scaffold - 005

bridge_kind: implementation_report
Document: gtkb-advisory-proposal-envelope-scaffold-implementation
Version: 005 (REVISED; NO-GO correction report)
Responds to: bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-004.md
Corrects report: bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-003.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD-COMBINED-20260715
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD
Work Item: WI-AUTO-SPEC-INTAKE-8161DC
Included Work Items: WI-AUTO-SPEC-INTAKE-8161DC, WI-5263, WI-5264, WI-5265
Primary specification: SPEC-INTAKE-8161dc
Recommended commit type: feat:

## Revision Claim

Corrected the independent NO-GO finding F1 by replacing the unsupported advisory discovery command `gt bridge threads --status ADVISORY` with the supported read-only dispatcher-backed route `gt bridge dispatch report --json --compact` in both deliberation and build session preload command lists.

TEST-11408 now verifies more than text presence: it requires the worker-facing command text to appear in both generated preload states, then executes the registered CLI route through `python -m groundtruth_kb.cli bridge dispatch report --json --compact`, parses the returned dispatcher workflow JSON, verifies `schema_version == "gtkb.dispatch_workflow.v1"`, and verifies the compact report exposes `ADVISORY` candidates.

No changes were made to backlog selection, dispatcher routing, role authority, unrelated startup behavior, or the pre-existing staged foreign hunks.

## Specification Links

- `SPEC-INTAKE-8161dc` - generated deliberation/build envelopes must expose usable Advisory Proposal knowledge and access direction.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder files this REVISED response only; terminal VERIFIED remains independent Loyal Opposition authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps advisory findings as governed artifacts and carries owner/project evidence forward.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - carries concrete specification linkage from the approved implementation proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - supplies executed spec-derived test evidence for independent VERIFIED review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - carries project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision evidence remains carried forward; no new AUQ is required.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB platform paths.
- `GOV-STANDING-BACKLOG-001` - Advisory Proposals remain future-work initiation artifacts, not implementation approval.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - generated prompt/config surfaces retain deterministic advisory access guidance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves advisory-to-governed-artifact progression instead of dropbox authority.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves ADVISORY non-dispatchable, non-approval lifecycle semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - remediation remains within the approved seven target paths and active claim.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - correction follows NO-GO, claim, target validation, and bridge report gates.

## Prior Deliberations

- `DELIB-20260715-ADVISORY-PROPOSAL-PRIMARY-LO-INITIATION-MECHANISM` - owner defined Advisory Proposals as the primary Loyal Opposition future-work initiation mechanism and required worker retrieval through the bridge.
- `DELIB-20260715-ADVISORY-PROPOSAL-KNOWLEDGE-IN-DELIBERATION-BUILD-ENVELOPES` - owner required generated deliberation/build envelopes to include usable advisory knowledge and access direction.
- `DELIB-20260715-ADVISORY-PROPOSAL-ENVELOPE-SCAFFOLD-COMBINED-PROPOSAL` - owner approved the combined implementation route.
- `bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-002.md` - independent implementation GO and hunk-isolation conditions.
- `bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-003.md` - prior implementation report.
- `bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-004.md` - independent NO-GO finding corrected here.

## Owner Decisions / Input

No new owner decision is required. The NO-GO explicitly states the correction is within the existing authorized seven-path scope.

## Findings Addressed

### F1 - P1 - Generated advisory access command does not exist

Response: corrected. `groundtruth-kb/src/groundtruth_kb/session/envelope.py:61` and `groundtruth-kb/src/groundtruth_kb/session/envelope.py:81` now advertise `gt bridge dispatch report --json --compact`, which is a supported read-only dispatcher-backed discovery route. `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py:67` executes the registered CLI command, validates JSON schema, and verifies the report exposes `ADVISORY` candidates. `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py:125` requires the advertised worker-facing command text in both preload states.

## Scope Changes

Only the NO-GO-targeted correction changed after report 003:

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`: replaced `gt bridge threads --status ADVISORY` with `gt bridge dispatch report --json --compact` in deliberation and build `PRELOAD_STATES`.
- `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`: added executable validation of the registered dispatcher report CLI route while retaining the worker-facing `gt bridge dispatch report --json --compact` command text assertion.

The other five authorized target paths remain as reported in version 003. The pre-existing staged baseline hunks remain foreign and preserved:

- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`: staged `CANONICAL_ACTIVITY_ORDER` introduction and loop change from `CANONICAL_ACTIVITIES` to `CANONICAL_ACTIVITY_ORDER`.
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`: staged `::open build` activity envelope sharding note.

## Current Target Path Hashes

| Path | Current SHA256 |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/session/envelope.py` | `1BECEDD10A72702CAE7051163CC47A7BE15C92F855E021F7CB2CEE7255D8197A` |
| `groundtruth-kb/src/groundtruth_kb/activity/profiles.py` | `B1788D38E2FD5F197D27966865A4C0718CF0F982A3E05125EE7173CFC268C009` |
| `config/agent-control/activity-disposition-profiles.toml` | `C612E9688308D4BA61BDCA31D58C04CC4B376E19DBE99077003FC43C88EF1BB2` |
| `config/agent-control/SESSION-STARTUP-INDEX.md` | `D5C143DDA556738120198A865170E870B694A0C21CE518C422CFAE14EABB9350` |
| `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` | `19F12AA15D353657B4A7227B5E74E208A2373EB2D719D85700DBF4C3308C7223` |
| `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` | `7F01D8003E1E0E70AC4E7036DAFA2BB650933EBD93FAD6195E7863C3C60F5012` |
| `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py` | `2E30FA5E2F993033FE60413309B6147FD0E8CDB0CF7162E1959630EC0A63484E` |

## Specification-Derived Verification Mapping

| Spec / test id | Executed evidence |
| --- | --- |
| `SPEC-INTAKE-8161dc` | `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py` verifies advisory semantics across startup overlays, activity profiles, rendered context, and session preload state; TEST-11408 now executes the supported advisory discovery command path. |
| `TEST-11408` | `test_test11408_session_envelope_preload_states_expose_advisory_access_path` verifies both preload states advertise `gt bridge show <advisory-slug>` and `gt bridge dispatch report --json --compact`, executes the registered dispatcher report CLI route, parses JSON, validates schema, and verifies `ADVISORY` candidates are exposed. |
| `TEST-11418` | `test_test11418_role_and_startup_scaffolds_teach_advisory_bridge_semantics` verifies PB/LO overlays and startup index carry required Advisory Proposal semantics. |
| `TEST-11419` | `test_test11419_deliberation_and_build_profiles_teach_advisory_progression` verifies deliberation/build activity profiles and rendered topic contexts carry advisory terminology, guardrails, history sources, and manipulated surfaces. |
| `TEST-11420` | `test_test11420_executable_assertion_covers_required_advisory_prompt_markers` verifies stable semantic marker coverage. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This file is a Prime Builder `REVISED` response to latest `NO-GO`; Prime Builder did not write terminal `VERIFIED`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Active claim rowid `31352` acquired for the NO-GO correction; all seven target paths returned `authorized: true`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Work remains under prior GO/start evidence plus latest NO-GO remediation claim; no direct bypass or out-of-scope mutation occurred. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries plain project authorization, project, and work item metadata lines. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries concrete governing specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused, adjacent, preflight, lint, format, and executable command evidence are supplied for independent verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Seven `implementation_authorization.py validate --target ...` checks returned `authorized: true` for in-root GT-KB paths. |
| `GOV-STANDING-BACKLOG-001` | Advisory future-work wording remains intact; no backlog selection or mutation was performed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Deterministic prompt/config surfaces retain advisory access semantics without depending on an unsupported hook. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Advisory artifacts remain bridge-governed, non-dispatchable, and not implementation approval. |

## Commands Run

- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py -q --tb=short`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest platform_tests/scripts/test_session_envelope_runtime.py -q --tb=short`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/skills/test_advisory_intake_profile_surfacing.py platform_tests/scripts/test_topic_router_operator_context.py platform_tests/scripts/test_session_startup_index.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/activity/profiles.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/activity/profiles.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb.cli bridge dispatch report --json --compact`
- `python scripts/implementation_authorization.py validate --target <each of the seven target paths>`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-proposal-envelope-scaffold-implementation`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-proposal-envelope-scaffold-implementation`

## Observed Results

- Focused advisory scaffold test: `4 passed in 16.07s`.
- Session envelope runtime adjacent regression: `19 passed in 1.58s`.
- Activity disposition, advisory intake surfacing, topic router context, and startup index adjacent regression: `28 passed in 0.55s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `3 files already formatted`.
- Dispatcher report command: exit 0; JSON `schema_version` was `gtkb.dispatch_workflow.v1`; compact report included `ADVISORY` candidate entries.
- Target authorization validation: all seven target paths returned `authorized: true`.
- Bridge applicability preflight: PASS; `missing_required_specs: []`; `blocking_errors: []`.
- Candidate-content applicability preflight: PASS; packet hash `sha256:7c605b11b2f97ba9b30f524aa371f7017db42b1bc67f8fec777b76c3f539101f`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.
- ADR/DCL clause preflight: PASS; clauses evaluated `5`; must-apply `3`; may-apply `2`; blocking gaps `0`.
- Candidate-content ADR/DCL clause preflight: PASS; clauses evaluated `5`; must-apply `4`; may-apply `1`; blocking gaps `0`.

## Risk And Rollback

Rollback remains narrow: revert only the advisory command replacement in `groundtruth-kb/src/groundtruth_kb/session/envelope.py` and the executable command validation additions in `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`, or revert the full seven-path advisory-envelope hunks from version 003 if Loyal Opposition requires a complete rollback. Preserve the staged foreign baseline hunks called out above.

## WI-5266 Serialization Note

WI-5266 remains serialized behind this slice. Its four overlapping paths should treat the current hashes in this report as the post-remediation handoff baseline after independent terminal verification.
