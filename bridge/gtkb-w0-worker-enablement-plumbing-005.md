NEW
::init gtkb pb
::open build

# GT-KB Bridge Implementation Report - gtkb-w0-worker-enablement-plumbing - 005

bridge_kind: implementation_report
Document: gtkb-w0-worker-enablement-plumbing
Version: 005 (NEW; post-implementation report)
Responds to: bridge/gtkb-w0-worker-enablement-plumbing-004.md
Approved proposal: bridge/gtkb-w0-worker-enablement-plumbing-003.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5839
Recommended commit type: feat:
kb_mutation_in_scope: false

**No KB mutation.** This implementation report performs no MemBase write and
does not modify `groundtruth.db`. Its entire scope is the declared source/test
target paths below.

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: 235a0cb7-2d12-4241-9951-a54c73c301f8
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity
author_metadata_source: session envelope (worker_role_provenance)

## Implementation Claim

W0.1 Thread B (worker-enablement plumbing) implemented the three live-anchor
fixes and their focused coverage:

1. `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` — added
   `"goose": "GOOSE_SESSION_ID"` to `_HOST_SESSION_ID_ENV_BY_HARNESS`, so
   `gt session envelope open --harness-name goose` binds a pre-set
   `GOOSE_SESSION_ID` instead of minting/ignoring a different id. This aligns
   the envelope-open CLI with `gtkb_session_id.py` and
   `session/envelope.py`, eliminating the claim-time id-mismatch denial class.
2. `scripts/harness_identity.py` — added `"goose": "G"` to
   `DEFAULT_HARNESS_IDS`, matching the owner-registered goose identity.
3. `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` —
   `mint_bridge_publication_capability` now resolves its default TTL through
   `timer_config.resolve_protected_commit_timers` when the caller passes no
   explicit value (signature default changed from hard-coded 120 to `None`).
   The 800-second ceiling and explicit-value support are unchanged.
4. `scripts/gtkb_bridge_writer.py` — the single production mint call now
   resolves the timer pair and passes
   `ttl_seconds=timers.bridge_publication_capability_ttl_seconds`, so the
   writer's publication window matches the configured pair (800s), no longer
   the 120s default.

Tests:
- New `platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py`
  asserting the mint default is resolution-routed, equals the config-backed
  resolver value, the 800s ceiling is still enforced for explicit values, and
  the writer's mint call carries the resolved TTL.
- Extended `platform_tests/scripts/test_session_envelope_cli_choice.py` with a
  goose envelope-open binding case (pre-set `GOOSE_SESSION_ID` binds that
  exact id).
- Extended `platform_tests/scripts/test_gtkb_session_id.py` with a
  `DEFAULT_HARNESS_IDS` goose==G assertion.

The scratch-tree hygiene defects (`.tmp-lo-verdict-drafts/`, `.driveignore`)
remain OUT OF SCOPE and routed to the W0.2 custodial lane per the approved
proposal; they were NOT touched.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `WI-5839`
- `DELIB-20260803084763`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `WI-5849`
- `WI-5368`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The bounded
PAUTH `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` was
verified active at implementation-start; the active GO (v004), matching
work-intent claim, and implementation-start authorization packet were all in
place before any protected file mutation. The W0.2 custodial routing for the
scratch-tree hygiene defects follows the approved -002 LO verdict F1 remedy.

## Prior Deliberations

- `bridge/gtkb-w0-worker-enablement-plumbing-003.md` - approved implementation proposal carried forward.
- `bridge/gtkb-w0-worker-enablement-plumbing-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths under `E:\GT-KB` (`groundtruth-kb/src/...`, `scripts/`, `platform_tests/scripts/`); no adopter-application scope touched. |
| `WI-5839` | Mint TTL wiring (default resolves through timer_config; writer passes resolved TTL) implemented and covered. |
| `DELIB-20260803084763` | W0.2 custodial split respected; hygiene defects not mutated by this thread. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | `resolve_protected_commit_timers` (single resolution path incl. env override) left intact; no config-file or timer_config change. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge publication capability mint/consume unchanged except TTL resolution; no bridge-authority behavior weakened. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All relevant governing specs linked; applicability/clause preflights passed at GO (v004). |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | WI-5839 bound to PROJECT-GTKB-HOUSEKEEPING-HARDENING via active PAUTH; confirmed in implementation-start packet. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests executed (see Commands Run); 31 passed in focused suites. |
| `GOV-WORK-TREE-HYGIENE-001` | Only the 7 declared target paths changed; 623 unrelated dirty paths excluded. |
| `WI-5849` | Publication-capability recovery relationship preserved; no capability-evidence behavior removed. |
| `WI-5368` | Bridge publication capability path remains typed and exact; no regression to writer publication. |

## Commands Run

- `"E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" -m pytest platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py platform_tests/scripts/test_session_envelope_cli_choice.py platform_tests/scripts/test_gtkb_session_id.py -q --tb=short`
- `"E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" -m pytest groundtruth-kb/tests/test_registry_control_plane.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_helper_publication_capability.py -q --tb=short`
- `"E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" -m ruff check <changed files>`
- `"E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" -m ruff format --check <changed files>`

## Observed Results

- Focused suites: `31 passed` (new TTL-sizing tests + extended envelope-cli and session-id tests).
- Regression suites: `114 passed, 2 failed` — the 2 failures are pre-existing,
  WI-5942-owned helper tests
  (`platform_tests/scripts/test_bridge_helper_publication_capability.py`:
  `test_helper_has_mint_consume_integration`,
  `test_helper_source_has_wj5942_marker`) asserting WI-5942 markers in
  `.goose/skills/gtkb-bridge-propose/helpers/write_bridge.py`, which this
  thread does not touch; they are tracked by the WI-5942 bridge thread and are
  unrelated to this implementation.
- Ruff check: `All checks passed!`; Ruff format --check: all files formatted
  after `ruff format` was applied to the two new/extended test files.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_session_id.py`
- `platform_tests/scripts/test_session_envelope_cli_choice.py`
- `scripts/gtkb_bridge_writer.py`
- `scripts/harness_identity.py`
- `platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py` (new)

Excluded out-of-scope dirty paths: 623.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: adds goose session binding, harness-identity G, mint
  TTL SoT resolution, writer TTL pass-through, and focused tests.

```text
     .../src/groundtruth_kb/cli_session_handoff.py      |  1 +
     .../project/registry_control_plane.py              |  7 ++++-
     platform_tests/scripts/test_gtkb_session_id.py     |  7 +++++
     .../scripts/test_session_envelope_cli_choice.py    | 31 ++++++++++++++++++++++
     scripts/gtkb_bridge_writer.py                      |  6 +++++
     scripts/harness_identity.py                        |  1 +
     6 files changed, 52 insertions(+), 1 deletion(-)
     (new file platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py)
```

## Acceptance Criteria Status

- Goose envelope-open binds a pre-set `GOOSE_SESSION_ID` (A: `_HOST_SESSION_ID_ENV_BY_HARNESS` now maps `goose`) — MET, covered by `test_goose_envelope_open_binds_preset_session_id`.
- `DEFAULT_HARNESS_IDS` includes `goose` == `G` — MET, covered by `test_default_harness_ids_include_goose_g`.
- Mint default resolves through `timer_config` (no hard-coded 120) with the 800s ceiling preserved — MET, covered by TTL-sizing tests.
- Writer's single production mint call passes the resolved TTL — MET, covered by `test_writer_mint_call_carries_resolved_ttl`.
- No config-file or `timer_config.py` change; 800s ceiling unchanged — MET (no such file modified).
- Scratch-tree hygiene defects untouched (routed to W0.2) — MET.

## Risk And Rollback

Residual risk is low and bounded to the seven declared target paths. The mint
TTL default change (120 -> resolve-through-SoT) preserves the 800-second
ceiling and explicit-value override, so no publication window can exceed the
configured bound. Rollback is the revert of the seven changed files under
separately governed Git mechanics; bridge audit files and project-authorization
records are append-only and must not be deleted by rollback. No unrelated
source or test file was modified.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.

---

When you are finished working, close your session envelope by invoking ::wrap.
