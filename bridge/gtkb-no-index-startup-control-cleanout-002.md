REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
author_model: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Startup And Control-Surface Cleanout Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-startup-control-cleanout
Version: 002
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["AGENTS.md", "CLAUDE.md", "config/agent-control/*.md", "config/agent-control/system-interface-map.toml", "scripts/session_self_initialization.py", "scripts/session_start_dispatch_core.py", ".codex/hooks.json", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "docs/gtkb-dashboard/session-startup-report.md", "docs/gtkb-dashboard/dashboard-data.json", ".codex/gtkb-hooks/last-user-visible-startup*.md", ".codex/gtkb-hooks/last-session-start.json", ".gtkb-state/startup-payload-profiles/last-codex.json", "platform_tests/scripts/test_session_self_initialization*.py", "platform_tests/hooks/test_workstream_focus.py", "bridge/gtkb-no-index-startup-control-cleanout-*.md"]

implementation_scope: startup_control_surface_no_index_cleanup
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note

This REVISED version incorporates direct owner-provided evidence from a fresh
Codex Loyal Opposition startup attempt. The screenshot showed Codex loading
`gtkb-bridge`, then planning to check `bridge/INDEX.md`, and then explicitly
choosing the automation's `bridge/INDEX.md` selection rule over newer
TAFE/dispatcher surfaces. The follow-up local sweep confirmed the generated
Codex startup payload and Codex hook cache still contain those instructions.

## Summary

The no-index sweep found active startup and control-surface instructions still
telling agents that `bridge/INDEX.md` is live authority, must be read at
startup, or must exist for startup freshness. These are agent-facing surfaces
and therefore high-risk: they are exactly the content a fresh PB/LO session
reads before deciding how to behave.

Representative evidence from the read-only sweep:

- Owner-provided Codex LO screenshot, 2026-06-15: the session says it will check `gtkb-bridge`, `bridge/INDEX.md`, backlog, and git state before review action, then states that the automation explicitly requires `bridge/INDEX.md` as queue authority and it will honor that automation selection rule.
- `.codex/gtkb-hooks/last-user-visible-startup-lo.md` says the bridge is "always available through bridge/INDEX.md", manual `bridge/INDEX.md` scans are fallback, and AXIS 2 periodically scans `bridge/INDEX.md`.
- `.codex/gtkb-hooks/last-session-start.json` says `Bridge authority: read bridge/INDEX.md directly before bridge queue claims`, marks `bridge/INDEX.md` as a required startup freshness input, and reports the payload invalid because that file is missing.
- `scripts/session_start_dispatch_core.py` still emits `Read bridge/INDEX.md directly before acting.`
- `scripts/session_self_initialization.py` still renders startup disclosures saying the bridge is always available through `bridge/INDEX.md`, requires direct reads, and marks startup freshness invalid because `bridge/INDEX.md` is missing.
- `.codex/hooks.json` still runs `single_harness_bridge_automation.py` and carries status messages about guarding `bridge/INDEX.md` atomic writes.
- `AGENTS.md` still says the live contents of `bridge/INDEX.md` are the sole authoritative source for bridge queue state and instructs LO startup to read it.
- `docs/gtkb-dashboard/session-startup-report.md` and `docs/gtkb-dashboard/dashboard-data.json` contain generated startup text that repeats stale instructions.
- `config/agent-control/system-interface-map.toml`, `SESSION-STARTUP-INDEX.md`, `LOYAL-OPPOSITION-STARTUP-OVERLAY.md`, and `REVIEW-MODE-SETUP.md` still contain active read/mutation methods that name the retired index as queue authority.

## Prior Deliberations

- `DELIB-20263438` - Owner requirement: corrected bridge-dispatch architecture; dispatch is rule-based and independent of role assignment.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - Historical startup role-confusion mitigation involving the old index; relevant because those startup assumptions must now be retired or explicitly historical.
- `DELIB-20260757` - Prior startup index and role overlay verification history; relevant to startup overlay correctness.
- `bridge/gtkb-no-index-implementation-authorization-bootstrap-003.md` - Bootstrap report proving no-index bridge authorization can work.
- `bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md` - Related design constraint: mutating GT-KB operations should move behind CLI surfaces that skills call, rather than direct agent artifact edits.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must proceed through a GO and live work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle remains governed by proposal, review, report, and verification files.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project/work authorization metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal links governing requirements for implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map tests to specifications and observed results.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher/status/health and harness registry surfaces are the dispatch topology authorities.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - dispatch routing uses roles, subjects, and activity rules rather than a retired index file.

## Requirement Sufficiency

Existing requirements are sufficient for removing `bridge/INDEX.md` as a live
startup/control authority. Mike explicitly directed that `bridge/INDEX.md` must
not exist, that backward compatibility should not be preserved, and that breaks
caused by its deletion are defects.

The broader CLI-mediated mutation-boundary requirement is tracked separately in
`bridge/gtkb-cli-mediated-agent-mutation-boundary-002.md` and requirement
candidate `INTAKE-f8bc08a3`; this proposal should align with that direction but
does not need to solve every CLI migration.

## Pre-Filing Self-Check

Preflight tooling is itself partially blocked by the retired-index dependency
for first-file bridge proposals:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-no-index-startup-control-cleanout
Expected current behavior: ERR_NO_INDEX_ENTRY until the preflight resolver is repaired.
```

Loyal Opposition should rerun applicability and clause preflights after this
file exists and should treat any preflight inability to resolve versioned files
as a defect in the preflight implementation, not as a reason to restore
`bridge/INDEX.md`.

## Proposed Implementation

1. Update startup disclosure generation so it says:
   - `bridge/INDEX.md` must not exist;
   - bridge thread state comes from versioned bridge files and dispatcher/TAFE state;
   - topology and dispatch health come from `gt bridge dispatch config|status|health`;
   - missing `bridge/INDEX.md` is healthy, not a startup freshness failure.
2. Update Codex and Claude startup dispatch surfaces so generated additional context cannot tell agents to read `bridge/INDEX.md` directly before bridge claims.
3. Update or retire Codex hook entries that invoke single-harness/index-era automation or advertise guarding `bridge/INDEX.md` atomic writes.
4. Update root/control docs (`AGENTS.md`, `CLAUDE.md`, `config/agent-control/*`) so fresh agents are not instructed to read or update the retired index.
5. Regenerate or update generated startup/dashboard outputs only through the repo's normal generation path after the source text is repaired.
6. Update focused tests so they assert no-index startup behavior and fail if generated startup text reintroduces `bridge/INDEX.md` as live authority.

## Specification-Derived Verification Plan

Run:

```powershell
Test-Path bridge\INDEX.md
rg -n -F "bridge/INDEX.md" AGENTS.md CLAUDE.md config\agent-control scripts\session_self_initialization.py scripts\session_start_dispatch_core.py .codex\hooks.json .codex\gtkb-hooks docs\gtkb-dashboard\session-startup-report.md docs\gtkb-dashboard\dashboard-data.json platform_tests\scripts platform_tests\hooks
rg -n "Bridge authority: read|always available through bridge/INDEX|manual bridge/INDEX|AXIS 2.*bridge/INDEX|required.*bridge/INDEX|startup.*invalid.*bridge/INDEX|Guarding bridge/INDEX" .codex\gtkb-hooks .codex\hooks.json scripts\session_self_initialization.py scripts\session_start_dispatch_core.py
python -m pytest platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py -q --tb=short
python -m ruff check scripts\session_self_initialization.py scripts\session_start_dispatch_core.py platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py
python -m ruff format --check scripts\session_self_initialization.py scripts\session_start_dispatch_core.py platform_tests\scripts\test_session_self_initialization.py platform_tests\hooks\test_workstream_focus.py
gt bridge dispatch config
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Expected:

- `Test-Path bridge\INDEX.md` returns `False`.
- Active startup/control surfaces no longer instruct agents to read, update, or require the retired index.
- Generated Codex startup payloads no longer mark absent `bridge/INDEX.md` as an invalid freshness condition.
- Codex hook configuration no longer invokes index-era bridge automation as a startup/stop authority unless it has been rebuilt to use no-index dispatcher state.
- Any remaining `bridge/INDEX.md` mention in target files is explicitly historical or a negative test.
- Startup freshness no longer fails solely because the retired index is absent.
- Dispatcher config/status/health remain the live operational health surfaces.

## Risks

- Startup content is a high-leverage prompt surface; partial cleanup could leave agents receiving contradictory instructions in generated caches even after source text is corrected.
- Some generated files may be safe to regenerate rather than hand-edit. The implementation must identify source-of-truth files and avoid making generated outputs the only repaired surface.
- Removing old single-harness automation hooks without replacement could temporarily reduce automatic surfacing of interactive/AUQ-heavy work. The implementation should either route that behavior through dispatcher/TAFE state or explicitly preserve it as a separate follow-up if it cannot be safely migrated in this slice.

## Rollback

Revert changes in the target files. Do not recreate `bridge/INDEX.md`; a
rollback that depends on that file violates the owner directive and masks the
defect.
