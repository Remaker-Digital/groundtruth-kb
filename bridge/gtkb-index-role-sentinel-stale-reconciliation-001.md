NEW

# Reconcile Stale bridge/INDEX.md Role Sentinel and Clear 9 Parse Errors via Generator Regeneration (WI-3488)

bridge_kind: implementation_proposal
Document: gtkb-index-role-sentinel-stale-reconciliation
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3488
Project Authorization: PAUTH-WI-3488-INDEX-ROLE-SENTINEL-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3488
target_paths: ["scripts/check_index_role_intent_sentinel.py", ".claude/hooks/session_start_dispatch.py", "bridge/INDEX.md", "platform_tests/scripts/test_index_role_intent_sentinel.py", "groundtruth-kb/tests/test_bridge_detector.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

`bridge/INDEX.md` carries a stale, orphaned role-intent sentinel that contradicts the durable role map, and the live bridge index parser reports exactly **9 parse errors** as a direct consequence of two distinct INDEX malformations. WI-3488 records this verbatim: its title is `bridge/INDEX.md has 9 parse errors incl. stale role sentinel claiming Codex-as-Prime/prime_only (2026-05-20)` (`origin=defect`, `priority=P2`, `resolution_status=open`, confirmed live in the `work_items` table).

Evidence — the live parser count is reproducible and equals nine:

- `groundtruth_kb.bridge.status_driver.collect_bridge_status(Path('E:/GT-KB'))` returns `queue.parse_error_count == 9` (and `parse_warning_count == 1`). The parser is `groundtruth_kb.bridge.detector.parse_index` (`groundtruth-kb/src/groundtruth_kb/bridge/detector.py:106`); `parse_error_count` is surfaced at `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py:185` and folds into `dispatchable_counts["unknown_or_malformed"]` at `status_driver.py:155`. `operating_state.py:236` raises a WARN whenever `queue.parse_error_count` is nonzero, so this defect degrades bridge-health reporting on every status read.

The nine errors decompose into two malformation classes:

- **Class A — orphaned sentinel fragment (7 errors, INDEX lines 484-490).** `bridge/INDEX.md` contains the sentinel *tail* — `Authority:` (484), `This sentinel is a checksum mirror only…` (485), `Prime Builder harness:    A (Codex)` (486), `Loyal Opposition harness: none` (487), `Topology:                 prime_only` (488), `Sentinel updated:         2026-05-20T01:14:29Z` (489), and the closing `-->` (490) — but the opening `<!-- Role-intent sentinel (per GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL, Slice 1; NON-AUTHORITATIVE):` line is **missing**. Because the opener is gone, the parser never enters `comment_block` state (`detector.py:162`), the leading-whitespace tail lines do not match `_SINGLE_LINE_COMMENT_RE = ^\s*<!--.*-->\s*$` (`detector.py:42`), and each line falls through to `ParseError(expected_state="document_or_blank")` at `detector.py:255`. The orphaned fragment sits in body state between the `gtkb-worker-packet-auth-envelope-slice-2-auto-packet` entry and the `gtkb-bridge-target-paths-kb-mutation-check` entry.

- **Class B — version-less status lines (2 errors, INDEX lines 876 and 881).** `NEW: bridge/gtkb-commit-scope-bundling-detection-001-prop.md` (876) and `NEW: bridge/gtkb-auto-push-investigation-001-prop.md` (881) lack the `-NNN` version suffix that `_STATUS_LINE_RE` requires (`bridge/(?P<name>…)-(?P<version>\d+)\.md`, `detector.py:36-39`). Each has a valid `Document:` line and parseable `-002.md`/`-003.md`/`WITHDRAWN` siblings, but the version-less first line yields `ParseError(expected_state="status_line")` at `detector.py:245`.

The **live role-map contradiction** is direct and load-bearing: `harness-state/role-assignments.json` currently records `A=codex=["loyal-opposition"]`, `B=claude=["prime-builder"]`, `C=antigravity=["prime-builder"]`. The sentinel's `Prime Builder harness: A (Codex)` / `Loyal Opposition harness: none` / `Topology: prime_only` is the exact inverse of durable truth: Codex (A) is now Loyal Opposition, not Prime; and the topology is not `prime_only` (two harnesses hold `prime-builder`). The sentinel is explicitly a checksum mirror — `render_sentinel` stamps "This sentinel is a checksum mirror only. It MUST NOT be used to override the durable role record." (`scripts/check_index_role_intent_sentinel.py:163-165`) — so a mirror that has gone stale and inverted is a reliability defect, not an authority question.

Root cause of staleness: the sentinel's only writer is `check_index_role_intent_sentinel.py --update` (`scripts/check_index_role_intent_sentinel.py:351-354`), and that command is **not wired into any hook or `.claude/settings.json` registration** (a repo-wide search finds the checker referenced only by itself and its archive). It was last run 2026-05-20 (the stamped timestamp), before the role map changed. The serialized canonical INDEX writer `scripts/bridge_index_writer.py` (WI-3374) has zero sentinel awareness, so ordinary INDEX churn neither preserves nor refreshes the block — which is how the opener was lost and the mirror drifted.

This proposal makes the **generator** keep the sentinel a faithful, self-healing mirror (an orphaned-tail-tolerant replace plus a SessionStart auto-regenerate invocation), performs a one-time correction of the live INDEX (the orphaned sentinel and the two version-less status lines), and adds regression tests so the 9-error condition cannot silently recur. The fix never makes the sentinel an authority.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 (v1) — `bridge/INDEX.md` is the canonical bridge workflow state. A 9-parse-error INDEX with an inverted role mirror degrades the canonical surface and its health reporting; restoring a clean, parseable INDEX with a faithful non-authoritative mirror is compliance with this authority. This is the WI-3488 governing specification.
- GOV-SESSION-ROLE-AUTHORITY-001 (v1) — establishes that durable role authority is `harness-state/role-assignments.json` and that derived/generated surfaces must not override it. The fix keeps the sentinel a derived mirror of that authority and regenerates it from the live role map, never inverting the authority split.
- DCL-SESSION-ROLE-RESOLUTION-001 (v1) — the deterministic role-resolution table keyed to the durable role map; the regenerated sentinel must reflect the same durable source this DCL resolves from, so the mirror and the resolver agree.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 (v2) — role assertions emitted across surfaces must agree with the durable role assertion; a sentinel that contradicts the role map violates this consistency expectation, which the regeneration repairs.
- GOV-HARNESS-ROLE-PORTABILITY-001 (v1) — roles attach to durable harness IDs; the regenerated mirror resolves Prime/Loyal/topology from the durable identity+role maps via the existing `build_role_intent_state` (`check_index_role_intent_sentinel.py:104`).
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 (v1) — all touched paths are in-root under `E:\GT-KB`; the clause-in-root constraint is satisfied.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (v1) — the WI, this bridge thread, and the linked specs/tests form the durable artifact graph for the fix (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (v1) — traceability across the work item, proposal, and spec-derived tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (v1) — the defect drives the work item through its lifecycle toward verified (advisory).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (v1) — this proposal cites every relevant governing specification, and the Spec-To-Test Mapping shows how the proposed tests derive from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (v1) — verification is derived from the linked specifications and executed against the implementation; the post-implementation report will carry the mapping, the exact commands, and the observed results.

## Authorization

This work is authorized by the dedicated standard project authorization `PAUTH-WI-3488-INDEX-ROLE-SENTINEL-001` (project `PROJECT-GTKB-RELIABILITY-FIXES`; owner decision `DELIB-2548`; owner-approved via AskUserQuestion in S381). The authorization's `allowed_mutation_classes` are `["source", "test_addition", "hook_upgrade"]`, which cover every change in this proposal:

- `source` — the orphaned-tail-tolerant replace in `scripts/check_index_role_intent_sentinel.py`, and the one-time `bridge/INDEX.md` corrections.
- `hook_upgrade` — adding a best-effort sentinel-regenerate invocation to the existing `.claude/hooks/session_start_dispatch.py` SessionStart hook.
- `test_addition` — the regression tests under `platform_tests/scripts/` and `groundtruth-kb/tests/`.

The authorization forbids `deploy`, `git_push_force`, and `spec_deletion`; this proposal performs none of those (no deployment, no force-push, no spec deletion). This is a **standard project authorization**, not the reliability fast-lane: no `GOV-RELIABILITY-FAST-LANE-001` eligibility is claimed, and no fast-lane criteria are invoked. The authorization satisfies the owner-approval evidence for the implementation scope; it is additive to the bridge gate - implementation proceeds only after Loyal Opposition records `GO` on this proposal and the implementation-start packet is created from that GO per `.claude/rules/codex-review-gate.md`.

## Prior Deliberations

- `bridge/gtkb-bridge-index-role-intent-sentinel-001.md` … `-006.md` — the thread that *built* the Slice-1 sentinel checker. Its latest status is **NO-GO** at `-006` (Codex-as-Prime Slice-1 implementation report `-005` was not verified because the live sentinel block was already orphaned/missing). That thread's scope is the checker's own construction and its NO-GO awaits a Codex-Prime REVISED of *its own implementation report*; it never addresses the 9-parse-error condition and never mentions the Class-B version-less status lines (876/881), which are unrelated to the sentinel. WI-3488 is a distinct, Claude-authored reliability work item with its own dedicated authorization, targeting the live parse-error symptom and the generator that lets the mirror drift. This proposal builds on, and does not duplicate, the `-006` F1 finding (which independently observed the stale `A (Codex)` / `prime_only` fragment and recommended Prime repair the block and rerun the checker).
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` — the originating owner directive establishing the non-authoritative checksum sentinel; this proposal preserves the "mirror only, never authority" contract.
- `DELIB-2548` — the owner decision (S381 AskUserQuestion) authorizing WI-3488 under `PAUTH-WI-3488-INDEX-ROLE-SENTINEL-001`.

## Owner Decisions / Input

- 2026-05-31/S381: via AskUserQuestion the owner approved authorizing implementation of WI-3488, recorded as owner decision `DELIB-2548`. The authorization envelope is `PAUTH-WI-3488-INDEX-ROLE-SENTINEL-001` (project `PROJECT-GTKB-RELIABILITY-FIXES`; `allowed_mutation_classes = ["source", "test_addition", "hook_upgrade"]`; forbids deploy / git_push_force / spec_deletion).
- No further owner decision is required before GO. The authorization covers the implementation scope; no formal-artifact-approval packet is needed because this proposal creates and mutates no formal GOV/SPEC/PB/ADR/DCL artifact.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already requires `bridge/INDEX.md` to be the clean canonical bridge state, and GOV-SESSION-ROLE-AUTHORITY-001 + DCL-SESSION-ROLE-RESOLUTION-001 already establish the durable role map as authority and derived surfaces as non-overriding mirrors. The 9 parse errors and the inverted sentinel are non-compliance with those existing requirements; no new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to one checker script, one SessionStart hook, a one-time correction of the live `bridge/INDEX.md`, and regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3488) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Make the sentinel a self-healing mirror (the generator fix)

Two complementary changes so the sentinel cannot silently go stale or orphaned again:

1. **Orphaned-tail-tolerant replace in `scripts/check_index_role_intent_sentinel.py`.** `insert_or_replace_sentinel` (`check_index_role_intent_sentinel.py:270`) currently relies on `SENTINEL_RE` (`:26`) matching a *well-formed* block (opening `<!-- Role-intent sentinel … :` through closing `-->`). When the opener is lost, `sentinel_bounds` returns `None`, so `--update` inserts a *second* block before the first `Document:` line and leaves the dangling tail in place — it cannot self-repair the exact failure mode now present. Extend the detection so a dangling sentinel tail (the `Authority:` / `Prime Builder harness:` / `Loyal Opposition harness:` / `Topology:` / `Sentinel updated:` field run ending in a bare `-->`, with no matching `<!--` opener) is recognized and replaced in place by a freshly rendered, well-formed block. The replacement is generated by the existing `render_sentinel(state_from_files(root))` path, so it always reflects the live durable role map and stays non-authoritative. No new authority, no new field, no schema change.

2. **Auto-regenerate at SessionStart (`hook_upgrade`).** Add a single best-effort, fail-soft invocation of `check_index_role_intent_sentinel.py --update` to the existing SessionStart hook `.claude/hooks/session_start_dispatch.py`, so every fresh session re-stamps the sentinel from the live role map. This closes the "no invocation site" gap that let the mirror drift for 11 days. The call is best-effort (any failure is swallowed and never blocks session start or any dispatch path) and writes only the sentinel mirror — it does not touch durable role state, dispatch state, or queue entries. The exact wiring point within `session_start_dispatch.py` (and whether to guard it behind the same interactive-vs-headless branch the hook already uses) is finalized at implementation time within that target file.

### IP-2: One-time correction of the live `bridge/INDEX.md`

A one-time, mechanical correction of the two live malformations, so the parser is clean immediately (the generator fix in IP-1 prevents *recurrence*; this clears the *current* 9 errors):

- **Class A:** replace the orphaned sentinel tail (lines 484-490) with a well-formed block regenerated from the live role map via `python scripts\check_index_role_intent_sentinel.py --update` (run after IP-1 lands so the orphaned-tail-tolerant replace does the in-place repair rather than inserting a duplicate). The regenerated block reflects durable truth (`B (Claude)` / `A (Codex)` / `multi_harness` per `build_role_intent_state`), not the stale `A (Codex)` / `prime_only`.
- **Class B:** correct the two version-less status lines so they match `_STATUS_LINE_RE`. The corrected form uses the canonical `-NNN` suffix matching the on-disk first-version files for the `gtkb-commit-scope-bundling-detection-001-prop` and `gtkb-auto-push-investigation-001-prop` documents; the exact replacement strings are confirmed against the on-disk files at implementation time so the references resolve.

`bridge/INDEX.md` is contended by parallel writers and the serialized INDEX writer. The one-time correction is performed within the implementation-start window using the project's serialized write discipline (read-modify-write under the INDEX writer lock per `scripts/bridge_index_writer.py`), and is re-verified against live INDEX state immediately before and after the write so a concurrent writer cannot be clobbered. The hand-correction of INDEX is explicitly NOT the durable fix — IP-1's generator regeneration is — and IP-2 is a one-time cleanup that IP-1 would otherwise eventually heal on the sentinel side; the Class-B lines are corrected once because they are legacy hand-entered status lines, and the canonical writer already emits the versioned `-NNN.md` form.

### IP-3: Regression tests

Add tests:

- `platform_tests/scripts/test_index_role_intent_sentinel.py` (extend the existing file): an INDEX whose sentinel has lost its `<!--` opener (a dangling tail) is repaired in place by `--update` into a single well-formed block reflecting the live role map — no duplicate block is inserted and no dangling tail remains; and a well-formed sentinel is still replaced in place (no regression of the existing replace path).
- `groundtruth-kb/tests/test_bridge_detector.py` (extend the existing file): a fixture INDEX containing (a) a well-formed sentinel comment block and (b) correctly versioned status lines parses with `parse_error_count == 0`; and the two known malformation shapes (orphaned-tail fragment; version-less `…-prop.md` status line) each produce the expected `ParseError` so the detector's behavior is pinned.

## Out Of Scope

- **Do not hand-edit `bridge/INDEX.md` as the durable fix.** The durable fix is the generator (IP-1): the orphaned-tail-tolerant replace plus SessionStart auto-regeneration. IP-2's one-time INDEX correction clears the current 9 errors but is explicitly a cleanup, not the mechanism that prevents recurrence. `bridge/INDEX.md` is contended by parallel writers, so the one-time correction is performed under the serialized writer discipline and re-verified live before/after the write.
- The Codex-authored `gtkb-bridge-index-role-intent-sentinel` thread's own NO-GO remediation (its `-005` implementation report) — that thread is owned by the Loyal Opposition harness as Prime-at-the-time and is a separate lifecycle; this proposal does not author a REVISED on that thread.
- Changing the sentinel schema, fields, freshness window, the `--counts` behavior, or making the sentinel authoritative — the mirror remains a non-authoritative checksum surface.
- Modeling the two-prime (`B` and `C` both `prime-builder`) reality in `build_role_intent_state` — that function currently picks a single prime via `sorted(prime_ids)[0]`; refining its multi-prime representation belongs to the role/status-orthogonality dispatch work, not this reliability fix.
- Wiring the sentinel checker into `gt project doctor`, release-readiness gating, or startup fail-loud enforcement — those remain the named follow-on `gtkb-bridge-index-role-intent-sentinel-startup-enforcement` concern.
- The canonical `bridge_index_writer.py` gaining full sentinel-preservation awareness — a larger generator change; this proposal's SessionStart auto-regeneration is the minimal sufficient fix for the staleness root cause.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `scripts/check_index_role_intent_sentinel.py` — extend sentinel detection/replacement so a dangling orphaned tail is recognized and replaced in place by a freshly rendered, role-map-faithful block (IP-1.1).
- `.claude/hooks/session_start_dispatch.py` — add a best-effort, fail-soft SessionStart invocation of `check_index_role_intent_sentinel.py --update` so the mirror auto-regenerates each session (IP-1.2).
- `bridge/INDEX.md` — one-time correction of the orphaned sentinel tail (Class A) and the two version-less status lines (Class B), performed under serialized-writer discipline (IP-2).
- `platform_tests/scripts/test_index_role_intent_sentinel.py` — regression coverage for the orphaned-tail-tolerant replace (IP-3).
- `groundtruth-kb/tests/test_bridge_detector.py` — regression coverage asserting a clean INDEX parses with zero errors and pinning the two malformation shapes (IP-3).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Detector test: a well-formed sentinel block plus correctly versioned status lines parse with `parse_error_count == 0`, so the canonical INDEX is clean; the orphaned-tail and version-less shapes are pinned as the expected ParseErrors. |
| GOV-SESSION-ROLE-AUTHORITY-001 / DCL-SESSION-ROLE-RESOLUTION-001 / DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 | Sentinel test: `--update` on a dangling-tail INDEX regenerates a single well-formed block from the live durable role map (faithful mirror; never an authority), so the sentinel agrees with the durable role assertion. |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Sentinel test: the regenerated block resolves Prime/Loyal/topology from the durable identity+role maps via `build_role_intent_state` (identity-map-first), reflecting role-to-harness-ID attachment. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Applicability + clause preflight confirm all touched paths are in-root (clause-in-root). |
| GOV-FILE-BRIDGE-AUTHORITY-001 (live clearance) | Live verification: after IP-1+IP-2, `collect_bridge_status(Path('E:/GT-KB')).queue.parse_error_count == 0`, and `python scripts\check_index_role_intent_sentinel.py` prints the sentinel is present, fresh, and consistent. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed test commands and observed results. |

Implementation verification will run (PowerShell-valid; repo venv interpreter):

- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_index_role_intent_sentinel.py -q --tb=short`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_bridge_detector.py -q --tb=short`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'E:/GT-KB/groundtruth-kb/src'); from pathlib import Path; from groundtruth_kb.bridge.status_driver import collect_bridge_status; print('parse_error_count=', collect_bridge_status(Path('E:/GT-KB')).queue.parse_error_count)"`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\check_index_role_intent_sentinel.py`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-index-role-sentinel-stale-reconciliation`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-index-role-sentinel-stale-reconciliation`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\check_index_role_intent_sentinel.py platform_tests\scripts\test_index_role_intent_sentinel.py groundtruth-kb\tests\test_bridge_detector.py`
- `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\check_index_role_intent_sentinel.py platform_tests\scripts\test_index_role_intent_sentinel.py groundtruth-kb\tests\test_bridge_detector.py`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/check_index_role_intent_sentinel.py --update` repairs a dangling orphaned-tail sentinel in place (single well-formed block, no duplicate, no remaining tail) and the block reflects the live durable role map; covered by a test.
- [ ] `.claude/hooks/session_start_dispatch.py` invokes the sentinel `--update` best-effort and fail-soft at SessionStart (a failure neither blocks session start nor any dispatch path).
- [ ] Live `collect_bridge_status(Path('E:/GT-KB')).queue.parse_error_count == 0` after the one-time INDEX correction; the orphaned sentinel tail (lines 484-490) and the two version-less status lines (876, 881) are gone.
- [ ] `python scripts\check_index_role_intent_sentinel.py` exits 0 and prints the sentinel is present, fresh, and consistent against the real `bridge/INDEX.md`.
- [ ] The sentinel remains a non-authoritative checksum mirror; no change makes it override the durable role record, and no durable role state is mutated.
- [ ] A detector test asserts a clean fixture INDEX parses with `parse_error_count == 0` and pins both malformation shapes as expected ParseErrors.
- [ ] `ruff check` and `ruff format --check` pass on the changed files.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): the orphaned-tail-tolerant replace mis-identifies non-sentinel content as a dangling tail and overwrites it.** Mitigation: detection is anchored to the specific sentinel field run (the `Authority:`/`Prime Builder harness:`/`Loyal Opposition harness:`/`Topology:`/`Sentinel updated:` sequence terminating in a bare `-->` with no preceding `<!--` opener), not to any individual field; a dedicated test exercises both the dangling-tail and the well-formed replace paths, and the existing `test_update_preserves_other_content` guards `Document:` entries.

**Risk R2 (low): the one-time `bridge/INDEX.md` correction races a parallel writer.** Mitigation: the correction is performed under the serialized INDEX-writer lock (`scripts/bridge_index_writer.py`) as a read-modify-write, and live parse state is re-verified immediately before and after the write; if a concurrent change is detected, the correction is re-derived against the fresh INDEX rather than clobbering it.

**Risk R3 (low): the SessionStart `--update` call adds latency or noise to session start.** Mitigation: the invocation is best-effort and fail-soft (any exception is swallowed), writes only the small sentinel mirror via the existing atomic-replace path, and runs once per session; on any error the prior behavior is preserved exactly (session start proceeds, sentinel simply not re-stamped that session).

**Risk R4 (low): the Class-B correction picks a version suffix that does not resolve on disk.** Mitigation: the replacement status-line strings are confirmed against the on-disk first-version files for the two `…-prop` documents at implementation time; the detector's `referenced_file_missing` warning (not error) provides a secondary check that the corrected references resolve.

Rollback: each IP is independently revertible. Reverting `scripts/check_index_role_intent_sentinel.py` and `.claude/hooks/session_start_dispatch.py` to their prior versions restores prior generator behavior; the one-time `bridge/INDEX.md` correction can be reverted to its prior content; the tests are additive. No durable role state, dispatch state, or canonical-artifact mutation is involved, so rollback is content-only.

## Loyal Opposition Asks

1. Confirm that the generator-side fix (orphaned-tail-tolerant replace + SessionStart auto-regeneration) is the correct durable remedy for the staleness root cause, with the one-time INDEX correction (IP-2) framed strictly as a one-time cleanup rather than the mechanism of prevention.
2. Confirm the scope boundary: this thread fixes the live 9-parse-error condition and the mirror's self-healing, and explicitly does NOT author a REVISED on the separate Codex-owned `gtkb-bridge-index-role-intent-sentinel` thread, nor refine `build_role_intent_state` multi-prime modeling.
3. Confirm that adding the best-effort `--update` invocation to the existing `.claude/hooks/session_start_dispatch.py` (rather than registering a new standalone hook in `.claude/settings.json`) is the right minimal structural choice for the SessionStart auto-regeneration.
4. Confirm the one-time `bridge/INDEX.md` correction under serialized-writer discipline with before/after live re-verification adequately addresses the parallel-writer contention on the contended INDEX.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
