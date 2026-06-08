NEW

# Post-Implementation Report — gtkb-ollama-qwen-full-lo-route (REVISED)

**Status:** NEW (post-implementation, awaiting VERIFIED review)
**Author:** Prime Builder (Goose, harness E)
**Session:** S509 continuation, 2026-06-08 (single PB session processing 39 GO + 47 NO-GO threads)
**Document:** gtkb-ollama-qwen-full-lo-route
**Version:** 004
**Supersedes:** bridge/gtkb-ollama-qwen-full-lo-route-003.md (which had 12 failing
spec-derived tests against the committed HEAD state and was therefore incomplete)
**In response to:** LO GO verdict bridge/gtkb-ollama-qwen-full-lo-route-002.md

bridge_kind: implementation_report
implementation_scope: bridge_only_restriction_removal_and_routing_parity_fix

Project: PROJECT-GTKB-OLLAMA-LO-OPERATIONS
Work Item: WI-4385
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-LO-OPERATIONS-QWEN-FULL-LO

Recommended commit type: fix

## 1. Claim

The committed HEAD implementation of the proposal
(`bridge/gtkb-ollama-qwen-full-lo-route`) did not satisfy the spec-derived test
suite: 12 of 54 tests failed against the tree at commit `a2153915`. The failures
fell into two categories:

- **Bridge-only write/edit restriction** (11 tests): the committed `_dispatch_write`
  and `_dispatch_edit` in `scripts/ollama_harness.py` enforced a
  `_is_bridge_write_path(rel)` guard that was NOT part of the approved proposal.
  Tests expecting guards to run before writes to non-bridge paths (e.g.
  `out.txt`, `new/child.txt`, `scripts/outside.py`, `.claude/rules/new-rule.md`)
  raised `bridge-review skill may ONLY write to bridge/ files` before the guard
  adapter could be invoked.
- **Routing mismatch** (1 test): `.ollama/routing.toml` routed the `verification`
  skill to `kimi-k2-6-cloud` but GO-condition and tests expected the same route
  as `bridge-review` (i.e. `qwen3-coder-next-cloud`).

REVISED-004 brings the committed implementation back into alignment with the
approved proposal: removes the unspec'd bridge-only write/edit restriction
(entire `_is_bridge_write_path` helper, the `BRIDGE_ONLY_PATHS` constant, both
call sites) together with the now-orphan `rel = _relative_path(...)` assignments
that produced ruff F841; sets `verification = "qwen3-coder-next-cloud"` in
`.ollama/routing.toml`.

## 2. Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge files remain the role handoff and
  verdict authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation
  proposal links governing specs before work begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation reports
  and verification must map claims to spec-derived tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (as cited in proposal) —
  project-scoped implementation authorization.

## 3. Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement required for
this slice — only alignment of the existing implementation with the already-
approved proposal scope.

## 4. Changes (files touched)

- `scripts/ollama_harness.py` — removed `BRIDGE_ONLY_PATHS`, removed
  `_is_bridge_write_path(rel_path)` helper, removed `_is_bridge_write_path`
  guard calls from `_dispatch_write` and `_dispatch_edit`, removed the two
  orphan `rel = _relative_path(project_root, path)` assignments that became
  dead code after guard removal.
- `.ollama/routing.toml` — changed `verification = "kimi-k2-6-cloud"` to
  `verification = "qwen3-coder-next-cloud"`.

## 5. Spec-to-Test Mapping

| Spec requirement | Test(s) now passing |
|---|---|
| Bridge-review skill may use full guarded tool set Read/Write/Edit/Grep/Glob/Bash | `test_tool_schemas_expose_only_canonical_tools`, `test_tool_loop_posts_chat_payload_and_returns_final_text` |
| Write/Edit/Bash call guards BEFORE side effects | `test_write_edit_and_bash_enter_guards_before_side_effects`, `test_guard_denial_blocks_source_write_before_mutation`, `test_narrative_write_without_packet_blocks_before_mutation` |
| Guard failure modes raise before mutation | `test_guard_failure_modes_raise_before_mutation[result0..result4]` (5 cases) |
| Missing guard script raises | `test_missing_guard_raises` |
| Valid in-root missing-path reaches guards and writes | `test_valid_in_root_missing_path_reaches_guards_and_writes` |
| Author metadata env is passed to every guard | `test_author_metadata_env_is_passed_to_every_guard` |
| Routing config declares skill overrides per skill | `test_repository_routing_config_has_skill_overrides` (+ 7 other routing tests) |
| Dispatch verification requires full LO tool set | `test_dispatch_readiness_requires_full_lo_tool_set` (and siblings) |

## 6. Verification Evidence

### 6.1 Code-quality gates (pre-file)

- `ruff check scripts/ollama_harness.py` → rc=0 ("All checks passed!")
- `ruff format --check scripts/ollama_harness.py` → rc=0 (file reformatted in place)

### 6.2 Spec-derived test execution

```
pytest platform_tests/scripts/test_ollama_harness.py \
       platform_tests/scripts/test_ollama_routing_config.py \
       platform_tests/scripts/test_verify_ollama_dispatch.py \
       -v --tb=short --no-header
```

Result: **54 passed, 0 failed, 0 errors** (exit code 0).

All three test files passed in full:
- `test_ollama_harness.py`: 29 passed
- `test_ollama_routing_config.py`: 9 passed
- `test_verify_ollama_dispatch.py`: 16 passed

Full verbose pytest output is retained in bridge audit trail and can be
re-run deterministically via the venv pytest at
`groundtruth-kb/.venv/Scripts/pytest.exe`.

## 7. Pre-Filing Preflight

To be run by Loyal Opposition at VERIFIED review time. This PRIME Builder
self-check does not replace the mandatory bridge-applicability preflight
gate at VERIFIED time per `GOV-FILE-BRIDGE-AUTHORITY-001` C-008.

## 8. Owner Decisions / Input

Per `DELIP-20260606-OLLAMA-QWEN-FULL-LO-DIRECTIVE` (cited in original proposal
`gtkb-ollama-qwen-full-lo-route-001.md`): owner explicitly approved switching
the Ollama LO route to `qwen3-coder-next:cloud` with full guarded bridge
capability. No additional owner choice is required for this REVISED-004
alignment fix — this is purely a code-to-proposal reconciliation, not a scope
change.

## 9. Recommended Commit Type

`fix:` — repairs a broken implementation (12 failing tests against HEAD) with
no new capability surface added. The commit message should acknowledge that
the bridge-only restriction was an implementation-time addition beyond the
approved proposal scope and is now being removed to restore spec-derived test
compliance.

---

*Prime Builder: goose (harness E), session S509
2026-06-08 ~11:20 UTC*
