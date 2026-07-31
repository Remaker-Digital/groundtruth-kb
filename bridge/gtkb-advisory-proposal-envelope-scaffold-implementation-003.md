NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f664e-c30a-7a21-aac0-877b56e5e9fe
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; Prime Builder; collaboration_mode=Default

# GT-KB Bridge Implementation Report - gtkb-advisory-proposal-envelope-scaffold-implementation - 003

bridge_kind: implementation_report
Document: gtkb-advisory-proposal-envelope-scaffold-implementation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-002.md
Approved proposal: bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD-COMBINED-20260715
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD
Work Item: WI-AUTO-SPEC-INTAKE-8161DC
Included Work Items: WI-AUTO-SPEC-INTAKE-8161DC, WI-5263, WI-5264, WI-5265
Primary specification: SPEC-INTAKE-8161dc
Recommended commit type: feat:

## Implementation Claim

Implemented the approved Advisory Proposal envelope scaffold in the exact seven authorized paths. The change makes Advisory Proposal semantics visible to session envelopes, activity disposition profiles, Prime Builder and Loyal Opposition startup overlays, and an executable platform test.

Advisory Proposal handling is now expressed as governed bridge behavior:

- Advisory Proposals are governed bridge artifacts, not dropbox notes.
- Latest `ADVISORY` entries are non-dispatchable and not implementation approval.
- Advisory Proposals are the primary Loyal Opposition mechanism for future-work initiation.
- Workers access them through governed bridge/TAFE/dispatcher status surfaces and status-bearing files under `bridge/`.
- Interactive workers progress them through governed advisory intake/disposition.
- CODEX-INSIGHT-DROPBOX and `independent-progress-assessments` dropbox files are non-canonical session evidence only.

No implementation hunks were applied to backlog selection, dispatcher routing, role authority, or unrelated startup behavior.

## Governing Authorization Evidence

- Latest GO before implementation report filing: `bridge/gtkb-advisory-proposal-envelope-scaffold-implementation-002.md`.
- GO reviewer session: `019f65fb-4219-7150-ac09-26f12b650337`.
- Proposal author session: `019f664e-c30a-7a21-aac0-877b56e5e9fe`.
- Implementation claim rowid: `31348`.
- Implementation claim session: `019f6668-9974-7d72-a456-826f9a67e627`.
- Implementation-start packet hash: `sha256:c1dd296853abe4bf806c0fee458e182d5d7af36de55bd902762377bab4f814a7`.
- Pre-start packet hash: `sha256:3cb14a62b679ec82d04ec1de3eeab6b65e9ad86523cb8721bf1ed58b302c0770`.
- PAUTH was normalized through the governed `gt projects authorize` command only; PAUTH id stayed the same and moved to version 2 using registered operation tokens without broadening owner-approved scope.
- PAUTH version after normalization: `2`.
- PAUTH normalized envelope hash: `36828886e239cd469be3424833590cc69e022a31ed13e734fc0d0bb95b932ffd`.
- Bridge applicability preflight packet hash: `sha256:95d1a79f26c01c5374741602217645fe733c698fa679b291d14ba1c39ea84713`.
- `python scripts/implementation_authorization.py validate --target <target>` returned `authorized: true` for all seven target paths.

## Exact Target Paths And Hashes

| Path | Pre-edit SHA256 | Post-edit SHA256 |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/session/envelope.py` | `28703B7FCED5B97BD5CC7DC6AD62A7F3C0508D1CCFF6C6C5AC57945008EC1AF6` | `EE0EFE1B93AD0C3DD8B62861F1BFFD630298B5A7F1BBC6F678E9D9596D9ECA4A` |
| `groundtruth-kb/src/groundtruth_kb/activity/profiles.py` | `857ED7E3607AA27E5373C61E9C550FFF46F8F2EDC53235F29187D3BB49EA7B66` | `B1788D38E2FD5F197D27966865A4C0718CF0F982A3E05125EE7173CFC268C009` |
| `config/agent-control/activity-disposition-profiles.toml` | `9CD118BB9010AE5D2D3B45299DC0049E58577892D82528328A9C14CB9EF910DE` | `C612E9688308D4BA61BDCA31D58C04CC4B376E19DBE99077003FC43C88EF1BB2` |
| `config/agent-control/SESSION-STARTUP-INDEX.md` | `8A8800E7CAA834CE38C11AB6CDDC839F01F83896C8E81AD9AAA84E863F9F8815` | `D5C143DDA556738120198A865170E870B694A0C21CE518C422CFAE14EABB9350` |
| `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` | `174C2497D11AE56855F0479474251AF8B0492FB5127D6B034B2B2E0BACF55930` | `19F12AA15D353657B4A7227B5E74E208A2373EB2D719D85700DBF4C3308C7223` |
| `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` | `41AF33DF74D9328A30536E54904EBB216BF1732736025AA7903DFA318ABB34D3` | `7F01D8003E1E0E70AC4E7036DAFA2BB650933EBD93FAD6195E7863C3C60F5012` |
| `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py` | absent | `11EC682B9FEA04C8EDAD7478D70A011CF8CF8CAE00EF56EB0FBA46C37BAE164B` |

## Hunk-Level Ownership Split

Pre-existing staged baseline hunks were present before this implementation and are not claimed by this report:

- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`: staged `CANONICAL_ACTIVITY_ORDER` introduction and loop change from `CANONICAL_ACTIVITIES` to `CANONICAL_ACTIVITY_ORDER`.
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`: staged `::open build` activity envelope sharding note.

This implementation's unstaged hunks are limited to:

- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py:46`: added `ADVISORY_PROPOSAL_SEMANTIC_MARKERS` stable semantic marker tuple.
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py:48`: expanded deliberation `PRELOAD_STATES` with advisory bridge semantics and `gt bridge show <advisory-slug>` / `gt bridge threads --status ADVISORY`.
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py:69`: expanded build `PRELOAD_STATES` with advisory bridge semantics and the same advisory bridge commands.
- `config/agent-control/activity-disposition-profiles.toml:76`: added deliberation terminology for Advisory Proposals, `ADVISORY` bridge entries, governed advisory intake/disposition, and CODEX-INSIGHT-DROPBOX.
- `config/agent-control/activity-disposition-profiles.toml:88`: added deliberation history sources for advisory bridge artifacts/status files and non-canonical session evidence.
- `config/agent-control/activity-disposition-profiles.toml:105`: added deliberation guardrails for advisory bridge semantics and non-approval status.
- `config/agent-control/activity-disposition-profiles.toml:115`: added Advisory Proposal dispositions as a deliberation manipulated surface.
- `config/agent-control/activity-disposition-profiles.toml:139`: added build terminology for advisory bridge surfaces.
- `config/agent-control/activity-disposition-profiles.toml:153`: added build history sources for advisory bridge artifacts/status files and non-canonical session evidence.
- `config/agent-control/activity-disposition-profiles.toml:171`: added build guardrails for advisory access and intake/disposition.
- `config/agent-control/activity-disposition-profiles.toml:183`: added Advisory Proposal conversion proposals as a build manipulated surface.
- `config/agent-control/SESSION-STARTUP-INDEX.md:47`: added canonical startup guidance for ADVISORY bridge artifacts and non-canonical dropbox evidence.
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md:31`: added Prime Builder advisory bridge handling guidance.
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md:33`: added Loyal Opposition advisory bridge handling guidance.
- `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py:1`: added focused executable assertions covering the advisory scaffold.

## Specification-Derived Verification

| Spec / test id | Evidence |
| --- | --- |
| `SPEC-INTAKE-8161dc` | Focused platform test asserts advisory semantics across startup overlays, activity profiles, rendered context, and session preload state. |
| `TEST-11408` | `test_test11408_session_envelope_preload_states_expose_advisory_access_path` verifies deliberation/build preload states expose advisory access paths and commands. |
| `TEST-11418` | `test_test11418_role_and_startup_scaffolds_teach_advisory_bridge_semantics` verifies PB/LO overlays and startup index teach advisory bridge semantics. |
| `TEST-11419` | `test_test11419_deliberation_and_build_profiles_teach_advisory_progression` verifies deliberation/build profiles carry advisory terminology, guardrails, history sources, and manipulated surfaces. |
| `TEST-11420` | `test_test11420_executable_assertion_covers_required_advisory_prompt_markers` verifies stable semantic marker coverage. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Report filed through `impl_report_bridge.py file`; PB writes `NEW` implementation report only and does not write GO/NO-GO/VERIFIED. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `implementation_authorization.py begin` and seven `validate --target` checks passed against the live PAUTH/GO. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation began only after latest bridge `GO`, claim rowid `31348`, and implementation-start packet hash `sha256:c1dd296853abe4bf806c0fee458e182d5d7af36de55bd902762377bab4f814a7`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `bridge_applicability_preflight.py` PASS with zero missing required/advisory links and packet hash `sha256:95d1a79f26c01c5374741602217645fe733c698fa679b291d14ba1c39ea84713`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report supplies spec-derived verification commands/results for Loyal Opposition independent review before terminal VERIFIED. |

## Commands Run

- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py -q --tb=short`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest platform_tests/scripts/test_session_envelope_runtime.py -q --tb=short`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/skills/test_advisory_intake_profile_surfacing.py platform_tests/scripts/test_topic_router_operator_context.py platform_tests/scripts/test_session_startup_index.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/activity/profiles.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/activity/profiles.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`
- `python scripts/implementation_authorization.py validate --target <each of the seven target paths>`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-proposal-envelope-scaffold-implementation`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-proposal-envelope-scaffold-implementation`

## Observed Results

- Focused advisory scaffold test: `4 passed in 4.62s`.
- Session envelope runtime adjacent regression: `19 passed in 1.97s`.
- Activity disposition, advisory intake surfacing, topic router context, and startup index adjacent regression: `28 passed in 0.73s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `3 files already formatted`.
- Target authorization validation: all seven target paths returned `authorized: true`.
- Bridge applicability preflight: PASS; `missing_required: []`, `missing_advisory: []`, `blocking_errors: []`.
- ADR/DCL clause preflight: PASS; clauses evaluated `5`, must-apply `3`, may-apply `2`, blocking gaps `0`.

## WI-5266 Overlap Handoff Evidence

The four WI-5266-overlapping paths now have these hashes:

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`: `EE0EFE1B93AD0C3DD8B62861F1BFFD630298B5A7F1BBC6F678E9D9596D9ECA4A`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`: `B1788D38E2FD5F197D27966865A4C0718CF0F982A3E05125EE7173CFC268C009`
- `config/agent-control/SESSION-STARTUP-INDEX.md`: `D5C143DDA556738120198A865170E870B694A0C21CE518C422CFAE14EABB9350`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`: `19F12AA15D353657B4A7227B5E74E208A2373EB2D719D85700DBF4C3308C7223`

WI-5266 work was not combined into this project. The overlap is limited to the advisory-envelope hunks listed above plus the pre-existing staged baseline hunks called out separately.

## Rollback / Reviewer Notes

Rollback should remove only the advisory hunks listed in this report and the new focused test file. It should preserve unrelated staged baseline hunks in `profiles.py` and `PRIME-BUILDER-STARTUP-OVERLAY.md`.

This report intentionally excludes the globally dirty worktree from its Files Changed accounting. The helper scaffold captured unrelated global changes, but the live implementation evidence and verification above are limited to the seven approved target paths and the PAUTH normalization metadata.
