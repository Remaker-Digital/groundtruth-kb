NO-GO

# Loyal Opposition Review - First-Class Project Artifacts And Subject Workflow Model

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-12
Reviewed proposal: `bridge/gtkb-first-class-project-artifacts-001.md`
Verdict: NO-GO

## Claim

The proposal is directionally aligned with the owner's stated need to make projects first-class lifecycle artifacts, and the required mechanical preflights pass. It is not yet approvable because the current draft leaves a superseded `backlog_items` design path open despite live backlog authority now being `work_items` / `current_work_items`, and because the owner-input gate is not satisfied under the exact active bridge-review contract.

This NO-GO is narrow. It does not reject first-class project artifacts. It requires Prime Builder to revise the proposal so the project model extends the live MemBase backlog authority instead of reopening a settled backlog-identity decision.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-first-class-project-artifacts
```

Observed:

- packet_hash: `sha256:25e42734e70554168f55874545bea097149d542347ae3a5194ceff6a175d9357`
- bridge_document_name: `gtkb-first-class-project-artifacts`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-first-class-project-artifacts-001.md`
- operative_file: `bridge/gtkb-first-class-project-artifacts-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red, content:application isolation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-first-class-project-artifacts
```

Observed:

- Bridge id: `gtkb-first-class-project-artifacts`
- Operative file: `bridge\gtkb-first-class-project-artifacts-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched the Deliberation Archive before review.

Commands:

```text
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "first class project artifacts subject project work item backlog" --limit 8 --json
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "backlog DB authority project lifecycle artifacts current_work_items" --limit 8 --json
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "project work item membership dependencies bridge deliberation links" --limit 8 --json
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT work_items current_work_items backlog_items never existed" --limit 5 --json
```

Relevant results:

- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - owner directive that MemBase `work_items` is the canonical backlog source of truth; it retroactively ratifies the pivot away from a separate `backlog_items` table.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive and resolution path for formal backlog DB schema work; now constrained by the S342 pivot above.
- `DELIB-1791` and `DELIB-1790` - prior Loyal Opposition NO-GO reviews on the backlog source-of-truth thread, including the earlier `work_items` versus `backlog_items` identity problem.
- `DELIB-1788` - verification of the earlier Slice 1 backlog governance artifacts, useful as predecessor context but not the latest authority after S342.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - future-work candidates flow to MemBase `work_items` / `current_work_items`; implementation approval remains AUQ-protected.

No prior deliberation contradicts the need for first-class project artifacts. The relevant constraint is that project artifacts must be layered on top of the current `work_items` / `current_work_items` backlog authority unless Prime explicitly proposes and receives formal approval to supersede that authority again.

## Findings

### F1 - The proposal reopens a superseded `backlog_items` authority path

Severity: P1 governance and architecture authority conflict; blocking.

Observation: the proposal cites current backlog DB authority, but its model still leaves open whether "`backlog_items` becomes a rankable queue table over `projects` and `work_items`" (`bridge/gtkb-first-class-project-artifacts-001.md:111`). That is incompatible with the current live backlog authority unless the proposal explicitly seeks formal supersession.

Evidence:

- `bridge/gtkb-first-class-project-artifacts-001.md:32-33` cites `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, and `DCL-STANDING-BACKLOG-SCHEMA-001` as current/planned backlog authority to reconcile with.
- `bridge/gtkb-first-class-project-artifacts-001.md:86` introduces `Backlog entry` as a distinct rankable queue representation, and `bridge/gtkb-first-class-project-artifacts-001.md:111` leaves `backlog_items` open as a possible table.
- Live `KnowledgeDB.get_spec("ADR-STANDING-BACKLOG-DB-AUTHORITY-001")` returned version 3, status `specified`, with the decision that canonical backlog authority is the MemBase `current_work_items` view backed by append-only `work_items`, and that v3 supersedes prior `backlog_items` table references.
- Live `KnowledgeDB.get_spec("DCL-STANDING-BACKLOG-DB-SCHEMA-001")` returned version 3, status `specified`, with the constraint that `work_items` extended with backlog columns is the canonical schema and `current_work_items` is the canonical backlog query.
- Live `KnowledgeDB.get_spec("GOV-STANDING-BACKLOG-001")` returned version 4, status `specified`, saying the post-migration implementation surface is `work_items` / `current_work_items`, and that `backlog_items` never existed in MemBase.
- The current implementation has the backlog metadata fields on `work_items` at `groundtruth-kb/src/groundtruth_kb/db.py:253` through `groundtruth-kb/src/groundtruth_kb/db.py:285`, adds backlog indexes to `work_items` at `groundtruth-kb/src/groundtruth_kb/db.py:751` through `groundtruth-kb/src/groundtruth_kb/db.py:762`, and defines `current_work_items` at `groundtruth-kb/src/groundtruth_kb/db.py:527` through `groundtruth-kb/src/groundtruth_kb/db.py:530`.
- `config/agent-control/system-interface-map.toml:17` through `config/agent-control/system-interface-map.toml:29` names the backlog authoritative source as `current_work_items`; `config/agent-control/system-interface-map.toml:37` through `config/agent-control/system-interface-map.toml:45` gives the same authority for work items.

Deficiency rationale:

The proposal can introduce `projects`, project membership, project dependencies, and project artifact links without changing the settled backlog-record identity. Leaving `backlog_items` open as a possible rankable queue table lets implementation drift back into the exact wrapper-table path S342 superseded. That would create a second candidate backlog authority beside `work_items` / `current_work_items` and would undermine the just-completed backlog migration pivot.

Required action:

Revise the proposal to make `work_items` / `current_work_items` non-negotiable backlog authority for this work. If project-level stack rank is needed, model it as project rank plus membership ordering/dependency metadata, or explicitly define a project-ranking surface that does not reintroduce `backlog_items` as a work/backlog authority. If Prime believes a separate rankable queue table is still required, the revision must explicitly propose formal supersession of `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3, `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3, and `GOV-STANDING-BACKLOG-001` v4 with owner-approval evidence.

Owner decision needed:

No owner decision is needed if Prime keeps `work_items` / `current_work_items` as the backlog authority and layers project artifacts around it. An owner decision would be needed only if Prime wants to supersede S342's backlog-authority pivot.

### F2 - The owner-input section does not satisfy the active required heading

Severity: P1 bridge gate mismatch; blocking.

Observation: the proposal contains substantive owner-input content, but the heading is `## Owner Decisions And Input` (`bridge/gtkb-first-class-project-artifacts-001.md:50`) instead of the active `## Owner Decisions / Input` section name required by the bridge review gate.

Evidence:

- `bridge/gtkb-first-class-project-artifacts-001.md:50` uses `## Owner Decisions And Input`.
- The proposal depends on owner decision scope: `bridge/gtkb-first-class-project-artifacts-001.md:52` through `bridge/gtkb-first-class-project-artifacts-001.md:62` records the owner's working model and says the chat input is sufficient direction to create the proposal while not granting formal artifact mutation approval.
- `.claude/rules/codex-review-gate.md:101` requires applicable proposals/reports to include a non-empty `## Owner Decisions / Input` section.
- `.claude/rules/codex-review-gate.md:103` says Codex review checks the section's presence and substance, and Loyal Opposition issues NO-GO when applicable proposals/reports lack the section.
- `.claude/rules/loyal-opposition.md:130` and `.claude/rules/loyal-opposition.md:132` repeat the Loyal Opposition NO-GO obligation and substantive-content check.

Deficiency rationale:

The content is useful, but the bridge gate is intentionally mechanical and section-name based. A near-match heading increases the chance that future hook or report tooling fails to recognize the approval-scope narrative. This proposal is specifically about lifecycle artifacts and owner-stated vocabulary, so the owner-input audit surface needs to be exact.

Required action:

Rename the heading to `## Owner Decisions / Input` in the revised proposal and preserve the substantive content. Also state whether the evidence is direct chat-only, AskUserQuestion-backed, or formal artifact approval packet-backed. The current text correctly says formal GOV/ADR/DCL/SPEC/rule mutations remain separately gated; keep that limit.

Owner decision needed:

None. This is a proposal-format correction.

### F3 - `Subject` must be disambiguated before schema implementation starts

Severity: P2 terminology and schema ambiguity; blocking for Slice 1 as drafted.

Observation: the proposal introduces `Subject` as a normalized schema concept in Slice 1 (`bridge/gtkb-first-class-project-artifacts-001.md:82`, `bridge/gtkb-first-class-project-artifacts-001.md:94` through `bridge/gtkb-first-class-project-artifacts-001.md:99`) while deferring governance and glossary alignment to Slice 3 (`bridge/gtkb-first-class-project-artifacts-001.md:128` through `bridge/gtkb-first-class-project-artifacts-001.md:132`). Current GT-KB terminology already has `application`, `platform`, `hosted application`, and `work subject`, and the proposal acknowledges that `Subject` must be mapped carefully rather than blindly replacing `application`.

Evidence:

- `.claude/rules/operating-model.md:17` defines `application`, `project`, `sub-project`, `platform`, and `hosted application`, and explicitly says a project is not the hosted application.
- `.claude/rules/operating-model.md:59` through `.claude/rules/operating-model.md:69` define `project`, `work item`, and `backlog`, including that all work items are backlog items and that known work converges into `work_items`.
- `.claude/rules/canonical-terminology.md:946` through `.claude/rules/canonical-terminology.md:967` defines `work subject` as the startup-payload concept naming the active subject area of a session.
- `config/agent-control/system-interface-map.toml:412` through `config/agent-control/system-interface-map.toml:425` defines `work-subject`, including accepted aliases `active subject` and `project subject`, and discourages using `project` for it.
- `bridge/gtkb-first-class-project-artifacts-001.md:82` proposes `Subject` as an owner-facing conceptual target, and `bridge/gtkb-first-class-project-artifacts-001.md:155` through `bridge/gtkb-first-class-project-artifacts-001.md:156` identifies conflict with `application` as a risk.

Deficiency rationale:

Implementing a `subjects` table before resolving this naming boundary risks encoding a new canonical concept that overlaps with the existing `work subject` session-scope term and the `application` lifecycle term. The proposal's own mitigation says the mapping must be careful, but the slice order puts schema implementation ahead of terminology/governance alignment.

Required action:

Revise the slice order or Slice 1 scope so `Subject` is disambiguated before the `subjects` table becomes implementation scope. Acceptable revisions include: (a) move the minimal terminology/governance alignment for `Subject` ahead of schema creation; (b) keep Slice 1 limited to `projects` and project/work-item memberships while deferring `subjects`; or (c) rename the schema concept to a less overloaded term and explicitly state how it relates to `work subject`, `application`, `platform`, and `hosted application`.

Owner decision needed:

Not necessarily. Prime can propose a conservative default, but any formal terminology/rule mutation still needs the applicable owner approval packet.

## Verification Performed

- Read `harness-state/harness-identities.json`: Codex maps to durable harness ID `A`.
- Read `harness-state/role-assignments.json`: harness `A` has role set `["loyal-opposition", "prime-builder"]`; this dispatch carried `lo`, so only `NEW` / `REVISED` entries were actionable.
- Read live `bridge/INDEX.md`: `gtkb-first-class-project-artifacts` latest status was `NEW` at `bridge/gtkb-first-class-project-artifacts-001.md`.
- Read full selected bridge thread. This is the first version, so the full chain is `-001` only.
- Read required bridge/review rules: `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/report-depth-prime-builder-context.md`, `.claude/rules/project-root-boundary.md`, and `.claude/rules/canonical-terminology.md`.
- Ran bridge applicability preflight: PASS, no missing required/advisory specs.
- Ran ADR/DCL clause preflight: PASS, no blocking gaps.
- Searched the Deliberation Archive for project/backlog/work-item membership and the S342 backlog-authority pivot.
- Read current backlog authority through `KnowledgeDB.get_spec(...)` for `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, `GOV-STANDING-BACKLOG-001`, and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.
- Inspected current implementation and interface-map surfaces for `work_items`, `current_work_items`, `project_name`, `subproject_name`, backlog authority, and `work subject`.

I did not run pytest or ruff because this is a pre-implementation design proposal with no implementation diff to verify.

## Required Revision

Prime Builder should file `bridge/gtkb-first-class-project-artifacts-003.md` as `REVISED` with:

1. The project-artifact schema direction constrained to extend `work_items` / `current_work_items` as current backlog authority, with `backlog_items` removed as an open implementation option unless formal supersession is explicitly proposed.
2. An exact `## Owner Decisions / Input` section preserving the owner-direction evidence and approval-limit language.
3. A `Subject` terminology/schema ordering correction so implementation does not create a first-class `subjects` table before disambiguating it from `work subject`, `application`, `platform`, and `hosted application`.
4. Fresh applicability and clause preflight outputs after revision.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
