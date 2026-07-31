GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-16T18-04-07Z-loyal-opposition-B-367974
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatched Loyal Opposition (harness B); ::init gtkb lo; PowerShell/Bash; project root E:\GT-KB

bridge_kind: lo_verdict
Document: gtkb-wi5116-per-thread-finalization-repair
Version: 002
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-16 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5116-per-thread-finalization-repair-001.md

## Verdict

GO. The proposal is a well-scoped, report-only, fail-closed per-thread finalization repair planner plus operator runbook under the active Tree Stabilization project. Its load-bearing premise (a renewed 2026-07-16 worktree sprawl) is confirmed live at review time, the authorization chain is complete and current, both mandatory preflights pass with zero blocking gaps, and the design honors every mechanical-operation carve-out the governing owner decision preserves. This is the exact narrow-residual path the prior broad-drain NO-GO recommended, filed as a fresh thread only after the broad drain was terminally withdrawn.

## Review Independence

- Reviewed artifact author session: 019f6bf6-3e6d-7761-be14-fb894a0e84d2 (Prime Builder Codex, harness A), from the operative file's author metadata.
- Reviewer session: 2026-07-16T18-04-07Z-loyal-opposition-B-367974 (Loyal Opposition Claude, harness B; bridge auto-dispatch).
- The session-context review-independence boundary is satisfied: the reviewer session context does not match the reviewed proposal's author session context. Harness IDs also differ (author A / reviewer B), but session-context divergence is the controlling boundary.

## Premise Verified Live (the decisive check)

The prior WI-5116 broad drain (bridge/gtkb-wi5116-bridge-finalization-backlog-diagnosis-drain-002 NO-GO) died because its premise was stale: the 365-file terminal backlog it targeted had already been drained to ~30 files. The cardinal risk for any successor is repeating that failure. I therefore independently confirmed this proposal's renewed-sprawl premise against live runtime:

- Canonical dirty-path count (git status --porcelain --untracked-files=all) is 1506 at review time, matching the proposal's reproduction of ~1492-1495 and the canonical auto-resolve planner's dirty_paths: 1506.
- Current worktree_finalization_triage.py actuator counts (manual_owner_review=1430, safe_commit=10, skip=37, auto_ignore=24, auto_drop_byte_identical=5) are within drift of the proposal's snapshot (1420 / 9 / 37 / 24 / 5). The sprawl is live and stable, not drained.
- Method note: a naive git status --porcelain (untracked-dirs collapsed) returns 658, which would manufacture a false staleness signal. The premise holds only under the canonical --untracked-files=all counting the planner uses. This directly informs an implementation note below.

Unlike the prior broad drain (which asked to act on a specific enumerated backlog that had vanished), this proposal builds a report-only planner that classifies whatever exists at runtime, so a fluctuating count does not falsify it.

## Restart Legitimacy

- Prior broad-drain thread gtkb-wi5116-bridge-finalization-backlog-diagnosis-drain is terminally WITHDRAWN (v3, confirmed via canonical bridge state), closed without replacement implementation authority.
- The prior NO-GO explicitly offered two valid Prime paths: withdraw as superseded, or revise to a narrow residual with reproduction and targeted tests. This new per-thread-finalization-repair slug is that narrow residual.
- Therefore this is not an illegitimate new-slug restart of an open NO-GO; the predecessor is terminal and this is the recommended follow-on.

## Authorization Chain Verified

- WI-5116 exists, Project = PROJECT-GTKB-TREE-STABILIZATION, P1, open. Its own description directs "drain the terminal backlog via per-thread finalization," so a per-thread finalization tool is squarely in scope; the proposal's report-only narrowing is a conservative reading.
- PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE is active, project-scoped, imposes no per-work-item inclusion restriction (covers WI-5116), and authorizes source/test/documentation work.
- Owner decision DELIB-202666274 backs the PAUTH and explicitly preserves separate gates for "Git index/history operations, dispatcher/TAFE/harness mutation, release, and deployment" - exactly the mechanical operations the proposal forbids the new tool from performing.
- All three target paths are in-root (E:\GT-KB): scripts/per_thread_finalization_repair.py, platform_tests/scripts/test_per_thread_finalization_repair.py, docs/procedures/per-thread-finalization-repair.md. None exist yet (clean NEW create).
- Load-bearing cited specs exist: GOV-WORK-TREE-HYGIENE-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001.

## Assessment by Review Dimension

- Specification linkage: complete. Applicability preflight harvested all Specification Links; no missing required or advisory specs. Spec-derived verification plan maps each governing surface to a concrete verification with an expected result.
- Scope discipline: strong. Explicit non-scope section forbids git add -A, sweep/bulk commit, untracked-file deletion, dispatcher/TAFE/PAUTH mutation, and changes to auto_finalize_sweep.py / auto_resolve / write_verdict.py. Report-only-by-default with explicit STOP labels and fail-closed classes.
- Non-redundancy: acceptable. The existing WI-5027 worktree_finalization_triage.py is a file-level hygiene classifier (buckets: bridge_thread_chain, protected_source_test_config, etc.). This tool operates at the bridge-thread level with finalization-readiness semantics (terminal VERIFIED chain plus target-path cleanliness) and emits per-thread repair instructions. That is a genuine increment layered on the canonical auto-resolve planner, not a duplicate.
- Risk handling: the one real risk (planner wording that could encourage unsafe finalization) is self-identified and mitigated by report-only design, explicit STOP labels, and absence of mutation flags. Rollback is a scoped 3-file revert.

## Non-Blocking Implementation Notes (for the report/verification phase)

These do not gate GO; they are guidance to reduce a later NO-GO risk at verification.

1. Canonical dirty-path counting. The tool must derive its dirty-path/thread census from the same canonical source the auto-resolve planner uses (git status --untracked-files=all, or the planner's own count), not a collapsed git status --porcelain. As shown above, the collapsed count (658) vs canonical count (1506) differ by ~2.3x purely from untracked-directory collapse; a collapsed count would misclassify sprawl scale and could hide finalizable threads.
2. Fixture-based tests, not live-count dependence. Acceptance criterion 3 references "the current nine numbered untracked terminal VERIFIED files." The count is volatile (the proposal itself flags concurrent drift). The focused tests must exercise the classification logic against constructed fixtures for each class (terminal_verified_repair_candidate, terminal_verified_blocked_dirty_targets, terminal_verified_blocked_missing_scope, in_flight_bridge_chain, excluded_active_program, mixed_provenance_stop), not assert a hardcoded count against the live tree. The proposal's verification plan already specifies fixture-based unit tests, which is correct; the report should confirm they are count-independent.
3. Actuation-path awareness. The real per-thread finalization actuator (write_verdict.py --finalize-verified) is itself currently blocked on this branch by unrelated dirt (WI-5113 class). The planner is correctly scoped to NOT fix that; the runbook should make plain that its emitted instructions presuppose a clean finalizer and reference the finalizer-repair track rather than implying the operator can finalize while the finalizer is dirty.

## Prior Deliberations

Independent Deliberation Archive search (gt deliberations search "per-thread finalization repair tool runbook" and "WI-5116 finalization repair") surfaced no prior decision rejecting this narrow approach. Nearest matches are unrelated finalization verdicts and DELIB-20266278 (dispatch-treadmill-drain program authorization; context, not conflict). DELIB-20260710-PRIORITIZE-WI5158-BEFORE-WI5105-FINALIZATIONS holds commingled-worktree VERIFIED finalizations pending WI-5158, which concerns the actuation mechanism the proposal explicitly scopes out - no conflict. The proposal's own Prior Deliberations section (WI-5027, WI-4979, WI-5112, WI-5318 precedents plus the WI-5116 drain NO-GO/withdrawal chain) is accurate and complete.

## Applicability Preflight

- packet_hash: `sha256:92434ad40a9494f53b03a2efa4698282136f0eecb09e4cee52a7d660bdf5d526`
- bridge_document_name: `gtkb-wi5116-per-thread-finalization-repair`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md`
- operative_file: `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5116-per-thread-finalization-repair`
- Operative file: `bridge\gtkb-wi5116-per-thread-finalization-repair-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prime Builder Implementation Context

- Objective: implement the report-only per-thread finalization repair planner + runbook per the GO'd proposal scope (three target paths only).
- Preconditions: acquire a work-intent claim for slug gtkb-wi5116-per-thread-finalization-repair; run implementation_authorization.py begin --bridge-id gtkb-wi5116-per-thread-finalization-repair against this GO before touching source.
- File touchpoints: scripts/per_thread_finalization_repair.py (new), platform_tests/scripts/test_per_thread_finalization_repair.py (new), docs/procedures/per-thread-finalization-repair.md (new).
- Verification sequence: python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short ; ruff check <both .py> ; ruff format --check <both .py> ; sample run python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330. Run BOTH ruff check AND ruff format --check; the format gate is a separate NO-GO surface at verification.
- Open decisions: none blocking. The three implementation notes above are guidance, not gates.

## Recommended Commit Type

fix (the proposal's recommendation is accurate: this adds a bounded repair-planner tool/test/runbook for a defect class, no new capability surface beyond the planner itself).
