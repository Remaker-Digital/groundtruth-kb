# GroundTruth Control-Surface Review

Date: 2026-03-30
Scope: recent Codex/Prime/bridge sessions as observed from the Agent Red workspace
Audience: owner and Prime Builder

## Claim

GroundTruth's recent collaboration stack is materially better than it was a week ago, but it still has six structural weaknesses that can cause drift, confusion, or silent process failure:

1. review mode is not actually non-mutating
2. startup reading order still conflicts with bridge SLA expectations
3. the live control plane is not portable from git alone
4. Codex review posture is still mixed with builder capabilities
5. Cursor is now archive-only in practice, but not fully retired in process docs
6. bridge storage/runtime topology is still too easy to misread, and contract-breaking outbound messages still occur

## Executive Recommendation

Treat this as a control-surface hardening pass, not a product-feature pass.

Recommended order:

1. make review mode truly non-mutating for the Knowledge DB
2. change startup process to `bridge sweep first, deeper reading second`
3. decide whether GroundTruth wants a tracked portable control bundle or an intentionally local-only one
4. split Codex review profile from builder profile
5. either retire Cursor formally or recreate a real live Cursor baseline
6. simplify bridge operator ergonomics around DB path and outbound validation

## Findings

### P1 - Review mode still mutates the append-only Knowledge DB

- claim:
  The documented review-mode goal of "no hidden state mutation" is contradicted by the actual session-start path, which still writes fresh assertion history and retains a delete-based pruning path.
- evidence:
  - [REVIEW-MODE-SETUP.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/REVIEW-MODE-SETUP.md#L5) through [REVIEW-MODE-SETUP.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/REVIEW-MODE-SETUP.md#L10) define review-mode goals as analysis-first, no hidden state mutation, evidence-heavy output, additive artifacts.
  - [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L65) through [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L103) always run assertions at session start.
  - [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L530) through [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L543) only skip pruning and handoff consumption in read-only review mode; they do not skip assertion execution itself.
  - [assertions.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/tools/knowledge-db/assertions.py#L229) through [assertions.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/tools/knowledge-db/assertions.py#L236) record every assertion run into the database.
  - [db.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/tools/knowledge-db/db.py#L2) through [db.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/tools/knowledge-db/db.py#L10) define the Knowledge DB as append-only, no UPDATE in place, no DELETE, never delete.
  - [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L477) through [assertion-check.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/hooks/assertion-check.py#L509) still include a `DELETE FROM assertion_runs` pruning routine when review mode is not active.
  - Direct DB evidence from `tools/knowledge-db/knowledge.db` during this review showed `assertion_runs=93842`, with fresh rows at `2026-03-30T05:22:29+00:00`, confirming current startup-time writes.
- risk/impact:
  This weakens the credibility of GroundTruth's own process model. A reviewer session is supposed to be low-mutation and auditable, but it currently writes operational history on startup and still carries a deletion path that contradicts the database contract.
- recommended action:
  Make review mode truly read-only for the Knowledge DB:
  1. do not execute `run_all_assertions()` in review mode
  2. do not compute/write quality-score artifacts in review mode if they persist state
  3. remove the pruning routine entirely, or move it behind an explicit admin-maintenance command with a documented policy change
- decision needed from owner:
  Yes. Confirm whether GroundTruth wants strict append-only semantics to remain authoritative, or whether the KB policy should be revised to permit maintenance deletes.

### P1 - Startup reading order still conflicts with bridge urgency requirements

- claim:
  The current startup working process still front-loads local reading, while the bridge protocol requires near-immediate acknowledgement and session-start sweeping. That conflict is already visible in the responsiveness history.
- evidence:
  - [AGENTS.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/AGENTS.md#L27) through [AGENTS.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/AGENTS.md#L36) require reading multiple startup documents before substantive work.
  - [prime-bridge-collaboration-protocol.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/rules/prime-bridge-collaboration-protocol.md#L36) through [prime-bridge-collaboration-protocol.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/rules/prime-bridge-collaboration-protocol.md#L39) require acknowledgement within 60 seconds.
  - [prime-bridge-collaboration-protocol.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/rules/prime-bridge-collaboration-protocol.md#L117) through [prime-bridge-collaboration-protocol.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/rules/prime-bridge-collaboration-protocol.md#L123) require an unresolved-message sweep plus risk-surface checks at session start.
  - [BRIDGE-RESPONSIVENESS-LEDGER.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/BRIDGE-RESPONSIVENESS-LEDGER.md#L26) through [BRIDGE-RESPONSIVENESS-LEDGER.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/BRIDGE-RESPONSIVENESS-LEDGER.md#L47) record repeated acknowledgement and cadence misses, including concrete `ack_breach` cases.
- risk/impact:
  GroundTruth can satisfy either "read everything first" or "ack bridge work within 60 seconds," but not both reliably. Without an explicit two-phase startup model, bridge responsiveness will remain dependent on operator discipline instead of process design.
- recommended action:
  Adopt a two-phase startup contract:
  1. phase A: bridge sweep, thread-risk check, immediate ack/claim/negotiate for live work
  2. phase B: full local bootstrap reading if no urgent bridge obligations remain
  Update both the runbook and the bridge rule so they no longer compete for first position.
- decision needed from owner:
  No product decision is needed, but the owner should confirm that bridge obligations outrank deep startup reading when both are present.

### P1 - The live control plane is not portable from git alone

- claim:
  The effective GroundTruth control surface still lives mostly outside tracked git state, so another machine or fresh checkout cannot reconstruct the real runtime with confidence.
- evidence:
  - [.gitignore](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.gitignore#L177) through [.gitignore](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.gitignore#L192) ignore both `.claude/` and `independent-progress-assessments/`.
  - [config/agent-control/README.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/README.md#L7) through [config/agent-control/README.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/README.md#L23) explicitly state that the tracked files are only a sanitized intent baseline, not the live local configuration.
  - `git ls-files 'config/agent-control' '.claude' 'AGENTS.md'` returned only `AGENTS.md`.
  - `git status --short --ignored 'independent-progress-assessments' '.claude' 'config/agent-control' 'AGENTS.md'` showed `?? config/agent-control/`, many `?? independent-progress-assessments/...`, and `!! .claude/`.
- risk/impact:
  This makes GroundTruth hard to reproduce, audit, or migrate. It also means recent role/rule/report improvements can silently remain local and never become part of a durable shared operating model.
- recommended action:
  Pick one portability model and enforce it:
  1. tracked sanitized control bundle in git, plus explicit local secrets/runtime exclusions
  2. or a consciously local-only control repo/export flow with an automated bootstrap command that recreates the local runtime from tracked intent
  The current hybrid is the worst of both models.
- decision needed from owner:
  Yes. Decide whether GroundTruth's operating configuration should be portable through git or intentionally local-only with explicit export/import tooling.

### P2 - Codex review posture is still mixed with builder capabilities

- claim:
  Codex's documented role is review-first, but the live tool/skill surface still exposes a mixed review-plus-builder profile.
- evidence:
  - [CODEX-WAY-OF-WORKING.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/CODEX-WAY-OF-WORKING.md#L5) through [CODEX-WAY-OF-WORKING.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/CODEX-WAY-OF-WORKING.md#L12) define review/investigation as the default mode.
  - [CONTROL-MAP.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/CONTROL-MAP.md#L19) through [CONTROL-MAP.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/config/agent-control/CONTROL-MAP.md#L25) say review skill intent currently lives in `proposal-review`, `code-review-audit`, and `alternatives-investigation`.
  - [settings.local.json](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/settings.local.json#L42) through [settings.local.json](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/settings.local.json#L58) still allow broad Python, npm, npx, and bridge mutation tools, plus [settings.local.json](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/settings.local.json#L89) through [settings.local.json](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/settings.local.json#L94) allow general web search/fetch.
  - [deploy/SKILL.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/skills/deploy/SKILL.md#L2) through [deploy/SKILL.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/skills/deploy/SKILL.md#L4) define a full deployment skill.
  - [run-tests/SKILL.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/skills/run-tests/SKILL.md#L2) through [run-tests/SKILL.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/skills/run-tests/SKILL.md#L4) define a test-execution skill.
- risk/impact:
  Mixed-role capability is manageable when the operator is careful, but it is not the same thing as a clean review profile. GroundTruth is still relying on discipline and runtime inference more than on hard separation of concerns.
- recommended action:
  Create explicit `review` and `builder` profiles:
  - review profile: review skills, read-heavy permissions, bridge tools, limited search
  - builder profile: deploy/test/build skills only when the owner explicitly switches modes
  If dual use is required in one workspace, make the active profile explicit in startup output.
- decision needed from owner:
  Yes. Decide whether GroundTruth wants one flexible profile with discipline, or two explicit role profiles with cleaner boundaries.

### P2 - Cursor is archive-only in practice, but not fully retired in process language

- claim:
  Cursor no longer has a live in-repo control surface, but GroundTruth still carries enough Cursor-era language to create role ambiguity.
- evidence:
  - `Test-Path '.cursor'` returned `False`.
  - `Test-Path '.cursor/rules'` returned `False`.
  - [CODEX-KNOWLEDGE-BASE-INDEX.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md#L29) through [CODEX-KNOWLEDGE-BASE-INDEX.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md#L36) explicitly move Cursor artifacts to `archive/cursor-legacy/`.
  - [CURSOR-KNOWLEDGE-BASE-INDEX.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/archive/cursor-legacy/CURSOR-KNOWLEDGE-BASE-INDEX.md#L13) through [CURSOR-KNOWLEDGE-BASE-INDEX.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/archive/cursor-legacy/CURSOR-KNOWLEDGE-BASE-INDEX.md#L24) describe the old live Cursor knowledge base and dropbox.
  - [LOYAL-OPPOSITION-LOG.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/LOYAL-OPPOSITION-LOG.md#L1) through [LOYAL-OPPOSITION-LOG.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/LOYAL-OPPOSITION-LOG.md#L5) still describe the log as "Cursor's appraisals, evaluations, and questions."
- risk/impact:
  If GroundTruth still intends Cursor to be a supported live actor, it currently has no canonical configuration. If it does not, the lingering live-language references increase confusion about ownership, authority, and expected session behavior.
- recommended action:
  Choose one:
  1. formally retire Cursor and relabel remaining live docs/logs as Codex/groundtruth-neutral
  2. or recreate a real live Cursor baseline with tracked prompts/rules/skills
  Do not keep the current in-between state.
- decision needed from owner:
  Yes. Is Cursor still a supported live runtime for GroundTruth, or should it be treated as historical-only?

### P2 - Bridge storage/runtime topology is still too easy to misread, and invalid sends still happen

- claim:
  The bridge works, but operator ergonomics are still weak: the live DB is in the user profile, an empty project-local shadow DB exists in `.claude/hooks/`, and contract-breaking outbound messages still occur in normal use.
- evidence:
  - [prime-bridge-sync/SKILL.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/skills/prime-bridge-sync/SKILL.md#L147) through [prime-bridge-sync/SKILL.md](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/.claude/skills/prime-bridge-sync/SKILL.md#L150) state the DB location is `~/.claude/prime-bridge/bridge.db`.
  - [prime_bridge_runtime.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/prime_bridge_runtime.py#L22) through [prime_bridge_runtime.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/prime_bridge_runtime.py#L28) use the same home-directory DB path by default.
  - Direct inspection showed `.claude/hooks/prime_bridge.db` exists in the repo but has no tables, while `C:\Users\micha\.claude\prime-bridge\bridge.db` contains `messages=743`, `notifications=2771`, `threads=134`.
  - The live home DB still contains a fresh invalid message from `2026-03-30T15:20:51.386225+00:00` with validation errors `missing expected_response`, `missing response_window`, `missing artifact_refs`, and `missing action_items`.
  - [prime_bridge_runtime.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/prime_bridge_runtime.py#L203) through [prime_bridge_runtime.py](/e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/prime_bridge_runtime.py#L237) validate the contract, but that validation still occurs only after the outbound send attempt reaches the runtime.
- risk/impact:
  This is not just cosmetic. It slows debugging, makes local inspection error-prone, and still allows bridge traffic that fails protocol validation in the middle of active work.
- recommended action:
  1. remove or clearly relabel the unused project-local `prime_bridge.db`
  2. add one canonical "active bridge DB path" note to the bridge health/debug workflow
  3. provide one project helper for outbound bridge sends that refuses to send if required fields are absent
  4. use that helper in review/report workflows instead of manual ad hoc send payloads
- decision needed from owner:
  No owner-only product decision is required, but Prime should decide whether this is fixed in runtime, helper tooling, or both.

## Suggested Remediation Sequence For Prime

### Tranche 1 - correctness and process integrity

1. make review mode truly non-mutating for the KB
2. remove the delete-pruning path or explicitly de-authorize the append-only claim
3. adopt `bridge sweep first` startup ordering

### Tranche 2 - portability and role clarity

1. choose tracked-vs-local control-plane strategy
2. split review and builder profiles for Codex
3. decide Cursor retirement vs. reactivation

### Tranche 3 - bridge ergonomics

1. remove shadow DB confusion
2. add outbound preflight helper
3. keep monitoring the responsiveness ledger until invalid-message and ack-breach recurrence both stay at zero

## Owner Decisions Needed

1. Should the Knowledge DB remain strictly append-only, with no delete-based maintenance path at all?
2. Should GroundTruth's operating control surfaces be portable through git, or intentionally local-only with explicit bootstrap tooling?
3. Is Cursor still a supported live runtime, or should GroundTruth treat it as historical-only?
4. Does the owner want explicit split profiles for Codex (`review` vs `builder`), or one mixed profile with policy discipline?

## Bottom Line

GroundTruth does not have a product-architecture crisis here. It has a control-plane integrity problem.

The fastest value is not another feature. It is making the collaboration and evidence system say exactly what it does, do exactly what it says, and travel cleanly from one machine/session to the next.
