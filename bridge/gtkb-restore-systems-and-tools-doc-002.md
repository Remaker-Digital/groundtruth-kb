GO

bridge_kind: lo_verdict
Document: gtkb-restore-systems-and-tools-doc
Version: 002
Responds to: bridge/gtkb-restore-systems-and-tools-doc-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# Loyal Opposition Verdict - Restore Systems-and-Tools Companion Doc

## Claim

`bridge/gtkb-restore-systems-and-tools-doc-001.md` is ready for `GO`.

This verdict approves only restoring `docs/gtkb-systems-and-tools.md` to the
in-root platform docs tree and strengthening the named regression guard in
`platform_tests/scripts/test_system_interface_map.py`. It does not authorize
editing `config/agent-control/system-interface-map.toml`,
`scripts/resolve_system_interface.py`, `groundtruth-kb/tests/test_operating_state.py`,
or the Agent Red copy at `applications/Agent_Red/docs/gtkb-systems-and-tools.md`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Live bridge state before filing this verdict: `bridge/INDEX.md` listed
  `gtkb-restore-systems-and-tools-doc` latest status as
  `NEW: bridge/gtkb-restore-systems-and-tools-doc-001.md`, actionable for Loyal
  Opposition.

## Prior Deliberations

Required Deliberation Archive searches were run with the repo venv `gt.exe` for:

- `WI-3487 systems tools doc restore`
- `gtkb systems terminology map systems-and-tools human-readable companion`

The text searches returned no additional matching rows. Exact read of
`DELIB-2548` confirmed the S381 owner decision authorizes WI-3487 through the
normal bridge path. The proposal-cited prior bridge thread
`bridge/gtkb-systems-terminology-map-001-003.md` was considered as prior
bridge evidence for the original in-root companion-document creation.

No prior deliberation found in this review rejected restoring the platform
companion document to `docs/gtkb-systems-and-tools.md`.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-restore-systems-and-tools-doc
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:d8d7a90e39c64a5efe17804cb36fc809003d0cf67b8900db9e4aa28ea70425cc`
- bridge_document_name: `gtkb-restore-systems-and-tools-doc`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-restore-systems-and-tools-doc-001.md`
- operative_file: `bridge/gtkb-restore-systems-and-tools-doc-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory spec is not blocking in this review. The required specs
are present and the preflight passed.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-restore-systems-and-tools-doc
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-restore-systems-and-tools-doc`
- Operative file: `bridge\gtkb-restore-systems-and-tools-doc-001.md`
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

## Review Evidence

- `git show --summary -M --oneline 350b2754 -- docs/gtkb-systems-and-tools.md`
  confirms commit `350b2754` created `docs/gtkb-systems-and-tools.md`.
- `git show --summary -M --oneline 687f4707 -- docs/gtkb-systems-and-tools.md applications/Agent_Red/docs/gtkb-systems-and-tools.md`
  confirms commit `687f4707` renamed
  `{docs => applications/Agent_Red/docs}/gtkb-systems-and-tools.md (100%)`.
- Current filesystem inspection confirmed `docs/gtkb-systems-and-tools.md` is
  absent and `applications/Agent_Red/docs/gtkb-systems-and-tools.md` is present.
- `config/agent-control/system-interface-map.toml:3` still declares
  `human_companion = "docs/gtkb-systems-and-tools.md"`.
- `platform_tests/scripts/test_system_interface_map.py:73`,
  `groundtruth-kb/tests/test_operating_state.py:151`, and
  `scripts/resolve_system_interface.py:156-163` still target or compute the
  in-root companion path.
- Current targeted test run with the repo venv confirms the defect:
  `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_system_interface_map.py -q --tb=short`
  produced `2 failed, 6 passed`, with `FileNotFoundError` for the in-root doc
  and `human_companion_exists is False`.
- Read-only PAUTH inspection confirmed
  `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001` is `active`, cites
  `DELIB-2548`, includes `WI-3487`, allows
  `["source", "design_documentation", "test_addition"]`, and is under
  `PROJECT-GTKB-RELIABILITY-FIXES`.

## Findings

No blocking findings.

## Non-Blocking Note

The proposal text says the WI-3487 PAUTH forbids `deploy`, `git_push_force`,
and `spec_deletion`. The live PAUTH row reviewed here has
`forbidden_operations = NULL`. This does not block `GO` because the approved
bridge `target_paths`, positive mutation classes, and normal governance gates
still exclude those operations from this implementation. Prime Builder should
not cite `forbidden_operations` as a populated PAUTH field in the
post-implementation report unless the MemBase authorization row has been
updated through the proper governed path.

## GO Conditions

Prime Builder may implement this slice within the filed `target_paths` only.

Implementation report expectations:

- Carry forward the linked specifications from the proposal.
- Include exact command evidence for
  `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_system_interface_map.py -q --tb=short`,
  `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts/resolve_system_interface.py --status --json`,
  the bridge applicability preflight, the ADR/DCL clause preflight,
  `ruff check platform_tests/scripts/test_system_interface_map.py`, and
  `ruff format --check platform_tests/scripts/test_system_interface_map.py`.
- Restore the in-root doc content without repointing the platform map at the
  Agent Red copy.
- Leave `applications/Agent_Red/docs/gtkb-systems-and-tools.md` untouched.
- Do not edit `config/agent-control/system-interface-map.toml`,
  `scripts/resolve_system_interface.py`, or
  `groundtruth-kb/tests/test_operating_state.py` in this slice.

## Opportunity Radar

No separate token-savings or deterministic-service opportunity emerged. The
proposal is already the minimal restoration of a displaced platform artifact.

## Verdict

GO.
