NEW

# Defect-Fix Proposal - Make Interactive Session Envelope CLI Writer-Usable

bridge_kind: prime_proposal
Document: gtkb-wi5252-session-envelope-cli-provenance
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-15T21-31-23Z
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; governed bridge and harness black-box stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5252-SESSION-ENVELOPE-PROVENANCE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5252
Test: TEST-11406

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_kb_attribution.py"]

## Claim

`gt session envelope open --role prime-builder --init-keyword "::init gtkb pb"` currently creates an open role-resolved interactive envelope but omits `worker_role_provenance`. Governed MemBase writers then reject that envelope and require a private Python API workaround. Make the public CLI validate the canonical init keyword against the requested role and create the same document-authoritative interactive provenance that the underlying structured API already supports. Preserve generated successor session IDs so a resumed desktop thread never overwrites its closed predecessor; WI-5256 remains the separate document-aware selector that lets later writers find that successor automatically.

## Defect / Reproduction

1. A resumed interactive Codex A Prime Builder session had no current writer-usable session envelope.
2. `gt session envelope open --harness-name codex --harness-id A --init-keyword "::init gtkb pb" --role prime-builder ...` returned an open envelope with the expected role resolution but no `worker_role_provenance` object.
3. The next canonical `gt backlog add-work-item` failed before mutation with `resolve_changed_by: Worker role provenance requires an open session envelope.`
4. Calling `groundtruth_kb.session.envelope.open_session(..., worker_role_source="transcript_init_keyword")` for that exact session produced complete provenance, after which the governed writer succeeded when bound to the exact session ID.
5. The CLI exposes no governed way to request that already-supported provenance behavior.

This recurrence is the exact WI-5252 defect. It also confirms why WI-5256 is complementary: the desktop's persistent ambient thread ID can name a closed predecessor, while `gt session envelope open` deliberately creates a new timestamped successor. WI-5252 creates valid authority in the successor document; WI-5256 selects that sole valid successor without environment rebinding.

## In-Root Placement Evidence

All five proposed source/test targets, the work item, linked test, PAUTH, bridge evidence, and session-envelope runtime are inside `E:\GT-KB`. No external file, direct harness contact, raw session JSON edit, or dispatcher/runtime mutation is required.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` - governed writer attribution must come from a validated open session document carrying explicit worker-role provenance.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - mutations must retain exact role, harness, and session attribution.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - the owner-declared interactive role persists in the current context without changing dispatcher role defaults.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the repair remains gated by independent review, claim, start authorization, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant behavioral and cross-cutting requirements are linked before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires executed CLI, runtime, and attribution regressions.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to PAUTH, project, WI, test, and exact paths.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - limits implementation to the declared source/test envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO or implementation-start evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the repeated public-CLI failure as a durable repair chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links the observation, WI/test, authorization, implementation, report, and verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps candidate, authorized, GO, implementation, and verification transitions explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all implementation and evidence in the GT-KB root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to self-enforce all bridge and source-write gates.
- `GOV-STANDING-BACKLOG-001` - keeps both WI-5252 and its WI-5256 integration dependency visible until verified.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - active bounded defect-repair authorization for bridge/TAFE/harness stabilization.
- `bridge/gtkb-wi5256-codex-interactive-session-successor-001.md` and `-002.md` - separately GO'd successor-selection repair; its source targets are not part of WI-5252.
- `DELIB-20260710-WI5086-CONCURRENT-CODEX-SESSION-ENVELOPE-CLOBBER` - prior decision protecting concurrent session documents from shared-slot overwrite.
- `TEST-11406` - linked integration test for public-CLI writer-usable provenance.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded repair of defects discovered while stabilizing genuine fleet work.
- The active owner goal directs automatic processing of bridge, TAFE, and harness black-box defects while preserving live workers and dispatcher state.

## Requirement Sufficiency

Existing requirements are sufficient. The role-authority, author-provenance, and interactive-persistence contracts already require a validated session document. WI-5252 repairs the public construction path and does not create a new authority model.

## Proposed Scope

1. Reuse the canonical closed-vocabulary init-keyword parser. Do not add a second regex or accept arbitrary role-source text.
2. When `gt session envelope open` receives a canonical `::init gtkb pb|lo` keyword and an explicit matching role, pass `worker_role_source="transcript_init_keyword"` to the structured session-envelope API so the resulting successor document includes validated `worker_role_provenance`.
3. Fail closed before writing an authoritative envelope when keyword and role disagree, the keyword is noncanonical, the role is outside the closed Prime Builder/Loyal Opposition vocabulary, or required identity data is missing.
4. Preserve the current timestamped successor session ID behavior. Do not reuse a persistent desktop thread ID that could overwrite a closed historical envelope.
5. Preserve non-authoritative role-free envelope opening for callers that do not request interactive worker authority, subject to current behavior.
6. Keep dispatcher-composed `ensure_worker_session` behavior, dispatch run provenance, bridge author-session metadata, role registry defaults, and all unrelated session lifecycle behavior unchanged.
7. Add focused CLI/runtime tests proving the positive PB and LO paths, keyword/role mismatch denial, no arbitrary source injection, role-free compatibility, historical predecessor preservation, and resolution by the exact returned session ID.
8. Treat WI-5256 VERIFIED as the prerequisite for the final no-environment-rebinding end-to-end writer assertion. WI-5252 must not modify or absorb WI-5256's shared session-selection targets.

Explicit non-scope:

- No dispatcher/TAFE runtime JSON, lease, lock, eligibility, ranking, route, model, allowance, or role-registry mutation.
- No direct harness contact, credential lifecycle, destructive cleanup, external system, push, deployment, or release.
- No raw editing or deletion of current or historical session-envelope files.
- No adoption of foreign changes in WI-5256 targets.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Document-authoritative interactive role | CLI tests invoke canonical PB and LO init keywords with matching roles and assert complete `worker_role_provenance` in the exact open successor document. |
| Fail-closed authority | Tests prove missing/noncanonical/mismatched keyword-role combinations cannot create authoritative provenance and that arbitrary source injection is not exposed. |
| Historical session safety | Tests seed a closed persistent-thread predecessor and prove CLI opening creates a distinct successor without rewriting the predecessor. |
| Governed writer attribution | Runtime/attribution tests resolve the exact returned successor to `prime-builder/codex` or `loyal-opposition/codex`; after WI-5256 lands, an end-to-end test proves ambient closed-predecessor selection reaches the sole current successor automatically. |
| Dispatcher isolation | Existing dispatcher-composed worker-session tests remain green and retain `dispatcher_composition` plus the exact dispatch run ID. |
| Exact implementation scope | Run focused pytest, Ruff lint/format, and exact five-path diff checks. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_kb_attribution.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_kb_attribution.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_kb_attribution.py
git diff --check -- <five authorized paths>
```

## Acceptance Criteria

- [ ] The public CLI creates complete writer-role provenance for canonical matching PB and LO interactive opens.
- [ ] Keyword/role mismatch, unsupported roles, and arbitrary role-source injection fail closed.
- [ ] Closed predecessors remain immutable and a distinct successor document is created.
- [ ] The exact returned successor resolves governed `changed_by` attribution without private API calls.
- [ ] Once WI-5256 is VERIFIED, subsequent writers automatically select the sole current successor without environment rebinding.
- [ ] Dispatcher-composed worker provenance and all role-free envelope behavior remain unchanged.
- [ ] Focused pytest, Ruff lint/format, and exact-path diff checks pass.
- [ ] Independent Loyal Opposition verification precedes a focused commit.

## Risks / Rollback

The main risk is granting document authority from an unvalidated CLI role assertion. Reusing the canonical init-keyword parser, requiring exact keyword/role agreement, and exposing no arbitrary role-source option contain that risk. A second risk is overwriting a closed persistent-thread document; preserving generated successor IDs and testing predecessor immutability prevents it. Rollback is a focused revert of the CLI integration and focused tests; session, WI, test, PAUTH, and bridge evidence remain append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` only if a shared validation helper is required
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_kb_attribution.py`

## Recommended Commit Type

`fix`
