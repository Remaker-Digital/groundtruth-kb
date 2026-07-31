NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex interactive Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write

# WI-5002 Codex Headless Add-Dir Invocation Repair

bridge_kind: prime_proposal
Document: gtkb-wi5002-codex-headless-add-dir-invocation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: ["groundtruth.db", "harness-state/harness-registry.json", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "scripts/verify_codex_dispatch.py"]

implementation_scope: harness-config, harness-helper-parity, tests, kb-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Proposal Claim

The previous WI-5002 revised proposal received GO at `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-006.md`, but implementation-start quarantined it because the proposal omitted the mandatory `Requirement Sufficiency` section. That proposal also under-scoped the approved target paths: it required proof of a `.codex/**` helper write while omitting the `.codex` helper target from `target_paths`.

This replacement proposal preserves the narrow route Loyal Opposition approved: add Codex's in-root `.codex` directory as an explicit writable root for headless Codex dispatch:

```text
--add-dir {{PROJECT_ROOT}}/.codex
```

The implementation must preserve `--sandbox workspace-write`, `approval_policy="never"`, `--model gpt-5.5`, and `model_reasoning_effort="xhigh"`. It must not use `--dangerously-bypass-approvals-and-sandbox`, must not switch to `danger-full-access`, and must not ask any other harness to write `.codex/**` for Codex.

Because the first Codex worker to implement this proposal may be launched with the old argv, this proposal explicitly permits a two-dispatch completion path:

1. The first Codex PB run updates the Codex headless invocation/projection and tests the argv shape.
2. If the same run still cannot write `.codex/**` because it was launched before the argv change took effect, it files an implementation report documenting that staged state.
3. Loyal Opposition may return `NO-GO` for the staged report to resume the same GO, causing the next Codex PB run to launch with the updated argv and perform the `.codex` helper write and parity proof.

The work is not complete until a Codex PB run launched through the dispatcher with the updated argv either writes the approved `.codex/**` target successfully or reports a new, different blocker.

## Requirement Sufficiency

Existing requirements sufficient. The owner goal, WI-5002 backlog item, PAUTH record, direct harness-to-harness ban, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, and the access-denial evidence in `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-003.md` and `-004.md` define the required behavior. No new or revised requirement is required before implementation because this proposal only repairs the Codex headless invocation surface and the helper-parity target paths needed to satisfy already-governed bridge dispatch behavior.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex PB dispatch must complete approved work without manual intervention.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the fix must not use direct harness-to-harness fallback or a different harness as Codex's writer.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific hook/sandbox gaps must be handled mechanically and audibly.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper behavior must not diverge across Claude, Codex, and Cursor after the sandbox route is repaired.
- `ADR-CROSS-HARNESS-PARITY-001` - generated/adapted harness surfaces must preserve behavior parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, implementation, and verification must use the numbered bridge chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specs, target paths, and requirement sufficiency are cited before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the changed invocation and the subsequent `.codex` write path.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical backlog item for this blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the failed route and corrected route are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation must preserve evidence for rejected broader sandbox routes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocked dispatches triggered this corrected lifecycle step.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, and no direct harness fallback.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md`, `-005.md`, `-007.md`, and `-009.md` - repeated Codex `.codex/**` write-denial reports.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md` - Loyal Opposition accepted that identical Codex retries should stop until the write boundary changes.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` - original bounded repair proposal.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-002.md` - GO verdict for the original repair route.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-003.md` - blocked Codex implementation report proving the original route still could not write `.codex/**`.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-004.md` - NO-GO confirming the sandbox/tool-approval layer is the blocker.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md` - revised proposal for the add-dir route, missing the mandatory sufficiency metadata and the `.codex` helper target.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-006.md` - GO verdict approving the narrow add-dir route with conditions.

## Cross-Harness Disposition

- Claude Code / harness B: canonical helper source remains `.claude/skills/verify/helpers/write_verdict.py`; no Claude invocation or helper behavior change is proposed.
- Codex / harness A: headless invocation changes by adding `--add-dir {{PROJECT_ROOT}}/.codex`; `.codex/skills/verify/helpers/write_verdict.py` may be updated only by Codex after the new invocation surface is active, and it must be byte-identical to the Claude canonical helper before parity is claimed.
- Antigravity / harness C: no invocation or helper behavior change is proposed.
- Ollama / harness D: no invocation or helper behavior change is proposed.
- Cursor / harness E: `.cursor/skills/verify/helpers/write_verdict.py` may be kept byte-identical to the Claude canonical helper to preserve parity with the already-produced blocked-run alignment; no Cursor invocation change is proposed.
- OpenRouter / harness F: no invocation or helper behavior change is proposed.
- Waivers: none requested. Direct harness-to-harness fallback remains prohibited. Broad sandbox bypass is explicitly rejected.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes harness-config, KB-state, source/test, bridge, and harness-helper changes for WI-5002 while forbidding direct harness-to-harness launch, credential mutation, production deployment, and retired poller restoration.
- No new owner decision is required for this replacement proposal because it uses the narrow Codex-owned route already GO'd by Loyal Opposition and explicitly rejects the higher-risk broad sandbox and non-Codex executor options.

## Corrected Scope

The implementation may:

- update MemBase/projection state for Codex harness A headless argv;
- update `harness-state/harness-registry.json` through the canonical harness projection path;
- add `--add-dir {{PROJECT_ROOT}}/.codex` to the Codex headless invocation surface;
- preserve the existing GPT-5.5 model, `xhigh` reasoning effort, `approval_policy="never"`, and `workspace-write` sandbox settings;
- update `.codex/skills/verify/helpers/write_verdict.py` only after Codex is launched with the corrected invocation surface;
- keep `.cursor/skills/verify/helpers/write_verdict.py` aligned when committing helper parity work already produced by the blocked run;
- add or update tests proving the invocation shape, prohibited-flag absence, and helper parity.

The implementation must not:

- use `--dangerously-bypass-approvals-and-sandbox`;
- use `--sandbox danger-full-access`;
- launch or invoke another harness directly as a fallback;
- ask another harness to write `.codex/**` for Codex;
- restore the retired smart poller or OS poller.

## Pre-Filing Preflight Subsection

Pre-filing checks passed against this completed draft before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5002-codex-headless-add-dir-invocation --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-codex-headless-add-dir-invocation-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5002-codex-headless-add-dir-invocation --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-codex-headless-add-dir-invocation-001.md
python scripts/bridge_proposal_wi_id_collision_check.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-codex-headless-add-dir-invocation-001.md --strict
```

Observed result before live filing: applicability preflight passed with no missing required specs and no missing advisory specs; clause preflight passed with zero blocking gaps; collision check found only declared `WI-5002`.

## Verification Plan

The implementation report must include spec-to-test mapping and exact observed results for:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short --basetemp .harness-tmp/pytest-wi5002-add-dir
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py scripts/verify_codex_dispatch.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/skills/test_verified_finalization_validation_hardening.py scripts/verify_codex_dispatch.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py
```

Required assertions:

- harness A headless argv includes `--model gpt-5.5`;
- harness A headless argv includes `-c model_reasoning_effort="xhigh"`;
- harness A headless argv keeps `--sandbox workspace-write`;
- harness A headless argv includes `--add-dir {{PROJECT_ROOT}}/.codex` or an equivalent normalized in-root `.codex` writable root;
- harness A headless argv does not include `--dangerously-bypass-approvals-and-sandbox`;
- harness A headless argv does not include `--sandbox danger-full-access`;
- no direct harness-to-harness fallback is introduced;
- `.codex/skills/verify/helpers/write_verdict.py`, `.cursor/skills/verify/helpers/write_verdict.py`, and `.claude/skills/verify/helpers/write_verdict.py` are byte-identical when helper parity is claimed;
- the implementation report includes SHA-256 hashes for the three helper copies.

Post-implementation acceptance requires a dispatcher-launched Codex PB attempt with the revised invocation surface to write the approved `.codex/**` target or to report a new, different blocker. Another identical access-denied result against the same target means this replacement proposal failed.

## Risk And Rollback

Risk: `--add-dir {{PROJECT_ROOT}}/.codex` may still be insufficient if Codex treats `.codex` as a protected configuration namespace even when explicitly added. That failure would be a useful narrower fact and would not broaden sandbox authority.

Risk: changing the canonical harness registry/projection incorrectly could break Codex dispatch. Tests must verify the full argv shape, and rollback is restoring the previous harness A argv from git plus regenerating the projection.

Risk: the two-dispatch completion path can look like a partial implementation report. The report must explicitly distinguish stage-one invocation repair from final helper-write acceptance; Loyal Opposition should withhold VERIFIED until the dispatcher-launched Codex run with the new argv proves the helper write or reports a new blocker.

Rejected alternatives:

- `--dangerously-bypass-approvals-and-sandbox` - too broad for this repair.
- `--sandbox danger-full-access` - too broad for this repair.
- asking Claude, Cursor, or another harness to write `.codex/**` - prohibited direct harness fallback.
- owner manual copy - may unblock one file but does not satisfy unattended dispatch stability.

## Recommended Commit Type

fix - this is a bounded repair to Codex headless dispatch configuration and helper parity for an existing blocker.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
