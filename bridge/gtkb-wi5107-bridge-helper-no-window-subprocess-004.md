NO-GO

# Verification Verdict - WI-5107 bridge-helper no-window subprocess (NO-GO)

bridge_kind: lo_verdict
Document: gtkb-wi5107-bridge-helper-no-window-subprocess
Version: 004
Author: Loyal Opposition (Claude Code, harness B)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-003.md

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 85e78bc0-61f1-4383-84cd-fb4128f29b95
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

## Verdict: NO-GO

WI-5107's no-window subprocess fix is correct in isolation and its tests pass, but
the report **cannot be verified as filed** because two of its declared target
files commingle WI-5107's small change with a large, uncommitted, undeclared,
unrelated feature owned by **WI-4978** (`gtkb-wi4978-helper-compliance-audit-chokepoint`).
A `VERIFIED` finalization stages whole files, so it would sweep WI-4978's in-flight
compliance-audit machinery into a commit labeled as WI-5107's no-window fix -
corrupting WI-4978's audit trail (an actively-iterating, previously-NO-GO'd thread)
and violating scoped-commit discipline. This is the same failure class as the
WI-5100 NO-GO earlier this session.

## Applicability Preflight

- packet_hash: `sha256:547efa4f9987658aed2034f83d1c85297bb2f7c1241ea46afcad1b3ca9998cc1`
- bridge_document_name: `gtkb-wi5107-bridge-helper-no-window-subprocess`
- operative_file: `bridge/gtkb-wi5107-bridge-helper-no-window-subprocess-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"] (advisory only; non-blocking)

## Clause Applicability

- No blocking clause gap drives this verdict; the NO-GO is a finalizability/scoped-commit blocker, not a clause-evidence gap.

## Prior Deliberations

- `DELIB-202665694` - Loyal Opposition Verdict: WI-4978 Helper Compliance Audit Chokepoint (Post-Implementation Verification), NO-GO - confirms WI-4978's compliance-audit feature is an actively-iterating thread whose implementation is the uncommitted machinery commingled here.
- WI-5100 NO-GO (`bridge/gtkb-wi5100-work-subject-config-platform-classification-004.md`, this session) - same commingled-tree failure class; see also the companion LO advisory `LO-ADVISORY-2026-07-09-commingled-tree-root-cause.md` and WI-5105.
- _No prior deliberation designs the no-window bridge-helper change; this is a novel reliability fix. The commingling concern is an evidence-of-current-state finding, not a design-precedent question._

## Specifications Carried Forward

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` + WI-5107 intent | `python -m pytest platform_tests/scripts/test_bridge_helper_no_window.py` | yes | 4 passed (WI-5107 substance correct) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (lint) | `ruff check` on the 5 declared files | yes | All checks passed |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (format) | `ruff format --check` on the 5 declared files | yes | 5 files already formatted |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | commit-finalization can commit exactly the verified WI-5107 path set | no | **BLOCKED - two target files commingled with WI-4978 (see Findings)** |

## Positive Confirmations

- WI-5107's own change is correct: the no-window fix routes the bridge-filing subprocess call sites through `no_window_subprocess_kwargs()`; the four call-site tests pass.
- `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py` (+2) and `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` (+3) are clean / WI-5107-only (0 off-topic added lines).
- New test `platform_tests/scripts/test_bridge_helper_no_window.py` is WI-5107-only.
- Review independence satisfied: report author session `a7996a03-...` differs from this reviewer session `85e78bc0-...`; the Prime `go_implementation` claim is expired and no peer verdict exists.
- `ruff check` and `ruff format --check` pass on all five declared files.

## Findings

### [P1] Finding 1 - `scripts/gtkb_bridge_writer.py` commingles WI-5107's ~3-line no-window change with ~80 lines of WI-4978's uncommitted compliance-audit-chokepoint feature

- **Observation:** The report declares the `gtkb_bridge_writer.py` change as "import `no_window_subprocess_kwargs`; spread it into the git-existence-check and compliance-audit `subprocess.run`" (~3 lines). The live `git diff --stat` for the file is **+83**. `git show HEAD:scripts/gtkb_bridge_writer.py | grep -cE 'run_bridge_compliance_audit|BridgeComplianceError|_bridge_compliance_gate_path'` returns **0**; the working tree returns **3** - so `run_bridge_compliance_audit`, `class BridgeComplianceError`, and `_bridge_compliance_gate_path` are uncommitted working-tree additions, not in HEAD. `gt bridge threads`/target_paths attribution shows `gtkb-wi4978-helper-compliance-audit-chokepoint` (chain at `-049`) targets `gtkb_bridge_writer.py`; that thread owns this compliance-audit machinery. Only 3 of the +83 added lines are WI-5107's (`from scripts.windows_subprocess import no_window_subprocess_kwargs` + two `**no_window_subprocess_kwargs()` spreads).
- **Deficiency rationale:** The `VERIFIED` commit-finalization gate stages `--include` paths via whole-file `git add`. Staging `scripts/gtkb_bridge_writer.py` for a WI-5107 commit would fold WI-4978's entire uncommitted compliance-audit feature into a commit whose subject and verdict claim WI-5107's no-window fix. That (i) violates scoped-commit discipline, (ii) commits WI-4978's implementation with no WI-4978 report/verification under a foreign SHA - and WI-4978 is an actively-iterating, previously-NO-GO'd thread, so this would strand it mid-flight, and (iii) makes WI-4978's own eventual verification impossible to finalize cleanly.
- **Proposed solution:** WI-4978's compliance-audit-chokepoint machinery must land its own commit first (via WI-4978's thread finalization), isolating `gtkb_bridge_writer.py` to WI-5107's 3 no-window lines; then WI-5107 re-files a REVISED report with an accurate diff and finalizes on a clean tree. Alternatively, hunk-isolate WI-5107's 3 lines via hunk-scoped staging and re-file the WI-5107 report to match.
- **Option rationale:** Sequencing WI-4978 first is cleaner because its feature is the larger, load-bearing change (the compliance-audit gate every bridge write already depends on). Bundling under WI-5107 was rejected: it breaks WI-4978's audit trail and the scoped-commit invariant.
- **Prime Builder implementation context:**
  - Objective: make `scripts/gtkb_bridge_writer.py` finalizable as a WI-5107-only scoped commit.
  - Evidence paths: `git diff -- scripts/gtkb_bridge_writer.py` (WI-5107 = the `no_window_subprocess_kwargs` import + two spreads; WI-4978 = `run_bridge_compliance_audit`/`BridgeComplianceError`/`_bridge_compliance_gate_path`/`_relative_to_project`); `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-049.md`.
  - Verification steps: after separation, `git diff --stat` on the WI-5107 commit shows only the no-window lines + the clean helper files + the test; re-run the 4-test suite and both ruff gates.
  - Rollback notes: no data/KB mutation; commit separation is non-destructive.

### [P1] Finding 2 - `impl_report_bridge.py` commingles WI-5107's `_git_lines` change with WI-4978's uncommitted project-metadata extraction

- **Observation:** The report declares the `impl_report_bridge.py` change as the `_git_lines` subprocess no-window kwargs. The live diff is **+19**. `git show HEAD` returns **0** for `_PROJECT_METADATA_LINE_RE`/`_extract_project_metadata_lines`; the working tree returns **4** - uncommitted project-metadata-extraction code (same WI-4978 chokepoint concern), not WI-5107's scope.
- **Deficiency rationale:** Same as Finding 1 - a whole-file finalize of the template would commit WI-4978's project-metadata code under a WI-5107 label.
- **Proposed solution:** Isolate under WI-4978 as in Finding 1; WI-5107's `_git_lines` no-window kwargs finalize on a clean template.
- **Option rationale:** Same sequencing rationale as Finding 1.
- **Prime Builder implementation context:** After WI-4978's template changes land their own commit, WI-5107's `_git_lines` kwargs commit cleanly; re-run the test suite.

### [P3] Finding 3 - Report "Files Changed" under-describes the actual diffs

- **Observation:** The report describes `gtkb_bridge_writer.py` as a ~3-line change and `impl_report_bridge.py` as a `_git_lines` one-liner; the live diffs are +83 and +19 respectively. Per "verify claims against canonical state," the report's change descriptions do not match the working tree.
- **Deficiency rationale:** A VERIFIED verdict must not endorse a report whose stated scope diverges from what would be committed; the gap is the direct signature of the Finding 1/2 commingling.
- **Proposed solution:** The re-filed WI-5107 REVISED report must describe a diff that matches the isolated WI-5107-only change.

## Required Revisions

1. Land WI-4978's compliance-audit-chokepoint machinery (`run_bridge_compliance_audit`, `BridgeComplianceError`, `_bridge_compliance_gate_path`, project-metadata extraction) in its own commit via the WI-4978 thread, isolating `gtkb_bridge_writer.py` and `impl_report_bridge.py` to WI-5107's no-window lines (Findings 1, 2).
2. Re-file the WI-5107 REVISED report with a `git diff --stat` matching the isolated WI-5107-only change (Finding 3).
3. Re-run the 4-test suite + both ruff gates on the isolated tree before re-submission.

## Commands Executed

- `git status --short` on the 5 declared target files -> 4 tracked ` M`, 1 untracked test.
- `git diff --stat` -> gtkb_bridge_writer.py +83, impl_report_bridge.py +19, revise_bridge.py +2, write_bridge.py +3.
- `git show HEAD:scripts/gtkb_bridge_writer.py | grep -cE 'run_bridge_compliance_audit|BridgeComplianceError|_bridge_compliance_gate_path'` -> 0 (HEAD); working tree -> 3.
- `git show HEAD:.../impl_report_bridge.py | grep -cE '_PROJECT_METADATA_LINE_RE|_extract_project_metadata_lines'` -> 0 (HEAD); working tree -> 4.
- `grep -lE 'target_paths.*gtkb_bridge_writer' bridge/*.md` -> `gtkb-wi4978-helper-compliance-audit-chokepoint` (owns the commingled machinery).
- `python -m pytest platform_tests/scripts/test_bridge_helper_no_window.py` -> 4 passed.
- `ruff check` / `ruff format --check` on the 5 declared files -> All checks passed / 5 already formatted.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5107-bridge-helper-no-window-subprocess` -> preflight_passed true, missing_required_specs [].

## Owner Action Required

None. Standard NO-GO routed back to Prime Builder for scoped-commit separation (WI-4978 first) and report correction. No owner decision is required.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
