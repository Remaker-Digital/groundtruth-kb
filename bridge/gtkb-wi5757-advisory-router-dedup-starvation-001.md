NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker; manual dispatch per DELIB-202667523; resolved role prime-builder for this filing

# Implementation Proposal - Re-Key Advisory-Router Dedup To Slug+Version, Add Starvation Liveness Signal, Backfill Starved Advisories (WI-5757)

Document: gtkb-wi5757-advisory-router-dedup-starvation
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5757

target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py"]

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write during filing; the implementation's router writes flow through the existing governed service path and are covered by the cited PAUTH. This proposal performs no approval-evidence work; it requires no approval packets.

---

## Problem

Source advisory: `bridge/gtkb-lo-advisory-router-slug-dedup-starvation-advisory-001.md` (read in full; root-cause verified against source at HEAD).

The advisory-to-backlog router (`scripts/advisory_backlog_router.py`) deduplicates bridge advisories on **thread slug alone**:

- `collect_bridge_advisories` sets `source_key=doc_id` (the bare slug) at line 402, discarding the version that `_latest_bridge_threads` already provides at the call site (line 376 binds it as `_version`).
- Idempotency gate #1 (`run()` lines 603-612) skips any advisory whose `source_key` appears in the candidate-store fold `current_candidate_status` (lines 483-496) with **any** status - including `rejected`.
- Idempotency gate #2 (`_existing_wi_for`, lines 424-440) skips via substring `LIKE '%{source_key}%'` against `current_work_items.related_deliberation_ids`.

Consequence: once any version of a slug has been staged, every later advisory version on that slug is permanently and silently skipped. Per the advisory's evidence (E2-E5), 13 of 15 advisories on disk at the observation snapshot were unreachable, the run reported `staged_count: 0, skipped_existing_count: 15, errors_count: 0` (byte-indistinguishable from a healthy no-op), and the P0 root-cause filing for the VERIFIED-finalization deadlock was among the starved items. The append-only advisory chain - the correct audit shape under `GOV-FILE-BRIDGE-AUTHORITY-001` - is silently converted into a write-only sink, defeating the standing-backlog intake that `GOV-STANDING-BACKLOG-001` makes the durable cross-session work authority.

## Proposed Changes

All changes are confined to the two `target_paths` files. The router remains a stage-only deterministic service: it appends to `.gtkb-state/advisory-candidates/candidates.jsonl` and writes `.gtkb-state/advisory-router/last-scan.json` (runtime evidence surfaces, not canonical state). It creates no `work_items` rows; promotion remains the owner-batch-AUQ path in `scripts/hygiene/advisory_candidate_promote.py` (unchanged).

### Change 1 - Re-key bridge-advisory dedup to slug+version

In `collect_bridge_advisories`, construct `source_key = f"{doc_id}-{int(version):03d}"` (the versioned document id, identical to the staged file's filename stem). The dropbox path keeps its filename key (already version-free by construction and permanently a no-op per the module docstring).

Legacy-compat predicate (deterministic, no store rewrite; the candidate log stays append-only per its own audit discipline):

- Gate #1: skip when the versioned key is in the fold, OR when a legacy bare-slug record exists for this slug AND that record's `relative_path` equals this advisory's `relative_path` (same physical file already staged under the legacy key). This prevents duplicate staging of already-staged files while unblocking every newer version.
- Gate #2 (`_existing_wi_for`): query `LIKE` on the versioned key (a bare-slug-attributed WI row cannot contain the versioned key, so newer versions are unblocked automatically); add a legacy-compat clause so a WI matched via bare-slug `LIKE` blocks only the version recorded in that slug's legacy candidate record (conservative default: version 001 when no store record exists). Without this clause the second gate re-introduces duplicate staging for already-promoted version-001 heads.

### Change 2 - Starvation liveness signal

Per advisory Recommended Prime Action #2: a run where `scanned > 0`, `staged_count == 0`, and `skipped_existing_count == scanned` must be distinguishable from a mixed or staging run. Add a computed `starvation_signal: bool` to `RouterResult`, persist it in `last-scan.json` via `_write_last_scan`, and emit a single WARNING line on stdout in the CLI path when it is true. This is a durable machine-readable hook for monitors; it does not change exit codes and does not touch the Stop-hook wrapper.

### Change 3 - Backfill the starved advisories

Backfill is the first post-fix non-dry-run router pass: with the re-keyed gates, every currently-starved ADVISORY thread head stages under its versioned key in one deterministic run. No separate backfill script, no MemBase write. Scope honesty: the router scans thread heads only; historical non-head versions (e.g., the root-cause text at `-007`/`-008` of the tooling-defect chain) reach the owner through the staged head under the full-thread read discipline (`Document:` block must be read in full).

Bulk-visibility evidence per `GOV-STANDING-BACKLOG-001` (CLAUSE-VISIBILITY-BULK-OPS): the backfill produces an inventory artifact - the before/after `--dry-run` staging inventory plus the resulting `last-scan.json` - carried in the post-implementation report, which serves as the review packet for the bulk staging action. Entry of any staged candidate into the active backlog remains individually owner-gated through the promotion tool's owner-batch AUQ review; the backfill itself creates zero backlog rows.

### Explicitly out of scope

- The Codex hook-registration parity gap and the divergent hook-path registry entries (advisory item #5) - adjacent observations, separate tracking.
- The fail-silent behavior of `.claude/hooks/advisory-router-scan.py` - the liveness signal lands in the router result and `last-scan.json`, which the wrapper persists regardless.
- Removal of the retired dropbox source path (tracked as WI-5509's sibling follow-on per the module docstring).

## Specification Links

- `GOV-STANDING-BACKLOG-001` - the standing backlog is the durable cross-session work authority; the router is its advisory intake and stamps `source_spec_id='GOV-STANDING-BACKLOG-001'` on routed candidates. The starvation defect suppresses this authority's intake; the fix restores it.
- `DCL-STANDING-BACKLOG-SCHEMA-001` - staged candidates carry the metadata the promotion tool needs to mint conformant `work_items` rows; the re-key changes the idempotency key, not the staged record schema.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the append-only versioned bridge chain is the audit trail; the fix makes the router honor (rather than penalize) append-only versioning, and the router remains read-only over `bridge/`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this work proceeds under the cited active project authorization plus this proposal's bridge `GO`; PAUTH metadata does not broaden `target_paths` or replace the live latest-`GO` requirement.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the router is a deterministic service; the fix and the backfill are service-side, not session-ceremony-side.
- `SPEC-1830` - operational procedures must be code: backfill is a deterministic router pass, not a conversational procedure.
- `SPEC-1662` (GOV-18) - assertion quality: the new tests assert behavioral outcomes (staged vs skipped records, signal emission), not structure.
- `GOV-10` - tests exercise the exposed production interface (`run()`, the CLI surface, and the candidate-store/last-scan artifacts), via the existing module-load harness in the test file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section satisfies the mandatory proposal spec-linkage constraint; the verification plan maps each link to derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the eventual `VERIFIED` is conditional on creation and execution of the spec-derived tests T1-T6; the implementation report will carry the executed commands and observed results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix restores an artifact-graph intake path (advisory -> staged candidate -> owner-promoted work item) instead of leaving findings as transient chat/file state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - project memory is a durable artifact graph; starved advisories are dropped graph edges, and the backfill reconnects them.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - staged candidates carry explicit lifecycle states (`staged` -> `promoted`/`rejected`) with owner confirmation flows; the re-key preserves those states and their append-only provenance.

Tests derive from these links as mapped in the verification plan below.

## Prior Deliberations

- `DELIB-202667531` - owner advisory-triage decision: fix-class first, authorized corrective WIs (WI-5757 is part of that set).
- `DELIB-202667534` - advisory corpus disposition table: all live ADVISORY threads triaged; this thread implements the router-starvation disposition.
- `DELIB-202667532` - program north-star scoring under which WI-5757 was sequenced.
- `DELIB-202667523` - integrated parallel-operation program mandate and manual-dispatcher operating model (this filing is a fan-out worker product).
- `DELIB-20264768` - Loyal Opposition verification of the original advisory-to-backlog router implementation (the surface being corrected).
- `DELIB-20265695` - LO review of WI-4403 (advisory router compact skipped-existing test) - prior decision history on the exact `skipped_existing` surface this change re-keys.
- `DELIB-20261055` - Advisory Router Output Volume Advisory - prior volume-shape concern; the owner-gated promotion path (unchanged here) is the accepted control, so the backfill stages candidates without creating backlog rows.

## Owner Decisions / Input

- `DELIB-202667531` - owner authorization of the fix-class advisory-correction work set, including WI-5757 (advisory triage 2026-07-29). Recorded owner decision; per CLAUDE.md session-start rules, items already authorized by recorded owner decision need no fresh approval to enter the bridge protocol.
- `AUQ-20260729-ADVISORY-TRIAGE-POLICY` - the AskUserQuestion evidence behind the 2026-07-29 advisory-triage policy (fix-class first; capture is not implementation approval), under which this proposal is filed for Loyal Opposition review rather than implemented directly.
- No further owner decision is required to review this proposal; implementation proceeds only on bridge `GO` plus an implementation-start authorization packet.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-STANDING-BACKLOG-001` (standing-backlog intake authority), `GOV-FILE-BRIDGE-AUTHORITY-001` (append-only versioned bridge audit trail), and the source advisory's mechanically-verified defect analysis (`bridge/gtkb-lo-advisory-router-slug-dedup-starvation-advisory-001.md`, confirmed against `scripts/advisory_backlog_router.py` lines 402, 424-440, 483-496, 603-625 at HEAD) fully determine the required behavior. No new or revised requirement is needed before implementation.

## Verification Plan (Spec-Derived Test Mapping)

New tests extend `platform_tests/scripts/test_advisory_backlog_router.py` (existing tmp_path fixture-project harness; live store and live DB untouched):

| # | Test | Derives from |
|---|------|--------------|
| T1 | Dedup re-key regression: slug staged at `-001`, then `-002` filed as thread head - second run STAGES `-002` (not `skipped_existing`) | GOV-STANDING-BACKLOG-001 intake; advisory E1/E2 |
| T2 | Legacy-compat no-duplicate: candidate store holds a legacy bare-slug record whose `relative_path` is the current head file - run skips (no duplicate staging of the same file) | GOV-STANDING-BACKLOG-001; append-only store discipline |
| T3 | `_existing_wi_for` re-key behavior: (a) WI row containing the versioned key blocks that version; (b) legacy bare-slug-attributed WI row does NOT block a newer version on the same slug; (c) legacy bare-slug WI row still blocks re-staging the version recorded in the legacy candidate record (001 default) | GOV-STANDING-BACKLOG-001; advisory recommendation #1 second-gate clause |
| T4 | Starvation liveness signal: all-skip run (`scanned>0, staged==0, skipped_existing==scanned`) writes `starvation_signal: true` to `last-scan.json` and result; a run that stages >=1 records `false` | advisory recommendation #2; SPEC-1662 behavioral-assertion standard |
| T5 | Backfill idempotency: fixture corpus with multiple starved heads - first post-fix run stages each starved head exactly once; an immediately repeated run stages zero | GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001; SPEC-1830; advisory recommendation #3 |
| T6 | Read-only bridge invariant: post-run fixture `bridge/` file set and contents unchanged | GOV-FILE-BRIDGE-AUTHORITY-001 |

Commands (implementation report will carry observed output):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_advisory_backlog_router.py -q`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/advisory_backlog_router.py platform_tests/scripts/test_advisory_backlog_router.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/advisory_backlog_router.py platform_tests/scripts/test_advisory_backlog_router.py`
- Backfill evidence: `--dry-run --source bridge` listing before/after, then one non-dry-run pass; capture `last-scan.json`.

## Acceptance Criteria

1. A new advisory version on a previously-staged slug is staged as a distinct candidate (T1); no already-staged file is staged twice (T2, T3c).
2. Bare-slug-promoted WIs no longer starve newer versions (T3b).
3. `last-scan.json` carries a truthful `starvation_signal` field (T4).
4. One post-fix router pass backfills all starved thread heads; a second pass is a no-op (T5).
5. `bridge/` remains read-only to the router (T6); ruff check and ruff format --check pass on both changed files.

## Risk and Rollback

- Risk: legacy-compat predicate wrong in either direction -> duplicate candidates or residual starvation. Contained: staging is owner-gated (no autonomous backlog rows); T2/T3 pin both directions.
- Risk: mixed key shapes in the fold (legacy bare + versioned). Keys cannot collide (`-NNN` suffix); legacy records remain untouched historical events in the append-only log.
- Rollback: single-commit revert of the two files. Unwanted post-fix staged candidates are dispositioned through the existing promotion tool's reject path; no schema migration, no store rewrite, no MemBase rollback needed.

Recommended commit type: fix

## Review Questions for Loyal Opposition

1. Is the gate-#2 legacy-compat clause (bare-slug WI blocks only the legacy-recorded version, 001 default) the correct conservative default, or should a bare-slug WI match block nothing post-re-key?
2. Is `starvation_signal` in `last-scan.json` + stdout WARNING sufficient as the liveness signal for this slice, given the Stop-hook wrapper's fail-silent design is explicitly out of scope?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
