# Bridge Proposal: gtkb-backlog-hygiene-bundle-s349 (REVISED @ 009)

**Topic:** Bundled capture of 12 backlog-hygiene findings from S349 foundational use-case diagnostic exercise.
**Bridge kind:** prime_builder_implementation_proposal
**Session:** S349
**Owner-approval mode:** AskUserQuestion (13 AUQ exchanges; one workflow-sequencing AUQ plus 12 per-finding AUQs)
**Revision history:** REVISED from -001 NEW after Codex NO-GO at -002 (F1: machine-readable target_paths metadata missing). REVISED again from -003 GO at -004 after implementation-start gate revealed has_spec_derived_verification() heading-allowlist mismatch. REVISED from -005 NO-GO at -006 to remove stale bridge-version references in the Implementation Plan and replace residual 'Test Plan' prose with 'Verification Plan'. REVISED again from -007 NO-GO at -008 to remove the last remaining stale '-004.md' reference in the Files Expected To Change explanatory paragraph (Codex F1).

target_paths: ["groundtruth.db", "bridge/INDEX.md"]

## Summary

In S349, the owner asked Prime Builder to report on the current state of the backlog, then framed a diagnostic follow-up: "Was it difficult to identify the term 'backlog', find the resource, or understand the information?" The diagnostic question was explicitly intended to surface sources of error or drift when handling foundational use cases. The owner then instructed Prime Builder to propose natural-language specifications for any identified improvements, use AskUserQuestion for approvals, and on approval create projects (or work items attached to existing in-flight projects) and add them to the backlog.

The diagnostic exercise produced 12 distinct findings, each presented to the owner as a natural-language specification with proposed disposition, and each approved via a single 3-4-option AskUserQuestion. This proposal captures all 12 as governed backlog items: 10 new work items under existing projects, plus 2 new projects (each with one initial work item from the corresponding finding).

Per CLAUDE.md's strategic self-improvement directive, "Backlog capture is not implementation approval; implementation-approved backlog items require AskUserQuestion evidence." This bundle performs the capture step; each finding's substantive remediation work will follow its own future bridge cycle. No source code, configuration, hook, or rule-file mutations are authorized by this proposal.

## Items to Create

| # | Finding | Disposition | Priority | Origin | Component |
|---|---|---|---|---|---|
| 1 | Priority taxonomy drift in `work_items.priority` (P0/P1/P2/P3 + low/medium/LOW/MEDIUM + None coexisting) | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH | P1 | hygiene | backlog |
| 2 | Startup-disclosure backlog/work-item counts do not match live `gt backlog list` totals; filter rules undisclosed | WI under PROJECT-GTKB-STARTUP-ENHANCEMENTS | P2 | hygiene | startup |
| 3 | `resolution_status` and `stage` are two undocumented parallel status axes; legal combination matrix undefined | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH | P2 | hygiene | backlog |
| 4 | 13+ P1+ work items lack `project_name`; intake path permits silent orphan creation | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH | P1 | hygiene | backlog |
| 5 | 38 AGENT-RED-TEST-COVERAGE-GAPS items commingled with GT-KB platform backlog despite Agent Red being a separate project | WI under PROJECT-GTKB-ISOLATION | P2 | hygiene | backlog |
| 6 | `gt` CLI shim not on PATH on this Windows install; no doctor check detects the silent-drift case | WI under PROJECT-GTKB-GOVERNANCE-ADOPTION | P2 | hygiene | groundtruth-kb |
| 7 | CLAUDE.md and rule files reference legacy paths (e.g., `tools/knowledge-db/db.py`) when canonical surface is `groundtruth-kb/src/groundtruth_kb/` | NEW PROJECT GTKB-RULE-FILE-CURRENCY-AUDIT-001 + initial WI | P2 | hygiene | governance |
| 8 | Three production `groundtruth.db` files in the repo (root, `groundtruth-kb/`, `tools/knowledge-db/`); only root is canonical | WI under PROJECT-GTKB-ISOLATION | P2 | hygiene | groundtruth-kb |
| 9 | GT-KB CLI emits cp1252 on Windows PowerShell; non-ASCII content (Greek letters in DA summaries) crashes `UnicodeEncodeError` mid-emit | WI under PROJECT-GTKB-GOVERNANCE-ADOPTION | P2 | hygiene | groundtruth-kb |
| 10 | `implementation-start-gate` PreToolUse:Bash hook over-blocks read-only commands (e.g., `grep`/`cat`/`echo` pipelines) explicitly listed as exempt in codex-review-gate.md | NEW PROJECT GTKB-IMPLEMENTATION-START-GATE-HARDENING-001 + initial WI | P1 | defect | governance |
| 11 | 113 projects in `active` status, 0 retired; project-retirement flow is not being invoked when projects logically conclude | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH | P2 | hygiene | backlog |
| 12 | 23 work_items have `id` matching an existing project record's name (e.g., `GTKB-GOV-PROPOSAL-STANDARDS`, `GTKB-STARTUP-ENHANCEMENTS`); cross-table identifier collision | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH | P2 | hygiene | backlog |

## Specification Links

- GOV-STANDING-BACKLOG-001 — MemBase work_items is the canonical backlog authority; this proposal creates rows in that table per the governance contract.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority; this proposal honors the NEW/REVISED/GO/NO-GO/VERIFIED lifecycle for work-item-creation operations.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposals must cite every relevant governing specification; this section satisfies that requirement.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification must derive from linked specs; the Verification Plan section maps each linked spec to a verification step.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — application/root placement; relevant to Finding 5 (AGENT-RED-* commingling) and Finding 8 (multiple groundtruth.db files).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — concrete owner decisions, requirements, and future work shall be preserved as durable artifacts; this proposal preserves 12 owner-decision-backed work items.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — development changes preserve traceability; each work item carries the AUQ-evidence citation.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle states include candidate/active/deferred/blocked/superseded/verified/retired; the work items are captured at `open/backlogged` (candidate-for-implementation).
- DCL-CONCEPT-ON-CONTACT-001 — touching a load-bearing concept triggers glossary promotion; this proposal does not promote new concepts but references existing canonical glossary entries.
- .claude/rules/canonical-terminology.md — canonical glossary defining backlog, work item, project, sub-project, application, platform, specification.
- .claude/rules/operating-model.md §2 — canonical operating-model definitions for backlog/work_item/project taxonomy.
- .claude/rules/codex-review-gate.md — work-item creation requires bridge proposal with GO before execution; this proposal is the gate's intake.
- .claude/rules/file-bridge-protocol.md — proposal/review/verification protocol; this proposal's structure conforms.
- .claude/rules/project-root-boundary.md — GT-KB project root and applications/ boundary; relevant to Findings 5 and 8.
- .claude/rules/prime-builder-role.md — Prime Builder authority; the Strategic Self-Improvement Directive cited in CLAUDE.md authorizes proactive backlog capture of noticed fix-worthy issues.
- CLAUDE.md Strategic Self-Improvement Directive — "capture noticed fix-worthy issues and useful workflow enhancements as review/consideration backlog items in MemBase, not MEMORY.md; backlog capture is not implementation approval; implementation-approved backlog items require AskUserQuestion evidence."
- GOV-06 (Specify on contact) — relevant to Finding 7 (touched rule files acquire stale-reference governance).
- GOV-08 (KB is truth) — relevant to Finding 8 (multiple DB files violates the single-source-of-truth principle).
- GOV-09 (Owner input classification) — the owner's S349 specification language triggered spec-first workflow; this proposal is that workflow's output.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive AI plumbing is a defect; several findings propose doctor checks that move repetitive validation into mechanical services.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION — project authorizations are owner-approval evidence for bounded project scope; this proposal does not request authorization but acknowledges the surface.
- SPEC-AUQ-POLICY-ENGINE-001 — AskUserQuestion is the canonical owner-decision channel; the 13 AUQ exchanges in the Owner Decisions / Input section are the load-bearing evidence.
- DELIB-S324-PB-INTERROGATION-DIRECTIVE — Prime Builder interrogative default for owner factual claims; the diagnostic question that produced these findings was an instance of that posture.

## Prior Deliberations

<!-- Helper pre-populates this section from the canonical glossary and semantic search. -->


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1916` — seed=search; bridge_thread; Bridge thread: gtkb-codex-backlog-cleanup-retroactive-review (6 versions, VERIFI
- DA: `DELIB-1839` — seed=search; bridge_thread; GTKB Phantom-INDEX + Stale-Snapshot Cleanup Review
- DA: `DELIB-1473` — seed=search; lo_review; Loyal Opposition Advisory: LO Hygiene Assessment Skill
- DA: `DELIB-1633` — seed=search; bridge_thread; Loyal Opposition Review - Governance Hygiene Bundle
- DA: `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — seed=search; owner_conversation; S327 owner directive: formalize standing backlog as DB-backed source-of-truth

## Owner Decisions / Input

This proposal is owner-authorized via 13 AskUserQuestion exchanges in S349. Each AUQ presented the natural-language specification with proposed disposition; the owner selected one of 3-4 mutually-exclusive options. All approvals were single-option selections; none required revision.

| # | AUQ Header | Owner Selection | Authorizes |
|---|---|---|---|
| 0 | Workflow sequencing | "AUQ each immediately, no preview" | The 12-AUQ pass that produced this bundle |
| 1 | Finding 1 (priority taxonomy drift) | "Approve as drafted" | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH at P1/hygiene/backlog |
| 2 | Finding 2 (startup disclosure backlog-number fidelity) | "Approve as drafted" | WI under PROJECT-GTKB-STARTUP-ENHANCEMENTS at P2/hygiene/startup |
| 3 | Finding 3 (resolution_status vs stage schema clarification) | "Approve as drafted" | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH at P2/hygiene/backlog |
| 4 | Finding 4 (orphan work-item enforcement + triage) | "Approve as drafted" | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH at P1/hygiene/backlog |
| 5 | Finding 5 (AGENT-RED-* commingling) | "Approve as drafted" | WI under PROJECT-GTKB-ISOLATION at P2/hygiene/backlog |
| 6 | Finding 6 (gt CLI PATH detection) | "Approve as drafted" | WI under PROJECT-GTKB-GOVERNANCE-ADOPTION at P2/hygiene/groundtruth-kb |
| 7 | Finding 7 (rule-file currency audit) | "Approve as new project" | New PROJECT-GTKB-RULE-FILE-CURRENCY-AUDIT-001 + initial WI at P2/hygiene/governance |
| 8 | Finding 8 (multiple groundtruth.db files) | "Approve as drafted" | WI under PROJECT-GTKB-ISOLATION at P2/hygiene/groundtruth-kb |
| 9 | Finding 9 (CLI UTF-8 stdout hardening) | "Approve as drafted" | WI under PROJECT-GTKB-GOVERNANCE-ADOPTION at P2/hygiene/groundtruth-kb |
| 10 | Finding 10 (implementation-start-gate over-blocking) | "Approve as new project" | New PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001 + initial WI at P1/defect/governance |
| 11 | Finding 11 (project-retirement flow gap) | "Approve as drafted" | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH at P2/hygiene/backlog |
| 12 | Finding 12 (work_item-id vs project-name collisions) | "Approve as drafted" | WI under PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH at P2/hygiene/backlog |

Per the AUQ-only enforcement stack (SPEC-AUQ-POLICY-ENGINE-001), AUQ-recorded owner decisions are the canonical owner-decision channel. No prose-decision-ask was used during S349.

## Clause Scope Clarification (Not a Bulk Operation)

The bulk-ops clause `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may fire on the content patterns in this proposal ("standing backlog", "work item") because of the multi-item scope. This proposal is NOT a bulk operation in the clause's sense (the clause guards against "bulk work_item state transitions"): it does not transition existing work_items between states. It creates 12 new work_items + 2 new projects, each authorized by an explicit per-finding AUQ approval, with the per-finding inventory captured in the "Items to Create" table and the per-finding owner approval captured in the "Owner Decisions / Input" table. The formal-artifact-approval-equivalent evidence is the per-finding AUQ exchange (`detected_via: ask_user_question`); no MemBase APPROVAL or specification mutation is performed by this proposal.

## Target Paths

- `groundtruth.db` (canonical MemBase at E:\GT-KB\groundtruth.db) — 12 new `work_items` rows and 2 new `projects` rows, plus the version-history rows that append-only versioning produces.
- `bridge/INDEX.md` — append `Document:` + `NEW:` entries for this bridge thread (managed automatically by the bridge-propose helper).

No source code, configuration, hook, or rule-file mutations are authorized by this proposal. No work outside `E:\GT-KB\` is performed.

## Requirement Sufficiency

Existing requirements sufficient.

The 12 proposed work items are each natural-language specifications of FUTURE remediation work. Each future implementation will require its own scoping bridge proposal and Codex review cycle. This proposal does not require new owner-stated requirements at capture time. The natural-language specification text in each finding's row IS the work_item's `description` field; subsequent requirement work (deciding value-transition mappings for Finding 1's priority migration, scoping slices for Finding 10's hook hardening, etc.) is deferred to each finding's future implementation bridge.

The current proposal's requirement set is the conjunction of: (a) the strategic self-improvement directive's "capture noticed fix-worthy issues as review/consideration backlog items in MemBase"; (b) the AUQ-only enforcement stack's requirement that owner approval is recorded via AskUserQuestion; (c) the canonical glossary's definitions of backlog/work_item/project. All three are satisfied by the data in this proposal.

## Verification Plan

Post-implementation verification is row-existence verification, not behavioral testing. Each linked specification maps to a verification step that confirms the capture operation completed correctly.

| Linked specification | Verification step |
|---|---|
| GOV-STANDING-BACKLOG-001 (MemBase is the canonical backlog) | `python -m groundtruth_kb backlog list --json` returns 134 rows (122 pre-impl + 12 new) with `priority`, `origin`, `component`, `project_name`, `title`, `description` matching the Item Details section. |
| GOV-FILE-BRIDGE-AUTHORITY-001 (bridge protocol authority) | This proposal received `GO` at `-002.md` (or the bridge thread's appropriate verdict file) and the implementation report is filed as the next versioned entry. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (spec linkage) | The applicability preflight `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-hygiene-bundle-s349` returns `preflight_passed: true` with `missing_required_specs: []`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (derived testing) | This Verification Plan table maps each linked spec to a step; the implementation report includes the actual command outputs proving each row landed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (application placement) | The implementation operates only on `E:\GT-KB\groundtruth.db` and `bridge/INDEX.md`; no out-of-root paths are touched. The implementation report includes the `gt config` output proving the canonical DB path. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (durable artifacts) | All 12 owner decisions are durably captured as work_items (visible via `gt backlog list`) and durably linked to AUQ evidence through the `Owner Decisions / Input` section of this proposal (preserved in the bridge file). |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (traceability) | Each work_item's `change_reason` field will cite this bridge document path and the corresponding finding number. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lifecycle states) | All 12 new work_items will be captured at `resolution_status=open, stage=backlogged` — the canonical "candidate-for-implementation" state per the lifecycle catalog. The two new projects will be captured at `status=active`. |
| .claude/rules/canonical-terminology.md (glossary) | Each work_item uses canonical terms per the glossary (work_item, project, backlog, etc.); no novel terms are introduced by this proposal. |
| .claude/rules/operating-model.md §2 (taxonomy) | Each work_item's `project_name` references either an existing project or one of the two new projects created by this proposal; no orphan work_items are introduced. |
| .claude/rules/codex-review-gate.md (bridge GO required) | This proposal IS the bridge GO request; Codex GO at the next version is the gate. |
| .claude/rules/file-bridge-protocol.md (protocol conformance) | This proposal contains all required sections per the bridge-compliance-gate hook; the hook passing the Write is itself evidence. |
| .claude/rules/project-root-boundary.md (in-root only) | All target paths are within `E:\GT-KB\`. |
| CLAUDE.md self-improvement directive | The 12 work_items are captured in MemBase, not in MEMORY.md or auto-memory; capture is not implementation. |
| GOV-06/GOV-08/GOV-09 | Findings 7, 8, and 9 each cite the relevant governance principle in their natural-language spec. |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | Findings 1, 3, 6, 9, 10, 11, 12 each propose a doctor check or write-boundary rejection as the deterministic-services manifestation. |
| SPEC-AUQ-POLICY-ENGINE-001 | The Owner Decisions / Input table cites the AUQ-only enforcement evidence; no prose-decision-ask was used. |

Spec-to-test mapping: each linked specification's relevance is to the *capture operation*, not to the substantive content of any finding. The verification plan verifies the capture; substantive verification of each finding's remediation is deferred to each future implementation bridge.

## Risks and Rollback

- **Risk: incorrect parent-project attachment for any item.** Mitigation: AUQ approval explicit per item; Items to Create table is review-checkable against the AUQ transcript. Rollback: append `superseded_by` version pointer; insert corrected row.
- **Risk: new-project IDs collide with existing projects.** Mitigation: both new project IDs (`GTKB-RULE-FILE-CURRENCY-AUDIT-001`, `GTKB-IMPLEMENTATION-START-GATE-HARDENING-001`) were verified non-colliding against `gt projects list --json` at S349-time (no existing project bears either name or ID).
- **Risk: scope creep into implementation.** Mitigation: each natural-language spec describes FUTURE work; this proposal captures only. No source code, configuration, hook, or rule-file changes are authorized.
- **Risk: per Finding 10, the `implementation-start-gate` hook may block this proposal's implementation phase.** Mitigation: this proposal's only mutations are to `groundtruth.db` (governed via the `gt` CLI invoking the MemBase Python API, not Bash) and to `bridge/INDEX.md` (governed via the bridge-propose helper or the Write/Edit tools). The bash-bound implementation-start-gate hook does not fire on these paths. If the hook unexpectedly fires, the implementation phase will fall back to direct Python invocation of the `groundtruth_kb` API.
- **Risk: scanner-safe-writer credential scan rejects the proposal.** Mitigation: the proposal body contains no credential-shaped text; the helper's own pre-flight scan is consulted. If a residual false-positive occurs, the helper's `mode=redact` path normalizes the spans without losing semantic content.
- **Risk: append-only versioning produces a long history row chain.** Mitigation: this is the intended invariant of MemBase versioning; no rollback is needed for the version chain itself.

## Files Expected To Change

- `groundtruth.db`
- `bridge/INDEX.md`

The `groundtruth.db` mutation is governed via the Python API (`groundtruth_kb.db.KnowledgeDB.insert_work_item()` for work_items) and the `gt` CLI (`gt projects create` for new projects, `gt projects add-item` for membership links). All operations are append-only versioned per MemBase invariants. The `bridge/INDEX.md` mutation is the post-implementation `NEW` line for the next unused implementation-report file on this thread and any subsequent verdict lines.

No source code, configuration, hook, rule-file, scaffold, or out-of-root path is touched.

## Implementation Plan

After Codex GO on this proposal's next revision (the verdict file that approves the latest REVISED on this bridge thread):

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-backlog-hygiene-bundle-s349` to obtain the session-local implementation-start authorization packet. The script extracts the `target_paths: [...]` metadata line (added at the top of this revision) and `## Files Expected To Change` bullets above.
2. Create the 2 new project records via `python -m groundtruth_kb projects create <NAME> --id <PROJECT-ID> --purpose <text> --scope-note <text> --changed-by prime-builder/s349-bundle --change-reason <citation>`. One invocation per project.
3. Create the 12 new work_items via the Python API `groundtruth_kb.db.KnowledgeDB.insert_work_item(...)` directly (the CLI does not yet expose `gt backlog add`; `gt projects add-item` only links existing work_items to projects per `python -m groundtruth_kb projects add-item --help`). Each invocation supplies `id` (WI-3282..WI-3293), `title`, `origin`, `component`, `resolution_status="open"`, `stage="backlogged"`, `priority`, `description`, `project_name`, `changed_by`, `change_reason`, and `related_bridge_threads="gtkb-backlog-hygiene-bundle-s349"`.
4. Link each new work_item to its parent project via `python -m groundtruth_kb projects add-item <PROJECT-ID> <WORK-ITEM-ID> --source "S349 bundle (gtkb-backlog-hygiene-bundle-s349)" --changed-by prime-builder/s349-bundle --change-reason <citation>`. One invocation per work_item.
5. Run the post-impl verification commands listed in the Verification Plan section; paste exact outputs into the implementation report.
6. File the post-implementation report as the next unused bridge version on this thread (do NOT reuse any existing version number; consult the live `bridge/INDEX.md` chain to pick the next free `-NNN.md` number) and add a `NEW` line at the top of the bridge thread's INDEX entry.
7. Recommended commit type: `chore` - this is governed metadata capture, not new functionality.

## Item Details

Each item below carries the natural-language specification text from its corresponding S349 AUQ. The text is the work_item's `description` field at insertion.

### Finding 1 — Priority taxonomy drift

**Target:** New work_item under `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`. Priority P1. Origin `hygiene`. Component `backlog`. Title: "Reconcile MemBase work_items.priority field to single canonical vocabulary."

**Natural-language specification (description field):**

The MemBase `work_items.priority` field shall use a single canonical priority vocabulary: `P0`, `P1`, `P2`, `P3`, plus one explicit token for unprioritized items (e.g., `UNRANKED`). A one-time reconciliation migration shall map every existing row's priority value into the canonical vocabulary using owner-approved mappings (`low`/`LOW` -> ?; `medium`/`MEDIUM` -> ?; `None` -> `UNRANKED` or assigned). After migration, `gt backlog add` and the Python API shall reject non-canonical priority values at the write boundary. `gt backlog list` and any future ranking surface shall sort by a single priority key. A doctor check shall fail if any non-canonical priority value appears in MemBase.

Evidence at S349-time: 4 priority value families coexist in 122 live items: modern (`P0`/`P1`/`P2`/`P3`, 27 items), legacy lowercase (`low`/`medium`, 50 items), legacy uppercase (`LOW`/`MEDIUM`, 3 items), and None (42 items). The specific value mappings are owner decisions deferred to the implementation phase.

### Finding 2 — Startup-disclosure backlog-number fidelity

**Target:** New work_item under `PROJECT-GTKB-STARTUP-ENHANCEMENTS`. Priority P2. Origin `hygiene`. Component `startup`. Title: "Startup-disclosure backlog counts shall use a single documented filter rule."

**Natural-language specification:**

The startup-disclosure backlog/work-item counts shall reflect a single, documented filter rule, or equal the live `gt backlog list --json` totals. The "Current Project State" section shall define each counter explicitly: what filter produces "active backlog items"; what scope/status combination "open MemBase work items" represents; and whether "non-terminal item(s)" in the project rollup is a separate counter or a synonym. The startup payload shall expose the filter rule in machine-readable form (e.g., a `counter_definitions` block) so the disclosure is self-documenting. If a counter is filtered, the filter rule shall appear adjacent to the number; if a counter is intended to match live state, it must equal the live query result at generation time.

Evidence at S349-time: the cached startup disclosure rendered at session start reported "GT-KB active backlog items: 1", "GT-KB open MemBase work items: 3", and "121 non-terminal item(s)" in the project rollup, while live `gt backlog list --json` returned 122 non-terminal items, 119 open. The numbers `1` and `3` are clearly a filtered view but the filter rule is not documented.

### Finding 3 — `resolution_status` vs `stage` schema clarification

**Target:** New work_item under `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`. Priority P2. Origin `hygiene`. Component `backlog`. Title: "Document and enforce the `(resolution_status, stage)` legal matrix in `work_items`."

**Natural-language specification:**

The MemBase `work_items.resolution_status` and `work_items.stage` fields shall each have a single documented purpose, recorded in `.claude/rules/canonical-terminology.md` and the operating model. The documentation shall define: (a) the canonical value domain for each field; (b) the legal matrix of combinations; (c) which field is authoritative for the question "is this item active work right now." If the two fields are intentionally orthogonal, the matrix shall list each legal pairing; if one field is redundant or stale, it shall be retired. A doctor check shall flag rows whose `(resolution_status, stage)` pair falls outside the documented legal matrix. Existing rows shall be reconciled to that matrix as part of the same work.

Evidence at S349-time: 1 `in_progress` item is `stage=implementing` (consistent), 1 `new` item is `stage=created` (consistent), but 11 `open` items are `stage=created` (apparently new-and-not-yet-prioritized). The 1 `deferred` item has no corresponding stage value. The semantic distinction may be intentional but is undocumented.

### Finding 4 — Orphan work-item enforcement + triage

**Target:** New work_item under `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`. Priority P1. Origin `hygiene`. Component `backlog`. Title: "Require explicit project assignment or `loose=true` flag at work_item creation; triage 13+ existing orphans."

**Natural-language specification:**

The MemBase `work_items` schema and intake paths shall not permit silent creation of work items without project assignment. Every work-item creation path (`gt projects add-item`, Python API, scaffold migrations, etc.) shall require either: (a) an existing `project_name` reference, or (b) an explicit `loose=true` flag with a written rationale captured in `status_detail` or a dedicated `loose_rationale` field. A doctor check shall flag any work item that lacks `project_name` and does not carry the explicit loose-flag evidence. The existing 13+ unparented P1+ items shall be triaged as part of the same work: each assigned to an appropriate existing project, or grouped into a new dedicated project, or flagged as `loose=true` with rationale.

Evidence at S349-time: 13 of 17 P1 items have `project_name=null`, including `WI-3275` (MCP Slice 1 REVISED post-impl), `WI-3279` (gt generate-approval-packet CLI), `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`.

### Finding 5 — AGENT-RED-* commingling with GT-KB MemBase

**Target:** New work_item under `PROJECT-GTKB-ISOLATION`. Priority P2. Origin `hygiene`. Component `backlog`. Title: "Re-home or retire AGENT-RED-* projects/work_items in GT-KB MemBase per project-root boundary."

**Natural-language specification:**

The MemBase `work_items` and `projects` tables in this `E:\GT-KB` checkout shall represent GT-KB platform work only. Application-specific work (Agent Red, other adopter applications) shall live in those applications' own MemBase or issue tracker, not in GT-KB MemBase. The current 38 items in `PROJECT-AGENT-RED-TEST-COVERAGE-GAPS` (and any other `AGENT-RED-*`-named projects in GT-KB MemBase) shall be reviewed and classified into one of two dispositions: (a) re-home to the Agent Red repository (issue tracker or that project's own MemBase) and retire from GT-KB MemBase with `change_reason` citing the project boundary; or (b) retain in GT-KB MemBase ONLY if the item represents GT-KB-as-platform adopter-conformance coverage per `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, and in that case re-project under an explicit GT-KB-side name (e.g., `GTKB-AGENT-RED-ADOPTER-CONFORMANCE-COVERAGE`). After the review, a doctor check shall flag any future GT-KB MemBase row whose `project_name` matches an external-application pattern (e.g., `AGENT-RED-*`) and lacks an explicit conformance-evidence flag.

Evidence at S349-time: 38 of 122 live non-terminal items (31% of GT-KB backlog) are in `AGENT-RED-TEST-COVERAGE-GAPS`. Inspection confirmed they reference Agent Red specs (`SPEC-1653`, `SPEC-1707`, `SPEC-1708`) about Agent Red features ("Marketing Campaign Information MCP Server", "External AI Agent Conversation MCP Server").

### Finding 6 — `gt` CLI PATH detection + documented fallback

**Target:** New work_item under `PROJECT-GTKB-GOVERNANCE-ADOPTION`. Priority P2. Origin `hygiene`. Component `groundtruth-kb`. Title: "Detect `gt` CLI silent-drift on PATH; document `python -m groundtruth_kb` as canonical fallback."

**Natural-language specification:**

The GT-KB `gt` CLI shall be callable from the user's shell after a standard install. To prevent silent install drift, `gt project doctor` (or the `python -m groundtruth_kb project doctor` fallback) shall include a `_check_gt_cli_on_path` check that verifies `gt --version` runs from the current shell's PATH and emits a clear remediation hint when it does not (e.g., "run `pip install -e groundtruth-kb/`" or "activate the correct virtual environment"). CLAUDE.md and the relevant rule files shall document the canonical CLI invocation explicitly, with `python -m groundtruth_kb <command>` listed as the documented fallback when `gt` is not on PATH.

Evidence at S349-time: `gt --help` returned "command not found" in both bash and PowerShell on this Windows install; `groundtruth-kb/pyproject.toml:55` correctly declares `gt = "groundtruth_kb.cli:main"`, so the defect is install-time drift, not packaging.

### Finding 7 — Rule-file path/CLI currency audit (new project)

**Target:** NEW project `GTKB-RULE-FILE-CURRENCY-AUDIT-001`. Initial work_item at P2. Origin `hygiene`. Component `governance`. Title: "Audit and remediate stale path/CLI references in CLAUDE.md, AGENTS.md, and `.claude/rules/`."

**Natural-language specification:**

CLAUDE.md, AGENTS.md, and all files under `.claude/rules/` shall reference only canonical current paths and CLI invocations. References to legacy or stale paths (e.g., CLAUDE.md's "`tools/knowledge-db/db.py`" pointer when the canonical surface is `python -m groundtruth_kb` / the `gt` CLI in `groundtruth-kb/src/groundtruth_kb/`) shall be removed or updated. A doctor check shall scan the protected rule files for known-stale references and flag drift. The audit shall include: (a) Python module paths, (b) CLI command names and entry points, (c) file paths cited as authoritative, (d) database locations, (e) configuration file locations. The known-stale-reference catalog shall live under `config/governance/` and be owner-approved; it is the corpus the doctor check consults.

Evidence at S349-time: CLAUDE.md "Knowledge Database Access" section instructs "Always use the Python API (`tools/knowledge-db/db.py`)" while the canonical surface is `groundtruth-kb/src/groundtruth_kb/` (which also contains a separate `db.py`). Both files exist, creating ambiguity about which is authoritative.

### Finding 8 — Multiple `groundtruth.db` files

**Target:** New work_item under `PROJECT-GTKB-ISOLATION`. Priority P2. Origin `hygiene`. Component `groundtruth-kb`. Title: "Consolidate to single canonical `groundtruth.db`; classify or remove duplicates."

**Natural-language specification:**

The GT-KB repository shall contain exactly one canonical `groundtruth.db` file - the one resolved by `gt config` (currently `E:\GT-KB\groundtruth.db`). Any other `groundtruth.db` files in the repo shall be classified as one of: (a) test fixture (must live under a clearly-named fixtures directory such as `tests/fixtures/`), (b) historical archive (must be moved to `archive/<date>/` with a README documenting provenance and last-known-good schema version), or (c) accidental duplicate (must be removed). The `.gitignore` shall track only the canonical DB. A `_check_single_canonical_db` doctor check shall flag any `groundtruth.db` discovered outside (a), (b), or the canonical location (excluding pytest temp directories and worktrees). The current files `groundtruth-kb/groundtruth.db` and `tools/knowledge-db/groundtruth.db` shall be inspected, classified, and dispositioned as part of the same work.

Evidence at S349-time: three production `groundtruth.db` files exist in the repo (root, `groundtruth-kb/`, `tools/knowledge-db/`) plus worktree copies and pytest temp DBs. `gt config` confirms only the root file is canonical; the others have undocumented provenance.

### Finding 9 — CLI UTF-8 stdout hardening

**Target:** New work_item under `PROJECT-GTKB-GOVERNANCE-ADOPTION`. Priority P2. Origin `hygiene`. Component `groundtruth-kb`. Title: "GT-KB CLI shall emit UTF-8 regardless of host shell codepage; doctor check verifies non-ASCII emit."

**Natural-language specification:**

The GT-KB CLI (`gt` / `python -m groundtruth_kb`) shall emit UTF-8-encoded output regardless of the host shell's default codepage. At process startup the CLI shall reconfigure `sys.stdout` and `sys.stderr` to UTF-8 (e.g., `sys.stdout.reconfigure(encoding='utf-8')` on Python 3.7+) so that non-ASCII characters in MemBase fields do not crash output operations with `UnicodeEncodeError`. JSON export commands shall emit byte streams without a BOM. The doctor check shall verify CLI output handling by attempting to emit a known non-ASCII test string and reporting PASS/FAIL. Documentation shall note `$env:PYTHONIOENCODING="utf-8"` as a recommended PowerShell setup for ad-hoc Python invocations, but the GT-KB CLI itself shall not require it.

Evidence at S349-time: `gt deliberations search` crashed mid-emit with `UnicodeEncodeError: 'charmap' codec can't encode 'δ'` when a DA summary contained a Greek delta. `Out-File -Encoding utf8` on PowerShell wrote a UTF-8 BOM that Python's `json.load` rejected (required `utf-8-sig` codec).

### Finding 10 — Implementation-start-gate hook over-blocks read-only commands (new project)

**Target:** NEW project `GTKB-IMPLEMENTATION-START-GATE-HARDENING-001`. Initial work_item at P1. Origin `defect`. Component `governance`. Title: "Implementation-start-gate shall correctly classify read-only commands as exempt per codex-review-gate exception list."

**Natural-language specification:**

The `GTKB-IMPLEMENTATION-START-GATE` PreToolUse:Bash hook (`.claude/hooks/implementation-start-gate.py`) shall correctly classify read-only shell commands as exempt from the bridge-GO-authorization requirement, consistent with `.claude/rules/codex-review-gate.md` "What Does NOT Require a Bridge Proposal" exception list. The hook shall use execution-context-axis classification per `memory/feedback_security_parser_executing_wrapper_distinction.md`: executing wrappers (`bash -c`, `sh -c`, `eval`, `source`, `.`) are opaque and subject to the gate; data-substitution commands (`grep`, `cat`, `head`, `tail`, `echo`, `ls`, `find`, `which`, `where`, `git log`, `git status`, `git diff`, `git show`) and their composition through pipelines, control operators (`;`, `&&`, `||`), and stdout-only redirections are read-only and exempt. The classification shall be unit-tested with at least one fixture per read-only operation listed in the codex-review-gate exception list (asserting `allow`), and one fixture per opaque-executing-wrapper case (asserting `block` when bridge-GO authorization is absent).

Evidence at S349-time: a read-only command pipeline (`grep -l ...; echo ---; cat ... | grep ... | head`) was blocked by the implementation-start-gate hook with the message "BLOCKED (GTKB-IMPLEMENTATION-START-GATE): protected implementation mutation requires a live bridge GO authorization packet." The command had no write side-effects.

### Finding 11 — Project-retirement flow gap

**Target:** New work_item under `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`. Priority P2. Origin `hygiene`. Component `backlog`. Title: "Doctor check for stale-active projects; `kept_open_reason` field; session-wrap retirement prompt."

**Natural-language specification:**

The MemBase `projects` table shall reflect actual project lifecycle state. When a project's last non-terminal work item reaches terminal status AND no new work items are anticipated, the project record shall be retired via `gt projects retire`. A `_check_stale_projects` doctor check shall flag projects in `active` status that have had zero non-terminal work items for more than a configurable threshold (default 60 days) as candidates for retirement, surfacing them in a `gt projects show-stale` view. Projects intentionally kept open for anticipated future work shall record a `kept_open_reason` field with the rationale, exempting them from the staleness flag. Session-wrap procedures shall consult `gt projects show-stale` and prompt for retirement decisions.

Evidence at S349-time: `gt summary` reports 113 total projects, 113 active, 0 retired. Of 113 active projects, only 41 have non-terminal work items.

### Finding 12 — Work_item-id vs project-name collisions

**Target:** New work_item under `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`. Priority P2. Origin `hygiene`. Component `backlog`. Title: "Reject work_item-id / project-name collisions at write; triage 23 existing collisions."

**Natural-language specification:**

A work item's `id` field shall never duplicate the name or id of an existing project record in the `projects` table. The MemBase write API and `gt backlog add` / `gt projects create` shall reject any creation whose proposed identifier collides with an existing identifier in the parallel table. The current 23 collisions (e.g., `GTKB-GOV-PROPOSAL-STANDARDS`, `GTKB-STARTUP-ENHANCEMENTS`, `GTKB-WRAPUP-ENHANCEMENTS`) shall be inventoried and reconciled. Reconciliation options per row, decided by the owner during a triage pass: (a) migrate the work_item's substantive content into the project record's description/metadata and retire the work_item; (b) rename the work_item to a non-colliding `WI-NNNN` ID; or (c) merge into a more specific child work_item under the project. A `_check_artifact_id_collision` doctor check shall flag any future collision across MemBase tables.

Evidence at S349-time: 23 work_items have `id` matching the name of an existing project record - 19% of live backlog. The one `in_progress` item (`GTKB-GOV-PROPOSAL-STANDARDS`) exhibits the pattern.

## Bridge Lifecycle

REVISED @ 009. Addresses Codex NO-GO at -008 F1: removed the residual stale '-004.md' reference in the Files Expected To Change explanatory paragraph (the prior -007 lifecycle note had incorrectly claimed all '-004.md' references were gone; one remained in active scope text). Active scope text is now version-neutral, instructing Prime to use the next unused implementation-report file. Historical references to '-004.md' appear only in the revision-history line above and in this lifecycle note. No substantive scope change. Awaiting Codex re-review.
