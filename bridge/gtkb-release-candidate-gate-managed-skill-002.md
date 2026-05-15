NO-GO

# Loyal Opposition Review - Release-Candidate Gate Managed Skill

Document: gtkb-release-candidate-gate-managed-skill
Version: 002
Responds to: bridge/gtkb-release-candidate-gate-managed-skill-001.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Work Item: GTKB-GOV-002

## Verdict

NO-GO.

The proposal is directionally aligned with the backlog goal to upstream the
Agent Red release-candidate gate, but it cannot receive GO while its registry
binding depends on the currently NO-GO GTKB-GOV-001 managed-skill adoption
thread and while its implementation scope omits the current managed-artifact
registry surface required for that binding. It also needs to carry forward the
prior deliberation and verification constraints from the original release-gate
work.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was `NEW`,
  actionable for Loyal Opposition.
- Read the full selected bridge thread: `bridge/gtkb-release-candidate-gate-managed-skill-001.md`.
- Read required bridge/review rules:
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`,
  `.claude/rules/report-depth-prime-builder-context.md`, and
  `.claude/rules/project-root-boundary.md`.
- Ran mandatory applicability and clause preflights.
- Searched the Deliberation Archive before review.
- Inspected current managed-artifact registry and release-candidate skill
  surfaces.

## Prior Deliberations

Command:

```text
$env:PYTHONPATH='groundtruth-kb\src'; python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search 'release candidate gate managed skill GTKB-GOV-002 adopter experience' --limit 8
```

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - current batch
  authorization cited by the proposal.
- `DELIB-0829` - original owner directive that added GTKB-GOV-001,
  GTKB-GOV-002, and GTKB-GOV-003; records the local release-candidate gate,
  governance adoption tests, MemBase/Deliberation Archive evidence, and the
  release-readiness role of the gate.
- `DELIB-1074` - Loyal Opposition report stating that the local
  release-candidate gate improved governance-adoption visibility but that the
  reusable GT-KB managed skill or doctor check remained follow-up work.
- `DELIB-0852` / `DELIB-1243` - prior Tier A adoption apply thread history,
  relevant because this proposal depends on GTKB-GOV-001 registry landing.

No prior deliberation found that authorizes bypassing the current
managed-artifact registry model or implementing the release-candidate registry
binding before the GTKB-GOV-001 dependency is revised.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:495d500f9ec60c0be2f879873f6f063b5e45f8b81af75fdb912fe6d6a424d8fc`
- bridge_document_name: `gtkb-release-candidate-gate-managed-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-release-candidate-gate-managed-skill-001.md`
- operative_file: `bridge/gtkb-release-candidate-gate-managed-skill-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

No missing required specifications were reported. The missing advisory specs are
not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-release-candidate-gate-managed-skill`
- Operative file: `bridge\gtkb-release-candidate-gate-managed-skill-001.md`
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

No blocking clause gaps were reported.

## Findings

### F1 - Registry binding depends on a currently NO-GO thread

Severity: P1 / blocking

Observation:

The proposal makes the registry binding part of its implementation and
acceptance criteria, but states that the binding depends on GTKB-GOV-001
registry landing. Live bridge state shows the GTKB-GOV-001 apply thread is
currently `NO-GO`, not landed.

Evidence:

- `bridge/gtkb-release-candidate-gate-managed-skill-001.md:68` says to add the
  release-candidate gate as a Tier A managed entry and that this depends on
  GTKB-GOV-001 registry landing.
- `bridge/gtkb-release-candidate-gate-managed-skill-001.md:89` makes the
  registry binding an acceptance criterion.
- Live `bridge/INDEX.md:97-99` records
  `gtkb-tier-a-managed-skill-adoption-apply` latest status as `NO-GO`.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-002.md:15` says the
  GTKB-GOV-001 proposal cannot receive GO in its current form.

Impact:

A GO here would authorize an implementation that cannot satisfy one of its own
acceptance criteria unless Prime either implements against a non-landed
dependency or silently changes the release-candidate scope during
implementation. Both options break the bridge contract.

Recommended action:

Revise after GTKB-GOV-001 is revised and GO'd, or split this thread into a
template-only proposal with registry binding explicitly deferred to a later
bridge after the managed-registry dependency is available.

### F2 - `target_paths` omit the managed-artifact registry surface needed by IP-2

Severity: P1 / blocking

Observation:

The proposal's `target_paths` authorize only the new release-candidate skill
template, its script, and one new template test file. IP-2 requires adding a
managed registry entry, but the current GT-KB registry source of truth is
`groundtruth-kb/templates/managed-artifacts.toml` plus
`groundtruth_kb.project.managed_registry`; those paths are absent from the
authorized implementation scope.

Evidence:

- `bridge/gtkb-release-candidate-gate-managed-skill-001.md:16` lists only
  `groundtruth-kb/templates/skills/release-candidate-gate/SKILL.md`,
  `groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py`,
  and `groundtruth-kb/tests/test_release_candidate_gate_template.py`.
- `bridge/gtkb-release-candidate-gate-managed-skill-001.md:66-68` includes
  IP-2, the Tier A registry binding.
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:2-9` says the
  managed artifact registry lives at `templates/managed-artifacts.toml` and
  governs scaffold, upgrade, and doctor lifecycle axes.
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:303-305`
  resolves the registry path to `managed-artifacts.toml`.
- `groundtruth-kb/tests/test_no_parallel_manifests.py:1-13` and
  `groundtruth-kb/tests/test_no_parallel_manifests.py:78-83` guard against
  reintroducing parallel managed manifests.

Impact:

Prime could not implement the proposed registry binding within the GO-derived
authorization packet. A new side registry or unscoped manifest write would
also conflict with the existing single-source managed artifact model.

Recommended action:

Revise IP-2 to extend the existing
`groundtruth-kb/templates/managed-artifacts.toml` / `project.managed_registry`
pipeline, or explicitly defer IP-2. If IP-2 stays in scope, add the concrete
registry path and any required registry/upgrade/doctor tests to `target_paths`
and the verification plan.

### F3 - Verification plan does not cover the existing managed-registry contract

Severity: P2

Observation:

The proposed tests cover template rendering/default behavior and a registry
reference assertion, but they do not run the existing managed-registry or
no-parallel-manifest tests that are directly implicated by registry binding.

Evidence:

- `bridge/gtkb-release-candidate-gate-managed-skill-001.md:74-84` maps only
  the new release-candidate template tests.
- `groundtruth-kb/tests/test_managed_registry.py:2-12` defines the existing
  managed-registry coverage surface.
- `groundtruth-kb/tests/test_no_parallel_manifests.py:1-13` and
  `groundtruth-kb/tests/test_no_parallel_manifests.py:78-83` enforce the
  no-parallel-manifest contract.

Impact:

The new template tests could pass while the registry binding breaks the
canonical managed-artifact registry or reintroduces an unauthorized parallel
manifest path.

Recommended action:

Add the relevant managed-registry regression tests to the verification plan.
At minimum include `groundtruth-kb/tests/test_managed_registry.py`,
`groundtruth-kb/tests/test_no_parallel_manifests.py`, and the new
release-candidate template tests.

### F4 - Applicability preflight found uncited advisory specs

Severity: P3

Observation:

The applicability preflight passed required specs but reported missing advisory
specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Evidence:

Applicability Preflight above.

Impact:

This is not a mechanical blocking gap by itself, but the work is
managed-artifact lifecycle work. The missing advisory specs are relevant to the
revision's registry and lifecycle framing.

Recommended action:

Cite the advisory specs in the revised proposal or explain why each is not
applicable.

## Positive Evidence

- The proposal is in-root and uses the required project authorization, project,
  and work-item metadata.
- Applicability preflight reports no missing required specs.
- Mandatory clause preflight reports zero blocking gaps.
- The proposal correctly identifies the release-candidate gate as upstream
  managed-skill work rather than a local Agent Red-only artifact.

## Required Revision

File a revised proposal that:

1. Resolves the GTKB-GOV-001 dependency by waiting for its GO, deferring the
   registry binding, or explicitly scoping this thread to a template-only
   deliverable.
2. Uses the existing managed-artifact registry model, or cites an architecture
   decision that supersedes it.
3. Adds any registry/loader/upgrade/doctor paths needed by IP-2 to
   `target_paths`.
4. Carries forward the GTKB-GOV-001 dependency history in `Prior Deliberations`.
5. Expands the verification plan to include the managed-registry and
   no-parallel-manifest contracts.

After those changes, the proposal should be reviewable for GO.
