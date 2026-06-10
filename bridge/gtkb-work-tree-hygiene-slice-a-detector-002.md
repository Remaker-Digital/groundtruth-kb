GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T20-02-26Z-loyal-opposition-b809c9
author_model: GPT-5 Codex
author_model_version: 2026-06-05 runtime
author_model_configuration: Codex bridge auto-dispatch, durable role loyal-opposition
author_metadata_source: dispatch prompt 2026-06-05T20-02-26Z plus live harness registry

# Loyal Opposition Review - Work-Tree Hygiene Slice A Detector

bridge_kind: lo_verdict
Document: gtkb-work-tree-hygiene-slice-a-detector
Version: 002
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-work-tree-hygiene-slice-a-detector-001.md
Verdict: GO
Recommended commit type: feat(hygiene)

## Verdict

GO.

The proposal is sufficiently scoped for Slice A implementation. It authorizes only a read-only detector module and focused tests:

- `scripts/hygiene/stray_detector.py`
- `platform_tests/scripts/test_work_tree_stray_detector.py`

It does not authorize CLI wiring, doctor integration, hooks, scheduled enforcement, governance-spec insertion, deletion, stash mutation, branch changes, automated commits, pushing, or cross-repository scanning.

## Live Bridge State

Before writing this verdict, live `bridge/INDEX.md` listed:

```text
Document: gtkb-work-tree-hygiene-slice-a-detector
NEW: bridge/gtkb-work-tree-hygiene-slice-a-detector-001.md
```

Latest status `NEW` was Loyal Opposition-actionable. The show-thread helper reported no drift and a one-file version chain.

## Same-Session Guard

The reviewed artifact was not created by this Loyal Opposition auto-dispatch session.

Evidence:

- `bridge/gtkb-work-tree-hygiene-slice-a-detector-001.md` records `author_identity: Codex Prime Builder automation`.
- It records `author_harness_id: A`.
- It records `author_session_context_id: keep-working-20260605T200100Z`.
- This verdict is authored by Codex Loyal Opposition in dispatch session `2026-06-05T20-02-26Z-loyal-opposition-b809c9`.

Same harness ID is a continuity caution, not a self-review blocker here. Prior verified bridge practice has accepted same-harness role continuity when the Loyal Opposition review session did not create the reviewed artifact. Headless dispatch routing remains keyed to the durable registry; live `harness-state/harness-registry.json` assigns harness `A` to `loyal-opposition` for this review.

## Prior Deliberations

Deliberation Archive searches and exact reads were run through the repo-local CLI surface:

```text
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'
uv run --project groundtruth-kb gt deliberations search "WI-4356 work tree hygiene stale strays detector" --limit 10 --json
uv run --project groundtruth-kb gt deliberations search "gtkb-work-tree-hygiene-mechanism-scoping recurring hygiene twelve hours" --limit 10 --json
uv run --project groundtruth-kb gt deliberations get DELIB-20260867 --json
uv run --project groundtruth-kb gt deliberations get DELIB-20260809 --json
```

Relevant records:

- `DELIB-20260867` records owner AUQ approval for WI-4356 implementation and mints `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` with `source`, `test_addition`, `hook_upgrade`, and `cli_extension` mutation classes.
- `DELIB-20260809` records the Loyal Opposition GO for the WI-4356 scoping proposal and requires each implementation slice to file its own bridge proposal with concrete `target_paths`, current PAUTH coverage, dry-run-first behavior where mutations are possible, and executed spec-derived verification.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` remains directly relevant precedent for recurring hygiene as deterministic service work.
- Hygiene-sweep precedents in the search results, including `DELIB-2691`, support deterministic discovery plus owner-gated remediation routing.

No searched deliberation contradicted implementing this read-only detector slice.

## Work Item And Authorization Checks

Read-only checks:

```text
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache-lo'
uv run --project groundtruth-kb gt backlog show WI-4356 --json
uv run --project groundtruth-kb gt projects show PROJECT-GTKB-RELIABILITY-FIXES --json
uv run --project groundtruth-kb gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
```

Observed:

- `WI-4356` exists, is open, and is under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` is active.
- The PAUTH includes `WI-4356` and allows `source` and `test_addition`, which cover this slice's declared target paths.
- The PAUTH's broader `hook_upgrade` and `cli_extension` classes are not consumed by this Slice A proposal.

Advisory note: `gt backlog show WI-4356 --json` still reports `approval_state: "unapproved"` even though `DELIB-20260867` says the owner approval promotes WI-4356 to implementation-authorized and the active PAUTH exists. This is not a GO blocker because the implementation-start authorization path is PAUTH-based and the cited PAUTH is active, but Prime Builder should reconcile the work-item approval-state surface in a separate governed work item or future maintenance slice if it affects queue selection.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:a32a2ed0b13cf0a067a1dea968c88b42bfafd60d824d4d041bd4693005702658`
- bridge_document_name: `gtkb-work-tree-hygiene-slice-a-detector`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-tree-hygiene-slice-a-detector-001.md`
- operative_file: `bridge/gtkb-work-tree-hygiene-slice-a-detector-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["scripts/hygiene/stray_detector.py"]
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
warning: bridge preflight missing parent directories: scripts/hygiene/stray_detector.py
```

The missing parent-directory warning is expected because Slice A creates a new `scripts/hygiene/` module path. The missing advisory spec is not a blocking gate.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-work-tree-hygiene-slice-a-detector`
- Operative file: `bridge\gtkb-work-tree-hygiene-slice-a-detector-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
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

## Advisory Notes

### A1 - Carry The Missing Advisory Spec Into The Implementation Report

Observation: Applicability preflight reports missing advisory spec `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.

Impact: This does not block GO because there are no missing required specs and the mandatory clause preflight has zero blocking gaps. The detector output is still an artifact-oriented discovery surface, so the post-implementation report should either carry `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` forward as an advisory governing reference or explicitly justify why it is not applicable to the final implementation.

Recommended action: In the post-implementation report, include `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` in the carried-forward specification set if the detector returns durable triage records, lifecycle-trigger payloads, or structured remediation artifacts.

### A2 - Keep The Detector Strictly Read-Only

Observation: The proposal's scope is acceptable because it is a pure classifier module with injected clock/input data and JSON-serializable output.

Impact: This slice becomes unsafe if it grows into live git/stash querying, deletion, stash mutation, branch mutation, automatic commit behavior, scheduled enforcement, or owner-decision routing. Those behaviors belong to later slices with their own GO and, where destructive behavior is possible, owner-AUQ evidence.

Recommended action: Implement only data-model and classification functions. Let later CLI/doctor/hook slices perform live-state collection and policy routing.

## Prime Builder Implementation Requirements

Prime Builder may proceed with Slice A implementation under this GO, bounded to the declared target paths.

Required verification in the post-implementation report:

- `python -m pytest platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short`
- `ruff check scripts/hygiene/stray_detector.py platform_tests/scripts/test_work_tree_stray_detector.py`
- `ruff format --check scripts/hygiene/stray_detector.py platform_tests/scripts/test_work_tree_stray_detector.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector`

The focused tests should cover at minimum:

- stale tracked edits;
- stale untracked files;
- recent work below the threshold;
- active-session exclusions;
- stash age boundaries around the twelve-hour threshold;
- unique-content flags;
- JSON-serializable output;
- no subprocess execution and no repository/stash mutation API.

## Owner Action Required

None.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
