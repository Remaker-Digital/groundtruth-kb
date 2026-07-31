VERIFIED
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 00d48361-1114-4817-a20e-da4d03d186a5
author_model: Gemini 3.5 Flash
author_model_version: 3.5
author_model_configuration: Antigravity interactive Loyal Opposition; resolved role loyal-opposition

bridge_kind: lo_verdict
Document: gtkb-wi5061-cursor-harness-no-gui-launcher-probe
Version: 004
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-07-06 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md
Recommended commit type: fix

## Applicability Preflight

- packet_hash: `sha256:633c35870a7df94ec910312db28099538a045db1388f86a6ee819f57b072f247`
- bridge_document_name: `gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md`
- operative_file: `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
- Operative file: `bridge\gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` — owner requirement that Windows launches be headless.
- `INTAKE-c60bf094` — "Prohibit direct harness-to-harness invocation"; related harness-discipline lineage formalized as `GOV-HARNESS-ISOLATION-001`.
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md` — proposal version 001.
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-002.md` — LO GO verdict version 002.
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md` — implementation report version 003.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — small, low-risk reliability defect fix filed under the project's standing authorization.
- `GOV-HARNESS-ISOLATION-001` — harnesses are clients confined to bridge and `gt` CLI surfaces; the cursor shim must not open the vendor GUI IDE as a side effect of command-resolution.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority for this proposal, GO, and implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal and report carry forward governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project, Work Item, and Project Authorization linkage are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derives from the linked headless/harness-isolation behavior.
- `GOV-STANDING-BACKLOG-001` — WI-5061 is the governing backlog authority.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py -q --no-header --basetemp=E:\GT-KB\.pytest-basetemp-lo-verify` | yes | 32 passed |
| `GOV-HARNESS-ISOLATION-001` | Unit tests `test_resolve_agent_command_rejects_cursor_gui_override_without_probe` and `test_cursor_agent_subcommand_support_refuses_gui_launcher_without_probe` in `platform_tests/scripts/test_cursor_harness.py` | yes | passed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe` | yes | preflight_passed: true |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe` | yes | verified spec list cited |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe` | yes | project metadata correct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Unit tests cover absent standalone agent raising error and preventing GUI probe | yes | passed |
| `GOV-STANDING-BACKLOG-001` | Header metadata verification | yes | matches WI-5061 |

## Positive Confirmations

- Checked that the allowlist `_STANDALONE_AGENT_EXECUTABLE_NAMES` restricts candidate check execution to standalone `agent` or `cursor-agent` binaries.
- Verified that `_cursor_supports_agent_subcommand` refuses execution against GUI launcher names (`cursor`, `cursor.cmd`, `cursor.exe`).
- Verified that `_resolve_agent_command` fails closed with `CursorHarnessError` when `CURSOR_AGENT_BIN` points at a GUI launcher.
- Confirmed that the fallback path that queried PATH for GUI launchers has been completely removed.
- Confirmed that all unit tests pass successfully.

## Commands Executed

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py -q --no-header --basetemp=E:\GT-KB\.pytest-basetemp-lo-verify`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5061-cursor-harness-no-gui-launcher-probe`

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(cursor): WI-5061 fail-closed Cursor launcher probe - LO VERIFIED`
- Same-transaction path set:
- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md`
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-002.md`
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-003.md`
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
