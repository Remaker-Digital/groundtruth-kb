NEW

# gtkb-wi-auto-spec-intake-46594e-activity-envelope-context-sharding — Activity Envelope Context Sharding

bridge_kind: prime_proposal
Document: gtkb-wi-auto-spec-intake-46594e-activity-envelope-context-sharding
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-30T19:07:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-interactive-2026-06-30-activity-envelope-context-sharding
author_model: GPT-5 Codex
author_model_version: current Codex desktop runtime
author_model_configuration: default Codex desktop coding-agent configuration

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-WI-AUTO-SPEC-INTAKE-46594E-ACTIVITY-SHARDING
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-AUTO-SPEC-INTAKE-46594E

target_paths: ["config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md", "config/agent-control/activity-disposition-profiles.toml", "config/agent-control/skill-scenarios.toml", "scripts/startup_glossary_load.py", "scripts/session_self_initialization.py", "scripts/skill_usage_router.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "groundtruth-kb/src/groundtruth_kb/canonical_terms.py", ".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_startup_index.py", "platform_tests/scripts/test_startup_payload_budget_report.py", "platform_tests/scripts/test_skill_usage_router.py", "platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py"]

implementation_scope: source | governance | protocol | tests | documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner directed that canonical terminology and skill context be loaded by
activity envelope rather than loaded wholesale at base session startup. The
base session envelope should contain only core GT-KB vocabulary and lightweight
routing cues; activity-specific terms and skills should appear only when an
agent opens the corresponding activity envelope with `::open <activity>`.

This proposal implements that progressive-disclosure model on the existing
activity-envelope surfaces. It will keep the current activity profile shape
(`skills`, `terminology`, `history_state`, `direction`) but make it operative:
startup glossary loading becomes a core-term subset, activity profiles become
the authoritative per-activity terminology/skill reference, and the topic
router renders bounded context for opened activities without forcing every
session to read the full terminology corpus or arbitrary skill bodies.

## Specification Links

- `SPEC-INTAKE-46594e` — owner-stated requirement that base session startup loads only core GT-KB terminology, activity-specific terms load only for the related activity envelope, and skills follow the same activity-envelope loading pattern.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` — existing 4-class activity profile schema already defines `skills`, `terminology`, `history_state`, and `direction`; this work makes those fields the operative context-load contract.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` — governs the `::open <activity>` / `::close` activity-envelope command surface and the closed activity vocabulary `{ops, deliberation, build, test, spec, project}`.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — requires startup token-cost awareness and preferred controls including index-first artifact loading, targeted skill loading, and progressive disclosure.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected startup/source/config/governance changes require proposal, LO review, implementation report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links the implementation to the governing spec and DCLs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal carries Project Authorization, Project, Work Item, and concrete `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must derive tests from the linked terminology/skill loading requirement.
- `GOV-STANDING-BACKLOG-001` — the new work item remains in the canonical MemBase-backed backlog and is attached to the existing envelope-refinement project.

## Prior Deliberations

- `INTAKE-27bf7cdb` — owner requirement captured and confirmed into `SPEC-INTAKE-46594e`; this proposal implements that requirement.
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` — owner authorization for implementation of `PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT`, applied to this new spec/WI.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` provenance cites owner decisions `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` and `DELIB-20265287`, which established the four activity profile payload classes and the six canonical activity types.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v3 records the single-active activity-envelope command model that this implementation will use as the context-load trigger.

## Owner Decisions / Input

Owner gave two current-session directives:

- "Canonical terminology should be sharded based on activity envelope requirements..." captured as `INTAKE-27bf7cdb` and confirmed to `SPEC-INTAKE-46594e`.
- "I approve and authorize the implementation of the PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT project." captured as `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` and bound to `PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-WI-AUTO-SPEC-INTAKE-46594E-ACTIVITY-SHARDING`.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-46594e` states the new owner
requirement; `DCL-ACTIVITY-DISPOSITION-PROFILE-001`,
`SPEC-TOPIC-ENVELOPE-ROUTER-001`, and
`DCL-SESSION-STARTUP-TOKEN-BUDGET-001` define the relevant activity-profile,
router, and startup-budget constraints. No further AUQ is required before LO
review.

## Cross-Harness Disposition

This implementation changes shared GT-KB startup/activity-envelope behavior used
by Claude, Codex, Cursor, Antigravity, Ollama, and OpenRouter through the common
Python session/topic-router modules and shared `config/agent-control` profile
data. It does not add harness-specific skill bodies, hooks, or adapter-only
behavior. Parity requirement: every harness that receives `::open <activity>`
context must see the same activity profile fields, the same bounded terminology
references, and the same activity-scoped skill recommendations for the same
activity type.

No typed waiver is requested. If implementation discovers that a harness-specific
hook or adapter must change, the implementation report must name that surface and
run the relevant parity/generator checks.

## Spec-Derived Verification Plan

Spec-to-test mapping:

```text
SPEC-INTAKE-46594e
  - Add/extend startup glossary tests proving the base session summary loads only a bounded core terminology subset and does not require reading/rendering every term from canonical-terminology.md.
  - Add/extend topic-router/activity-envelope tests proving `::open <activity>` injects that activity's terminology references and skill list while unrelated activity terms/skills are absent.
  - Add/extend skill-router/profile tests proving skill recommendations are activity/scenario scoped and not arbitrary base-startup loads.

DCL-ACTIVITY-DISPOSITION-PROFILE-001
  - Add/extend profile-loader tests proving every canonical activity has `skills` and `terminology` entries and those entries drive rendered activity context.

SPEC-TOPIC-ENVELOPE-ROUTER-001
  - Add/extend session-envelope tests proving the context-load trigger remains the strict `::open <activity>` command over the closed activity vocabulary.

DCL-SESSION-STARTUP-TOKEN-BUDGET-001
  - Add/extend startup payload budget/profile tests proving base startup remains minimized and reports/uses progressive disclosure for activity context.

DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 and DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - Run bridge applicability and ADR/DCL clause preflights against this proposal and the implementation report.
```

Expected verification commands:

```text
python -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_startup_payload_budget_report.py platform_tests/scripts/test_skill_usage_router.py platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py -q --tb=short
python -m ruff check scripts/startup_glossary_load.py scripts/session_self_initialization.py scripts/skill_usage_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/activity/profiles.py groundtruth-kb/src/groundtruth_kb/canonical_terms.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_startup_payload_budget_report.py platform_tests/scripts/test_skill_usage_router.py platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py
python -m ruff format --check scripts/startup_glossary_load.py scripts/session_self_initialization.py scripts/skill_usage_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/activity/profiles.py groundtruth-kb/src/groundtruth_kb/canonical_terms.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_startup_payload_budget_report.py platform_tests/scripts/test_skill_usage_router.py platform_tests/scripts/test_check_canonical_terminology_doctor_integration.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-auto-spec-intake-46594e-activity-envelope-context-sharding
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-auto-spec-intake-46594e-activity-envelope-context-sharding
```

## Risk / Rollback

Risk is concentrated in startup/context routing: over-sharding could hide a term
needed for base role safety, while under-sharding preserves the current token
waste. Implementation must keep role/bridge/core GT-KB vocabulary in the base
startup subset and move only activity-specific vocabulary/skill recommendations
behind the `::open <activity>` trigger. Rollback is a single commit reverting the
profile/config/source/test/doc changes and restoring the prior monolithic
startup terminology behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi-auto-spec-intake-46594e-activity-envelope-context-sharding`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat — changes the session/activity-envelope context-loading behavior and adds
tests for the new progressive-disclosure contract.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
