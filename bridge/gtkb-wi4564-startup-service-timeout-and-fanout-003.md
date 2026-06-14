REVISED

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T19-25-14Z-prime-builder-B-370c5f
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m; headless bridge auto-dispatch (GTKB_BRIDGE_POLLER_RUN_ID set)

Project Authorization: PAUTH-PROJECT-GT-KB-INFRASTRUCTURE-WI-4564-STARTUP-SERVICE-TIMEOUT-ALIGNMENT-INNER-COST-A-C
Project: PROJECT-GT-KB-INFRASTRUCTURE
Work Item: WI-4564
target_paths: ["scripts/session_start_dispatch_core.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/scripts/test_session_self_initialization.py"]
bridge_kind: prime_proposal

# Implementation Proposal (REVISED) — WI-4564: Startup-service timeout alignment + inner-cost reduction (A+C)

- **Bridge thread:** `gtkb-wi4564-startup-service-timeout-and-fanout`
- **Version:** 003
- **Status:** REVISED
- **Bridge kind:** prime_proposal
- **Work Item:** WI-4564
- **Project:** PROJECT-GT-KB-INFRASTRUCTURE
- **Author:** prime-builder / claude (Opus 4.8 [1m]), harness B, headless auto-dispatch `2026-06-14T19-25-14Z-prime-builder-B-370c5f`
- **Responds to:** `bridge/gtkb-wi4564-startup-service-timeout-and-fanout-002.md` (NO-GO)
- **target_paths:** `["scripts/session_start_dispatch_core.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/scripts/test_session_self_initialization.py"]`

## Response to NO-GO (-002)

The -002 NO-GO raised one blocking finding (F1): the live `work_items` row for `WI-4564` still described the earlier **A+B / `PROJECT-GTKB-RELIABILITY-FIXES`** scope (and still expected the dropped Part B sync-exclusion work), while this proposal and its active PAUTH describe the owner-approved **A+C / `PROJECT-GT-KB-INFRASTRUCTURE`** scope. The reviewer noted *"Owner Action Required: None — Prime Builder can revise the bridge/current-work metadata under the existing owner decision and PAUTH path."* This REVISED addresses all four required revisions; the technical implementation (Parts A and C) is unchanged from -001.

| Required revision (-002) | Disposition in -003 |
|---|---|
| **1. Reconcile the live `WI-4564` current-work record to the A+C scope** (or cite a governed supersession/deferral). | **Done.** Appended `WI-4564` **v2** (`changed_by=prime-builder/claude`) under standing-backlog grooming authority + DELIB-20263378 + the active PAUTH: `project_name` set to `PROJECT-GT-KB-INFRASTRUCTURE`; description/acceptance_summary rewritten to A+C (Part B explicitly noted as pre-existing and out of scope); `approval_state` set to `auq_resolved`; `related_deliberation_ids = DELIB-20263378`; `related_bridge_threads = gtkb-wi4564-startup-service-timeout-and-fanout`. No resolution/closure — `stage=backlogged`, `resolution_status=open` (no GOV-15 gate triggered). |
| **2. Align project/work metadata with the live work-item authority.** | **Done.** The reconciled v2 row carries `project_name=PROJECT-GT-KB-INFRASTRUCTURE`. `WI-4564` is also a first-class member of `PROJECT-GT-KB-INFRASTRUCTURE` (via `projects add-item`), and the active PAUTH is listed under that project. The scalar column, the project membership, and the PAUTH now agree. |
| **3. Replace the stale "Owner Decisions" paragraph (pre-implementation-steps language) with the durable decision + PAUTH evidence.** | **Done.** See the rewritten `## Owner Decisions / Input` below — it cites `DELIB-20263378` and the active PAUTH id directly and removes the obsolete "Archival … and minting … are pre-implementation steps" wording, since both already exist as durable records. |
| **4. Re-run applicability, ADR/DCL clause, and citation-freshness preflights on the revised proposal.** | **Done.** Results recorded in `## Preflight Evidence (-003)` below (run after this file was filed/INDEX-updated). |

**KB-mutation scope note.** The WI-4564 v2 reconciliation above was a one-time backlog-grooming write completed *before* this REVISED was filed (standing-backlog authority + DELIB-20263378 + the active PAUTH). The GO-authorized implementation phase (Parts A and C) **performs no MemBase mutation** and writes nothing to `groundtruth.db`; it edits only the four source/test files in `target_paths`. `target_paths` therefore intentionally excludes `groundtruth.db`, consistent with the PAUTH's allowed mutation classes (`source`, `test_addition`) and its forbidden operations (`deployment`, `sync_configuration_change`).

## Summary

The SessionStart payload generator intermittently times out, producing the "GroundTruth-KB Startup Service Degraded" fallback. This proposal implements the owner-approved **A+C** scope to make degraded startups rare: **Part A** aligns the inner subprocess timeout to the hook's async budget and makes it env-configurable; **Part C** reduces the inner per-startup cost (one fewer interpreter relaunch; deduplicated git metadata calls) so the bound is rarely approached. The outer subprocess crash-isolation boundary is preserved.

## Problem / Evidence

Measured during session B-2026-06-14 (each claim reproduced directly):

- The exact failing command (`session_self_initialization.py --emit-startup-service-payload --fast-hook ...`) runs in **4.8 s** in isolation — **not** inherently slow. Of that, ~2.1 s is 11 `subprocess.run` calls (git + one child-Python) and ~2.7 s is in-process model-building.
- `scripts/session_start_dispatch_core.py:52` sets `STARTUP_SERVICE_TIMEOUT_SECONDS = 50.0`, used as the subprocess `timeout` at line 686; on timeout it emits the degraded payload (line 243). The SessionStart hook registration carries `asyncTimeout: 180000` (180 s). **The 50 s inner bound fires ~3.6× short of the 180 s budget the harness would otherwise allow.**
- Disproven prior hypotheses (recorded so they are not re-litigated): canonical `groundtruth.db` is **224 MB** (the 1.3 GB file is the `archive/worktrees/musing-hoover-35dd81/` copy); `E:` is a **local internal SSD** (`DriveType=3`), not a cloud filesystem; `backlog list --json` = **1.7 s**; `import groundtruth_kb` = **0.08 s**. DB size and package import are not the bottleneck.
- The repo is a Google Drive mirror (`.driveignore` present); the corruption/perf-sensitive paths (`.git/`, `groundtruth.db[-wal/-shm]`, `.groundtruth-chroma/`, `.gtkb-state/`, `*.lock`) are **already excluded** (S311 SQLite + 2026-05-29 git-gc incidents). OneDrive does not watch `E:\GT-KB`. So the originally-considered "Part B" (add sync exclusions) is already implemented — it is intentionally **not** in scope here.
- Root cause: intermittent **cold-start contention** — `git status --porcelain` (and ~15 serial git calls total) scan the Drive-synced working tree while a dirty tree is being uploaded, occasionally pushing total time past the 50 s cutoff even though the work is ~5 s warm.

## Specification Links

- **GOV-RELIABILITY-FAST-LANE-001** — Part A (the timeout constant change) is a small, reversible reliability defect fix in the fast-lane class; this proposal carries the change through full bridge review rather than claiming the fast-lane exemption, but the spec governs the fix's reliability framing.
- **GOV-SESSION-SELF-INITIALIZATION-001** — the startup service implements the mandated fresh-session self-initialization disclosure; the fix preserves that contract (degraded mode remains the fallback, not the norm).
- **DCL-SESSION-STARTUP-TOKEN-BUDGET-001** — startup cost constraint; Part C reduces per-startup subprocess cost, consistent with the budget intent.
- **PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001** — the payload delivers the governance/role disclosure; the fix increases the probability the full (non-degraded) disclosure is delivered.
- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** — degraded mode forces fallback to live-INDEX reads; reducing degraded events improves the freshness of the disclosed startup state without weakening the live-read discipline.

Cross-cutting bridge-governance specs (always applicable to bridge proposals):

- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file-bridge protocol; `bridge/INDEX.md` remains canonical workflow state and the append-only audit trail is preserved.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal cites every relevant governing specification (above) per the mandatory-linkage constraint.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan below derives tests from the linked specifications; `VERIFIED` will require executed spec-derived test evidence.

Artifact-oriented governance specs (advisory):

- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** — the fix is preserved as a durable artifact network (WI-4564, DELIB-20263378, the bounded PAUTH, this proposal) rather than chat-only context.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** — same artifact-network framing for the decision + rationale.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** — the capture→propose lifecycle triggers were exercised (owner-decision capture, work-item creation, work-item reconciliation, proposal filing).
- **GOV-STANDING-BACKLOG-001** — the WI-4564 v2 reconciliation is standing-backlog grooming under the canonical `work_items` authority; it aligns the backlog record to the owner-approved decision without granting new implementation authority.

## Prior Deliberations

_No prior deliberations found: searched "startup payload subprocess timeout degraded session start" and "google drive onedrive sync exclusion git repo performance driveignore" — both returned no matches (novel topic). Related-but-distinct cache-freshness cluster (not superseded): WI-3447, WI-3486, WI-3456; prior measurement thread `gtkb-startup-payload-budget-report` (VERIFIED). Governing owner decision for the A+C scope: `DELIB-20263378`._

## Requirement Sufficiency

**Existing requirements sufficient.** The governing specifications above (reliability fast-lane framing, self-initialization disclosure contract, startup token budget, freshness discipline) are sufficient to constrain this fix; no new or revised requirement is required before implementation. The change is corrective (a defect in the timeout bound + an efficiency reduction), not a new capability surface.

## Proposed Implementation

### Part A — env-configurable, budget-aligned inner timeout
- In `scripts/session_start_dispatch_core.py`, change `STARTUP_SERVICE_TIMEOUT_SECONDS = 50.0` to read `GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS` from the environment with a raised default of **150.0** (≈30 s margin under the 180 s `asyncTimeout`, leaving headroom for the dispatch-core post-subprocess cache writes).
- Preserve the outer subprocess + timeout + degraded-fallback structure (crash isolation and a bounded wait are retained — only the bound value and its configurability change).

### Part C — reduce inner per-startup cost
- In `scripts/session_self_initialization.py`, replace the child-Python `subprocess.run([sys.executable, "-m", "groundtruth_kb", "backlog", "list", "--json"], ...)` (≈line 1235) with an **in-process call** to the same backlog API that `groundtruth-kb/src/groundtruth_kb/cli.py` invokes for `backlog list --json` (the package import is already 0.08 s; this removes a full child-interpreter relaunch). Preserve the existing try/except fail-soft (return `[]` on error) so a backlog read failure never aborts the payload.
- Compute git `branch` / `HEAD` / `short-sha` / `status --porcelain` **once** and thread the values to the ~15 call sites that currently recompute them (e.g., lines 1623, 1721, 1873–1877, 3017–3020). No behavior change to the emitted payload; fewer serial git invocations under the cold-tree filter-driver tax.

### Rejected alternative (documented)
- **Fully in-process payload execution** (call `build_startup_model` directly in `session_start_dispatch_core.py` via the existing `_render_role_startup_report` path at line 530, eliminating the outer subprocess). Rejected for this slice: it dismantles the deliberate crash-isolation + bounded-timeout boundary and would require a Windows-portable in-process watchdog to retain those properties. Higher risk than warranted given Part A already provides generous budget headroom.

## Spec-Derived Verification Plan

| Specification | Derived test / check |
|---|---|
| GOV-RELIABILITY-FAST-LANE-001; PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 | `platform_tests/scripts/test_session_start_dispatch_core.py`: assert `STARTUP_SERVICE_TIMEOUT_SECONDS` resolves from `GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS` when set (parse to float) and falls back to the 150.0 default when unset/invalid. |
| DCL-SESSION-STARTUP-TOKEN-BUDGET-001; GOV-SESSION-SELF-INITIALIZATION-001 | `platform_tests/scripts/test_session_self_initialization.py`: assert the backlog fetch path no longer spawns a child interpreter (no `-m groundtruth_kb` subprocess in the backlog fetch) and still returns the same item shape; assert git metadata is computed once (call-count assertion on the git helper). |
| GOV-SESSION-SELF-INITIALIZATION-001 (regression) | Run the full `--emit-startup-service-payload --fast-hook` path and assert a valid (non-degraded) payload is emitted; assert wall time is ≤ prior baseline. |
| Code quality | `ruff check` AND `ruff format --check` on both changed `.py` files (separate gates). |

Commands: `python -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_session_self_initialization.py -q`; `ruff check <files>`; `ruff format --check <files>`.

## Risk / Rollback

- **Risk (A):** a longer bound means a pathological cold-start could now occupy up to ~150 s before degrading. Mitigation: the hook is async (non-blocking to the user); the disclosure simply arrives when ready within the 180 s budget. Reversible by env override or reverting the default.
- **Risk (C):** moving the backlog read in-process removes child-process fault isolation for that one read. Mitigation: the existing try/except fail-soft is preserved (returns `[]`), so a backlog failure degrades one payload field, not the whole payload. Git-call dedup is behavior-preserving (same values, fewer calls).
- **Rollback:** revert the two files; no schema, migration, or persisted-state change. `GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS` can also pin the prior 50 s behavior without a code change.

## Recommended Commit Type

`fix:` — corrects a reliability defect (premature inner-timeout cutoff) with an accompanying efficiency reduction; no new capability surface. (Diff is two scripts + two test files; net behavior is corrective.)

## Owner Decisions / Input

This proposal depends on owner approval. The owner decision authorizing the A+C scope is durably recorded; this REVISED cites the durable records directly (the obsolete "pre-implementation steps" wording from -001 is removed because those records already exist):

- **Durable owner decision:** `DELIB-20263378` (`source_type=owner_conversation`, `title="Owner decision: startup-service timeout fix scope (WI-4564, A+C)"`) — owner approved the A+C scope: env-configurable budget-aligned inner startup timeout (A) plus inner-cost reduction (C); Part B sync-exclusions already implemented in `.driveignore`, so out of scope.
- **Bounded project authorization:** `PAUTH-PROJECT-GT-KB-INFRASTRUCTURE-WI-4564-STARTUP-SERVICE-TIMEOUT-ALIGNMENT-INNER-COST-A-C` — active; cites `DELIB-20263378`; includes `WI-4564`; allows mutation classes `source` and `test_addition`; forbids `deployment` and `sync_configuration_change`. The proposal's `target_paths` are within the authorized source/test scope.
- **Originating AUQ evidence (session B-2026-06-14), captured into the above DELIB:** AUQ-1 "How should I pursue the long-term fix?" → owner **"Layered A+B (recommended)"**; AUQ-2 (re-scope after evidence Part B was already implemented) "How should I re-scope?" → owner **"A + C together"**.

No new owner decision is required for this REVISED: the -002 NO-GO recorded "Owner Action Required: None," and the WI-4564 v2 reconciliation was performed under the existing DELIB + PAUTH path the reviewer authorized.

## Preflight Evidence (-003)

Recorded after filing this version and updating `bridge/INDEX.md` (so the preflights resolve the operative `-003` file):

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4564-startup-service-timeout-and-fanout`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4564-startup-service-timeout-and-fanout`
- `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-wi4564-startup-service-timeout-and-fanout`

Expected: `preflight_passed: true`, `missing_required_specs: []`, `Blocking gaps (gate-failing): 0`, `No stale cross-thread citations detected.` Actual run results are recorded in this dispatch's closing report.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
