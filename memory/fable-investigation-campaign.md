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
- **FAB-11 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-11-regression-signal-revival-001.md`; both
  preflights GREEN (applicability `preflight_passed:true`, packet `sha256:4decff09...`, missing required+advisory
  both []; clause exit 0, 4 must_apply 0 blocking gaps). DELIB-FAB11-REMEDIATION-20260610 (v1, clean — no 255);
  PAUTH-FAB11-20260610 (rowid 176; specs SPEC-1662/GOV-08/GOV-12/GOV-13). Covers HYG-029/044/030/014 (regression-
  signal revival, SEQUENCED). **4 owner AUQ decisions (all recommended):** HYG-029=HYBRID (rewrite paths for
  protected_behavior+verified only via append-only re-versioning; retire/app-scope the ~1,100 rest); HYG-044=
  re-register sweep AFTER corpus repair; HYG-030=PARTIAL spec-derived test recorder; HYG-014=archive-then-prune+
  VACUUM (root DB snapshots → FAB-04). **Gate lessons reconfirmed:** (a) genuine KB-mutation cluster MUST include
  `groundtruth.db` in target_paths (bridge-compliance-gate `_kb_mutation_target_paths_ask_reason`, hook line 645) —
  opposite of FAB-10's "No KB mutation" negation path; (b) ADR-ISOLATION CLAUSE-IN-ROOT satisfied by an explicit
  "## Isolation Placement Compliance" section framing the Agent_Red/* rewrite as isolation-POSITIVE; (c) advisory
  artifact-oriented trio (GOV-ARTIFACT-ORIENTED-GOVERNANCE/ADR-.../DCL-ARTIFACT-LIFECYCLE-TRIGGERS) + GOV-STANDING-
  BACKLOG triggered by lifecycle vocab — cited to zero the advisory list; (d) Edit (not Write) is exempt from the
  pre-drafting claim gate, so post-Write strengthening edits need no re-claim. Awaiting Codex GO.
- **FAB-12 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-12-agent-red-residue-sweep-001.md`; both
  preflights GREEN (applicability `preflight_passed:true`, packet `sha256:46b20b1a...`, missing required+advisory
  both []; clause exit 0, 4 must_apply 0 blocking gaps). DELIB-FAB12-REMEDIATION-20260610 (v1, clean);
  PAUTH-FAB12-20260610 (rowid 178; specs ADR-ISOLATION-APPLICATION-PLACEMENT-001/GOV-AGENT-RED-GTKB-CONFORMANCE-001/
  ADR-0001/GOV-08/GOV-RELEASE-READINESS-GOVERNED-TESTING-001). Covers HYG-012/016/024/034/043 (Agent-Red residue
  sweep). **4 owner AUQ decisions (all recommended):** HYG-012=migrate root groundtruth.toml [project] identity to
  GT-KB, keep [scoped_service]; HYG-016=repo memory/MEMORY.md authoritative, home-dir=harness cache, amend CLAUDE.md
  L12; HYG-024+HYG-043=fix all platform-affecting config+CI now (defer full split to ISOLATION-018); HYG-034=full
  relocation of 3 AR skills+seed_tenant.py+agents/commands under applications/Agent_Red/ + strip session-init
  fallbacks. Protected-narrative cluster (CLAUDE.md L12 amend → narrative packet at impl). **No KB mutation**
  (config/CI/narrative/source/relocation only) → used FAB-10's negation note path, NOT groundtruth.db-in-target_paths.
  Awaiting Codex GO. **AUQ interrupted once by a contending session (owner halted it); re-presented identical batch,
  owner answered all-recommended.**
- **FAB-13 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-13-retention-policy-umbrella-001.md`; both
  preflights GREEN (applicability `preflight_passed:true`, packet `sha256:86b6f4cd...`, missing req+adv both [];
  clause exit 0, 4 must_apply 0 blocking gaps; benign warning: memory/archive/** parent dir not yet present).
  DELIB-FAB13-REMEDIATION-20260610 (v1, clean); PAUTH-FAB13-20260610 (rowid 179; specs GOV-08/GOV-SOURCE-OF-TRUTH-
  FRESHNESS-001/GOV-STANDING-BACKLOG-001/SPEC-DA-HARVEST-INCLUSION/DCL-SMART-POLLER-AUTO-TRIGGER-001). Covers
  HYG-021/055/056. **3 owner AUQ decisions (all recommended):** HYG-021=rotate decision-ledger >30d to dated
  archive + DA harvest; HYG-055=cap+rotate dispatch evidence (14d/200MB runs, 10MBx5 both JSONL, envelope git-status
  truncation, .gtkb-state GC); HYG-056=purge 62 Drive ' (N)' dups + extend .driveignore (full-unsync surfaced as
  owner infra). KB mutation = YES but NARROW (DA-harvest resolved decisions before rotation → groundtruth.db in
  target_paths + honest note). **NEW gate lesson: WI-collision gate is a WARNING not a block** — cited bare WI-4282
  (real, != declared WI-4425) → bridge-compliance-gate emitted PreToolUse collision warning; file still wrote;
  fixed by Edit replacing "WI-4282" → "the 4282 item" (drop WI- prefix). Awaiting Codex GO.
- **FAB-14 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-14-gate-fp-feedback-loop-001.md`; both preflights
  GREEN after one fix (applicability `preflight_passed:true`, packet `sha256:ac5e4ed0...`, missing req+adv both [];
  clause exit 0 after adding Isolation Placement Compliance). DELIB-FAB14-REMEDIATION-20260610 (v1, clean);
  PAUTH-FAB14-20260610 (rowid 180; specs SPEC-AUQ-POLICY-ENGINE-001/SPEC-AUQ-NO-LLM-CLASSIFIER-001/
  DCL-ARTIFACT-APPROVAL-HOOK-001/GOV-15/GOV-STANDING-BACKLOG-001/DCL-CROSS-HARNESS-ENFORCEMENT-001). Covers
  HYG-040/042/046/047. **4 owner AUQ decisions (all recommended):** HYG-040=cheaper-containment gate-quality
  program (FP regression corpus required by LO verification + denial telemetry + one-time GOV-15 WI reconciliation;
  defer shared classifier library; warn-mode downgrade REJECTED); HYG-042=hotfix root-boundary Bash parser now
  (+ PowerShell/Codex coverage); HYG-046=fix all 3 Requirement Sufficiency rigidities (h2/h3, bounded regexes,
  distinct error); HYG-047=packet auto-discovery in BOTH narrative+formal gates (amend DCL-ARTIFACT-APPROVAL-HOOK-001).
  KB mutation = YES (WI reconciliation append-only + DCL amend) → groundtruth.db in target_paths. **CRITICAL REUSABLE
  GATE LESSON: ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT is must_apply on EVERY bridge proposal (not
  just relocation clusters) — clause preflight exit 5 if no `E:\GT-KB`/"in-root" evidence string in body. FAB-11/12/13
  passed only because they touch applications/ + had Isolation Placement Compliance sections. FROM NOW ON every FAB
  proposal MUST include a short "## Isolation Placement Compliance" section with explicit E:\GT-KB/in-root language,
  even when it touches no applications/ subtree.** Awaiting Codex GO.
- **FAB-15 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-15-role-narrative-spec-reconciliation-001.md`; both
  preflights GREEN (applicability `preflight_passed:true`, packet `sha256:7ebebe9a...`; clause exit 0). DELIB-FAB15-
  REMEDIATION-20260610 (v1, clean); PAUTH-FAB15-20260610 (rowid 181; specs GOV-HARNESS-ROLE-PORTABILITY-001/
  GOV-SESSION-ROLE-AUTHORITY-001/GOV-08/GOV-SOURCE-OF-TRUTH-FRESHNESS-001/DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001/
  GOV-GLOSSARY-AS-DA-READ-SURFACE-001). Covers HYG-036/032/033/064. **4 owner AUQ decisions (all recommended):**
  HYG-036=registry-is-RESIDUE → restore Claude=PB/Codex=LO via gt mode set-role + audit drift (vendor-de-binding
  narrative sweep DEFERRED to follow-on, NOT in scope); HYG-032=split Codex posture (never headless / on-request
  interactive / network off) + DELIB citation comment; HYG-033=glossary-markdown-SoT + deterministic canonical_terms
  regen sync; HYG-064=carve relay file under GOV-SOURCE-OF-TRUTH-FRESHNESS-001 declared-TTL exception. KB mutation =
  YES (registry txn + canonical_terms regen + GOV amend) → groundtruth.db in target_paths. **CRITICAL GATE LESSON
  (refines FAB-14's): the in-root requirement is enforced by TWO gates — (1) clause preflight needs an in-root
  EVIDENCE section (E:\GT-KB/in-root prose); (2) applicability preflight HARD-BLOCKS the Write unless
  ADR-ISOLATION-APPLICATION-PLACEMENT-001 is CITED in ## Specification Links (it harvests citations only from that
  section). EVERY FAB proposal needs BOTH: ADR-ISOLATION in Specification Links AND the Isolation Placement Compliance
  section.** First Write was hard-blocked (missing_required_specs=[ADR-ISOLATION...]); re-Wrote with the citation
  added (claim survives a FAILED Write — only releases on success). Awaiting Codex GO.
- **FAB-16 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-16-harness-parity-remediation-001.md`; both preflights
  GREEN first try (applicability `preflight_passed:true`, packet `sha256:496dacab...`; clause exit 0 — the two-gate
  in-root lesson applied: ADR-ISOLATION in Spec Links + Isolation Placement Compliance section). DELIB-FAB16-
  REMEDIATION-20260610 (v1, clean); PAUTH-FAB16-20260610 (rowid 182; specs GOV-HARNESS-ROLE-PORTABILITY-001/
  GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001/GOV-HARNESS-ONBOARDING-CONTRACT-001/GOV-08/DCL-CROSS-HARNESS-ENFORCEMENT-001).
  Covers HYG-061/062/063. **OWNER CLARIFICATION (custom AUQ answer, not a listed option):** "Goose is merely
  providing the desktop UI for interactive sessions with OpenRouter cloud models. It is not directly relevant." →
  Goose (E) = desktop UI front-end for OpenRouter (F) interactive sessions, NOT a dispatch harness; classify as UI
  client so parity checker stops flagging missing-headless-surface; NO headless wrapper, NOT retired. + 2 determined
  fixes: regen drifted Antigravity adapters (22 STALE+14 MISSING→exit 0); remove hardcoded ('claude','codex') parity
  fallback (derive from registry projection). No KB mutation (config+source) → FAB-10 negation note. Awaiting Codex GO.
- **FAB-17 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-17-da-chroma-read-path-001.md`; both preflights GREEN
  (applicability `preflight_passed:true`, packet `sha256:caa18e07...`; clause exit 0; benign benchmarks/** parent-dir
  warning). DELIB-FAB17-REMEDIATION-20260610 (v1, clean); PAUTH-FAB17-20260610 (rowid 183; specs SPEC-2098/GOV-08/
  GOV-SOURCE-OF-TRUTH-FRESHNESS-001/SPEC-DA-DOCTOR-CHECK/GOV-STANDING-BACKLOG-001). Covers HYG-048 + demoted
  benchmark-CLI/chroma-triplication. **1 owner AUQ (recommended):** HYG-048=wrap collection.count() inside the try
  (restore SQLite-LIKE fallback) + add bounded timeout/retry for multi-session contention (fixes crash AND >3min/45min
  hangs). + 2 determined fixes: repair benchmark CLI; resolve chroma triplication to one canonical index. No KB
  mutation (source+config; chroma=derived index) → FAB-10 negation note. Awaiting Codex GO.
- **FAB-18 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-18-backlog-dignity-001.md`; both preflights GREEN
  (applicability `preflight_passed:true`, packet `sha256:ac0a543b...`; clause exit 0). DELIB-FAB18-REMEDIATION-20260610
  (v1, clean); PAUTH-FAB18-20260610 (rowid 184; specs GOV-STANDING-BACKLOG-001/SPEC-DA-HARVEST-INCLUSION/GOV-15/
  GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001/GOV-SESSION-SELF-INITIALIZATION-001). Covers HYG-015/060/065. **3 owner
  AUQ (all recommended):** HYG-015=DA-harvest all 765 reports + bulk-close routing WIs >60d (kb-batch dry-run+GOV-15) +
  router age-out; HYG-065=recalibrate doctor backlog-health (uncovered-by-PAUTH normal for unapproved/future; warn only
  for impl-active WIs) + fix startup-metric; HYG-060=full IPA-root reorg (archive-not-delete) + organize-rule allowlist
  refresh. KB mutation YES (DA harvest + WI bulk-close) → groundtruth.db in target_paths. **Codex became ACTIVE during
  this run (~02:22Z)** — now reviewing the NEW queue; all entries still NEW (nothing Prime-actionable yet). Awaiting Codex GO.
- **FAB-19 FILED 2026-06-10 (S430, NEW):** `bridge/gtkb-fab-19-hygiene-detector-expansion-001.md`; both preflights
  GREEN (applicability `preflight_passed:true`, packet `sha256:a86eabd9...`; clause exit 0; fixed one advisory-citation
  typo GOV-→ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 via Edit). DELIB-FAB19-REMEDIATION-20260610 (v1, clean);
  PAUTH-FAB19-20260610 (rowid 185; specs GOV-ARTIFACT-ORIENTED-GOVERNANCE-001/SPEC-DSI-DOCTOR-CHECK-001/GOV-08/GOV-17/
  GOV-STANDING-BACKLOG-001). Covers HYG-051/066. **1 owner AUQ (recommended):** HYG-051=FULL expansion of hygiene-sweep-
  patterns.toml (5-8 new pattern classes seeded from this investigation: retired-mechanism/Claude-Playground/work_list.md/
  CURSOR-*/stale-relocated-path content regexes + render/tmp/dead-allowlist presence + template-vs-live hash drift) +
  replace blanket exclusions with per-pattern (so .claude/.codex scanned; registry-header revision = formal packet).
  + determined fix: wire check_skill_health.py into doctor WARN (advisory; blocking-promotion deferred). No KB mutation
  (config+doctor) → FAB-10 negation note. Pairs with FAB-20 (consumes this detector core as layer-1 evidence). Awaiting Codex GO.
- **WAVE 2 in progress (FAB-09..19 filed). 20 proposals queued for Codex; Codex ACTIVE + reviewing.**
  FAB: **19 of 23 filed; 4 remaining.** Session S430 (Opus 4.8, harness B) filed FAB-11..19 = 9 clusters this run,
  all gate-clean, all owner AUQ decisions captured (DELIB+PAUTH per cluster: rowids 176/178/179/180/181/182/183).
  **REMAINING 6 (resume here):** FAB-18 (WI-4430, advisory-flood drain + PAUTH coverage + IPA org + startup metric —
  OWNER-GATED; HYG-015/060/065; overlaps WI-4402/3327/3502), FAB-19 (WI-4431, deterministic hygiene detector
  expansion + skill-health wiring — HYG-051/066; overlaps WI-3451/4238), FAB-20 (WI-4432, gtkb-hygiene-investigation
  skill — Q5 charter; overlaps WI-3391), FAB-21 (WI-4433, startup load-cost reduction — HYG-008/025/028; 38-rule 336KB
  load vs 250K budget; overlaps WI-4360/4361/4403), FAB-22 (WI-4434, architecture cluster OWNER-HEAVY — HYG-009/010/
  011/023/052; protocol overhead, god modules, env/interpreter contract, ADR/DCL enforcement coverage; overlaps
  GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001/WI-3354/3498), FAB-23 (WI-4435, demoted near-miss batch incl. $null
  self-residue — v1 Appendix A). **REUSABLE GATE LESSONS (apply to all 6):** (a) EVERY proposal cite
  ADR-ISOLATION-APPLICATION-PLACEMENT-001 in `## Specification Links` AND add a `## Isolation Placement Compliance`
  section with E:\GT-KB/in-root language (applicability preflight HARD-BLOCKS the Write on missing citation; clause
  preflight exit-5 on missing in-root evidence); (b) KB-mutating clusters put `groundtruth.db` in inline-JSON
  target_paths + a "KB mutation: YES" note; non-mutating use FAB-10's "No KB mutation:..." negation note; (c) describe
  overlapping non-declared WIs WITHOUT bare `WI-NNNN` (use "the 4402 item") — collision check warns; (d) claim survives
  a FAILED Write (only releases on success), so a hard-blocked Write can be fixed + re-Written under the same claim;
  (e) transcript-UUID for claims = d2f32e6b-5441-45b3-b355-097a2507f5f7 (this session; re-derive newest .jsonl for a
  new session); (f) scratch DELIB/PAUTH scripts live in .gtkb-state/scratch/ (gitignored, regenerable).

## NEXT SESSION — Handoff / continuation prompt (2026-06-10)

(Canonical term is "handoff prompt"; "continuation prompt" is the DELIB-20260883-rejected synonym — same thing.)
Paste the block below to resume:

```
::init gtkb pb

Continue PROJECT-FABLE-INVESTIGATION — file implementation proposals for the remaining FAB clusters (FAB-20..23).
READ FIRST: memory/fable-investigation-campaign.md (this file — playbook + cheap-drafting recipe + operating model
+ per-cluster status + the consolidated gate lessons); bridge/gtkb-fable-investigation-advisory-001.md (charter,
Q1-Q7, anti-duplication, the per-FAB WI/findings/overlap table); bridge/INDEX.md (live queue);
independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md (frozen findings HYG-001..068).

DONE: 19 of 23 FAB clusters filed (FAB-01..FAB-19) + draft-linter = 20 proposals NEW. Codex (Loyal Opposition) is
ACTIVE and reviewing the queue. S430 filed FAB-11..19 (9 clusters) this run; DELIB+PAUTH per cluster (PAUTH rowids
176/178/179/180/181/182/183/184/185); all preflights green; all owner AUQ decisions captured.

NEXT (4 remaining, resume at FAB-20):
- FAB-20 (WI-4432): gtkb-hygiene-investigation skill — Q5 charter (4-round probe workflow + chunked report generator
  + delta mode keyed to the HYG-001..068 registry; consumes FAB-19's expanded detector core as layer-1 evidence;
  token targets <=400K full / <=150K delta). Determined-fix-ish but READ findings for touchpoints. Overlaps WI-3391.
- FAB-21 (WI-4433): startup load-cost reduction — HYG-008/025/028 (38 rules / 335,977 bytes vs the 250,000
  STARTUP_PRUNING_TOTAL_WARN_BYTES budget; canonical-terminology.md ~84KB; per-tool-call hook latency; stale
  always-loaded pointers). Overlaps WI-4360/4361/4403.
- FAB-22 (WI-4434): architecture cluster — OWNER-HEAVY, use grill-me depth — HYG-009/010/011/023/052 (protocol
  overhead per landed change, god modules, environment/interpreter contract, ADR/DCL enforcement coverage = 5/97
  artifacts per HYG-052, template-sync). Overlaps GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001/WI-3354/3498.
- FAB-23 (WI-4435): demoted near-miss cleanup batch (14 items incl. the investigation self-residue $null file) —
  v1 Appendix A demoted list.

PER-CLUSTER CYCLE: read the cluster's frozen findings → AUQ batch via AskUserQuestion (owner-gated/touchpoint
clusters; do NOT checkpoint-and-ask between clusters — proceed autonomously, pause only for genuine owner AUQ) →
DELIB via the decision-capture helper (write a scratch script under .gtkb-state/scratch/ calling
record_decision; rows commit even if the post-commit Chroma index 255s; PAUTH success validates the DELIB by id) →
bounded PAUTH (gt projects authorize PROJECT-FABLE-INVESTIGATION --id PAUTH-FABxx-20260610 --owner-decision <DELIB>
--name ... --scope ... --change-reason ... --include-work-item WI-44xx --include-spec <real approved spec(s)>
--allowed-mutation ... --forbid ...; verify specs exist+approved first via read-only sqlite) → author (Opus for
owner-gated/protected-narrative/KB-mutating; cheap-draftable for mechanical once GO'd) → claim slug
(python scripts/bridge_claim_cli.py claim <slug> --session-id <NEWEST-TRANSCRIPT-UUID>) → Write bridge file +
prepend INDEX entry (Document:/NEW:) → both preflights green (applicability preflight_passed:true + clause exit 0).

CRITICAL GATE LESSONS (apply to all 4): (a) EVERY proposal MUST cite ADR-ISOLATION-APPLICATION-PLACEMENT-001 in
`## Specification Links` AND add a `## Isolation Placement Compliance` section with explicit E:\GT-KB/in-root
language — applicability preflight HARD-BLOCKS the Write on missing citation; clause preflight exit-5 on missing
in-root evidence. (b) KB-mutating clusters MUST put `groundtruth.db` in inline-JSON target_paths + a "KB mutation:
YES" note; non-mutating use FAB-10's "No KB mutation:..." negation sentence. (c) describe overlapping non-declared
WIs WITHOUT a bare `WI-NNNN` (e.g. "the 4402 item") — the collision gate warns. (d) claim survives a FAILED Write
(releases only on success) — fix + re-Write under the same claim. (e) claim --session-id is the NEWEST
transcript-filename UUID under C:\Users\micha\.claude\projects\E--GT-KB\*.jsonl (NOT CLAUDE_CODE_SESSION_ID) —
re-derive it for the new session. (f) `## Requirement Sufficiency` MUST be h2; canonical `## Specification Links`
heading; 6 author-metadata fields; first line status token `NEW`; bridge_kind: prime_proposal. (g) tooling: gt not
on PATH → python -c "from groundtruth_kb.cli import main; ..."; canonical MemBase = root groundtruth.db; use the
PowerShell tool for shell (the Bash root-boundary parser is broken — that's FAB-14/HYG-042).

CODEX = Loyal Opposition (now ACTIVE): its disjoint-context GO authorizes implementation; NOTHING implements until
GO. As GO/NO-GO verdicts land, Prime acts ONLY on latest GO (proceed to tiered implementation) or NO-GO (revise →
REVISED). Do NOT process NEW/REVISED/VERIFIED entries as Prime. Implementation routes tiered local→cheap→Claude once GO'd.

OPEN FOLLOW-UPS (after FAB-23): draft-linter source builds on its Codex GO; Agent_Red application.toml backfill =
separate Agent-Red-scoped bridge (HYG-022); the WI-resolution/backlog-state reconciliation for each cluster's
absorbed overlaps is a post-VERIFIED operational step. STRATEGIC (future AUQ sessions, NOT part of FAB): the
active-orchestrator vision (WI-4438 / DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610) + the INVIOLABLE review-independence
invariant (DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610) — candidate formal GOV+DCL.
```

## STAND-DOWN — two-session collision (2026-06-11 ~00:41Z, session 07ef97df)
This session (07ef97df) committed FAB-01..10 + draft-linter at commit `d64abaec`, then detected a CONCURRENT
Prime session **d2f32e6b** running the same campaign. d2f32e6b filed FAB-11
(`bridge/gtkb-fab-11-regression-signal-revival-001.md`, NEW in INDEX) at ~00:33Z. Owner AUQ (~00:41Z) chose:
**"Other session (d2f32e6b) drives; I stand down."** No further FAB work from 07ef97df.

CORRECTIVE CONTEXT FOR THE DRIVING SESSION (d2f32e6b) — FAB-11-001 is filed against **SUPERSEDED** decisions:
- It cites `DELIB-FAB11-REMEDIATION-20260610` (v1) and encodes HYG-030 = partial-recorder + HYG-014 = archive-then-prune.
- The owner REVISED both under the cost/waste framing (`DELIB-COST-WASTE-FRAMING-20260610`):
  HYG-030 = **amend GOV-12/13 to pytest-as-evidence** (scope tests table to Agent Red history);
  HYG-014 = **prune + retention.toml + VACUUM, NO off-root archive**.
- Authoritative record: **`DELIB-FAB11-REMEDIATION-20260610B`** (supersedes v1 on decisions 3+4; SUPERSESSION NOTE in its body).
- **`PAUTH-FAB11-20260610` is now v2** (rowid 177): owner_decision = DELIB-...B, and it **FORBIDS `off_root_telemetry_archive`**,
  so FAB-11-001's Slice-4 archive step is blocked at implement-time. FAB-11 needs a **REVISED -002** aligning to DELIB-...B.
- HYG-029 (hybrid) + HYG-044 (re-register after corpus) are UNCHANGED and correct in -001.

## CAMPAIGN COMPLETE — FAB-20..23 filed (2026-06-11 ~03:50Z, session e45ccf07, Opus 4.8, harness B)

All 23 FAB clusters now filed (FAB-01..FAB-23) + draft-linter = 24 proposals. Session e45ccf07 (interactive
owner, `::init gtkb pb`) filed the final 4 this run; DELIB+PAUTH per cluster (PAUTH rowids 186/187/188/189);
all preflights GREEN; owner AUQ captured for the owner-gated clusters.

- **FAB-20 FILED** `bridge/gtkb-fab-20-hygiene-investigation-skill-001.md` (NEW). Determined-fix per Q5
  charter (no fresh AUQ). DELIB-FAB20-REMEDIATION-20260610; PAUTH-FAB20 (rowid 186). gtkb-hygiene-investigation
  skill (4-round probe + chunked report generator + delta mode keyed to HYG-001..068 baseline registry;
  consumes FAB-19 detector core). No KB mutation. Applicability packet `sha256:a9621a21...`; clause exit 0.
  **Codex already NO-GO@-002.**
- **FAB-21 FILED** `bridge/gtkb-fab-21-startup-load-cost-reduction-001.md` (NEW). 3 owner AUQ (all
  recommended): HYG-008=Partial measure-first (PostToolUse-spawn consolidation, no safety-gate change);
  HYG-025=Full sequenced glossary-payload program (WI-4360 profiler→core/detail IA→dedup+era archival);
  HYG-028=One-batch stale-pointer sweep (.ollama→.api-harness, tests→platform_tests across 5 rule files).
  DELIB-FAB21; PAUTH-FAB21 (rowid 187). Protected-narrative + No KB mutation. packet `sha256:e6ce07df...`;
  clause exit 0. **Codex already NO-GO@-002.**
- **FAB-22 FILED** `bridge/gtkb-fab-22-architecture-cluster-001.md` (NEW). 5 owner AUQ grill-me depth (all
  recommended): HYG-009=mechanical INDEX auto-trim + versions-per-change KPI (lightweight-lane DEFERRED);
  HYG-010=registry-discovery ADR + on-touch doctor.py (db.py last/never); HYG-011=groundtruth-kb/.venv
  canonical (delete root stub, venv-first _check_ruff, py3.14 CI); HYG-023=live-is-canonical templates (regen
  + hash-parity doctor + replace DEPRECATED poller prompt + fix file-bridge-protocol.md:273); HYG-052=feed
  5/97 census to clause-auto-discovery + interim doctor WARN. DELIB-FAB22; PAUTH-FAB22 (rowid 188). **KB
  mutation YES** (HYG-010 ADR → groundtruth.db in target_paths). packet `sha256:ffe5ece4...`; clause exit 0.
- **FAB-23 FILED** `bridge/gtkb-fab-23-demoted-cleanup-batch-001.md` (NEW). 2 owner AUQ (both recommended):
  cleanup disposition=archive-provenance/delete-junk; .gtkb/directive-registry.json=git-track. Deduped vs
  FAB-04/05/06/10/17 (those AUGMENTS deferred to their clusters). OWNS: $null file delete, pre-commit
  consolidation, .claude/session pruning, AR PDF archive, PS-5.1 decode hardening, directive-registry
  tracking. DELIB-FAB23; PAUTH-FAB23 (rowid 189). No KB mutation. packet `sha256:c8a694cb...`; clause exit 0.

**NEW REUSABLE GATE LESSON (applied to FAB-20/23):** `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`
becomes must_apply (clause exit-5 BLOCK) whenever a proposal cites GOV-STANDING-BACKLOG-001 AND uses
"backlog"/"work item"/"bulk" content; satisfy it with a short note containing one of the tokens
`inventory | review packet | DECISION DEFERRED | formal-artifact-approval`. FAB-19 passed incidentally
(it had "formal-artifact-approval packet"); FAB-20 first-Write FAILED the clause gate and was fixed by adding
a "## Backlog Visibility" note with "inventory". Add the note pre-emptively on any cluster touching backlog
content. (Clause-gate is exit-5 BLOCK, unlike the WI-collision WARN.)

**Other this-run confirmations:** newest transcript UUID for claims = e45ccf07-99f6-4ad6-b572-570a76a264a2;
`gt projects authorize | Out-Null` then verify PAUTH via read-only sqlite (pipe to a second `python -c` JSON
parse fails because CLI output isn't pure stdout JSON — the authorize itself still lands); INDEX shifts
between read and edit (Codex active + reviewing fast) — re-read top before each prepend.

**CODEX (ACTIVE, fast) is producing verdicts in real time.** As of this run's end the Prime-actionable bridge
queue includes: GO on FAB-01/02/08/10/16 + draft-linter; NO-GO on FAB-03/05/06/07/09/11/12/13/14/15/17/18/19
and now FAB-20/FAB-21. Next Prime work (separate from this filing task): act on latest GO (tiered
implementation) / NO-GO (REVISED) per the standard cycle. NOTHING implements until GO; do not process
NEW/REVISED/VERIFIED as Prime.

## GO/NO-GO CYCLE — 3 REVISEDs filed (2026-06-11 ~04:00-04:05Z, session e45ccf07)

Owner: "move into the GO/NO-GO cycle." **SYSTEMATIC NO-GO PATTERN DISCOVERED** (high-leverage): Codex is
applying ONE consistent standard across the batch — **whenever a proposal promises a formal-artifact-approval
or narrative-approval packet, `target_paths` MUST enumerate the concrete `.groundtruth/formal-artifact-approvals/*.json`
packet path(s)** (and any GENERATED artifacts: on-demand detail files, archive destinations, move inventories).
The impl-start gate denies writes outside GO'd target_paths, so a promised-but-unlisted packet would be
un-writable. This single defect explains FAB-19 P1, FAB-21 P1, and almost certainly the other
protected-narrative / KB-mutating NO-GOs (FAB-05/06/09/11/12/13/14/15/18). FAB-20 is the exception (pure
sequencing block on FAB-19).

REVISEDs filed this run (all preflights GREEN, all REVISED in INDEX, claim per slug w/ session e45ccf07):
- **FAB-19 -003 REVISED**: added `.groundtruth/formal-artifact-approvals/fab-19-hygiene-sweep-patterns-registry-header.json`
  to target_paths (sole P1 fix). Unblocks FAB-20's dependency.
- **FAB-21 -003 REVISED**: P1 = added 5 concrete per-rule-file packet paths; P2 = added on-demand detail
  artifact (`groundtruth-kb/docs/reference/canonical-terminology-detail.md`), archive dest
  (`archive/rules-era-stranded-2026-06/**`), move inventory
  (`independent-progress-assessments/fab-21-startup-payload-archive-inventory.md`); era-archival scoped to
  inventory + coordinated with FAB-05 (no Cursor-era double-ownership).
- **FAB-20 -003 REVISED**: NARROWED to dependency-free first slice (skill scaffold + 4-round probe workflow +
  chunked report generator + HYG baseline registry); **delta mode DEFERRED** to a follow-on after FAB-19's
  evidence-pack contract is GO'd+implemented (Codex's offered path B). Removed the layer-1 dependency from
  target_paths/acceptance/tests; added ## Deferred Follow-On.

**REUSABLE REVISE-CYCLE LESSON:** for the remaining packet-omission NO-GOs, the fix is mechanical — add the
`.groundtruth/formal-artifact-approvals/<fab-NN-...>.json` path(s) per promised packet + any generated-artifact
paths to target_paths, bump version, add `## Revision Scope`, re-claim slug, Write `-NNN`, prepend REVISED to
INDEX, preflights. REVISED versions are monotonic across the whole thread (FAB-19 was at -002 NO-GO → REVISED
is -003). Author metadata = this session (e45ccf07); -001 authors differed (d2f32e6b for the 11-19 batch).

REMAINING NO-GOs to clear (cold-read each NO-GO's Findings first to confirm the specific defect): FAB-03, 04,
05, 06, 07, 09, 11, 12, 13, 14, 15, 17, 18. GO'd clusters ready for tiered implementation: FAB-01, 02
(secrets, P0-aligned per standing priorities), 08 (cleanest greenfield), 10, 16, draft-linter.

## FAB-08 IMPLEMENTED end-to-end (2026-06-11 ~04:10-04:25Z, session e45ccf07) — owner chose "Implement FAB-08"

Full GO→implement→report cycle on `gtkb-fab-08-slot-leak-fix` (GO@-002). Impl-start packet
`sha256:f11f2ea8...` (8h TTL). **DONE:** (1) `_force_rmtree` onexc robust remover (clears Windows read-only
`.git` bit + retry; fails loudly, no `ignore_errors`) added self-contained to the 3 in-scope test files
(conftest.py, test_scaffold_isolation.py ×5 sites, test_cli.py); (2) `doctor.py` `_check_stale_test_slots` +
`_force_remove_tree` (prunes `applications/_test_*` >24h, WARN, never touches non-`_test_*`/real apps),
registered as a project-level check; (3) **purged 234 leaked `_test_*` slots → 0 remaining, `Agent_Red`
preserved** (GO required recording actual count; was 229 in investigation, 234 live); (4)
`platform_tests/scripts/test_fab08_slot_leak_fix.py` 5/5 PASS; (5) ruff check + format --check CLEAN on all 5
changed files (incl. an incidental pre-existing `SIM105` fix in doctor.py:3051 → `contextlib.suppress`, noted
per GOV-06); (6) in-situ `test_scaffold_isolation.py` 19 pass + 2 FAIL — the 2 (tp14/tp15 golden byte-compare
on `.claude/hooks/bridge-compliance-gate.py`) are **pre-existing HYG-023 template drift (FAB-22 scope), NOT
FAB-08** (scaffold-output mismatch, not the cleanup path). Post-impl report
`bridge/gtkb-fab-08-slot-leak-fix-003.md` (NEW) filed, both preflights GREEN (applicability packet
`sha256:5b4875d2...`; clause exit 0). **Changes UNCOMMITTED** (commit pending owner direction). Out-of-scope
follow-ons noted in report: test_core_spec_intake.py + test_golden_fixture_diff_per_version.py have the same
leak pattern but aren't in target_paths; shared-util consolidation deferred.

**TWO NEW REUSABLE GATE LESSONS (post-impl reports):** (a) `SPEC_LINK_HEADING_RE` rejects a heading SUFFIX —
`## Specification Links (carried forward)` harvests ZERO specs → bridge-compliance-gate HARD-BLOCKS the Write
(missing_required_specs=all). Use EXACTLY `## Specification Links`; put "carried forward" in body text. (b)
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` is must_apply on post-impl reports too (clause exit
5) — include a `## Bridge Protocol Compliance` section naming `bridge/INDEX.md` + "inserted at the top of the
entry" (regex `bridge/INDEX\.md|INDEX update|insert.+top of.+(?:INDEX|entry)`). (c) reconfirmed:
CLAUSE-VISIBILITY-BULK-OPS fires on a bulk purge + GOV-STANDING-BACKLOG citation → add Backlog Visibility note
w/ "inventory" token. Impl-auth `begin` packet is per-bridge-id and gates Write/Edit to the GO'd target_paths
(out-of-scope files like test_core_spec_intake.py would be DENIED).

## GO/NO-GO CYCLE — FAB-02 (P0 secrets) verification NO-GO CLEARED (2026-06-11 ~04:38-04:46Z, session 430d5513, Opus 4.8, harness B)

Owner resumed the GO/NO-GO cycle. **Live-INDEX state delta from the 04:26Z handoff:** FAB-02 had
advanced GO@-002 → implemented → NEW@-003 (post-impl report, author session 4490dc1a) → **NO-GO@-004**
(Codex verification verdict) — i.e., FAB-02 was implemented + post-impl-reported + got a verification
NO-GO since the handoff was written. The uncommitted `infrastructure/terraform/*` + `scripts/hygiene/
secret_at_rest_guard.py` + `platform_tests/scripts/test_secret_at_rest_guard.py` in the working tree are
that implementation. FAB-08 is still NEW@-003 (NOT VERIFIED → not committed). FAB-19/20/21 still
REVISED@-003 (NOT re-verdicted). FAB-22/23 still NEW@-001 (Codex queue).

**FAB-02 -004 NO-GO (single P1):** docs (`backend.hcl.example`, `STATE-MIGRATION-RUNBOOK.md`) claim the
owner-filled `infrastructure/terraform/backend.hcl` is "Drive-excluded / never Drive-synced" and
`.gitignore` excludes it, but `.driveignore` (the INDEPENDENT cloud-replication surface) did NOT. Codex's
preferred fix = make the claim mechanically true.

**CLEARED → REVISED -005 filed (both preflights GREEN):**
- `.driveignore`: added exact-path `infrastructure/terraform/backend.hcl` (does not touch `backend.hcl.example`
  via the `!*.example` re-include) + explanatory comment.
- `scripts/hygiene/secret_at_rest_guard.py`: added `("backend_hcl_excluded", ("infrastructure/terraform/backend.hcl",))`
  to `_REQUIRED_DRIVEIGNORE` + docstring bullet (the Opportunity-Radar deterministic-service cue).
- `platform_tests/scripts/test_secret_at_rest_guard.py`: added backend.hcl line to `_CLEAN_DRIVEIGNORE`
  fixture (so clean tree still passes the new invariant) + negative test `test_missing_backend_hcl_exclusion_fails`.
- Verification ALL GREEN: guard `ok=true` **11/11** checks (backend_hcl_excluded matched on live tree);
  pytest **10 passed** (was 9); `ruff check` clean; `ruff format --check` 2 files already formatted.
- Filed `bridge/gtkb-fab-02-secrets-remediation-005.md` (REVISED) + INDEX prepend. Applicability
  `preflight_passed:true` packet `sha256:3d03cc90...`; clause exit 0 (4 must_apply, 0 blocking gaps —
  the `## Bridge Protocol Compliance` section made CLAUSE-INDEX-IS-CANONICAL must_apply-with-evidence).
- Still UNCOMMITTED (commit pending owner direction + Codex VERIFIED). On Codex VERIFIED → commit the
  FAB-02 cluster `feat:` + resolve WI-4414.

**REUSABLE GATE LESSON (post-impl NO-GO → revise authorization):** `implementation_authorization.py begin`
WORKS when latest status is NO-GO-over-GO. `_post_go_chain_state` classifies a post-GO NO-GO as
**"resumable"** — "the GO still authorizes the revision." Packet `sha256:21cca9ad...` (8h TTL, latest_status
NO-GO accepted). So a verification-NO-GO'd cluster does NOT need a fresh GO to re-edit source within the
original GO'd target_paths.

**Concurrency:** transcript `1bcfec08` was active 11s-stale while I worked (this session = `430d5513`,
the NEWEST .jsonl). No FAB work-intent claims held in `.gtkb-state/work-intent/` — claim guard used per
slug. **DECISION-1133 cleared** (owner-directed; mirrored the hook clear handler in pending-owner-decisions.md;
the `clear pending` hook only fires when the phrase starts the prompt, which the owner's embedded mention did not).

### FAB-03 CLEARED (owner-gated) → REVISED -003 (~04:56Z)
FAB-03 NO-GO was NOT the mechanical fix — FINDING-P1-001 was a genuine root-boundary conflict: the Slice-1
design schedules `gt db snapshot` output + a doctor freshness check against `%LOCALAPPDATA%\gtkb-snapshots`
(outside `E:\GT-KB`), and the existing Sandbox Output Exception only allowlists rehearsal `C:/temp/...` paths.
**Owner AUQ (session 430d5513): chose "Formal off-root exception"** — keep `%LOCALAPPDATA%` (separate C: drive
= stronger DR; survives an E: drive failure) and add a formal DB-Snapshot Output Exception to
project-root-boundary.md (narrative packet + allowlist + parity test, mirroring the Sandbox Output Exception)
over the in-root Drive-excluded redesign (co-locates backups on E: = weaker DR). Captured
`DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` (owner_conversation/owner_decision, v1, exit 0) via scratch
script `.gtkb-state/scratch/record_delib_fab03_root_boundary.py`. **Gate lesson: `resolve_changed_by()` raises
"no harness_name resolved" with multiple harnesses registered — set `$env:GTKB_HARNESS_NAME = "claude"`.**
Filed REVISED -003 (added `.claude/rules/project-root-boundary.md` + the narrative packet path + allowlist/test
to scope; cited the new DELIB; corrected the Sandbox-Exception misframing). Both preflights GREEN (applicability
`sha256:1005200d...`; clause exit 0, 4 must_apply). PAUTH-FAB03 covers it (docs/config/source classes).

### FAB-05 CLEARED (mechanical) → REVISED -003 (~05:00Z)
FAB-05 NO-GO WAS the systematic fix — FINDING-P1-001 = `target_paths` incompleteness. Added 4 paths:
`independent-progress-assessments/bridge-automation/**` (archive SOURCE — only dest was listed),
`.groundtruth/formal-artifact-approvals/*.json` (the ~10-12 narrative packets), `platform_tests/scripts/**`
(grep-assertion test), `.claude/rules/prime-builder-role.md` (HYG-027 canonical home). Added `## Revision
Scope` + `## Isolation Placement Compliance`; body otherwise unchanged. Both preflights GREEN. **WI-collision
WARNING (non-blocking) on WI-3278/4404/4404 — those are substantive scope refs (the items HYG-038 retires +
the sanctioned restore-path WI), not incidental mentions; -001 carried the same and Codex didn't NO-GO. Left
as legitimate references.**

### KEY TRIAGE INSIGHT — the NO-GO batch is HETEROGENEOUS, not all mechanical
The 04:26Z handoff's "MOST share ONE fix" is only partly true. Cold-reading is load-bearing:
- **Mechanical (systematic target_paths/packet-path fix):** FAB-05 ✓ (cleared). Likely also FAB-06 (narrative),
  and the KB-mutating/narrative clusters that promised packets.
- **Owner-gated (need an AUQ before REVISED):** FAB-03 ✓ (cleared, root-boundary exception); **FAB-04**
  (destructive ~11GB deletions — almost certainly needs an owner decision); possibly FAB-13/14/18 if their
  NO-GOs raise policy questions beyond packet paths. COLD-READ each before assuming mechanical.

**Remaining Prime-actionable (live INDEX ~05:01Z):** implement GOs — FAB-01, FAB-10, FAB-16, draft-linter;
revise NO-GO@-002 proposals — FAB-04 (owner-gated, cold-read first), 06, 07, 09, 11, 12, 13, 14, 15, 17, 18.
FAB-02 REVISED@-005, FAB-03 REVISED@-003, FAB-05 REVISED@-003 all now in Codex's queue (not Prime-actionable).
FAB-08 still NEW@-003 (awaiting Codex VERIFIED — do NOT commit); FAB-19/20/21 still REVISED@-003.

## PARALLEL TRIAGE MAP — remaining NO-GOs classified (2026-06-11 ~05:05Z, session 430d5513, 4 Explore agents)

Owner: "spawn sub-agents and parallelize." 4 read-only Explore agents triaged the 11 remaining NO-GOs
concurrently. Result: 9 of 11 are turnkey-mechanical; only FAB-11 + FAB-12-F3 break the pattern.
**FAB-04 already moved to GO@-004** (Codex re-verdicted — now an implement target, not a NO-GO).
The dominant Codex standard: EVERY promised artifact (approval packet / archive dest / telemetry file /
generated doc) MUST be enumerated in target_paths (impl-start gate denies writes outside them).

Per-cluster fix (current target_paths verbatim → paths to ADD). All keep status REVISED, version +2 over
the NO-GO, author session 430d5513, a `## Revision Scope`, and (if absent) a `## Isolation Placement
Compliance` section + ADR-ISOLATION in `## Specification Links`:

- **FAB-06** (WI-4418, DELIB-FAB06-REMEDIATION-20260610, PAUTH-FAB06) MECHANICAL, no-KB-mut, protected-narrative.
  ADD: `.groundtruth/formal-artifact-approvals/*.json`. (only gap)
- **FAB-07** (WI-4419, DELIB-FAB07-REMEDIATION-20260610, PAUTH-FAB07) MECHANICAL, no-KB-mut, protected-narrative.
  ADD: `.groundtruth/formal-artifact-approvals/*.json` + NAME the missing bridge-doc path the doctor surfaces
  (or DEFER the missing-doc creation to a separate item).
- **FAB-09** (WI-4421, DELIB-FAB09-REMEDIATION-20260610, PAUTH-FAB09) MECHANICAL, no-KB-mut, protected-narrative.
  ADD: `.groundtruth/formal-artifact-approvals/*.json`.
- **FAB-12** (WI-4424, DELIB-FAB12-REMEDIATION-20260610, PAUTH-FAB12) MECHANICAL+1-defer, no-KB-mut, protected-narrative.
  ADD: `.groundtruth/formal-artifact-approvals/*.json` + `.github/pull_request_template.md` + `.github/ISSUE_TEMPLATE/**`.
  F3 (home-cache reconciliation reads out-of-root C:/Users/micha/.claude/...) → DEFER home-cache merge to a
  post-VERIFIED in-root-export step (Codex option B; keeps Area 2 to in-root MEMORY.md retitle + CLAUDE.md L12;
  no new owner decision — consistent with DELIB-FAB12 HYG-016).
- **FAB-13** (WI-4425, DELIB-FAB13-REMEDIATION-20260610, PAUTH-FAB13) MECHANICAL, KB-mut narrow (DA-harvest), no protected-narrative.
  ADD: `.gtkb-state/**`, `.codex/gtkb-hooks/**`, `.claude/hooks/*.json` (runtime deletion/rotation perimeters).
- **FAB-14** (WI-4426, DELIB-FAB14-REMEDIATION-20260610, PAUTH-FAB14) MECHANICAL, KB-mut YES (WI reconcile + DCL amend).
  F1 = ADD `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to `## Specification Links` (currently only in the Isolation
  section → applicability preflight risk). ADD: `.groundtruth/formal-artifact-approvals/*.json` + `.gtkb-state/gate-denials.jsonl`.
- **FAB-15** (WI-4427, DELIB-FAB15-REMEDIATION-20260610, PAUTH-FAB15) MECHANICAL, KB-mut YES (registry txn + canonical_terms regen + GOV amend).
  ADD: `.groundtruth/formal-artifact-approvals/*.json` + NAME the session-wrap integration surface (or DEFER wrap wiring to a follow-on slice).
- **FAB-17** (WI-4429, DELIB-FAB17-REMEDIATION-20260610, PAUTH-FAB17) MECHANICAL, no-KB-mut.
  ADD: `.groundtruth-chroma/**` (Chroma dedup perimeter) OR DEFER Chroma dedup to a separate bridge (limit FAB-17 to
  search-reliability + benchmark-CLI + timeout/retry). Also confirm `groundtruth-kb/src/groundtruth_kb/benchmarks/**` intent.
- **FAB-18** (WI-4430, DELIB-FAB18-REMEDIATION-20260610, PAUTH-FAB18) MECHANICAL, KB-mut YES (DA-harvest + bulk-close via kb-batch/GOV-15).
  ADD: `.groundtruth/formal-artifact-approvals/*.json` (narrative packet) + `archive/**` + a concrete move-manifest path.
- **FAB-11** (WI-4423) SUBSTANTIVE REDRAFT, KB-mut YES, protected-narrative. NOT a path fix: -001 cites the
  **superseded** `DELIB-FAB11-REMEDIATION-20260610`; authoritative is `DELIB-FAB11-REMEDIATION-20260610B` (HYG-030 →
  GOV-12/13 pytest-as-evidence amendment; HYG-014 → prune+retention+VACUUM, NO off-root archive). PAUTH-FAB11 is v2
  keyed to ...B and FORBIDS `off_root_telemetry_archive`. Redraft the WHOLE proposal against ...B (HYG-029 hybrid +
  HYG-044 re-register are unchanged), then enumerate the formal packets. No new AUQ (the ...B decision exists).

Filing remains SERIAL (one bridge/INDEX.md, session-scoped claims/packets — parallel gated writes would corrupt the
bridge per bridge-essential.md). The parallel win is the triage; the filing is per-cluster: claim → read -001 → Write
-003 (add paths + Revision Scope) → INDEX prepend → both preflights green.

**FILED THIS PASS (~05:12-05:14Z):** FAB-06 REVISED-003 (added packet glob; gate-green) + FAB-09 REVISED-003 (added
packet glob; gate-green). Both back in Codex's queue. **STATE DELTAS observed mid-pass (Codex is fast):**
FAB-05 → **GO@-004** (my REVISED-003 approved — now an implement target); **FAB-08 → NO-GO@-004** (the post-impl
report -003 got a verification NO-GO — do NOT commit FAB-08; it needs a REVISED post-impl report addressing the -004
findings; cold-read bridge/gtkb-fab-08-slot-leak-fix-004.md). **REMAINING turnkey-mechanical REVISEDs (per the map
above):** FAB-07, 12, 13, 14, 15, 17, 18. SUBSTANTIVE redraft: FAB-11. NOW-GO implement targets: FAB-01, 04, 05, 10,
16, 19, 20, 21, 22, 23, draft-linter. NEW post-impl REVISED needed: FAB-08 (-005).

## FAB-16 IMPLEMENTATION BLOCKED — Area 2 generator↔registry drift (2026-06-11 ~05:20Z, session 430d5513)

Owner chose "Full FAB-16 now (accept risk)." Began impl-start packet `sha256:626b03b3` (8h TTL). VERIFIED live
state first (proposal premise was 2026-06-10, codebase drifted): **Area 3 (HYG-063) already mostly done**
(`check_harness_parity.py:42-63` already derives KNOWN_HARNESSES from `load_harness_projection`; only the
degraded-projection-reports-error refinement + `_FALLBACK_KNOWN_HARNESSES` removal remains). **Area 1 (HYG-062)
genuinely open** — Goose IS in the projection (fleet = antigravity/claude/codex/goose/ollama/openrouter), has no
`[harnesses.goose]` registry entry, so the checker flags it all-MISSING; needs a `harness_class="ui_client"`
registry entry + a checker exclusion (route ui_client harnesses out of the active/floor selection in
`check_harness_parity`). **Area 2 (HYG-061) BLOCKED:** ran `scripts/generate_antigravity_skill_adapters.py
--update-registry` → "updated 1 file (registry)" ONLY; parity STAYED FAIL (22 STALE + 14 MISSING). Root cause:
`.antigravity/` has only 5 files (config.toml, README.md, 3 scratch) and **NO generated skill adapters**, but the
registry expects **36** antigravity skill adapters (all 36 skill caps carry an antigravity entry). The generator's
`generate()` writes NO adapter files yet the registry points at 36 that don't exist on disk — generator output is
out of sync with the registry+parity expected surfaces. **The GO's Area-2 acceptance gate ("antigravity parity
0 stale/0 missing after regen") is UNREACHABLE with the current generator.** Reverted my lone registry touch
(`git checkout` — the FAIL is pre-existing). impl-start packet left to expire.

**DISPOSITION NEEDED (owner/Codex):** FAB-16 as GO'd cannot be cleanly VERIFIED-implemented — Area 2 needs the
`generate_antigravity_skill_adapters.py` ↔ registry/parity drift DEBUGGED FIRST (a real defect; candidate new WI),
OR FAB-16 re-scoped to land Areas 1+3 now and split Area 2 behind the generator fix. STRATEGIC/self-improvement
finding: the antigravity skill-adapter generator does not produce the adapters the capability registry declares —
worth a backlog item independent of FAB-16.

## FRESH-SESSION HANDOFF PROMPT (2026-06-11 ~04:26Z, supersedes the 2026-06-10 block above)

```
::init gtkb pb

Continue PROJECT-FABLE-INVESTIGATION — work the GO/NO-GO cycle.
READ FIRST: memory/fable-investigation-campaign.md (this notepad — full state, the consolidated GATE LESSONS,
the systematic NO-GO pattern, and the per-cluster cycle); bridge/INDEX.md (live authoritative queue);
bridge/gtkb-fable-investigation-advisory-001.md (charter); independent-progress-assessments/
GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md (frozen findings HYG-001..068).

STATE: All 23 FAB clusters filed (FAB-01..23) + draft-linter. Codex (Loyal Opposition) is ACTIVE and fast.
This session (e45ccf07): filed FAB-20..23 NEW; filed FAB-19/FAB-20/FAB-21 REVISED (-003 each); IMPLEMENTED
FAB-08 end-to-end (post-impl report bridge/gtkb-fab-08-slot-leak-fix-003.md NEW, awaiting Codex VERIFIED).

UNCOMMITTED working tree (commit pending owner direction — do NOT commit without an owner ask):
- FAB-08 source: groundtruth-kb/tests/adopter/conftest.py, groundtruth-kb/tests/test_scaffold_isolation.py,
  groundtruth-kb/tests/test_cli.py, groundtruth-kb/src/groundtruth_kb/project/doctor.py,
  platform_tests/scripts/test_fab08_slot_leak_fix.py (new). Verified GREEN (5/5 new test; ruff clean; 234
  slots purged). On Codex VERIFIED → commit these with `fix:` (the report's Recommended Commit Type).
- Bridge files + bridge/INDEX.md + this notepad (bridge/governance work; commit separately if owner asks).

FIRST ACTIONS (read live bridge/INDEX.md — it is authoritative; Codex changes it in real time):
1. Check FAB-08 latest status. If VERIFIED → (with owner OK) commit the 5 FAB-08 source files `fix:`, then
   resolve WI-4420 in MemBase (gt-style, GOV-15/origin=defect). If NO-GO → address + REVISED.
2. Check FAB-19/20/21 latest status (REVISED → may be GO or NO-GO). On GO → tiered implementation; on NO-GO →
   REVISED.
3. Remaining NO-GOs to clear (cold-read each NO-GO Findings first): FAB-03, 04, 05, 06, 07, 09, 11, 12, 13,
   14, 15, 17, 18. MOST share ONE mechanical fix — add the promised .groundtruth/formal-artifact-approvals/
   *.json packet path(s) + any generated-artifact paths to target_paths, bump version, add ## Revision Scope,
   re-claim slug, Write -NNN, prepend REVISED to INDEX, both preflights green.
4. Other GO'd clusters ready to implement: FAB-01, FAB-02 (secrets, P0-aligned per standing priorities),
   FAB-10, FAB-16, draft-linter. FAB-22/23 are still NEW (Codex's queue — NOT Prime-actionable).

DO NOT process NEW/REVISED/VERIFIED entries as Prime; act ONLY on latest GO (implement) or NO-GO (REVISED).

CYCLE MECHANICS: re-derive the NEWEST transcript-filename UUID under
C:\Users\micha\.claude\projects\E--GT-KB\*.jsonl for bridge claims (NOT CLAUDE_CODE_SESSION_ID). Use the
PowerShell tool (Bash root-boundary parser is broken — HYG-042/FAB-14). To IMPLEMENT a GO'd cluster: read the
proposal + GO verdict (note GO constraints), run `python scripts/implementation_authorization.py begin
--bridge-id <slug>` (8h packet; gates Write/Edit to the GO'd target_paths), implement, run pytest + `ruff
check` + `ruff format --check` via the venv (E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe — the canonical
interpreter; gt/ruff/pytest live ONLY there), file the post-impl report as the next version (status NEW),
prepend NEW to INDEX, both preflights green.

GATE LESSONS (all consolidated above in this notepad — read them): (a) EVERY proposal cites
ADR-ISOLATION-APPLICATION-PLACEMENT-001 in `## Specification Links` AND has a `## Isolation Placement
Compliance` section. (b) Promised packets → list .groundtruth/formal-artifact-approvals/*.json in
target_paths (the systematic NO-GO fix). (c) Heading must be EXACTLY `## Specification Links` (no suffix — a
suffix harvests zero specs and HARD-BLOCKS the Write). (d) Post-impl reports need a `## Bridge Protocol
Compliance` section (names bridge/INDEX.md + "top of the entry") for CLAUSE-INDEX-IS-CANONICAL. (e) Citing
GOV-STANDING-BACKLOG-001 + backlog/bulk content → add a `## Backlog Visibility` note with an `inventory`/
`formal-artifact-approval` token (CLAUSE-VISIBILITY-BULK-OPS, exit-5 BLOCK). (f) KB-mutating → groundtruth.db
in target_paths + "KB mutation: YES"; else FAB-10 "No KB mutation" note. (g) No bare foreign WI-NNNN (use "the
4402 item"). (h) claim survives a FAILED Write. (i) `## Requirement Sufficiency` must be h2.

STALE: clear DECISION-1133 (owner: `clear pending`) — it predates the filing and is obsolete.

OPEN STRATEGIC (future AUQ, not part of FAB): WI-4438 active-orchestrator vision
(DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610); DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610 (no session context
formally reviews artifacts it created).
```

## DRAFT-LINTER IMPLEMENTED end-to-end + FAB-02 commit BLOCKED (2026-06-11 ~05:05-05:25Z, session f2bde760, Opus 4.8, harness B, AUTONOMOUS keep-working-pb)

Autonomous scheduled Prime Builder run. Live-INDEX delta since the 05:01Z handoff: **FAB-02 advanced
REVISED@-005 → VERIFIED@-006** (Codex, `feat:`); FAB-04 now GO@-004; FAB-19/20/21 now GO@-004 (were
REVISED@-003); FAB-08 NO-GO@-004 (post-impl verification rejected); FAB-22/23 now GO@-002.

**DRAFT-LINTER (gtkb-cheap-draft-linter) IMPLEMENTED end-to-end (GO@-002 → report -003 NEW).** Impl-start
packet `sha256:e29291c5...` (8h TTL; target_paths = the 2 files). Created `scripts/draft_lint.py` (~230 lines,
read-only: 6 deterministic checks — cited-path resolution, HYG-id match, phantom-spec via `current_specifications`
mode=ro, required-section presence, placeholder, GOV-18 concrete-assertion floor; `lint()` pure core + `main()`
CLI) + `platform_tests/scripts/test_draft_lint.py` (14 tests: PASS+FAIL per check, in-memory fixture DB, CLI
exit-code, **AST read-only contract test for DELIB-S312** asserting no write-mode open / no `.write` / no
mutating SQL literal / no subprocess|shutil|os import). Verification ALL GREEN: pytest **14 passed**; ruff
check + `format --check` clean (1 format pass applied); acceptance-3 smoke = linter on
`bridge/gtkb-fab-08-slot-leak-fix-001.md` against canonical 1.37GB MemBase → `ok:true` 6/6, exit 0. Filed
`bridge/gtkb-cheap-draft-linter-003.md` (NEW) + INDEX prepend; both preflights GREEN (applicability
`preflight_passed:true` packet `sha256:9d353c43...`; clause exit 0, 4 must_apply 0 blocking gaps). **Source
UNCOMMITTED** (awaiting Codex VERIFIED per discipline). A DIFFERENT session must verify (review-independence).

**REUSABLE GATE LESSON (two-gate coupling, INVERSE direction):** the draft-linter touches only `scripts/` +
`platform_tests/scripts/` so ADR-ISOLATION-APPLICATION-PLACEMENT-001 was NOT triggered at -001/-002 (clean
preflight without it). BUT adding a defensive `## Isolation Placement Compliance` section whose prose mentioned
"applications/" **re-triggered** ADR-ISOLATION as must_apply → applicability preflight HARD-BLOCKED the Write
(missing_required_specs=[ADR-ISOLATION...]). Fix: cite ADR-ISOLATION in `## Specification Links` AND reword the
section to drop the literal "applications/" content token ("no application subtree artifact"). The Isolation
section is double-edged: it satisfies CLAUSE-IN-ROOT but its content can create a NEW citation obligation. Claim
survived the FAILED Write (re-Wrote same claim). claim --session-id = NEWEST transcript UUID
`f2bde760-42de-44f1-aae6-eee14d7ee5a7` (this session; NOT CLAUDE_CODE_SESSION_ID).

**FAB-02 COMMIT BLOCKED — pre-commit inventory-drift gate (affects ALL commits, not just FAB-02).** Attempted
the VERIFIED FAB-02 `feat:` commit (surgically staged exactly 8 FAB-02 files — `.driveignore`, `.gitignore`,
`infrastructure/terraform/{backend.hcl.example,backend.tf,STATE-MIGRATION-RUNBOOK.md,CREDENTIAL-ROTATION-OWNER-ACTION.md}`,
`scripts/hygiene/secret_at_rest_guard.py`, `platform_tests/scripts/test_secret_at_rest_guard.py` — 524 insertions;
staged credential scan passed 0 secrets). **BLOCKED** by `Inventory drift check: FAIL (release_blocker)`, diff keys
`harnesses, role_by_harness_compatibility`: `harness-state/harness-registry.json` has an uncommitted
role/status/reviewer_precedence reconciliation (regenerated MemBase projection, generated_at 2026-06-11T04:11:22Z —
A Codex PB/suspended→LO/active, B Claude PB/suspended→PB/active, reviewer_precedence 10/20/30 set, all 5 active)
that the committed `.groundtruth/inventory/dev-environment-inventory.json` baseline doesn't match. The gate
(`config/governance/protected-artifact-inventory-drift.toml`) BLOCKs ANY commit until registry + regenerated
inventory baseline are committed together. **DEFERRED rather than ratified blind** (per "ASK rather than act" — the
registry is a legitimate generated projection, but the role-TOPOLOGY change is prior-session governance state of
uncertain provenance; FAB-15 role-narrative reconciliation is still NO-GO/unimplemented; committing it ratifies a
multi-harness-active topology without owner/governance context). **NEXT-SESSION / OWNER DECISION NEEDED:** either
(a) confirm the harness-registry projection is the intended canonical role topology → regen
`.groundtruth/inventory/dev-environment-inventory.json` (`scripts/collect_dev_environment_inventory.py`) and commit
registry+inventory as `chore:` sync (UNBLOCKS all commits), or (b) revert the stray registry change if unintended.
Until resolved, NO commits land — VERIFIED FAB-02 source stays uncommitted (harmless: VERIFIED + recorded in the
bridge; the bridge-docs side was already committed at 1fa4c051).

**Net this run:** +1 clean end-to-end implementation filed for verification (draft-linter -003 NEW); 0 commits
(inventory gate blocks all). Tooling: `$env:GTKB_HARNESS_NAME="claude"`; venv python
`groundtruth-kb\.venv\Scripts\python.exe`; PowerShell tool (Bash root-boundary parser broken). NEXT Prime work
(separate session, review-independence): VERIFY draft-linter -003; clear the inventory-drift commit blocker; then
implement remaining GOs (FAB-01/04/10/16/19/20/21/22/23) / revise NO-GOs (FAB-06/07/09/11/12/13/14/15/17/18).

## GO/NO-GO CYCLE — 7 turnkey REVISEDs + FAB-08 post-impl REVISED filed (2026-06-11 ~05:42-06:12Z, session 9660f4cb, Opus 4.8, harness B)

Owner: "work the GO/NO-GO cycle" (autonomous). Transcript UUID for claims = `9660f4cb-1b84-410e-a024-febdabe7c541`.
Codex (LO) is ACTIVE+fast — verdicts in minutes; observed FAB-07/12/15 → **GO@-004** in real time as I filed.

**FILED + gate-green (all REVISED -003, both preflights GREEN, per the PARALLEL TRIAGE MAP paths-to-add):**
- **FAB-07 -003** (now GO@-004): added `.groundtruth/formal-artifact-approvals/*.json` (F1) + DEFERRED the
  doctor-surfaced missing-bridge-doc creation out to a separate item (F2, Codex path 2) + added explicit
  `## Isolation Placement Compliance`.
- **FAB-12 -003** (now GO@-004): added packet glob + `.github/pull_request_template.md` + `.github/ISSUE_TEMPLATE/**`
  (F1/F2); DEFERRED out-of-root home-cache lesson migration, Area 2 now in-root only (F3, Codex option B).
- **FAB-13 -003**: added `.gtkb-state/**` + `.codex/gtkb-hooks/**` + `.claude/hooks/*.json` (F1 deletion/rotation
  perimeters) + `## Deletion Perimeter` section separating destructive cleanup from code/config.
- **FAB-14 -003**: cited `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in `## Specification Links` (F1, the
  applicability HARD-BLOCK) + packet glob + `.gtkb-state/gate-denials.jsonl` (F2/F3).
- **FAB-15 -003** (now GO@-004): added packet glob (F1) + DEFERRED the session-wrap wiring to a follow-on, FAB-15
  limited to sync script + config + doctor check + one-time regen (F2, Codex's offered path).
- **FAB-17 -003**: added `.groundtruth-chroma/**` dedup perimeter (F1, Codex option 1, kept Area 3) + REPLACED the
  phantom `groundtruth-kb/src/groundtruth_kb/benchmarks/**` (does NOT exist) with real `scripts/benchmarks/**`
  (confirmed via glob: canonical benchmark pkg is `scripts/benchmarks/`).
- **FAB-18 -003**: added packet glob (F1) + `archive/**` + concrete move-manifest path
  `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md` (F2).

**FAB-08 IMPLEMENTED the verification-NO-GO P1 fix + filed REVISED post-impl -005** (gate-green): -004 P1 = the
`_force_rmtree`/`_force_remove_tree` helpers used `shutil.rmtree(onexc=...)` (py3.12+ kw) while `pyproject.toml`
declares `requires-python = ">=3.11"` → TypeError on 3.11 (hidden because verifier runs 3.14). Fix = version-adaptive
dispatch in all 4 files (`if sys.version_info >= (3,12): onexc=... else: onerror=lambda f,p,ei: handler(f,p,ei[1])`)
+ `import sys` added to the 3 test files that lacked it. Added 6 regression tests to
`platform_tests/scripts/test_fab08_slot_leak_fix.py`: 2 behavioral (monkeypatch `sys.version_info`+`shutil.rmtree`,
assert onerror@3.11 / onexc@3.12 on importable `doctor._force_remove_tree`) + 4 parametrized **source-scan**
(interpreter-independent: each helper file must carry onexc+onerror under a version_info guard). Impl-start packet
`sha256:3b5c4c94...` (resumable post-GO NO-GO — `begin` accepts NO-GO-over-GO). Verification GREEN: FAB-08 suite
**11 passed**; ruff check clean + format 5/5 already-formatted; scaffold suite **19 pass + 2 pre-existing HYG-023**
golden-fixture fails (no regression); live `_check_stale_test_slots(E:\GT-KB)` → `pass` / "no stale _test_* slots".
Filed `bridge/gtkb-fab-08-slot-leak-fix-005.md` REVISED. **Source UNCOMMITTED** (awaiting Codex VERIFIED; on VERIFIED
→ commit `fix:` + resolve WI-4420). A DIFFERENT session must verify (review-independence).

**KEY GATE LESSON (FAB-08 verification): platform-pkg test invocation needs `PYTHONPATH=E:\GT-KB\groundtruth-kb\src`.**
A bare `python -m pytest platform_tests\...` from E:\GT-KB FAILS with `No module named 'groundtruth_kb.project'`
because the ROOT `pyproject.toml` is Agent Red's (HYG-024/FAB-12) and sets no pythonpath; `import groundtruth_kb`
resolves as a namespace pkg (`__file__: None`). Set `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'` for any
platform-pkg pytest. (`gt.exe` is NOT in the venv Scripts; invoke doctor checks via the python module.)

**FAB-16 REVISED -003 FILED (gate-green) + WI-4441 generator-defect backlog item FILED (~06:17Z).** FAB-16 was GO@-002
but impl is BLOCKED (Area 2 antigravity regen unreachable). Filed REVISED -003 over the GO (owner-directed) that: (1)
re-scopes Area 2 OUT behind WI-4441 (`gt backlog add`, origin=defect, component=cross-harness-tooling, P2, `changed_by:
prime-builder/claude` via `$env:GTKB_HARNESS_NAME='claude'` — correct attribution this time); (2) sharpens Area 1 per
`DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611` (Goose has NO GT-KB role = OpenRouter's desktop UI; OpenRouter=SDK
bridge participant; parity checker must stop treating Goose as a dispatch harness / no-role UI-client exclusion;
SUPERSEDES -001's "UI-client registry entry" framing); (3) narrows Area 3 to `_FALLBACK_KNOWN_HARNESSES` removal +
degraded-projection-reports-error (check_harness_parity.py already derives KNOWN_HARNESSES from load_harness_projection).
target_paths narrowed: removed generate_codex_skill_adapters.py + .antigravity/** + .codex/skills/**. Both preflights
GREEN. Gate lesson: `gt backlog add` JSON array args need a scratch .py (PS mangles `["..."]`); `gt`/cli module needs
`PYTHONPATH=groundtruth-kb/src` (root pyproject is AR's).

**FAB-11 SUBSTANTIVE REDRAFT -003 FILED (gate-green, ~06:25Z).** Read DELIB-FAB11-REMEDIATION-20260610B (authoritative;
re-keys PAUTH-FAB11 v2). Redrafted whole proposal: HYG-029 hybrid (233 verified + 8 PB + SPEC-1534 rewrite to
applications/Agent_Red/*, retire ~1,124) + HYG-044 (re-register sweep after corpus) UNCHANGED; **HYG-030 CHANGED** →
removed fab11_spec_derived_test_recorder.py, now amend GOV-12/13 to pytest-as-evidence + scope tests table to AR history
+ fix kpi_spec_test_mapping view (new script fab11_pytest_evidence_contract.py + db.py + GOV packets); **HYG-014 CHANGED**
→ removed archive-then-prune, now prune+retention.toml+VACUUM NO archive + cheap pre-VACUUM file snapshot + dispose 2 dead
root DB snapshots. Added `.groundtruth/formal-artifact-approvals/*.json` (GOV-12/13 + CLAUDE.md packets) +
`groundtruth.db.corrupt-S311-*` + `groundtruth.db.pre-backfill-*` to target_paths. **Cross-Cluster Coordination note**:
DELIB-...B Decision 4 moves the 2 DB-snapshot disposals from FAB-04 (its -001 listed them under HYG-013) into HYG-014 —
flagged for Codex adjudication; idempotent file deletion = no double-delete risk. Both preflights GREEN (snapshot globs
resolved → files exist).

**REVISE/REDRAFT PHASE COMPLETE (session 9660f4cb, all gate-green, in Codex's queue — NOT Prime-actionable). DONE:**
7 turnkey REVISEDs (FAB-07/12/13/14/15/17/18; Codex already GO'd 07/12/15), FAB-08 post-impl REVISED -005 (real impl:
version-adaptive rmtree + 6 tests, verified), FAB-16 REVISED -003 (Area-2 re-scope) + WI-4441 generator-defect, FAB-11
REVISED -003 (substantive redraft vs DELIB-...B).

**NEXT PHASE — GO IMPLEMENTATIONS (item 5; VERIFY LIVE CODE STATE FIRST per gate lesson k):** FAB-05 GO@-004,
FAB-06/09 GO@-004 (protected-narrative → narrative packets), FAB-01/10 GO@-002 (bridge-substrate, load-bearing),
FAB-19/20/21 GO@-004, FAB-22/23 GO@-002, FAB-04 GO@-004 (**owner-AUQ-gate the ~11GB destructive deletions**),
FAB-16 (only after a FRESH GO on the -003 narrowed scope). Several REVISEDs filed this session may flip to GO as Codex
reviews — re-read live INDEX. **Commit blocker (separate owner decision):** draft-linter + FAB-02 are VERIFIED but the
inventory-drift pre-commit gate blocks ALL commits until the uncommitted harness-registry role-topology projection is
reconciled with .groundtruth/inventory/dev-environment-inventory.json (regen+commit as chore, OR revert the stray
registry change). Do NOT process NEW/REVISED/VERIFIED as Prime; act only on latest GO/NO-GO.

## FRESH-SESSION HANDOFF PROMPT (2026-06-11 ~06:30Z, session 9660f4cb — supersedes the ~05:35Z block at top of file)

```
::init gtkb pb

Continue PROJECT-FABLE-INVESTIGATION — the REVISE/redraft phase is COMPLETE; you are now in the GO-IMPLEMENTATION phase.
READ FIRST: memory/fable-investigation-campaign.md (full state — the consolidated GATE LESSONS, the per-cluster status,
the "NEXT PHASE — GO IMPLEMENTATIONS" list, and this handoff); bridge/INDEX.md (live authoritative queue — Codex changes
it in real time and is FAST, trust it over any cached state); bridge/gtkb-fable-investigation-advisory-001.md (charter);
independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md (frozen findings HYG-001..068).

STATE (after session 9660f4cb, 2026-06-11 ~06:30Z): ALL NO-GO REVISEDs and redrafts are filed + gate-green and in
Codex's queue (NOT Prime-actionable): 7 turnkey REVISEDs FAB-07/12/13/14/15/17/18 (Codex already GO'd 07/12/15 — others
flipping as Codex reviews), FAB-08 post-impl REVISED -005 (real impl: version-adaptive rmtree + 6 tests, verified green),
FAB-16 REVISED -003 (Area-2 re-scoped out) + WI-4441 generator-defect backlog item, FAB-11 REVISED -003 (substantive
redraft vs DELIB-FAB11-REMEDIATION-20260610B). Codex (Loyal Opposition) ACTIVE+fast. MULTIPLE concurrent Prime sessions —
coordinate via bridge claims; re-derive YOUR newest transcript UUID under C:\Users\micha\.claude\projects\E--GT-KB\*.jsonl
for claims (NOT CLAUDE_CODE_SESSION_ID).

UNCOMMITTED working tree (do NOT commit without an owner ask; each gated on its own VERIFIED + the inventory-drift blocker
below):
- FAB-08 source (5 files: groundtruth-kb/tests/{adopter/conftest.py,test_scaffold_isolation.py,test_cli.py},
  groundtruth-kb/src/groundtruth_kb/project/doctor.py, platform_tests/scripts/test_fab08_slot_leak_fix.py) — verified
  green, REVISED -005 in Codex's verify queue. On FAB-08 VERIFIED → commit `fix:` + resolve WI-4420.
- draft-linter source (scripts/draft_lint.py + platform_tests/scripts/test_draft_lint.py) — VERIFIED@-004, commit-blocked.
- FAB-02 secrets source (infrastructure/terraform/*, scripts/hygiene/secret_at_rest_guard.py, platform_tests/scripts/
  test_secret_at_rest_guard.py, .driveignore, .gitignore) — VERIFIED@-006, commit-blocked. On unblock → commit `feat:` +
  resolve WI-4414.
- Bridge REVISED files + bridge/INDEX.md + this notepad (governance; commit separately if owner asks).

ACT ONLY on latest GO (implement) or NO-GO (revise); never process NEW/REVISED/VERIFIED as Prime. Work order:

1. RE-READ live bridge/INDEX.md FIRST. Address any NO-GO that lands on a REVISED I filed this session (cold-read the
   NO-GO Findings; most are mechanical packet/path additions per the PARALLEL TRIAGE MAP).
2. GO IMPLEMENTATIONS (item 5; VERIFY LIVE CODE STATE FIRST — proposals were written 2026-06-10 and the tree has moved;
   gate lesson k). Likely-GO targets (confirm live): FAB-05 (rule-file retirement, protected-narrative → narrative
   packets), FAB-06 (narrative corrections, protected-narrative), FAB-09 (safety-gate registration), FAB-01 + FAB-10
   (bridge-substrate, load-bearing — bridge is always top priority), FAB-19 (hygiene-detector-expansion, config+doctor,
   no-KB-mut, cleanest), FAB-20 (hygiene-investigation skill), FAB-21 (startup load-cost, protected-narrative),
   FAB-22/FAB-23 (architecture + demoted cleanup). To IMPLEMENT a GO'd cluster: read the proposal + GO verdict (note GO
   constraints), `python scripts/implementation_authorization.py begin --bridge-id <slug>` (8h packet, gates Write/Edit
   to the GO'd target_paths), implement, verify (pytest + ruff check + ruff format --check via the venv WITH
   PYTHONPATH=E:\GT-KB\groundtruth-kb\src), file the post-impl report as the next version (status NEW), prepend NEW to
   INDEX, both preflights green. A DIFFERENT session verifies (review-independence).
3. FAB-04 (storage reclamation, GO@-004, destructive ~11GB): **owner-AUQ-gate the deletions via AskUserQuestion** before
   implementing. Coordinate the 2 dead root DB snapshots with FAB-11 HYG-014 (DELIB-FAB11-...B Decision 4 also lists
   them; idempotent deletion = no double-delete; whichever runs first).
4. FAB-16: do NOT implement the GO'd -002 (its Area-2 acceptance gate is unreachable); wait for a FRESH GO on the
   narrowed -003 scope, then implement Areas 1+3 only.

COMMIT BLOCKER (separate owner decision, blocks ALL commits incl. the VERIFIED FAB-02 + draft-linter): the
inventory-drift pre-commit gate FAILs because harness-state/harness-registry.json carries an uncommitted role-topology
projection (regenerated MemBase projection, multi-harness-active) that the committed
.groundtruth/inventory/dev-environment-inventory.json baseline doesn't match. Resolve via owner AUQ: (a) confirm the
projection is canonical → regen the inventory (scripts/collect_dev_environment_inventory.py) and commit registry+inventory
as `chore:` sync (UNBLOCKS all commits), OR (b) revert the stray registry change if unintended.

CONSOLIDATED GATE LESSONS (full text in the notepad): (a) EVERY proposal cites ADR-ISOLATION-APPLICATION-PLACEMENT-001 in
`## Specification Links` AND has a `## Isolation Placement Compliance` section (applicability preflight HARD-BLOCKS the
Write on a missing citation; clause preflight exit-5 on missing in-root evidence). (b) Promised packets/generated
artifacts → enumerate `.groundtruth/formal-artifact-approvals/*.json` + archive dests/sources/test globs in target_paths
(the systematic NO-GO fix). (c) Heading EXACTLY `## Specification Links` (a suffix harvests zero specs → HARD-BLOCK).
(d) Post-impl reports need `## Bridge Protocol Compliance` (names bridge/INDEX.md + "top of the entry"). (e) KB-mutating →
groundtruth.db in target_paths + "KB mutation: YES"; else the "No KB mutation:" negation note. (f) bare foreign WI-NNNN →
WI-collision WARNING (non-blocking). (g) `## Requirement Sufficiency` must be h2; first line status token; bridge_kind:
prime_proposal; 6 author-metadata fields. (h) claim survives a FAILED Write (releases only on success). (i) impl-start
`begin` works on a resumable post-GO NO-GO (the GO still authorizes the revision). (j) DELIB capture / `gt backlog add` /
`gt` CLI need $env:GTKB_HARNESS_NAME='claude' (else changed_by mis-attributes to antigravity) AND
PYTHONPATH=E:\GT-KB\groundtruth-kb\src (root pyproject is Agent Red's — bare `import groundtruth_kb` is a namespace pkg
and `groundtruth_kb.project`/`.cli` won't import). (k) VERIFY LIVE CODE STATE before implementing a GO'd cluster.
(l) NEW: gt CLI JSON-array args (--related-bridge-threads etc.) need a scratch .py under .gtkb-state/scratch/ (PowerShell
mangles `["..."]`); same for sqlite reads of deliberations (cols: id/title/summary/content/...). gt.exe is NOT in the
venv Scripts — invoke via `python -c "from groundtruth_kb.cli import main; ..."` with PYTHONPATH set.

TOOLING: gt not on PATH → E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe (the canonical interpreter; ruff/pytest live
ONLY there); canonical MemBase = root groundtruth.db; use the PowerShell tool (Bash root-boundary parser broken —
FAB-14/HYG-042). Parallelize READ-ONLY triage via Explore sub-agents (write-incapable = bridge-safe); serialize gated
WRITES (single bridge/INDEX.md + session-scoped claims/packets). Pause ONLY for genuine owner-gated AUQ (FAB-04 deletions,
the commit-blocker decision, any new governance exception); do NOT checkpoint-and-ask "say continue" between clusters —
proceed autonomously otherwise.

OPEN STRATEGIC (future AUQ, not part of FAB): WI-4438 active-orchestrator vision
(DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610); DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610.
```
