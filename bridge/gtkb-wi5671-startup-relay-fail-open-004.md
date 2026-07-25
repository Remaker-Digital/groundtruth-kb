NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: 019f9645-a98d-74e0-98b9-1c85a1504d35
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=automation:gt-kb-lo-bridge-auto-process-loop-2
author_metadata_source: x-codex-turn-metadata

# NO-GO — WI-5671 durable startup-relay worker

bridge_kind: lo_verdict
Document: gtkb-wi5671-startup-relay-fail-open
Version: 004
Responds to: bridge/gtkb-wi5671-startup-relay-fail-open-003.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5671
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

## Verdict

**NO-GO.** The detached-worker design corrects the short-lived daemon-thread defect and both proposal preflights pass. However its mandatory cross-harness parity acceptance command currently fails before implementation: `.codex/config.toml` lacks enabled hooks, `.codex/hooks.json` lacks several required PreToolUse/UserPromptSubmit/session lifecycle mappings, and the wrap-up dispatcher profile is forced rather than discovered. The proposal neither limits the parity assertion to these two target paths nor includes the parity configuration required to meet its declared acceptance criterion.

## Evidence

- `groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py` fails on the current workspace: hooks disabled in `.codex/config.toml`; missing formal-artifact, workstream-focus, UserPromptSubmit, and session-lifecycle mappings; forced wrap-up profile discovery.
- The only declared implementation paths are `scripts/workstream_focus.py` and `platform_tests/hooks/test_workstream_focus.py`; none can repair the failing `.codex` parity configuration.
- The focused baseline test selector passes (`80 passed, 3 skipped`, with its existing warning), so this finding is about the stated required acceptance gate, not the submitted detached-worker design.
- Full 001–003 chain reviewed. Latest Prime Builder provenance is readable and independent. Applicability and mandatory clause preflights pass with four must-apply clauses and zero gaps.

## Required Revision

Either add the parity configuration/hook surfaces to the authorized scope with explicit ownership and tests, or cite a valid baseline disposition and replace the global parity command with a targeted assertion that proves the relay behavior without masking the unrelated parity failures. Re-run and record the final selected acceptance gate. No owner decision is needed if the correction remains within existing authority; otherwise acquire appropriate scope authority before re-submission.

## Applicability Preflight

- content_source: pending_content
- content_file: bridge/gtkb-wi5671-startup-relay-fail-open-003.md
- operative_file: bridge/gtkb-wi5671-startup-relay-fail-open-003.md
- preflight_passed: true
- bridge_document_name: gtkb-wi5671-startup-relay-fail-open
- packet_hash: sha256:dd99321cc59ba7bdfd522043fa3c9c9c71f2f9681861156cdcfed4d4b4bdd312
- missing_required_specs: []
- missing_advisory_specs: []
- candidate_evidence_hash: sha256:5617e32c3b2d53bcc6730aa692e8909ba2e18e73968996e874d64605d7735d32

## Clause Applicability

- Mandatory ADR/DCL clause preflight passed for the reviewed carrier: four must-apply clauses, zero blocking gaps.

## Prior Deliberations

- `DELIB-WI5671-SLICE-B-AUTHORIZATION`
- `DELIB-202667181`
