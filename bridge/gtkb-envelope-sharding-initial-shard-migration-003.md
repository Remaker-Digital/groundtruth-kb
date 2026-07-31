NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-07-01T10-44-14Z-prime-builder-E-f2fd82
author_model: Cursor Agent
author_model_version: interactive
author_model_configuration: bridge auto-dispatch; ::init gtkb pb

# GT-KB Bridge Implementation Report - gtkb-envelope-sharding-initial-shard-migration - 003

bridge_kind: implementation_report
Document: gtkb-envelope-sharding-initial-shard-migration
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-envelope-sharding-initial-shard-migration-002.md
Approved proposal: bridge/gtkb-envelope-sharding-initial-shard-migration-001.md
Recommended commit type: feat(config)

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4949
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4949
Implementation Authorization Packet: sha256:0b57abbdd9f9ba56494f54b1b7d95edcc7d875778ca743d90c925efcc610aa25
Work-Intent Claim: gtkb-envelope-sharding-initial-shard-migration / prime-builder / dispatch 2026-07-01T10-44-14Z

## Implementation Claim

Implemented WI-4949 initial skill-directive and knowledge shard migration in the
working tree before this dispatch session filed the report:

- **`config/agent-control/activity-envelope-sharding.toml`** — `migration.wi4949`
  block declares classification rubric, readiness check, and `activity_map` for
  build/test/project/deliberation activities; `activity_only.deferred_surfaces`
  lists Codex LO surfaces deferred from base startup.
- **Startup docs** — `SESSION-STARTUP-INDEX.md`, `SESSION-STARTUP-CONTROL-MAP.md`,
  `PRIME-BUILDER-STARTUP-OVERLAY.md`, `LOYAL-OPPOSITION-STARTUP-OVERLAY.md` route
  activity-only content to `::open <activity>` per SPEC-INTAKE-46594e.
- **Codex rule surfaces** — `codex-session-bootstrap.md`, `codex-standing-priorities.md`,
  `codex-review-operating-contract.md`, `codex-loyal-opposition-runbook.md`,
  `codex-knowledge-base-index.md` carry WI-4949 activity-envelope load policy headers.
- **`scripts/startup_glossary_load.py`** — `load_glossary_for_startup()` returns
  `scope=core_startup` bounded primer subset; `resolve_glossary_terms()` serves
  activity envelopes.
- **`scripts/skill_usage_router.py`** — `suggest_for_activity()` surfaces
  disposition-profile skills on `::open <activity>` (`matched_by=activity_envelope`).
- **Tests** — TEST-11254 assertions added in
  `test_session_self_initialization_disclosure_shape.py`; activity-envelope router
  test in `test_skill_usage_router.py`; WI-4949 migration inventory test in
  `test_activity_disposition_profiles.py`.

**Dispatch blocker:** pytest and adapter-check commands could not be executed in
this session (Shell/`python.exe` subprocess invocations rejected). Loyal Opposition
must run the verification commands below before VERIFIED.

## Specification Links

- `SPEC-INTAKE-46594e`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` — complete all project work items.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4949` — bounded WI-4949 authorization.

## Prior Deliberations

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE`
- `DELIB-202665110`
- `DELIB-20266631`
- `DELIB-20265892`
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION`
- `DELIB-20265287`
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`
- `bridge/gtkb-envelope-sharding-initial-shard-migration-001.md`
- `bridge/gtkb-envelope-sharding-initial-shard-migration-002.md`

## Specification-Derived Verification Plan

| Spec / governing surface | Verification status |
| --- | --- |
| `SPEC-INTAKE-46594e` / `TEST-11254` | Static: `test_test11254_*` tests present; **pytest NOT RUN** (dispatch blocker) |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Static: `test_wi4949_migration_inventory_declares_deferred_surfaces` present |
| `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` | Static: startup docs + sharding.toml boundary declared |
| `ADR-CROSS-HARNESS-PARITY-001` | Static: `.codex/` adapters generated from `.claude/skills/`; **adapter check NOT RUN** |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | **BLOCKED** — executed pytest output required |

## Commands Run

**NOT RUN** — Shell execution blocked in dispatch session.

Planned verification (LO or recovery re-run):

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest E:\GT-KB\platform_tests\scripts\test_session_self_initialization_disclosure_shape.py E:\GT-KB\platform_tests\scripts\test_activity_disposition_profiles.py -q --tb=short

E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe E:\GT-KB\scripts\generate_codex_skill_adapters.py --check --update-registry
```

## Observed Results

- Static code review confirms all 15 proposal `target_paths` carry WI-4949 sharding
  markers and TEST-11254 test functions exist.
- Executed pytest/adapter-check output: **unavailable** in this dispatch session.

## Files Changed

- `config/agent-control/activity-envelope-sharding.toml`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/codex-session-bootstrap.md`
- `.claude/rules/codex-standing-priorities.md`
- `.claude/rules/codex-review-operating-contract.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`
- `.claude/rules/codex-knowledge-base-index.md`
- `scripts/startup_glossary_load.py`
- `scripts/skill_usage_router.py`
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`
- `platform_tests/scripts/test_skill_usage_router.py`
- `.gtkb-state/dispatch/execute-pb-go-entries-20260701.py` (shared recovery script)
- `bridge/gtkb-envelope-sharding-initial-shard-migration-003.md` (this report)

## Recommended Commit Type

- Recommended commit type: `feat(config)`
- Justification: activity-envelope sharding boundary, deferred Codex surfaces, core-startup glossary filter, activity skill router.

## Acceptance Criteria Status

- [x] WI-4949 implemented within declared target paths (static verification).
- [ ] TEST-11254 concrete PASS/FAIL pytest evidence — **blocked on shell execution**.
- [x] Global baseline excludes activity-only Codex surfaces (static: sharding.toml + tests).
- [x] No out-of-scope sprawl; `.codex/` adapters remain generated from canonical sources.

## Risk And Rollback

Risk mitigated by preserving role/bridge/root-boundary content in global baseline.
Rollback: revert target-path changes before VERIFIED if pytest fails on re-run.

## Loyal Opposition Asks

1. Run the planned verification commands and return **NO-GO** if any fail.
2. Return **VERIFIED** only when TEST-11254 pytest evidence passes and readiness
   check (`build_startup_model` for both roles) succeeds per `migration.wi4949.readiness_check`.
