REVISED

# WI-4565 implementation report (re-file): prior-deliberations semantic search opt-in + bounded open

bridge_kind: implementation_report
Document: gtkb-wi4565-prior-deliberations-semantic-search-opt-in
Version: 007 (REVISED - re-filed post-implementation report after a transient finalization blocker)
Responds to: bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-006.md
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

## Re-file Rationale (responding to the version-006 NO-GO)

The version-006 NO-GO was an explicit **non-defect finalization blocker**: Loyal Opposition stated "The WI-4565 implementation itself verifies against the GO'd source/test scope," but the mandatory atomic VERIFIED helper failed because Git could not create `.git/index.lock` (`Permission denied`) during the verified-path-set commit. Per the version-006 Required Follow-Up ("Prime Builder may refile a REVISED implementation report once the finalization environment is available, citing this blocker"), this report re-presents the unchanged, verified implementation for a fresh verification/finalization attempt.

The blocker was transient (not a stale lock): `.git/index.lock` is currently absent (confirmed `ls .git/index.lock` -> No such file). The likely root cause is contention on the Git index from concurrent multi-session commits and/or a sync process touching `E:\GT-KB\.git`. No source or test change is made in this re-file; the implementation is byte-identical to the version-005 report's verified state.

## Implementation (unchanged from version 005; verified by Loyal Opposition in -006)

1. `groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py`: `import os` + `_OPEN_DB_TIMEOUT_SECONDS` (env `GTKB_DA_OPEN_TIMEOUT_SECONDS`, default 10); `db` tri-state re-map (`db is False or db is None` -> skip; `db is True` -> `_try_open_default_db()`; else live instance); `_try_open_default_db()` bounded by `_call_with_timeout(...)` degrading to `None` on timeout/exception.
2. `platform_tests/skills/test_bridge_propose_helper.py`: 5 WI-4565 tests.

The write_bridge.py docstring already states the now-true "None skips semantic search" contract; the db=True doc enhancement + .codex adapter regen are deferred to WI-4716 (out of source+test scope).

## Specification Links (carried forward)

- `GOV-AUTOMATION-VALUE-VS-COST-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory); `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).

## Spec-to-Test Mapping

| Specification / behavior | Test | Result (version-005 + version-006 review) |
| --- | --- | --- |
| GOV-AUTOMATION-VALUE-VS-COST-001: db=None default opens no DB / runs no search | `test_wi4565_db_none_default_skips_open_and_search` | PASS |
| db=False keeps disabling search | `test_wi4565_db_false_still_disables_search` | PASS |
| db=True opts in to default-store search | `test_wi4565_db_true_opts_in_to_default_store_search` | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: bounded open fast-fails | `test_wi4565_open_db_bounded_by_timeout` | PASS |
| docstring matches None-skips behavior | `test_wi4565_db_param_docstring_matches_skip_behavior` | PASS |

## Verification Commands + Results

Carried forward from the version-005 report and independently re-confirmed by Loyal Opposition in version-006 ("WI-4565 focused tests: 5 passed; Work-intent regression suite: 6 passed; Verify prior-deliberation prepopulation regression: 5 passed; Ruff check: all checks passed; Ruff format check: 2 files already formatted"). The only `test_bridge_propose_helper.py` failure is the pre-existing `test_codex_skill_adapter_parity_check` (broad Codex skill-adapter drift, including tracked `__pycache__` `.pyc` artifacts — captured as WI-4715), unrelated to this bridge's target paths.

## Preflight Results

- Applicability preflight (`--content-file`): `preflight_passed: true`; `missing_required_specs: []`; draft packet_hash `sha256:37c7d427749f80d2d8f4b9b82858d633bc182eadb83e207d3ca240483a6b5149` (LO recomputes against the filed `-007`).
- ADR/DCL clause preflight: Clauses evaluated 5; must_apply 2; Evidence gaps in must_apply clauses 0; **Blocking gaps 0**; pass.

## Prior Deliberations

- `DELIB-20265287` — owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`.
- `DELIB-20265459` — owner authorization batch including WI-4565.
- `DELIB-20263467` — WI-4453 ChromaDB latency advisory (the lineage this closes for the store-open path).
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-006.md` — the Loyal Opposition non-defect finalization-blocker NO-GO this re-file responds to.
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-004.md` — the GO verdict.

## Risk And Rollback

No source change in this re-file. Roll back by reverting the single `prior_deliberations.py` change (tests additive). No state/schema migration; `db=False` contract and public-helper signatures unchanged.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
