GO
author_identity: loyal-opposition/antigravity/C
author_harness_id: C
author_session_context_id: C-2026-07-03T23-07-28Z
author_model: Gemini 3.5 Flash (High)
author_model_version: 3.5
author_model_configuration: Antigravity headless Loyal Opposition; mode=auto-dispatch

# Loyal Opposition Verdict -- GO (proposal reviewed)

bridge_kind: lo_verdict
Document: gtkb-wi5061-cursor-harness-no-gui-launcher-probe
Version: 002
Date: 2026-07-06 UTC
Reviewed: bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md (NEW prime implementation proposal)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5061
Recommended commit type: fix

## Verdict

**GO** -- The implementation proposal is approved. It restricts Cursor harness shims to resolving standalone, headless `agent` executables, preventing unwanted GUI launch events when Cursor's command-resolution falls back.

## Findings

1. **Resolution Restriction**: Restricting command-resolution to standalone `agent` or `cursor-agent` binaries removes the problematic fallback of running GUI launcher commands (`cursor`, `cursor.cmd`, `cursor.exe`) with `agent --help`, which triggers GUI IDE launches on Windows.
2. **Defect-Agnostic Prevention**: By modifying `_cursor_supports_agent_subcommand` to refuse execution against launcher names, the harness is protected from GUI launches regardless of what triggers the capability check.
3. **Spec-Derived Testing**: The verification plan adds unit tests that mock the absence of a standalone agent and verify that `_resolve_agent_command` fails closed with a `CursorHarnessError` without calling `subprocess.run` on the GUI launchers.
4. **Preflights Passed**: Both applicability preflight and clause preflight have passed cleanly.

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` — The owner requirement that Windows launches be headless.
- `INTAKE-c60bf094` — "Prohibit direct harness-to-harness invocation"; related harness-discipline lineage formalized as `GOV-HARNESS-ISOLATION-001`.
- `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md` — The original implementation proposal under review.

## Applicability Preflight

- packet_hash: `sha256:cf0ad50f5f42153318595e705464ee9c37e2dfc38d703ab8a26a6d1f622eeec9`
- bridge_document_name: `gtkb-wi5061-cursor-harness-no-gui-launcher-probe`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md`
- operative_file: `bridge/gtkb-wi5061-cursor-harness-no-gui-launcher-probe-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
