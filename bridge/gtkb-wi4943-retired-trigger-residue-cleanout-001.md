NEW

# WI-4943 Retired Cross-Harness Trigger Residue Cleanout

bridge_kind: prime_proposal
Document: gtkb-wi4943-retired-trigger-residue-cleanout
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-01 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-prime-builder-20260701-retired-trigger-residue-cleanout
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop automation; Prime Builder release-preparation session; PowerShell; workspace-write

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: [".temp_verified_cross_harness_006.md", ".claude/**", ".codex/**", "config/**", "groundtruth-kb/docs/**", "groundtruth-kb/templates/**", "groundtruth-kb/tests/**", "platform_tests/**", "scripts/**"]

implementation_scope: source | governance | protocol | tests | docs
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Complete the release dispatcher-substrate reconciliation by removing residual live, load-bearing, test, template, and local-helper references to the retired cross-harness trigger family.

The existing WI-4885 purge thread is terminal VERIFIED at `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-006.md`, but current release-preparation evidence contradicts its implementation claim that forbidden-term scans over load-bearing roots were clean. The runtime file `scripts/cross_harness_bridge_trigger.py` is absent and untracked, which is good. The problem is residual tracked/test/config/doc/helper surfaces that still preserve the retired trigger as an active or testable concept, plus tracked scratch-like residue `.temp_verified_cross_harness_006.md`.

This proposal does not delete or rewrite historical bridge audit chains. It targets current release surfaces only: source, tests, docs/templates, hook/skill/rule helper text, config surfaces, and tracked scratch-like artifacts outside formal append-only history.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — This correction must proceed as a new append-only bridge thread because the prior WI-4885 purge thread is terminal VERIFIED and cannot be rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — The proposal carries concrete governing links before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — The proposal carries PAUTH/project/work-item metadata for WI-4943.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification must prove the retired trigger cannot remain in active release surfaces.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — Dispatcher daemon must remain the only automated bridge dispatch substrate.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — Dispatcher status/health/control documentation must not point operators at retired trigger paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` — The release architecture is dispatcher-daemon based; hook-driven/cross-harness-trigger automation must not be restored.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Release dispatcher operation must stay on the headless dispatcher-daemon/supervisor path rather than revived hook or shell-trigger automation.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Release readiness requires test and documentation surfaces to match the actual supported operating state.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — Cross-harness parity remains valid, but parity tests must not preserve retired trigger behavior as a required harness capability.
- `ADR-CROSS-HARNESS-PARITY-001` — Harness parity should describe current dispatcher/daemon semantics, not stale trigger mechanics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — The contradiction discovered during release preparation must be preserved as governed bridge work rather than scratch memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Release-blocking cleanup must be expressed as a durable artifact with explicit scope, evidence, and review outcome.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Any intentionally deferred historical/audit residue must have an explicit expiry/trigger.
- `GOV-STANDING-BACKLOG-001` — Residual release blockers must be visible and routed, not silently ignored.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` — Owner-authorized scoped release-integration WI/PAUTH for WI-4943; expires 2026-07-02T00:00:00Z.
- `DELIB-20266276` — Daemon-resilience program scope-lock and release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` — Dispatcher release-health directive.
- `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-001.md` — Approved original purge proposal.
- `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-006.md` — Terminal VERIFIED verdict whose claim is now contradicted by current tree evidence.
- Owner directive in the current release-preparation session: the cross-harness trigger was previously purged and should not remain as a live release surface.

## Owner Decisions / Input

Owner input is already present:

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` authorized the active WI-4943 release-integration PAUTH.
- The owner questioned why `cross_harness_bridge_trigger` still exists after the purge.
- The owner previously directed that retired cross-harness trigger paths and hook-driven automation must not be restored.
- The owner directed that deferrals need explicit expiry or trigger, not open-ended "deferred" status.

No further owner decision is required to propose this correction. Implementation still requires Loyal Opposition GO before protected files are modified.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4943 authorizes release dispatcher-substrate reconciliation, including only verified dispatcher substrate work and documentation/evidence corrections needed for the clean release branch. WI-4885 already established the dispatcher-only direction: dispatcher daemon is the only automated bridge success path, and manual owner assignment/manual bridge handling is the fallback. This proposal corrects incomplete execution of that requirement before release integration.

Historical bridge artifacts are explicitly out of implementation scope because the bridge file chain is append-only under `GOV-FILE-BRIDGE-AUTHORITY-001`. That is not an indefinite deferral: if post-cleanout release-health scans or README/wiki/dashboard audits still count historical bridge files as active residue, open a separate archival/reporting-scope proposal no later than 2026-07-02 UTC or before merging the release branch to `main`, whichever comes first.

## Proposed Implementation

1. Remove tracked scratch-like residue outside formal bridge history, including `.temp_verified_cross_harness_006.md`.
2. Delete, rename, or rewrite tests whose only purpose is to exercise the retired cross-harness trigger implementation.
3. Preserve legitimate cross-harness parity concepts that are independent of the retired trigger, but rename tests/doc text so they no longer imply `cross_harness_bridge_trigger` is a supported subsystem.
4. Update docs, templates, skills, hooks, rules, config, and scripts to refer to dispatcher-daemon/manual fallback semantics only.
5. Add or repair an anti-regression test that scans live release surfaces for retired trigger terms, excluding formal bridge audit history and intentionally historical evidence records.
6. Do not recreate `scripts/cross_harness_bridge_trigger.py`, single-harness dispatcher scripts, hook-driven bridge worker registrations, or aggregate queue artifacts.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | `Test-Path scripts/cross_harness_bridge_trigger.py`; `git ls-files scripts/cross_harness_bridge_trigger.py` | Runtime file absent and untracked. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`; WI-4943 release integration | `rg -l "cross_harness_bridge_trigger|cross-harness-trigger|cross_harness_trigger" .claude .codex config groundtruth-kb/docs groundtruth-kb/templates groundtruth-kb/tests platform_tests scripts .temp_verified_cross_harness_006.md` | No matches in live release surfaces after implementation. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Focused pytest for renamed/retained parity tests plus the new retired-trigger residue guard. | Passing tests; no parity test depends on the retired trigger implementation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map every changed surface to an executed scan/test. | LO has concrete evidence to VERIFY or NO-GO. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain remains append-only; historical `bridge/gtkb-cross-harness-trigger-*` files are not deleted or rewritten. | No bridge history mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; owner deferral-expiry directive | Implementation report records any excluded historical/audit residue with trigger/date. | No open-ended deferrals. |

Minimum focused commands expected after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest <retired-trigger-guard-test> <renamed-or-retained-parity-tests> -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed-python-files>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed-python-files>
```

## Risk / Rollback

Risk: some residual files may be historical evidence rather than live release surfaces; over-cleaning could erase useful audit context. Mitigation: preserve formal bridge history and any explicitly historical evidence records unless they are part of current runtime, docs, templates, tests, or configuration.

Rollback is a single revert of the implementation commit. Rollback must not restore active trigger automation, worker hook registrations, or deleted retired scripts as supported dispatch paths.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4943-retired-trigger-residue-cleanout`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — this corrects incomplete release dispatcher-substrate reconciliation and removes release-blocking retired-subsystem residue.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
