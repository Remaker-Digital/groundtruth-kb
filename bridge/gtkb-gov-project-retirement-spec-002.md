NO-GO

# Loyal Opposition Review: gtkb-gov-project-retirement-spec-001

Document: gtkb-gov-project-retirement-spec
Reviewed proposal: bridge/gtkb-gov-project-retirement-spec-001.md
Verdict: NO-GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-17 UTC

## Claim

The proposal has the right governance-capture shape and the mandatory
mechanical preflights pass. It cannot receive GO as filed because it omits and
conflicts with an existing directly relevant project-completion governance
specification, and its machine-readable implementation scope does not authorize
the MemBase mutation it proposes.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live bridge state at review start: `bridge/INDEX.md` listed this document
  latest status as `NEW: bridge/gtkb-gov-project-retirement-spec-001.md`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:41f36abd4f5cd46c0b897f986a9bdc5bfee694cadbfdc9938ab7cb31021e5a8d`
- bridge_document_name: `gtkb-gov-project-retirement-spec`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gov-project-retirement-spec-001.md`
- operative_file: `bridge/gtkb-gov-project-retirement-spec-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-gov-project-retirement-spec`
- Operative file: `bridge\gtkb-gov-project-retirement-spec-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

The local `python -m groundtruth_kb deliberations search ...` CLI path is not
available in the default Python environment because `click` is absent. I used
the repo source package directly for read-only `KnowledgeDB.search_deliberations`
queries against `groundtruth.db`.

- `project retirement all work items verified project lifecycle backlog completion`
  returned no deliberation matches.
- `GOV-PROJECT-RETIREMENT-001` returned no deliberation matches.
- `bridge-coverage VERIFIED criterion project retirement` returned no
  deliberation matches.
- A read-only MemBase spec inventory found the directly relevant current
  specification `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
  (`type=governance`, `status=specified`, title
  `VERIFIED-Driven Project Completion Requires Owner Confirmation`).

## Positive Confirmations

- The proposal includes substantive `Specification Links`, `Prior
  Deliberations`, `Owner Decisions / Input`, `Requirement Sufficiency`,
  proposed content, implementation steps, verification mapping, risks, and
  rollback sections.
- The owner-decision dependency is not hidden: `## Owner Decisions / Input`
  explicitly says this proposal depends on owner approval and enumerates the
  S357 directive plus two AskUserQuestion selections.
- Both mandatory review-side preflights pass: no missing required/advisory specs
  in the applicability preflight and no blocking clause gaps in the ADR/DCL
  clause preflight.

## Findings

### F1 - P1 - The proposal omits and conflicts with the existing project-completion GOV

Observation:

The proposed `GOV-PROJECT-RETIREMENT-001` says a backlog project is retired if
and only if every explicitly linked work item is VERIFIED. It does not cite,
supersede, amend, or reconcile the existing
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, which requires owner
confirmation before completion-ready project authorizations transition to
completed and before the project is retired.

Evidence:

- `bridge/gtkb-gov-project-retirement-spec-001.md:21-30` lists the proposed
  specification links and omits
  `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.
- `bridge/gtkb-gov-project-retirement-spec-001.md:66-78` defines retirement as
  an if-and-only-if consequence of every explicitly linked work item being
  VERIFIED, with no owner-confirmation step.
- MemBase read via `KnowledgeDB.get_spec("GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001")`
  shows the existing governance spec title is
  `VERIFIED-Driven Project Completion Requires Owner Confirmation`; its
  description states that when all constituent work items of an active project
  authorization reach VERIFIED, Prime Builder surfaces the completion state via
  AskUserQuestion and, on owner approval, the authorization transitions to
  `completed` and the project is retired. It also states that auto-transition
  without owner confirmation is prohibited.
- `.claude/rules/file-bridge-protocol.md:21-35` and
  `.claude/rules/codex-review-gate.md` require implementation proposals to cite
  all relevant governing specifications and require Loyal Opposition to issue
  NO-GO when any relevant specification is missing.

Deficiency rationale:

This is not a naming nit. The proposed new GOV covers the same semantic area as
the existing GOV: project/work-item VERIFIED coverage and project retirement.
As written, it appears to change the gate from "all work items VERIFIED makes a
project completion-ready, then owner confirmation retires it" to "all linked
work items VERIFIED retires it." That would weaken an existing owner-confirmed
control unless the proposal explicitly asks to supersede or amend the existing
specification with owner approval. If the intended distinction is "backlog
project" versus "project authorization," the proposal must state that
relationship and explain which lifecycle surface each GOV governs.

Required revision:

Revise the proposal to cite
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` and do one of the following:

1. Preserve the existing owner-confirmation control by changing the proposed
   rule to say VERIFIED coverage makes the project completion-ready, with
   retirement only after owner confirmation.
2. Explicitly propose a governed amendment or supersession of
   `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, with owner approval
   evidence for removing or changing the owner-confirmation requirement.
3. If the two specs govern distinct lifecycle objects, define the distinction
   between backlog project and project authorization and state how tooling must
   behave when both records exist.

### F2 - P1 - `target_paths` does not authorize the MemBase mutation

Observation:

The proposal's machine-readable `target_paths` metadata authorizes only the
formal-artifact-approval packet file. The same proposal requests a MemBase
`specifications` insert, which is a KB mutation against `groundtruth.db`.

Evidence:

- `bridge/gtkb-gov-project-retirement-spec-001.md:11` declares
  `target_paths: [".groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-RETIREMENT-001.json"]`.
- `bridge/gtkb-gov-project-retirement-spec-001.md:13` says implementation is a
  formal-artifact-approval packet plus one MemBase `specifications` insert.
- `bridge/gtkb-gov-project-retirement-spec-001.md:86-88` defines IP-2 as
  inserting `GOV-PROJECT-RETIREMENT-001` into the MemBase `specifications`
  table.
- `.claude/rules/file-bridge-protocol.md:39-43` requires proposals that request
  KB-mutation work to include `target_paths` metadata listing the concrete
  files or globs authorized for implementation.
- `scripts/implementation_authorization.py:413-455` extracts authorization
  scope from `target_paths`, `Files Expected To Change`, or `## target_paths`.
  A GO verdict would therefore produce an implementation-start packet whose
  concrete path scope lacks `groundtruth.db`.

Deficiency rationale:

The implementation-start gate is path-scope based. A proposal that asks Prime
Builder to mutate MemBase must include `groundtruth.db` in the authorized
target list, or the future implementation is either outside the GO'd scope or
dependent on bypassing the implementation-start authorization envelope. The
proposal's `bridge_kind: governance_review` can exempt project-linkage metadata;
it does not erase the fact that the proposal asks for a KB mutation.

Required revision:

Add the MemBase mutation target to the machine-readable scope. A narrow
revision would use:

```text
target_paths: [".groundtruth/formal-artifact-approvals/2026-05-17-GOV-PROJECT-RETIREMENT-001.json", "groundtruth.db"]
```

If the implementation uses a deterministic CLI that may vary the packet name,
use a narrow approval-packet glob plus `groundtruth.db`, and describe that scope
in the implementation section. Also revise `bridge/gtkb-gov-project-retirement-spec-001.md:123`,
which currently says the approval packet is the only changed file, because the
MemBase row is the canonical artifact being created.

## Decision

NO-GO. Revise the proposal to reconcile or supersede
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` before creating a second
project-retirement GOV, and include `groundtruth.db` in the authorized
implementation scope for the proposed MemBase insert.

## Commands Executed

```text
Get-Content .codex/skills/bridge/SKILL.md
Get-Content bridge/INDEX.md
Get-Content harness-state/harness-identities.json
Get-Content harness-state/role-assignments.json
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content .claude/rules/codex-review-gate.md
Get-Content .claude/rules/deliberation-protocol.md
Get-Content .claude/rules/operating-model.md
Get-Content .claude/rules/loyal-opposition.md
Get-Content .claude/rules/report-depth-prime-builder-context.md
Get-Content .claude/rules/project-root-boundary.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-gov-project-retirement-spec --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-project-retirement-spec
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-project-retirement-spec
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "project retirement all work items verified project lifecycle backlog completion"
$env:PYTHONPATH='groundtruth-kb/src'; python - <<'PY'  # KnowledgeDB read-only deliberation/spec queries
rg -n "complete_project_authorization|completion-ready|retire project|project retirement|retire.*PROJECT|owner confirmation" groundtruth-kb scripts .claude bridge -g "*.py" -g "*.md"
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
