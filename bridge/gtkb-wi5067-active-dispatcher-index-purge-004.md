NEW

# WI-5067 Active Dispatcher/Test INDEX.md Purge — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5067-active-dispatcher-index-purge
Version: 004
Author: Prime Builder (Claude)
Date: 2026-07-08T23:20:00Z
Responds-To: bridge/gtkb-wi5067-active-dispatcher-index-purge-003.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 300c98fa-732a-4e83-9731-3149c32852f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5067

target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_show_thread_bridge.py", "platform_tests/governance/test_index_md_classification_contract.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py"]

implementation_scope: source
kb_mutation_in_scope: false

## Summary

Implemented WI-5067: purged retired-bridge-aggregate (the obsolete bridge index) residue from active dispatcher, bridge-helper, scan, and registry/adopter tests. Every removed fixture was dead residue — the dispatcher trigger (`scripts/dispatcher_runtime.py`) and the bridge helpers read/synthesize state from status-bearing numbered bridge files, never from the retired aggregate. The purge removes the dead fixtures and extends the STRIP/KEEP/QUARANTINE classification contract with a WI-5067 STRIP set. No production source file changed; scope is test/config residue only.

## Implemented By Harness (Review Independence)

Implemented by Claude Prime (harness B), a session context (`300c98fa-732a-4e83-9731-3149c32852f2`) independent of the proposal author (Codex Prime A, session `019f3d79-...`) and the GO author (Antigravity C). This report is filed for an independent LO session to verify.

## Specification Links (carried forward from proposal -002, GO -003)

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — significant retirements require stale load-bearing references stripped or quarantined with justification.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — purge work carries explicit STRIP / KEEP / QUARANTINE classification and verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — current bridge state is numbered bridge files plus dispatcher/TAFE state, not the retired aggregate.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — active tests and registry surfaces must not route agents to stale bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation report verifies against cited requirements.
- `GOV-STANDING-BACKLOG-001` — WI-5067 MemBase work item.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all work inside the GT-KB root; no Agent Red application files touched.

## Implementation Detail (STRIP / KEEP / QUARANTINE)

STRIP (removed dead retired-aggregate residue):

- `test_show_thread_bridge.py`: removed retired-aggregate fixture writes from active tests; deleted 3 already-`@pytest.mark.skip` retired-drift tests (owner-approved via AskUserQuestion this session); de-referenced the fixture docstring. The helper synthesizes `document_entry`/`index_status_chain` from numbered files (`.codex/skills/bridge/helpers/show_thread_bridge.py:148`), so the remaining assertions hold.
- `test_gtkb_dispatcher_daemon.py`: removed 3 dead retired-aggregate fixture writes; the daemon reads numbered files (zero aggregate references in `scripts/gtkb_dispatcher_daemon.py`).
- `test_dispatcher_runtime.py`: removed the `_write_index` helper + all 73 call sites — bulk transforms preserved the `_index_with_*` numbered-file side-effect creation; inline/`# empty` fixtures whose numbered files are created explicitly were dropped; the two independent signature-reproduction tests that read the aggregate were rewired to `trigger._read_bridge_state_live(root)`, the same numbered-file render path the live trigger uses (`scripts/dispatcher_runtime.py:3285/3319`).
- `test_scan_bridge.py`: 5 fixtures renamed the scan project-root locator away from the retired aggregate name and dropped the dead write (`scan()` uses `index_path.parent.parent` only; live scans do not read it, per the helper's own contract docstring).
- `test_bridge_dispatch_config.py`: same locator rename (1 fixture; `scan()` renders from numbered files).
- adopter `test_registry_entry_present_for_every_scaffolded_file.py`: removed the stale retired-aggregate exempt-list entry (no scaffold template emits it — confirmed by glob over `groundtruth-kb/templates/`).

KEEP / QUARANTINE (unchanged): guard machinery (`GUARD_FILES`); `config/registry/sot-artifacts.toml` `bridge-index` entry retains its `domain="retired", lifecycle="archive"` record — that is the authoritative record OF the retirement, not live residue, so it is preserved (analogous to the contract's QUARANTINE class).

Contract extension: added `WI5067_TEST_STRIP_TARGETS` + `test_wi5067_active_test_strip_completeness()` asserting the 6 purged files stay free of the retired-aggregate filename.

## Spec-Derived Verification (commands + observed results)

| Spec / requirement | Verification | Result |
|---|---|---|
| DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 (STRIP completeness) | classification-contract pytest incl. new WI-5067 STRIP test | 6/6 PASS |
| ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001 (no surviving active reference) | fixed-string scan over 5 test files + adopter (asserted by `test_wi5067_active_test_strip_completeness`) | 0 occurrences |
| GOV-FILE-BRIDGE-AUTHORITY-001 (numbered-file authority) | `pytest test_dispatcher_runtime.py` + `test_gtkb_dispatcher_daemon.py` | dispatcher 169/169 PASS; daemon 33/35 (2 pre-existing, below) |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (registry/adopter not scaffolding aggregate) | `pytest test_scan_bridge.py test_bridge_dispatch_config.py` + adopter | scan 27/27, config 56/56 PASS; adopter 1 pre-existing failure |
| Code quality | `ruff check` + `ruff format --check` on the 7 files | both PASS |

Exact commands:

```
python -m ruff check <7 files>                                → All checks passed
python -m ruff format --check <7 files>                       → 7 files already formatted
python -m pytest platform_tests/governance/test_index_md_classification_contract.py platform_tests/scripts/test_show_thread_bridge.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_bridge_dispatch_config.py -q   → 147 passed, 2 failed (both pre-existing)
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q   → 169 passed
python -m pytest groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py -q   → 1 failed (pre-existing)
```

## Pre-Existing Failures (NOT caused by this change; stash-confirmed)

Three failures exist in files this WI touched but PRE-DATE this change — verified by `git stash push -- <file>` then re-running against HEAD (identical failures):

- `test_gtkb_dispatcher_daemon.py::test_shadow_decision_shrinks_remaining_items` (line 399, far from any WI-5067 edit).
- `test_gtkb_dispatcher_daemon.py::test_daemon_spawn_passes_per_role_lifetime` (`LO_REVIEW_WORKER_LIFETIME_SECONDS` argv vs. config-env mismatch).
- adopter `test_every_scaffolded_file_is_covered_by_registry_or_explicit_exemption` (`.claude/rules/CODEX-SESSION-BOOTSTRAP.md` case-mismatch + `bridge/.gitkeep`; both unrelated to the retired aggregate).

These are out of WI-5067 scope (per the proposal's Out-of-Scope clause) and warrant separate backlog items.

## Acceptance Criteria Check

- No declared target path uses the retired aggregate as live bridge authority: PASS (0 occurrences in the 5 test files + adopter; asserted by the STRIP contract test).
- Dispatcher/runtime + bridge-helper tests exercise numbered-file behavior without recreating the aggregate as an input fixture: PASS (dispatcher 169/169; helper tests pass).
- Registry/adopter no longer treats the aggregate as a current scaffolded artifact: PASS (exempt-list entry removed; `sot-artifacts.toml` retains the correct `retired` record).
- KEEP guard machinery not weakened: PASS (`GUARD_FILES` untouched; `test_keep_guard_machinery_intact` passes).

## Files Changed (7 of 8 authorized; net -98 LOC)

`platform_tests/scripts/test_dispatcher_runtime.py`, `test_gtkb_dispatcher_daemon.py`, `test_bridge_dispatch_config.py`, `test_scan_bridge.py`, `test_show_thread_bridge.py`; `platform_tests/governance/test_index_md_classification_contract.py`; `groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py`. `config/registry/sot-artifacts.toml` was reviewed and left unchanged (already correctly classified as retired).

## Owner Decisions / Input

- Owner directive 2026-07-07 (cited in proposal): the bridge index is obsolete; purge references. Active `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` authorizes this tranche.
- AskUserQuestion 2026-07-08 (this session): owner selected "Delete the 3 skipped tests," approving removal of the 3 already-`@skip` retired-drift tests in `test_show_thread_bridge.py` — satisfying the protected-behavior test-removal gate (CLAUDE.md § Protected Behaviors).

## Recommended Commit Type

Recommended commit type: `test` — test-residue purge plus a test-contract extension; no production source or capability change.

## Risk / Rollback

Low. Rollback is a revert of the 7-file diff. Bridge files remain append-only audit artifacts.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
