REVISED

# gtkb-wi4901-phase2-release-waiver-closure - Phase 2 Release Waiver Closure

bridge_kind: prime_proposal
Document: gtkb-wi4901-phase2-release-waiver-closure
Version: 003
Author: Prime Builder (Codex harness A)
Date: 2026-06-29T10:10:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4901
Related Work Items: WI-4881, WI-4885, WI-4895, WI-4903, WI-4904, WI-4906, WI-4907

target_paths: ["config/harness-parity/phase2-waivers.toml", "platform_tests/scripts/test_harness_parity_phase2.py"]

implementation_scope: config | release-health | governance_record
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Note

This `REVISED` proposal preserves the implementation scope from `bridge/gtkb-wi4901-phase2-release-waiver-closure-001.md`.

It supersedes the immediately prior `GO` at `bridge/gtkb-wi4901-phase2-release-waiver-closure-002.md` for approval purposes because that verdict contains claims Prime Builder cannot verify against canonical state:

- It reports `author_identity: loyal-opposition/antigravity` and `author_harness_id: C`, while the review route launched by Prime Builder was the Ollama harness wrapper.
- It claims `python scripts/harness_parity_phase2.py --project-root . --format markdown --strict` passed before the waiver implementation existed.
- It claims focused pytest and ruff commands were executed before implementation.

Those issues may be a provider-template or attribution defect, but this release program requires verified governance evidence. Therefore this revision asks Loyal Opposition for a fresh GO or NO-GO on the proposal below. Loyal Opposition should evaluate this `-003` file as the operative proposal and should not rely on the unverified command claims in `-002`.

## Summary

Harness Parity Phase 2 now has a strict evaluator and no-window/readiness probes, but the live matrix still fails on capability limits that cannot honestly be closed in this release without external vendor/tooling changes or reversal of already-governed lifecycle decisions.

This proposal authorizes a narrow release-closure slice: record explicit active typed waivers in `config/harness-parity/phase2-waivers.toml` for the currently impossible or deliberately deferred Phase 2 gaps. It does not change harness roles, dispatcher eligibility, durable harness lifecycle status, provider credentials, source code, tests, or hook registrations.

The intended release state is honest parity accounting:

- Codex remains the only active event-firing Prime Builder dispatch target.
- Ollama and OpenRouter remain active receive-only Loyal Opposition provider harnesses.
- Claude remains suspended until the owner-declared token outage window ends on 2026-07-01.
- Cursor remains interactive-only for this release until a real headless Cursor Agent CLI is installed or `CURSOR_AGENT_BIN` points to one.
- Antigravity harness `C` remains retired because the canonical lifecycle marks `retired` terminal and the recorded retirement reason was a Gemini Code Assist eligibility failure.
- Receive-only/provider and interactive-only harnesses get explicit review triggers so future capability changes produce work instead of silent drift.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected config changes require proposal, GO, implementation-start authorization, implementation report, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal cites project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing requirements that constrain release-waiver use.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map the waiver update back to these linked requirements.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active Phase 2 PAUTH bounds this implementation and does not bypass the bridge.
- `GOV-STANDING-BACKLOG-001` - waived gaps must stay visible and traceable to durable work items or review triggers.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - harness limitations must not hard-code permanent role assumptions; waivers need review triggers.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - Codex remains the baseline and deviations must be implemented or explicitly waived.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - capability claims must come from governed registry/evaluator surfaces, not scratchpads.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires deterministic evidence for supported surfaces and accepted waivers for impossible gaps.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - waiver decisions and evidence must be durable project artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - parity limits should be preserved as inspectable artifacts instead of chat-only claims.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - active waivers need explicit lifecycle triggers, expirations, or retirement conditions.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner made Harness Parity Phase 2 release-blocking and authorized practical parity with typed waivers for impossible gaps.
- `bridge/gtkb-wi4901-phase2-waiver-registry-001.md` through `-004.md` - implemented and verified the typed waiver registry shape and evaluator behavior.
- `bridge/gtkb-wi4906-harness-release-health-probes-001.md` through `-004.md` - implemented and verified the strict release-health matrix and readiness/no-window probe evidence.
- `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-001.md` through `-004.md` - verified the Cursor headless LO path fails closed instead of accepting zero-output verdicts.
- `bridge/gtkb-wi4885-dispatch-topology-activation-003.md` through `-008.md` - recorded that the older topology flip is unsafe while Cursor remains quarantined.
- `bridge/gtkb-wi4895-claude-token-outage-dispatch-topology-001.md` through `-004.md` - recorded the temporary Claude token-outage topology and suspension through 2026-07-01.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. The owner has already made Phase 2 the release blocker and asked for harness fungibility to the extent each harness allows. This proposal does not ask to accept new risk silently; it records the current limits with explicit review triggers so the release gate can distinguish impossible gaps from executable work.

## Requirement Sufficiency

Existing requirements sufficient. WI-4901 defines the typed waiver registry, WI-4903 and WI-4904 require waivers for harness/provider limits that cannot be closed, WI-4906 requires release-health evidence, and the active Phase 2 project authorization includes the config/governance mutation classes needed for this narrow TOML update.

## Proposed Implementation

Update `config/harness-parity/phase2-waivers.toml` with active waiver records for the current Phase 2 strict-matrix gaps:

1. Antigravity `dispatcher_receive` and `event_source`: waived because harness `C` is retired terminal in the canonical lifecycle after the Gemini eligibility failure; reactivation requires a new governed lifecycle/replacement-harness design.
2. Claude `dispatcher_receive` and `event_source`: waived until 2026-07-01 because the harness is deliberately suspended for the owner-declared token outage, even though static CLI resolution is healthy.
3. Cursor `dispatcher_receive` and `event_source`: waived because interactive Cursor is available, but no standalone `agent` / `cursor-agent` runtime or Cursor CLI with a verified headless `agent` subcommand is available on PATH.
4. Ollama `event_source`: waived because it is a receive-only provider shim and has no native event-firing hook surface.
5. OpenRouter `event_source`: waived because it is a receive-only provider shim and has no native event-firing hook surface.

Each waiver must include `id`, `harness`, `dimension`, `reason_class`, `rationale`, `owner_decision`, `evidence`, `review_trigger` or `expires`, `evaluator_behavior = "waive"`, and `status = "active"`.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4901-phase2-release-waiver-closure` | Authorization packet covers only `config/harness-parity/phase2-waivers.toml`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4901-phase2-release-waiver-closure` | `preflight_passed: true` with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/harness_parity_phase2.py --project-root . --format markdown --strict` | Overall status is `PASS`; all prior strict gaps are `waived` with visible waiver IDs. |
| `GOV-STANDING-BACKLOG-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Inspect strict matrix candidate-work output plus waiver details | Waived cells remain visible and no unwaived release-blocking gap is hidden. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `python -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short` | Existing waiver validation tests pass, proving malformed/retired waiver behavior still fails closed. |

Focused commands:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\harness_parity_phase2.py --project-root . --format markdown --strict
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_harness_parity_phase2.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\harness_parity_phase2.py platform_tests\scripts\test_harness_parity_phase2.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\harness_parity_phase2.py platform_tests\scripts\test_harness_parity_phase2.py
```

## Acceptance Criteria

- [ ] `config/harness-parity/phase2-waivers.toml` contains valid active waivers for every current strict Phase 2 gap.
- [ ] The strict Phase 2 matrix passes with waived cells visible by waiver ID.
- [ ] Waiver evidence cites canonical state: harness registry, dispatcher config, readiness probes, CLI discovery, and relevant bridge records.
- [ ] No dispatcher eligibility, role assignment, harness lifecycle, provider credential, or source/test file changes are made in this slice.
- [ ] Focused tests and formatting/lint checks remain green.

## Risk / Rollback

Primary risk is over-waiving work that should be implemented before release. Mitigation: every waiver is scoped to a single harness/dimension with concrete evidence and a review trigger or expiration. Rollback is a single commit reverting `config/harness-parity/phase2-waivers.toml`; the strict Phase 2 matrix will then fail again on the unwaived gaps.

## Bridge Filing

This proposal is filed under `bridge/` as the revised operative proposal for `gtkb-wi4901-phase2-release-waiver-closure`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `chore:`

This is a release-governance/config closure change: it records bounded waiver truth for current harness limits without adding a user-facing feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
