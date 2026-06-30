GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-20260630-manual-review-wi4932-wi4933
author_model: Cursor Agent
author_model_version: direct-node-print
author_model_configuration: Cursor Agent direct node/index print mode; manual LO review; daemon stopped for containment; cwd=E:\GT-KB

bridge_kind: proposal_review
Document: gtkb-wi4932-cursor-direct-node-launcher
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-30 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4932-cursor-direct-node-launcher-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4932
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4932-CURSOR-NO-WINDOW-LAUNCHER
Verdict: GO

## Review Independence

Proposal `-001` author session `019f09c9-2db0-7b00-a337-40f998b07e56` (harness A, Prime Builder). Independent Cursor LO manual review session `cursor-lo-20260630-manual-review-wi4932-wi4933` (harness E). Same harness ID is not the review boundary; session contexts are unrelated.

## Proposal Reviewed

`bridge/gtkb-wi4932-cursor-direct-node-launcher-001.md` — bounded Windows Cursor headless launcher repair to prefer direct versioned `node.exe` + `index.js` over shell wrappers that can spawn visible consoles.

## Project / Work Item / PAUTH

- **Project:** `PROJECT-GTKB-DISPATCHER-RELIABILITY` (active dispatcher reliability program; dashboard rollup confirms project is live).
- **Work Item:** `WI-4932` — Cursor dispatcher no-window launcher repair; description in `-001` matches observed shell-wrapper launch path.
- **PAUTH:** `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4932-CURSOR-NO-WINDOW-LAUNCHER` cited with owner-decision evidence `DELIB-20266506`. Per-bridge WI-scoped PAUTH matches sibling WI-4927 pattern on the same project.

## Target Path Scope

All declared paths are in-root under `E:\GT-KB`:

- `scripts/cursor_harness.py` — launcher selection logic (`_windows_cursor_agent_candidates`, `_resolve_agent_command`).
- `platform_tests/scripts/test_cursor_harness.py` — existing focused harness tests; appropriate home for wrapper-bypass and fallback coverage.

Scope is bounded: no dispatcher topology, config, credential, deployment, or retired automation paths. External Cursor Agent install is read-only discovery input, not a GT-KB artifact path.

## Bridge Metadata

`-001` carries required Prime Builder author metadata, `bridge_kind: prime_proposal`, `implementation_scope: source`, `requires_review` / `requires_verification`, explicit `target_paths`, and matching **Files Expected To Change**. No slug collision (`gtkb-wi4932-cursor-direct-node-launcher` has only `-001` before this verdict).

## Requirement Sufficiency

Sufficient. Release-health no-visible-console requirement, centralized dispatcher architecture, and owner authorization via `DELIB-20266506` define the defect and approval boundary. No new owner decision required before implementation.

## Findings

No blocking findings.

**Code alignment:** Live `scripts/cursor_harness.py` enumerates Windows candidates as `.cmd`/`.ps1`/`.exe` under `%LOCALAPPDATA%\cursor-agent` and `_resolve_agent_command()` returns the first existing file without preferring a direct `node.exe` + `index.js` argv. That matches the reported conhost/OpenConsole risk from shell-wrapper dispatch.

**Non-scope respected:** Proposal explicitly excludes topology/config/credential changes and retired trigger fallback.

## Required Conditions

1. Preserve explicit `CURSOR_AGENT_BIN` / PATH override precedence; direct-node preference must not break documented override semantics in existing tests.
2. When no direct entrypoint exists, retain current fallback behavior (fail-closed or next candidate) and cover both paths in tests.
3. Do not expand `target_paths` beyond `-001` without a new `REVISED` bridge version.

## Spec-derived Verification Expectations

| Spec | Expectation at VERIFIED |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Focused cursor harness tests prove wrapper bypass when direct node/index exists and safe fallback when it does not. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Command-construction smoke/unit shows daemon-equivalent argv avoids `cmd.exe` / `powershell.exe` wrapper paths when direct entrypoint is available. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Ruff check/format on touched launcher and tests; no topology or retired-trigger changes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report adds targeted tests mapping to the above; bridge applicability preflights pass on the report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All edits and generated bridge/report artifacts remain under `E:\GT-KB`. |

## Prior Deliberations

- `DELIB-20266506` — Authorize WI-4932 Cursor dispatcher no-window launcher repair.
- `DELIB-20266409`, `DELIB-20266502`, `DELIB-20266504`, `DELIB-20266454` — cited separation/applicability context from `-001`.

## Verdict

**GO.** Proceed with implementation per `-001` within declared target paths.
