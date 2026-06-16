NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Startup And Control-Surface Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-startup-control-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["AGENTS.md", "CLAUDE.md", "config/agent-control/*.md", "config/agent-control/system-interface-map.toml", "scripts/session_self_initialization.py", "docs/gtkb-dashboard/session-startup-report.md", "docs/gtkb-dashboard/dashboard-data.json", ".codex/gtkb-hooks/last-user-visible-startup*.md", ".codex/gtkb-hooks/last-session-start.json", "platform_tests/scripts/test_session_self_initialization*.py", "platform_tests/hooks/test_workstream_focus.py", "bridge/gtkb-no-index-startup-control-cleanout-*.md"]

implementation_scope: startup_control_surface_no_index_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The no-index sweep found active startup and control-surface instructions still telling agents that `bridge/INDEX.md` is live authority, must be read at startup, or must exist for startup freshness. These are agent-facing surfaces and therefore high-risk: they are exactly the content a fresh PB/LO session reads before deciding how to behave.

Representative evidence from the read-only sweep:

- `AGENTS.md` still says the live contents of `bridge/INDEX.md` are the sole authoritative source for bridge queue state and instructs LO startup to read it.
- `scripts/session_self_initialization.py` still renders startup disclosures saying the bridge is always available through `bridge/INDEX.md`, requires direct reads, and marks startup freshness invalid because `bridge/INDEX.md` is missing.
- `docs/gtkb-dashboard/session-startup-report.md` and `docs/gtkb-dashboard/dashboard-data.json` contain generated startup text that repeats the same stale instructions.
- `config/agent-control/system-interface-map.toml`, `SESSION-STARTUP-INDEX.md`, `LOYAL-OPPOSITION-STARTUP-OVERLAY.md`, and `REVIEW-MODE-SETUP.md` still contain active read/mutation methods that name the retired index as queue authority.

## Prior Deliberations

- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture; dispatch is rule-based and independent of role assignment.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - Historical startup role-confusion mitigation involving the old index; relevant because those startup assumptions must now be retired or explicitly historical.
- `DELIB-20260757` - Prior startup index and role overlay verification history; relevant to startup overlay correctness.
- `bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` - Bootstrap report proving no-index bridge authorization can work.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle remains governed by proposal, review, report, and verification files.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project/work authorization metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal links governing requirements for implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to specifications and observed results.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health and harness registry surfaces are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing uses roles, subjects, and activity rules rather than a retired index file.

## Requirement Sufficiency

Existing requirements are sufficient. Mike explicitly directed that `bridge/INDEX.md` must not exist, that backward compatibility should not be preserved, and that breaks caused by its deletion are defects. Startup and control-surface text that tells agents to use the deleted file is a direct implementation defect.

## Pre-Filing Self-Check

Preflight tooling is itself partially blocked by the retired-index dependency for first-file bridge proposals:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-startup-control-cleanout
Expected current behavior: ERR_NO_INDEX_ENTRY until the preflight resolver is repaired.
```

Loyal Opposition should rerun applicability and clause preflights after this file exists and should treat any preflight inability to resolve versioned files as a defect in the preflight implementation, not as a reason to restore `bridge/INDEX.md`.

## Proposed Implementation

1. Update startup disclosure generation so it says:
   - `bridge/INDEX.md` must not exist;
   - bridge queue/thread state comes from versioned bridge files and dispatcher/TAFE state;
   - topology and dispatch health come from `gt bridge dispatch config|status|health`;
   - missing `bridge/INDEX.md` is healthy, not a startup freshness failure.
2. Update root/control docs (`AGENTS.md`, `CLAUDE.md`, `config/agent-control/*`) so fresh agents are not instructed to read or update the retired index.
3. Regenerate or update generated startup/dashboard outputs only through the repo's normal generation path after the source text is repaired.
4. Update focused tests so they assert no-index startup behavior and fail if generated startup text reintroduces `bridge/INDEX.md` as live authority.

## Spec-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n -F "bridge/INDEX.md" AGENTS.md CLAUDE.md config\agent-control scripts\session_self_initialization.py docs\gtkb-dashboard\session-startup-report.md docs\gtkb-dashboard\dashboard-data.json .codex\gtkb-hooks platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py
python -m pytest platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py -q --tb=short
python -m ruff check scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py
python -m ruff format --check scripts\session_self_initialization.py platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Active startup/control surfaces no longer instruct agents to read, update, or require the retired index.
- Any remaining `bridge/INDEX.md` mention in target files is explicitly historical or a negative test.
- Startup freshness no longer fails solely because the retired index is absent.

## Risks

- Startup content is a high-leverage prompt surface; partial cleanup could leave agents receiving contradictory instructions in generated caches even after source text is corrected.
- Some generated files may be safe to regenerate rather than hand-edit. The implementation must identify source-of-truth files and avoid making generated outputs the only repaired surface.

## Rollback

Revert changes in the target files. Do not recreate `bridge/INDEX.md`; a rollback that depends on that file violates the owner directive and masks the defect.
