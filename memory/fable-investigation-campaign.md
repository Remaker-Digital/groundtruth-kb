author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

# PROJECT-FABLE-INVESTIGATION — Proposal Campaign Notes

Operational notepad (not canonical). Canonical state: the advisory, the project
record, WI-4413..4435, the bridge INDEX, and per-cluster DELIB/PAUTH rows.

## Charter
Owner (2026-06-10) directed creating ALL 23 implementation proposals for
PROJECT-FABLE-INVESTIGATION (FAB-01..FAB-23 = WI-4413..WI-4435), chartered by
`bridge/gtkb-fable-investigation-advisory-001.md` (ADVISORY) +
`DELIB-FABLE-GRILL-20260610-Q1..Q7`. Findings frozen HYG-001..068 in
`independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md`
(+ `-v2.md`). Cite verified facts; do not re-derive (Anti-Duplication Guide in the advisory).

## Operating model (owner AUQ decisions 2026-06-10)
- **Implementation routing = tiered local→cheap→Claude:** Ollama Qwen2.5-Coder 14B
  (harness D, free) → DeepSeek-V3.x / Qwen3-Coder via `scripts/openrouter_harness.py`
  → Claude/Codex only for governance/protected/gate-finicky. ≈ Ollama Phase 2
  (PROJECT-GTKB-OLLAMA-INTEGRATION). Manual today; formal harness-D dispatch is Phase-2 future work.
- **Authoring = hybrid:** Opus authors owner-gated/high-complexity + protected-narrative
  clusters; mechanical clusters get cheap-model-drafted bodies that Opus finalizes + files.
  AUQ-batch only owner-gated clusters (Q4); determined-fix file without per-cluster AUQ.

## Cluster triage (provisional)
- **Owner-gated** (Opus + AUQ batch; grill-depth for high-complexity): FAB-02 ✓, FAB-04
  (destructive ~11GB deletions), FAB-11 (regression-revival sequencing), FAB-13 (retention
  policy), FAB-14 (gate-FP policy + 20-WI consolidation), FAB-18 (advisory-drain/PAUTH policy),
  FAB-22 (architecture, owner-heavy).
- **Protected-narrative** (mechanical but edits CLAUDE.md/AGENTS.md/rules → per-file
  narrative-approval packets): FAB-05, FAB-06, FAB-12, FAB-15.
- **Determined-fix** (cheap-model-drafted + Opus finalize): FAB-01, FAB-03, FAB-07, FAB-08,
  FAB-09, FAB-10, FAB-16, FAB-17, FAB-19, FAB-20, FAB-21, FAB-23.

## BRIDGE-GATE FILING PLAYBOOK (learned filing FAB-02 — 3 rejections)
1. `bridge_kind: prime_proposal` (NOT implementation_proposal; enum per DCL-BRIDGE-KIND-TAXONOMY-ENUM-001).
2. THREE linkage metadata lines REQUIRED (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001):
   `Project:`, `Work Item:`, `Project Authorization:`. → each cluster needs a PAUTH:
   `gt projects authorize PROJECT-FABLE-INVESTIGATION --id PAUTH-... --owner-decision <DELIB>
   --name ... --scope ... --change-reason ... --include-work-item WI-NNNN --include-spec <SPEC>
   [--allowed-mutation ...] [--forbid ...]`. **--include-spec REQUIRED**
   (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001). PAUTH = approval envelope; bridge GO = per-cluster
   authorization moment (Q7-consistent).
3. Applicability preflight auto-runs at Write; cite triggered cross-cutting specs. Known triggers:
   `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking) on paths infrastructure/terraform/**,
   applications/**, groundtruth-kb/src/groundtruth_kb/project/** and content "applications/".
   Always-required: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
   DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
4. WI-collision flags ANY bare `WI-NNNN` != declared WI — describe other WIs without bare IDs.
5. Sections: status token first line (`NEW`); canonical `## Specification Links` heading
   (regex matches only Specification Links|References + relevant|linked|governing prefix);
   `## Prior Deliberations`; `## Owner Decisions / Input` (substantive); h2 `## Requirement Sufficiency`;
   spec-to-test mapping; inline-JSON `target_paths`.
6. Author metadata 6 fields: author_identity, author_harness_id, author_session_context_id,
   author_model, author_model_version, author_model_configuration.
7. Claim BEFORE Write: `python scripts/bridge_claim_cli.py claim <slug> --session-id <TRANSCRIPT-UUID>`
   (transcript UUID, NOT CLAUDE_CODE_SESSION_ID). Auto-releases on successful Write. File via Write
   tool + manual INDEX prepend (Document:/NEW:).
8. Verify: `python scripts/bridge_applicability_preflight.py --bridge-id <slug>` (preflight_passed:true)
   + `python scripts/adr_dcl_clause_preflight.py --bridge-id <slug>` (exit 0).
- `gt` not on PATH → `python -c "from groundtruth_kb.cli import main; import sys; sys.argv=[...]; main()"`.
- Canonical MemBase = root `groundtruth.db`; WAL reads don't block writers.
- Auto-memory under C:\Users\ is Write-blocked by project-root-boundary; use E:\GT-KB\memory\ topic files.

## Cheap-model drafting workflow (VALIDATED 2026-06-10 on FAB-08/HYG-053)

Owner chose "build the cheap-drafting workflow + validate on 1 cluster" over pulling FAB-19/20
forward (FAB-19/20 are detector-expansion + re-investigation, NOT proposal drafting).

**Backend:** local Ollama (`ollama.exe` at `C:\Users\micha\AppData\Local\Programs\Ollama`,
server auto-starts on any `ollama` invocation). Local models: `qwen3.6:latest` (23GB, used),
`gemma4:latest` (9.6GB). Cloud models `*:cloud` (kimi-k2.6, qwen3-coder-next) are EXTERNAL —
avoid for private GT-KB content. Local = private (nothing leaves the machine) + free.

**CRITICAL:** `qwen3.6` is a REASONING model — without `think:false` it spends the whole
`num_predict` budget on hidden thinking and returns an EMPTY `response`. Always set `think:false`.

**Call (bypasses the agentic shim; `.ollama/routing.toml` is missing — stale canonical-terminology
pointer, a hygiene finding):**
`POST http://localhost:11434/api/generate` body `{model:'qwen3.6:latest', prompt, stream:false,
think:false, options:{num_predict:1500, temperature:0.3}}`. ~90s/draft (829 tok). resp.response = body.

**Prompt pattern:** finding text + already-made owner decisions + fix approach + "Write these
sections as markdown ## headings: Summary; Scope and Boundaries; Proposed Implementation;
Spec-Derived Verification Plan; Acceptance Criteria; Risk and Rollback; Recommended Commit Type."

**Division of labor (the cost saving):** cheap model drafts the BODY PROSE; Opus adds gate
metadata (status token, bridge_kind: prime_proposal, the 3 linkage lines + a per-cluster PAUTH,
inline-JSON target_paths, ## Specification Links, ## Prior Deliberations, ## Owner Decisions/Input,
h2 ## Requirement Sufficiency, 6 author-metadata fields), runs the preflights, and files.
Owner-gated clusters still need their real AUQ batch first (the validation FED the model an
assumed decision; real filing needs the captured owner decision).

## Status
- **FAB-02 FILED 2026-06-10** (NEW): `bridge/gtkb-fab-02-secrets-remediation-001.md`;
  applicability packet `sha256:727f81c3...`, clause exit 0. DELIB-FAB02-REMEDIATION-20260610 (v1);
  PAUTH-FAB02-20260610. Covers HYG-019/020. Awaiting Codex GO.
- **FAB-04 FILED 2026-06-10** (NEW): `bridge/gtkb-fab-04-storage-reclamation-001.md`;
  applicability packet `sha256:a723d30f...`, clause exit 0. DELIB-FAB04-REMEDIATION-20260610;
  PAUTH-FAB04-20260610. Covers HYG-013/057/058 (~10.8GB reclamation + WI-3394 closure). Awaiting Codex GO.
- Gate-FP datapoint for FAB-14: clause `CLAUSE-IN-ROOT` detector false-positives on a *descriptive*
  `C:\Users\` mention (not an actual out-of-root write); reworded to pass. Reserve waivers for real exceptions.
- **FAB-01 FILED 2026-06-10** (NEW): `bridge/gtkb-fab-01-dispatch-substrate-revival-001.md`;
  applicability `preflight_passed:true`, clause exit 0. DELIB-FAB01-REMEDIATION-20260610;
  PAUTH-FAB01-20260610. Covers HYG-001 (spawn-time argv normalization + launchability doctor
  check) + HYG-004 (split capability axes can_fire_events/can_receive_dispatch + gated 5-min
  scheduled wake extending the single-harness-dispatcher pattern; gated-wake re-enablement
  owner-approved w/ cost-benefit per bridge-essential.md). Couples to FAB-10. Awaiting Codex GO.
- **TRIAGE CORRECTION:** most clusters carry an "Owner Touchpoint Required" in their findings, so
  the campaign is MORE owner-gated than the provisional triage guessed (FAB-01 was mislabeled
  determined-fix). READ each cluster's findings before assuming determined-fix.
- **Gate lesson:** bridge-substrate clusters (FAB-01/FAB-10) trigger
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` as must_apply → include a
  "## Bridge Protocol Compliance" assertion (filed under bridge/, NEW INDEX entry, append-only).
- **Owner working-style feedback (2026-06-10):** do NOT checkpoint-and-ask "say continue" between
  clusters. Proceed autonomously; pause ONLY for genuine owner-gated AUQ batches (those are real
  decisions, not permission-checks).
- **FAB-03 FILED 2026-06-10** (NEW): `bridge/gtkb-fab-03-membase-backup-001.md`; both preflights green.
  DELIB-FAB03-REMEDIATION-20260610; PAUTH-FAB03-20260610. Covers HYG-002 (staged backup: Slice 1
  scheduled `gt db snapshot` + doctor freshness check + retention; Slice 2 upload follow-on; repoint
  SyncBackSE to snapshot output). Owner follow-up: SyncBackSE repoint (manual). Awaiting Codex GO.
- **Gate lesson:** DB-backup clusters trip the KB-mutation completeness check as a FALSE POSITIVE
  (backup READS the DB, doesn't mutate it) → confirm "no KB mutation" rather than adding groundtruth.db
  to target_paths. Use `%LOCALAPPDATA%` env-var form (not expanded `C:\Users\...`) to avoid the
  CLAUSE-IN-ROOT detector when citing the non-synced snapshot output.
- **DRAFT-LINTER FILED 2026-06-10** (NEW, campaign-support, not a FAB cluster):
  `bridge/gtkb-cheap-draft-linter-001.md`; both preflights green. WI-4437;
  DELIB-DRAFTLINTER-20260610; PAUTH-DRAFTLINTER-20260610. Owner-agreed deterministic QA gate for
  cheap-model drafts (6 checks: path-resolution, HYG-id match, phantom-spec, section-presence,
  placeholder, >=1 concrete assertion). Source-write DEFERRED to Codex GO (Codex offline several hrs).
- **ATTRIBUTION-DRIFT observation (2026-06-10):** `gt backlog add` from harness B (Claude) recorded
  `changed_by: prime-builder/antigravity` — the KB attribution resolver picked the wrong harness
  (antigravity/C, not B). Real defect; likely FAB-15 (role-narrative) or a new WI. Note, don't chase now.
- **FAB-05 FILED 2026-06-10** (NEW): `bridge/gtkb-fab-05-rule-file-retirement-001.md`; both preflights
  green. DELIB-FAB05-REMEDIATION-20260610; PAUTH-FAB05-20260610. Protected-narrative: archive OS-poller
  stack + DEPRECATED-stub runbook; archive 4 Cursor/Agent-Red rule files + fix index; dedup normative
  blocks; repoint codex-standing-priorities to gt backlog list + retire WI-3278/3465. ~10-12 packets.
- **FAB-06 FILED 2026-06-10** (NEW): `bridge/gtkb-fab-06-narrative-corrections-001.md`; both preflights
  green. DELIB-FAB06-REMEDIATION-20260610; PAUTH-FAB06-20260610. Protected-narrative: regenerate CLAUDE.md
  GOV index from DB (GOV-08) + GOV-18=SPEC-1662 alias + citation sweep; realign AGENTS.md to S347
  reference-adopter framing; fix CLAUDE.md KB-access pointer (tools/knowledge-db shim cleanup = separate
  Agent-Red follow-up).
- **STRATEGIC CAPTURES 2026-06-10 (orchestrator):** DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610 + WI-4438
  (PROJECT-GTKB-ACTIVE-ORCHESTRATION) — evolve the bridge into an active multi-model orchestrator (route by
  efficacy/cost/availability; PRESERVE governance+audit+GO; measurement = the linchpin).
  DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610 — INVIOLABLE: no session CONTEXT may formally review
  artifacts it created (cheapest route = reuse a warm context = the violation → machine-enforce;
  deterministic gates exempt). Candidate formal GOV+DCL. Other LOs (Codex/Ollama-Cloud/Antigravity/
  OpenRouter) available but uncalibrated + dispatch broken (FAB-01) → keep queue for Codex's authoritative GO.
- **FAB-07..10 FILED 2026-06-10** (NEW; all preflights green; DELIB/PAUTH per cluster):
  FAB-07 (gtkb-fab-07-doctor-false-signals): doctor false-signal repairs — reword four-demo-apps to
  examples/ + carve-out; fix DA-harvest check (prefix match); AUQ-coverage precision; isolation-suite calibration.
  FAB-08 (gtkb-fab-08-slot-leak-fix): _force_rmtree onexc + purge 229 + doctor auto-prune (HYG-022 Agent_Red
  application.toml = separate AR bridge). **BODY CHEAP-DRAFTED by local qwen3.6, Opus-finalized — first
  production use of the cost-saving loop.**
  FAB-09 (gtkb-fab-09-safety-gate-registration): promote destructive/credential gates to tracked settings.json
  + Codex parity; retire dead scheduler; implement owner-decision-capture + gov09-capture hooks
  (owner-decision-capture AUTOMATES the manual AUQ→DA capture that's been 255-ing).
  FAB-10 (gtkb-fab-10-dispatch-telemetry-claim-contract): bare-id claim + 600s TTL; sanitize ':' + revive dead
  worker telemetry (orchestrator measurement foundation); half-open breaker + GTKB_DISPATCH_* knobs; INDEX
  well-formedness lint + helper-only follow-on.
- **DELIB-255 observation:** background decision-capture commits SQLite (rows valid) but throws exit-255 on the
  post-commit Chroma index under load; each PAUTH success validates its DELIB by id. FAB-09's
  owner-decision-capture hook is the deterministic fix. Hygiene note for FAB-17 (DA/Chroma read-path).
- **WAVE 1 COMPLETE (FAB-01..08) + FAB-09/10 (wave 2). 11 proposals queued for Codex; Codex offline.**
  FAB: **10 of 23 filed; 13 remaining.** Next: FAB-11 (regression-signal revival, SEQUENCED — HYG-029/044/030/014;
  high-complexity, internally ordered: corpus→sweep→tests-table→pipeline_events retention+VACUUM).

## NEXT SESSION — Handoff / continuation prompt (2026-06-10)

(Canonical term is "handoff prompt"; "continuation prompt" is the DELIB-20260883-rejected synonym — same thing.)
Paste the block below to resume:

```
::init gtkb pb

Continue PROJECT-FABLE-INVESTIGATION — file implementation proposals for the remaining FAB clusters.
READ FIRST: memory/fable-investigation-campaign.md (this file: playbook + cheap-drafting recipe + operating
model + per-cluster status); bridge/gtkb-fable-investigation-advisory-001.md (charter, Q1-Q7, anti-duplication);
bridge/INDEX.md (live queue); independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md
(frozen findings HYG-001..068).

DONE: 10 of 23 FAB clusters filed (FAB-01..FAB-10) + draft-linter (WI-4437) = 11 proposals NEW, queued for Codex.
NEXT: FAB-11 (WI-4423, regression-signal revival) — HYG-029/044/030/014; HIGH-complexity + SEQUENCED
(assertion-corpus → sweep revival → tests-table reconnection → pipeline_events retention+VACUUM); use grill-me depth.
Then FAB-12..FAB-23.

PER-CLUSTER CYCLE: read the cluster's frozen findings → AUQ batch (owner-gated clusters ONLY; do NOT
checkpoint-and-ask between clusters) → DELIB via decision-capture (rows commit despite the exit-255 Chroma
post-step; the PAUTH success validates the DELIB by id) → bounded PAUTH (gt projects authorize ... --owner-decision
<DELIB> --include-spec <real spec> --include-work-item <WI>) → author (Opus for owner-gated/protected-narrative;
cheap-draft via local Ollama qwen3.6 think:false for determined-fix, recipe above) → claim slug
(scripts/bridge_claim_cli.py claim <slug> --session-id <newest-transcript-UUID>) → Write bridge file + manual
INDEX prepend → both preflights green (applicability preflight_passed:true + clause exit 0).

CODEX = Loyal Opposition: its disjoint-context GO authorizes implementation; NOTHING implements until GO
(11 proposals already wait for it). Implementation routes tiered local→cheap→Claude once GO'd.

OPEN FOLLOW-UPS: draft-linter source builds on Codex GO; Agent_Red application.toml backfill = separate
Agent-Red-scoped bridge (HYG-022); attribution-drift defect (gt backlog add from harness B logged
changed_by:antigravity) → FAB-15; DELIB-capture exit-255 Chroma-index-under-load → FAB-17. STRATEGIC (future
AUQ sessions, NOT now): the active-orchestrator vision (WI-4438 / DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610) and
the INVIOLABLE review-independence invariant (DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610) — candidate formal GOV+DCL.
```
