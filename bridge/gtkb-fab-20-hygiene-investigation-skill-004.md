GO

Document: gtkb-fab-20-hygiene-investigation-skill
Version: 004
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-20-hygiene-investigation-skill-003.md

# Loyal Opposition Verdict - FAB-20 Hygiene Investigation Skill

## Verdict

GO. The `-003` revision resolves the prior sequencing blocker by narrowing FAB-20 to a dependency-free first slice: the orchestration skill scaffold, chunked report generator, baseline registry, Codex adapter, capability-registration, and tests. Delta mode and any FAB-19 evidence-pack differ are explicitly deferred until FAB-19 reports a concrete implemented output contract.

The mandatory bridge gates pass. The missing-parent-dir warnings are expected for new skill directories and are not a scope blocker.

## Same-Session Guard

Not a self-review. The operative `REVISED` proposal was authored by Prime Builder harness B in session `e45ccf07-99f6-4ad6-b572-570a76a264a2`. This verdict is authored by Loyal Opposition harness A.

## Dependency / Future-Work Check

FAB-20 no longer needs FAB-19 to land first for this slice. The future delta-mode follow-on remains dependent on the implemented FAB-19 evidence-pack contract and must be filed as its own bridge thread with that output path cited.

The current target set touches new skill directories, helper scripts, a baseline registry, the harness capability registry, and tests. The protected narrative-artifact packet requirement does not apply to these paths; `config/governance/narrative-artifact-approval.toml` protects `.claude/rules/*.md`, AGENTS/CLAUDE files, and application-scope CLAUDE files, not `.claude/skills/**` or `config/agent-control/harness-capability-registry.toml`.

## Prior Deliberations

- `DELIB-FABLE-GRILL-20260610-Q5` records the owner repeatability architecture: deterministic CLI core, orchestration skill, and delta mode.
- `DELIB-FAB20-REMEDIATION-20260610` records FAB-20 as a determined build under Q5. The original determination included delta mode, but the `-003` revision safely sequences that piece into a separate follow-on.
- `DELIB-FAB19-REMEDIATION-20260610` records the FAB-19 detector-core decision that the deferred delta-mode follow-on will eventually consume.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports replacing repeated manual hygiene investigations with deterministic services and reusable skill workflows.

Deliberation search note: direct searches for `FAB20` and `hygiene investigation skill` returned no additional hits beyond the IDs already cited in the proposal/thread.

## Applicability Preflight

- packet_hash: `sha256:d1ea2efaf723d1c48b5d67ca228de72e59f13615526b05541e7916fe8b774cd8`
- bridge_document_name: `gtkb-fab-20-hygiene-investigation-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-20-hygiene-investigation-skill-003.md`
- operative_file: `bridge/gtkb-fab-20-hygiene-investigation-skill-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [".claude/skills/gtkb-hygiene-investigation/**", ".codex/skills/gtkb-hygiene-investigation/**"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-fab-20-hygiene-investigation-skill`
- Operative file: `bridge\gtkb-fab-20-hygiene-investigation-skill-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

No blocking findings.

Implementation constraints:

- Do not implement delta mode, an evidence-pack differ, or any FAB-19 output consumer in this slice.
- Keep generated findings routable to `work_items` without performing any bulk backlog/MemBase mutation.
- Keep the Codex adapter generated from the canonical skill source, not manually forked.
- Include parity/capability-registration evidence in the implementation report.

## Opportunity Radar

- Token-savings cue: the narrowed skill still captures the high-value manual-investigation workflow and avoids repeated report-shaping cost.
- Deterministic-service cue: the chunked report generator and baseline loader are the stable deterministic surfaces in this slice.
- Recommended surface: implementation should make the baseline registry loader/testable report generator callable without requiring a live agent run.
- Residual human judgment: probe completeness and finding quality remain review work; the service reduces setup/report cost, not substantive LO judgment.

## Required Next Step

Prime Builder may implement the dependency-free FAB-20 first slice. File any delta-mode/evidence-pack differ as a later bridge after FAB-19 implementation defines the producer contract.
