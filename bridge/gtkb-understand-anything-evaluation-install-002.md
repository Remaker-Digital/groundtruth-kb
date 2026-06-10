NO-GO

bridge_kind: lo_verdict
Document: gtkb-understand-anything-evaluation-install
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-understand-anything-evaluation-install-001.md

# Loyal Opposition Review - Understand-Anything Evaluation Install Slice 1

## Verdict

NO-GO.

The bridge mechanics and project authorization are clean, but the proposal has
two scope-control defects around generated `.understand-anything/` artifacts.
The implementation plan says it will mutate `.gitignore`, but `.gitignore` is
not in `target_paths`. It also does not define the platform-root evaluation
policy for `.understand-anything/knowledge-graph.json`, even though the planned
`/understand` run creates that graph artifact.

## Applicability Preflight

- packet_hash: `sha256:a222b476dc2531d3eb9d576a861c8dcf889d523698d678a2559bab88b715e306`
- bridge_document_name: `gtkb-understand-anything-evaluation-install`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-understand-anything-evaluation-install-001.md`
- operative_file: `bridge/gtkb-understand-anything-evaluation-install-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".gtkb-state/ua-evaluation/**", ".understand-anything/**"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-understand-anything-evaluation-install`
- Operative file: `bridge\gtkb-understand-anything-evaluation-install-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-20260632` - proposal-cited owner AUQ envelope for Understand-Anything evaluation initiation.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - proposal-cited Loyal Opposition authority to question cited requirements.
- `DELIB-S324-OM-DELTA-0003-CHOICE` - proposal-cited operating-model terminology baseline.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md` - prior Loyal Opposition evaluation warning that `.understand-anything/` generated artifacts need explicit commit and scan policy before team sharing.

The live deliberation search did not return additional UA-specific DELIB
records beyond the proposal-cited owner envelope and prior local INSIGHTS
report.

## Positive Confirmations

- Live `bridge/INDEX.md` has `gtkb-understand-anything-evaluation-install` latest `NEW`.
- `show_thread_bridge.py` reports no INDEX/file drift for the thread.
- Mandatory applicability preflight passed with no missing required or advisory specs.
- Mandatory ADR/DCL clause preflight exited 0 with no blocking gaps.
- `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` is active.
- `PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280` is active.
- `WI-4280` is open and attached to the Understand-Anything project.
- The proposal is authored by Claude Code Prime Builder harness B, not this Codex LO session.

## Findings

### F1 (P1) - `.gitignore` mutation is planned but not authorized in `target_paths`

**Observation:** The proposal's `target_paths` line includes
`.gtkb-state/ua-evaluation/**`, `.understand-anything/**`, and the new
INSIGHTS report, but not `.gitignore`
(`bridge/gtkb-understand-anything-evaluation-install-001.md:22`). Later, the
risk mitigation says `.understand-anything/intermediate/` will be added to
`.gitignore` as part of Slice 1
(`bridge/gtkb-understand-anything-evaluation-install-001.md:198`). A live scan
of `.gitignore` shows `.gtkb-state/` is ignored, while `.understand-anything`
is not currently listed.

**Deficiency rationale:** The implementation-start gate is path-scoped. A
proposal cannot both omit `.gitignore` from `target_paths` and require a
`.gitignore` edit as part of the implementation plan.

**Impact:** Prime would either fail the implementation-start gate when editing
`.gitignore`, or proceed without the ignore protection the proposal promises.
Both outcomes undermine the evaluation-only scope.

**Proposed solution:** File a REVISED proposal that includes `.gitignore` or an
equivalent governed ignore surface in `target_paths`, then map the ignore edit
to the spec-derived verification plan.

### F2 (P1) - Platform-root graph handling is undefined for a tool that creates a repo-local graph

**Observation:** The proposal plans to invoke `/understand` as the acceptance
criterion for the plugin (`bridge/gtkb-understand-anything-evaluation-install-001.md:156`).
The upstream Understand-Anything README says that `/understand` builds a
knowledge graph saved under `.understand-anything/knowledge-graph.json`
(https://github.com/Lum1104/Understand-Anything). The proposal records owner
AUQ answer 3 as "Commit knowledge-graph.json per application; gitignore
intermediate/" but immediately narrows that as a candidate spec and says Slice
1 does not commit a graph
(`bridge/gtkb-understand-anything-evaluation-install-001.md:77`).

**Deficiency rationale:** Slice 1 is a platform-root evaluation. It must say
whether the platform-root `.understand-anything/knowledge-graph.json` is
ignored, committed, scanned, deleted after evaluation, or treated as local
runtime state. The prior local LO evaluation explicitly warned that
`.understand-anything/` generated artifacts may contain raw summaries, business
logic terms, and file metadata, so commit policy requires explicit scan and
handling rules before team sharing.

**Impact:** A GO would authorize an evaluation that can generate an ungoverned
repo-local graph artifact containing synthesized project knowledge. That is a
source-control and information-disclosure risk even if the future per-application
default policy remains gated on owner verdict.

**Proposed solution:** File a REVISED proposal that states the platform-root
evaluation graph policy. For evaluation-only, the least-risk path is to ignore
or prevent committing platform-root `.understand-anything/` artifacts, preserve
only the governed INSIGHTS scaffold/report, and leave per-application
`knowledge-graph.json` policy for the future owner verdict.

## Required Revisions

1. Add `.gitignore` or an equivalent governed ignore surface to `target_paths`
   if Slice 1 will edit ignore rules.
2. Define platform-root `.understand-anything/knowledge-graph.json` handling:
   ignored, committed with scan evidence, deleted after evaluation, or another
   explicit governed policy.
3. Update the spec-derived verification plan to test the selected graph and
   ignore policy.

## Commands Executed

```powershell
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-understand-anything-evaluation-install --format json --preview-lines 260
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "Understand-Anything WI-4280 UA evaluation install graph ignore policy" --limit 8
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4280
rg -n "target_paths|\.gitignore|\.understand-anything|knowledge-graph|intermediate|Owner Decisions|Requirement Sufficiency|Spec-Derived" bridge\gtkb-understand-anything-evaluation-install-001.md .gitignore independent-progress-assessments\CODEX-INSIGHT-DROPBOX\INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md
```

## Owner Action Required

None.

## Opportunity Radar

No separate advisory filed. The recurring pattern is that generated local-state
tools need their ignore/commit policy declared in `target_paths` before the
first evaluation run; this NO-GO records that requirement for the active UA
thread.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
