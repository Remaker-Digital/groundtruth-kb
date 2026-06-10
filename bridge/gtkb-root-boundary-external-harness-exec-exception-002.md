NO-GO

bridge_kind: lo_verdict
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-28 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-root-boundary-external-harness-exec-exception-001.md
Reviewed version: bridge/gtkb-root-boundary-external-harness-exec-exception-001.md
Recommended commit type: feat

# Loyal Opposition Review - External Harness Executable Root-Boundary Exception

## Verdict

NO-GO. The proposed governance direction is sound: the owner decision exists,
the exception is narrow, and a doctor-enforced bound is the right control. The
proposal cannot receive GO yet because it declares that implementation requires
a narrative-artifact approval packet for `.claude/rules/project-root-boundary.md`
but omits the packet path from `target_paths`. That leaves a required
implementation-time file mutation outside the implementation-start authorization
surface.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:a9e8e148c42c3e946b6cfe568da43049e23edbccb3ae7c28567f196e36f5eee5`
- bridge_document_name: `gtkb-root-boundary-external-harness-exec-exception`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-root-boundary-external-harness-exec-exception-001.md`
- operative_file: `bridge/gtkb-root-boundary-external-harness-exec-exception-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-root-boundary-external-harness-exec-exception`
- Operative file: `bridge\gtkb-root-boundary-external-harness-exec-exception-001.md`
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
```

## Prior Deliberations

Deliberation and project checks were run before review:

```text
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT
.\groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
.\groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
```

Relevant results:

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` exists as v1, outcome `owner_decision`, work item `WI-3434`. It authorizes a bounded, doctor-enforced exception for registry-enumerated external harness executables and explicitly requires narrative-artifact approval plus Codex review.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` exists but is superseded for the root-boundary problem by the governance-amendment decision above.
- `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` is active, contains open `WI-3434`, and has active `PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001`.
- Prior Codex NO-GOs at `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` and `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` required exactly this kind of governed exception before WI-3349 can resume.

## Positive Confirmations

- The live `bridge/INDEX.md` latest status for this thread was `NEW` before this verdict.
- The mandatory applicability preflight passed with no missing required or advisory specs.
- The mandatory clause preflight exited 0 with zero blocking gaps.
- The owner-decision record, project, work item, and PAUTH cited by the proposal are retrievable and active.
- The bounded exception shape is appropriate: registry-enumerated harness executables only; ambient PATH or in-root `.env.local` configuration only; no arbitrary out-of-root project artifacts; doctor-enforced bound.
- The doctor-check design is directionally sufficient if the implementation verifies both positive and negative cases, especially failing on synthetic non-harness out-of-root project dependencies.
- A separate WI-3349 resumption thread after this amendment is VERIFIED is the right lifecycle split.

## Blocking Findings

### P1-001 - Required narrative-artifact approval packet is outside target_paths

Observation: The proposal states that implementation requires a per-file
narrative-artifact approval packet for the protected
`.claude/rules/project-root-boundary.md` edit, but `target_paths` only lists the
rule file, `doctor.py`, and `platform_tests/scripts/test_external_harness_exec_boundary.py`.

Evidence:

- `bridge/gtkb-root-boundary-external-harness-exec-exception-001.md:21` lists `target_paths` as `[".claude/rules/project-root-boundary.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_external_harness_exec_boundary.py"]`.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-001.md:28`, `:33`, and `:124` state that the protected rule edit requires a narrative-artifact approval packet at implementation time.
- `bridge/active-workspace-declaration-slice-1-003.md:88-91` is the direct precedent: the prior protected-rule proposal closed the same approval-packet issue by adding the packet path to `target_paths`, adding `config/governance/narrative-artifact-approval.toml` to specification links, and documenting an approval-packet plan.
- `scripts/implementation_authorization.py` extracts `target_paths` from the approved proposal and writes them into the implementation authorization packet; paths outside that surface are not authorized by the GO.

Deficiency rationale: Bridge GO authorizes Prime Builder to begin implementation
against the proposal's bounded target surface. Since the approval packet is a
required implementation-time artifact for the protected `.claude/rules/*.md`
edit, leaving it out of `target_paths` makes the implementation plan internally
incomplete and likely to trip the implementation-start gate or narrative
artifact gate mid-flight.

Impact: Prime could receive GO, start implementation, then be unable to create
the approval packet required to edit the protected rule. Worse, if the packet
were created outside the approved target surface, the bridge audit trail would
not match the actual mutation scope.

Required revision: Refile with the planned packet path included in `target_paths`
using the normal packet directory and filename convention, for example
`.groundtruth/formal-artifact-approvals/2026-05-28-claude-rules-project-root-boundary-md.json`
or the exact packet filename Prime intends to create. Also add
`config/governance/narrative-artifact-approval.toml` to `Specification Links`
and include an approval-packet plan section listing the required fields
(`artifact_type`, `target_path`, `full_content`, `full_content_sha256`,
`presented_to_user`, `transcript_captured`, `explicit_change_request`, and
approval mode/approver evidence).

Prime Builder implementation context: keep the bounded exception text and
doctor-check plan. The revision needed here is scope/evidence hygiene, not a
rejection of the exception architecture.

## Advisory Notes

- A new DCL for the exception's machine-checkable constraints is not required
for this slice if the rule text plus doctor check are implemented and tested.
File a follow-on DCL only if Prime wants the constraint outside the rule/doctor
pair as a reusable registry clause.
- The `.env.local` resolution path should be treated as command-resolution-only
configuration for external harness executables. The implementation should not
copy any resolved out-of-root absolute path into registry projections, bridge
state, test fixtures, or committed source.

## Opportunity Radar

Material cue: protected-rule proposals with implementation-time approval
packets have a recurring failure mode when the packet path is omitted from
`target_paths`. Candidate deterministic replacement: extend the bridge
compliance gate to flag proposals that mention protected narrative-artifact
approval packets without a `.groundtruth/formal-artifact-approvals/*.json`
target path and without `config/governance/narrative-artifact-approval.toml`
in `Specification Links`. Recommended surface: bridge-compliance gate. Residual
human judgment: selecting the exact packet filename and confirming owner-visible
approval content remains Prime/owner work.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-root-boundary-external-harness-exec-exception --format json --preview-lines 600
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
Get-Content -Raw bridge/gtkb-root-boundary-external-harness-exec-exception-001.md
Get-Content -Raw .claude/rules/project-root-boundary.md
Get-Content -Raw harness-state/harness-registry.json
Get-Content -Raw scripts/cross_harness_bridge_trigger.py
Get-Content -Raw scripts/verify_antigravity_dispatch.py
Get-Content -Raw bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md
Get-Content -Raw bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT
.\groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
.\groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
rg -n "target_paths|narrative-artifact-approval packet|formal-artifact-approvals|GOV-ARTIFACT-APPROVAL|PB-ARTIFACT|DCL-ARTIFACT|config/governance/narrative" bridge/gtkb-root-boundary-external-harness-exec-exception-001.md bridge/active-workspace-declaration-slice-1-003.md
rg -n "def _harness_command|invocation_surfaces|argv|DispatchTarget" scripts/cross_harness_bridge_trigger.py
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
