NEW

# WI-5028 Dispatch Run Author Identity Fallback

bridge_kind: prime_proposal
Document: gtkb-wi5028-dispatch-run-author-identity-fallback
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5028-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5028

target_paths: ["scripts/bridge_author_metadata.py", "platform_tests/scripts/test_bridge_author_metadata.py"]

implementation_scope: source/test/governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5028 captures a durable provenance defect in headless bridge verdict filing. When a helper subprocess lacks `GTKB_HARNESS_NAME`, `scripts.bridge_author_metadata._resolve_durable_identity_fields()` falls back to the single active Prime Builder in the registry. That fallback is wrong for headless Loyal Opposition verdict workers: their `GTKB_BRIDGE_POLLER_RUN_ID` already carries the true role/harness id, and per-session metadata remains correct, but the durable fields can be stamped as Prime Builder/Codex A instead of Loyal Opposition/Claude B.

This proposal repairs the durable-identity fallback order. When `GTKB_HARNESS_NAME` is absent, the resolver should parse dispatcher-format `GTKB_BRIDGE_POLLER_RUN_ID` values (`<timestamp>-<role>-<harnessId>-<suffix>`) and resolve that harness id through the durable registry before using the active-Prime fallback. Non-dispatch or malformed run IDs must preserve existing fail-closed/fallback behavior.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - bridge artifacts must carry accurate durable author identity and harness id.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - status-bearing bridge verdict files are canonical workflow evidence, so their provenance must be trustworthy.
- `GOV-SESSION-ROLE-AUTHORITY-001` - role authority comes from durable registry/dispatch context, not a misleading active-Prime fallback.
- `DCL-SESSION-ROLE-RESOLUTION-001` - dispatcher session context and durable role data must resolve consistently for headless workers.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A2 PAUTH permits this bounded source/test fix but does not replace LO review or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge review or implementation-start gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay within the named WI-5028 source/test envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing provenance, role, and bridge specs are cited and mapped to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must include focused tests and observed command evidence.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - provenance resolution must work for cross-harness headless workers, not only interactive Codex/Claude sessions.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - WI-5028 can close only if the concrete LO dispatch-stamp defect is covered by regression tests.
- `GOV-STANDING-BACKLOG-001` - the open WI must reach terminal state only with durable bridge/test evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation must read current registry projection and dispatch-id semantics rather than cached summaries.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - provenance defects and repair evidence remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix is preserved through bridge, source, and tests rather than session-local memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - verdict filing is the lifecycle trigger where accurate author metadata must be stamped.

## Prior Deliberations

- `WI-5028` backlog text - captures the concrete WI-3400 verdict instance stamped `prime-builder/codex/A` despite being authored by a headless LO Claude/B worker.
- `bridge/gtkb-wi3400-v1-release-strategy-advisory-disposition-002.md` - concrete provenance-defect example named in the WI.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing Batch A2 high-priority reliability fixes through governed bridge work.
- `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` - approval packet for that owner decision; scoped here by PAUTH and LO review.
- Prior author-metadata hardening tests in `platform_tests/scripts/test_bridge_author_metadata.py` - establish fail-closed behavior and runtime-session precedence that this proposal must preserve.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved continuing the high-priority queue through governed implementation/disposition work.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5028-BATCH-A2-20260705` - active Batch A2 authorization for WI-5028 source, tests, and governance evidence.

No additional owner decision is required. This proposal still requires Loyal Opposition `GO` and an implementation-start packet before protected mutation.

## Requirement Sufficiency

Existing requirements sufficient.

Existing provenance and role-authority specifications already require accurate author identity and harness id on bridge artifacts. WI-5028 identifies an implementation defect in the durable identity fallback order; no new requirement is needed.

## Proposed Implementation

1. Add a dispatcher-run-id parser in `scripts/bridge_author_metadata.py` for IDs produced by `scripts.dispatcher_runtime._new_dispatch_id()`: `<UTC timestamp>-<role>-<harnessId>-<hex suffix>`, where role is one of the canonical dispatch role tokens.
2. In `_resolve_durable_identity_fields()`, when `GTKB_HARNESS_NAME` is unset, resolve `GTKB_BRIDGE_POLLER_RUN_ID` through that parser before the active-Prime fallback:
   - parse harness id and role token;
   - find the harness name in `harness-state/harness-identities.json`;
   - read the durable role assignment for that harness id;
   - return `author_identity: <durable-role>/<harness_name>` and `author_harness_id: <harness_id>`.
3. Treat the dispatch role token as locator evidence only. The durable registry remains authoritative for the role label; token/registry disagreement must resolve from the registry or fail closed.
4. Preserve existing behavior for explicit `GTKB_HARNESS_NAME`, explicit metadata, runtime session/model fields, malformed/non-dispatch run IDs, missing registry entries, multiple active Prime fallbacks, and complete embedded metadata.
5. Add focused tests proving:
   - absent `GTKB_HARNESS_NAME` plus LO dispatch run id resolves to LO/Claude B;
   - token/registry role disagreement uses durable registry role;
   - malformed/non-dispatch run id does not produce a wrong stamp;
   - current Prime fallback behavior remains available only when no better dispatch identity exists.

## Cross-Harness Disposition

This change affects shared author metadata stamping used by bridge helpers across harnesses. The fix remains in shared `scripts/bridge_author_metadata.py`; no harness-local fork is proposed. The dispatcher run id supplies the filing harness id for Claude, Codex, Antigravity, Cursor, Ollama, and OpenRouter workers, while the durable registry remains the role authority.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Headless verdict helpers stamp the true filing harness durable identity, not the active Prime fallback. | `platform_tests/scripts/test_bridge_author_metadata.py` adds a fixture with `GTKB_BRIDGE_POLLER_RUN_ID=2026-07-05T07-50-27Z-loyal-opposition-B-54c749`, no `GTKB_HARNESS_NAME`, and registry B=`claude` LO; expected `author_identity=loyal-opposition/claude`, `author_harness_id=B`. |
| `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` | Dispatch token role does not override durable registry role. | Test with token role/harness id mismatch asserts durable registry role wins or fails closed rather than trusting token role. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | The fix is shared and harness-neutral. | Tests use registry projection fixtures rather than hard-coded Claude-only behavior. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Durable identity resolves from current registry projection and env, not stale current.json or summaries. | Existing stale-current tests remain green; new tests verify no active-Prime fallback is used when dispatch id resolves. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification evidence is command-based and repeatable. | Implementation report includes pytest and ruff command output. |

Minimum verification commands after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short --basetemp .gtkb-state/pytest-tmp-wi5028
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py
```

## Acceptance Criteria

- With `GTKB_HARNESS_NAME` unset and a dispatch-format LO/B run id, durable fields resolve to the B harness's durable LO identity.
- Explicit `GTKB_HARNESS_NAME` and explicit metadata still take precedence where they already do.
- Dispatch token role is not treated as authority when registry role differs.
- Malformed/non-dispatch run ids do not synthesize a wrong identity.
- Existing runtime session/model envelope behavior and stale-current fail-closed tests remain green.
- No KB mutation, credential action, deployment, destructive cleanup, broad status mutation, dispatcher routing change, or bridge-history rewrite is in scope.

## Risk / Rollback

Risk is low to moderate because author metadata is a shared bridge surface. The mitigation is a narrow fallback insertion before an already-risky active-Prime fallback, with durable registry role as the authority and focused regression tests. Rollback is a single revert of the source/test diff; no schema or bridge-history mutation is proposed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5028-dispatch-run-author-identity-fallback`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the eventual diff repairs a concrete bridge-verdict author-provenance defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
