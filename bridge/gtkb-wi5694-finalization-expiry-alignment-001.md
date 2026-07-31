NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 parallel-operation mandate; proposal authoring only - no implementation, no commit, no review, no session wrap in this session

bridge_kind: prime_proposal
Document: gtkb-wi5694-finalization-expiry-alignment
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5694

target_paths: ["platform_tests/scripts/test_wi5694_finalization_expiry_closure.py"]
implementation_scope: cycle3_finalization_expiry_closure_regression_lock
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5694 Implementation Proposal — Cycle 3 of 3 (RESCOPED): Finalization-Layer Expiry-Alignment Closure — End-to-End Regression Lock and Completion Declaration

## Summary

Cycle 3 of WI-5694 was scoped by `DELIB-202667723` and the WI status_detail as "protected-commit/finalization expiry checks" adopting terminal-evidence-sufficient semantics. A fresh worktree inventory this session (evidence below) found that the single live expiry-denial in that surface — the protected-commit checker's route-3 ambient-now expiry deny, the exact deny that wedged the wi5759/wi5758 finalizations — has ALREADY been replaced with implementation-time authority validation by WI-5824 Fix B (`bridge/gtkb-wi5824-protected-commit-checker-null-safety-ordering-003.md`, implementation in the current worktree, thread non-terminal awaiting verification). Every other surface in the finalization/commit path either contains no packet-expiry logic at all, deliberately retains its expiry check as active-authority bounding per the unchanged WI-4532 invariant, or is owned by a concurrent thread. Per the honest-rescope contingency in the dispatch mandate, this proposal is therefore the NARROW CLOSURE of cycle 3: a new WI-5694-anchored end-to-end regression module that locks finalization-time acceptance of expired-but-live packets across the full commit-authorization stack, locks cross-layer semantic parity between the checker's inline route-3 logic and the cycle-1 `assess_packet_terminal_evidence` API so the two independent implementations of the same owner-decided semantics cannot drift silently, plus the WI-5694 cycle-3 completion declaration. No source file is modified.

This proposal is filed as `bridge/gtkb-wi5694-finalization-expiry-alignment-001.md`, a new thread continuing the append-only numbered bridge file chain for WI-5694 (sibling of `gtkb-wi5694-terminal-evidence-packet-validator`, cycle 1). No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write during filing; it mints no implementation-start packet and confers no mutation authority; filing it authorizes nothing.

## Fresh-Read Rescope Inventory (2026-07-31, live worktree)

All claims re-derived this session from the code of record at current worktree state (`git --no-optional-locks status` confirms `scripts/check_protected_commit_authorization.py` and `scripts/implementation_authorization.py` are worktree-modified by their owning threads). Line numbers are current-worktree references.

1. **Checker route 3 — ALREADY ALIGNED (wi5824 Fix B; owned by that thread).** `_load_finalized_packet` in `scripts/check_protected_commit_authorization.py` (lines 1643-1675) no longer denies on ambient wall-clock expiry. It validates implementation-time authority: `expires_at` must parse (deny "invalid expiry" otherwise), `implementation_start.finalized_at` must parse (deny "finalized_at is unparseable"), and `finalized_at > expires_at` denies with "was not live at implementation" — never-live and unparseable shapes stay fail-closed, mirroring the cycle-1 API's E2 boundary (`finalized <= expires` accepts, `scripts/implementation_authorization.py` line 2648). The wi5759 wedge shape (packet live at implementation `08:06Z`, expired `10:06Z`, finalization attempted hours later) now clears. Route 2 (`_packet_binding_errors`) has no expiry clause; route 1 requires an active-valid packet only for live-GO evidence, and per wi5824's end-to-end test the transaction-local terminal path clears with `live_go_packets_valid == 0`. The only other `expires_at` logic in the checker (lines 2062-2064) bounds bridge-publication capability mint-to-consume use — an active-authority bound retained by Fix A, not a terminal-evidence surface.
2. **`gtkb-verify` finalization helper — NOTHING TO ALIGN.** `.claude/skills/gtkb-verify/helpers/write_verdict.py` contains zero matches for `expire|expiry|expires_at` and zero matches for `packet|implementation_authorization` (fresh greps this session). It consults no packet and applies no expiry check; its finalize-verified commit inherits expiry semantics exclusively from the pre-commit chain below.
3. **`auto_finalize_sweep` — NOTHING TO ALIGN.** `scripts/auto_finalize_sweep.py` contains zero expiry logic of its own. Its eligibility path delegates to `write_verdict.validate_verified_body` (no packet consultation) and `check_protected_commit_authorization.evaluate` (lines 226-239), and its commit path (`git commit`, line 256) triggers the same pre-commit chain. All expiry behavior is inherited from the wi5824-fixed checker.
4. **Commit chain — the checker is the ONLY packet-expiry gate.** `.githooks/pre-commit` runs `scripts/check_protected_commit_authorization.py --staged` as its protected-commit gate; `groundtruth_kb/governance/commit_preflight.py` invokes the same checker (line 47) and contains no packet-expiry logic of its own. The only other expiry logic in the governance package is the formal artifact-approval expiry in `approval_packet.py` lines 297-307 (a different artifact class under GOV-ARTIFACT-APPROVAL-001, not a packet-TTL surface and not consumed at implementation-authorization finalization time) and the PAUTH `expires_at` read in `project_authorization_operation_time.py` — DCL-mandated operation-time PAUTH enforcement, expressly preserved inside route 3 by wi5824's GO'd design and outside DELIB-202667723's packet-TTL scope.
5. **`load_named_packet` / `_validate_packet` expiry hard-reject — CORRECT AS-IS, and NOT consumed at finalization time.** The active-authority expiry hard-reject (`scripts/implementation_authorization.py` lines 2553-2554) is deliberately unchanged per DELIB-202667723 (TTL retains its active-authority-bounding function; WI-4532 invariant) and is locked by cycle-1's T4. Fresh caller inventory: `validate_targets`/`_named_packets_authorizing_targets`/`cross_claim_path_collision_reason` (implementation-time mutation gating), `activate_packet` (active-authority recovery), `impl_start_target_paths_preflight.py` and the bridge-compliance-gate advisory path (non-blocking, implementation-time), and `gtkb_file_reference_migration.py` (migration-specific active gating). The checker's route 3 reads the packet bytes directly and no longer routes through `_validate_packet`. No finalization-path consumer denies on `_validate_packet` expiry. The known "active load_named_packet still expiry-hard-rejects" note therefore resolves as BY DESIGN: that rejection is the retained active-authority bound, not a finalization defect.
6. **Cycle-1 API present in worktree.** `assess_packet_terminal_evidence` (`scripts/implementation_authorization.py` line 2605) and the additive `evidence_valid`/`evidence_error`/`expired` list fields are implemented (thread `gtkb-wi5694-terminal-evidence-packet-validator` at NO-GO `-004` on report `-003` — a report spec-links documentation defect, not a behavior finding; the behavior surface is landed and regression-tested by `platform_tests/scripts/test_implementation_authorization_terminal_evidence.py`).

**Inventory conclusion (honest rescope):** wi5824's Fix B left NOTHING remaining in the protected-commit/finalization expiry surface for cycle 3 to re-implement. The only candidate refinements discovered live inside files owned by non-terminal concurrent threads (see Residual Findings). Cycle 3 therefore lands as the closure: the end-to-end four-case regression lock at the finalization layer, the cross-layer parity drift-lock, and the completion declaration.

## Proposed Change — Single Slice: WI-5694 Finalization-Layer Regression Module

New test module `platform_tests/scripts/test_wi5694_finalization_expiry_closure.py` (the ONLY target path; no source file is touched). Conventions follow the existing suites: importlib module-load fixtures for `scripts/check_protected_commit_authorization.py` and `scripts/implementation_authorization.py`, isolated `tmp_path` project roots with fixture git repositories, fixture bridge chains, fixture schema-v3 finalized packets, and fixture work-intent registry state; the live store, live MemBase, and live bridge chain are never touched. The module imports both production surfaces strictly read-only and deliberately imports NOTHING from `.claude/skills/gtkb-verify/**` (cycle-2's surface) and NOTHING from the sibling threads' test modules (their files are owned by their threads; self-contained fixtures avoid cross-thread coupling).

Tests (T1-T5; T1-T4 are the four owner-mandated DELIB-202667723 cases expressed at the finalization layer, T5 is the parity drift-lock):

- T1 `test_finalization_accepts_expired_but_live_packet_end_to_end` — full finalize-verified staged-transaction fixture (staged implementation path + thread chain + same-transaction VERIFIED verdict carrying Commit Finalization Evidence + bound schema-v3 finalized packet re-timed to `finalized_at <= expires_at < now`): `evaluate()` passes and clears the paths; the SAME fixture through `assess_packet_terminal_evidence` returns `evidence_valid=True`, `expired=True`, `live_at_implementation=True`, `contested=False`. This is the WI-5694 P0 defect class (wi5759 wedge shape) locked end-to-end at the layer that produced the wedge.
- T2 `test_finalization_rejects_never_live_packet_both_layers` — same fixture re-timed to `finalized_at > expires_at`: `evaluate()` denies citing "was not live at implementation"; the API returns `live_at_implementation=False`, `evidence_valid=False`. The expired-before-implementation case stays invalid at both layers.
- T3 `test_contested_thread_fails_evidence_and_embedded_claim_floor` — (a) API layer: an active competing work-intent claim from a DIFFERENT session yields `contested=True`, `evidence_valid=False`; (b) checker floor: a packet whose embedded `implementation_start` claim session differs from the start session denies with "claim session differs from start session". The commit-layer LIVE-registry contest consultation is NOT asserted — it does not exist today (Residual Finding RF-1 below, declared honestly rather than locked as expected behavior).
- T4 `test_active_authority_expiry_hard_reject_unchanged` — an expired packet still raises "Implementation authorization packet has expired" through `load_named_packet` and an unexpired packet still loads: the WI-4532 active-authority invariant re-locked from the closure module's perspective (independent of cycle-1's suite, which this module does not modify).
- T5 `test_route3_and_evidence_api_semantics_agree` — parametrized over fixture shapes {expired-but-live, never-live, unparseable `finalized_at`, unparseable `expires_at`, live-unexpired}: the checker's route-3 accept/deny classification agrees with the API's E2 classification for every shape. This is the new load-bearing coverage neither sibling suite provides: wi5824's suite never calls the cycle-1 API, cycle-1's suite never calls the checker, and the two files implement the same owner-decided semantics independently because file ownership forced wi5824 to inline its E2 logic. T5 converts that structural duplication from a silent-drift risk into a tested invariant.

Timer discipline: the diff introduces zero new hard-coded timer, interval, retry, or throttle literals. Fixture timestamps (re-timed `expires_at`/`finalized_at` values) are test data, not timer configuration; `DEFAULT_EXPIRY_MINUTES` and every production timer surface are untouched (the coupled TTL externalization proceeds separately as WI-5806 under DELIB-202667722).

## Residual Findings And Routing (declared, not implemented here)

- **RF-1 — commit-layer live-contest consultation is missing.** Route 3 validates the packet's EMBEDDED claim/provenance consistency but does not consult the live work-intent registry for an ACTIVE competing claim at finalization time, while DELIB-202667723 case 3 defines contest by an active competing claim (the cycle-1 API's E5 clause does consult `bridge_work_intent_registry.current_holder`). The natural homes for closing this are (a) the verification workflow consulting the cycle-1 API before finalize — the concurrently-filed CYCLE-2 sibling's surface — and (b) defense-in-depth inside the checker — owned by wi5824's non-terminal thread. Neither file is available to this cycle. Routing: declared here for the record; recommended for backlog capture by the implementing/leader session as a follow-on scoped after wi5824 reaches terminal (this filing performs no MemBase mutation).
- **RF-2 — route-3 E2 logic is inlined rather than consuming `assess_packet_terminal_evidence`.** Same-cause structural duplication (file ownership during parallel operation). T5 locks the semantics against drift NOW; a consolidation refactor (route 3 consuming the cycle-1 API) is a candidate follow-on after both owning threads are terminal, same routing as RF-1.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — WI-5694's source spec; operation-time PAUTH enforcement is preserved inside route 3 and re-exercised by the T1 fixture's PAUTH-decision evidence; nothing in this cycle weakens an operation gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the project-scoped authorization chain under which this cycle proceeds (cited PAUTH triple + this thread's eventual GO); PAUTH metadata does not broaden `target_paths` and does not replace the live latest-GO requirement.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project authorization does not bypass bridge controls; this cycle is itself filed through the full bridge protocol and its tests assert evidence classification only, never authority resurrection.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the PAUTH envelope fields consumed by the fixtures remain explicit and append-only; this cycle reads them, never writes them.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the append-only versioned bridge chain is the audit substrate the fixtures model and the finalization discipline this closure locks; the module is read-only over live `bridge/`.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the terminal-evidence rule is enforced mechanically at the commit layer; this cycle adds the regression floor proving the write-time/review-time layers agree.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the mandatory proposal spec-linkage constraint; the verification plan maps each link to derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the eventual VERIFIED is conditional on creation and execution of the spec-derived tests T1-T5; the implementation report will carry the executed commands and observed results.
- `GOV-12` — work item creation triggers test creation; `TEST-11713` is WI-5694's derived test anchor and this module is its finalization-layer expression.
- `GOV-10` — the tests exercise exposed production interfaces (`evaluate`, `assess_packet_terminal_evidence`, `load_named_packet`) through the established module-load harness.
- `SPEC-1662` — assertion quality: every test asserts behavioral outcomes (pass/deny classifications, deny-reason substrings, evidence field values), not structure.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — the locked surfaces are deterministic caller-driven services; the module adds no timers and no background behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the rescope inventory derives entirely from fresh canonical reads this session (live worktree code, `gt backlog show`, `gt projects authorizations`, first-line bridge status reads, targeted greps); no cached substitute was consulted.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary containment: the single target path is an in-root platform surface (`platform_tests/`); no application subtree and no out-of-root dependency is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the rescope evidence, residual findings, and completion declaration are preserved as durable bridge artifacts rather than transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability: the module ties DELIB-202667723's four cases, the wi5824 delivery vehicle, and the cycle-1 API into one executable record.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — defect-origin WI-5694 lifecycle transitions follow the recorded trigger classifications; the completion declaration below names the terminal condition explicitly.
- `GOV-STANDING-BACKLOG-001` — WI-5694 in MemBase is the sole work authority for this cycle; RF-1/RF-2 follow-ons route to the standing backlog, not to this thread's scope.

## Prior Deliberations

- **DELIB-202667723** — the controlling owner decision: terminal-evidence-sufficient packet validation ("evidence at the time of the act, not ambient state now"); four required regression cases; per-surface bridge cycles; WI-4532 active-authority invariant unchanged. This cycle is the third and final mandated surface.
- **DELIB-202667735** — the delegated proposal-authoring and parallel-operation mandate under which this worker files this NEW entry.
- **DELIB-202667732** — PAUTH v2 repair decision for the cited list-free whole-project grant (git_commit removed from allowed_mutation_classes per WI-5809); confirmed `active`, list-free, `expires_at: null` by fresh read this session.
- **DELIB-202667724** — the original owner grant decision for the same PAUTH.
- **DELIB-202667736** — retroactive owner-approval capture for the wi5824 emergency hot-patch; cited read-only as part of the delivery-vehicle audit trail this closure builds on.
- **DELIB-202667722** — timer/throttle governance (timers first-class, relaxed-first): this diff introduces zero new timer literals; TTL externalization remains WI-5806.
- **DELIB-202667533** — AT-01 commit-first finalization ordering; untouched and expressly preserved by DELIB-202667723.
- **DELIB-202667523** — the integrated parallel-operation program mandate (fan-out worker model) whose file-ownership constraints shaped this rescope.
- All deliberation, specification, work-item, test, and PAUTH ids cited anywhere in this proposal were verified this session by exact-id lookup against the live MemBase (`groundtruth.db`, read-only); the wi5824 and cycle-1 thread states were verified by direct first-line status-token reads of the numbered bridge files.

## Owner Decisions / Input

1. **DELIB-202667723 / AUQ-20260730-PACKET-EXPIRY-AUTHORITY-MODEL** — the owner AskUserQuestion selecting "Terminal-evidence-sufficient" (archived 2026-07-30, source `owner_conversation`, outcome `owner_decision`, work item WI-5694). It defines the exact four-case semantics this closure locks at the finalization layer and mandates the per-surface cycle split this proposal completes.
2. **DELIB-202667735** — the owner's delegated proposal-authoring mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5694 cycle 3. Authoring-only: this filing performs no implementation, no commit, and no review.
3. **DELIB-202667724 + DELIB-202667732** — the owner decisions issuing and repairing `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` (v2, `active`, list-free, no expiry; fresh read this session). Per its scope summary, WI-5694 still requires this full governed cycle: this proposal, independent Loyal Opposition GO with complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization.
4. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** DELIB-202667723 (owner-decided four-case semantics and cycle split), WI-5694's status_detail (fresh-read verified via `gt backlog show WI-5694 --json` this session), `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, and the wi5824 Fix B GO'd behavior contract fully determine the behavior this closure locks. No new or revised requirement is required before implementation.

## Specification-Derived Verification Plan (Four Cases at the Finalization Layer)

MemBase test record `TEST-11713` (WI-5694's GOV-12 derived test anchor) is expressed at the finalization layer by this module. All tests land in `platform_tests/scripts/test_wi5694_finalization_expiry_closure.py`; the sibling suites are executed unmodified as the regression net.

| # | Owner-mandated case (DELIB-202667723) | Test | Layer(s) exercised | Derives from |
|---|---|---|---|---|
| T1 | Expired-but-live-at-implementation ACCEPT | `test_finalization_accepts_expired_but_live_packet_end_to_end` | checker `evaluate()` end-to-end + API agreement | DELIB-202667723 case 1; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-10; SPEC-1662 |
| T2 | Expired-before-implementation REJECT | `test_finalization_rejects_never_live_packet_both_layers` | checker deny "was not live at implementation" + API `live_at_implementation=False` | DELIB-202667723 case 2 |
| T3 | Contested REJECT | `test_contested_thread_fails_evidence_and_embedded_claim_floor` | API `contested=True` reject + checker embedded-claim-consistency floor (RF-1 declared, not asserted) | DELIB-202667723 case 3 |
| T4 | Live-packet behavior unchanged | `test_active_authority_expiry_hard_reject_unchanged` | `load_named_packet` expiry hard-reject retained; unexpired loads | DELIB-202667723 case 4; WI-4532 invariant; DELIB-202667722 |
| T5 | (parity drift-lock across the two implementations of the same semantics) | `test_route3_and_evidence_api_semantics_agree` | checker route 3 vs `assess_packet_terminal_evidence` E2, five parametrized shapes | GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001; SPEC-1662; DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |

Commands (implementation report will carry observed output; venv interpreter only):

- `& groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_wi5694_finalization_expiry_closure.py -q --tb=short`
- `& groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/scripts/test_implementation_authorization_terminal_evidence.py -q --tb=short` (unmodified sibling regression net; the one pre-existing unrelated failure documented in wi5824 `-003` Deviations item 2 is expected until its own repair lands)
- `& groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests/scripts/test_wi5694_finalization_expiry_closure.py`
- `& groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests/scripts/test_wi5694_finalization_expiry_closure.py`

## Acceptance Criteria

1. T1-T5 pass green against the current worktree behavior contract (wi5824 Fix B + cycle-1 API), with T1 reproducing the wi5759 wedge shape end-to-end and clearing it.
2. The diff is confined to the single `target_paths` file; zero source, hook, skill, config, or bridge-chain mutation; sibling suites executed unmodified.
3. `ruff check` and `ruff format --check` pass clean on the new file (separate gates).
4. Zero new hard-coded timer, interval, retry, or throttle literals.
5. T5's parity lock fails if either layer's E2 classification drifts from the other for any parametrized shape.

## Completion Declaration (WI-5694 Cycle 3)

With this thread VERIFIED, WI-5694's third mandated enforcement surface is closed: the protected-commit/finalization expiry check adopted terminal-evidence-sufficient semantics via WI-5824 Fix B (the delivery vehicle, landed cross-project under PROJECT-GTKB-HARNESS-TEST-CORRECTIONS because the checker file was owned by that thread), and this cycle contributes the WI-5694-anchored four-case end-to-end regression lock plus the T5 cross-layer parity drift-lock that neither owning thread could provide alone. WI-5694 as a whole is complete when its three cycle threads (cycle 1 `gtkb-wi5694-terminal-evidence-packet-validator`, the concurrently-filed cycle-2 verification-workflow thread, and this thread) and the wi5824 delivery-vehicle thread are all terminal; work-item resolution then follows the standard governed backlog path with RF-1/RF-2 captured as follow-on candidates. This filing itself resolves nothing and mutates no MemBase record.

## Coordination Note (file ownership and sequencing; scope-shaping, not scope)

1. **wi5824 thread (non-terminal, latest `-003` NEW awaiting verification)** owns `scripts/check_protected_commit_authorization.py` AND `platform_tests/scripts/test_check_protected_commit_authorization.py` until terminal. This proposal's `target_paths` excludes both; the new module imports the checker strictly read-only. Implementation of this cycle MUST be sequenced AFTER the wi5824 thread finalizes: its worktree behavior is the contract under test, and a verification-driven revise loop there would otherwise move the deny-string surface underneath these tests. If the landed wi5824 state changes any asserted deny substring, the implementing session re-baselines the expectations and notes it in the implementation report.
2. **Cycle-1 thread (`gtkb-wi5694-terminal-evidence-packet-validator`, latest `-004` NO-GO on report `-003`)** owns `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization_terminal_evidence.py`. This proposal's `target_paths` excludes both; the module imports the API strictly read-only. The `-004` NO-GO is a report-documentation defect (missing Specification Links on the report), not a behavior finding; implementation of this cycle is nevertheless sequenced after that thread reaches terminal so the API surface is commit-stable.
3. **Cycle-2 sibling (verification-workflow packet consultation, filed concurrently tonight under the same DELIB-202667735 mandate)** owns the verification-workflow surfaces — the `gtkb-verify` skill including `.claude/skills/gtkb-verify/helpers/write_verdict.py` and any workflow consultation it introduces. This proposal's `target_paths` and the module's imports deliberately exclude every `gtkb-verify` surface: the end-to-end scope here is the commit-authorization layer (the layer that produced the wi5759 wedge), not the verdict-authoring workflow. RF-1's workflow-layer contested gate is expected to be cycle-2 territory; this thread will not collide with it.
4. `scripts/implementation_authorization.py` is additionally targeted by the WI-5823 extractor-alignment thread (its own coordination note governs that sequencing). This proposal touches no source file at all, so no collision is possible from this thread.

## Risk And Rollback

- **Risk: asserting a moving contract.** The tested behavior lives in files owned by two non-terminal threads. Mitigated by the sequencing constraints in the Coordination Note (implement only after wi5824 and cycle-1 are terminal) and by the re-baseline disclosure obligation.
- **Risk: fixture duplication with wi5824's suite.** The end-to-end fixture construction resembles wi5824's transaction-local test. Accepted deliberately: importing another thread's test helpers would couple this module to a file this thread does not own; self-contained fixtures keep the closure independent and are the vehicle for the T5 parity coverage that suite cannot host.
- **Risk: T5 could ossify an implementation detail.** T5 asserts classification agreement (accept/deny per shape), not message-for-message equality, so either layer may be refactored freely (including the RF-2 consolidation) without breaking parity.
- **Rollback:** exact revert of the single new test file. No schema, MemBase, packet, dispatcher/TAFE, or bridge-chain state is created or modified by the implementation.

## DISARM — KB Mechanics

This proposal creates one test file only. No MemBase records, specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work; `kb_mutation_in_scope: false` is accurate. All DELIB/spec/WI/TEST/PAUTH citations are read-only references. RF-1/RF-2 backlog capture is recommended to the implementing/leader session and is NOT performed by this filing.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5694-finalization-expiry-alignment`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet; it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file, expires, and fails closed on bridge status drift. The PAUTH triple in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: test — the diff is a test-only addition (one new regression module; zero production-behavior change), which is the exact `test:` case in the Conventional Commits discipline of `.claude/rules/file-bridge-protocol.md`. Disclosure: the dispatch instruction anticipated remainder alignment work and pre-specified `fix`; the fresh-read inventory found the fix already delivered by wi5824, so the honest type for the rescoped closure diff is `test`. The type-matches-diff validation should be applied to this declaration.

## Loyal Opposition Review Questions

1. Is the honest-rescope conclusion supported by the inventory evidence — i.e., do you independently find any finalization-path expiry denial that wi5824 Fix B did not cover and that is not owned by a concurrent thread?
2. Is T5's classification-level parity (accept/deny per shape, not message equality) the right strength for the drift-lock, or should specific deny substrings also be pinned?
3. Is declaring RF-1 (commit-layer live-contest consultation) as a routed follow-on acceptable for cycle-3 closure, or must WI-5694 completion be conditioned on landing RF-1 first?
4. Do you concur with `test` over the dispatch-instructed `fix` for a test-only diff under the Conventional Commits discipline?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
