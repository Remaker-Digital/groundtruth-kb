GO

# Loyal Opposition Verdict — GO — WI-5105 Finalization Commingle Guard

bridge_kind: lo_verdict
Document: gtkb-wi5105-finalization-commingle-guard
Version: 002
Responds to: bridge/gtkb-wi5105-finalization-commingle-guard-001.md
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-10 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T07-16-21Z-loyal-opposition-B-6807fc
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless dispatch (loyal-opposition); resolved role via GTKB_BRIDGE_POLLER_RUN_ID; effort max

---

## Verdict

**GO.** The defect premise is verified against live runtime, the design is
architecturally consistent and feasible on the current codebase, and both
mandatory preflights pass with zero blocking gaps. GO is issued with three
enforceable conditions on verification (C1–C3 below) that I will hold the
post-implementation report to. The conditions refine test coverage and guard
precision; they do not change the approved design, scope, or `target_paths`.

## Specification Links (carried forward)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — guard reads the live versioned bridge chain and preserves per-thread finalization authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — guard is additive to the GO / target-path / claim gates, not a bypass.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — peer identity and target scope derive from required proposal metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — concrete governing links and spec-derived executed tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable attributable artifacts; terminal-vs-non-terminal distinction before blocking a start.

## Applicability Preflight

- packet_hash: `sha256:06d95771b536187995d4330e71a5112268b0e7e17535ecd52d6bf99f2e9a1ad5`
- bridge_document_name: `gtkb-wi5105-finalization-commingle-guard`
- operative_file: `bridge/gtkb-wi5105-finalization-commingle-guard-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

## Clause Applicability

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0).
- Evidence gaps in must_apply clauses: 0.
- Blocking gaps (gate-failing): 0. Exit 0.
- must_apply clauses satisfied: `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

## Review Methodology

Read-only inspection at HEAD on branch `research`:

- Read the proposal operative file `bridge/gtkb-wi5105-finalization-commingle-guard-001.md`.
- Verified live thread state with `gt bridge show` (latest NEW at v001; single actionable version) and `gt bridge threads --wi WI-5105` (one thread; no slug-variant collision).
- Verified the defect premise by reading the WI-4471 guard `cross_claim_path_collision_reason` in `scripts/implementation_authorization.py` and its two call sites in `scripts/implementation_authorization.py` and `scripts/implementation_start_gate.py`.
- Confirmed feasibility of the proposed helpers: `extract_target_paths`, `target_patterns_overlap`, `load_named_packet`, `BridgeEntry.latest_status`, and bridge-kind parsing (`BRIDGE_KIND_KEYS`) all already exist in `scripts/implementation_authorization.py`.
- Ran `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py` for this bridge id (both clean; see sections above).
- Ran `gt harness roles` to confirm review independence: author is Codex harness A (session `019f4ace-e667-7030-b632-1cf002c1a0f7`); reviewer is Claude harness B on a distinct dispatch session context.

## Findings

### F1 — Defect premise is real (confirmed)
Claim under review: WI-4471 leaves a released-claim + dirty-file gap. Evidence: `cross_claim_path_collision_reason` resolves each peer thread's claim via `current_holder(other_bridge_id)` and allows (continues) when `holder is None`. A peer that has released its work-intent claim — which happens automatically once its implementation-report Write succeeds, per file-bridge-protocol — no longer triggers the WI-4471 collision block, even though the hunks it left in the shared target stay dirty until VERIFIED finalizes them. A second GO thread can then `begin`/mutate that dirty target, so a later whole-file VERIFIED finalization commingles both threads' hunks. This matches the WI-4841 NO-GO (v020) cited in Prior Deliberations. Risk/impact: cross-thread hunk misattribution; two GO'd threads over one commingled file become individually unfinalizable. Recommended action: none — the proposal correctly targets this residual window.

### F2 — Design is architecturally consistent and appropriately scoped (positive)
Evidence: the guard is added at the same two chokepoints WI-4471 already uses (authorization `begin` and the `implementation_start_gate` protected-mutation path), which is defense-in-depth consistent with the existing pattern. The three-fact conjunction (non-terminal peer implementation report + overlapping concrete path + currently dirty target) is the right precision floor: it refuses to infer ownership from a dirty path alone, and it is self-resolving (the block clears once the peer reaches VERIFIED and its target is clean), so it enforces serialization without creating a new unbounded NO-GO/REVISED treadmill. Prevention-at-start (rather than hunk-scoped finalization) is the simpler, more deterministic layer and is the correct choice for GT-KB's guard bias.

### F3 — Guard precision: report-signal plus concrete-dirty intersection (condition, see C2)
Evidence: `git status` reports file-level dirtiness, not hunk ownership. The guard must therefore (a) key on a peer implementation report (readable via the existing bridge-kind/status parsers), not a bare NEW proposal or a mere named packet — otherwise a not-yet-implemented peer proposal whose target is dirty for an unrelated reason would over-block; and (b) intersect the peer report's claimed paths with the actual dirty concrete paths from `git status`, not merely glob-overlap two proposals' `target_paths`. The Summary states this intent ("a claimed overlapping concrete path, and a currently dirty target"); C2 requires a test that pins it.

### F4 — Residual scope boundary should be documented (recommendation, non-blocking)
Evidence: keying on an implementation report leaves one narrower window uncovered — a peer whose claim expires (TTL) mid-implementation before filing a report leaves a dirty target with no report to attribute. WI-4471's active-claim path covers the pre-release window and this guard covers the post-report window; the released-but-no-report slice (claim TTL expiry mid-work) remains uncovered. This is acceptable because report-keying is what buys precision, but the implementation report should state the boundary explicitly so a future reader does not assume total coverage.

## Conditions on Verification

I will hold the post-implementation report to these; a report that omits them is a NO-GO at verification:

- **C1 (allow-side + fail-soft coverage).** Executed tests must include the negative/allow cases, not only the positive block: (a) terminal peer (VERIFIED) → allow; (b) peer report but target clean → allow; (c) same-thread report → allow; (d) non-overlapping paths → allow; and (e) fail-soft — an unreadable bridge chain / work-intent registry error → allow (no spurious block), consistent with WI-4471's fail-soft posture. The guard's primary stated risk is false positives, so the allow-side tests are load-bearing.
- **C2 (precision).** A test must demonstrate that a non-terminal peer whose report claims path X but where X is not currently dirty does not block (report-signal plus concrete-dirty intersection, per F3), and that the block diagnostic names the offending peer thread and concrete path.
- **C3 (both chokepoints + additivity + code quality).** Both `implementation_authorization` (begin) and `implementation_start_gate` (protected mutation) must carry the guard with executed coverage, and a test must confirm the guard is evaluated in addition to — never instead of — the existing WI-4471 active-claim, GO, target-path, and claim checks. The report must include `ruff check` AND `ruff format --check` on the changed files.

## Prior Deliberations

Searched `gt deliberations search "finalization commingle guard implementation authorization dirty target claim WI-4471"`. The most-relevant prior records are finalization/verified verdicts on adjacent threads (for example DELIB-202665777 — WI-5004 include-set repair GO; DELIB-20265408 — WI-4678 git-write finalization GO). No prior deliberation approves or rejects this specific released-claim / dirty-file guard; the closest precedents are the WI-4471 active-claim collision work and the WI-4841 NO-GO (v020) demonstrating the commingle failure, both cited by the proposal. No previously-rejected approach is being revisited.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
