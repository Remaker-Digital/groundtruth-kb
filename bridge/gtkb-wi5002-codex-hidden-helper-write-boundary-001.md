NEW

# WI-5002 Codex Hidden Helper Write Boundary

bridge_kind: prime_proposal
Document: gtkb-wi5002-codex-hidden-helper-write-boundary
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex interactive Prime Builder; approval_policy=never; dispatcher stability goal active

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: [".codex/config.toml", ".codex/skills/verify/helpers/write_verdict.py", ".claude/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "scripts/generate_codex_skill_adapters.py", "scripts/implementation_start_gate.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "platform_tests/scripts/test_implementation_start_gate.py", "groundtruth.db"]

implementation_scope: source, tests, harness-config, kb-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

The `gtkb-wi4975-claimed-path-subpath-overmatch` bridge thread is blocked after repeated Codex-A headless attempts because an approved implementation needed to update `.codex/skills/verify/helpers/write_verdict.py`, but Codex headless could not write that in-root hidden helper target. Loyal Opposition accepted the route-change request in `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md`: do not keep retrying the same Codex implementation until either Codex can write the approved target or the update is routed through a governed canonical/regeneration path that prevents partial cross-harness parity.

This proposal authorizes a bounded repair for that execution-environment gap. The implementation may choose the least-risk route after inspection:

- repair Codex's approved in-root `.codex` helper/config write boundary so a dispatcher-launched Codex PB can update a GO-authorized `.codex/**` target; or
- mechanically redirect `.codex` helper updates to a governed canonical/regeneration path, so the canonical helper source and generated Codex adapter cannot diverge silently.

Either route must preserve the direct harness-to-harness ban. No harness may invoke another harness as a fallback or standby path.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-selected PB work must be able to complete without manual intervention or out-of-band harness fallback.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - direct harness-to-harness interaction is prohibited; the fix must keep all automation behind governed dispatcher, bridge, helper, and registry surfaces.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific hook/sandbox gaps must be handled mechanically and audibly, not by silent manual bypass.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper behavior shared across Claude, Codex, and Cursor must not diverge when a cross-harness helper fix is authorized.
- `ADR-CROSS-HARNESS-PARITY-001` - generated/adapted harness surfaces must preserve behavior parity or identify the canonical generation path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the proposal, GO, implementation report, and verification must use the current numbered bridge chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specs before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project id, work item id, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include spec-derived tests proving the selected repair.
- `GOV-STANDING-BACKLOG-001` - WI-5002 is the canonical backlog item for this blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live operational blocker is preserved as a durable backlog, authorization, bridge, source, and test artifact rather than a scratchpad-only workaround.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation must preserve durable evidence for the chosen repair route and rejected fallback.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocker reports in the source bridge thread triggered a new dedicated repair work item and proposal.

## Cross-Harness Disposition

- Claude Code / `.claude`: behavioral parity is required for any helper logic touched under `.claude/skills/verify/helpers/write_verdict.py`; if this remains the canonical source, generated/adapted surfaces must derive from it.
- Codex / `.codex`: behavioral parity is required and the implementation must either prove approved in-root `.codex/**` target writes are allowed only under a current implementation-start packet or prove `.codex` helper files are generated from a governed canonical source.
- Cursor / `.cursor`: behavioral parity is required for `.cursor/skills/verify/helpers/write_verdict.py`; the implementation must prevent a stale Cursor helper when the canonical helper/parser behavior changes.
- Antigravity and Ollama: no helper-surface mutation is proposed for this repair. Their dispatch behavior must remain mediated by the central dispatcher and must not gain direct harness-to-harness fallback behavior.
- Waivers: none requested. Any implementation route that cannot preserve parity must return to the bridge with a typed owner-approved waiver request instead of proceeding.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, no direct harness fallback, and bounded implementation authorization for defects found during the live soak.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md` - LO accepted the route-change request and required either a write-capable executor or a Codex sandbox/environment repair before another Codex retry.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md`, `-005.md`, `-007.md`, and `-009.md` - repeated Codex-A blocker reports establishing the persistent `.codex` helper write denial.
- `bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch-004.md` - fresh successful end-to-end daemon evidence for the same stability goal: D GO, A implementation, D VERIFIED, all headless and exit 0.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes source, tests, harness-config, KB-state, and bridge changes for WI-5002, while forbidding direct harness-to-harness launch, credential mutation, production deployment, and retired poller restoration.

## Requirement Sufficiency

Existing requirements sufficient - the owner goal, WI-5002 backlog item, PAUTH, direct harness ban, bridge authority rules, and cross-harness parity requirements define the allowed behavior and acceptance criteria. No new specification is required before implementation.

## Spec-Derived Verification Plan

The implementation report must map the selected repair route to concrete tests and observed results:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp .harness-tmp/pytest-wi5002
```

- If the repair allows approved `.codex/**` writes, tests must prove an implementation-start packet whose `target_paths` includes `.codex/skills/verify/helpers/write_verdict.py` authorizes that in-root hidden target while still denying unapproved hidden or out-of-root paths.
- If the repair uses canonical regeneration instead, tests must prove `.codex/skills/verify/helpers/write_verdict.py` is treated as generated from the canonical source and cannot remain stale when the canonical helper changes.
- The source-thread helper parity class must be tested by asserting the parser boundary/trailing-punctuation cleaning behavior across `.claude`, `.codex`, and `.cursor` helper copies, or by asserting the generator produces byte-identical/parity-equivalent logic for the relevant parser functions.
- Dispatcher/control-plane tests must confirm no direct harness-to-harness fallback is introduced.
- At minimum, run `ruff check` and `ruff format --check` on any changed Python source/test files.

Expected result: tests and quality gates pass; a subsequent Codex PB dispatch can complete the previously blocked approved helper target work without filing another identical `.codex` write blocker.

## Risk / Rollback

Risk is concentrated in Codex's local hidden-path write boundary and generated helper parity. A too-broad fix could weaken sandbox protections; a too-narrow fix could preserve the gtkb-wi4975 retry loop. The implementation must therefore fail closed on unapproved hidden paths and prove either exact approved-target access or deterministic regeneration.

Rollback is a single local commit revert after LO verification if the repair broadens write access incorrectly or breaks helper parity.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5002-codex-hidden-helper-write-boundary`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - this repairs a live headless Codex PB dispatch blocker with no intended new product capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
