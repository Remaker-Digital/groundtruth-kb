NO-GO

# Loyal Opposition Verification Review - Project-Scoped Implementation Authorization

bridge_kind: lo_verdict
Document: gtkb-project-scoped-implementation-authorization
Version: 006
Reviewer: Loyal Opposition (Codex, harness A, mode lo)
Date: 2026-05-13 UTC
Reviewed report: bridge/gtkb-project-scoped-implementation-authorization-005.md
Approved proposal: bridge/gtkb-project-scoped-implementation-authorization-003.md
Prior GO: bridge/gtkb-project-scoped-implementation-authorization-004.md
Verdict: NO-GO

## Claim Reviewed

Prime Builder reports implementation of project-scoped implementation authorization and automatic backlog intake for implementation-bearing specs. The report claims append-only project authorization storage, `gt projects` authorization commands, project authorization metadata in implementation-start packets, automatic backlog intake, deterministic project attachment, rule/skill/glossary updates, formal approval packets, and focused verification.

## Prior Deliberations

Deliberation search was run before review with these queries:

- `project scoped implementation authorization`
- `implementation authorization stale project authorization excluded specs`
- `automatic backlog intake implementation-bearing specs`

Relevant deliberations reviewed:

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - direct owner decision for bounded project authorization, automatic backlog intake, deterministic project attachment where supported, and no bridge bypass.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` - related scoped authorization pattern for specification creation.
- Prior compressed `gtkb-core-spec-intake` and `gtkb-skill-spec-intake` deliberations surfaced in search results as related spec-intake history.

`DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` explicitly rejects skipping per-proposal bridge review and requires project authorization to preserve implementation-start controls. That makes stale or narrowed project authorization state part of the verification scope.

## Verification Summary

Passing evidence:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization` passed against `bridge/gtkb-project-scoped-implementation-authorization-005.md` with no missing required or advisory specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization` passed against `bridge/gtkb-project-scoped-implementation-authorization-005.md` with zero blocking gaps.
- `python -m pytest platform_tests/scripts/test_project_authorization.py -q` passed: 1 passed.
- `python -m pytest platform_tests/groundtruth_kb/test_spec_auto_backlog.py -q` passed: 5 passed.
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q` passed: 20 passed.
- `python -m pytest platform_tests/scripts/test_projects_cli.py -q` passed: 3 passed.
- `python scripts\generate_codex_skill_adapters.py --check` passed: 27 adapters current.
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` passed: 6 passed.
- `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q` passed: 8 passed.
- `python scripts\check_narrative_artifact_evidence.py --paths .claude/rules/codex-review-gate.md .claude/rules/file-bridge-protocol.md .claude/rules/canonical-terminology.md` passed: 3 cleared.
- `python -m py_compile scripts/implementation_authorization.py scripts/implementation_start_gate.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/project/authorization.py groundtruth-kb/src/groundtruth_kb/cli.py` passed.
- Local MemBase inspection found the five new specs, work item `WI-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001`, and project authorization `PAUTH-GTKB-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001` in `groundtruth.db`.
- Local approval packet inspection found the project-authorization approval JSON files and the three rule approval JSON files listed in the implementation report.

Blocking evidence:

- A focused stale-authorization reproduction showed that `scripts.implementation_authorization.load_packet()` still accepts an issued implementation-start packet after the current project authorization is append-only revised to exclude one of the proposal's linked specs:

```text
LOAD_PACKET_RESULT: PASSED_AFTER_SPEC_EXCLUSION
```

## Findings

### P1 - Project authorization packet revalidation does not fail closed when current authorization scope narrows

Observation:

- `scripts/implementation_authorization.py:305` to `scripts/implementation_authorization.py:310` correctly rejects excluded linked specs when `validate_project_authorization_row()` receives `spec_links`.
- `scripts/implementation_authorization.py:392` to `scripts/implementation_authorization.py:421` extracts proposal `spec_links`, validates the project authorization at packet creation time, and stores `spec_links` in the packet.
- `scripts/implementation_authorization.py:452` to `scripts/implementation_authorization.py:465` revalidates the current project authorization when loading an existing packet, but it calls `validate_project_authorization_row()` without `spec_links`.
- The focused reproduction created a valid packet, then append-only updated `PAUTH-AUTH` with `excluded_spec_ids=['GOV-FILE-BRIDGE-AUTHORITY-001']`. `load_packet()` still returned success.

Deficiency rationale:

Project authorization is the new owner-approval evidence surface. The approved proposal requires project authorization to be current, active, unexpired, tied to the cited project, and not a bypass of proposal-level controls. A current authorization version that excludes a linked governing spec is a narrowed authorization envelope. Continuing to accept an older packet for up to `DEFAULT_EXPIRY_MINUTES = 480` minutes means implementation-start authorization can rely on stale owner-approval scope after the current MemBase authorization has changed.

This is not covered by the current tests. `platform_tests/scripts/test_implementation_start_gate.py` verifies packet creation, target-scope non-broadening, and work-item membership/inclusion, but it does not verify that `load_packet()` fails after project authorization scope changes.

Impact:

Prime Builder could continue protected implementation under a packet that no longer reflects the current project authorization envelope. That weakens `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` by making the new owner-approval control stale until packet expiry.

Recommended action:

- Update `load_packet()` to revalidate the current project authorization against the packet's proposal `spec_links`, not only project and work item metadata.
- Prefer storing the project authorization version and failing closed when the current authorization version changes after packet issuance, unless the revalidation intentionally proves the current version still covers the same work item and linked specs.
- Add a regression test in `platform_tests/scripts/test_implementation_start_gate.py` that creates a packet, updates the current project authorization to exclude a proposal-linked spec, and asserts `auth.load_packet()` raises `AuthorizationError`.
- Consider extending the same stale-scope regression to excluded work items, owner decision drift, and scope-summary or allowed/forbidden-operation changes if those fields are intended to participate in authorization enforcement.

## Applicability Preflight

- packet_hash: `sha256:1b1ebf845a5df6711863f9cf4726a166e4447a33146300c05ce5c3de3cc5beae`
- bridge_document_name: `gtkb-project-scoped-implementation-authorization`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-scoped-implementation-authorization-005.md`
- operative_file: `bridge/gtkb-project-scoped-implementation-authorization-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-project-scoped-implementation-authorization`
- Operative file: `bridge\gtkb-project-scoped-implementation-authorization-005.md`
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

## Commands Run

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`
- `python -m pytest platform_tests/scripts/test_project_authorization.py -q`
- `python -m pytest platform_tests/groundtruth_kb/test_spec_auto_backlog.py -q`
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`
- `python -m pytest platform_tests/scripts/test_projects_cli.py -q`
- `python scripts\generate_codex_skill_adapters.py --check`
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q`
- `python -m pytest platform_tests/scripts/test_governing_specs_preserved.py -q`
- `python scripts\check_narrative_artifact_evidence.py --paths .claude/rules/codex-review-gate.md .claude/rules/file-bridge-protocol.md .claude/rules/canonical-terminology.md`
- `python -m py_compile scripts/implementation_authorization.py scripts/implementation_start_gate.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/project/authorization.py groundtruth-kb/src/groundtruth_kb/cli.py`
- `python -m groundtruth_kb deliberations search "project scoped implementation authorization" --limit 10`
- `python -m groundtruth_kb deliberations search "implementation authorization stale project authorization excluded specs" --limit 10`
- `python -m groundtruth_kb deliberations search "automatic backlog intake implementation-bearing specs" --limit 10`
- `python -m groundtruth_kb deliberations get DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`
- Temporary-workspace reproduction of project authorization spec-exclusion drift against `scripts.implementation_authorization.load_packet()`.

## Final Verdict

NO-GO. The implementation is close and most scoped verification passes, but the current packet revalidation accepts stale project-authorization scope after a current authorization revision excludes a linked governing spec. Prime Builder should revise the implementation and resubmit a new post-implementation report.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
