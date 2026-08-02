NEW
::init gtkb pb
::open build


author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; desktop interactive; Prime Builder; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: transcript-defined role and current Codex desktop session

# GT-KB Bridge Implementation Report - gtkb-wi5580-session-envelope-collision-repair - 005

bridge_kind: implementation_report
Document: gtkb-wi5580-session-envelope-collision-repair
Version: 005
Responds to: bridge/gtkb-wi5580-session-envelope-collision-repair-004.md
Approved proposal: bridge/gtkb-wi5580-session-envelope-collision-repair-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5580
Linked Test: TEST-11627
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/collect_modernization_semantic_evidence.py", ".claude/hooks/workstream-focus.py", "platform_tests/scripts/test_collect_modernization_semantic_evidence.py", "platform_tests/scripts/test_kb_attribution_session_role.py", "platform_tests/hooks/test_workstream_focus.py"]
Recommended commit type: fix:

## Implementation Claim

WI-5580 is implemented on the approved six-path envelope. The shared session layer now resolves an acting harness document selector from unambiguous runtime-family markers or an explicit durable producer identity, while role authority continues to come only from validated `worker_role_provenance` in the selected exact-session envelope. Conflicting marker families, unknown producers, explicit/durable identity conflicts, and selected-envelope identity conflicts fail closed.

The modernization evidence collector passes the validated selector into the exact-document resolver, snapshots only that document, and emits a deterministic sorted list of ignored foreign same-session document paths. It never reads, deletes, closes, rewrites, or relocates those foreign documents. A narrow legacy path remains for an unambiguous single exact-session document when older direct callers provide no selector; same-session ambiguity still fails closed.

The Claude workstream-focus adapter is bound to durable harness `claude` / `B`. A foreign inherited `GTKB_HARNESS_NAME` or `GTKB_HARNESS_ID` causes a fail-soft refusal to persist, while the normal hook response continues. Valid Claude init input writes only the Claude exact-session document.

Start authority was created from current GO v004 and active list-free Assurance PAUTH v5. The persisted authorization packet is `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5580-session-envelope-collision-repair.json`, packet hash `sha256:e3a49dc6f851a8fe048762344a0d1345b1d26d0335d1c548740e92f3e4d64a7f`, with all six targets allowed at packet-create and implementation-start. No dispatcher/TAFE, role map, harness eligibility, credentials, Git index/history, release, deployment, or live envelope history was mutated.

This implementation report performs no KB or `groundtruth.db` mutation, write, insert, change, or edit.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

The owner-approved list-free Assurance PAUTH v5 applies through active project membership. No new owner decision is required for this implementation report. Independent verification and atomic finalization remain mandatory.

## Prior Deliberations

- `DELIB-202667714` - active Assurance project authorization v5 and retained bridge/claim/start/verification controls.
- `bridge/gtkb-wi5580-session-envelope-collision-repair-001.md` - approved proposal and TEST-11627-derived acceptance matrix.
- `bridge/gtkb-wi5580-session-envelope-collision-repair-004.md` - current independent GO.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Session-role and collector tests prove host data selects only a document, forged ambient role is ignored, and the selected document supplies the role: 29 passed across the applicable provenance/collector selection set. |
| `DCL-SESSION-ENVELOPE-DURABILITY-001` | Three-way Codex/Claude/Cursor collision test hashes all live fixture documents before and after resolution and proves byte identity; deterministic foreign paths are reported. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Hook suite 82 passed, 3 skipped; hard-invariant suite 4 passed; modernization harness parity 5 passed; no dispatcher/TAFE mutation occurred. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Executable tests cover conflicting markers, unknown producer, durable-id mismatch, selected-envelope mismatch, foreign immutability, Claude ownership, and legacy ambiguity. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Persisted packet records active project PAUTH v5 and `allowed: true` for all six targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Packet-create decision at `2026-08-01T08:53:45Z` and implementation-start decision at `2026-08-01T08:55:52Z` both report `reason_code: allowed`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Authorization packet `sha256:e3a49dc6f851a8fe048762344a0d1345b1d26d0335d1c548740e92f3e4d64a7f` binds GO v004, WI-5580, Assurance, and the exact six paths. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | Proposal, packet, and this report carry the complete linked-spec set and WI-5580 / TEST-11627 linkage. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Claim acquired before writes; implementation-start packet finalized before the first protected edit; claim extended while verification/reporting continued. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This NEW v005 implementation report responds to current LO-authored GO v004 and requests independent verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project, PAUTH, WI, approved proposal, GO, and linked test are explicit above. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All proposal-linked specifications are carried forward without omission. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact commands and observed pass/fail evidence are recorded below, including non-WI baseline failures rather than hiding them. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Six paths only; final hashes and `313 insertions, 13 deletions` diff stat are recorded below; no whole-tree attribution is claimed. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Current target diff contains only WI-5580 additions against HEAD; the proposal's WI-5396 baseline bytes are already in HEAD and remain unchanged. No overlapping active exact-path claim was introduced. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation is carried by WI-5580, TEST-11627, authorization packet, source/tests, and this append-only report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation completion is filed as NEW and remains nonterminal until independent VERIFIED. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Governed bridge, project authorization, claim, packet, exact tests, and immutable report evidence control the lifecycle. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/hooks/test_workstream_focus.py -q --tb=short --timeout=300`
- `python -m pytest platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --timeout=300 -k "not live_program_reconciliation_is_executable_and_duplicate_free and not pre_modernization_baseline_binds_historical_observations_and_explicit_gaps"`
- `python -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short --timeout=300 -k "not mod_ad09_proves_query_quarantine_and_no_historical_worker_dependency"`
- `python -m pytest platform_tests/scripts/test_modernization_hard_invariants.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_modernization_harness_parity.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=300 -k "not fresh_worker_bootstraps_from_only_copied_product_assets"`
- `python -m pytest platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --timeout=300 -k "not live_program_reconciliation_is_executable_and_duplicate_free and not pre_modernization_baseline_binds_historical_observations_and_explicit_gaps"`
- `python -m ruff check <the six approved paths>`
- `python -m ruff format --check <the six approved paths>`
- `python -m py_compile groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/collect_modernization_semantic_evidence.py .claude/hooks/workstream-focus.py`
- `git diff --check -- <the six approved paths>`

## Observed Results

- Provenance plus hook: `89 passed, 3 skipped`.
- Collector applicable set before the final identity-mismatch addition: `21 passed, 2 deselected`; final provenance plus collector applicable set after that addition: `29 passed, 2 deselected` (7 provenance + 22 collector).
- Scope semantics applicable set: `14 passed, 1 deselected`.
- Hard invariants: `4 passed`.
- Harness parity: `5 passed`.
- Fresh-worker applicable set: `3 passed, 1 deselected`.
- Ruff check: all checks passed. Ruff format check: six files formatted. Python compile and diff check: pass.
- Full collector suite remains `2 failed, 21 passed` on live-state prerequisites unrelated to WI-5580: duplicated modernization memberships for WI-5541/WI-5580/WI-5086 and the absent historical corpus manifest.
- Full scope-semantic suite reaches `14 passed` but the remaining history-quarantine test fails on the hard-coded registry lock deadline at `.gtkb-state/sot-registry/control-plane.lock`, including after Pytest's test cap was raised to 300 seconds.
- Full fresh-worker suite reaches `3 passed`; its existing fresh-host bootstrap isolation assertion remains red and is outside these six paths.
- The initial parallel broad run also demonstrated the arbitrary global 30-second Pytest cap terminating registry-lock and subprocess-reader work. This evidence is being carried into a separate timer/concurrency configuration WI per owner direction.

## Files Changed

- `.claude/hooks/workstream-focus.py` - SHA-256 `658A50138C83FB0A09BFCBCF5A9E8D17FE46773FAB538E37DD6004DCB9CD915B`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` - SHA-256 `BB026C2B1B05214B29438BED4076B9DE3EF6FF228B293AF8C6D88814B7A2BE12`
- `platform_tests/hooks/test_workstream_focus.py` - SHA-256 `296F3467D105C021234BCE3B1E3E9022117C78FACBB9F05B6E8FEFB00AC191D6`
- `platform_tests/scripts/test_collect_modernization_semantic_evidence.py` - SHA-256 `BC64B9E8007684D816DC9539B2ED31120C89597156D275C47847A6DC5E682DA9`
- `platform_tests/scripts/test_kb_attribution_session_role.py` - SHA-256 `8AA493A6A0030992D6BB4F14745CE30A3A314DD6AAC234443EC88945DE2A373B`
- `scripts/collect_modernization_semantic_evidence.py` - SHA-256 `4A1DA95C3B168FD4D6BCE0E2F5E5504A6B40BA3DBC61AFB4E96071255F7EB2AB`

Excluded out-of-scope dirty paths remain excluded. No excluded path is attributed to WI-5580.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: a collision blocker and foreign-producer write risk are repaired with exact regression coverage.

```text
6 files changed, 313 insertions(+), 13 deletions(-)
```

## Acceptance Criteria Status

- [x] Acting Codex resolves and snapshots its valid exact document despite simultaneous Claude and Cursor documents.
- [x] Role authority remains exclusively document-derived; forged ambient role values do not change it.
- [x] Conflicting marker families, unknown explicit producers, and explicit/durable identity contradictions fail closed before evidence mutation.
- [x] Foreign exact-session documents remain byte-identical and appear only as deterministic in-root collision diagnostics.
- [x] Missing, malformed, stale, conflicting-provenance, and durable-identity-mismatched selected documents fail closed.
- [x] Claude cannot persist into a foreign harness directory; valid Claude init persists only to durable `claude` / `B` state.
- [x] All WI-5580-applicable collector/provenance tests pass; downstream non-WI live-state blockers remain independently visible.
- [x] Dispatcher/TAFE, roles, eligibility, routing, credentials, Git index/history, release, deployment, and live envelope history are unchanged.
- [x] The approved six paths are isolated; no unrelated dirty path or pre-existing HEAD byte is absorbed.

## Risk And Rollback

Residual risk is limited to runtime families without a native host marker: those producers must pass both durable harness name and id, and the selector validates both. The backward-compatible no-selector path accepts only one unambiguous exact-session document; collisions still hard-fail. Rollback must be a governed successor that reverses only the WI-5580 hunks in these six paths. Existing session-envelope history and foreign collision documents must not be rewritten as rollback.

## Loyal Opposition Asks

1. Verify the implementation against every linked specification and TEST-11627-derived command above.
2. Confirm foreign collision documents and dispatcher/TAFE state remained immutable.
3. Return VERIFIED only if exact reviewed hunks can be finalized without absorbing unrelated worktree changes; otherwise return NO-GO with findings.
