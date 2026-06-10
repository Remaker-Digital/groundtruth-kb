GO

# Loyal Opposition Review - Work-Tree Hygiene Mechanism Scoping

bridge_kind: lo_verdict
Document: gtkb-work-tree-hygiene-mechanism-scoping
Version: 002
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-work-tree-hygiene-mechanism-scoping-001.md
Verdict: GO

## Verdict

GO for scoping.

This approves the design direction for a recurring work-tree hygiene and stash-stray-cleanup mechanism. It does not authorize source, hook, CLI, doctor, git, stash, work-item, project, MemBase, or governance-spec mutation. Each implementation slice must file its own bridge proposal with concrete `target_paths`, current PAUTH coverage, dry-run-first behavior where mutations are possible, formal-artifact approval where required, and executed spec-derived verification before requesting VERIFIED.

## Review Boundary

The scoping boundary is acceptable because the proposal:

- sets `target_paths: []`;
- declares `requires_verification: false` for the scoping artifact itself;
- places implementation into five future slices;
- keeps automatic mutation execution out of scope by default;
- requires owner-AUQ for Slice E enforcement automation; and
- keeps cross-repository scanning out of scope.

The later implementation proposals must not treat this GO as authorization for destructive cleanup. Dropping stashes, committing another session's stale work, deleting untracked files, or enabling scheduled enforcement requires the child proposal to show exact mutation policy, rollback/recovery evidence, and owner-confirmed apply behavior.

## Prior Deliberations

Deliberation Archive searches and exact reads were run before review through the repo CLI:

```text
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt deliberations search "work tree hygiene strays WI-4356 stash cleanup" --limit 5 --json
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt deliberations search "DELIB-S312 deterministic services principle recurring hygiene" --limit 5 --json
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE --json
```

Relevant records:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` exists and directly supports moving recurring deterministic cleanup and triage plumbing into service surfaces rather than repeated AI ceremony.
- Hygiene-sweep precedents returned in search results, including `DELIB-2675`, `DELIB-2691`, and `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP`, support the pattern of deterministic discovery plus owner-gated remediation child work.
- Commit-scope and bridge-scope precedent in `DELIB-2452` reinforces that future hook/config/source mutations must not be smuggled through a scoping GO.
- No prior deliberation found in the searches contradicts creating a scoped hygiene mechanism for stale work-tree and stash triage.

## Work Item and Authorization Checks

Read-only checks:

```text
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt backlog show WI-4356 --json
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt projects show PROJECT-GTKB-RELIABILITY-FIXES --json
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'; uv run --project groundtruth-kb gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
```

Observed:

- `WI-4356` exists, is open, and is a `P2` hygiene-origin work item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers small defect/reliability fixes by active project membership, with allowed mutation classes `source`, `test_addition`, and `hook_upgrade`.
- The standing PAUTH does not by itself clearly cover all future slices named in this scoping proposal. In particular, CLI extension work and governance-spec insertion may require either a dedicated PAUTH or explicit evidence that the active project authorization accepts that mutation class.

This is not a blocker for the scoping GO because no implementation is authorized here. It is a child-slice requirement.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-mechanism-scoping
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:0b09848be3f8dd8a97e6a64398655f5f5c0338ddb546365e12a2ee06d7975f93`
- bridge_document_name: `gtkb-work-tree-hygiene-mechanism-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-tree-hygiene-mechanism-scoping-001.md`
- operative_file: `bridge/gtkb-work-tree-hygiene-mechanism-scoping-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-tree-hygiene-mechanism-scoping
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-work-tree-hygiene-mechanism-scoping`
- Operative file: `bridge\gtkb-work-tree-hygiene-mechanism-scoping-001.md`
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

## Findings

No GO-blocking findings.

### Confirmation - Deterministic Discovery Plus Owner-Gated Apply Is The Right Direction

Observation: The proposal separates read-only detection, triage classification, doctor reporting, governance insertion, and optional enforcement automation into separate slices.

Impact: That split limits blast radius. The highest-risk behavior, mutation or enforcement automation, is deferred and owner-gated.

### Confirmation - Dry-Run First Must Remain Non-Negotiable

Observation: The proposal states that the `gt hygiene strays` CLI emits actions but does not execute mutations by default.

Impact: This is essential because stash drops, stale-file commits, and cleanup of abandoned work can destroy reviewable evidence if applied incorrectly.

### Advisory - Future Slices Must Tighten Authorization Evidence

Observation: The scoping proposal says each slice files under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, but the live standing PAUTH does not obviously include every mutation class in the slice list.

Impact: A future Slice B CLI extension or Slice D governance-spec insertion could otherwise be filed under a PAUTH that lacks the needed mutation class.

Recommended action: Each future child proposal must either cite a PAUTH whose allowed mutation classes cover its exact target paths and operations, or create a dedicated PAUTH before implementation. Slice D must also carry the formal-artifact approval packet for `GOV-WORK-TREE-HYGIENE-001`.

### Advisory - Carry The Missing Advisory Spec Forward

Observation: Applicability preflight reports missing advisory spec `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

Impact: This does not block scoping GO because there are no missing required specs and the mandatory clause preflight has no blocking gaps. However, the future implementation slices affect lifecycle routing, owner-AUQ remediation, and verified governance state.

Recommended action: Future child proposals should cite `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` or explicitly justify non-applicability.

## Prime Builder Implementation Context

Future child proposals should:

- keep Slice A detector read-only with JSON fixtures for stale file, active-session, and stash age cases;
- keep Slice B CLI dry-run by default, with any `--apply` path owner-confirmed and separately tested;
- never auto-commit protected path changes;
- require owner-AUQ for any unique stash content, untracked discard, or scheduled enforcement;
- use live `bridge/INDEX.md`, live `git status`, live `git stash list`, and live active-session markers rather than cached snapshots;
- cite `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`;
- carry exact PAUTH evidence for CLI/governance/hook mutation classes; and
- include rollback/recovery steps for every destructive or potentially destructive operation.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
