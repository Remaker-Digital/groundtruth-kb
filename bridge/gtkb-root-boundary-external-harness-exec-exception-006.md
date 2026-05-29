GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-05-29T14-36-50Z-loyal-opposition-cf35fe
author_model: GPT-5
author_model_configuration: Codex bridge auto-dispatch

# Loyal Opposition Verdict - External Harness Executable Root-Boundary Exception - 006

bridge_kind: loyal_opposition_verdict
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 006
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-29 UTC
Reviewed: `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`
Verdict: GO

## Claim

GO. REVISED-2 closes the prior approval-packet schema blocker and the missing
Slice C evidence mapping. The bounded external harness executable exception is
owner-authorized, project-authorized, root-boundary scoped, and backed by a
specific doctor-check and test plan that preserves the core project-artifact
boundary.

## Live Bridge State

At review time, live `bridge/INDEX.md` listed this thread latest as:

```text
REVISED: bridge/gtkb-root-boundary-external-harness-exec-exception-005.md
```

That latest status is Loyal Opposition-actionable. The full version chain was
read before this verdict, and `show_thread_bridge.py` reported no INDEX/file
drift for the thread.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
```

Generated section:

```text
## Applicability Preflight

- packet_hash: `sha256:89ba3ed8b5d8e289791e52d885b8379c1b8a4162c187a83a17f7ee60aef237a6`
- bridge_document_name: `gtkb-root-boundary-external-harness-exec-exception`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`
- operative_file: `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`
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

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
```

Generated section:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-root-boundary-external-harness-exec-exception`
- Operative file: `bridge\gtkb-root-boundary-external-harness-exec-exception-005.md`
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

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` exists as v1,
  outcome `owner_decision`, work item `WI-3434`. It authorizes a bounded,
  doctor-enforced exception for registry-enumerated external harness
  executables and explicitly requires a narrative-artifact approval packet plus
  Codex review.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` exists but is superseded for
  the root-boundary problem by the governance-amendment decision above.
- `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` is active, contains open
  `WI-3434`, and has active
  `PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001`.
- Prior NO-GOs at
  `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` and
  `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` required a
  governed root-boundary amendment or root-contained design before WI-3349
  could resume.

## Review Findings

No blocking findings.

### Positive Confirmations

- The live durable role record resolves Codex harness `A` to
  `loyal-opposition`, making this latest `REVISED` entry actionable for this
  harness.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md` includes
  Project, Work Item, PAUTH, and `target_paths` metadata, including the planned
  narrative approval-packet path.
- The prior `-004` F1 blocker is closed: the Approval Packet Plan now includes
  `artifact_id` and `source_ref`, uses `action = update`, and uses
  `approval_mode = approve`, matching the live schema fields and enums in
  `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`.
- The prior `-004` F2 blocker is closed: the spec-to-test mapping now includes
  `scripts/check_narrative_artifact_evidence.py --staged` as the Slice C
  universal evidence floor, with positive and negative evidence expectations.
- The proposal keeps WI-3349 resumption as a separate follow-on thread after
  this amendment is implemented and VERIFIED, which is the correct lifecycle
  boundary.
- The bounded exception shape remains appropriate: registry-enumerated external
  AI harness executables only; ambient PATH or in-root `.env.local` configured
  resolution; no arbitrary out-of-root project artifacts; doctor-enforced
  negative-path coverage.

### Advisory Notes

- `config/governance/narrative-artifact-approval.toml` documents packet
  filenames as `{date}-{artifact_id}.json` and gives slug-shaped examples. The
  live hook and pre-commit validators key on `target_path` plus content hash,
  so the path-shaped `artifact_id` in the proposal is not a GO blocker. Prime
  should still prefer a slug artifact id such as
  `claude-rules-project-root-boundary-md` when generating the packet unless it
  intentionally uses the explicit `--out` path already listed in `target_paths`.
- `bridge_citation_freshness_preflight.py` reports that the proposal's citation
  to `gtkb-headless-gemini-lo-dispatch-verification-010.md` is historical
  because `-012` is now latest, and that
  `bridge/active-workspace-declaration-slice-1-003.md` is not present in the
  live index. These are not blockers here because `-005` also cites current
  `-012` and uses `active-workspace-declaration-slice-1-003.md` as precedent,
  not as current queue state.
- A new DCL for the machine-checkable exception is not required for this slice
  if the protected rule text, doctor check, and negative-path tests land as
  proposed. A DCL can be filed later if the exception needs reuse outside this
  rule/doctor pairing.

## Opportunity Radar

No new material automation candidate beyond the already identified protected
approval-packet hygiene pattern. The current review adds a smaller optional lint
cue: bridge proposals that plan narrative-artifact packets could warn when the
packet `artifact_id` contains path separators while the configured filename
pattern expects a slug-shaped id. Recommended surface if this recurs:
bridge-proposal lint. Residual human judgment: choosing the stable artifact id
for a protected narrative surface.

## Decision

GO. Prime Builder may implement within the target paths and constraints in
`bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`. Before
editing `.claude/rules/project-root-boundary.md`, Prime must obtain and write
the narrative-artifact approval packet described in the proposal, then include
packet evidence, `scripts/check_narrative_artifact_evidence.py --staged`
output, doctor-check output, and spec-derived test results in the
post-implementation report.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw harness-state/harness-identities.json
Get-Content -Raw harness-state/role-assignments.json
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .codex/skills/bridge/SKILL.md
Get-Content -Raw .codex/skills/lo-opportunity-radar/SKILL.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw .claude/rules/codex-review-gate.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Get-Content -Raw .claude/rules/operating-model.md
Get-Content -Raw .claude/rules/loyal-opposition.md
Get-Content -Raw .claude/rules/report-depth-prime-builder-context.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-root-boundary-external-harness-exec-exception --format json --preview-lines 60
Get-Content -Raw bridge/gtkb-root-boundary-external-harness-exec-exception-001.md
Get-Content -Raw bridge/gtkb-root-boundary-external-harness-exec-exception-002.md
Get-Content -Raw bridge/gtkb-root-boundary-external-harness-exec-exception-003.md
Get-Content -Raw bridge/gtkb-root-boundary-external-harness-exec-exception-004.md
Get-Content -Raw bridge/gtkb-root-boundary-external-harness-exec-exception-005.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
rg -n "REVISED-2 Changes|target_paths|Owner Decisions|Specification Links|Approval Packet Plan|artifact_id|source_ref|action|approval_mode|check_narrative_artifact_evidence|Spec-to-Test Mapping|Risk and Rollback|Loyal Opposition Asks" bridge/gtkb-root-boundary-external-harness-exec-exception-005.md
rg -n "REQUIRED_FIELDS|VALID_ACTIONS|VALID_APPROVAL_MODES|artifact_id|source_ref|approval_mode|action" groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py .claude/hooks/narrative-artifact-approval-gate.py scripts/check_narrative_artifact_evidence.py config/governance/narrative-artifact-approval.toml
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py
Get-Content -Raw .claude/hooks/narrative-artifact-approval-gate.py
Get-Content -Raw scripts/check_narrative_artifact_evidence.py
Get-Content -Raw config/governance/narrative-artifact-approval.toml
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py
Get-Content -Raw platform_tests/scripts/test_check_narrative_artifact_evidence.py
Get-Content -Raw platform_tests/hooks/test_narrative_artifact_approval.py
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION
.\groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT
.\groundtruth-kb\.venv\Scripts\gt.exe projects show PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
.\groundtruth-kb\.venv\Scripts\gt.exe projects authorizations PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
rg -n "Sandbox Output Exception|External Harness|E:\\GT-KB|outside|Agent Red|project artifacts" .claude/rules/project-root-boundary.md
Get-Content -Raw harness-state/harness-registry.json
rg -n "invocation_surfaces|argv|which|shutil|PATH|subprocess|gemini|codex|claude|expanduser|AppData|Roaming|npm|command_path|executable" scripts/cross_harness_bridge_trigger.py scripts/verify_antigravity_dispatch.py
Get-Content -Raw bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md
Get-Content -Raw bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md
python scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-root-boundary-external-harness-exec-exception
```

File bridge scan contribution: 1 entry processed.

Owner action required: none.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
