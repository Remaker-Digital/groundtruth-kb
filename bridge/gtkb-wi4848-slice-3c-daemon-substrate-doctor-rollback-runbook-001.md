NEW

# gtkb-wi4848-slice-3c-daemon-substrate-doctor-rollback-runbook — Doctor readiness surface + substrate rollback runbook

bridge_kind: prime_proposal
Document: gtkb-wi4848-slice-3c-daemon-substrate-doctor-rollback-runbook
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-26 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-e-pb-autoproc-20260626
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Prime Builder

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4848

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py", ".claude/rules/dispatcher-daemon-substrate-rollback-runbook.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

After slice 3b registers `dispatcher_daemon` in the governed substrate selector, operators need **mechanical visibility** and a **documented rollback** before go-live. Slice **3c** adds:

1. A `gt doctor` check (WARN/ALARM severity) that correlates `harness-state/bridge-substrate.json` with dispatcher-daemon liveness (lock + heartbeat age via `collect_daemon_status`), surfacing "substrate says daemon but daemon is not healthy" and "daemon healthy but substrate still on trigger" advisory states.
2. A concise rollback runbook at `.claude/rules/dispatcher-daemon-substrate-rollback-runbook.md` describing the governed rollback transaction (`gt mode set-bridge-substrate --substrate cross_harness_trigger`), dispatch quiesce expectations, and verification steps (`gt bridge dispatch health`, `gt bridge dispatch daemon status`).

**Out of scope:** performing rollback or go-live in this slice; re-enabling dispatch; starting/stopping the daemon service (documented only).

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — daemon readiness is a pre-go-live invariant.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — doctor.py changes stay in-root under `groundtruth-kb/src/`.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — operator surfaces for dispatch service health.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — rollback uses governed substrate transaction, not manual JSON edits.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — doctor evidence supports release-readiness posture.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only bridge filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- `GOV-STANDING-BACKLOG-001` — WI-4848 governs.

## Prior Deliberations

- `DELIB-20266138` — "build flip, hold the switch"; 3c is the doctor + rollback runbook named in slice 3a out-of-scope.
- `DELIB-20265888` — dispatcher-service ownership of dispatch.
- WI-4848 slice 3a VERIFIED — triple-inert until selector + quiesce lifted.

## Owner Decisions / Input

No further owner decision required under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. Executing rollback or go-live remains owner-deliberate.

## Requirement Sufficiency

Existing requirements sufficient — slice 3a/3b and `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` define substrate authority; doctor + runbook operationalize readiness/rollback without new KB specs.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (doctor) | `test_doctor_dispatcher_substrate_mismatch_warns` (new) | substrate=`dispatcher_daemon` + stale/missing heartbeat → doctor WARN/ALARM |
| ADR-DISPATCHER-ARCHITECTURE-001 (doctor OK) | `test_doctor_dispatcher_substrate_healthy_ok` (new) | substrate=`dispatcher_daemon` + fresh heartbeat → OK or advisory-only |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 (runbook) | `test_rollback_runbook_exists_and_cites_governed_command` (new) | runbook file exists; contains `gt mode set-bridge-substrate` and `cross_harness_trigger` |
| No-regression | targeted doctor pytest module | green |

Commands (pre-report): `python -m pytest platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py -q --tb=short`; `ruff check` / `ruff format --check` on `doctor.py` and test file.

## Risk / Rollback

- Risk: low — additive doctor WARN surface and documentation only.
- Rollback: remove doctor check registration + runbook file.

## Bridge Filing

Append-only `bridge/gtkb-wi4848-slice-3c-daemon-substrate-doctor-rollback-runbook-001.md`.

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
