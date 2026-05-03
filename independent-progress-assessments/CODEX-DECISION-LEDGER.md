# Codex Decision Ledger - GroundTruth-KB

Purpose: persistent record of owner decisions and standing operating choices that materially affect Codex review behavior.

## Usage Rules

- Record only durable decisions that future sessions should honor.
- Prefer one entry per decision.
- Include source, impact, and whether the decision is still active.

## Entries

### 2026-05-02 - Canonical terminology loads at startup for both roles

- source:
  Owner directive in session on 2026-05-02.
- decision:
  `.claude/rules/canonical-terminology.md` must be included in the session
  start procedure for both Loyal Opposition and Prime Builder roles.
- impact:
  Future Prime Builder and Loyal Opposition sessions should load the live
  canonical glossary before ordinary role work, not rely only on pasted
  startup text, cached summaries, or the operating-model excerpt.
- status:
  Active

### 2026-05-02 - Bare question mark requests status update

- source:
  Owner directive in session on 2026-05-02.
- decision:
  A question mark as input, with no other accompanying text, (`?`) should be
  interpreted as a request for an update on Codex's current and recent
  activity.
- impact:
  Future Codex sessions should answer a bare `?` with concise status: what
  Codex is doing now, what it recently did, whether anything is running or
  blocked, and what input or next step is needed if idle. Codex should not
  treat a bare `?` as an invalid or non-actionable prompt.
- status:
  Active

### 2026-05-03 - Status updates must refresh bridge and sub-agent state

- source:
  Owner directive in session on 2026-05-03.
- decision:
  When Codex provides a status update, including in response to a bare `?`,
  Codex must first load and examine the live `bridge/INDEX.md` and examine the
  state of all active sub-agents.
- impact:
  Status updates should report current bridge state from the authoritative
  index, not cached summaries or earlier reads. If no sub-agents are active,
  say so. If sub-agents are active, include their current state and whether
  their work affects the next step.
- status:
  Active

### 2026-05-03 - Loyal Opposition proceeds directly on actionable bridge items

- source:
  Owner directive in session on 2026-05-03.
- decision:
  If Loyal Opposition is aware of a bridge item that needs LO attention, it
  should proceed directly without asking for owner input.
- impact:
  Latest `NEW` or `REVISED` bridge entries are sufficient authorization for
  Loyal Opposition review/verification work. Codex should read the live
  `bridge/INDEX.md`, process the actionable item under the file bridge
  protocol, and only stop for owner input when a necessary owner decision
  blocks the review itself.
- status:
  Active

### 2026-04-29 - AI-driven work prefers tracked surfaces for load-bearing change

- source:
  Owner clarification in session on 2026-04-29.
- decision:
  GT-KB work should use per-surface versioning and named tracked surfaces
  rather than a monolithic or implicit-control model, especially for
  functioning subsystems and load-bearing components. Human-development
  heuristics often minimize controlled surfaces because documentation and
  tracking cost human time and attention. AI-driven development has the
  opposite dominant cost: untracked surfaces create drift, lost memory, and
  re-derived conventions across sessions. The default bias is therefore toward
  modularity, explicit change control, and durable tracking unless the
  per-surface ratchet cost exceeds the drift risk.
- impact:
  Future reviews should challenge "simplifying" changes that reduce named or
  versioned surfaces without a clear evolutionary benefit. Small work items
  that promote informal patterns into tracked artifacts can have higher
  leverage than their visible scope suggests because they reduce future drift
  exposure. Load-bearing helpers, command surfaces, bridge behavior,
  governance flows, and recurring agent workflows should default toward
  explicit tracked surfaces, machine-checkable invariants, and per-surface
  versioning.
- status:
  Active

### 2026-04-28 - GT-KB host supports one active developed application

- source:
  Owner clarification in session on 2026-04-28.
- decision:
  GT-KB and applications built using it are isolated for lifecycle reasons:
  the GT-KB platform must be able to evolve independently of applications and
  release on its own cadence. A GT-KB host directory supports only one active
  developed application at a time; it is not expected to host concurrent
  application-development work.
- impact:
  Future isolation, packaging, installer, bridge, and review proposals should
  treat `applications/` as an application slot and lifecycle boundary, not as a
  concurrent multi-application workspace. Findings should reject designs that add
  unnecessary multi-app orchestration inside one GT-KB host unless Mike later
  changes this constraint.
- status:
  Active

### 2026-03-25 - Codex primary role is review and investigation

- source:
  Owner request in session on 2026-03-25.
- decision:
  Codex's primary role in this project is:
  1. reviews of proposals and code
  2. investigations of alternatives and solutions to technical challenges or decisions
- impact:
  Analysis-first behavior is the default expectation for Codex sessions in this repo.
  Implementation should not be assumed unless explicitly requested.
- status:
  Active

### 2026-03-25 - Review-mode artifacts adopted

- source:
  Owner approval to implement the Codex review configuration proposal.
- decision:
  The project adopts dedicated Codex review artifacts:
  - `CODEX-REVIEW-OPERATING-CONTRACT.md`
  - `CODEX-REVIEW-CHECKLISTS.md`
  - `CODEX-DEAD-ENDS-AND-FALSE-POSITIVES.md`
  - `TEMPLATE-CODE-REVIEW.md`
  - `TEMPLATE-DECISION-MEMO.md`
- impact:
  Future review and investigation work should use these artifacts as the default operating scaffold.
- status:
  Active

### 2026-03-28 - Extensibility investigation is the next prepared design track

- source:
  Owner request to summarize the proposed agent-extensibility model and send it to Prime for evaluation and implementation planning.
- decision:
  The next prepared investigation track is the `agent extensibility` design:
  - distinguish `skills` from `peer agents`
  - evaluate tenant-scoped custom MCP as per-agent skills
  - evaluate direct team-member access to peer agents through Chat UI
  - have Prime prepare an implementation proposal for later Codex review
- impact:
  A fresh Codex session should be ready to immediately resume this design track without rediscovering the recent S227 Tier 3/4 review history.
- status:
  Active

### 2026-04-01 - Widget functionality is a hard deployment gate

- source:
  Owner directive in session on 2026-04-01 during S251 closeout.
- decision:
  A deployment is a failure if the chat widget is non-functional in the target environment.
  The only exception is an explicit owner approval to deploy with the widget disabled.
- impact:
  Future review and release verdicts must treat widget failures as blockers or rollback-required conditions, not advisory defects.
- status:
  Active

### 2026-04-01 - GroundTruth distribution contract is GitHub-installable, not PyPI-required

- source:
  Owner clarification in session on 2026-04-01 after the GroundTruth closeout checkpoint.
- decision:
  `groundtruth-kb` should be a versioned Python package installable directly from GitHub by outside users.
  PyPI publication is not required at this time.
- impact:
  Packaging audits and implementation proposals must distinguish:
  1. GitHub-installable package
  2. release-artifact installable package
  3. PyPI-published package
  and must not assume PyPI as the contract unless the owner later says so explicitly.
- status:
  Active

### 2026-04-01 - Non-disruptive deployment operating model adopted

- source:
  Owner agreement with the operating-model findings and Prime response `9fa11da0` on 2026-04-01.
- decision:
  The accepted release model is:
  1. `release_pipeline.py` is the canonical production GO/NO-GO path
  2. widget, chat, auth, tenant-routing, and config changes are `Class C`
  3. `Class C` promotion requires live widget proof
  4. widget failure means promotion blocked or rollback required
- impact:
  Future release and verification proposals should be reviewed against the OM Wave 1-3 program, not against older smoke-only deployment assumptions.
- status:
  Active

### 2026-04-01 - Artifact immutability and lane separation are prerequisites for trustworthy hotfixes

- source:
  Owner agreement on spec request `ad40ba38` and the hotfix/WIP separation specs on 2026-04-01.
- decision:
  Urgent fixes must ultimately be supported by three explicit separations:
  1. code lane separation (`git worktree` or equivalent clean hotfix lane from the deployed SHA)
  2. environment lane separation (`integration-staging` vs `release-staging`)
  3. artifact lane separation (manifest-based build-once, promote-the-same-artifact release flow)
- impact:
  OM Wave 2/3 proposals should treat immutable artifact promotion and staging-lane separation as prerequisites, not optional polish.
- status:
  Active

### 2026-04-09 - Bridge implementation ownership is reversed from the default relationship

- source:
  Owner clarification in session on 2026-04-09.
- decision:
  For bridge runtime, protocol, poller, worker, and handshake work, Codex is the implementation owner and Prime Builder is the reviewer.
- impact:
  Future bridge sessions should not wait for Prime-authored implementation proposals. Codex should inspect, correct, implement, verify, and then send Prime an implementation report or targeted review request.
- status:
  Active

### 2026-04-09 - Bridge protocol is asynchronous, not transactional

- source:
  Owner clarification in session on 2026-04-09.
- decision:
  The bridge should be treated as asynchronous message passing rather than transactional request/reply. Not all messages are replies, not all messages require replies, and retries should be reserved for important requests.
- impact:
  Future bridge reviews, diagnostics, and implementations should avoid reasoning from "pending outbound" to "the peer is waiting" unless an important request or deadline explicitly makes that true.
- status:
  Active

### 2026-04-21 - Owner input is requested one item at a time

- source:
  Owner request in session on 2026-04-21 to make owner-input prompts durable
  across future sessions.
- decision:
  When owner input is required, Codex must present one decision, question,
  approval, credential action, or manual action at a time. The request must use
  a visually distinct `OWNER ACTION REQUIRED` Markdown block that describes the
  current decision/question, why it matters, practical options, and the expected
  reply shape. The block must be the only substantive user-facing content in
  that response. Codex must stop after the block and wait for Mike's answer; it
  must not continue with other work, progress updates, summaries, or unrelated
  evidence because that can push the request out of the visible chat area.
  Additional owner inputs should be queued internally for later instead of
  being displayed or asked all at once. A necessary owner decision is one that
  blocks work Mike has requested; optional preferences, nice-to-have direction,
  and non-blocking status choices are not necessary decisions unless they block
  the requested work.
- impact:
  Future sessions should avoid bundled owner-question lists and should make the
  single currently requested owner response immediately visible in chat. Prime
  Builder and Loyal Opposition must both pause at owner-input gates unless Mike
  explicitly authorizes parallel work.
- status:
  Active

### 2026-04-21 - Startup focus menu is Prime Builder-only

- source:
  Owner directive in session on 2026-04-21.
- decision:
  The GT-KB numbered "Choose This Session's Focus" startup menu is presented to
  the owner only by Prime Builder. Loyal Opposition does not present the
  numbered focus options.
- impact:
  Prime Builder startup can continue to offer owner-facing release, staging,
  production, and backlog focus choices. Loyal Opposition startup must instead
  begin prepared to review and verify Prime Builder work.
- status:
  Active

### 2026-04-21 - Loyal Opposition startup begins with bridge verification

- source:
  Owner directive in session on 2026-04-21.
- decision:
  When Loyal Opposition starts a fresh session, its first task is to verify that
  the Prime Builder / Loyal Opposition bridge is functioning. If the bridge is
  not functioning, Loyal Opposition must diagnose and repair it before ordinary
  review work.
- impact:
  Loyal Opposition has owner pre-approval to make any file and configuration
  changes required to restore bridge function. Bridge restoration outranks
  ordinary review startup when the bridge is broken.
- status:
  Active

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
