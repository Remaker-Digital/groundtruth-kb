NEW

# gtkb-wi4738-workstream-focus-dashboard-summary-timeout - Bound init-keyword relay dashboard summary reads

bridge_kind: prime_proposal
Document: gtkb-wi4738-workstream-focus-dashboard-summary-timeout
Version: 001
Author: Prime Builder (Codex, session-stated via `::init gtkb pb`)
Date: 2026-06-23T02:25:50Z

author_identity: prime-builder/codex/A (session-stated Prime Builder override)
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: GPT-5 Codex
author_model_version: unavailable in harness metadata
author_model_configuration: Codex Desktop, approval_policy=never, filesystem=danger-full-access, session role override from owner prompt `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4738

target_paths: ["scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/gtkb_scoped_client.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Bound the `UserPromptSubmit` init-keyword relay path so it cannot hang while trying to regenerate or validate startup relay context through dashboard-summary reads. `WI-4738` was opened after LO verification reproduced `platform_tests/hooks/test_workstream_focus.py::test_prompt_hook_accepts_bom_prefixed_stdin_from_windows_pipeline` timing out while `.claude/hooks/workstream-focus.py` called `scripts/workstream_focus.py`, which entered `scripts/session_self_initialization.py::build_startup_model()` and blocked in `scripts/gtkb_scoped_client.py::_dashboard_summary_read()`.

The intended fix is narrow: preserve visible, cache-isolated startup disclosure relay behavior, but make the hook path bounded/fail-soft when dashboard summary data is slow or unavailable. Implementation should prefer a deterministic function-level seam or bounded timeout around relay-cache refresh/dashboard summary reads over widening the hook subprocess timeout.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This implementation proposal is filed through the numbered bridge chain, and implementation must wait for LO `GO` plus an implementation-start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal enumerates all known relevant startup, init-keyword, project authorization, and bridge-governance specs before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal includes machine-readable `Project Authorization`, `Project`, and `Work Item` metadata, and the PAUTH includes `WI-4738`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The post-implementation report and LO verification must map each linked spec to executed tests or preflight evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-4738` is a MemBase-backed open project member; the backlog/project record is the durable work authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active project PAUTH is bounded owner authorization for this snapshot member WI, but does not bypass bridge review or impl-start.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - The fix must preserve complete visible startup disclosure relay, cache isolation, and visible failure when relay cache state is unusable.
- `GOV-SESSION-SELF-INITIALIZATION-001` - Startup operational claims must remain live-source based, but generated/cached startup context must not be treated as authority or create an unbounded hook path.
- `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` - UserPromptSubmit startup-gate behavior must stay correctly armed only by real SessionStart dispatch and must not regress normal prompt handling.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - The canonical `::init gtkb pb` first-line keyword used in the reproduced failing test must continue to parse and route correctly.
- `DCL-SESSION-ROLE-RESOLUTION-001` - The owner-declared interactive role token must continue to resolve as the transcript-defined role; bounded relay behavior must not change role resolution.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - The relay path should remain bounded and token-conscious, using cache pointers/fail-soft behavior instead of expensive synchronous regeneration in the hook hot path.

## Prior Deliberations

- `DELIB-20265586` - Owner authorized the bounded drive-to-conclusion project sweep and selected the snapshot-bound shape; the PAUTH for `PROJECT-GTKB-MAY29-HYGIENE` includes `WI-4738`.
- `DELIB-2078` - Owner approved the init-keyword startup disclosure relay DCL after a visible relay failure; this proposal preserves that relay contract while bounding the hot path.
- `DELIB-20260648` - Owner clarified canonical init-keyword subject/role optionality; this proposal preserves `::init gtkb pb` routing semantics.
- `DELIB-20265226` - Owner confirmed transcript-defined interactive role persistence; this proposal does not alter role authority or marker semantics.

## Owner Decisions / Input

No new owner decision is required for this proposal. `DELIB-20265586` and `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23` authorize bounded implementation for the 14 snapshot member WIs, including `WI-4738`, with allowed mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.

This proposal does not request GOV/SPEC/ADR/DCL/PB/REQ mutation, production deployment, credential lifecycle work, destructive cleanup, or work outside the cited PAUTH snapshot.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, `GOV-SESSION-SELF-INITIALIZATION-001`, `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001`, `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, and `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` already define the required behavior: the init-keyword relay must be visible, cache-isolated, correctly role-routed, and bounded enough for startup/token discipline. `WI-4738` is an implementation defect in that already-governed behavior, not a new policy choice.

## Spec-Derived Verification Plan

Expected implementation verification:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
python -m ruff check scripts/workstream_focus.py scripts/session_self_initialization.py scripts/gtkb_scoped_client.py platform_tests/hooks/test_workstream_focus.py
python -m ruff format --check scripts/workstream_focus.py scripts/session_self_initialization.py scripts/gtkb_scoped_client.py platform_tests/hooks/test_workstream_focus.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4738-workstream-focus-dashboard-summary-timeout
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4738-workstream-focus-dashboard-summary-timeout
```

Spec-to-test mapping:

| Spec | Derived verification |
|---|---|
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Add or update focused `platform_tests/hooks/test_workstream_focus.py` coverage proving a BOM-prefixed `UserPromptSubmit` init keyword returns bounded startup-relay output even when dashboard summary refresh is slow/unavailable, and still fails visibly for unusable relay cache state. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Focused hook test proves the live-source startup path is not replaced by stale dashboard authority; any fail-soft path must disclose the degraded relay/cache state instead of fabricating authoritative startup queue state. |
| `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` | Existing startup gate tests in `platform_tests/hooks/test_workstream_focus.py` continue to pass, including normal prompt pass-through and real startup gate arming behavior. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Existing/new test exercises `::init gtkb pb` as a first-line canonical keyword and confirms it still routes through the startup relay path. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Focused tests confirm the `pb` role token remains represented in relay metadata/context without changing durable role dispatch authority. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | New bounded-path test confirms hook execution avoids unbounded startup model/dashboard summary work on the init relay hot path. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Bridge preflights pass before implementation; implementation begins only after LO `GO` and `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4738-workstream-focus-dashboard-summary-timeout`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report lists the executed tests above with per-spec mapping and outcomes. |
| `GOV-STANDING-BACKLOG-001` | `gt projects show PROJECT-GTKB-MAY29-HYGIENE --json` continues to show `WI-4738` as the governed project member being driven by this bridge thread; no new WI is added. |

## Risk / Rollback

Risk surface: the implementation touches startup hook hot-path behavior. A too-broad shortcut could weaken visible relay failures or accidentally treat cached/generated dashboard data as authoritative. A too-narrow fix could leave the subprocess timeout flaky under Windows cold-start conditions.

Rollback: revert the implementation commit and the added/updated focused tests. The bridge thread remains append-only evidence; no formal artifact mutation is proposed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4738-workstream-focus-dashboard-summary-timeout`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - repairs a reproduced startup hook timeout defect without changing the public init-keyword contract.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
