NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - INDEX pruning strands un-implemented GO bridge threads

bridge_kind: prime_proposal
Document: gtkb-index-pruning-strands-unimplemented-go-threads
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4283

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py", "platform_tests/scripts/test_versioned_files_archival_invariant.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The defect WI-4283 originally describes (the `bridge/INDEX.md` maintenance routine dropping entries whose latest status was a non-terminal GO, stranding Loyal-Opposition-approved-but-unimplemented work) was structurally eliminated by the WI-4510 Phase-3 no-index cutover (2026-06-15): `bridge/INDEX.md` no longer exists, `scripts/bridge_index_writer.py` no longer exists, and bridge state is now derived fresh from versioned files on every read. The live successor surface that carries the same "which threads may be excluded from the actionable queue" decision is `groundtruth_kb.bridge.versioned_files._classify_candidate` / `candidate_is_archived`, consumed by `scripts/cross_harness_bridge_trigger.py::_render_bridge_state_text` (line 1891: `if candidate_is_archived(...): continue`) and by the Claude/Codex `scan_bridge.py` helpers. That successor already encodes the correct invariant (only terminal status tokens -> "archived"/excluded; non-terminal NEW/REVISED/GO/NO-GO -> "lost"/preserved), but the invariant is UNTESTED, and `_classify_candidate`'s fallthrough branch (scan-all-lines-for-any-terminal-token) can mis-classify a non-terminal thread as archived when its latest file body merely mentions a terminal word (e.g., a GO/NO-GO verdict whose prose references "VERIFIED"). This is a latent re-introduction of the WI-4283 defect class. The minimal defect fix is to (a) tighten `_classify_candidate` so archival is decided strictly from the first canonical status token (the body status-token rule), never from incidental prose, and (b) lock the non-terminal-preservation invariant with a regression test.

## Defect / Reproduction

Original incident (origin of WI-4283): a scan on 2026-06-03 found 13 threads whose latest status was GO absent from the then-1471-line `bridge/INDEX.md`; at least 3 were genuinely-unimplemented 2026-06-01 reliability fixes (WI-3413 dashboard launcher, WI-3469 pytest basetemp, plus WI-3482 git-hooks-path-lint and WI-3493 bash-hook-destructive). The INDEX "prune oldest when >~200 lines" maintenance dropped non-terminal GO entries, stranding approved work.

Current-era reproduction (logical, against the live successor surface): the original INDEX prune routine is gone (confirmed: `bridge/INDEX.md`, `scripts/bridge_index_writer.py`, and a live `groundtruth_kb/bridge/index_mutation.py` are all absent from the tree). The remaining exclusion decision lives in `_classify_candidate`. Construct a bridge thread whose latest version file's first canonical status token is non-terminal (GO) but whose body prose contains a terminal word such as "VERIFIED" (common in GO verdicts that say "ready to proceed to VERIFIED" or cite a sibling's VERIFIED status). When the first-token parse is bypassed by the fallthrough scan (lines 69-72 of `versioned_files.py`), `_classify_candidate` returns "archived", `candidate_is_archived` returns True, and `_render_bridge_state_text` `continue`s past the slug — silently dropping a non-terminal GO thread from the dispatchable/actionable bridge state. Expected: a thread whose latest status token is non-terminal is NEVER auto-archived; only an explicit terminal first-token or an owner-acknowledged slug (`config/governance/tafe-acknowledged-archived-bridges.toml`) is archived.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`, `platform_tests/scripts/test_versioned_files_archival_invariant.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `VERIFIED` (and the other terminal tokens) are the authoritative terminal signals; the exclusion/archival decision must read those signals and must not exclude a thread whose latest signal is non-terminal, which is exactly the invariant this fix protects.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - bridge threads are durable audit artifacts; silently excluding a non-terminal GO thread from the actionable queue erases a live artifact from the working set, contrary to artifact-oriented governance.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage gate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives every test from the cited specs/clauses (mandatory spec-derived testing gate).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries the Project Authorization / Project / Work Item linkage lines (mandatory project-linkage gate).
- `SPEC-AUQ-POLICY-ENGINE-001` - not directly applicable: this fix is confined to the deterministic bridge-state derivation surface and introduces no owner-decision/AUQ policy surface; cited per scaffold-seed completeness and confirmed out of behavioral scope (no AUQ path is added, changed, or bypassed).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform bridge module (`groundtruth-kb/src/...`) and platform tests; no application/adopter surface is touched and no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4283 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES, surfaced via the canonical `work_items` authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - parity-relevant: the successor surface is consumed identically by both `.claude/skills/bridge/helpers/scan_bridge.py` and `.codex/skills/bridge/helpers/scan_bridge.py`; the fix lives in the shared `groundtruth_kb.bridge.versioned_files` module so both harness surfaces inherit the corrected invariant with no per-harness divergence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the exclusion decision remains artifact-backed (the bridge file's first canonical status token), not inferred from incidental prose; this fix removes the prose-inference path.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the archive/exclude trigger with the bridge thread's actual terminal lifecycle state rather than a false-positive text match.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes terminal bridge statuses as the authoritative signals that govern thread lifecycle, and the file-bridge protocol's Body Status-Token Rule already mandates that a versioned bridge file's first non-blank line is its canonical status token. This fix enforces those existing contracts at the `_classify_candidate` archival boundary; no new or revised requirement/specification is introduced.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`, tighten `_classify_candidate(latest_file_text)` so the archival classification derives strictly from the FIRST canonical status token of the latest file (the Body Status-Token Rule), removing the prose-inference fallthrough:
   - If the first canonical status token is in `_TERMINAL_STATUS_TOKENS` -> return `"archived"`.
   - If the first canonical status token is in `_NON_TERMINAL_STATUS_TOKENS` -> return `"lost"` (preserved/surfaced).
   - If no canonical first-token is found (malformed/unrecognized leading line) -> return `"lost"` (fail-safe: never silently archive a thread we cannot positively classify as terminal). This replaces the current lines 69-72 scan-all-lines-for-any-terminal-token branch that can match terminal words in prose.
   - Behavior for the explicit owner-acknowledged path (`candidate_is_archived` -> `load_acknowledged_archived_slugs` / `tafe-acknowledged-archived-bridges.toml`) and the `-implementation` sibling path is preserved unchanged; only the prose-inference branch is removed.
2. Add a new regression test file `platform_tests/scripts/test_versioned_files_archival_invariant.py` (see verification plan) that locks the non-terminal-preservation invariant on the live successor surface.

This is the defect-removal path for the WI-4283 defect class as it exists in the post-cutover codebase. The WI's secondary asks (recover/triage the historically-stranded GOs WI-3482/WI-3493 and reconcile the other superseded-vs-stranded threads) are bridge/backlog reconciliation operations, not a code defect, and are out of scope for this fast-lane code fix; they are tracked separately under the bridge-reconciliation workflow and WI-4235 (bridge INDEX/file-chain deviation detection).

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (non-terminal latest status is authoritative and preserved) | `test_non_terminal_first_token_never_archived` | For each non-terminal first-token in {NEW, REVISED, GO, NO-GO}, `candidate_is_archived(slug, ...)` returns False (thread preserved), parametrized over all four tokens. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (archival decided from the status token, not prose) | `test_go_thread_with_verified_prose_not_archived` | A thread whose latest file first line is `GO` but whose body prose contains the word "VERIFIED" is classified "lost" (not archived); reproduces the fallthrough defect and asserts the fix. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (terminal first-token triggers archival) | `test_terminal_first_token_archived` | For each terminal first-token in {VERIFIED, WITHDRAWN, DEFERRED, ADVISORY, ACCEPTED}, `candidate_is_archived` returns True (no regression to the legitimate archive path). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (owner-acknowledged archival preserved) | `test_owner_acknowledged_slug_archived` | A non-terminal thread whose slug is listed in `tafe-acknowledged-archived-bridges.toml` is archived (explicit owner-acknowledged path unchanged). |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (malformed leading line fails safe) | `test_unrecognized_first_token_not_archived` | A thread whose latest file has no canonical status token on its first non-blank line is classified "lost" (fail-safe: never silently archived). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_versioned_files_archival_invariant.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py platform_tests/scripts/test_versioned_files_archival_invariant.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py platform_tests/scripts/test_versioned_files_archival_invariant.py`

## Acceptance Criteria

1. `_classify_candidate` returns `"archived"` only when the latest file's FIRST canonical status token is terminal; a non-terminal first token always yields `"lost"` (preserved).
2. A GO/NO-GO/NEW/REVISED thread whose body prose merely mentions a terminal word (e.g., "VERIFIED") is NOT archived (the original WI-4283 strand-the-GO defect class cannot recur on the successor surface).
3. The legitimate archival paths are unchanged: a terminal first-token archives, and an owner-acknowledged slug (`tafe-acknowledged-archived-bridges.toml`) archives.
4. All derived tests pass; `ruff check` and `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: removing the prose-inference fallthrough could fail to auto-archive a legacy thread whose latest file has a non-canonical first line but a terminal token later in the body. Mitigation: such threads fall to "lost" (surfaced as a deviation) rather than being silently dropped — the conservative/correct posture for this defect; the owner-acknowledged-slug path remains available to explicitly archive any such legacy thread.
- Risk: a thread legitimately needing archival is now surfaced as "lost". Mitigation: this is by design (surfacing > silent dropping); the owner-acknowledged path is the sanctioned archive mechanism and is untouched.
- Rollback: revert the `_classify_candidate` change in `versioned_files.py` and remove the new test file. The change is a single function body plus an additive test file, fully reversible with no migration and no data/state changes.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`
- `platform_tests/scripts/test_versioned_files_archival_invariant.py`

## Prior Deliberations

- `DELIB-20263775` - Loyal Opposition Review - bridge/INDEX.md Archival Trim Revision 2 - directly on-topic: this is the original INDEX archival-trim review thread whose mechanism produced the WI-4283 strand-the-GO incident; the fix migrates that archival invariant to the post-cutover successor surface.
- `DELIB-20263860` - Loyal Opposition Verification - Bridge VERIFIED Backlog Retirement - 010 - establishes that VERIFIED is the terminal retirement signal driving thread removal; this fix keeps terminal-token archival as the only archival trigger.
- `DELIB-2734` / `DELIB-20264014` - Loyal Opposition Review - Deterministic Services Stale Status Reconciliation - prior reconciliation of stale bridge statuses; relevant precedent for deriving thread lifecycle state deterministically from the status token rather than inference.
- `DELIB-20263654` - Loyal Opposition Review - Antigravity related_bridge_threads Backfill REVISED-1 (WI-3362) - related bridge-thread state-derivation work; cited per scaffold seed, tangential to this fix's `_classify_candidate` scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing reliability fast-lane authorization, `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4283 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, introduces no new/revised requirement or spec, and is bounded to 1 source file + 1 new test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (pipeline-repair and P1/P2 first); WI-4283 is P2 and in scope for this batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction (via PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) that authorizes bounded, single-concern reliability defect fixes to proceed through the bridge protocol without a fresh per-item owner approval.

## Recommended Commit Type

`fix`
