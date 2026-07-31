ADVISORY

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive; dispatched advisory-authoring worker; claim-resolved acting_role=loyal-opposition (ADVISORY is a Loyal-Opposition-authored status per file-bridge-protocol.md and bridge_lifecycle_resolver.py)

# Advisory — GT-KB Source-of-Truth Access Latency and Append-Only Growth Cost

bridge_kind: governance_advisory
Document: gtkb-sot-access-latency-append-only-growth-cost-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-30 UTC

> Diagnostic / evidentiary advisory. It documents measured cost; it authorizes no
> implementation, requests no owner approval to file, and does NOT propose converting
> append-only SoT to mutable-in-place. Per DELIB-202667697, append-only remains the
> default SoT discipline; this advisory documents the cost of that discipline so future
> governed corrections are well-informed.

## Source

- Standing directive **DELIB-202667697** (SoT-latency advisory standing directive): append-only stays the default SoT discipline; document the cost, do not authorize mutable-in-place conversion.
- Program mandate **DELIB-202667523**.
- Leader-session live observations this working window: `gt bridge state-report` ~5+ minutes (420000 ms timeouts); repeated "Ripgrep search timed out after 20 seconds" on `bridge/` globs; registry control-plane lock hard timeouts during concurrent fleet filings.
- Every number below was re-measured against live state on 2026-07-30 by this advisory-authoring worker under read-only investigation; the figures are not copied from prior summaries.

Prior-deliberation / work-item anchors: DELIB-202667697, DELIB-202667523, DELIB-202667526 (registry-lock convoy), WI-5659 (DB-size finalization break), WI-5703 (DB-size evidence), WI-5739 (wi5668 wedge), WI-5788 (registry-lock timeout), WI-5758 (currentness deadlock).

## Claim

One structural pattern underlies all five cases: **append-only SoT access cost grows monotonically**, and several access surfaces have already crossed thresholds that break or severely slow governed operations. Each case below is a candidate for a future governed correction; this advisory documents the case only and designs nothing.

### Case 1 — Bridge chain resolution is O(chain-length) and wedges on a single broken historical head

Evidence (`scripts/bridge_lifecycle_resolver.py`):
- `resolve_bridge_lifecycle` parses **every** historical version of a thread on each call (lines 664-667 parse the full `_exact_version_paths` set through `_parse_version`), then `_validate_ordinary_transitions` re-walks all versions (lines 395-456). Cost is O(n) in chain length per publication.
- `_exact_version_paths` additionally scans the **entire** `bridge/` directory via `bridge_dir.iterdir()` (line 141) on **every** resolution — so each publication also pays O(total-directory) = O(14,088 files), not merely O(chain).

Measured live longest append-only chains (2026-07-30):

| versions | thread |
|---|---|
| 85 | gtkb-work-tree-hygiene-slice-d-governance-spec |
| 51 | gtkb-wi4944-release-dispatcher-lo-dispatch-unblock |
| 50 | gtkb-wi4978-helper-compliance-audit-chokepoint |
| 38 | gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation |
| 34 | gtkb-dispatcher-black-box-spec-foundation |

(Task-cited examples corroborated live: gtkb-wi5441-global-registry-membership-reconciliation = 20 versions; gtkb-wi5679-session-role-keying-continuity = 16 versions.)

Wedge (the append-only-cost-vs-latency tradeoff made concrete): resolving `gtkb-wi5668-skill-rename-sweep-completion-gate` (14 versions on disk) raises `WRONG_RESPONDS_TO_LINK` at `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-007.md` (v007): "Responds to metadata None does not match 'bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-006.md'". A single metadata-broken historical head at v007 makes the **entire** thread unresolvable and blocks **all** future statuses — even an owner-directed DEFERRED. Tracked WI-5739.

### Case 2 — Bridge directory enumeration scales with total (never-deleted) thread count

Measured live: `bridge/` holds **14,098** files (**14,088** `.md`) across **2,357** distinct threads. Bridge files are append-only (never deleted — audit trail), so the directory and every read that enumerates it grow monotonically.

- Name-only enumeration (PowerShell `Get-ChildItem`): **1.54 s**.
- Content search (ripgrep / Glob over `bridge/`): **times out** — the leader hit "Ripgrep search timed out after 20 seconds" repeatedly this session.
- `gt bridge state-report`: observed **~5+ minutes** (420000 ms timeouts).

Read surfaces that scale with directory size: session-start bridge scan; `gt bridge state-report`; the applicability-preflight resolver; dispatch signature computation; and every `resolve_bridge_lifecycle` call (via the `iterdir()` full-directory scan noted in Case 1).

### Case 3 — MemBase groundtruth.db size breaks governed operations

Measured live: `(Get-Item groundtruth.db).Length` = **844,025,856 bytes (~805 MiB / 844 MB)** — grown beyond the WI-5703 evidence of 814,247,936 bytes (and the earlier 727 MB WI-5659 figure).

- Finalizer blob ceiling `MAX_BLOB_BYTES = 64 MiB = 67,108,864` (`scripts/check_protected_commit_authorization.py:67`). The live DB is **12.6× the ceiling**.
- WI-5659: at 727 MB the tracked `groundtruth.db` exceeded `MAX_BLOB_BYTES` by **11.4×**, failing **every** governed finalization closed until the finalizer was bounded to authorized audit scratch. This is SoT **size** directly breaking a governed operation.
- The DB is append-only / versioned (`UNIQUE(id, version)`, no UPDATE / DELETE), so it grows monotonically. Corroborating retained magnitudes measured live: 12,602 deliberation rows, 2,435 current specifications, 4,578 current work items (plus all versioned history behind the `current_*` views).
- Compounding: WI-5659 recorded a 50.7 min → 17 s prospective-tree fix and a 460.8 s → 9.6 s 472-packet resolution; bridge-publication currentness checks and prospective-tree subprocess storms scale with DB size.

### Case 4 — Control-plane aggregate under a single global lock: per-publication cost AND contention both grow with SoT size

Evidence (`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`):
- A single lock `.gtkb-state/sot-registry/control-plane.lock` (line 250) with `_RegistryFileLock(timeout=30.0)` (line 255) serializes access; on timeout it raises `TimeoutError("timed out acquiring registry lock ...")` (line 283).
- The lock wraps the authority read barrier (line 785) **and every** generation commit (lines 1399, 1591, 1712). Each mint recomputes a generation digest over the **growing aggregate** (`aggregate_digest` line 552; `aggregate_entry_id` / `aggregate_preimage_digest` lines 698-699).
- As the aggregate grows, each mint does more work while holding a lock more sessions contend for. Observed hard-fail telemetry: WI-5788 (registry-lock timeout), DELIB-202667526 (convoy), WI-5758 (currentness deadlock).
- **Live corroboration:** any registry control-plane lock contention encountered while publishing this very advisory is itself Case-4 evidence; the worker's per-attempt filing retry telemetry is reported to the leader alongside this advisory.

### Case 5 — Deliberations corpus growth

Measured live (read-only): **12,509** current deliberations (`current_deliberations`); **12,602** total append-only rows (`deliberations`). Of these, **9,130** fall in the `DELIB-2026%` timestamp era, magnitude up to **DELIB-202667697**. The leader observed ~160 records added in one working window (DELIB-202667534 → DELIB-202667697).

`gt deliberations search` runs a semantic (ChromaDB) query plus SQLite queries over the full append-only corpus + index; there is no prune / tier route (append-only), so search latency grows with the never-pruned corpus.

## Cross-Cutting Structural Pattern

These are not five isolated bugs but one pattern: **monotonic append-only SoT access cost**. Cases 1 (wi5668 wedge / WI-5739), 3 (WI-5659 finalization break), and 4 (registry-lock hard timeouts / WI-5788) have already crossed thresholds that break governed operations; Cases 2 and 5 are severe-and-worsening latency. Candidate correction DIRECTIONS (named, not designed — each is a future governed correction requiring its own owner-approved proposal, and each must preserve append-only as the SoT default per DELIB-202667697):

- Case 1: resolver bounds / chain-length caps / checkpointing — resolve from a validated checkpoint rather than re-validating full history, and quarantine a broken head without wedging the thread.
- Case 2: bridge-directory archival tiering or indexed bridge state — stop enumerating the full directory per read.
- Case 3: DB compaction / snapshotting or blob externalization — bound governed-operation inputs independent of total DB size.
- Case 4: per-thread or sharded locks replacing the single control-plane lock; incremental generation digest instead of whole-aggregate recompute.
- Case 5: deliberation corpus tiering — hot / cold split and a bounded semantic-search working set.

## Owner Decision Needed

This advisory decides nothing and requires no approval to file; it presents options for the owner to weigh:

1. **Which cases to convert to correction proposals**, and in what priority order. Suggested triage: threshold-crossed breakers first (Case 1 wedge / WI-5739; Case 3 DB size / WI-5659; Case 4 lock / WI-5788), then the worsening-latency cases (Case 2, Case 5).
2. **Scope discipline:** confirm any correction preserves append-only as the SoT default (DELIB-202667697) and treats these as access-path / representation corrections, not mutable-in-place conversions.
3. **Batching:** whether to pursue per-case proposals or a single umbrella program with per-case slices.

## Recommended Prime Action

Per-case recommended default disposition (each subject to owner selection through the advisory-intake owner-grilling gate before any implementation proposal is filed):

- **Case 1 (bridge resolver O(n) + O(dir) + wedge):** convert to implementation proposal. Highest leverage — already wedging live threads (WI-5739) and taxing every publication.
- **Case 2 (bridge directory enumeration):** convert to implementation proposal (indexed bridge state / archival tiering); pairs naturally with Case 1's `iterdir` scan.
- **Case 3 (DB size vs finalizer ceiling):** convert to implementation proposal — already a proven governed-operation breaker (WI-5659).
- **Case 4 (single control-plane lock):** convert to implementation proposal — live contention observed (WI-5788 and this filing's retry telemetry).
- **Case 5 (deliberation corpus):** monitor now; convert when search latency crosses an owner-set threshold. Lowest current breakage.

## Classification Slot

Recommended default classification per case (owner may override):

| Case | Recommended | Rationale |
|---|---|---|
| 1 — bridge resolver | adopt (correct the case) | Live wedge (WI-5739) + per-publication O(n)+O(dir) tax |
| 2 — bridge dir enumeration | adopt (correct the case) | Content reads time out; scales with 14,098 files |
| 3 — DB size | adopt (correct the case) | 12.6× finalizer ceiling; proven breaker (WI-5659) |
| 4 — control-plane lock | adopt (correct the case) | Live hard timeouts during governed filings (WI-5788) |
| 5 — deliberation corpus | monitor | Worsening latency; not yet a hard breaker |

"adopt (correct the case)" = adopt the direction of correcting the case; the concrete design is deferred to each future proposal and its own owner grilling.
