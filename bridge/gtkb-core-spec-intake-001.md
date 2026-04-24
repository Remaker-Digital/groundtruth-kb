NEW

# GT-KB Core Specification Intake - Phase 0 Governance And Compatibility Proposal

**Status:** NEW
**Author:** Prime Builder (Codex)
**Date:** 2026-04-22
**Standing backlog:** `GTKB-CORE-001 - Make core application specification intake default GT-KB behavior`
**Plan sources:**
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-BASELINE-EVALUATION-2026-04-22.md`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CORE-SPEC-INTAKE-IMPLEMENTATION-PLAN-2026-04-22.md`

## Requested Verdict

GO for Phase 0 scope, or NO-GO with specific required revisions.

This is a governance and compatibility proposal only. It does not request
implementation approval for GT-KB package code yet, and it does not mutate
formal SPEC, ADR, DCL, or Deliberation Archive records.

## Claim

GT-KB should add a default-on, opt-out core application specification intake
loop for new projects. The feature should ask one missing baseline question at
a time after initialization and across session starts until persisted evidence
shows every required core slot is owner-stated or explicitly not applicable.

Phase 0 should authorize the governed workstream shape and compatibility
constraints before code changes begin.

## Evidence

### Standing backlog authority

`memory/work_list.md` records `GTKB-CORE-001` as TOP priority. The backlog entry
states that the owner directed GT-KB to use Agent Red specifications as the
worked example for reusable baseline requirements, then repeatedly prompt for
missing input and clarity after initialization until those core specifications
exist. It also states that prompting must cease once the core specifications are
complete.

The same backlog entry records the target outcome:

- a persisted core application specification intake loop
- default active behavior for newly initialized projects
- an explicit opt-out for automation or unusual cases
- one missing core-spec question at a time
- persisted owner-stated provenance or confirmation-needed status
- continuation across sessions while slots remain missing, inferred, or unclear
- stop condition when every required slot is owner-stated or explicitly not
  applicable

### Current behavior gap

The baseline evaluation and implementation plan both confirm this behavior is
not mechanically present today:

- `gt project init` does not ask core application specification questions.
- `ScaffoldOptions.spec_scaffold` defaults to `None`.
- `scaffold_project()` only inserts scaffold specs when `spec_scaffold` is
  explicitly supplied.
- the current scaffold generator covers minimal/full governance,
  infrastructure, AI, and compliance phases, but not a persisted core
  application spec state machine.

### Existing enabling work

The related `/gtkb-spec-intake` skill has already been VERIFIED in
`bridge/gtkb-skill-spec-intake-006.md`. That skill establishes a
confirm-before-mutate intake path and changed-by provenance suitable for later
core-spec answer capture. This proposal does not reopen that thread; it treats
it as an enabling primitive.

## Proposed Core Slot Catalog

Phase 1 should define a package-level catalog with stable handles, required
fields, deterministic prompt text, and first-class not-applicable semantics:

| Handle | Required baseline |
|---|---|
| `core-identity` | development name and one-sentence product description |
| `core-app-type` | application type and delivery surface |
| `core-tenancy` | single-tenant or multi-tenant; provider/admin tool requirement |
| `core-users` | single-user or multi-user; launch roles |
| `core-data` | data classes processed or stored |
| `core-compliance` | GDPR, HIPAA, PCI-DSS, SOC 2, residency, retention, deletion, audit |
| `core-security` | auth, MFA, RBAC, encryption, audit logging, tenant isolation, key management, threat model |
| `core-reliability` | uptime, zero-downtime deployment, backup/restore, RTO/RPO, rate limits, failover, health checks |
| `core-integrations` | payment, commerce, email, identity, AI/LLM, webhooks, external systems |
| `core-ai` | AI usage, human review, privacy, logging, model/provider constraints |
| `core-operations` | environments, CI, release, rollback, monitoring |
| `core-non-goals` | explicit first-release exclusions |

## Proposed State Model

The evaluator should be read-only and derive completion from persisted MemBase
evidence rather than session memory.

Allowed slot states:

- `missing`: no current spec, decision, or explicit not-applicable record exists
- `inferred`: a generated or inferred candidate exists, but the owner has not
  confirmed it
- `needs_clarity`: some answer exists, but required fields or quality checks are
  incomplete
- `stated`: the owner confirmed the requirement and current persisted evidence
  has owner-stated authority
- `not_applicable`: the owner explicitly marked the slot out of scope

Prompting continues while any required slot is `missing`, `inferred`, or
`needs_clarity`.

Prompting stops when every required slot is `stated` or `not_applicable`.

## Compatibility Policy

Recommended Phase 0 policy:

1. New projects are enrolled in core-spec prompting by default.
2. Automation and unusual projects can opt out with a deliberate flag or config
   setting, for example `--no-core-spec-prompts`.
3. Non-interactive and JSON-safe command paths must not emit interactive
   prompts.
4. Existing `minimal` and `full` spec scaffold behavior remains
   backward-compatible unless a later formal decision explicitly changes it.
5. Generated or inferred core candidates do not count as complete until the
   owner confirms them or marks the slot not applicable.
6. Direct formal artifact mutation remains gated by the normal Agent Red and
   GT-KB approval rules.

## Proposed Formal Artifact Candidates

If this Phase 0 proposal receives GO, the next owner-facing step should request
approval to create or update the following governed artifacts in the appropriate
GT-KB artifact store:

- `SPEC-CORE-INTAKE-001`: GT-KB prompts for missing core application
  specifications after project initialization.
- `SPEC-CORE-INTAKE-002`: Core specification prompting ceases once all core
  slots are owner-stated or explicitly not applicable.
- `ADR-CORE-INTAKE-001`: Core spec completion is derived from persisted MemBase
  evidence, not session memory.
- `DCL-CORE-INTAKE-001`: Existing scaffold profiles remain
  backward-compatible unless core intake is explicitly enabled or separately
  approved as default behavior.

This proposal does not itself create those records.

## Proposed Multi-Phase Implementation Plan

### Phase 1 - Core slot catalog

Add stable package-level slot definitions, handles, required fields, prompt
text, and not-applicable semantics.

Exit criteria:

- catalog is importable
- tests prove slot handle stability and prompt text shape
- existing scaffold tests remain compatible

### Phase 2 - Completion evaluator

Add a read-only evaluator that inspects current specifications and linked
decision/not-applicable evidence by stable handle or tag.

Exit criteria:

- fresh database reports missing slots
- inferred specs do not suppress prompts
- owner-stated evidence suppresses prompts for its slot
- not-applicable evidence suppresses prompts for its slot
- all-complete state suppresses all prompts

### Phase 3 - CLI surface

Add deterministic commands for tests, hooks, and humans:

- `gt core-specs status`
- `gt core-specs next-question`
- `gt core-specs answer <slot>` or equivalent governed intake helper

Exit criteria:

- CLI tests cover missing, partial, inferred, not-applicable, and complete
  states
- output is stable enough for session-start hooks to consume
- non-interactive paths have explicit no-prompt behavior

### Phase 4 - Project init, doctor, startup, dashboard

Wire the behavior into:

- `gt project init`
- `gt project doctor`
- session-start hook reporting
- dashboard/startup report signal

Exit criteria:

- fresh project initialization surfaces the first core question
- doctor reports incomplete core specs
- startup repeats the next missing question without overriding a concrete owner
  task
- startup stops after all slots are complete

### Phase 5 - Documentation and adoption evidence

Update CLI reference, bootstrap docs, user journey, specification method docs,
and release notes. Add clean-adopter verification.

Exit criteria:

- docs match behavior
- GT-KB tests pass
- Agent Red standing backlog/dashboard evidence shows the workstream state

## Verification Requirements For Later Implementation

Use GT-KB repo-native checks:

```powershell
python -m pytest tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
python -m pytest tests/test_cli.py tests/test_doctor.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
python -m mypy --strict src tests
```

Add feature-specific tests once file names exist, likely:

```powershell
python -m pytest tests/test_core_specs.py tests/test_cli_core_specs.py -q --tb=short
```

## Review Questions For Loyal Opposition

1. Is the proposed slot catalog sufficiently small and stable for a default
   new-project baseline?
2. Is default-on with an explicit opt-out compatible with the existing scaffold
   and non-interactive workflow guarantees?
3. Is the persisted-evidence state model adequate to prevent both repeated
   prompting and premature prompt suppression?
4. Are the formal artifact candidates sufficient for Phase 0 governance, or is
   another SPEC/ADR/DCL needed before implementation?

## Non-Scope

- No GT-KB package code changes in this proposal.
- No formal SPEC, ADR, DCL, or Deliberation Archive mutation in this proposal.
- No Agent Red release-gate or production deployment changes.
- No changes to the already VERIFIED `/gtkb-spec-intake` skill.

## Requested GO Conditions

If Loyal Opposition returns GO, implementation should still wait until the
formal artifact approval path is either approved or explicitly deferred by the
owner. A GO should authorize only the Phase 0 workstream shape and the first
implementation bridge for Phase 1 catalog/evaluator work.
