NO-GO

# Loyal Opposition Review: gtkb-fab-03-membase-backup-001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition, harness A
**Date:** 2026-06-11

## Review Scope

Reviewed the full bridge thread:

- `bridge/gtkb-fab-03-membase-backup-001.md`

Same-session self-review guard: this Codex LO session did not author the Prime
Builder proposal. The proposal was authored by Prime Builder harness B,
session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

Dependency and precedence check: after FAB-02 GO, FAB-04 NO-GO, and FAB-01 GO,
FAB-03 is the next oldest LO-actionable proposal. It is a backup
operationalization proposal, so the out-of-root snapshot-output authority must
be explicit before implementation starts.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:113452c7de1c740d62a051fd7b983db7340803a546f6cdf0e748d3ee1895c587`
- bridge_document_name: `gtkb-fab-03-membase-backup`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-03-membase-backup-001.md`
- operative_file: `bridge/gtkb-fab-03-membase-backup-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

## Clause Applicability Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-03-membase-backup`
- Operative file: `bridge\gtkb-fab-03-membase-backup-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Authority Evidence

- `groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-FAB03-REMEDIATION-20260610`
  returned version 1 with outcome `owner_decision`, work item `WI-4415`, and
  the staged-backup decisions cited by the proposal.
- `PAUTH-FAB03-20260610` is active for `PROJECT-FABLE-INVESTIGATION`, includes
  `WI-4415`, and allows `source`, `test_addition`, `config`,
  `repository_state`, and `docs`.
- The PAUTH forbids file-copying the live WAL `groundtruth.db` without
  `-wal`/`-shm`, writing DB snapshots onto the Drive-synced `E:` root, and
  deleting the live `groundtruth.db`.

## Findings

### FINDING-P1-001 - Out-of-root snapshot output lacks a current root-boundary exception

The proposal depends on creating, scheduling, and doctor-verifying snapshots in
`%LOCALAPPDATA%\gtkb-snapshots`, which is outside `E:\GT-KB`.

The active root-boundary rule is stricter than the proposal's rationale:

- `.claude/rules/project-root-boundary.md` says no GT-KB artifact may be
  created, read as a live dependency, updated, verified, or required from
  outside `E:\GT-KB`.
- The same rule says any proposal, review, implementation, or test that depends
  on a path outside the allowed roots is a NO-GO until revised to be
  root-contained.
- The existing `Sandbox Output Exception` covers rehearsal-class runtime output
  only, under an owner-approved manifest and an allowlist of
  `C:/temp/agent-red-rehearsal*` or `/tmp/agent-red-rehearsal*`. It does not
  cover `%LOCALAPPDATA%\gtkb-snapshots`.

The previously VERIFIED `gt db snapshot` implementation establishes the
technical snapshot command and its user-local default, but the current FAB-03
proposal operationalizes that path as scheduled platform behavior and adds a
doctor freshness check that reads it as live operational evidence. That makes
the root-boundary exception an active governance precondition, not just
background rationale.

**Impact:** If Prime implements this as written, GT-KB will have scheduled
out-of-root backup artifacts and a doctor check that verifies an out-of-root
path while the active root-boundary rule still says such dependencies are
NO-GO unless covered by an allowed exception.

**Required change:** File a REVISED proposal that does one of the following:

- adds a formal DB-snapshot/root-boundary exception to the implementation scope,
  with owner-decision evidence and tests analogous to the existing sandbox
  exception; or
- revises the backup output/doctor verification model so all active project
  dependencies remain under an allowed root.

The revision should also stop describing the existing rehearsal-only `Sandbox
Output Exception` as if it already authorizes `%LOCALAPPDATA%\gtkb-snapshots`.

## Verdict

NO-GO. The backup operationalization is directionally supported by the owner
decision and PAUTH, and the mandatory bridge preflights pass, but the proposal
needs a current root-boundary exception or a root-contained design before it can
receive GO.
