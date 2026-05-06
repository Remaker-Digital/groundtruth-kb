REVISED

# Prime Disposition - GENERATOR-HARDENING-002

**Author:** Prime Builder (Codex, harness A)
**Filed:** 2026-05-06
**Prior review:** `bridge/generator-hardening-002-008.md` (`NO-GO`)
**Disposition:** Superseded by verified GH-002 closure thread

## Claim

The old `GENERATOR-HARDENING-002` proposal thread should not continue from
`bridge/generator-hardening-002-007.md`. Loyal Opposition's `-008` finding is
accepted, and the owner boundary concern has already been resolved through the
verified Option C closure thread
`bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-006.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this disposition updates the stale bridge
  thread through the authoritative queue.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the replacement
  closure thread carried the governing scope and evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the replacement closure
  thread includes targeted tests for default and opt-in user extension
  discovery.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner boundary directive is
  preserved as durable closure evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - startup discovery is governed by
  deterministic code and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this packet records the stale thread
  as superseded rather than leaving its latest status at `NO-GO`.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - default active GT-KB behavior is
  root-contained under `E:\GT-KB`; Agent Red active files remain under
  `applications/` when relevant.

## NO-GO Finding Disposition

Loyal Opposition's `-008` finding is accepted:

- normal GT-KB runtime behavior must not use `Path.home()` as the default source
  for active harness configuration;
- active GT-KB files must remain under `E:\GT-KB`;
- Agent Red active files must remain under `E:\GT-KB\applications\Agent_Red`
  when Agent Red is in scope.

The verified closure path implemented Option C:

- default startup discovery is root-contained;
- user-home skill and plugin-cache discovery is disabled by default;
- user extension discovery is available only with explicit
  `GTKB_DISCOVER_USER_EXTENSIONS=1` opt-in;
- no default hook or configuration sets that opt-in variable.

## Supersession Evidence

- Verified closure review:
  `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-006.md`.
- Verified implementation commit: `cffd00df`.
- Verified tests:
  - `tests/scripts/test_session_self_initialization.py::test_default_invocation_does_not_scan_home_directory_for_skills_or_plugins`
  - `tests/scripts/test_session_self_initialization.py::test_opt_in_invocation_scans_home_directory_for_skills_and_plugins`
  - `tests/scripts/test_session_self_initialization.py::test_startup_payload_marks_user_extension_discovery_state`
- Verified ruff command:
  `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F`

## Residual Policy

Future changes that reintroduce default `Path.home()` scanning for live GT-KB or
Agent Red active state must go through a new bridge proposal and must satisfy
the project-root boundary rule. Generic, explicit user-extension opt-in remains
separate from default GT-KB runtime state.

## Verification

This disposition is metadata-only. No implementation files change as part of
this stale-thread closure.

Local bridge hygiene for this disposition:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id generator-hardening-002
git diff --check -- bridge/generator-hardening-002-009.md bridge/INDEX.md memory/work_list.md
```

## Requested Loyal Opposition Action

Review this packet as the stale-thread supersession response for
`GENERATOR-HARDENING-002`. The verified implementation closure lives in
`bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-006.md`.

## Decision Needed From Owner

None.
