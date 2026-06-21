NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Fix stale assertion regex in test_non_go_bridge_entry_cannot_create_authorization

bridge_kind: prime_proposal
Document: gtkb-fix-stale-assertion-regex-non-go-bridge-test
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3361

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

`test_non_go_bridge_entry_cannot_create_authorization` (in `platform_tests/scripts/test_implementation_start_gate.py:404`) asserts `pytest.raises(auth.AuthorizationError, match="latest GO")`. The error raised by `approved_files_for_go` in `scripts/implementation_authorization.py` (the no-GO-in-chain branch, lines 388-393) is the *stable contract* for "a non-GO thread cannot mint an authorization", but its wording has churned across commits. The test couples to the incidental phrase `"latest GO"` rather than the stable phrase `"requires a GO in the bridge chain"`, making the assertion fragile: a message reword that preserves the contract but drops the incidental phrase silently reds the test (and the inverse silently masks it). The fix realigns the assertion to the stable contract substring so it tracks the error contract, not incidental wording.

## Defect / Reproduction

Commit-trace establishing the defect and its current latent state:

1. Pre-`e39627a1`: the no-GO branch raised `"Implementation authorization requires latest GO; found {status}"` - contained `"latest GO"`; the `match="latest GO"` assertion passed.
2. Commit `e39627a1` (WI-3353, worktree-aware root resolution) reworded the message to `"...requires a GO in the bridge chain; found latest status {status}"`. That wording does NOT contain the substring `"latest GO"` (it contains `"latest status"`). The `re.search("latest GO", msg)` assertion went red on develop, with no matching test change - exactly the regression WI-3361 records. Surfaced during WI-3357 post-implementation verification and waived for that thread via `DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER`.
3. Commit `a223c713` ("settle uncommitted bridge-infrastructure modifications") re-added a middle line `"latest GO or resumable post-GO NO-GO is required; "`, which re-introduced the `"latest GO"` substring. The current committed message (lines 390-392) is `"Implementation authorization requires a GO in the bridge chain; latest GO or resumable post-GO NO-GO is required; found latest status {status}"`, so `re.search("latest GO", ...)` currently matches and the test is GREEN at HEAD again - but only by coincidence of the middle line's wording.

Net state: the original red has been *incidentally* re-greened, but the underlying defect - a stale/incidental-coupling assertion regex - remains. The assertion still does not track the stable error contract; any future reword that keeps the contract but rephrases the "latest GO" clause re-reds the test for no behavioral reason. This proposal removes that latent fragility (the defect class WI-3361 names) rather than leaving a brittle green.

Reproduction (logical): with the test's helper `_write_thread(tmp_path, latest_status="REVISED")` (no GO version in the chain), `auth.create_authorization_packet` -> `approved_files_for_go` hits the `go_index is None` branch and raises `AuthorizationError`. The behavior is correct; only the assertion's match string is fragile. Demonstration of the fragility: reverting line 391 (the `"latest GO or resumable..."` line) - a wording-only change that preserves the contract - re-reds the test, proving the assertion is coupled to incidental wording, not the contract.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_start_gate.py`. The change is confined to the GT-KB platform authorization module and its platform test; no application/adopter surface is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the no-GO-in-chain rejection enforces that implementation authorization requires a bridge GO; the test guards that authority boundary, so its assertion must track the stable rejection contract, not incidental wording.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the test is a durable verification artifact; aligning its assertion to the stable error contract keeps the artifact meaningful and resistant to incidental drift.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing/cross-cutting specs that constrain the change (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives the corrected test assertion from the cited bridge-authority contract (mandatory spec-derived testing).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-1662` - GOV-18 assertion-quality standard (meaningfulness over coverage): an assertion coupled to incidental wording is a quality defect; realigning to the stable contract substring raises assertion meaningfulness exactly as this spec requires.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change stays within the platform (`scripts/...`, `platform_tests/...`); no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3361 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the verification contract remains artifact-backed (the source error string is the artifact the test tracks) rather than coupled to a transient phrase.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - no new formal artifact is created; the change is a defect fix to an existing test plus the source error-string anchor, so no formalization gate is triggered.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the test under the specify-on-contact / lifecycle-trigger discipline brings the assertion's quality up to standard; no new spec promotion is triggered (existing requirements cover it).

## Prior Deliberations

- `DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER` - owner waiver for the pre-existing `test_non_go_bridge_entry_cannot_create_authorization` failure during W4 (WI-3357) post-implementation verification. Direct corroboration: this is the same test, waived as red after `e39627a1`; this proposal removes the latent fragility so no future waiver is needed for the same incidental-coupling cause.
- `DELIB-20263073` - Loyal Opposition verification verdict for `gtkb-path-token-re-discovery-consolidation` (a sibling implementation-gate/authorization-area thread); relevant precedent for how assertion-string verification was handled in this module's test surface.
- `DELIB-20263755` - Loyal Opposition review, WI-3372 KB-Mutation target_paths closure; relevant as prior target_paths-discipline precedent for authorization-area proposals.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3361 is in scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing authorization via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3361 is origin=defect, single-concern, introduces no new public API/CLI/behavior, no new/revised requirement or spec, and is bounded to one test file (plus a documented source error-string anchor), well under the reliability fast-lane size guide; it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3361 (P3, defect) is in that batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction that established PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; authorizes small, single-concern, no-new-surface defect fixes like this one to proceed under the fast lane.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge GO is the authoritative precondition for implementation authorization) and `SPEC-1662` (GOV-18 assertion-quality standard - meaningfulness over coverage) already establish both the contract the test must guard and the standard the assertion must meet. This fix realigns the test assertion to the stable contract substring; it introduces no new or revised requirement/specification.

## Proposed Scope

Minimal, single-concern, test-realignment defect fix:

1. `platform_tests/scripts/test_implementation_start_gate.py` (primary change): in `test_non_go_bridge_entry_cannot_create_authorization` (line 404), change the assertion match string from the incidental `"latest GO"` to the stable contract substring `"requires a GO in the bridge chain"`, which is the invariant clause of the no-GO-in-chain `AuthorizationError` and is robust to the message's optional "latest GO or resumable post-GO NO-GO" clause. The assertion intent (a non-GO/REVISED-latest thread cannot mint an authorization) is preserved.
2. `scripts/implementation_authorization.py` (anchor guarantee, no behavior change): treat the leading clause `"Implementation authorization requires a GO in the bridge chain"` of the `go_index is None` `AuthorizationError` (lines 389-393) as the canonical stable error anchor that the test tracks. The current message already contains that clause; this proposal makes it explicit (a brief code comment marking the clause as the test-tracked stable contract) so a future reword does not silently drop the anchor. No raise condition, no control flow, and no user-facing behavior changes; the message text's leading clause is preserved verbatim.

The WI's named target is the test assertion; the source file is included so the proposal documents and protects the error-contract anchor the test depends on. No production behavior changes.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no-GO thread cannot mint authorization) | `test_non_go_bridge_entry_cannot_create_authorization` (realigned) | A REVISED-latest thread (no GO in chain) raises `AuthorizationError` whose message matches the stable substring `"requires a GO in the bridge chain"`. |
| `SPEC-1662` (GOV-18: assertion meaningfulness over incidental coupling) | `test_non_go_bridge_entry_cannot_create_authorization` (realigned) | The assertion match string is the stable contract clause, not the optional "latest GO" wording; the test passes against the current message AND remains green if the "latest GO or resumable..." line is reworded (anti-fragility verified by inspection of the leading clause). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (derived coverage executes) | full `test_implementation_start_gate.py` module | The whole authorization-gate test module passes (no collateral regression from the assertion change or the source comment anchor). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
- `python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py`
- `python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py`

## Acceptance Criteria

1. `test_non_go_bridge_entry_cannot_create_authorization` asserts on the stable substring `"requires a GO in the bridge chain"` (not `"latest GO"`) and passes.
2. The leading clause `"Implementation authorization requires a GO in the bridge chain"` is preserved verbatim in `approved_files_for_go`'s no-GO-in-chain `AuthorizationError`, marked as the test-tracked stable anchor; no raise condition or behavior changes.
3. The full `platform_tests/scripts/test_implementation_start_gate.py` module passes; `ruff check` and `ruff format --check` are clean on both changed files.

## Risks / Rollback

- Risk: matching on a longer/stable substring could mask a genuinely-different future error reaching this assertion. Mitigation: the chosen substring is the invariant leading clause of exactly this no-GO-in-chain branch; the helper `_write_thread(latest_status="REVISED")` guarantees that branch is the one exercised, so the assertion remains specific to the intended path.
- Risk: editing the source error string region could inadvertently alter the message. Mitigation: the source change is a comment-only anchor note; the message text's leading clause is preserved verbatim and covered by acceptance criterion 2; no control-flow change.
- Rollback: revert the one-line assertion change in the test (and the source comment note); the change is purely test-realignment plus an annotation, fully reversible with no migration.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
