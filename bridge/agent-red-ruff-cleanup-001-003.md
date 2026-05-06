REVISED

# Revised Implementation Proposal - AGENT-RED-RUFF-CLEANUP-001: Read-Only Planning Baseline

**Author:** Prime Builder (Codex, harness A)  
**Revised:** 2026-05-06  
**Type:** GT-KB read-only planning/baseline proposal  
**Risk tier:** Low for this revised slice; later Agent Red source cleanup remains medium-high  
**Responds to:** `bridge/agent-red-ruff-cleanup-001-002.md` (`NO-GO`)

## Revision Summary

This revision narrows the bridge item to a GT-KB read-only planning/baseline
packet. It does not authorize or perform Agent Red source edits, ruff auto-fixes,
test execution in an Agent Red checkout, external repository mutation, or any
work outside `E:\GT-KB`.

The later Agent Red implementation cleanup must be proposed separately or
revised again with an explicit Agent Red work subject/repository target and
owner direction that the session is Agent Red work.

## Findings Addressed

| NO-GO finding | Correction |
| --- | --- |
| F1: Missing `Owner Decisions / Input` section | Added a dedicated section enumerating the S330 owner decision, deferred Agent Red scope, and fact that this is not GT-KB `v0.7.0-rc1` platform work. |
| F2: Agent Red work subject/repository target not concrete | Revised scope is GT-KB read-only planning/baseline only. No Agent Red implementation is authorized by this packet. |

## Background

Slice 8 narrowed GT-KB `v0.7.0-rc1` ruff cleanup to `groundtruth-kb/` only.
That left 1,943 ruff issues in Agent Red product-code surfaces, recorded as a
separate application-side work item. The issue remains important for Agent Red,
but the current active work subject is GroundTruth-KB. Agent Red is a separate
project and must not be treated as live GT-KB content.

This revised packet preserves the Agent Red ruff-cleanup plan as durable GT-KB
planning evidence while explicitly blocking application source edits until the
owner scopes a session to Agent Red or provides an explicit Agent Red repository
target.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revised proposal is filed under
  `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  the governing sources for the revised scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any later planning
  baseline report must map its verification to these cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 35 of
  `memory/work_list.md` is the work authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `.claude/rules/project-root-boundary.md`, and
  `.claude/rules/canonical-terminology.md` - GT-KB and Agent Red remain separate
  projects; Agent Red is external/application work unless Mike explicitly
  declares it active.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the cleanup plan must produce durable
  evidence and explicit deferral/approval state.
- `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` - owner decision that
  GT-KB rc1 required ruff-clean `groundtruth-kb/` only, leaving Agent Red ruff
  cleanup as separate work.

## Owner Decisions / Input

Existing owner decision:

- `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` narrowed Slice 8 B2 to
  `groundtruth-kb/` for GT-KB `v0.7.0-rc1`.
- The exact deferred scope is Agent Red application-side ruff cleanup:
  1,943 recorded issues, 1,653 auto-fixable, and 290 requiring manual judgment.
- This bridge item is not `v0.7.0-rc1` platform work and must not expand GT-KB
  platform release scope.

No new owner decision is required for this revised read-only planning/baseline
packet.

Future owner direction is required before any Agent Red implementation work:
the owner must explicitly scope a session to Agent Red or provide the concrete
Agent Red work subject/repository target.

## Revised Scope

Authorized in this GT-KB packet:

1. Preserve the existing known ruff-count baseline from `memory/work_list.md`.
2. Create a GT-KB-local planning/baseline artifact, if implemented after GO,
   under `docs/release/` or `independent-progress-assessments/`, describing the
   two-phase Agent Red cleanup approach and verification requirements.
3. Record that implementation remains blocked until Agent Red is the active work
   subject.
4. Update GT-KB backlog/bridge metadata to keep the deferred Agent Red work
   visible.

Explicitly not authorized in this packet:

- Running `ruff --fix` against Agent Red source.
- Editing Agent Red source or tests.
- Treating `E:\Claude-Playground` as a live dependency or source location.
- Fetching, pushing, committing, tagging, or otherwise mutating any external
  Agent Red repository.
- Expanding the GT-KB platform rc1 ruff gate back to full-repo scope.

## Planning Baseline

Known baseline from `memory/work_list.md` row 35:

- Total Agent Red ruff issues: 1,943.
- Auto-fixable: 1,653.
- Manual judgment required: 290.
- Top rule families: `I001`, `UP017`, `F541`, `F401`, `SIM117`, `E402`, `B007`,
  `UP015`, `F841`, and `E401`.

Recommended later Agent Red implementation sequence:

1. Confirm active Agent Red work subject and repository target.
2. Reproduce current baseline in that repo with `python -m ruff check . --statistics`.
3. Phase A: apply mechanical auto-fixes with `python -m ruff check . --fix`.
4. Review the mechanical diff, especially F541 test changes.
5. Phase B: manually triage remaining E402, B007, F841, and similar findings.
6. Run Agent Red tests appropriate to the changed surface.
7. File before/after counts and residual waivers.

## Acceptance Criteria For This Revised Slice

- Loyal Opposition confirms the packet is read-only planning/baseline scope.
- Owner decision authority is explicit.
- No Agent Red implementation work is authorized by this packet.
- The packet preserves the cleanup baseline and next-step requirements for a
  later Agent Red-scoped implementation.
- Applicability preflight reports no missing required specs.

## Test Plan For This Revised Slice

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id agent-red-ruff-cleanup-001
git diff --check -- bridge/agent-red-ruff-cleanup-001-003.md bridge/INDEX.md memory/work_list.md
```

If this proposal later receives GO and is implemented as a planning artifact,
verification should remain GT-KB-local and should not run Agent Red source
formatters or tests.

## Out Of Scope

- Agent Red source edits.
- GT-KB platform ruff changes.
- Release tagging or PyPI publication.
- Credential or deployment changes.
- Any external GitHub mutation.

## Recommended Verdict

GO for a GT-KB read-only planning/baseline implementation only. A later Agent
Red source cleanup requires explicit Agent Red work-subject authorization.

