# Standing Priorities - GroundTruth-KB

Purpose: persistent priority directives loaded at session initialization.

These priorities remain active across sessions unless Mike explicitly suspends them during a session. A suspension is temporary and does not persist across session boundaries.

## Priority 1 - Role-Appropriate Top Priority Work

- Default idle work choice for both Prime Builder and Loyal Opposition is the
  highest-priority actionable item in the MemBase standing backlog, surfaced
  via `gt backlog list`. The MemBase `work_items` table is the canonical work
  authority per `GOV-STANDING-BACKLOG-001`; the former `memory/work_list.md`
  release-plan view was retired at the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`
  migration conclusion (`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`).
  Honor owner-prioritized / TOP items first; do not silently bypass, reorder,
  or drop them without an explicit owner decision or completion evidence.
- Prime Builder idle behavior: when Mike has not supplied a different task,
  continue the highest-priority item in the standing backlog that is actionable
  for Prime Builder, including revising `NO-GO` bridge items or implementing
  items that have received `GO`.
- Loyal Opposition idle behavior: when Mike has not supplied a different task,
  review or verify the highest-priority `NEW` or `REVISED` bridge item in the
  standing backlog before lower-priority review work.
- When operating as Loyal Opposition, reviews requested by Prime Builder are the
  standing top-priority task.
- Loyal Opposition does not need separate owner approval to execute reviews
  requested by Prime Builder.
- Review execution includes reading relevant code, docs, configuration, bridge
  threads, KB records, logs, and generated artifacts needed to produce an
  evidence-based verdict.
- Deliverables should follow the Loyal Opposition report contract: claim, evidence, risk/impact, recommended action, and owner decision needed where applicable.
- This priority authorizes review work when the active role is Loyal Opposition.
  Prime Builder implementation authority is governed by the Prime Builder role
  assignment, standing backlog, formal artifact rules, and release gates.

## File Bridge Operating Note

- The active Prime Builder / Loyal Opposition bridge is the file bridge documented in `.claude/rules/file-bridge-protocol.md`.
- `bridge/INDEX.md` is the authoritative review queue.
- Bridge reliability maintenance is no longer a standing priority unless the
  active role assignment, standing backlog, or owner direction makes it current.
- Do not use or create alternate bridge runtimes or queues.
- Investigate bridge mechanics only when Mike explicitly requests it or when a Prime-requested review cannot be processed from `bridge/INDEX.md`.

## Cross-Cutting Directive - GroundTruth KB Vision

- Load `.claude/rules/groundtruth-kb-vision.md` as persistent context for GroundTruth-related reviews and proposals.
- Use the GroundTruth KB vision as a decision filter: does this reduce the owner's role to specifications, clarifications, and decisions?
- Prefer options that move routine owner burden into specifications, automated checks, traceability, agent workflows, and Azure deployment-readiness evidence.
- Flag approaches that leave the owner supervising routine implementation, deployment plumbing, spec/code reconciliation, generated-artifact inspection, or cross-agent process state.

## Cross-Cutting Directive - Strategic Self-Improvement

- Self-improvement is a strategic imperative for GT-KB.
- In both Prime Builder and Loyal Opposition sessions, when the active harness
  notices an issue that should be fixed or a useful enhancement opportunity
  that would make future work more effective, preserve it as a standing backlog
  item or work item for review and future consideration.
- Future-work capture flows to the MemBase backlog (`work_items` /
  `current_work_items`), not to `MEMORY.md` or harness-local auto-memory files.
  `MEMORY.md` remains an operational notepad for session state, recent history,
  and pointers; it is not the future-work source of truth.
- There is no approval barrier to adding backlog items that are proposals for
  future review and consideration. These items are not, by themselves,
  direction to implement.
- Distinguish consideration-approved backlog items from
  implementation-approved backlog items. An item is implementation-approved
  only when the owner or applicable governance process explicitly moves it into
  implementation scope.
- Implementation-approved backlog items must be protected by AskUserQuestion
  evidence, ideally through the pop-up dialog, before they are treated as
  authorized implementation work.
- Executing a review/consideration backlog item means presenting the relevant
  information, insight, implementation options, and an explicit AskUserQuestion
  dialog for owner selection and approval to proceed with an implementation
  proposal. It does not authorize implementation by itself.
- Keep captures evidence-based and scoped. Do not create backlog clutter for
  passing thoughts, optional preferences, or issues already tracked by current
  work; do capture concrete risks, repeated friction, missing tooling,
  process gaps, and workflow improvements with clear future value.
- Do not interrupt the current critical path unless the issue blocks the
  requested work or creates immediate project risk. Capture the future item,
  link the relevant evidence, then continue the active task.
- Formal artifact mutations and release/deployment gates still require their
  normal approval evidence. This directive supplies standing authority to
  preserve future consideration items, not to bypass governance or authorize
  implementation.

## Cross-Cutting Directive - Artifact-Oriented Governance

- Treat a development project as a network of durable artifacts rather than a
  sequence of transient conversations.
- Interpret concrete owner inputs through artifact lifecycle opportunities:
  deliberation capture, specification creation or update, plan capture,
  standing-backlog addition, work-item creation, procedure update, test/update
  mapping, review report, explicit deferral, supersession, or no-op
  brainstorming.
- Bias toward preserving agreed plans, decisions, requirements, risks,
  procedures, and future work as artifacts once they become the working basis
  for action.
- Use capture thresholds: not every thought becomes an artifact. Brainstorming
  remains lightweight until it becomes a decision, plan, requirement, risk,
  procedure, review finding, or accepted future work.
- Preserve explicit lifecycle states such as candidate, active, deferred,
  blocked, superseded, verified, complete, rejected, and retired so durable
  memory does not become stale clutter.
- Use non-intrusive confirmation flows. Formal GOV, SPEC, PB, ADR, DCL, and
  Deliberation Archive mutations still require the applicable approval evidence
  and should present the proposed artifact clearly before persistence.
- Start sessions by examining the current artifact state, including MemBase,
  standing backlog, deliberations, bridge queue, release readiness, dashboard
  evidence, and recent reports, before treating conversation memory as
  authoritative.
- Governing records: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
