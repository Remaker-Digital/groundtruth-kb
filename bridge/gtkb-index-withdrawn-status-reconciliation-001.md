NEW

# Deterministic bridge/INDEX.md WITHDRAWN/Superseded Latest-Status Reconciliation Tool and Guard (WI-3491)

bridge_kind: implementation_proposal
Document: gtkb-index-withdrawn-status-reconciliation
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3491
Project Authorization: PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3491
target_paths: ["scripts/bridge_index_withdrawn_reconciler.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index_reconcile.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_index_withdrawn_reconciler.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

`bridge/INDEX.md` — the canonical file-bridge workflow state — can drift out of sync with the on-disk terminal disposition of bridge threads. WI-3491 captures a concrete instance of this drift: ~39 `WITHDRAWN` supersession notices plus ~2 superseded threads whose latest on-disk version records a terminal `WITHDRAWN`/supersession disposition, but whose `bridge/INDEX.md` latest-status line was never reconciled to `WITHDRAWN` — an "auto-retire gap" for the bridge index. While a stale non-`WITHDRAWN` top line persists, those terminally-closed threads continue to be classified by their *previous* (often actionable) status in every INDEX consumer.

A "WITHDRAWN supersession notice" is a bridge thread whose latest versioned file is filed with a leading `WITHDRAWN` status to record that the thread's work was superseded or subsumed by a successor thread. A live example is `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`, cited as the `WITHDRAWN` supersession notice for WI-3256 at `bridge/gtkb-bridge-poller-wi-retirement-disposition-005.md:68` and `:107`. The supersession is recorded in the superseded work item's `superseded_by`/`status_detail`/`change_reason`, and the thread itself is closed with a `WITHDRAWN` notice file — but nothing deterministic guarantees that the thread's `bridge/INDEX.md` latest-status line is moved to `WITHDRAWN` when the notice is filed.

Why the gap exists in the current code paths: the canonical bridge parser at `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:36-39` (`_STATUS_LINE_RE`) and `:24-32` (`BridgeStatus`) now *recognize* `WITHDRAWN` (landed by `gtkb-canonical-bridge-parser-withdrawn-status-handling`), and the size-bounding trim at `scripts/bridge_index_archival.py` treats a `WITHDRAWN` top as removal-eligible (per `gtkb-bridge-index-archival-trim`). But neither path *writes* a `WITHDRAWN` latest-status line into `bridge/INDEX.md` when an on-disk WITHDRAWN/superseded disposition exists with a stale INDEX top. Recognition and size-trim both read; neither reconciles. There is no deterministic tool that closes the loop by detecting and correcting the stale latest-status, and no guard that surfaces the condition when it recurs — so the drift accumulates silently between manual cleanups.

This proposal adds (IP-1) a deterministic reconciliation tool — a source module plus a `gt bridge index-reconcile` CLI surface — that scans on-disk bridge files against `bridge/INDEX.md` latest-status using the canonical parser, identifies threads whose latest on-disk version is a `WITHDRAWN` supersession notice (or a documented superseded thread) but whose INDEX top is non-`WITHDRAWN` (or absent), and reconciles the INDEX latest-status through the serialized, contention-safe atomic INDEX writer; and (IP-2) regression tests. A `--check` mode is non-mutating (the recurrence guard); `--apply` performs the reconciliation, which is a no-op when the index is already consistent. The deterministic tool — not an ad-hoc hand-edit — is the deliverable; a one-time `--apply` reconcile run on the live index is in scope but is bounded by, and audited through, the same tool.

Forensic note (read-only, this session): a read-only sweep of the live working tree using the canonical `parse_index` found `bridge/INDEX.md` currently reflects 40 `WITHDRAWN` latest-status tops correctly, with 0 threads in the "latest file `WITHDRAWN` but INDEX top stale" condition at this instant — the point-in-time backlog count in WI-3491's title was substantially closed by intervening manual reconciliation. The durable defect that remains, and that this proposal fixes, is the *absence of a deterministic tool and guard* that keep INDEX latest-status reconciled with on-disk WITHDRAWN/superseded dispositions so the gap cannot silently re-accumulate. The sweep also surfaced 2 threads whose INDEX top file points at an older version than the highest on-disk file (`gtkb-backlog-authorize-implementation-cli-slice-1`, `gtkb-backlog-update-cli-slice-1`); those are active in-flight threads, not WITHDRAWN/superseded, and are explicitly out of scope here.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` is the canonical bridge workflow state; INDEX latest-status that does not reflect a thread's terminal WITHDRAWN/superseded disposition is a faithfulness defect against this authority. The reconciliation moves a stale latest-status to its correct terminal value through the serialized atomic writer; it never alters version history or removes a bridge file. This is the WI-3491 governing specification.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — the in-root placement decision and the platform root-boundary rule; all four target paths (the reconciler script, the CLI module, the cli.py registration, and the test) are in-root under `E:\GT-KB`, and the tool reads/writes only the in-root `bridge/INDEX.md` and in-root `bridge/*.md` files. Clause-in-root is satisfied.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification; the reconciler's correctness is anchored to the canonical parser and the file-bridge status vocabulary.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward with executed commands and observed results.
- GOV-RELIABILITY-FAST-LANE-001 — governs small single-concern defect fixes; this proposal's defect-removal shape maps to those criteria, though the operative authorization is the dedicated PAUTH `PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001` (a standard project authorization, not the standing fast-lane).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the reconciliation is non-destructive: bridge `*.md` files remain on disk, version history is preserved, and only a stale latest-status line is corrected to reflect the durable on-disk disposition (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — the supersession relationship (notice file ↔ successor thread ↔ superseded work item) is an artifact-graph relationship; reconciling INDEX latest-status keeps the bridge surface faithful to that graph (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — `WITHDRAWN` is a terminal lifecycle status; the reconciler keys on a thread's latest on-disk terminal status to decide whether its INDEX latest-status requires correction (advisory).

## Authorization

This work is authorized under the dedicated project authorization `PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001` (confirmed live in `project_authorizations`: `status=active`, `project_id=PROJECT-GTKB-RELIABILITY-FIXES`, `owner_decision_deliberation_id=DELIB-2548`, `included_work_item_ids=["WI-3491"]`, `allowed_mutation_classes=["source","test_addition","hook_upgrade","cli_extension"]`, `included_spec_ids=["GOV-FILE-BRIDGE-AUTHORITY-001"]`). The owner decision is `DELIB-2548` (confirmed live in `deliberations`: `source_type=owner_conversation`, `outcome=owner_decision`, `session_id=S381`), recording the S381 AskUserQuestion approval that batch-authorized WI-3488/WI-3487/WI-3469/WI-3491/WI-3482 under `PROJECT-GTKB-RELIABILITY-FIXES`.

The four mutation classes map to the scope: `source` (the reconciler module), `cli_extension` (the `gt bridge index-reconcile` surface), `hook_upgrade` (reserved for an optional `--check` guard hookup if a guard surface is wired; no hook registration is added in this slice — see Out Of Scope), and `test_addition` (the regression tests). All edits are within the authorization's mutation classes and within `E:\GT-KB`. No formal-artifact-approval packet is required: the touched paths are NOT in `config/governance/narrative-artifact-approval.toml`'s protected-artifact set, and the bridge thread plus Codex GO is the per-WI implementation authority under this dedicated authorization.

## Prior Deliberations

Read-only deliberation/prior-art review was performed before drafting. The adjacent bridge threads were read in full via the live index chain; WI-3491 is distinct from each:

- `bridge/gtkb-bridge-index-archival-trim-001.md` through `-010.md` (WI-3364, VERIFIED at `-010`) — the **size-bounding** trim. It removes oldest *terminal* `Document:` blocks (`VERIFIED`/`WITHDRAWN`) from the bottom of `bridge/INDEX.md` to keep the file bounded, and treats a `WITHDRAWN` latest-status as removal-eligible (`-001.md:77`). It reads WITHDRAWN to decide *removal*; it does NOT write or reconcile a stale non-`WITHDRAWN` INDEX top into `WITHDRAWN`. WI-3491 is the complementary **status-reconciliation** concern: a thread can be WITHDRAWN/superseded on disk while its INDEX top still reads a non-terminal status, so the trim would never even consider it removable. Distinct concern (de-indexing/status-reconciliation vs size-trim).
- `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md` through `-004.md` (WI-3276 Layer-0, VERIFIED) — taught the canonical parser `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` to *recognize* `WITHDRAWN` lines already present in INDEX (`detector.py:24-32`, `:36-39`). It is a parse-recognition fix; it does not detect or correct threads whose INDEX top is stale relative to an on-disk WITHDRAWN notice. WI-3491 builds on this recognition (the reconciler consumes the now-correct parser) to close the *write* side. Distinct concern (parse-recognition vs index-reconciliation).
- `bridge/gtkb-audit-script-withdrawn-status-handling-001.md` through `-006.md` (WI-3276 Layer-1, VERIFIED) — the same recognition fix at the audit-script regex `scripts/audit_standing_backlog_sources.py:39`. Read-only audit recognition, not INDEX mutation. Distinct concern.
- `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md` through `-003.md` — a follow-on regex fix to the same audit-script recognition path; the `-003` top is itself `WITHDRAWN` in INDEX. Recognition/audit, not reconciliation. Distinct concern.
- `bridge/gtkb-bridge-verified-backlog-retirement-*` and `scripts/bridge_verified_backlog_reconciler.py` (DELIB-S345) — reconciles the **MemBase work-item** side (resolves active work items whose linked bridge threads are all VERIFIED). It parses INDEX latest-status (`scripts/bridge_verified_backlog_reconciler.py:43-62`, status regex at `:26`) but writes to `work_items`, never to `bridge/INDEX.md`. WI-3491 reconciles the INDEX latest-status itself. Distinct target (MemBase rows vs INDEX lines).
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-005.md` / `-008.md` (VERIFIED) — the disposition thread that named the WITHDRAWN supersession notice for WI-3256; it is the concrete example of the notice artifact WI-3491 reconciles into INDEX, not a fix for the INDEX-side gap.

A read-only `gt deliberations search` was run for `bridge INDEX withdrawn reconciliation`, `de-index supersession latest status`, and `auto-retire bridge index`; no Deliberation Archive row contradicts this scoped fix, and the governing owner decision is `DELIB-2548`.

## Owner Decisions / Input

- 2026-06-01 (S381): via AskUserQuestion the owner approved batch-authorizing WI-3491 (with WI-3488/WI-3487/WI-3469/WI-3482) under `PROJECT-GTKB-RELIABILITY-FIXES`, recorded as the owner-decision deliberation `DELIB-2548` (`source_type=owner_conversation`, `outcome=owner_decision`, `session_id=S381`). The dedicated authorization envelope `PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001` (active; `owner_decision_deliberation_id=DELIB-2548`; `included_work_item_ids=["WI-3491"]`; `allowed_mutation_classes=["source","test_addition","hook_upgrade","cli_extension"]`) is the operative implementation authorization for this thread.
- No further owner decision is required before GO. Implementation touches no protected narrative artifact and inserts no formal artifact; the dedicated project authorization plus the bridge thread and Codex GO are the implementation authority.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already establishes `bridge/INDEX.md` as the canonical workflow state that must faithfully reflect each thread's status; an INDEX latest-status that contradicts an on-disk terminal WITHDRAWN/superseded disposition is non-compliance with that existing requirement. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation. The reconciler's terminal-status vocabulary and the `WITHDRAWN`-notice detection rule are parameters of an internal tool, not a specification surface.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix: one new reconciler source module, one `gt` CLI subcommand module, the one-line CLI registration, and regression tests; plus a one-time `--apply` reconcile run bounded by the same tool. It is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: it does not resolve, retire, promote, batch-mutate, or produce an inventory of MemBase work items, and it requests no formal-artifact-approval packet for a bulk action. The reconciler operates on `bridge/INDEX.md` *latest-status lines* (bridge-thread state), not on `work_items` rows. The only work item cited (WI-3491) is this proposal's own implementing work item under the mandatory project-linkage metadata. The one-time reconcile pass corrects existing stale INDEX latest-status lines to reflect already-existing on-disk dispositions; it creates no new dispositions and is a no-op when the index is already consistent.

## Scope

### IP-1: Deterministic INDEX WITHDRAWN/superseded latest-status reconciler (tool + guard + CLI)

Add `scripts/bridge_index_withdrawn_reconciler.py`. The module exposes a pure analysis function and a contention-safe apply function:

- `find_stale_withdrawn_threads(index_text, *, project_root) -> list[StaleThread]` — a pure, I/O-light analysis that:
  - Parses `bridge/INDEX.md` latest-status with the canonical `parse_index` from `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` (the module bootstraps `groundtruth-kb/src` onto `sys.path` from its own resolved location, mirroring `scripts/bridge_verified_backlog_reconciler.py:15-18`, so it imports regardless of invocation context).
  - Enumerates on-disk `bridge/<slug>-<NNN>.md` files, groups them by thread slug, and identifies each thread's highest on-disk version.
  - Classifies a thread as a **WITHDRAWN supersession notice / superseded thread** when its highest on-disk version file carries a leading `WITHDRAWN` status line (the deterministic, unambiguous signal — the same first-non-blank-line `WITHDRAWN` convention the file-bridge protocol and `scripts/bridge_index_archival.py` already rely on). Threads whose terminal file is non-`WITHDRAWN` are never touched.
  - Returns the set of threads where the on-disk highest version is a `WITHDRAWN` notice but the INDEX latest-status for that slug is either absent or a non-`WITHDRAWN` status — i.e., the stale/de-index-gap set. Each `StaleThread` carries the slug, the current INDEX top status+file, the on-disk WITHDRAWN notice file, and the `line_number` of the stale INDEX top (available from `BridgeVersion.line_number`).
- `reconcile_index(*, project_root, dry_run) -> ReconcileReport` — when `dry_run` is False, applies the corrections through `scripts/bridge_index_writer.py` `atomic_index_update(...)` (the serialized, lock-guarded, atomic read-modify-write proven for contended INDEX mutation, `scripts/bridge_index_writer.py:282-317`). The mutate callback, for each stale thread, prepends a `WITHDRAWN: bridge/<slug>-<NNN>.md` latest-status line to that thread's existing version block (preserving the full version history below it) — the same "latest at top" insertion shape the protocol uses. Because the whole read-modify-write runs inside the index-writer lock, the reconcile is safe against the parallel INDEX writers currently active. `dry_run=True` performs no write and returns the same report for `--check`.

The `--check` mode is the **recurrence guard**: it reports the stale set and exits non-zero when the set is non-empty, so the condition is mechanically surfaced (in CI, a wrap scan, or an operator run) rather than rediscovered by hand. The reconciler never edits version history, never deletes or renames a bridge file, and never alters a thread whose terminal on-disk status is not `WITHDRAWN`; the actionable/non-WITHDRAWN set is an unconditional floor.

### IP-1b: `gt bridge index-reconcile` CLI surface

Add `groundtruth-kb/src/groundtruth_kb/cli_bridge_index_reconcile.py` exposing the subcommand and register it in `groundtruth-kb/src/groundtruth_kb/cli.py` (the established `cli_<name>.py` + one-line registration pattern, mirroring `cli_projects_reconcile.py` and `cli_bridge_propose.py`). Surface:

- `gt bridge index-reconcile --check` — non-mutating guard; prints the stale set (table/JSON) and exits non-zero when non-empty.
- `gt bridge index-reconcile --apply` — performs the reconcile through the serialized atomic writer; prints the corrected threads and a before/after stale count.

The CLI is a thin wrapper over the IP-1 functions; all analysis and write logic lives in the reconciler module so it is fully unit-testable without the CLI.

### IP-1c: One-time reconcile pass (bounded by the tool)

After GO and implementation, run `gt bridge index-reconcile --apply` once against the live `bridge/INDEX.md` to clear any stale WITHDRAWN/superseded latest-status that exists at implementation time. Per the read-only forensic finding above, the live index is currently consistent, so this pass is expected to be a no-op (0 corrections) — which itself is the verification that the tool correctly leaves a clean index untouched. The post-implementation report records the observed before/after stale count.

### IP-2: Regression tests

Add `platform_tests/scripts/test_bridge_index_withdrawn_reconciler.py`:

- A fixture INDEX whose top for a thread is `NO-GO` while the thread's highest on-disk version file (a fixture under a tmp bridge dir) begins with `WITHDRAWN` → `find_stale_withdrawn_threads` returns exactly that thread; `reconcile_index(dry_run=False)` rewrites the INDEX top to `WITHDRAWN: bridge/<slug>-<NNN>.md` and preserves the prior version lines beneath it.
- A thread whose INDEX top is already `WITHDRAWN` and matches the on-disk notice → not in the stale set; reconcile is a no-op (idempotence).
- A thread whose highest on-disk file is non-`WITHDRAWN` (e.g., `GO`/`NO-GO`/`NEW`) → never reconciled, even when over any threshold (the non-WITHDRAWN floor holds); this directly covers the 2 in-flight TOPFILE-MISMATCH threads' class so active threads are provably untouched.
- A WITHDRAWN-notice thread absent from INDEX entirely → reported by `--check` (guard surfaces it); the apply path inserts the corrected entry or reports it per the chosen safe default (the test pins the default).
- `--check` on a fully consistent index returns an empty stale set and exit 0; on a stale index returns the stale set and non-zero exit.
- The reconcile uses `atomic_index_update` (the write goes through the serialized writer): a test asserts the write path is the index-writer (so contention safety is structurally guaranteed), not a bare file write.

## Out Of Scope

- The size-bounding INDEX trim — owned and VERIFIED by `gtkb-bridge-index-archival-trim` (WI-3364). This thread does not change trim behavior; a reconciled `WITHDRAWN` top simply becomes eligible for the existing trim later.
- Parser recognition of `WITHDRAWN` — owned and VERIFIED by `gtkb-canonical-bridge-parser-withdrawn-status-handling` and `gtkb-audit-script-withdrawn-status-handling`. This thread consumes that recognition; it does not modify the parser.
- The MemBase work-item-side VERIFIED reconciler `scripts/bridge_verified_backlog_reconciler.py` — separate target (work_items vs INDEX lines); unchanged.
- Threads whose INDEX top file merely points at an older version than the highest on-disk file while the highest is non-`WITHDRAWN` (the 2 active in-flight threads observed this session) — those are live work, not WITHDRAWN/superseded; reconciling them is explicitly excluded.
- Registering a new hook or scheduled task to run the guard automatically — no hook registration is added in this slice; `--check` is operator/CI-invokable. (A future thread may wire the `--check` guard into a wrap or CI surface; the `hook_upgrade` mutation class in the authorization reserves that option but it is not exercised here.)
- Any change to bridge `*.md` files, version history, or the file-bridge status vocabulary — only the stale latest-status line in `bridge/INDEX.md` is corrected.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `scripts/bridge_index_withdrawn_reconciler.py` — NEW: the deterministic reconciler module (`find_stale_withdrawn_threads`, `reconcile_index`) plus a `__main__` CLI entry (IP-1).
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_index_reconcile.py` — NEW: the `gt bridge index-reconcile` subcommand wrapper (IP-1b).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — register the new subcommand (one-line wiring per the existing `cli_<name>.py` pattern) (IP-1b).
- `platform_tests/scripts/test_bridge_index_withdrawn_reconciler.py` — NEW: regression coverage for IP-1/IP-1b (IP-2).

The one-time `gt bridge index-reconcile --apply` run (IP-1c) mutates `bridge/INDEX.md` latest-status only when stale WITHDRAWN/superseded tops exist; it is expected to be a no-op against the currently-consistent live index and is performed via the tool, not by hand.

## Spec-To-Test Mapping

| Spec / governing surface | Test or verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Test: a thread whose highest on-disk version is a `WITHDRAWN` notice but whose INDEX top is `NO-GO` is detected and reconciled to a `WITHDRAWN` latest-status, with version history preserved; `bridge/INDEX.md` thereby reflects the thread's true terminal disposition. |
| GOV-FILE-BRIDGE-AUTHORITY-001 (non-WITHDRAWN floor) | Test: a thread whose highest on-disk version is non-`WITHDRAWN` (GO/NO-GO/NEW) is never reconciled — active/in-flight threads are provably untouched. |
| GOV-FILE-BRIDGE-AUTHORITY-001 (contention safety) | Test: the apply path writes through `scripts/bridge_index_writer.py` `atomic_index_update` (serialized lock + atomic replace), so the reconcile is safe under concurrent INDEX writers. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Applicability + clause preflight confirm all four target paths and the read/write surface are in-root under `E:\GT-KB`. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Test: reconcile prepends a latest-status line and preserves all prior version lines; no bridge `*.md` file is deleted, renamed, or otherwise mutated. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Test: detection keys on the highest on-disk version's terminal `WITHDRAWN` status; idempotence — a thread already `WITHDRAWN` at the INDEX top is a no-op. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | The Specification Links section cites every relevant governing specification; the applicability preflight reports `missing_required_specs: []`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed test command, the one-time `--apply` before/after stale count, and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_bridge_index_withdrawn_reconciler.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-withdrawn-status-reconciliation`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-withdrawn-status-reconciliation`
- `ruff check scripts/bridge_index_withdrawn_reconciler.py groundtruth-kb/src/groundtruth_kb/cli_bridge_index_reconcile.py platform_tests/scripts/test_bridge_index_withdrawn_reconciler.py` and `ruff format --check` on the same files (resolved against the repo venv interpreter, which has `ruff`).

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/bridge_index_withdrawn_reconciler.py` provides a pure `find_stale_withdrawn_threads(...)` that, using the canonical `parse_index`, returns exactly the threads whose highest on-disk version is a `WITHDRAWN` notice but whose INDEX latest-status is non-`WITHDRAWN` or absent; covered by tests.
- [ ] `reconcile_index(dry_run=False)` corrects those threads' INDEX latest-status to `WITHDRAWN` through `scripts/bridge_index_writer.py` `atomic_index_update`, preserving version history; covered by tests.
- [ ] A thread whose highest on-disk version is non-`WITHDRAWN` is never reconciled (non-WITHDRAWN floor); covered by a test that includes the active in-flight class.
- [ ] `--check` exits non-zero on a stale index and zero on a consistent index (the recurrence guard); covered by tests.
- [ ] `gt bridge index-reconcile --check` and `--apply` are registered and functional.
- [ ] The one-time `gt bridge index-reconcile --apply` run is executed and its before/after stale count recorded in the post-implementation report (expected no-op against the currently-consistent live index).
- [ ] No bridge `*.md` file is deleted, renamed, or content-mutated; no change to the trim, the parser, or the work-item reconciler.
- [ ] `ruff check` and `ruff format --check` pass on the changed files.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (medium): the reconciler reclassifies a still-active thread as `WITHDRAWN`.** Mitigation: the detection rule is gated strictly to threads whose *highest on-disk version file* begins with a `WITHDRAWN` status line — the deterministic, append-only signal that the thread was terminally withdrawn/superseded. A thread whose latest file is any non-`WITHDRAWN` status (including the 2 observed in-flight TOPFILE-MISMATCH threads) is never touched. A dedicated test asserts the non-WITHDRAWN floor.

**Risk R2 (low): the reconcile races a concurrent INDEX writer and loses an update.** Mitigation: the apply path performs the entire read-modify-write through `scripts/bridge_index_writer.py` `atomic_index_update`, which holds the process-exclusive `index-writer.lock` and writes atomically via temp-file-plus-`os.replace` (`scripts/bridge_index_writer.py:244-254`, `:282-317`). This is the same serialized writer designed for the contended-INDEX case, so the reconcile inherits its concurrency guarantees rather than adding a bare write.

**Risk R3 (low): the one-time `--apply` pass corrupts a currently-consistent INDEX.** Mitigation: when the stale set is empty the mutate callback returns the input text unchanged, so a consistent index is a guaranteed no-op; a test pins the idempotence/empty-set behavior, and the post-impl report records the observed 0-correction result.

**Risk R4 (low): `WITHDRAWN`-notice detection misfires on a file that merely mentions "withdrawn" in prose.** Mitigation: detection requires the *first non-blank line* of the highest-version file to be a `WITHDRAWN` status line (not prose mention), matching the file-bridge convention and the existing archival-trim terminal-status rule; tests include a prose-mention negative case.

Rollback: the change is contained to two new modules, a one-line CLI registration, and a new test file. Reverting those restores the prior (no-reconciler) state. The one-time `--apply` only ever moves a stale latest-status to its correct terminal `WITHDRAWN` value with full history preserved; if a specific reconciliation were ever judged wrong, the bridge file remains on disk and the INDEX line is hand-correctable, but no data is lost. No MemBase mutation and no canonical-artifact insertion are involved.

## Loyal Opposition Asks

1. Confirm the detection rule — a thread is reconcilable to `WITHDRAWN` only when its *highest on-disk version file* begins with a `WITHDRAWN` status line — is the correct, sufficiently conservative signal, versus also keying on `superseded_by`/supersession-prose heuristics (which this proposal deliberately excludes as ambiguous).
2. Confirm that routing the apply write through `scripts/bridge_index_writer.py` `atomic_index_update` (rather than the four helper INDEX-insertion paths or a bare write) is the right structural choice for safe reconciliation under the currently-active parallel INDEX writers.
3. Confirm the scope boundary: this thread delivers the reconciliation tool + `--check` guard + a tool-bounded one-time pass, and leaves the size-trim, the parser recognition, the work-item reconciler, and any automatic guard hook/CI wiring to their own threads.
4. Confirm the disposition of WITHDRAWN-notice threads that are absent from INDEX entirely: report-only via `--check` versus auto-insert on `--apply` — the test pins whichever default Loyal Opposition prefers as safest.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
