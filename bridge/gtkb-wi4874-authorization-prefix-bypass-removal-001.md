NEW

# Remove caller-controlled test/fixture prefix bypasses from bridge authorization gates

bridge_kind: prime_proposal
Document: gtkb-wi4874-authorization-prefix-bypass-removal
Version: 001
Author: Prime Builder (Codex automation, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f13e6-3e98-7371-bc99-913839756149
author_model: GPT-5
author_model_version: Codex desktop automation
author_model_configuration: Auto-builder automation; approval_policy=never; sandbox=danger-full-access; resolved_role=prime-builder

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4874

target_paths: ["scripts/implementation_authorization.py", "scripts/bridge_review_independence.py", ".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py", ".cursor/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_self_review_write_time_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_worker_packet_authorization_envelope.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: source, test, protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4874 identifies a security defect in bridge authorization and review-independence helpers: several production code paths treat a caller-controlled bridge slug beginning with `test-` or `fixture-` as a reason to skip authorization, self-review, or GO-activatability checks. A bridge actor controls the slug, so the prefix is not trustworthy input.

This proposal removes slug-prefix-based bypass behavior from production paths and replaces any test compatibility need with explicit test-only controls, monkeypatches, or hermetic fixture setup. The implementation also keeps the active `.claude`, `.codex`, and `.cursor` scan helper copies aligned with the template helper so the same defect does not regrow through harness projection.

Current worktree note: the listed implementation targets already have unrelated or partially overlapping dirty edits in this checkout. A future implementation session must re-check `git status`, preserve unrelated user/harness changes, and either finish the existing WI-4874-shaped edits in place or file a blocker if the overlap cannot be separated safely.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Bridge authority and implementation-start checks must fail closed from live numbered bridge state; slug text must not be able to bypass those checks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal names the governing specifications and maps them to verification commands before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project authorization, project, work item, and concrete target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification requires tests that prove prefix-named bridge ids no longer bypass implementation-start, verdict independence, or GO activatability.
- `GOV-STANDING-BACKLOG-001` - WI-4874 is an open MemBase backlog work item and is included in the active Harness Parity Phase 2 project authorization.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active PAUTH permits source, test, skill, CLI, and protocol work for WI-4874 while preserving bridge GO, work-intent, implementation-report, and verification gates.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - The fix must cover Claude, Codex, Cursor, and template helper paths rather than closing only one harness copy.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Harness helper parity must be preserved when the active scan helper behavior changes.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Dispatcher and bridge authorization must remain centralized, deterministic, and independent of caller-provided cosmetic slug patterns.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The fix must preserve the bridge proposal, implementation report, tests, and verification evidence as a durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The proposal distinguishes active implementation work, deferred/non-scope work, verification, and rollback states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The captured security defect is promoted from a work-item observation into governed proposal, test, and verification artifacts.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - Self-review checks depend on trustworthy author-session metadata and must not be bypassable through a bridge-id prefix.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Prime-actionable GO selection must report non-activatable GO entries instead of treating synthetic-looking bridge ids as automatically activatable.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - Dispatcher reporting surfaces must expose authorization failures consistently and not hide them behind a prefix exception.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - Owner directive and project authorization for Harness Parity Phase 2, including WI-4874 in the bounded implementation set.
- `DELIB-20266267` - Related bridge/governance reliability hardening authorization; reinforces that bridge reliability fixes proceed through normal per-WI proposal, GO, implementation report, and verification gates.
- `DELIB-20266268` - Dispatcher-reliability residue decision; confirms standard bridge protocol remains required for dispatcher reliability fixes.
- `bridge/gtkb-wi4893-false-verified-finalization-recovery-test-target-amendment-004.md` - Adjacent VERIFIED hardening work around false verification/finalization safety.
- No directly controlling prior deliberation was found that approves slug-prefix bypasses for production authorization gates. WI-4874 is therefore treated as a new security defect, not a revisit of an accepted design.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The active owner authorization is `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`, backed by `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`; it explicitly includes `WI-4874` and allows source, test, skill, CLI, and protocol/documentation mutation classes while forbidding bypass of bridge GO, work-intent claims, implementation reports, and Loyal Opposition verification.

## Requirement Sufficiency

Existing requirements sufficient. WI-4874 states the defect and the required fix direction: remove `test-` / `fixture-` prefix bypasses from authorization gates and replace them with explicit test harness controls such as an environment-gated test-only path or monkeypatching. The governing specifications listed above constrain the implementation and verification surface.

## Cross-Harness Disposition

This proposal touches harness-surface skill helper files and must preserve behavioral parity.

| Harness / surface | Disposition |
| --- | --- |
| Claude Code `.claude/skills/bridge/helpers/scan_bridge.py` | In scope. Remove prefix bypass behavior or align it to the same explicit test-only control used by the canonical helper. |
| Codex `.codex/skills/bridge/helpers/scan_bridge.py` | In scope. Must match the Claude helper for GO activatability behavior because Codex uses this helper for Prime bridge scans. |
| Cursor `.cursor/skills/bridge/helpers/scan_bridge.py` | In scope. Must match the Claude/Codex helper so Cursor scans cannot silently preserve the bypass. |
| Template `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py` | In scope. Update the template source so future scaffold/projection output does not reintroduce the prefix bypass. |
| Antigravity / Ollama / OpenRouter provider harnesses | No direct helper file is in this target path set. No typed waiver is requested; if implementation discovers a provider/API harness copy of this helper, it must either add that path to the implementation report's verified path set or file a revision before mutation. |

## Proposed Scope

1. Remove production checks that return success solely because `bridge_id.startswith("test-")` or `bridge_id.startswith("fixture-")` in:
   - `scripts/implementation_authorization.py`
   - `scripts/bridge_review_independence.py`
   - active and template `scan_bridge.py` helper copies

2. Preserve legitimate synthetic-test compatibility only through explicit test controls:
   - Prefer monkeypatching the helper under test where existing tests are only exercising routing shape.
   - If an explicit test-only bypass is unavoidable, require both a dedicated env var and an active pytest context (`PYTEST_CURRENT_TEST`) so production callers cannot trigger it by naming a bridge thread.

3. Add regression coverage proving:
   - `test-*` and `fixture-*` bridge ids no longer bypass implementation-start self-review checks in production mode.
   - `test-*` and `fixture-*` bridge ids no longer bypass verdict review-independence checks in production mode.
   - `scan_bridge._go_activatable()` consults authorization logic for prefix-named bridge ids unless a test explicitly monkeypatches or opts into the test-only path.
   - Active `.claude`, `.codex`, `.cursor`, and template helper copies remain aligned for this behavior.

4. Do not mutate `groundtruth.db`, project memberships, dispatcher topology, credentials, or production deployment state in this slice.

## Non-Scope

- Changing bridge slug syntax or banning `test-` / `fixture-` names at the proposal layer.
- Reworking the entire implementation-start authorization packet model.
- Changing review-independence semantics beyond removal of the prefix bypass.
- Resolving unrelated dirty changes already present in the same files unless they are required to complete WI-4874 safely.

## Spec-Derived Verification Plan

| Specification | Verification command / check | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `python -m pytest platform_tests/scripts/test_self_review_write_time_gate.py -q --tb=short` | Self-review and missing-author cases fail closed for normal and prefix-named bridge ids unless an explicit test control is active. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `python -m pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short` | GO activatability checks surface authorization failures for prefix-named bridge ids instead of automatically passing. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short` | Active harness helper copies and template behavior stay in parity for the changed gate semantics. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Review the implementation report's bridge artifact links, tests, and rollback notes. | The report preserves defect, implementation, verification, and residual-risk evidence without relying on scratchpads. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4874-authorization-prefix-bypass-removal` after LO GO | Implementation-start packet validates the proposal metadata and target paths before any protected mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this table forward with exact commands and observed results, plus `ruff check` and `ruff format --check` on changed Python files. | Loyal Opposition can verify every linked requirement against executed evidence. |

Implementation report must also run focused lint/format checks on changed Python files, at minimum:

```text
python -m ruff check scripts/implementation_authorization.py scripts/bridge_review_independence.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_self_review_write_time_gate.py
python -m ruff format --check scripts/implementation_authorization.py scripts/bridge_review_independence.py platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_self_review_write_time_gate.py
```

If the implementation changes hidden helper copies or templates, include those files in the ruff commands as well.

## Risk / Rollback

Risk is moderate because these helpers sit on bridge dispatch, implementation-start, and review-independence paths. The intended behavior is stricter: some synthetic tests may need explicit fixture setup instead of relying on bridge-id naming. The implementation should be small and covered by focused unit tests before any broader suite run.

Rollback is a normal revert of the implementation commit if the stricter gates break legitimate live bridge operation. Bridge proposal, implementation report, and verification files remain append-only audit artifacts and are not deleted by rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4874-authorization-prefix-bypass-removal`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

Diff-stat justification: this is a security and governance behavior repair to existing bridge authorization/review helpers plus regression tests. It does not add a new user-facing feature.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
