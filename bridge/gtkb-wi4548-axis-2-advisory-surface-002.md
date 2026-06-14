REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ec695-8ccc-7941-9cbb-76c8f4d7a4ff
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; resolved Prime Builder via init keyword; workspace root E:\GT-KB
author_metadata_source: Claude Code Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Implementation Proposal - WI-4548 AXIS-2 ADVISORY Surface Fix

bridge_kind: prime_proposal
Document: gtkb-wi4548-axis-2-advisory-surface
Version: 002
Author: Prime Builder (Codex, harness A)
Date: 2026-06-14 UTC

## Revision Note

This REVISED packet only closes the clause-preflight in-root evidence gap from version 001. Implementation scope, target paths, tests, and acceptance criteria are unchanged.

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION-IMPL
Project: PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION
Work Item: WI-4548

target_paths: [".claude/hooks/bridge-axis-2-surface.py", "platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

## Summary

Fix the residual AXIS-2 ADVISORY surfacing defect recorded in WI-4548. WI-4541
made ADVISORY entries Prime-actionable in manual scan/notify surfaces while
keeping them non-dispatchable for headless runs. The Claude AXIS-2
UserPromptSubmit hook still drops every item with `dispatchable=False`, which
correctly suppresses terminal-kind GO threads but incorrectly suppresses
ADVISORY entries, the canonical non-dispatchable interactive Prime work case.

This proposal narrows the fix to the AXIS-2 consumer: keep suppressing
non-dispatchable GO/NO-GO terminal-kind work, but include items whose latest
status is `ADVISORY` even though they are non-dispatchable. Add a regression
test beside the existing terminal-kind GO suppression tests.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical workflow
  state; ADVISORY is a first-class bridge status and Prime-disposition surface.
- `DCL-ADVISORY-ROUTING-001` - ADVISORY entries route via Axis 2 while remaining
  excluded from cross-harness headless dispatch.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  the governing bridge and routing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below
  maps the ADVISORY routing contract and terminal-kind suppression contract to
  executable tests.
- `GOV-STANDING-BACKLOG-001` - WI-4548 is the MemBase work authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths and the bridge artifact are under `E:\GT-KB`: `E:\GT-KB\.claude\hooks\bridge-axis-2-surface.py`, `E:\GT-KB\platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py`, and `E:\GT-KB\bridge\gtkb-wi4548-axis-2-advisory-surface-002.md`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - the residual defect is
  preserved as WI-4548 and this bridge proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - defect-to-WI-to-bridge
  lifecycle is followed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) - the implementation is
  routed through durable artifacts rather than chat-only repair.

Governing rule surfaces cited for implementation interpretation:
`.claude/rules/bridge-essential.md` section "Two-Axis Bridge Automation Model",
`.claude/rules/file-bridge-protocol.md` section "Advisory Reports", and
`.claude/rules/peer-solution-advisory-loop.md` section "Bridge Integration".

## Requirement Sufficiency

Existing requirements sufficient. WI-4548 records the defect and candidate fix;
`DCL-ADVISORY-ROUTING-001`, `bridge-essential.md`, and
`file-bridge-protocol.md` already specify the intended split: ADVISORY entries
are non-dispatchable Axis-2 work for interactive Prime attention, not headless
Axis-1 dispatch. No new or revised requirement is needed before implementation.

## Prior Deliberations

- `bridge/gtkb-advisory-prime-actionability-surfacing-004.md` - Codex VERIFIED
  WI-4541 and explicitly recorded the residual risk: AXIS-2 still filters
  non-dispatchable ADVISORY items; Prime should file a separate disposition
  thread rather than treating WI-4541 as AXIS-2 completion.
- `bridge/gtkb-advisory-prime-actionability-surfacing-003.md` - implementation
  report disclosed the AXIS-2 follow-on finding and distinguished it from the
  manual scan/notify implementation.
- `bridge/gtkb-advisory-routing-dcl-006.md` - verification chain for the ADVISORY
  routing DCL, including the design that ADVISORY routes through Axis 2 and is
  excluded from cross-harness trigger dispatch.
- Deliberation searches performed before filing found no direct matching DA
  entries for `WI-4548 AXIS-2 ADVISORY bridge-axis-2-surface`, `ADVISORY entries
  route via Axis-2`, or `advisory prime actionability surfacing AXIS-2 follow-on`.

## Proposed Change

1. In `.claude/hooks/bridge-axis-2-surface.py`, replace the current blanket
   `dispatchable` filter with a small predicate that preserves the existing
   compatibility-safe default and includes ADVISORY entries:
   - include items with `dispatchable=True`;
   - include items whose `top_status` is `ADVISORY` even when `dispatchable=False`;
   - exclude all other `dispatchable=False` items, preserving terminal-kind GO
     suppression.
2. In `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`,
   add a regression fixture proving an ADVISORY entry with
   `bridge_kind: loyal_opposition_advisory` remains visible in the Prime AXIS-2
   surface.
3. Do not change cross-harness trigger dispatch, single-harness dispatch,
   `compute_actionable_pending`, bridge kind taxonomy, or rule text in this
   slice. WI-4541 already completed the scan/notify/rule alignment; WI-4548 is
   the AXIS-2 consumer fix only.

## Spec-Derived Verification Plan

Run the focused AXIS-2 regression lane:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py platform_tests\hooks\test_bridge_axis_2_surface_work_intent.py platform_tests\hooks\test_bridge_axis_2_role_aware.py platform_tests\scripts\test_bridge_axis_2_surface.py -q --tb=short
```

Run the code-quality gates on changed Python files:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude\hooks\bridge-axis-2-surface.py platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .claude\hooks\bridge-axis-2-surface.py platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py
```

| Specification | Test / check | Expected evidence |
|---|---|---|
| `DCL-ADVISORY-ROUTING-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | New regression in `test_bridge_axis_2_surface_governance_review_terminal.py` | ADVISORY latest status appears in Prime AXIS-2 items despite `dispatchable=False`. |
| Terminal-kind suppression from WI-4278 / `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing governance-review GO tests in the same file | Non-dispatchable terminal-kind GO remains excluded. |
| Role-aware AXIS-2 contract | `test_bridge_axis_2_role_aware.py` | Prime/LO role selection remains unchanged. |
| Work-intent visibility contract | `test_bridge_axis_2_surface_work_intent.py` | Claim annotations/footer remain unchanged. |
| Hook runtime behavior | `test_bridge_axis_2_surface.py` | Prompt-time surface behavior, cache, dismissal, and emergency stop remain unchanged. |

## Acceptance Criteria

- ADVISORY entries in `compute_actionable_pending(...).actionable_for_prime` are
  included in the Claude AXIS-2 Prime surface even when their `dispatchable`
  attribute is false.
- Non-ADVISORY items with `dispatchable=False`, especially terminal-kind GO
  entries such as `governance_review`, remain excluded from the AXIS-2 surface.
- Existing role-aware, work-intent, cache/dismissal, and emergency-stop behavior
  does not regress.
- No headless dispatch consumer is changed and no ADVISORY entry becomes
  dispatchable.

## Owner Decisions / Input

Mike directed this session to complete WI-4548. That selects an already-open
MemBase defect under an active project authorization; it is not a new formal
requirement, waiver, protected-artifact approval, deployment approval, or
production release approval. Implementation remains gated on Loyal Opposition
GO plus the implementation-start packet.

## Risk / Rollback

- Risk: a too-broad exception could re-surface terminal-kind GO entries and
  reintroduce AXIS-2 noise. Mitigated by predicate-specific tests that keep
  governance-review GO suppressed while ADVISORY is included.
- Risk: ADVISORY could be confused with dispatchability. Mitigated by scoping
  the change only to the AXIS-2 prompt surface; no headless dispatch code or
  `dispatchable` computation changes.
- Rollback: revert the two target files; no schema, KB, protected narrative, or
  hook registration changes are involved.
