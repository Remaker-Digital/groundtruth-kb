NEW

# gtkb-wi4778-cursor-headless-dispatch-readiness — Cursor headless dispatch readiness probe and activation gate

bridge_kind: prime_proposal
Document: gtkb-wi4778-cursor-headless-dispatch-readiness
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: gpt-5-codex
author_model_version: 2026-06-29
author_model_configuration: Codex desktop Prime Builder session; approval_policy=never; Harness Parity Phase 2 release-hardening

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4778

target_paths: ["scripts/cursor_harness.py", "scripts/verify_cursor_dispatch.py", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/scripts/test_verify_cursor_dispatch.py", "platform_tests/groundtruth_kb/test_doctor_cursor_dispatch.py", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "config/agent-control/harness-capability-registry.toml"]

implementation_scope: source | config | test | governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4778 asks for Cursor harness E to become a reliable headless Loyal Opposition dispatch target. The verified WI-4881 work now makes `scripts/cursor_harness.py` fail closed when a bridge-review or verification route returns empty stdout, but current host evidence shows Cursor is still not dispatchable: no standalone `agent` or `cursor-agent` executable is on PATH, `CURSOR_AGENT_BIN` is unset, and the installed `cursor.cmd agent --help` surface prints the ordinary Cursor editor launcher help rather than a headless Agent CLI with `--print` / `--output-format`.

This proposal closes the release-health gap by adding deterministic Cursor dispatch readiness evidence and activation gating. Implementation may complete prompt-route parity and readiness plumbing, but it must not mark Cursor E as `can_receive_dispatch=true` unless the readiness probe proves that a headless Cursor Agent CLI is available and can produce non-empty bridge output without visible console windows. On this host, the expected honest release posture is a fail-closed Cursor quarantine until the external Agent CLI exists.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires Prime Builder implementation to proceed only after Loyal Opposition `GO` and to return through the bridge for verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this implementation proposal to cite all relevant governance, dispatch, and harness requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the project authorization, project, and work-item linkage metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the implementation report to carry forward linked specifications and executed tests.
- `GOV-STANDING-BACKLOG-001` — makes WI-4778 a MemBase work item in the release-blocking Harness Parity Phase 2 project, not an ad hoc task.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — requires cross-harness governance behavior to be enforced through equivalent native or fallback surfaces.
- `ADR-DISPATCHER-ARCHITECTURE-001` — constrains dispatcher readiness, target selection, and fail-closed handling for harness recipients.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — requires central dispatcher health/reporting to reflect actual target dispatchability.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — governs headless dispatch envelopes, author metadata, and route-specific failure handling.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — requires harnesses to declare and verify bridge, root-boundary, metadata, destructive-gate, and tool-surface behavior before promotion.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — constrains edits under `groundtruth-kb/src/groundtruth_kb/project/doctor.py` to respect the GT-KB root/application placement boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires discovered parity/readiness facts and future-work outcomes to be preserved as governed artifacts rather than scratchpad claims.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — frames the implementation as a traceable artifact graph connecting work item, proposal, tests, dispatcher state, and release evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — governs the readiness state distinction between supported, unavailable/quarantined, verified, and release-blocking outcomes.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — owner directive creating Harness Parity Phase 2 as a release blocker and authorizing bounded implementation through normal bridge gates.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` — prior sequencing decision to harden Claude/Cursor dispatch surfaces before broader topology activation.
- `DELIB-20266209` — Cursor headless Loyal Opposition skill-route context carried by the WI-4881 evidence chain.
- `bridge/gtkb-wi4872-cursor-harness-lo-skill-route-alias-004.md` — verified Cursor skill-route alias fix for `bridge-review` and `verification`.
- `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-004.md` — verified fail-closed guard for empty Cursor bridge-review/verification output.
- `bridge/gtkb-wi4885-dispatch-topology-activation-008.md` — NO-GO holding topology activation because Cursor remains quarantined.
- `bridge/gtkb-wi4903-antigravity-dispatch-parity-readiness-004.md` — related Phase 2 harness-readiness precedent: readiness evidence first, activation only when honest.

## Owner Decisions / Input

No new owner decision is required before implementation. The work is covered by `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` and active project authorization `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`. This proposal does not install external Cursor software, rotate credentials, perform production deployment, or mutate GitHub settings. If implementation proves that a headless Cursor Agent CLI is absent, the required outcome is a fail-closed readiness finding and continued dispatcher quarantine, not an owner-decision prompt hidden inside implementation.

## Requirement Sufficiency

Existing requirements sufficient. WI-4778 defines the work item scope, `PROJECT-HARNESS-PARITY-PHASE-2` defines the release-blocking parity objective, and the linked dispatch/governance specifications define the implementation and verification constraints. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Implementation must provide or update tests and commands that demonstrate:

- Cursor headless Agent CLI detection distinguishes standalone `agent`, `CURSOR_AGENT_BIN`, and `cursor agent` support from the ordinary editor launcher.
- Bridge-review and verification routes require non-empty output and fail closed on zero-output success.
- Readiness probes use hidden/no-window subprocess flags on Windows.
- Dispatcher/doctor surfaces report Cursor unavailable when the headless Agent CLI is absent and do not select Cursor as an LO recipient in that state.
- If the headless Agent CLI is present, the probe can prove availability without mutating bridge state or launching visible consoles.
- Harness parity output and capability registry state honestly distinguish supported, degraded/fallback, unsupported, and host-unavailable surfaces.

Expected focused verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/groundtruth_kb/test_doctor_cursor_dispatch.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/verify_cursor_dispatch.py --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --json
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cursor_harness.py scripts/verify_cursor_dispatch.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/groundtruth_kb/test_doctor_cursor_dispatch.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cursor_harness.py scripts/verify_cursor_dispatch.py scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/groundtruth_kb/test_doctor_cursor_dispatch.py
```

## Risk / Rollback

Primary risk is an over-eager activation that selects Cursor for headless LO dispatch before the external Agent CLI is actually available. Mitigation: readiness must fail closed and dispatcher activation must be conditioned on the probe result. Secondary risk is visible Windows console launch during readiness probing; implementation must use the same no-window discipline already verified for the Cursor harness shim. Rollback is a single commit revert that removes the probe/doctor wiring and restores prior Cursor quarantine state.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4778-cursor-headless-dispatch-readiness`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: this repairs a release-blocking dispatch readiness gap by adding fail-closed Cursor readiness evidence and preventing premature selection of an unavailable headless harness.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
