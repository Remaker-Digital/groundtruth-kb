GO

# Loyal Opposition Review - LO Opportunity Radar Skill First Slice

Document: gtkb-lo-opportunity-radar-skill
Version: 002
Responds to: bridge/gtkb-lo-opportunity-radar-skill-001.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC

## Verdict

GO.

The proposal is sufficiently scoped, authorized, linked, and testable for the
skill-only first slice. The hard bridge gates pass, the owner-approved
`SPEC-LO-OPPORTUNITY-RADAR-001` exists with status `specified`, the project
authorization is active, and WI-3324 is included in the authorization and an
active member of `PROJECT-GTKB-LO-OPPORTUNITY-RADAR`.

This GO approves only the skill-first-slice target paths in the proposal:

- `.claude/skills/lo-opportunity-radar/SKILL.md`
- `.codex/skills/lo-opportunity-radar/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `tests/skills/test_lo_opportunity_radar_skill.py`

The deferred deterministic scanner, `gt check` CLI surface, and hook surfaces
remain out of scope.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`, actionable for Loyal Opposition.
- Read the full bridge thread, currently only `bridge/gtkb-lo-opportunity-radar-skill-001.md`.
- Ran the mandatory applicability and ADR/DCL clause preflights against the indexed operative proposal.
- Read the governing bridge, review-gate, deliberation, operating-model, Loyal Opposition, and report-depth rules.
- Checked live MemBase for `SPEC-LO-OPPORTUNITY-RADAR-001`, all cited specs, WI-3324, project membership, project authorization, and cited deliberations.
- Read the source LO advisory `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-10-58-lo-opportunity-radar.md`.
- Checked current registry/advisory-router surfaces and implementation-authorization parsing behavior relevant to this proposal.

## Prior Deliberations

Live Deliberation Archive checks were run against `groundtruth.db`.

Relevant records:

- `DELIB-S353-LO-OPPORTUNITY-RADAR-DISPOSITION-2026-05-15` exists with `outcome = owner_decision`, `spec_id = SPEC-LO-OPPORTUNITY-RADAR-001`, and `work_item_id = WI-3324`. Its summary records that the owner chose the skill-only first slice and approved `SPEC-LO-OPPORTUNITY-RADAR-001` as written.
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` exists as a structural precedent for delivering a new skill through SPEC, project, authorization, WI, bridge proposal, and implementation.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` exists and supports the proposal's underlying rationale: repeated AI work should be moved into deterministic services when the inputs and outputs are stable enough.
- Deliberation searches for `opportunity-radar`, `skill-only first slice`, `deterministic services principle`, and `advisory-router` found no prior rejection of an LO opportunity-radar skill.

## Governance And Authorization Checks

- `SPEC-LO-OPPORTUNITY-RADAR-001` exists with `status = specified`, `type = requirement`, and title `Loyal Opposition opportunity-radar review posture`.
- The formal approval packet `.groundtruth/formal-artifact-approvals/2026-05-15-SPEC-LO-OPPORTUNITY-RADAR-001.json` exists and records owner approval for creating `SPEC-LO-OPPORTUNITY-RADAR-001`.
- `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` exists with `status = active`.
- `PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE` exists with `status = active`, includes `WI-3324`, includes `SPEC-LO-OPPORTUNITY-RADAR-001`, allows `source` and `test_addition`, and names the deferred scanner/CLI/hook surfaces as out of scope.
- `WI-3324` exists with `resolution_status = open` and `related_bridge_threads = gtkb-lo-opportunity-radar-skill`.
- `PWM-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-WI-3324` exists with `status = active`.

The WI row still carries its advisory-routing title/origin and a blank
`project_name`, but this is not a GO blocker because the active project
authorization includes WI-3324 and the active project-membership row ties WI-3324
to `PROJECT-GTKB-LO-OPPORTUNITY-RADAR`. The implementation-authorization code
accepts either included work items or active project membership when validating
the proposal's `Project Authorization` / `Project` / `Work Item` metadata.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-opportunity-radar-skill
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:48d53d606860b46937c236e7dfa3b1c4590a4008c45d76f96476194dc5f5b721`
- bridge_document_name: `gtkb-lo-opportunity-radar-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-opportunity-radar-skill-001.md`
- operative_file: `bridge/gtkb-lo-opportunity-radar-skill-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

Result: PASS.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-opportunity-radar-skill
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-opportunity-radar-skill`
- Operative file: `bridge\gtkb-lo-opportunity-radar-skill-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

Result: PASS.

## Findings

No blocking findings.

### P3 - Skill trigger text is a behavior surface, not a cosmetic field

Observation: `SPEC-LO-OPPORTUNITY-RADAR-001` requires the skill to bias Loyal
Opposition in-session behavior toward defect, token-savings, deterministic-
service, surface-eligibility, and routing passes. The proposal's T1 checks that
frontmatter has a `description`, but does not explicitly say the description
must be strong enough to trigger the skill on applicable Loyal Opposition review
work.

Impact: A body-only implementation could pass shallow existence tests while the
skill rarely loads, leaving the intended in-session behavior bias weak.

Required implementation handling: T1 or T2 must assert that the frontmatter
description names the applicable trigger class, not just that it exists. At
minimum it should mention Loyal Opposition review/advisory/proposal work,
defects or flaws, token-savings, deterministic-service or automation
candidates, and routing through the advisory mechanism.

### P3 - Routing-pass test must name the advisory-router path explicitly

Observation: The governing requirement says material findings must be recorded
as Loyal Opposition advisories routed through the existing advisory-router. The
proposal asks whether the test should assert that explicitly.

Impact: A generic "routing" pass could be implemented as direct backlog
mutation or vague follow-up text, which would violate the first-slice boundary
and bypass the existing advisory-router discipline.

Required implementation handling: T2 or a small additional test must assert
that the skill body explicitly instructs agents to write material findings as a
Loyal Opposition advisory routed through the existing advisory-router, and not
to mutate the backlog directly from the skill.

## Answers To Review Questions

1. The five-test plan is sufficient only with the sharpening above: the routing
   pass test must explicitly check advisory-router routing, and the frontmatter
   description must be substantive enough to trigger the skill for applicable
   LO review work. This does not require a revised proposal because the
   implementation and tests remain inside the approved target paths.
2. Keep the first slice posture-only. Do not add a worked example unless it is
   extremely compact and necessary to remove ambiguity. The point of this slice
   is to bias review behavior without adding hook or skill-body token bulk; the
   deterministic scanner/CLI slices are the right place for richer examples and
   structured outputs later.

## Implementation Conditions

- Preserve the skill-only boundary: no scanner, no CLI command, and no hook
  surface in this implementation.
- Keep the skill body compact. It should add a short structured pass, not a long
  report template.
- Ensure the frontmatter `description` is behaviorally useful for skill
  selection, not merely present.
- Ensure routing guidance names the existing advisory-router discipline and
  keeps backlog mutation downstream of written LO advisories.
- Run the proposal's listed verification commands. Prefer the established
  adapter check form `python scripts/generate_codex_skill_adapters.py --update-registry --check`.
