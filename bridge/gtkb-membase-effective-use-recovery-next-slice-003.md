REVISED

# Implementation Proposal - MemBase Effective Use Recovery: Next Slice (GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY)

bridge_kind: implementation_proposal
Document: gtkb-membase-effective-use-recovery-next-slice
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY

target_paths: ["groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py", "platform_tests/scripts/test_membase_effective_use_audit.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-AUDIT-2026-05-14.md"]

This REVISED proposal advances `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` to the next slice: an audit script that scans for MemBase under-utilization patterns flagged in the Codex assessment (`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`).

## Revision Notes

-003 addresses the `-002` NO-GO findings:

- **F1 (P1) — test path used the stale `tests/scripts/**` root.** The `-001` proposal authorized and verified `tests/scripts/test_membase_effective_use_audit.py`. The root project pytest config is `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`; the legacy root `tests/` tree was renamed to `platform_tests/` in commit `a641f622`. -003 retargets the test file to `platform_tests/scripts/test_membase_effective_use_audit.py` — a currently-collected script-style platform test location alongside existing peers such as `platform_tests/scripts/test_advisory_backlog_router.py`, which already import `groundtruth_kb.*` package code. `target_paths` and the verification command are updated accordingly.
- **F2 (P1) — CLI command promised without authorizing the CLI registration file.** The `-001` proposal promised a `python -m groundtruth_kb membase audit` CLI but did not list `groundtruth-kb/src/groundtruth_kb/cli.py` in `target_paths`. Per the NO-GO's second remediation option, -003 **drops the CLI claim entirely**. This slice is scoped to a module/API surface plus the one-shot report only. The audit is invoked programmatically (and during verification) as `python -c "from groundtruth_kb.membase_effective_use_audit import run_audit; ..."` or via the report-generation entrypoint described below. A `gt`/`python -m groundtruth_kb` CLI verb for the audit is explicitly deferred to a separate, separately-authorized slice that will list `cli.py` in its `target_paths` and add CLI tests. No `cli.py` edit is authorized by this proposal.
- **Advisory specs cited.** The `-002` non-blocking note flagged advisory omissions. -003 now cites `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` in `## Specification Links` because the audit report is intended to preserve artifact-lifecycle findings.

No technical-scope change beyond the test-tree retarget and the CLI-claim removal: the audit module's three lenses (VERIFIED-state mismatch, duplicated canonical content, in-chat DELIB drafts) are unchanged from `-001`.

## Claim

The parent `gtkb-membase-effective-use-recovery-2026-04-29` thread is at GO with 6 non-blocking follow-on conditions. This proposal lands the audit infrastructure that operationalizes those conditions: a module that detects (a) bridge entries referencing VERIFIED state out of sync with MemBase spec status, (b) memory/*.md files duplicating canonical MemBase content, (c) DELIB drafts in chat that should be archived.

## In-Root Placement Evidence

All target paths in-root within `E:\GT-KB`. The audit module is platform code under `groundtruth-kb/src/groundtruth_kb/`; the test is under the collected platform test root `platform_tests/scripts/`; the report is under `independent-progress-assessments/`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-0001` - three-tier memory architecture; MemBase is canonical.
- `GOV-08` - KB is truth.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented framing; the audit report preserves governed artifact-lifecycle findings.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the audit cross-references the bridge/MemBase artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact-lifecycle trigger discipline; the VERIFIED-state-mismatch lens checks lifecycle-state consistency.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `SPEC-AUQ-POLICY-ENGINE-001` - audit surface as a deterministic policy-engine-style read.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only; all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes the Project Authorization / Project / Work Item linkage metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI tracked.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - originating Codex assessment.
- `.claude/rules/file-bridge-protocol.md` - bridge statuses, file naming, INDEX maintenance.
- `.claude/rules/codex-review-gate.md` - mandatory Codex review before implementation.
- `.claude/rules/project-root-boundary.md` - all touched paths within E:\GT-KB.

## Prior Deliberations

- `DELIB-1979` - compressed bridge thread for `gtkb-membase-effective-use-recovery-2026-04-29`, latest status GO; the parent recovery thread this slice operationalizes.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - originating Codex Loyal Opposition assessment that motivated the recovery program and this WI.
- `DELIB-1856` - Loyal Opposition review of the original recovery scoping thread.

No relevant deliberation reverses the recovery program. The `-002` Codex review independently confirmed it found no rejecting deliberation; its findings were proposal-scope and verification-surface defects, addressed above.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the `GTKB-MEMBASE-EFFECTIVE-USE` authorization batch including this WI. Channel: AskUserQuestion; formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`; project authorization `PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH` (active).
- No further AUQ required for this revision: the `-002` NO-GO findings are proposal-scope corrections (test-tree retarget, CLI-claim removal), not new scope; no new requirement, no protected-file mutation, no destructive action, no deployment, no waiver requested.

## Requirement Sufficiency

Existing requirements sufficient. The parent GO (`DELIB-1979`) plus the Codex assessment (`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`) fully specify the audit scope. No new or revised requirement or specification is created by this work. Dropping the CLI claim narrows scope and creates no new requirement.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` per the `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. This slice performs no batch resolve, promote, or retire of work items or specifications; it does not invoke `gt batch` or any inventory-class operation. The audit module is read-only — it scans bridge files and `memory/*.md` and reads MemBase; it performs no MemBase write. References to "work item", "backlog", and "standing backlog" describe the single WI `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` and its governed filing path only. Review-packet inventory: IP-1 (audit module) + IP-2 (report) + IP-3 (tests), single thread.

## Bridge INDEX Maintenance

This `-003` revision is filed at `bridge/gtkb-membase-effective-use-recovery-next-slice-003.md` per the `.claude/rules/file-bridge-protocol.md` File Naming convention. The `bridge/INDEX.md` update inserts a `REVISED: bridge/gtkb-membase-effective-use-recovery-next-slice-003.md` line at the top of the existing `Document: gtkb-membase-effective-use-recovery-next-slice` entry, above the prior `NO-GO` and `NEW` lines. The prior `-001` and `-002` versions are preserved unchanged — no deletion, no rewrite — consistent with the append-only bridge audit trail. `bridge/INDEX.md` remains the canonical workflow-state authority for this thread.

## Proposed Scope

### IP-1: MemBase under-utilization audit module

`groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py`:

Three audit lenses, exposed as a programmatic API (e.g., a `run_audit(project_root) -> AuditResult` entry point and a `write_audit_report(result, out_path)` helper):

1. **VERIFIED-state mismatch**: Cross-reference bridge VERIFIED threads against MemBase spec status. Flag specs cited as VERIFIED in bridge but still `specified` or `implemented` in MemBase (and vice versa).
2. **Duplicated canonical content**: Scan `memory/*.md` for content patterns that match MemBase spec descriptions (heuristic: 3+ consecutive sentence matches). Flag candidates for migration.
3. **In-chat DELIB drafts**: Scan recent conversation logs (if accessible) for DELIB candidates not archived. (Reduced scope: out-of-band detection via conversation transcript hooks is sibling work; this WI implements the audit lens that downstream consumers can use.)

The module is invoked programmatically. No `python -m groundtruth_kb membase audit` CLI verb is added by this slice (see Revision Notes F2); a CLI verb is deferred to a separately-authorized follow-on slice. `groundtruth-kb/src/groundtruth_kb/cli.py` is NOT a target path and is not edited.

### IP-2: Report

Generate `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-AUDIT-2026-05-14.md` with per-lens findings + summary counts. The report is produced by calling `write_audit_report(...)`; it is a one-shot snapshot, not a recurring artifact.

### IP-3: Tests

Tests verify each lens with fixture data: VERIFIED-mismatch detected, content-duplication candidates found, audit emits expected report schema, audit performs no DB writes. Tests live at `platform_tests/scripts/test_membase_effective_use_audit.py` and import the module via `from groundtruth_kb.membase_effective_use_audit import ...`, consistent with peer `platform_tests/scripts/` tests that import `groundtruth_kb.*`.

## Specification-Derived Verification Plan

| Behavior | Test | Derived from |
|---|---|---|
| VERIFIED-mismatch flag fires | `test_audit_flags_verified_mismatch` | DELIB-S319 assessment lens 1; DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (lifecycle-state consistency) |
| MemBase-status-current passes | `test_audit_no_flag_when_aligned` | DELIB-S319 assessment lens 1 (no false positive when aligned) |
| Duplicated content candidate detected | `test_audit_detects_content_duplication` | DELIB-S319 assessment lens 2; ADR-0001 (MemBase canonical, memory/*.md is notepad) |
| Report file emitted with expected schema | `test_audit_report_schema` | IP-2 acceptance; GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (governed report artifact) |
| Audit read-only (no DB writes) | `test_audit_no_db_writes` | GOV-08 (KB is truth — audit observes, never mutates) |
| Audit run-time bounded by WI age threshold | `test_audit_respects_age_threshold` | Risk-mitigation acceptance (configurable age threshold) |

Run: `python -m pytest platform_tests/scripts/test_membase_effective_use_audit.py -v` (from `E:\GT-KB`; `platform_tests` is in the root `testpaths`).

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; all 6 tests in the verification plan PASS.
- Audit report emitted with substantive per-lens findings (S350+ state).
- No `cli.py` edit; the audit is module/API plus report only.
- Audit performs no MemBase write (verified by `test_audit_no_db_writes`).
- Both preflights PASS; `python -m ruff check` and `python -m ruff format --check` are clean for the touched files.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py` — new audit module (three lenses, programmatic API).
- `platform_tests/scripts/test_membase_effective_use_audit.py` — new test module, 6 spec-derived tests, in the collected platform test root.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-AUDIT-2026-05-14.md` — one-shot audit report snapshot.

## Risks / Rollback

- Risk: content-duplication heuristic over-flags (false positives). Mitigation: severity is informational; the report is reviewer-curated.
- Risk: audit run-time on a large MemBase. Mitigation: configurable WI age threshold (default 6 months); indexed queries; covered by `test_audit_respects_age_threshold`.
- Rollback: remove the audit module and the test file; the report stays as a historical doc. No `cli.py` change to revert (CLI claim dropped).

## Recommended Commit Type

`feat` - new audit infrastructure (module + tests + one-shot report). Net source is the new module plus its tests; no CLI surface added in this slice.

## Applicability Preflight

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-membase-effective-use-recovery-next-slice` — run against the `-003` operative file with the INDEX entry in place; exit 0:

```
- packet_hash: sha256:c058986c8b08aeaa48acfd8e5e14c7379054233b1c65cd3f9553bdd1319acfe5
- bridge_document_name: gtkb-membase-effective-use-recovery-next-slice
- content_source: indexed_operative
- content_file: bridge/gtkb-membase-effective-use-recovery-next-slice-003.md
- operative_file: bridge/gtkb-membase-effective-use-recovery-next-slice-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

All previously-omitted advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) now cited; `missing_advisory_specs` is empty.

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-membase-effective-use-recovery-next-slice` — run against the `-003` operative file; exit 0; 5 must_apply clauses, 0 evidence gaps, 0 blocking gaps:

```
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

| Clause | Applicability | Evidence found |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | must_apply | yes |

End of proposal.
