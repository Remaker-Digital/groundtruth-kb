NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; this filing is a Prime Builder proposal-authoring act (envelope pb); authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5742-bound-protected-commit-evaluation
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5742

target_paths: ["scripts/check_protected_commit_authorization.py", "scripts/controlled_artifact_paths.py", "scripts/implementation_authorization.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/timer_config.py", "config/governance/protected-commit-timers.toml", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_protected_commit_evaluation_bound.py", "platform_tests/scripts/test_bridge_publication_finalization_atomicity.py"]
implementation_scope: bounded_protected_commit_evaluation_and_stranding_prevention
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5742 Implementation Proposal — Bound Protected-Commit Full Evaluation and Prevent Stranded VERIFIED Publication

## Summary

HEAD has been frozen at `8a35eabc8` for days. Every governed VERIFIED finalization fails the same way: the bridge-publication capability is minted with a 120-second default TTL under a hard 300-second ceiling, then pre-commit gate 5 (`scripts/check_protected_commit_authorization.py --staged`) runs unbounded for minutes while holding the single global control-plane lock. The capability expires mid-gate, the parent `git commit` dies, compensation cannot restore the aggregate preimage because sibling threads appended in the interim, the capability row lands in `recovery_required`, and the terminal VERIFIED verdict is left file-only with no backing commit.

This proposal fixes the defect in the three layers that jointly produce it: **(a)** a fail-closed, configuration-sourced wall-clock bound on the full staged evaluation so the gate can never hang; **(b)** three measured cost reductions that make the gate fit inside that bound with wide margin; and **(c)** a reordering of the publication transaction so capability lifetime is no longer coupled to gate duration, which is what structurally guarantees no future stranding. It also closes the second half of the work item's title: on gate failure the transaction must leave no terminal VERIFIED file and no poisoned capability row.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5742-bound-protected-commit-evaluation-001.md`, continuing the append-only versioned bridge file chain. No prior version is deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads and measurements, 2026-07-31)

Every claim below was re-derived or measured this session against the live worktree. Line numbers are current-worktree references. Measurements were taken with the project virtual environment interpreter.

### 1. The capability TTL and its hard ceiling

`mint_bridge_publication_capability` (`registry_control_plane.py` line 2641) takes `ttl_seconds: int = 120` (line 2655) and enforces `if ttl_seconds <= 0 or ttl_seconds > 300: raise RegistryAuthorizationError(...)` (lines 2663-2664). Expiry is stamped at mint time as `created + timedelta(seconds=ttl_seconds)` (line 2711). The capability is therefore dead at most 300 seconds after minting, no matter what the commit path does afterwards.

### 2. The gate is unbounded

`main()` (line 2425) calls `evaluate()` (line 2385), which enters `_index_snapshot` and then `_evaluate_selected` (line 2290). There is a per-subprocess Git timeout (`_GIT_SUBPROCESS_TIMEOUT_SECONDS = 120`, line 287), but **no outer bound on the evaluation as a whole**. Nothing terminates a long evaluation; it simply runs to completion while the parent commit waits.

### 3. Measured cost driver #1 — packet evidence: 104s wall / 92s CPU in one call

`_evaluate_selected` calls `_load_live_go_evidence(root)` (line 2332) whenever any protected path is present. That calls `list_named_packets(root)` (`implementation_authorization.py` line 2766), which iterates **every** packet under `.gtkb-state/implementation-authorizations/by-bridge/` and, per packet, runs `_validate_packet` (line 2540 — which calls `_packet_go_integrity` plus `bridge_entry`, resolving that thread's full lifecycle chain) **and** `assess_packet_terminal_evidence` (line 2814 — a second full evidence resolution).

Measured this session:

```text
_load_live_go_evidence:          wall=104.54s cpu=91.91s   n=2 valid packets
_committed_bridge_entries_by_id: wall=0.36s   cpu=0.27s    n=2300 entries
_load_verified_evidence(2 paths):wall=4.26s   cpu=1.50s    n=5
```

The gate spends ~92 CPU-seconds resolving bridge chains for **524** packets in order to find **2** live ones, across a `bridge/` directory holding **14,390** files. Notably, `_committed_bridge_entries_by_id` is cheap (0.36s) — the WI-5658 hoist already fixed that one; it is **not** a current driver, and this proposal does not touch it.

### 4. Measured cost driver #2 — uncached, exclusively-locked snapshot loads, once per path

`_evaluate_selected` line 2296 evaluates `is_protected_path(path, project_root=root)` inside a list comprehension over every selected path. That reaches `classify_controlled_artifact` (`controlled_artifact_paths.py` line 120) → `_registry_classification` (line 107) → `load_registry_snapshot` (line 112) — **with no caching anywhere**. `load_registry_snapshot` (`registry_control_plane.py` line 824) acquires `_RegistryFileLock` (line 837) and then parses the registry TOML and queries the SQLite store.

Measured this session:

```text
toml_bytes 1550756        (1.55 MB registry TOML)
db_bytes   844025856      (844 MB store, 2348 current_sot_artifacts rows)
load#0 wall=8.510s cpu=0.438s   (cold)
load#1 wall=0.781s cpu=0.375s   (warm)
load#2 wall=0.925s cpu=0.484s   (warm)
```

The store is read here strictly for classification; this read path performs no write, insert, or mutation of any kind. `_registry_commit_assessment` (line 2105) then performs one further `load_registry_snapshot` (line 2132). For an N-path staged set the invocation performs up to **N+1** full snapshot loads.

### 5. The lock is exclusive and read paths take it — reproduced live

`_RegistryFileLock` (line 254) is an **exclusive** lock (`msvcrt.LK_NBLCK` / `fcntl.LOCK_EX`, lines 271-278) with `timeout: float = 30.0` (line 255), raising `TimeoutError(f"timed out acquiring registry lock {self.path}")` on expiry (line 283). Because `load_registry_snapshot` takes this exclusive lock for a **pure read**, per-path classification serializes the gate against every other control-plane user.

This is not theoretical. An attempt to profile `_evaluate_selected` this session failed with the verbatim error:

```text
TimeoutError: timed out acquiring registry lock E:\GT-KB\.gtkb-state\sot-registry\control-plane.lock
```

raised from `is_protected_path` → `classify_controlled_artifact` → `_registry_classification` → `load_registry_snapshot` → `_RegistryFileLock.__enter__`. A *classification question* failed because it could not obtain a *mutation* lock. This is the mechanism behind the divergence between measured wall time and CPU time: under sibling contention each of the N+1 acquisitions can block up to 30 seconds before either succeeding or failing the whole gate.

### 6. The stranding outcome

Because publication happens **before** the commit gates run, a gate that outlives the capability leaves the transaction torn. Compensation then fails at `registry_control_plane.py` line 3484-3485 when the aggregate preimage no longer matches, with the verbatim failure `bridge publication aggregate preimage cannot be restored exactly`, and `_mark_bridge_publication_recovery_required_with_observation` moves the row to `recovery_required` (lines 3486-3496). The WI-5742 `status_detail` records the same shape for the WI-5368 recurrence: the terminal verdict was physically published and the capability row consumed before any backing commit existed, HEAD never moved, and the physical chain later ended one version short.

The same signature is on record across `wi5758`, `wi5759`, `wi5824`, and eleven incident directories under `bridge/cleanup-evidence/`.

### 7. The defect is currently blocking its own neighbours

`bridge/gtkb-wi5824-protected-commit-checker-null-safety-ordering-004.md` is a **NO-GO** whose sole finding (F1) is *"Implementation-start packet expired at `2026-07-31T07:51:23Z`"*, with the verdict text recording *"Prior finalize attempts failed on bridge-publication aggregate repair / registry lock"*. WI-5824 is therefore itself a casualty of this defect: its packet expired while finalization repeatedly failed on the slow gate and the contended lock. Unblocking WI-5742 unblocks that thread's finalization path as well.

## Proposed Design

Three layers. Layers (a) and (b) are independently valuable; layer (c) is what makes stranding structurally impossible rather than merely unlikely.

### Layer A — Bound the full staged evaluation (fail-closed, configuration-sourced)

Wrap the whole of `evaluate()` in a monotonic wall-clock budget. On exhaustion the gate **denies** — it never passes on timeout and never hangs.

- **Value source.** No hard-coded literal is introduced. Per DELIB-202667722 and WI-5806, the bound is resolved through a single new resolution path, `groundtruth-kb/src/groundtruth_kb/project/timer_config.py`, reading `config/governance/protected-commit-timers.toml` with documented units and a relaxed-first default. Resolution precedence is env-local override (per GOV-ENV-LOCAL-AUTHORITY-001) → config file → in-code relaxed fallback constant used only when the config surface is absent.
- **Invariant-coupled pair.** WI-5806 requires invariant-coupled timers to be externalized *together* so independent tuning cannot break the invariant. The gate bound and the bridge-publication capability TTL are exactly such a pair: if the bound can exceed the TTL, publications strand. Both values are therefore externalized in the same config surface, and `timer_config.py` exposes a validated accessor that **refuses to return a bound greater than the capability TTL** it is paired with. This makes the stranding precondition unrepresentable in configuration.
- **Relaxed-first defaults.** Initial values start at the most relaxed tolerable posture, not at the measured optimum: the proposal's starting point is a gate bound comfortably above post-Layer-B measured cost and strictly below the paired capability TTL, with the tolerance bound documented inline in the config file.
- **Deterministic deny with phase evidence.** The evaluation records phase markers (`index_snapshot`, `classification`, `registry_assessment`, `live_go_evidence`, `verified_evidence`, `transaction_evidence`, `per_path`). On exhaustion the gate emits a deterministic failure naming the phase that was executing, the elapsed budget, the configured bound, and the remediation, rather than a bare timeout. The message is actionable text, not a stack trace.

### Layer B — Make the gate cheap enough to fit (three measured reductions)

**B1 — Per-invocation registry snapshot cache.** Introduce a process-scoped memoization for `load_registry_snapshot` keyed on resolved registry paths, so one gate invocation performs **one** snapshot load instead of N+1. This removes N exclusive-lock acquisitions per invocation, which is the contention amplifier reproduced in §5 as well as a CPU cost. Cache lifetime is strictly the invocation; the cache is not persisted across processes and no stale-read window is introduced for mutating callers, which continue to load under the lock as they do today.

*Expected reduction, from measurement:* for a 12-path set, from ~8.5s cold + 12 × ~0.9s ≈ **19s wall / ~5 CPU-s** down to a single ~8.5s cold load — and, more importantly, from 13 exclusive-lock acquisitions to 1.

**B2 — Cheap pre-filter before expensive packet validation.** `_load_live_go_evidence` currently runs two full bridge-chain resolutions per packet across all 524 packets to find 2 live ones. Add a pure-JSON pre-filter that reads each packet's `expires_at` and `target_path_globs` and admits a packet to expensive validation only if it is (i) unexpired and (ii) glob-matching at least one currently-selected path. Packets failing the cheap filter cannot authorize anything in this evaluation, so excluding them cannot change the verdict; expired packets are additionally surfaced in the existing error/evidence channels so the fail-closed reporting surface is unchanged.

*Measured selectivity, this session:*

```text
prefilter wall=0.13s cpu=0.12s
total=524 unparseable=0 unexpired=4 unexpired_and_pathmatch=0
```

A **0.12 CPU-second** pass reduces the expensive-validation set from 524 packets to **4** — a ~99.2% reduction in bridge-chain resolutions, projecting the dominant ~92 CPU-second phase to well under one CPU-second.

**B3 — Single classification pass; no duplicated assessment.** Compute each selected path's classification exactly once and reuse it for both the `protected_paths` and `skipped_unprotected` partitions (line 2296-2297 currently re-scans). Keep `_registry_commit_assessment` to exactly one call per invocation and have `_registry_commit_findings` (line 2279, the compatibility view) delegate to that single result rather than triggering an independent second assessment for any caller that runs both.

Layers B1-B3 together are expected to take the dominant measured cost of the gate from roughly two minutes of CPU to a few seconds, which is what allows the Layer A bound to be set well below the paired capability TTL while leaving wide headroom.

### Layer C — Decouple capability lifetime from gate duration

Layer A guarantees the gate terminates; Layer B makes it fast. Neither, alone, guarantees that a *slow-but-passing* gate cannot strand a publication. Three options were considered.

- **C-i — Extend or renew the capability across the commit transaction (heartbeat).** Keeps the current publish-before-commit ordering and adds a renewal path that refreshes `expires_at` while the commit is in flight. *Rejected as primary.* It preserves the torn-state window rather than removing it: a crash, a signal, or a lock timeout between renewals still leaves a published terminal file with no commit. It also adds a liveness mechanism to a path whose failure mode is precisely that liveness assumptions were violated.
- **C-ii — Acquire the capability after the gates pass (late mint / commit-before-terminal-visibility).** Run the full commit-gate preflight *first*, and mint-and-consume the publication capability only once the gates have passed, immediately before the commit that makes the terminal artifact visible. *Recommended.* The capability's lifetime then covers only the short, bounded publish-and-commit step, never the long evaluation. This is the direction the work item's own `status_detail` names: *"Required correction is commit-before-terminal visibility or one exact resumable transaction."* It removes the failure class rather than shortening the window.
- **C-iii — Make compensation robust to the expired-during-commit case.** Allow compensation to succeed when the aggregate preimage has legitimately moved due to sibling appends, instead of failing with `bridge publication aggregate preimage cannot be restored exactly` and poisoning the row. *Recommended as a required safety net, not as the primary fix.* Even with C-ii the process can die between mint and commit, so compensation must be able to unwind cleanly; C-iii is what makes the residual window recoverable instead of `recovery_required`.

**Recommendation: C-ii as the primary structural fix, with C-iii as a mandatory companion.** Note explicitly that **raising the TTL alone is not a candidate**: the 300-second hard ceiling at line 2663 is structurally below the measured ~720-second failing gate cost, so no legal TTL value can cover the current gate. Layer B is what makes any TTL-based reasoning viable at all, and C-ii is what makes it unnecessary.

### Stranding prevention (the work item's second clause)

The transaction must be all-or-nothing from the perspective of durable, dispatcher-visible state. On any gate failure — including Layer A bound exhaustion — the outcome must be: **no terminal VERIFIED file on disk, no consumed-or-minted capability row left behind, and no `recovery_required` row created.** Concretely: with C-ii the terminal file is not written until the gates have already passed, so a gate failure leaves nothing to unwind; and where an unwind is still required (failure after mint), C-iii guarantees it completes to a clean terminal state rather than to `recovery_required`. The append-only numbered bridge chain is never rewritten in either path.

### Rejected alternatives

- **Raise the capability TTL.** Structurally impossible within the 300-second ceiling, and treats a symptom. Rejected.
- **Remove or weaken the gate for finalization commits.** Would trade a liveness defect for an authorization hole; the gate is the protected-commit control. Rejected outright.
- **Cache the registry snapshot globally across processes.** Introduces a stale-authority window for mutating callers, which is a correctness risk in a control plane. Rejected in favour of the invocation-scoped B1 cache.
- **Convert the control-plane lock to a shared/read lock as part of this work.** The right long-term fix for read-path serialization, but it is WI-5715 and WI-5788 scope and would collide with them. This proposal deliberately reduces the *number* of acquisitions (B1) rather than changing lock *semantics*.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — append-only numbered bridge chain and bridge audit-trail authority; the stranding-prevention design exists to keep the chain and its backing commits convergent, and no chain file is rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own linkage obligation: every relevant governing specification is cited in this section, and the derived tests below map back to those citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs downstream verification; the Specification-to-Test Mapping below is the derivation record the Loyal Opposition verifier executes against.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — governs the project-scoped authorization chain whose packet lifetime and gate interaction this proposal repairs; the PAUTH triple in the header proceeds under it.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — required (blocking) — the WI-5742 source specification; operation-time enforcement is exactly the property violated when a capability expires mid-operation.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — required (blocking) — governed Git lifecycle; this work restores the ability of a governed finalization to produce a backing commit.
- `GOV-WORK-TREE-HYGIENE-001` — required (blocking) — worktree hygiene; a frozen HEAD with accumulating file-only terminal verdicts is the hygiene failure being cleared.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is mutated by this implementation; bridge artifacts and the PAUTH chain remain under the approval gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every target path is in-root under the mandatory project root; no application subtree and no out-of-root dependency is touched.
- `GOV-ENV-LOCAL-AUTHORITY-001` — required (blocking) — scopes the env-local layer of the timer resolution precedence introduced in Layer A.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the protected-commit gate is a mechanical enforcement layer; this work preserves its fail-closed posture while making it terminate.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — all evidence here derives from fresh canonical reads and measurements made this session.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — the bound, the phase evidence, and the timer resolution path replace per-incident manual diagnosis with a deterministic service surface.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes (termination, verdict identity, absence of orphan artifacts and poisoned rows), not structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — phase evidence and the config surface are durable artifacts rather than transient session state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability across proposal, config, tests, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions for WI-5742 follow the recorded trigger classifications.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5742 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667721`, `DELIB-202667734`, `DELIB-202667722`, `DELIB-202667723`, `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with parallel-operation program: the owner mandate under which this proposal-author worker files this NEW entry.
- **DELIB-202667721** — Owner authorization of the list-free whole-project PAUTH for PROJECT-GTKB-HOUSEKEEPING-HARDENING, recorded as the authorization cited in this proposal's header.
- **DELIB-202667734** — Owner decision repairing inert whole-project PAUTH envelopes by removing the unregistered mutation-class token; this is why the authorization cited here is currently operative rather than deny-everything.
- **DELIB-202667722** — Timer and throttle governance as a first-class concern with relaxed-first defaults: the direct authority for sourcing the Layer A bound from configuration instead of a hard-coded literal, and for the relaxed-first starting posture.
- **DELIB-202667723** — Terminal-evidence sufficiency for expired implementation-start packets: directly adjacent to the failure mode in §7, where an expired packet blocked a VERIFIED that had already been substantively reviewed.
- **DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS** — Exact recovery of stranded WI-5670 and WI-5588 terminal transactions: the WI-5742 `source_deliberation_query`, recording the recovery discipline this proposal is designed to stop needing.
- All deliberation, specification, and work-item IDs cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase; bridge chain states were verified by direct first-line status-token reads of the numbered files. `TEST-5742` was checked and is an **unrelated** record ("mcp repos missing"); it is deliberately **not** cited as this work item's test anchor, and WI-5742 carries a null `source_test_id`.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5742. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667721 / DELIB-202667734** — the owner's list-free whole-project grant recorded as PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 covers WI-5742 as a member work item. Verified fresh this session: the envelope is active, carries no expiry, and its `allowed_mutation_classes` correctly excludes the unregistered `git_commit` token repaired under DELIB-202667734. Per the PAUTH scope, this work item still requires its own full governed cycle: this proposal, independent Loyal Opposition GO, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
3. **DELIB-202667722** — the owner's timer-governance decision constrains Layer A to a configuration-sourced, relaxed-first bound. No additional owner decision is required to review this proposal, and this proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5742 title, description, `status_detail`, and `acceptance_summary` (fresh-read verified via `gt backlog show WI-5742 --json`), together with DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001, GOV-WORK-TREE-HYGIENE-001, GOV-ENV-LOCAL-AUTHORITY-001, and the DELIB-202667722 timer-governance decision, fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

WI-5742 carries no existing test anchor, so the derived tests are created with the implementation per GOV-12. Existing coverage in `platform_tests/scripts/test_check_protected_commit_authorization.py` is extended and must stay green as the authorization-semantics regression lock; two new modules carry the bound and atomicity coverage.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| WI-5742 (bound clause) / DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 | `test_delayed_evaluation_terminates_within_bound` | A deliberately delayed full staged evaluation terminates within the configured bound and returns a deny verdict, never hanging and never passing on timeout |
| WI-5742 (bound clause) / DELIB-202667722 | `test_bound_is_configuration_sourced` | The bound resolves through the timer-config path (env-local → config file → relaxed fallback); no production literal remains in the externalized category |
| WI-5806 coupling / DELIB-202667722 | `test_bound_cannot_exceed_paired_capability_ttl` | A configuration in which the gate bound exceeds the paired capability TTL is rejected by the validated accessor, making the stranding precondition unrepresentable |
| WI-5742 (phase evidence) | `test_bound_exhaustion_names_executing_phase` | The deny output names the executing phase, elapsed budget, configured bound, and remediation as actionable text |
| WI-5742 (regression) / GOV-FILE-BRIDGE-AUTHORITY-001 | `test_finalize_verified_near_bound_is_atomic` | **Required regression.** A finalize-verified transaction whose gate approaches the bound either commits atomically (verified paths + verdict in one commit) or fails cleanly — with, on the failure branch, **no orphan terminal VERIFIED file, no minted-or-consumed capability row left behind, and no `recovery_required` row created** |
| WI-5742 (stranding clause) / REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001 | `test_gate_failure_leaves_no_terminal_artifact` | On any gate-failure path the numbered chain is byte-identical before and after, and dispatcher-visible state is unchanged |
| WI-5742 (compensation robustness, C-iii) | `test_compensation_succeeds_after_sibling_aggregate_append` | Compensation completes to a clean terminal state when the aggregate preimage moved due to a sibling append, instead of raising the exact-restore failure and poisoning the row |
| WI-5742 (B1) / GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | `test_single_snapshot_load_per_invocation` | One staged evaluation performs exactly one registry snapshot load and one lock acquisition for classification, regardless of selected-path count |
| WI-5742 (B2) | `test_packet_prefilter_preserves_verdict` | The pre-filter changes no verdict: for a corpus including expired, non-matching, and live packets, pre-filtered and unfiltered evaluations produce identical findings and cleared sets |
| WI-5742 (B3) | `test_registry_assessment_runs_once` | A single evaluation performs exactly one `_registry_commit_assessment`, and the compatibility view delegates rather than re-running it |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (authorization lock) | existing `test_check_protected_commit_authorization.py` suite | Protected-path authorization semantics, fail-closed behavior, and clearance outcomes are unchanged by the performance work |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/scripts/test_protected_commit_evaluation_bound.py platform_tests/scripts/test_bridge_publication_finalization_atomicity.py -q --tb=short` passes green.
3. A delayed full staged evaluation terminates within the configured bound with a fail-closed deny carrying phase evidence.
4. Measured on the live repository, one staged evaluation performs exactly one registry snapshot load for classification, and the packet-evidence phase resolves bridge chains for only the pre-filter survivors.
5. The regression in `test_finalize_verified_near_bound_is_atomic` demonstrates atomic commit or clean failure with no orphan verdict and no poisoned row.
6. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals outside the documented relaxed fallback constant in the timer-config module.
7. Authorization semantics are unchanged: no path that was denied before is cleared after, and no path that was cleared before is denied after, for the existing suite's fixtures.

## Risk And Rollback

- **Bound set too low.** A bound below real gate cost would deny legitimate commits. Mitigated by relaxed-first defaults per DELIB-202667722, by Layer B reducing measured cost by roughly two orders of magnitude in the dominant phase, and by the documented tolerance bound in the config file.
- **Pre-filter excluding a packet that would have authorized.** Mitigated by construction (expired or non-path-matching packets cannot authorize a selected path) and by `test_packet_prefilter_preserves_verdict`, which asserts verdict identity against the unfiltered path over a mixed corpus.
- **Invocation-scoped cache masking a mid-gate registry change.** Accepted and bounded: the gate is a read-only evaluation of one staged set; a consistent snapshot across that evaluation is more correct than today's per-path re-reads, which can already observe different registry generations within a single verdict.
- **Reordering risk in Layer C.** Late minting changes transaction ordering in the publication path. Mitigated by keeping C-iii compensation robustness as a mandatory companion, by the atomicity regression, and by leaving the append-only chain semantics untouched.
- **Rollback** is the exact revert of the changed source files, the new timer-config module, the config file, and the new test modules. No MemBase mutation, no dispatcher/TAFE state change, and no bridge chain file rewrite is involved.

## Coordination Note (sequencing constraints, not scope)

- **WI-5824 — blocking predecessor on the same file.** `scripts/check_protected_commit_authorization.py` is claimed by the non-terminal WI-5824 thread, whose latest status is **NO-GO at `-004`** (verified this session by first-line status-token reads of `-001` NEW, `-002` GO, `-003` NEW, `-004` NO-GO). Its sole finding is an expired implementation-start packet. The worktree currently shows `scripts/check_protected_commit_authorization.py`, `scripts/implementation_authorization.py`, and `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` modified with that uncommitted work. **WI-5742 implementation MUST be sequenced after WI-5824 reaches a terminal status**, and must rebase on its landed worktree state; all measurements in this proposal were taken against that worktree state, which is the correct baseline. If the landed WI-5824 diff moves or renames a touched function, the implementing session re-baselines line references before editing and records the re-baseline in the implementation report.
- **WI-5825 — complementary, disjoint.** WI-5825 (GO'd) owns clearing **existing** `recovery_required` and compensated rows and back-filling receipts. WI-5742 prevents **new** strandings. The two are complementary and their target paths are kept disjoint: this proposal touches no recovery, cleanup, or receipt back-fill surface, and creates no MemBase row. Sequencing is independent, but running WI-5825's cleanup after WI-5742 lands avoids re-poisoning rows that were just cleared.
- **WI-5715 / WI-5788 — lock semantics, deliberately not touched.** Both own control-plane lock serialization and the 30-second acquisition timeout under concurrent workers. This proposal reduces the *number* of lock acquisitions (B1) but does not change lock semantics, timeout value, or introduce a shared/read lock; that remains their scope. The contention evidence in §5 is offered as corroborating input to those threads.
- **WI-5806 — timer externalization, first coupled pair.** WI-5806 owns externalizing hard-coded timers with relaxed-first defaults, a single resolution path, and invariant-coupled pairs externalized together. The Layer A config surface is deliberately shaped as the **first WI-5806 slice** for the gate-bound / capability-TTL pair, so WI-5806 adopts and extends it rather than rewriting it. Because WI-5806 is P1 and unimplemented while WI-5742 is the P0 keystone unfreezing HEAD, WI-5742 does **not** block on WI-5806.
- **WI-5791 — publication linearizability.** The cross-process generation race is WI-5791 scope; Layer C's reordering is designed to be compatible with, and not to pre-empt, that work.
- **WI-5658 — already landed.** Its committed-bridge-enumeration hoist is confirmed effective by measurement (0.36s); this proposal does not revisit it.

## DISARM — KB Mechanics

This proposal creates and modifies source, configuration, and test files only. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work; no `groundtruth.db` write, insert, or mutation occurs. The `kb_mutation_in_scope: false` flag accurately reflects a pure source, configuration, and test change; citations of DELIB, spec, and WI IDs in this proposal are read-only references, not mutations. The registry store reads described in the evidence section are likewise read-only and perform no write or edit.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5742-bound-protected-commit-evaluation`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: fix — repairs a defect (an unbounded authorization gate whose duration structurally exceeds the capability lifetime it runs under, stranding terminal publications and freezing HEAD) with regression coverage. The timer-config module is remediation plumbing required to source the bound without a hard-coded literal, not a new capability surface.

## Loyal Opposition Review Questions

1. Is C-ii (late mint / commit-before-terminal-visibility) the right primary structural fix versus C-i (renewal) or a resumable-transaction design, given the work item's `status_detail` names both commit-before-terminal-visibility and one exact resumable transaction as acceptable corrections?
2. Is coupling the gate bound and the capability TTL in one validated accessor — such that a bound exceeding the TTL is rejected at configuration time — the right enforcement point, or should the invariant be asserted at mint time instead?
3. Is the invocation-scoped snapshot cache (B1) acceptable for a read-only gate, or does Loyal Opposition require the consistency window to be narrower?
4. Does the pre-filter (B2) preserve fail-closed reporting adequately, given that expired packets are excluded from expensive validation but still surfaced in the evidence channels?
5. Is the sequencing constraint on WI-5824 sufficient, or should WI-5742 additionally wait on WI-5825's cleanup so that the atomicity regression runs against a registry with no pre-existing poisoned rows?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
