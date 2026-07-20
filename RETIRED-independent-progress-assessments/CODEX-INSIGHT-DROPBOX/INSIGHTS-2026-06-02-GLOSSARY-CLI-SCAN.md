# Glossary And CLI Scan - Loyal Opposition

Prepared: 2026-06-02
Prepared by: Codex Loyal Opposition
Scope: Codex/Claude bridge logs, harness hook/config surfaces, startup/bootstrap artifacts

## Claim

GroundTruth-KB still pays recurring cost for three related problems:

1. Live authority is too hard to resolve quickly.
2. Several bridge/process concepts used repeatedly in practice are still not first-class glossary or CLI concepts.
3. Startup/bootstrap remains heavier and less symmetric than it needs to be, especially for Codex.

These defects show up as stale-root confusion, repeated bridge churn, repeated reconciliation work, and large token/cache consumption in automated Claude bridge runs.

## Highest-Priority Findings

### 1. Historical live-authority confusion was real, repeated, and expensive.

- Evidence:
  - Older Codex bridge outputs repeatedly wrote and verified against `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\bridge\INDEX.md` instead of the current GT-KB root, for example:
    - `independent-progress-assessments/bridge-automation/logs/codex-20260411T145509Z.last-message.md`
    - `independent-progress-assessments/bridge-automation/logs/codex-20260412T173709Z.last-message.md`
    - `independent-progress-assessments/bridge-automation/logs/codex-20260413T020710Z.last-message.md`
  - The current project contract explicitly forbids treating `E:\Claude-Playground` as a live GT-KB surface in `AGENTS.md` and the project-root-boundary rule.
- Risk / impact:
  - Wrong-root reviews invalidate bridge evidence, create false verification, and force corrective audits later.
  - This is not just wording drift; it is source-of-truth drift.
- Recommended action:
  - Add a deterministic authority-resolution CLI that answers "where is the live authority for X?" before review/verification work starts.
  - Add doctor coverage for forbidden legacy-root references in active bridge/runtime artifacts.
- Decision needed from owner:
  - Whether the legacy-root detector should hard-fail `gt project doctor` or start as warn-only.

### 2. Bridge queue truth is still too easy to misread; chain reconciliation work is happening too often.

- Evidence:
  - Recent Codex bridge work repeatedly had to reconcile missing or misindexed bridge chains:
    - `independent-progress-assessments/bridge-automation/logs/codex-20260425T055134Z.last-message.md`
    - `independent-progress-assessments/bridge-automation/logs/codex-20260425T055734Z.last-message.md`
    - `independent-progress-assessments/bridge-automation/logs/codex-20260425T060334Z.last-message.md`
    - `independent-progress-assessments/bridge-automation/logs/codex-20260425T061534Z.last-message.md`
  - Claude logs describe the same issue from the other side: stale or missing `INDEX.md` coordination causes duplicate or late work.
    - `independent-progress-assessments/bridge-automation/logs/claude-20260425T060335Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260425T054835Z.stdout.log`
- Risk / impact:
  - Humans and harnesses keep re-deriving "operative review file", "retained chain", and "latest authoritative status" instead of querying a deterministic surface.
  - Every reconciliation round burns review cycles and increases duplicate-write race risk.
- Recommended action:
  - Add a bridge-chain status/reconciliation CLI that reports:
    - indexed latest status
    - on-disk latest file
    - missing versions
    - misordered status lines
    - stale parking/retirement markers
  - Make that CLI the canonical preflight for bridge scans and post-implementation verification.
- Decision needed from owner:
  - Whether chain mismatch should block only automation, or also interactive bridge edits.

### 3. Important practical process terms are repeated in logs but absent from the canonical glossary.

- Evidence:
  - The canonical glossary already covers `work subject` and canonical init keywords in `.claude/rules/canonical-terminology.md:972-993` and `:1218`.
  - The scan found no glossary matches for recurring operational terms used in bridge work:
    - `umbrella proposal`
    - `capped-spawn`
    - `parking marker`
    - `slug-mute`
    - `retained chain`
    - `provenance comment`
    - `dispatchable` / `non-dispatchable`
  - These terms recur in Claude bridge logs, for example:
    - `independent-progress-assessments/bridge-automation/logs/claude-20260416T221235Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260418T185135Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260418T191235Z.stdout.log`
- Risk / impact:
  - The harnesses are using stable concepts that the glossary does not formally define.
  - That increases prompt length because each session re-explains them.
- Recommended action:
  - Expand the glossary with short operator definitions for the terms above, especially where they map to deterministic behavior.
  - Prefer terms that can back future CLI nouns/verbs.
- Decision needed from owner:
  - Whether `parking marker` should remain a transitional convention or be superseded by a formal protocol status.

### 4. Deferral / parked-thread handling is not first-class, so automation churn persists.

- Evidence:
  - Claude explicitly describes a "parking-marker pattern" as an ad-hoc sixth status outside the five formal bridge statuses:
    - `independent-progress-assessments/bridge-automation/logs/claude-20260418T185135Z.stdout.log`
  - The same family of logs shows repeated no-op fires on parked work:
    - `independent-progress-assessments/bridge-automation/logs/claude-20260418T184835Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260418T185435Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260418T192435Z.stdout.log`
- Risk / impact:
  - The system spends real model budget re-proving that nothing changed.
  - Parking behavior currently lives in comments and precedent, not in a deterministic protocol surface.
- Recommended action:
  - Prioritize native deferred/parked semantics in bridge protocol and scanners.
  - Add slug-level mute/defer controls with explicit owner-authority semantics.
- Decision needed from owner:
  - Which formal status vocabulary should survive long-term: `DEFERRED`, `PARKED`, or a different owner-approved term.

### 5. Startup/bootstrap is functional but heavier and more asymmetric than the current workflow justifies.

- Evidence:
  - The intended bootstrap contract says startup should be "one short startup file" and deterministic: `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md:3`.
  - Both harnesses run `single_harness_bridge_automation.py --ensure` on SessionStart and `--ensure --dispatch-now` on Stop:
    - `.codex/hooks.json:14`, `.codex/hooks.json:279`
    - `.claude/settings.json:61`, `.claude/settings.json:158`
  - Both harnesses also run distinct near-duplicate `session_start_dispatch.py` implementations with 50-second startup-service timeouts:
    - `.codex/gtkb-hooks/session_start_dispatch.py:36`
    - `.claude/hooks/session_start_dispatch.py:42`
  - Claude has live prompt-submit protections that Codex does not mirror:
    - `.claude/settings.json:179`, `:184`
    - Codex prompt-submit surface in `.codex/hooks.json` lacks `owner-decision-tracker` and `bridge-axis-2-surface`.
  - Cached startup artifacts are large:
    - `.codex/gtkb-hooks/last-user-visible-startup-lo.md` = 16,607 bytes
    - `.claude/hooks/last-user-visible-startup-lo.md` = 17,811 bytes
  - Automated Claude bridge runs show very large cache reads/creation, for example:
    - `independent-progress-assessments/bridge-automation/logs/claude-20260425T061235Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260425T060335Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260425T054835Z.stdout.log`
- Risk / impact:
  - Large startup context becomes normalized even for narrow bridge tasks.
  - Codex/Claude parity remains partly document-level rather than mechanism-level.
- Recommended action:
  - Move from large rendered startup payloads toward a compact structured payload plus on-demand expansions.
  - Collapse duplicate session-start dispatch logic into one shared implementation with harness adapters only at the edge.
  - Decide which protections must be true parity features versus accepted harness differences.
- Decision needed from owner:
  - Whether startup optimization should target token/cost reduction first, parity closure first, or both in one project.

### 6. Harness readiness failures are still log-visible but not exposed through one deterministic health surface.

- Evidence:
  - Claude bridge automation logs contain repeated authentication/rate-limit failures:
    - `independent-progress-assessments/bridge-automation/logs/claude-20260414T163350Z.stdout.log`
    - `independent-progress-assessments/bridge-automation/logs/claude-20260505T162301Z.stdout.log`
  - Codex previously found `gt project doctor` insufficient as a bridge-readiness verifier:
    - `independent-progress-assessments/bridge-automation/logs/codex-20260415T231535Z.last-message.md`
- Risk / impact:
  - Operator time is wasted discovering auth/readiness by failure.
  - Doctor surfaces are not yet the one place to ask "can this harness actually perform bridge work right now?"
- Recommended action:
  - Extend readiness/doctor commands to expose:
    - harness auth state
    - bridge root/path authority
    - required bridge artifacts present
    - known muted/deferred threads
    - scanner/parser vocabulary compatibility
- Decision needed from owner:
  - Whether auth-state checks should remain redacted boolean readiness only, or include richer operator hints.

## Recommended Precedence

The order below follows dependency logic rather than convenience:

1. Formalize deferred/parked bridge semantics and authority-resolution surfaces.
2. Add bridge-chain/doctor/readiness CLIs on top of those semantics.
3. Expand the glossary to match the now-formalized process surfaces.
4. Reduce startup/bootstrap payload and close parity gaps using the new deterministic surfaces instead of prose.

Reason: glossary cleanup without deterministic authority/readiness surfaces will only document existing friction; bootstrap reduction without reliable bridge/authority CLIs risks removing context before replacement surfaces exist.

## Recommended Backlog Additions

### Project 1 - Authority Surface And Bridge Deferral Formalization

- Why this project should exist:
  - It addresses the highest-cost ambiguity first: live authority, parked work, and bridge latest-state resolution.
- Suggested work-items:
  - Add `gt authority resolve <subject>` / equivalent CLI for live source-of-truth lookup.
  - Add native bridge `DEFERRED` or `PARKED` status with scanner support.
  - Add slug-level mute/defer mechanism with explicit owner-authority semantics.
  - Add legacy-root detector for forbidden active references to `E:\Claude-Playground`.
- Owner grilling topics before approval:
  - Hard-fail vs warn-only for legacy-root detections.
  - Preferred formal parked-status vocabulary.
  - Whether slug mute is owner-only forever or delegable with evidence.

### Project 2 - Bridge Determinism And Readiness CLI

- Why this project should exist:
  - The logs show repeated human/model effort spent reconstructing chain state and harness readiness.
- Suggested work-items:
  - Add `gt bridge status` / equivalent chain-reconciliation report.
  - Add `gt bridge doctor` or extend `gt project doctor` with bridge-readiness checks.
  - Add checks for indexed/on-disk chain mismatches, missing versions, and stale status ordering.
  - Add readiness checks for harness auth/rate-limit state in a redacted operator-safe form.
- Owner grilling topics before approval:
  - Whether doctor failures should block automation only or all bridge work.
  - Whether auth/readiness should be polled proactively or only on demand.

### Project 3 - Glossary And Process-Term Discoverability

- Why this project should exist:
  - The harnesses now use stable process language not captured in the canonical glossary.
- Suggested work-items:
  - Add glossary entries for `umbrella proposal`, `sub-stream proposal`, `capped-spawn`, `parking marker`, `slug-mute`, `retained chain`, `provenance comment`, `dispatchable work`, `non-dispatchable work`.
  - Add a lightweight term-discovery CLI or command surface for glossary lookup.
  - Add "authoritative surface for this term" cross-links from glossary to CLI/docs/rules.
- Owner grilling topics before approval:
  - Whether glossary entries should stay minimal operator definitions or include protocol examples.
  - Whether term lookup belongs in `gt` CLI or only in docs.

### Project 4 - Startup Payload Reduction And Harness Parity Closure

- Why this project should exist:
  - Current startup remains large, duplicated, and only partially parity-driven.
- Suggested work-items:
  - Replace large pre-rendered startup markdown payloads with compact structured startup metadata plus demand-loaded detail.
  - Collapse the two `session_start_dispatch.py` implementations into one shared module.
  - Review Codex-vs-Claude hook parity for `owner-decision-tracker` and `bridge-axis-2-surface`.
  - Reassess duplicated bridge-automation ensure/dispatch hooks across SessionStart and Stop.
- Owner grilling topics before approval:
  - Whether startup minimization may reduce owner-visible richness in exchange for lower cost.
  - Whether parity closure should prefer adding Codex hooks or explicitly ratifying accepted differences.

## Suggested Individual Work-Item Candidates

- WI candidate: `gt authority resolve` live-source lookup.
- WI candidate: bridge native deferred/parked status.
- WI candidate: slug-level mute/defer directive with audit trail.
- WI candidate: bridge chain reconciler CLI.
- WI candidate: `gt project doctor` bridge/auth/root-boundary expansion.
- WI candidate: legacy-root reference scanner for active artifacts.
- WI candidate: glossary expansion for missing bridge/process nouns.
- WI candidate: glossary-to-authority cross-link surface.
- WI candidate: shared session-start dispatcher implementation.
- WI candidate: structured startup payload with lazy detail expansion.
- WI candidate: Codex/Claude prompt-submit parity review for owner-decision and bridge-axis surfaces.

## Recommended Approval Sequence

Approve projects in this order:

1. Project 1 - Authority Surface And Bridge Deferral Formalization
2. Project 2 - Bridge Determinism And Readiness CLI
3. Project 3 - Glossary And Process-Term Discoverability
4. Project 4 - Startup Payload Reduction And Harness Parity Closure

## Decision Needed From Owner

Use the report as the grilling packet for one-project-at-a-time approval.

The first project to take through owner approval should be Project 1, because the later CLI, glossary, and bootstrap changes depend on having a formal answer for:

- live authority lookup
- parked/deferred bridge semantics
- legacy-root detection policy

