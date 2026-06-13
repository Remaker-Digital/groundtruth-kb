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

!!! SUPERSEDED — DO NOT ACT ON THE CODEX WRAP NOTE BELOW (S436 correction) !!!
The "CODEX LO WRAP UPDATE" directive to implement on `-002` is OVERTURNED.
The `-002` GO is INVALID: it was authored by harness C (antigravity), which
the canonical registry (`harness-state/harness-registry.json`) records as
durable role `prime-builder` + status `suspended` — NOT a loyal-opposition
harness. D17 makes Codex (harness A) the MANDATORY reviewer; no Codex verdict
exists. A 5-lens audit (workflow wf_5454ee82-50a) unanimously found `-002` does
NOT authorize implementation (conf 0.88–0.92). Owner AUQ
(DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612) chose **Park DEFERRED
pending Codex**. The thread is now DEFERRED @ `-003`. DO NOT implement until a
genuine Codex (harness A) GO is filed as `-004`. Defects captured: WI-4513
(impl-start gate is author-role-blind), WI-4515 (harness-C LO-self-label vs
prime-builder/suspended registry role). The Codex wrap note trusted the `-002`
self-label without checking the registry — that is the root error.

CODEX LO WRAP UPDATE (A-2026-06-12T22-59-14Z) [SUPERSEDED — see block above]:
- Live `bridge/INDEX.md` now has `gtkb-tafe-phase-0-enablement` at GO via
  `bridge/gtkb-tafe-phase-0-enablement-002.md` (Antigravity LO, harness C).
  Ignore stale "awaiting Codex GO" wording below. Next Prime Builder action is
  to implement the bounded MemBase mutation authorized by proposal -001:
  create the Phase-0 PAUTH, enrich WI-4487..WI-4491, read back, file the
  post-implementation report, and drive it to VERIFIED.
- The GO accepts deferring GOV-12/GOV-13 linked-test creation to each WI's own
  implementation proposal under the GOV-10 rationale that the production
  interfaces do not exist yet.
- Live latest-status LO-actionable bridge scan at wrap: 0 latest NEW/REVISED.

STATE AT S436 END (2026-06-12 ~22:55Z — verify by fresh reads before acting):
- Reconciliation thread gtkb-tafe-backlog-reconciliation: VERIFIED @ -004
  (terminal; WI-4495/WI-4496 superseded; PAUTH rowid 198).
- Spec promotion thread gtkb-tafe-spec-promotion: VERIFIED @ -004 (terminal).
  All 8 SPEC-TAFE specs now v2 status=specified, byte-identical to candidate
  v1, v1 preserved. 8 promotion approval packets at
  .groundtruth/formal-artifact-approvals/2026-06-12-<spec-id>-promotion.json
  (-promotion suffix because candidate-INSERT packets occupy the plain names).
  Driver: .gtkb-state/tafe_spec_promotion.py; evidence in
  .gtkb-state/tafe-promotion-evidence/*.json. Codex hygiene note (advisory):
  future packet-creating proposals should list packet paths in target_paths.
- Phase-0 enablement thread gtkb-tafe-phase-0-enablement: **DEFERRED @ -003**
  (owner-directed parking). Proposal -001 (governance_advisory) proposes (1)
  create Phase-0 PAUTH (id PAUTH-...-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491)
  scoped to WI-4487..4491, include the 8 formal specs, forbid cutover/
  index-authority/pilot-expansion/phase-2/impl-flow-pilot/generated-view; (2)
  enrich the 5 WIs (related_spec_ids, acceptance, implementation_order 1-5,
  deps, approval_state->auq_resolved). Both preflights GREEN
  (applicability sha256:ca7b7b22...; clause exit 0). **A -002 "GO" exists but is
  INVALID** (harness C / antigravity = durable prime-builder + suspended, not a
  valid LO; D17 makes Codex harness-A mandatory; no Codex verdict). Owner AUQ
  chose Park DEFERRED. RESUME CONDITION: a genuine Codex (harness A) GO filed as
  -004. The enrichment design (spec->WI mapping + acceptance per WI) is fully
  written in -001 §"Proposed Work-Item Enrichment" — reuse it verbatim when
  implementing post-Codex-GO. Codex already (informally, in the now-superseded
  wrap note) accepted deferring GOV-12/13 test creation to each WI's impl
  proposal under GOV-10; re-confirm in the real Codex verdict.
  **HOLD DIRECTIVE SUPERSEDED (owner "Release all deferrals", 2026-06-13).** The
  earlier 00:08Z "Keep DEFERRED, hold" was reversed. A CONCURRENT Claude Prime
  session (7a602b01, opus-4-8) filed -004 REVISED (owner "Unblock TAFE Phase 0"
  AUQ) clearing the DEFERRED park; enablement is now REVISED @ -004 and
  Codex-actionable (awaiting a VALID Codex harness-A GO). The -004 carries -001
  content verbatim and routes to Codex. NOTE: two interactive Claude PB sessions
  ran concurrently (mine c76b3a89, the other 7a602b01); coordinate via
  work-intent claims before touching shared threads. Next: a real Codex GO on
  -004 → implement PAUTH + WI enrichment per -001/-004 §"Proposed Work-Item
  Enrichment".
- Owner decisions banked this session:
  DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612 (AUQ "Authorize all 5 WIs");
  DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612 (AUQ "Park DEFERRED pending
  Codex").
- Governance defects captured S436: WI-4513 (impl-start gate author-role-blind,
  P2 improvement); WI-4515 (harness-C LO self-label vs prime-builder/suspended
  registry role, P2 defect).
- DECISION-1165 moved Pending->Resolved (was mis-filed, re-surfacing each prompt).
- Commits at S435: 47a9b5dd1, 44197dde8, c281bf2b5. S436 work UNCOMMITTED
  (spec-promotion -003 report + 8 promotion packets + enablement -001 + -003
  DEFERRED + INDEX + evidence scripts) — commit deferred per protocol until
  owner sweep-commit. WI-4511 = duplicate sub-project rows defect (P3).

DO NEXT, in order, each through its own gate:
1. gtkb-tafe-phase-0-enablement is DEFERRED @ -003 pending a valid Codex
   (harness A) GO. DO NOT implement on the invalid -002 harness-C GO.
   - When a Codex harness-A verdict appears as -004:
     - Codex GO → run `python scripts/implementation_authorization.py begin
       --bridge-id gtkb-tafe-phase-0-enablement` from THAT GO, then implement
       the bounded MemBase mutation: (a) create the Phase-0 PAUTH via
       `python -m groundtruth_kb projects authorize PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
       --owner-decision DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612 --name <...>
       --scope <...> --include-work-item WI-4487 ... --include-spec SPEC-TAFE-R1 ...
       (×8) --allowed-mutation schema_table_creation ... --forbid bridge_rule_cutover ...
       --change-reason <cites bridge + DELIB>`; (b) enrich the 5 WIs via
       update_work_item (related_spec_ids_at_creation [JSON], acceptance_summary,
       implementation_order 1-5, depends_on_work_items [JSON],
       related_deliberation_ids, approval_state='auq_resolved') — values are in
       -001 §"Proposed Work-Item Enrichment"; (c) read-back; (d) file post-impl
       report; drive to VERIFIED. Write a .gtkb-state/*.py driver (no python -c).
       update_work_item accepts these as **fields kwargs (WORK_ITEM_BACKLOG_FIELDS).
     - Codex NO-GO → revise per findings and refile REVISED.
   - Soliciting the Codex GO: while an interactive session is active the
     cross-harness trigger suppresses headless Codex dispatch; let the session
     idle (trigger fires) or owner runs a Codex bridge scan.
2. (DONE: spec promotion VERIFIED @ -004.)
3. (DONE: reconciliation VERIFIED @ -004.)
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
