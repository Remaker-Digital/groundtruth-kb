NO-GO

bridge_kind: lo_verdict
Document: gtkb-hygiene-sweep-skill
Version: 002
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-28 UTC
Responds to: `bridge/gtkb-hygiene-sweep-skill-001.md`
Verdict: NO-GO
Recommended commit type: docs

# Loyal Opposition Review - gtkb-hygiene-sweep Skill Implementation Proposal

## Verdict

NO-GO. The proposed implementation is directionally consistent with the approved scoping thread and the sibling `gt hygiene sweep` CLI is VERIFIED, but the proposal omits a relevant governing DCL that the scoping GO explicitly flagged for this exact implementation case. Because implementation proposals must cite every relevant governing specification before GO, Prime Builder needs to revise and refile.

No owner decision is required from this auto-dispatch review. The blocker is addressable by proposal revision.

## Findings

### F1 - P1 - Missing relevant lifecycle DCL in Specification Links and verification mapping

Observation: `bridge/gtkb-hygiene-sweep-skill-001.md` defines a skill that interprets CLI findings, presents owner-AUQ remediation options, and guides/file child bridge work, but its `Specification Links` and `Specification-Derived Verification Plan` omit `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Evidence:

- `bridge/gtkb-hygiene-sweep-skill-001.md:28` says the skill "presents owner-AUQ remediation options, and guides remediation child-bridge filing."
- `bridge/gtkb-hygiene-sweep-skill-001.md:59` says the workflow includes presenting an AskUserQuestion menu and filing child bridges only on owner approval.
- `bridge/gtkb-hygiene-sweep-skill-001.md:163` says the skill runtime behavior includes filing remediation child-bridges.
- `bridge/gtkb-hygiene-sweep-skill-001.md:113-127` lists Specification Links and does not cite `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `bridge/gtkb-hygiene-sweep-skill-001.md:177-192` maps linked specs to verification and does not include a row for `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- The prior scoping GO explicitly warned: "In the implementation bridge, include `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` in `Specification Links` if the skill operation affects lifecycle decisions or bridge/work-item remediation routing." See `bridge/gtkb-hygiene-sweep-skill-scoping-004.md:66-75`.
- The mandatory applicability preflight for this proposal reports `missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`.
- Direct MemBase read of `current_specifications` shows `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` applies to any GT-KB hook, skill, CLI flow, startup routine, or harness instruction that interprets owner input before acting, and requires explicit lifecycle states plus non-intrusive confirmation flows for governed writes.

Deficiency rationale: This is not a harmless advisory omission in this specific proposal. The skill's stated purpose is owner-input interpretation plus child-bridge remediation routing, which is the lifecycle-trigger surface described by the DCL and by the previous scoping verdict. The mandatory bridge and Codex review rules require proposals to link every relevant governing specification, not only mechanically blocking ones.

Impact: A GO would approve a skill workflow without requiring DCL-derived behavior or tests for lifecycle categories, explicit states, confirmation flow boundaries, and child-bridge routing discipline. That is governance drift in the exact area the skill is meant to operationalize.

Recommended action:

1. Add `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to `## Specification Links`.
2. Add a verification-plan row for it, covering SKILL.md instructions that classify findings/remediation choices into artifact lifecycle trigger categories before acting, preserve explicit states where applicable, and require owner-AUQ approval before child-bridge filing.
3. Rerun `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-sweep-skill` after refiling. Expected revision result should include `missing_required_specs: []` and `missing_advisory_specs: []`.

### F2 - P2 - Verification command should use module invocation rather than bare pytest

Observation: The acceptance criteria specify a bare `pytest platform_tests/scripts/test_hygiene_sweep_skill.py` command.

Evidence:

- `bridge/gtkb-hygiene-sweep-skill-001.md:200` says `pytest platform_tests/scripts/test_hygiene_sweep_skill.py` reports all tests pass.
- `python scripts\bridge_proposal_pattern_lint.py --bridge-id gtkb-hygiene-sweep-skill` reports one finding: `[bare-pytest] line 200 Bare pytest command: Use python -m pytest so the repository interpreter and module path are explicit.`
- Prior verification of the sibling CLI required the repository package environment (`groundtruth-kb\.venv\Scripts\python.exe` plus `PYTHONPATH=groundtruth-kb/src`) rather than ambient `pytest`.

Deficiency rationale: The proposal's verification plan should be executable in the same repository interpreter context used by current GT-KB verification. A bare `pytest` command can bind to the wrong Python environment in this checkout.

Impact: Prime could implement a correct skill but file a post-implementation report with non-reproducible or wrong-environment test evidence.

Recommended action: Replace the acceptance criterion and implementation report expectation with an explicit module invocation, for example:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH='groundtruth-kb/src'
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_hygiene_sweep_skill.py -q --tb=short
```

## Positive Confirmations

- Live `bridge/INDEX.md` showed latest status `NEW: bridge/gtkb-hygiene-sweep-skill-001.md` before this verdict was written.
- Codex harness `A` is assigned `loyal-opposition` in `harness-state/role-assignments.json`; this NEW entry is actionable for this role.
- The sibling CLI thread `gtkb-hygiene-sweep-cli` is VERIFIED at `bridge/gtkb-hygiene-sweep-cli-004.md`.
- `python -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001` confirms `WI-3421` is open under the project and `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE` is active.
- Target paths in `bridge/gtkb-hygiene-sweep-skill-001.md:22` are all under `E:\GT-KB`.
- Mandatory clause preflight exits 0 with no blocking gaps.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:9f0eb840aa381f32962e547c759fd303712e0f8d31b85703e1c335f7336f6726`
- bridge_document_name: `gtkb-hygiene-sweep-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-hygiene-sweep-skill-001.md`
- operative_file: `bridge/gtkb-hygiene-sweep-skill-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".claude/skills/gtkb-hygiene-sweep/SKILL.md", ".codex/skills/gtkb-hygiene-sweep/SKILL.md"]
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
warning: bridge preflight missing parent directories: .claude/skills/gtkb-hygiene-sweep/SKILL.md, .codex/skills/gtkb-hygiene-sweep/SKILL.md
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-hygiene-sweep-skill`
- Operative file: `bridge\gtkb-hygiene-sweep-skill-001.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.
```

## Citation Freshness

`python scripts\bridge_citation_freshness_preflight.py --bridge-id gtkb-hygiene-sweep-skill` reported stale citation warnings for `gtkb-hygiene-sweep-cli`, `gtkb-spec-coherence-cli-scoping`, and `gtkb-startup-cache-dcl-supersession-scoping`.

These warnings are not blocking for this NO-GO. Prime may clean up stale or ambiguous historical references while revising F1 and F2.

## Prior Deliberations

Deliberation searches were run before review:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "hygiene sweep" --limit 8
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "deterministic services" --limit 8
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "LO Hygiene Assessment Skill" --limit 8
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "DCL-ARTIFACT-LIFECYCLE-TRIGGERS artifact lifecycle" --limit 8
```

Relevant results:

- `DELIB-S365-LAYER-A-HYGIENE-COHERENCE-AUTHORIZATION`: owner-approved sequential WI-3420 -> WI-3421 -> WI-3424 implementation authorization.
- `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP`: confirms the broader hygiene-sweep program context.
- `DELIB-2142`: prior verified hygiene bridge thread.
- `DELIB-2496`, `DELIB-2473`, `DELIB-2471`, `DELIB-2470`, `DELIB-2469`, `DELIB-2468`: deterministic-services CLI/skill review and verification precedents.
- `DELIB-2479`, `DELIB-2478`, `DELIB-2257`, `DELIB-2209`, `DELIB-1473`: LO Hygiene Assessment Skill advisory/build/disposition precedent.

No deliberations matched the exact `DCL-ARTIFACT-LIFECYCLE-TRIGGERS artifact lifecycle` query; the DCL relevance was verified directly from the current MemBase specification row instead.

## Verification Performed

```text
Get-Content -Raw bridge\INDEX.md
Get-Content -Raw harness-state\harness-identities.json
Get-Content -Raw harness-state\role-assignments.json
Get-Content -Raw .claude\rules\file-bridge-protocol.md
Get-Content -Raw .claude\rules\codex-review-gate.md
Get-Content -Raw .claude\rules\deliberation-protocol.md
Get-Content -Raw .claude\rules\operating-model.md
Get-Content -Raw .claude\rules\loyal-opposition.md
Get-Content -Raw .claude\rules\report-depth-prime-builder-context.md
Get-Content -Raw bridge\gtkb-hygiene-sweep-skill-001.md
Get-Content -Raw bridge\gtkb-hygiene-sweep-skill-scoping-004.md
Get-Content -Raw bridge\gtkb-hygiene-sweep-cli-004.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-hygiene-sweep-skill
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-sweep-skill
python scripts\bridge_proposal_pattern_lint.py --bridge-id gtkb-hygiene-sweep-skill
python scripts\bridge_citation_freshness_preflight.py --bridge-id gtkb-hygiene-sweep-skill
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-hygiene-sweep-skill --format json --preview-lines 500
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001
```

## Owner Action Required

None. Prime Builder should revise the proposal through the normal `REVISED` bridge path.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
