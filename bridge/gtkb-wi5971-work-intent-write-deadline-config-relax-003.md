NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f53987e0-de4b-4e90-a890-c0a98a4af012
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5971-work-intent-write-deadline-config-relax
Version: 003
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-wi5971-work-intent-write-deadline-config-relax-002.md
Prior GO: bridge/gtkb-wi5971-work-intent-write-deadline-config-relax-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5971

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]
implementation_scope: work_intent_write_retry_deadline_config_backed_and_relaxed
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

**No KB mutation.** No MemBase write; `groundtruth.db` schema and rows unchanged.
**No approval-evidence work.** No formal-artifact-approval packet created.
**No dispatcher or TAFE mutation.** No commit created by Prime Builder.

# WI-5971 Implementation Report - config-backed, relaxed-first work-intent write deadline

## Implementation Summary

All four Proposed Scope items are implemented exactly as approved at `-002`.
Only the two declared `target_paths` changed.

### Scope 1 - config-backed resolution

Added `WORK_INTENT_WRITE_RETRY_DEADLINE_ENV = "GTKB_WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS"`
and `resolve_work_intent_write_retry_deadline(explicit: float | None = None) -> float`
in `scripts/bridge_work_intent_registry.py`. The helper mirrors
`_resolve_registry_lock_timeout` in
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:279-304`
clause for clause: explicit caller value wins; else the env var when it parses
as a positive float; else the module default. Malformed input returns the
default (fail-open), and a non-positive value falls through to the default,
matching the precedent's `if value > 0` guard.

### Scope 2 - relaxed-first default

`WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS` raised from `10.0` to `300.0`,
aligning with the registry control-plane precedent named in the proposal.

### Scope 3 - adjacent knobs unchanged

Both call sites (`scripts/bridge_work_intent_registry.py:360` and `:1272`, the
pre-edit line numbers cited in the proposal being `315` and `1227`) now read
`deadline = started_at + resolve_work_intent_write_retry_deadline()`. Nothing
else in the retry path changed: `WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS`
(0.25), `WORK_INTENT_WRITE_INITIAL_BACKOFF_SECONDS` (0.025), and
`WORK_INTENT_WRITE_MAX_BACKOFF_SECONDS` (0.5) keep their WI-5784 values, and
lock ordering, exclusivity, and release semantics are untouched. A dedicated
test pins those three constants so a future change that widened them alongside
the deadline would fail.

`__all__` gained `WORK_INTENT_WRITE_RETRY_DEADLINE_ENV` and
`resolve_work_intent_write_retry_deadline`.

### Scope 4 - focused tests

Six tests added to `platform_tests/scripts/test_bridge_work_intent_registry.py`
(10 cases including parametrization), covering scope items (a) through (d) plus
the scope-3 invariant.

## Specification Links

Carried forward unchanged from the approved proposal at `-001`.

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge-state authority whose atomic
  VERIFIED finalization writes are blocked by the retired deadline; append-only
  and fail-closed guarantees are preserved (no lifecycle or status logic
  touched).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links carried
  forward here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping and
  executed evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5971 bound to
  PROJECT-GTKB-HOUSEKEEPING-HARDENING via the whole-project PAUTH.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both targets in-root under
  `E:/GT-KB`; no `applications/` path touched.
- `GOV-STANDING-BACKLOG-001` - WI-5971 is the governed backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact lifecycle preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - no lifecycle transition triggered.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - advisory; artifact-first delivery.

## Prior Deliberations

- `DELIB-202667722` - timer governance (relaxed-first, config-backed, no
  invisible hard-coded values). The implemented helper and the 300.0 default
  conform directly.
- WI-5788 / WI-5869 - the registry control-plane lock precedent this mirrors.
- WI-5784 - introduced the 10.0s deadline now relaxed.
- WI-5881 - reservation claim-fence CAS primitive; unchanged here.
- Finalization-contention NO-GO cluster
  (`bridge/gtkb-wi5939-false-terminal-finalization-recovery-004.md`,
  `bridge/gtkb-wi5941-deterministic-release-deadline-test-008.md`) - the cluster
  this deadline blocks.

## Owner Decisions / Input

- Owner AUQ 2026-08-06: presented with the finding that the NO-GO queue was
  dominated by a finalization-contention loop cluster, the owner selected **"Fix
  the root cause"**, authorizing this work. Carried forward from the approved
  proposal; no new owner decision was required or taken during implementation.
- Owner AUQ 2026-08-07: "Durable fix + proceed now" - authorized correcting
  harness B's registry role to `prime-builder`, which (with the owner's
  subsequent `::init gtkb pb`) established the Prime Builder session that
  performed this implementation.

## Spec-to-Test Mapping

| Requirement (Proposed Scope) | Test | Result |
| --- | --- | --- |
| 1 - explicit caller value wins | `test_wi5971_explicit_argument_wins_over_env` | PASS |
| 1 - env var resolution | `test_wi5971_env_var_overrides_default` | PASS |
| 1 - fail-open on malformed/non-positive | `test_wi5971_malformed_or_nonpositive_env_fails_open` (5 params: `""`, `"notanumber"`, `"0"`, `"-3"`, `"  "`) | PASS |
| 1 - unset env resolves to default | `test_wi5971_unset_env_uses_default` | PASS |
| 2 - relaxed-first default is 300.0 | `test_wi5971_default_deadline_is_relaxed_first` | PASS |
| 3 - adjacent retry knobs unchanged | `test_wi5971_adjacent_retry_knobs_unchanged` | PASS |
| 4 - no regression in the module | full `test_bridge_work_intent_registry.py` (62 tests) | PASS |

## Commands Executed

```
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5971-work-intent-write-deadline-config-relax
  -> allowed; packet expires 2026-08-07T06:48:53Z;
     pre_start_packet_hash sha256:173d2b4fbe089f397f032fb1c46b98801b298e51648037e8d6e34c53b6facc77

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q -k wi5971
  -> 10 passed, 52 deselected

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q
  -> 62 passed, 5 warnings

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
  -> 2 files already formatted
```

Direct resolution probe (all six precedence cases observed):

```
default                 -> 300.0
explicit=7.5            -> 7.5
env=45                  -> 45.0
env=malformed           -> 300.0   (fail-open)
env=-3                  -> 300.0   (non-positive -> default)
env=45 + explicit=2.0   -> 2.0     (explicit wins)
```

## Pre-Existing Failures Disclosed (NOT caused by this change)

`platform_tests/scripts/test_bridge_claim_cli.py` has **4 failing tests**:

```
test_claim_go_implementation_uses_versioned_bridge_files_without_index
test_claim_go_implementation_uses_host_bound_cli_envelope_provenance
test_claim_go_implementation_preempts_lingering_draft_claim
test_claim_go_implementation_refuses_peer_go_holder
```

All four fail with `Worker role provenance is missing for the current session.
(not prime-eligible)` - a role-provenance defect, not a retry-deadline defect.

**Causality established by measurement, not assertion.** Both target files were
stashed (`git stash push -- <both paths>`) and the module re-run at the clean
baseline: **the identical 4 tests failed, 10 passed**. With the change restored
the counts are unchanged. These failures therefore pre-date this work and are
outside its scope. They are consistent with WI-5979 (filed this session), which
documents the worker-role-provenance binding gap on the claude harness.

## Acceptance Criteria Check

1. Deadline is config-backed via the new env var, resolved through a helper
   mirroring `_resolve_registry_lock_timeout` - **met**.
2. Default raised from 10.0 to the relaxed-first 300.0 - **met**.
3. Lock ordering, exclusivity, per-attempt timeout, backoff/jitter, and release
   semantics unchanged; only the total-deadline value and its resolution path
   changed - **met**, and pinned by test.
4. Tests cover default, valid env override, unset/malformed fail-open, and
   explicit-argument precedence - **met** (10 cases).
5. Only the two declared `target_paths` changed - **met**.
6. Both ruff gates pass on both changed files - **met**.
7. No KB row, TAFE/dispatcher state, formal artifact, credential, deployment, or
   external system mutated; no commit created by Prime Builder - **met**.
   Finalization remains the Loyal Opposition atomic step.

## Out of Scope (unchanged, per the approved proposal)

SQLite `journal_mode` (already WAL), `synchronous`, lock ordering, the
registry-control-plane lock, and the git-commit finalization sequence are
untouched.

## Bridge Chain Discipline

This artifact is filed as
`bridge/gtkb-wi5971-work-intent-write-deadline-config-relax-003.md`, the next
numbered file in this thread, written through the governed bridge writer. The
numbered bridge files under `bridge/` are canonical and append-only: no prior
version is deleted or rewritten, and the `-002` `GO` it responds to is preserved
intact. Per the Post-Verdict Transition Table this first post-`GO`
implementation report publishes as `NEW`.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both changed files are in-root
platform paths; this bridge file resides under `E:/GT-KB/bridge/`. No
`applications/` path is touched.

## Recommended Commit Type

`fix:` - repairs a defect in which sustained concurrent claim and finalization
writers hard-failed at an invisible hard-coded deadline. No new capability
surface is added; the helper makes an existing value config-backed and aligns it
with the established registry-lock precedent.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
