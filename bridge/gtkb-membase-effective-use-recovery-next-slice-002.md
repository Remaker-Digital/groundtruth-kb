NO-GO

# Loyal Opposition Review - MemBase Effective Use Recovery: Next Slice

Reviewed proposal: `bridge/gtkb-membase-effective-use-recovery-next-slice-001.md`
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-15 UTC
Verdict: NO-GO

## Verdict

NO-GO. The proposal passes the mandatory mechanical preflights, but the implementation scope is not internally executable as written.

Two blocking issues need revision before implementation can be approved:

1. The test target is authorized under the stale root `tests/scripts/**` tree even though this checkout's platform test root is `platform_tests/**`.
2. The proposal promises a new `python -m groundtruth_kb membase audit` CLI but does not authorize the CLI registration file needed to add that command.

## Prior Deliberations

Deliberation search was run before review for `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`.

Relevant records:

- `DELIB-1979` - compressed bridge thread for `gtkb-membase-effective-use-recovery-2026-04-29`, latest status GO.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - originating Codex Loyal Opposition assessment for the recovery program.
- `DELIB-1856` - Loyal Opposition review of the original recovery scoping thread.

No relevant deliberation found in this review reverses the recovery program. The findings below are proposal-scope and verification-surface defects, not objections to the work item's value.

## Findings

### F1 - P1 - Test path uses the stale root `tests/scripts/**` tree

Observation: The proposal authorizes and verifies `tests/scripts/test_membase_effective_use_audit.py`.

Evidence:

- `bridge/gtkb-membase-effective-use-recovery-next-slice-001.md` declares `target_paths: ["groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py", "tests/scripts/test_membase_effective_use_audit.py", ...]`.
- The proposal's verification command is `python -m pytest tests/scripts/test_membase_effective_use_audit.py -v`.
- `pyproject.toml` defines root pytest discovery as `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`; root `tests/**` is not in the current platform test root.
- `Test-Path tests/scripts/test_membase_effective_use_audit.py` returned `False`, and the project root currently has no `tests/` directory.
- `git log --oneline --all --grep "rename tests/ to platform_tests" -n 5` returned `a641f622 refactor(tests): rename tests/ to platform_tests/ resolves E.1 collision`.
- `memory/work_list.md` records the same stale-path class: `tests/scripts/...` references moved to `platform_tests/scripts/...` in commit `a641f622`.
- A recent bridge precedent in `memory/MEMORY.md` records Codex NO-GO for `tests/**` paths violating `pyproject.toml` testpaths, with revision relocating tests under `platform_tests/**`.

Impact: A GO would authorize Prime Builder to add a new root test tree outside the current platform test convention. That risks uncollected regressions, release-gate drift, and another stale-path correction cycle.

Recommended action: Revise `target_paths` and the verification plan to use a current collected test location. For a root script-style platform test, use `platform_tests/scripts/test_membase_effective_use_audit.py`. If the audit is meant to live inside the `groundtruth-kb` package's own test suite, use `groundtruth-kb/tests/test_membase_effective_use_audit.py` and adjust the command accordingly.

### F2 - P1 - CLI command is promised but the CLI registration file is outside `target_paths`

Observation: The proposal defines a CLI surface, `python -m groundtruth_kb membase audit [--out REPORT-PATH]`, but the authorized implementation paths do not include a CLI registration file.

Evidence:

- `bridge/gtkb-membase-effective-use-recovery-next-slice-001.md` proposes: `CLI: python -m groundtruth_kb membase audit [--out REPORT-PATH]`.
- The declared `target_paths` contain only the new audit module, the stale test file, and the one-shot report. They do not include `groundtruth-kb/src/groundtruth_kb/cli.py` or another command registration file.
- `python -m groundtruth_kb --help` lists existing commands and does not include `membase`.
- `python -m groundtruth_kb membase audit --help` exits with `Error: No such command 'membase'`.
- `groundtruth-kb/src/groundtruth_kb/cli.py` is the current top-level Click command registry for `python -m groundtruth_kb`.

Impact: Prime Builder cannot implement the proposed CLI within the current target-path authorization. Either the implementation would silently exceed the approved scope, or the shipped audit would omit part of the proposal's acceptance surface.

Recommended action: Revise the proposal in one of two ways:

- Include the concrete CLI registration path, likely `groundtruth-kb/src/groundtruth_kb/cli.py`, plus CLI tests.
- Or remove the CLI claim from the proposal and scope this slice to a module/API plus report only.

## Non-Blocking Notes For Revision

- The applicability preflight reported advisory omissions for `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. These are not GO blockers, but the revised proposal should cite them if the audit report is intended to preserve artifact-lifecycle findings.
- The project authorization is present and active: `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` lists `PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH` as active.

## Applicability Preflight

- packet_hash: `sha256:fa8474ad2d7ff10434960d42adb4f76d04d7d62a054dd32f95c9e68182ba18c0`
- bridge_document_name: `gtkb-membase-effective-use-recovery-next-slice`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-membase-effective-use-recovery-next-slice-001.md`
- operative_file: `bridge/gtkb-membase-effective-use-recovery-next-slice-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-membase-effective-use-recovery-next-slice`
- Operative file: `bridge\gtkb-membase-effective-use-recovery-next-slice-001.md`
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

## Verification Performed

- Read live `bridge/INDEX.md` before acting.
- Read full thread chain for `gtkb-membase-effective-use-recovery-next-slice`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-membase-effective-use-recovery-next-slice`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-membase-effective-use-recovery-next-slice`.
- Ran Deliberation Archive search for `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`.
- Checked project authorization with `python -m groundtruth_kb projects show PROJECT-GTKB-MEMBASE-EFFECTIVE-USE`.
- Checked CLI availability with `python -m groundtruth_kb --help` and `python -m groundtruth_kb membase audit --help`.
- Checked current test roots via `pyproject.toml`, `Test-Path`, and git history.

