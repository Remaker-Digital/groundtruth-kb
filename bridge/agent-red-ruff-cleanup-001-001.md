NEW

# Implementation Proposal - AGENT-RED-RUFF-CLEANUP-001: Application-Side Ruff Cleanup

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Application release-hardening proposal
**Risk tier:** Medium-high (large mechanical lint cleanup across Agent Red product code; no GT-KB platform release behavior)
**Backlog item:** `AGENT-RED-RUFF-CLEANUP-001`

---

## Background

Slice 8 narrowed GT-KB `v0.7.0-rc1` ruff cleanup to `groundtruth-kb/` only.
That left 1,943 ruff issues in Agent Red product-code surfaces, recorded as a
separate application-side work item. This proposal files the governed cleanup
scope; it does not run ruff fixes or edit Agent Red files before `GO`.

Agent Red is a separate project. This proposal is a GT-KB bridge/control
artifact only. Actual Agent Red source edits require the implementation phase
to operate against the correct Agent Red work subject/repository and must not
treat Agent Red files as live GT-KB artifacts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  all known governing sources for the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must map
  lint/test verification back to the cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 35 of
  `memory/work_list.md` is the work authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `.claude/rules/project-root-boundary.md`, and
  `.claude/rules/canonical-terminology.md` - GT-KB and Agent Red must remain
  separate projects; Agent Red is external/application work unless Mike
  explicitly declares it active.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the cleanup must produce durable
  evidence and clear waiver/deferral states.
- `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` - owner decision that
  GT-KB rc1 only required ruff-clean `groundtruth-kb/`, leaving Agent Red ruff
  cleanup as separate work.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "Agent Red ruff cleanup application-side ruff issues Slice 8 B2 narrowing" --limit 8
```

Relevant result: `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`.
Older ruff cleanup reviews (`DELIB-1301`, `DELIB-1302`) are precedent only.

## Proposed Scope

1. Reproduce the current ruff baseline against the Agent Red application
   surface, preserving the original distribution:
   - 1,943 total issues observed in row 35.
   - 1,653 auto-fixable.
   - 290 requiring manual judgment.
2. Phase A: apply safe mechanical fixes with `ruff check . --fix` on the
   Agent Red work subject only.
3. Review the mechanical diff before any commit, especially F541 changes in
   tests where f-string removal can obscure intended interpolation.
4. Phase B: manually triage remaining E402, B007, F841, and similar findings.
5. Run targeted and broad Agent Red tests appropriate to the changed surface.
6. File an implementation report with before/after ruff counts and residual
   waivers, if any.

## Acceptance Criteria

- Agent Red product-code ruff count is reduced to zero or every remaining item
  has an explicit governed waiver.
- GT-KB platform package files under `groundtruth-kb/` are not changed as part
  of this application cleanup.
- No Agent Red work is performed against `E:\Claude-Playground`.
- Mechanical and manual changes are separated clearly in the report.
- The implementation report includes ruff command output and test evidence.

## Test Plan

Suggested commands, to be run in the Agent Red work subject/repository selected
for implementation:

```powershell
python -m ruff check . --statistics
python -m ruff check . --fix
python -m ruff check .
python -m pytest -q --tb=short
```

If full pytest is too slow or blocked, the implementation report must explain
the targeted suite selection and residual risk.

## Out Of Scope

- GT-KB platform ruff changes.
- Release tagging or PyPI publication.
- Broad refactors not required by lint.
- Credential or deployment changes.

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO` using a two-phase cleanup: mechanical
auto-fixes first, manual fixes second.

