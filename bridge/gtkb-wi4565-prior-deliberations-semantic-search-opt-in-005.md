NEW

# WI-4565 implementation report: prior-deliberations semantic search opt-in + bounded default-store open

bridge_kind: implementation_report
Document: gtkb-wi4565-prior-deliberations-semantic-search-opt-in
Version: 005 (NEW - post-implementation report)
Responds to: bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-004.md
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4565

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py", "platform_tests/skills/test_bridge_propose_helper.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented the GO'd (version 004) WI-4565 fix. Prior-deliberation seeding's semantic search is now opt-in (db=None default and db=False both skip; db=True opts in), and the default-store open is timeout-bounded so the opt-in path can never hang the bridge-authoring hot path.

## Changes Implemented

1. `groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py`:
   - Added `import os`; added module constant `_OPEN_DB_TIMEOUT_SECONDS = float(os.environ.get("GTKB_DA_OPEN_TIMEOUT_SECONDS") or "10")`.
   - Re-mapped the `db` tri-state in `pre_populate_prior_deliberations`: `db is False or db is None` -> no semantic search (glossary-source seeding still runs); `db is True` -> `_try_open_default_db()`; any other value -> live DB instance. This makes `db=None` honor the documented "skips semantic search" contract instead of auto-opening the default store.
   - Bounded `_try_open_default_db()` with `_call_with_timeout(lambda: KnowledgeDB(DEFAULT_DB_PATH), _OPEN_DB_TIMEOUT_SECONDS)` (lazy import of `_call_with_timeout` from `groundtruth_kb.db`, db.py:133), degrading to `None` on `TimeoutError`/exception. This guards the store-open/embedding-model-load step the FAB-17/WI-4519 query timeout did not cover.
2. `platform_tests/skills/test_bridge_propose_helper.py`: added 5 WI-4565 unit tests.

## Scope Note — write_bridge.py docstring deferred to WI-4716

The GO'd proposal listed `.claude/skills/bridge-propose/helpers/write_bridge.py` in target_paths for a `db` docstring update. During implementation I confirmed the EXISTING docstring already states "``None`` skips semantic search; glossary-source seeding still runs" — exactly the behavior the new code now honors. The proposal's only docstring ADDITION (a `db=True` opt-in mention) was reverted because editing the canonical helper forces regeneration of its generated Codex adapter `.codex/skills/bridge-propose/helpers/write_bridge.py`, which is outside the `source`/`test` allowed mutation classes of `PAUTH-...-COMPLIANCE-DISPATCH-BATCH-002` — the same generated-adapter scope boundary Loyal Opposition enforced on WI-4701 at version 002. The `db=True` doc enhancement plus the `.codex/` adapter regeneration are folded into the already-captured follow-up WI-4716 (bridge-propose skill-instruction/helper-doc sync). The proposal acceptance criterion "write_bridge.py db docstring matches the implemented behavior" is satisfied: the existing docstring matches the new code. `target_paths` above are correspondingly the two files actually changed.

## Specification Links (carried forward from the GO'd -003 proposal)

- `GOV-AUTOMATION-VALUE-VS-COST-001` — governing principle: gate the expensive, hang-capable ChromaDB operation behind a cheap deterministic opt-in.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed results below.
- `GOV-STANDING-BACKLOG-001` — WI-4565 is the governed backlog item; deferred doc sync is WI-4716.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths are under `E:\GT-KB`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory); `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).

## Spec-to-Test Mapping

| Specification / behavior | Test | Result |
| --- | --- | --- |
| GOV-AUTOMATION-VALUE-VS-COST-001: db=None (default) opens no DB / runs no search | `test_wi4565_db_none_default_skips_open_and_search` | PASS |
| db=False keeps disabling search (unchanged contract) | `test_wi4565_db_false_still_disables_search` | PASS |
| db=True opts in to the default-store search | `test_wi4565_db_true_opts_in_to_default_store_search` | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: bounded open fast-fails (no hang) | `test_wi4565_open_db_bounded_by_timeout` | PASS |
| docstring matches the None-skips behavior the code now honors | `test_wi4565_db_param_docstring_matches_skip_behavior` | PASS |

## Verification Commands + Results

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper.py -q --tb=short`: **18 passed, 1 failed** (the single failure is `test_codex_skill_adapter_parity_check` — pre-existing; see below).
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper_work_intent.py -q` run with `CLAUDE_CODE_SESSION_ID` unset: **6 passed**.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q`: passed (part of the combined 27-passed run).
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py platform_tests/skills/test_bridge_propose_helper.py`: **All checks passed!**
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check ...`: **2 files already formatted**.

### Pre-existing / environmental failures (NOT introduced by WI-4565)

- `test_codex_skill_adapter_parity_check` fails because of a tracked generated-artifact drift `.codex/skills/bridge/helpers/__pycache__/scan_bridge.cpython-314.pyc` (a committed `__pycache__` artifact), captured separately as **WI-4715**. After the write_bridge.py revert above, this parity check no longer flags any WI-4565-touched file; the failure is the pre-existing `.pyc` outlier only.
- The two `test_bridge_propose_helper_work_intent.py` failures seen when pytest runs under this interactive shell are caused by the shell's `CLAUDE_CODE_SESSION_ID` env var leaking into `resolve_work_intent_session_id` (asserting `'600b3b4c-...' == 'session-c'`). With that env var unset the suite passes 6/6 (shown above). Not a code regression from this change.

## Preflight Results

### Applicability Preflight (run against this report draft via `--content-file`)

- `preflight_passed: true`; `missing_required_specs: []`.
- `missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"]` — that advisory spec does not resolve as a live MemBase spec (verify-before-cite), so it is intentionally not cited.
- Draft packet_hash: `sha256:f90e5faead4b99e769f848f74f0abdddf338ab3525e97343baa55904b62dd225` (Loyal Opposition recomputes the packet against the filed `-005` file).

### ADR/DCL Clause Preflight

- Clauses evaluated: 5; must_apply: 2; Evidence gaps in must_apply clauses: 0; **Blocking gaps (gate-failing): 0**; exit 0 (pass).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: must_apply, evidence found: yes (all changed paths under `E:\GT-KB`).

## Prior Deliberations

- `DELIB-20265287` — owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`.
- `DELIB-20265459` — owner authorization batch (BATCH-002) including WI-4565.
- `DELIB-20263467` — WI-4453 ChromaDB latency advisory; the latency/hang lineage this change closes on the store-open path.
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-004.md` — the Loyal Opposition GO verdict this report responds to.

## Risk And Rollback

Source-only change plus additive tests. Roll back by reverting the single `prior_deliberations.py` change; the tests are additive. No state/schema migration; the `db=False` contract and both public-helper signatures are unchanged. The default flips toward the already-documented "None skips" contract, reducing silent cost.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
