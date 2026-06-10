NEW

# Implementation Proposal - Envelope Runtime Capstone Integration (WI-4301)

bridge_kind: prime_proposal
Document: gtkb-envelope-runtime-capstone-impl
Version: 001
Author: Codex (owner-directed implementation kickoff)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-envelope-implementation-umbrella-capstone-002.md

author_identity: Codex owner-directed implementation agent
author_harness_id: A
author_session_context_id: 2026-06-05-wi-4301-capstone-proposal
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop, owner-directed implementation request

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4301
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/__init__.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/__init__.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/scheduler.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/db.py", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_dispatcher_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Implement the remaining WI-4301 capstone runtime that binds the envelope
program together after the WI-4298 open-disclosure and WI-4299 handoff service
threads reached VERIFIED.

The implementation adds per-harness session-envelope state and archive writing,
strict `::wrap` / `::open <type>` / `::close <type>` command handling,
topic-envelope preload and route-target metadata, deterministic wrap closure,
dispatch-envelope rules loading and activity-gated scheduling, Codex
UserPromptSubmit hook integration, and focused platform tests.

## Prior Deliberations

- `DELIB-20260872` - PAUTH v2 mint authorizing source/test/hook work for
  WI-4298, WI-4299, and WI-4301 capstone integration.
- `DELIB-20260636` - envelope-program grilling and runtime shape.
- `DELIB-20260637` - topic-envelope terminology decision.
- `DELIB-2238` - session-envelope foundation.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic service mandate.
- Bridge `gtkb-envelope-implementation-umbrella-capstone-001.md` and GO verdict
  `-002.md` - five-slice capstone scope.
- Bridge `gtkb-envelope-disclosure-ui-impl-013.md` - VERIFIED open disclosure.
- Bridge `gtkb-handoff-prompt-deterministic-service-impl-011.md` - VERIFIED
  deterministic handoff-prompt service.

## Specification Links

Primary capstone specifications:

- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001`
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001`
- `SPEC-TOPIC-ENVELOPE-ROUTER-001`
- `SPEC-SPEC-TOPIC-ENVELOPE-001`
- `SPEC-BUILD-TOPIC-ENVELOPE-001`
- `SPEC-TEST-TOPIC-ENVELOPE-001`
- `SPEC-DELIBERATION-TOPIC-ENVELOPE-001`
- `SPEC-PROJECT-TOPIC-ENVELOPE-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `SPEC-ENVELOPE-DISCLOSURE-UI-001`
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`

Cross-cutting blocking specifications:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`

Cross-cutting advisory specifications:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

1. `DELIB-20260872` authorizes the capstone integration mutation classes under
   the envelope-program PAUTH.
2. Mike's 2026-06-05 owner prompt explicitly directs Codex to finish WI-4301
   now using existing envelope tests and startup priorities.

No fresh AUQ is required for this implementation. The work is the bounded
source/test/hook realization of already-specified WI-4301 capstone behavior.

## Requirement Sufficiency

Existing requirements sufficient. The cited session-envelope, wrap, topic
envelope, dispatch-envelope, disclosure, and handoff specifications define the
runtime behavior. No new or revised requirement is required before
implementation.

## Scope Boundaries

In scope:

- New deterministic runtime modules under `groundtruth_kb.session`.
- New deterministic dispatcher modules under `groundtruth_kb.dispatcher`.
- CLI registration for session envelope/topic/wrap helpers and dispatcher
  validation/tick helpers.
- `dispatch_events` schema presence in `groundtruth_kb.db`.
- Codex UserPromptSubmit hook handling for canonical `::wrap`, `::open`, and
  `::close` commands.
- Focused platform tests for envelope runtime, dispatcher rules, and hook
  command recognition.

Out of scope:

- Further edits to the already-VERIFIED open-disclosure shape from WI-4298.
- Further edits to the already-VERIFIED handoff-prompt service semantics from
  WI-4299 except CLI grouping compatibility needed by this capstone.
- MemBase status mutation for WI-4301; that remains a follow-on artifact update
  after implementation verification.
- Claude hook parity beyond existing startup/wrap surfaces; this proposal
  targets the active Codex UserPromptSubmit hook for the current session.

## Spec-Derived Verification Plan

- `DCL-SESSION-ENVELOPE-DURABILITY-001`: run
  `platform_tests/scripts/test_session_envelope_runtime.py` to verify current
  file and archive path contract.
- `SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001`: run session envelope and hook tests
  to verify exact first-non-blank-line `::wrap` matching.
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001`: run session envelope
  tests to verify mandatory wrap steps 1, 4, 8, 11, and 12 in archive JSON.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001`: run session envelope tests to verify strict
  topic open/close parsing and one-topic-per-type behavior.
- Per-type topic specs: run session envelope tests to verify preload state and
  route target metadata.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` and
  `DCL-DISPATCH-ENVELOPE-RULES-001`: run dispatcher tests to verify rules
  schema, mandatory `activity_gate`, empty registry load, dry-run logging, and
  persisted scheduler state.
- `SPEC-ENVELOPE-DISCLOSURE-UI-001`,
  `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`, and worker packet
  regressions: run the existing targeted envelope regression suite named below.

Verification commands:

```text
python -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_dispatcher_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_init_keyword_matching.py platform_tests/scripts/test_session_handoff_service.py platform_tests/scripts/test_worker_packet_authorization_envelope.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/session groundtruth-kb/src/groundtruth_kb/dispatcher groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/db.py .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_dispatcher_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/session groundtruth-kb/src/groundtruth_kb/dispatcher groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/db.py .codex/gtkb-hooks/session_wrapup_trigger_dispatch.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_dispatcher_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py
```

## Risk / Rollback

Risk is concentrated in prompt-time hook behavior and session state writes.
Mitigations are strict parser tests, temp-root runtime tests, and dry-run
default dispatcher behavior. Rollback is a single commit revert; runtime state
files are ignored/generated and are not part of the source diff.

