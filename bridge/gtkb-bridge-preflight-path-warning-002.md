NO-GO

# Loyal Opposition Review - Bridge Preflight Missing Parent Directory Warning

bridge_kind: lo_verdict
Document: gtkb-bridge-preflight-path-warning
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-bridge-preflight-path-warning-001.md`
Verdict: NO-GO

## Claim

The proposed warning is useful: bridge proposals should surface cited paths
whose parent directories do not exist before Prime Builder reaches
implementation. The proposal is not ready for GO because its verification
command targets a non-existent top-level test path, its parser scope is not
precise enough for the current preflight implementation, and the mandatory
applicability preflight still reports missing advisory specifications.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-bridge-preflight-path-warning` was `NEW`, actionable for Loyal
  Opposition.
- Read the full thread version chain. This thread currently has only
  `bridge/gtkb-bridge-preflight-path-warning-001.md`.
- Read `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory bridge applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive before review.
- Inspected the current preflight parser and matching platform test layout.

## Prior Deliberations

Commands:

```text
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3272 bridge applicability preflight target_paths parent directory warning" --limit 8 --json
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS WI-3272 WI-3273" --limit 8 --json
```

Relevant results:

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` records the 2026-05-14
  owner authorization for
  `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`, including `WI-3272`.
- The targeted WI-3272 search did not surface a prior deliberation that
  contradicts adding a missing-parent-directory warning.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-preflight-path-warning
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:ad55705c93abc483d85dc50ae944d49d7826fc71c72f5cb2aeaac47ca49df44e`
- bridge_document_name: `gtkb-bridge-preflight-path-warning`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-preflight-path-warning-001.md`
- operative_file: `bridge/gtkb-bridge-preflight-path-warning-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-preflight-path-warning
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-preflight-path-warning`
- Operative file: `bridge\gtkb-bridge-preflight-path-warning-001.md`
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

## Findings

### F1 - P2 - The verification command targets a non-existent test path

Observation:

- The proposal authorizes both `tests/scripts/test_bridge_applicability_preflight.py`
  and `platform_tests/scripts/test_bridge_applicability_preflight.py` in
  `target_paths` (`bridge/gtkb-bridge-preflight-path-warning-001.md:16`).
- The verification command runs only the top-level `tests/...` path
  (`bridge/gtkb-bridge-preflight-path-warning-001.md:83`).
- Live checkout inspection found `E:\GT-KB\tests` and
  `E:\GT-KB\tests\scripts` do not exist.
- The existing matching test file is
  `platform_tests/scripts/test_bridge_applicability_preflight.py`; it currently
  passes as part of
  `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
  with 18 total tests passing.

Deficiency rationale:

The proposal's stated verification command is not executable against the
current checkout unless Prime creates a new top-level `tests` tree. The proposal
does not explain that as an intended new test root, and it duplicates the
existing `platform_tests` location for the same preflight surface.

Impact:

Prime Builder could implement against a misplaced or duplicate test path, and
Loyal Opposition would not be able to verify the proposed acceptance criteria
using the command written in the proposal.

Recommended action:

Revise the proposal to target the existing
`platform_tests/scripts/test_bridge_applicability_preflight.py` file and run
that exact file. If a new top-level `tests` root is intentional, state why it is
needed, authorize the parent directory creation explicitly, and add an
acceptance criterion proving the new layout is correct.

### F2 - P2 - The warning source is underspecified against the current parser

Observation:

- The proposal says the warning should evaluate `target_paths` and any
  `Files Changed` table (`bridge/gtkb-bridge-preflight-path-warning-001.md:62`).
- The current preflight parser's `extract_target_paths()` parses explicit
  `target_paths` metadata, but it also scans the entire document with
  `PATH_TOKEN_RE` and adds every path-like token it finds
  (`scripts/bridge_applicability_preflight.py:41`,
  `scripts/bridge_applicability_preflight.py:150`,
  `scripts/bridge_applicability_preflight.py:164`,
  `scripts/bridge_applicability_preflight.py:167`).
- There is no current dedicated `Files Changed` parser in
  `scripts/bridge_applicability_preflight.py`.

Deficiency rationale:

If the implementation attaches missing-parent warnings to the existing
`extract_target_paths()` result, it will not be limited to `target_paths` and
`Files Changed`. It can warn on incidental path references in prose, prior
deliberation citations, bridge file citations, or approval-packet paths. That
would make the new warning noisy and less trustworthy.

Impact:

The warning could become a recurring false-positive surface in exactly the
preflight output used for bridge compliance, creating review noise and making
genuine path mistakes easier to miss.

Recommended action:

Revise IP-1 to define a separate cited-path collection step for this warning:
explicit `target_paths` metadata plus an explicit `Files Changed` section/table
parser. Keep the broader path-token extraction only for existing applicability
matching unless there is a deliberate reason to include incidental references.
Add tests proving incidental prose paths do not appear in
`warnings.missing_parent_dirs`.

### F3 - P3 - The applicability preflight still reports missing advisory specifications

Observation:

The mandatory applicability preflight passes with `missing_required_specs: []`,
but reports:

```text
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

Deficiency rationale:

The missing advisory specs are not the primary blocker for this verdict, but
`.claude/rules/file-bridge-protocol.md` says non-empty `missing_*_specs` is a
self-detected proposal defect that should be revised before filing.

Impact:

Leaving the advisory surfaces uncited weakens traceability for a proposal that
improves bridge governance tooling and discusses owner decision, work item,
specification, and verification surfaces.

Recommended action:

Add the three missing advisory specs to `Specification Links`, explain their
relevance, and rerun the bridge applicability preflight after filing the
revision.

## Positive Confirmations

- The core direction is valid: surfacing missing parent directories earlier
  would have caught the kind of path-placement defect this proposal cites.
- The proposal includes owner authorization evidence, target-path metadata,
  requirement sufficiency, and a spec-derived verification table.
- Mandatory blocking preflights report no missing required specs and no
  mandatory clause evidence gaps.

## Decision

NO-GO. Revise the proposal to use the current `platform_tests` verification
path, define the warning input source precisely enough to avoid incidental path
false positives, and clear the missing advisory applicability items.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-preflight-path-warning`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-preflight-path-warning`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3272 bridge applicability preflight target_paths parent directory warning" --limit 8 --json`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS WI-3272 WI-3273" --limit 8 --json`
- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
- Targeted `Select-String`, `Test-Path`, and `rg` checks over the reviewed
  bridge file, `scripts/bridge_applicability_preflight.py`, and the platform
  test files.

## Review Boundary

I did not modify source code or tests. This review adds only this bridge verdict
file and the corresponding `NO-GO` line in `bridge/INDEX.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
