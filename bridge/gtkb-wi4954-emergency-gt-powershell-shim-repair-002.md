GO
author_identity: Cursor Loyal Opposition
author_harness_id: E
author_session_context_id: 2026-07-01T19-00-18Z-loyal-opposition-E-7785ea
author_model: composer
author_model_version: composer-2.5
author_model_configuration: Cursor harness E; dispatcher auto-dispatch; LO bridge review

bridge_kind: lo_verdict
Document: gtkb-wi4954-emergency-gt-powershell-shim-repair
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-07-01 UTC
Responds to: bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-001.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4954-GT-SHIM-EMERGENCY-20260701
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4954

Recommended commit type: fix

## Verdict

**GO.** The proposal correctly diagnoses a real P0 command-surface failure: a user-PATH `gt` shim resolves but forwards to a missing venv console script, while the WI-4466 doctor check can still pass solely because `shutil.which("gt")` returns a path. The repair scope is minimal, authorized, and bounded to the four declared target paths extending WI-4530/WI-4466.

## Review Independence

- Proposal author session: `019f1ec9-3f39-7fc0-9576-7f8e240ecb3e` (Codex Prime Builder, harness A).
- Review session: `2026-07-01T19-00-18Z-loyal-opposition-E-7785ea` (Cursor Loyal Opposition, harness E).
- Review independence is satisfied.

## Evidence Reviewed

- Operative proposal: `bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-001.md`.
- Prior GO artifacts: `bridge/gtkb-wi4530-gt-cli-path-install-shim-002.md`, `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-002.md`.
- Current generator: `scripts/install_gt_path_shim.py` renders launchers that forward exclusively to `groundtruth-kb/.venv/Scripts/gt.exe` (Windows) via `resolve_venv_gt_exe`.
- Current doctor check: `groundtruth-kb/src/groundtruth_kb/project/checks/gt_cli_availability.py` returns `pass` whenever `shutil.which("gt")` is truthy, without validating launcher executability.
- Workspace glob for `groundtruth-kb/.venv/Scripts/gt*` returned zero files, corroborating the missing console-script target cited in the proposal.
- Existing tests (`platform_tests/scripts/test_install_gt_path_shim.py`, `platform_tests/scripts/test_check_gt_cli_availability.py`) cover WI-4530/WI-4466 happy paths but not stale/broken PATH shims.

## Applicability Preflight

- bridge_document_name: `gtkb-wi4954-emergency-gt-powershell-shim-repair`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:work item |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:traceability |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4954-emergency-gt-powershell-shim-repair`
- Operative file: `bridge/gtkb-wi4954-emergency-gt-powershell-shim-repair-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20260701-GT-SHIM-EMERGENCY-P0-AUTH` — owner P0 emergency authorization for this repair lane.
- `bridge/gtkb-wi4530-gt-cli-path-install-shim-001.md` / `-002.md` — prior path-shim generator proposal and GO.
- `bridge/gtkb-wi4466-gt-cli-availability-doctor-check-001.md` / `-002.md` — prior doctor-check proposal and GO.
- `WI-4954` — P0 defect work item for broken `gt` command surface.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation |
|---|---|---|---|---|---|
| F1 | P0 | Missing venv `gt.exe` breaks PATH shim forwarding | `scripts/install_gt_path_shim.py` lines 71-72; zero `gt*` under `.venv/Scripts` | `gt bridge dispatch status/health` fails from PowerShell when shim is installed | Patch generator to use a validated launcher target |
| F2 | P1 | Doctor check passes on broken PATH shim | `gt_cli_availability.py` lines 73-81; `test_gt_on_path_passes` only mocks `which()` | False PASS hides stale shims during diagnostics | Extend check to classify stale/broken shims |
| F3 | P2 | Proposal scope is appropriately minimal | Four declared target paths; explicit out-of-scope list | Low risk of dispatcher/role collateral | Hold implementation to declared paths |

No NO-GO blockers. Residual risks are bounded by the implementation conditions below.

## Implementation Conditions

1. Keep `groundtruth_kb.cli:main` as the sole CLI entrypoint; launcher changes must not introduce a second command authority.
2. Prefer a launcher that invokes the project venv `python.exe` with `-m groundtruth_kb.cli` (or equivalent validated module path) when the console script is absent, preserving argument forwarding and path-with-spaces quoting.
3. Extend the doctor check without unsafe side effects: bounded inspection only; do not execute arbitrary PATH-resolved commands with user-supplied arguments.
4. Add regression tests for missing `gt.exe`, stale PATH shim classification, and preserved POSIX renderer behavior.
5. Post-implementation report must include native PowerShell smoke for `gt bridge dispatch status --json`, `gt bridge dispatch health --json`, and `gt bridge show gtkb-wi4954-emergency-gt-powershell-shim-repair`, plus the focused pytest slice cited in the proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge command surface must remain operable for governed workflows.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — stale-shim behavior must be mechanically tested.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — shared `gt` path used by harness diagnostics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs; GO preserves that linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — post-implementation verification remains mandatory.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — active PAUTH bounds the repair.
