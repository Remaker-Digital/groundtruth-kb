# Handoff: TAFE Program Drive (S435 → next session)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3bc0229b-441d-46ca-ade0-e5bf06608e2a
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: default

Owner standing directive (2026-06-12, S435): drive PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
through to completion across multiple sessions with strong continuity. Owner is
present for AUQs and will manually sustain this work stream.

## Paste-ready continuation prompt

Send `::init gtkb pb` first, wait for the startup disclosure, then paste:

---

Continue work on GroundTruth-KB platform. Location: E:\GT-KB. Branch: develop.
Role: Prime Builder (harness B). Session focus: drive
PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE (TAFE) to completion. Standing owner
directive: keep driving; collect owner decisions via AskUserQuestion only.

READ FIRST (authority pointers — this prompt is routing context, NOT state truth):
1. memory/handoff-2026-06-12-tafe-program-drive.md — full state + gate mechanics.
2. bridge/INDEX.md (live) — current verdicts on the two open TAFE threads.
3. bridge/gtkb-typed-artifact-flow-engine-advisory-003.md §Corrected Owner
   Decision Map — the ONLY citable D1–D17 mapping. WARNING: the -001 advisory's
   D-gloss and any prior session-handoff D-list are confirmed-defective
   (Codex NO-GO at -002, finding P1); never cite D-numbers from anywhere else.
4. bridge/gtkb-typed-artifact-flow-engine-advisory-004.md — constrained GO:
   advisory/planning only; pilot limited to advisory/report verification,
   generated-view parity, non-mutating bookkeeping; bridge/INDEX.md canonical
   until a governed cutover is VERIFIED (Phase 7, owner AUQ).

STATE AT S435 END (2026-06-12 ~22:00Z — verify by fresh reads before acting):
- Reconciliation thread gtkb-tafe-backlog-reconciliation: WI-4495/WI-4496
  superseded at v2 (PAUTH rowid 198; owner decision
  DELIB-TAFE-BACKLOG-RECONCILIATION-PAUTH-20260612 v1+v2); post-impl report
  -003 filed NEW, awaiting Codex VERIFIED.
- Spec promotion thread gtkb-tafe-spec-promotion: proposal -001 filed NEW,
  awaiting Codex GO. Owner approved all 8 candidate texts unchanged
  (DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612).
- Commits: 47a9b5dd1 (sweep), 44197dde8 (TAFE filings). WI-4511 captured
  (duplicate sub-project rows defect, P3).

DO NEXT, in order, each through its own gate:
1. Check live INDEX for verdicts on both TAFE threads. NO-GO → revise per
   findings. Reconciliation VERIFIED → thread closes.
2. On spec-promotion GO: create 8 formal-artifact approval packets at
   .groundtruth/formal-artifact-approvals/2026-06-12-<spec-id>.json citing
   DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612; promote each spec
   candidate→specified, content byte-identical, append-only new version;
   read-back all 8; file post-impl with dry-run/apply/read-back evidence;
   drive to VERIFIED.
3. Phase 0 enablement: owner AUQ → PAUTH scoped to WI-4487..WI-4491
   (--include-spec the now-formal SPEC-TAFE-* IDs); enrich the 5 Phase-0 WIs
   (related_spec_ids, acceptance_summary, implementation_order) and create
   linked tests per GOV-12/GOV-13; progress approval_state with AUQ evidence.
4. File WI-4487 implementation proposal (flow_definitions table) — full spec
   linkage + spec-derived test plan + target_paths + `## Requirement
   Sufficiency` as a top-level h2. Resolve appraisal finding F5 inside it:
   give stage_attempts a schema home, and do NOT make compatibility_views a
   canonical MemBase table (conflicts with CX7 "generated views never
   canonical") — propose generated-file views or justify explicitly.
5. Continue per dependency graph: WI-4488 → WI-4489/4490/4491; then later
   phases, each via bridge propose→GO→implement→report→VERIFIED.
6. Phase-2 reformation requires a NEW owner decision expanding pilot
   eligibility first; dependency rewiring map lives in WI-4495/WI-4496 v2
   status_detail (WI-4500..4503 + WI-4507 depended on WI-4495; WI-4509 on
   WI-4496).

CONSTRAINTS (standing): pilot boundary per
DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612; INDEX canonical
until cutover VERIFIED; formal artifact mutations need owner packets; AUQ is
the only owner-decision channel; never remove protected behaviors.

---

## Gate mechanics verified in S435 (saves a NO-GO/blocked-write cycle each)

- **Bridge claim before any bridge Write:**
  `python scripts/bridge_claim_cli.py claim <slug> --session-id <UUID>` where
  UUID = NEWEST transcript filename in `~/.claude/projects/E--GT-KB/*.jsonl`
  (the `CLAUDE_CODE_SESSION_ID` env var is the WRONG id for the Write gate).
  Claim again before post-filing Edits; release when done.
- **implementation_authorization.py begin** requires the approved proposal to
  carry `## Requirement Sufficiency` as a top-level h2, OR pass
  `--owner-sufficiency-deliberation-id <DELIB>` where the DELIB is
  owner_conversation + owner_decision, contains a bounded phrase matching
  `(existing )?(requirements?|owner direction)…sufficient` (no intervening
  "not"), and mentions the bridge id in its text.
- **bridge-compliance-gate** hard-requires line-start `Project Authorization:`,
  `Project:`, `Work Item:` metadata lines for `bridge_kind:
  implementation_report` (bullets inside sections do not count).
- **gt projects authorize** requires ≥1 `--include-spec`
  (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001) and `--change-reason`;
  same for `gt backlog add`.
- **Clause preflight** (`adr_dcl_clause_preflight.py`) wants a literal
  INDEX-discipline sentence in the operative file (regex looks for
  `bridge/INDEX.md` / "INDEX update"); exit 5 = blocking gap.
- **Read-only `python -c` DB queries** can false-positive the
  implementation-start gate; run scripts from `.gtkb-state/*.py` files instead.
- **git worktrees must be in-root** (root-boundary hook); use
  `.gtkb-state/<name>-worktree`, remove after use.
- **Concurrent sessions share the worktree AND git index**: re-read
  bridge/INDEX.md immediately before editing (second-writer re-read-and-merge);
  your commits may sweep files other sessions staged — that is normal here.
- **New governed markdown docs** (including memory handoffs) require the
  6-field document-author provenance header (GOV-DOCUMENT-AUTHOR-PROVENANCE-001).
- **33 pre-existing test failures** in
  `platform_tests/scripts/test_cross_harness_bridge_trigger.py` at HEAD are
  owned by the fab-10 dispatch-telemetry thread — do not chase them in TAFE
  work; verified identical at HEAD vs working tree in S435.

## Appraisal residuals (S435 findings still open)

- F4: all TAFE WIs skeletal (no spec links / acceptance / tests) — fix at
  step 3 for Phase 0; later phases at their own enablement.
- F5: stage_attempts + compatibility_views tables lack schema WIs — resolve in
  the WI-4487 proposal (step 4).
- F6: duplicate sub-project rows (projects table rowids 291–298 duplicate
  283–290, mangled double-prefix ids) — tracked as WI-4511.
- F1: prior session-handoff D-number gloss is defective — only cite the -003
  corrected map.
