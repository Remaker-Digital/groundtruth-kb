NEW

# GTKB Work Subject And Root Enforcement - Foundation Implementation Proposal

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-007]
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", "scripts/session_self_initialization.py", "tests/hooks/test_workstream_focus.py", "tests/scripts/test_session_self_initialization.py", "tests/scripts/test_codex_hook_parity.py"]

## Requested Verdict

GO to implement the narrow Phase 7 foundation slice below, or NO-GO with
required revisions.

## Parent GO Inputs

This proposal is the first concrete implementation slice after the accepted
planning set below:

- `bridge/gtkb-isolation-003-environment-plan-review-002.md`
- `bridge/gtkb-isolation-004-service-boundary-plan-review-002.md`
- `bridge/gtkb-isolation-005-control-plane-plan-review-002.md`
- `bridge/gtkb-isolation-006-overlay-plan-review-003.md`
- `bridge/gtkb-session-work-subject-004.md`
- `bridge/gtkb-isolation-007-work-subject-root-plan-review-003.md`

Those reviews accepted the planning artifacts and required a later concrete
implementation proposal before behavior changes. This bridge is that next Prime
step.

## Claim

The correct first implementation slice is app-local and foundation-only:

1. replace the current workstream-focus runtime state with canonical
   work-subject state while preserving one migration window for legacy aliases
   and state,
2. update startup and hook messaging so operating role and work subject are not
   conflated, and
3. replace prefix-only mutation guards with a resolved-root-aware classifier for
   application paths, current-repo bridge/governance surfaces, and GT-KB
   product paths.

This slice should not yet implement dashboard control-plane mutation,
session-overlay mechanics, or upstream GT-KB scaffold/doctor delivery.

## Current Evidence

### Existing Workstream-Focus Surface

- `scripts/workstream_focus.py` currently stores canonical local state at
  `.claude/hooks/.workstream-focus-state.json`, uses `Application Focus` /
  `GT-KB Infrastructure Focus` labels, and blocks writes through static path
  prefix tables.
- `.claude/hooks/workstream-focus.py` is a thin adapter that imports
  `scripts/workstream_focus.py`, so the behavior is effectively centralized
  already.
- `scripts/session_self_initialization.py` imports the same module and renders
  `Default focus` / `Current focus` into startup output.

### Existing Test Baseline

- `tests/hooks/test_workstream_focus.py` and
  `tests/scripts/test_session_self_initialization.py` still assert the legacy
  focus labels and state shape.
- `tests/scripts/test_codex_hook_parity.py` verifies the hook wrapper still
  routes through `workstream-focus.py`.

### Why This Slice Is First

- Phase 3 requires application-subject environments and local harnesses to stop
  treating GT-KB product paths as ordinary writable workspace by default.
- Phase 4 rejects raw parent-root and raw DB authority for ordinary app work,
  so this first slice must remain app-local and avoid introducing broader
  service authority.
- Phase 5 accepted typed control-plane and generated projection concepts, but
  those remain planning only and should not be mixed into the first behavior
  migration.
- Phase 6 requires overlays to remain non-authoritative, which means the first
  slice should read and write canonical local state directly rather than
  introducing overlay persistence early.
- Phase 7 requires durable work-subject state, command precedence, startup/test
  scoping, root-boundary checks, and clear separation between operating role,
  work subject, root, and bridge role slot.

## Scope

Implement only:

1. Canonical work-subject state in an app-local runtime file.
2. Legacy state migration and alias compatibility.
3. Work-subject command parsing for `work subject application` and
   `work subject GT-KB`, with current focus aliases preserved for one migration
   window.
4. Resolved-root-aware guard behavior for current-repo application paths,
   current-repo bridge/governance surfaces, and GT-KB product paths.
5. Startup/report language updates from `focus` to `work subject`, while
   preserving the Prime Builder / Loyal Opposition role split and live bridge
   authority language.
6. Regression tests for state migration, startup output, hook parity, alias
   handling, and root-guard behavior.

Do not implement in this slice:

- dashboard control-plane mutation UI or operation registry,
- bridge writer/validator mechanics,
- `DEFERRED` / dispatcher mute semantics from `GTKB-GOV-008`,
- session-overlay persistence or promotion,
- upstream GT-KB scaffold/doctor/preflight/template delivery,
- migration rehearsal or repository moves.

## Proposed State Contract

Replace the current canonical state path with:

```text
.groundtruth/session/work-subject.json
```

Schema for this slice:

```json
{
  "schema_version": 1,
  "current_subject": "application",
  "updated_at": "2026-04-23T00:00:00Z",
  "updated_by": "owner_prompt|legacy_migration|default",
  "source": "standalone owner command|legacy workstream alias|startup default",
  "project_root": "absolute application root",
  "gtkb_root": "absolute GT-KB root or null",
  "role_slot": "shared"
}
```

Compatibility behavior:

- Read `.claude/hooks/.workstream-focus-state.json` for one migration window.
- If valid legacy state exists and the canonical file is absent, write the new
  canonical file lazily on the next successful command-handling path.
- Continue accepting legacy aliases such as `application mode`, `app mode`,
  `agent red mode`, `GT-KB mode`, and `GT-KB infrastructure mode`.
- New user-facing startup and hook messages should prefer `work subject`.

## Proposed Root And Guard Behavior

### Root classification

Introduce resolved-root helpers in `scripts/workstream_focus.py` to classify a
candidate write target as:

- `application_product`
- `current_repo_bridge_or_governance`
- `gtkb_product`
- `neutral`

For the first slice:

- `application_product` is the current repository root plus its application
  product paths.
- `current_repo_bridge_or_governance` includes live bridge and current-repo
  governance/process surfaces such as `bridge/`, selected
  `independent-progress-assessments/bridge-automation/` files, and startup/
  guard files required for current-repo bridge use.
- `gtkb_product` is resolved from either:
  - an explicit local override such as `GTKB_PRODUCT_ROOT`, or
  - a discovered sibling checkout when present and resolvable.

### Guard rules

- In `application` subject, block mutating resolved `gtkb_product` targets.
- In `GT-KB` subject, block mutating resolved `application_product` targets
  unless the task is an explicitly named migration/adopter path handled in a
  later slice.
- Do not block `current_repo_bridge_or_governance` paths merely because the
  subject is `application`; those are current-repo governance/process surfaces,
  not GT-KB product-root writes.
- Keep unresolved or unknown external paths conservative: do not silently
  classify them as safe GT-KB writes.

### Message contract

Required message shape:

```text
Current work subject is application. This change targets GT-KB product
artifacts. Switch with standalone `work subject GT-KB` before proceeding.
```

## Proposed File Touchpoints

Primary code:

- `scripts/workstream_focus.py`
- `.claude/hooks/workstream-focus.py`
- `scripts/session_self_initialization.py`

Tests:

- `tests/hooks/test_workstream_focus.py`
- `tests/scripts/test_session_self_initialization.py`
- `tests/scripts/test_codex_hook_parity.py`

The implementation may add one new focused test module if the current test files
become too broad for root-classification coverage.

## Implementation Sequence

1. Add canonical work-subject state helpers and legacy-state migration.
2. Add `work subject ...` command handling while preserving current aliases.
3. Replace focus labels/messages with work-subject labels in shared startup and
   hook rendering.
4. Add resolved-root helpers and update guard decisions to distinguish current
   repo bridge/governance paths from GT-KB product-root paths.
5. Update regression tests for startup text, alias compatibility, canonical
   state path, and root-guard behavior.

## Verification Commands

Required focused checks:

```powershell
python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_session_self_initialization.py tests/scripts/test_codex_hook_parity.py -q --tb=short
```

Recommended broader check after focused green:

```powershell
python -m pytest tests/hooks/ tests/scripts/ -q --tb=short
```

## Review Questions

1. Is limiting the first slice to app-local work-subject state, startup text,
   and resolved-root guard behavior sufficiently narrow?
2. Is treating current-repo bridge/governance surfaces as distinct from GT-KB
   product-root paths the correct first-slice boundary?
3. Is `GTKB_PRODUCT_ROOT` plus sibling-checkout discovery acceptable for the
   first resolved-root implementation, with richer topology/config integration
   deferred?
4. Is preserving legacy alias commands for one migration window acceptable, so
   existing tests and operator habits can move incrementally?

## Non-Scope Reminder

This proposal does not request immediate control-plane operations, bridge
writer/validator mechanics, overlay implementation, or upstream GT-KB template
delivery. Those remain later slices after the foundation migration lands.
