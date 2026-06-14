NEW

bridge_kind: implementation_report
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 009
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: af95d800-1e77-45cf-852b-6285e885373d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC
Review-Target: bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md
GO-Authorization: bridge/gtkb-wi4534-claim-role-eligibility-guard-008.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4534

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_go_impl_claim_timebox.py"]

# Implementation Report (NEW -009) — WI-4534 Slice A: Role-Eligibility Guard + Timebox-Regression Repair

## Claim

The GO'd REVISED proposal at
`bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md` (GO at `-008`) is
implemented. The registry-authoritative role-eligibility guard on
`go_implementation` work-intent claim acquisition is in place and verified by 8
passing role-eligibility tests, and the timebox-regression suite surfaced by the
guard is repaired green (8 passing) under the strict-F3 contract authorized by
`DELIB-20263205`. All work is confined to the three approved `target_paths`.

## Implementation Authorization

Per the GO's Implementation Conditions, the implementation-start packet was
created from the latest GO before any edit:

```powershell
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4534-claim-role-eligibility-guard
```

- `latest_status`: `GO`
- `go_file`: `bridge/gtkb-wi4534-claim-role-eligibility-guard-008.md`
- `packet_hash`: `sha256:4923c04b89158150b2e795995617671ba35f380253cfd839d53a835d5950ca79`
- `target_path_globs`: exactly the three approved paths
  (`scripts/bridge_work_intent_registry.py`,
  `platform_tests/scripts/test_work_intent_role_eligibility.py`,
  `platform_tests/scripts/test_go_impl_claim_timebox.py`).

The packet includes `platform_tests/scripts/test_go_impl_claim_timebox.py`, so
the GO's stop-and-file-a-bridge-issue precondition did not trigger.

## What Was Implemented

### Part 1 — Guard (unchanged from the GO'd -003 design; already on disk)

`scripts/bridge_work_intent_registry.py` carries the registry-authoritative
role-eligibility guard exactly as described in the `-007` Design section:
`DISPATCH_SESSION_ID_RE` + `_dispatch_harness_id` (role token only locates the
harness-id segment, never authorizes), `_resolve_go_implementation_eligibility`
(dispatch id → durable registry role set intersected with
`PRIME_ELIGIBLE_ROLES`; non-dispatch id → owner-declared interactive Prime
marker; no token fallback (F2); no fail-open (F3)), and the `acquire()` gate that
raises `WorkIntentRegistryError` for an ineligible `go_implementation` mint while
leaving draft / same-session / prime / registry-acting-prime acquisitions
unaffected. The 8 `test_work_intent_role_eligibility.py` oracles remain green.

### Part 2 — Timebox-regression repair (this session's scope-expansion work)

`platform_tests/scripts/test_go_impl_claim_timebox.py` was updated per
`DELIB-20263205` so each test that acquires a *held* `go_implementation` claim
presents positive Prime evidence, without weakening the guard:

- Added a `_write_prime_marker(root)` helper that writes the owner-declared
  interactive Prime marker (`.claude/session/active-session-role.json`,
  `role == "prime-builder"`) into the test `project_root`. The marker is read
  with no env-override path, so it is the hermetic eligibility source for a
  non-dispatch session id (mirrors the F3/b accepted case in the sibling
  role-eligibility module).
- The five direct-registry timebox tests
  (`test_go_claim_records_deadline_and_non_go_keeps_draft_ttl`,
  `test_extend_adds_fixed_increment_and_refuses_past_total_hold_cap`,
  `test_lapsed_go_claim_releases_for_takeover_after_grace`,
  `test_report_latest_status_stops_lapsed_go_claim_detection`,
  `test_doctor_warns_on_lapsed_go_implementation_claim`) now call
  `_write_prime_marker(tmp_path)` before acquiring. The original `session-a` /
  `session-b` identities are preserved (critical for the takeover test, which
  asserts on the distinct holder session id); the marker is role-only.
- The CLI test `test_cli_claim_extend_status_reports_go_implementation_fields`
  was made **hermetic**: it now writes the Prime marker into `tmp_path` and
  passes an explicit non-dispatch `--session-id` (arg-first resolution, immune to
  ambient harness session env vars). The prior form copied `os.environ` and
  injected `CODEX_THREAD_ID`, which let the subprocess inherit the running
  harness's session/registry env and resolve eligibility non-deterministically
  across Prime vs. LO verification environments. The now-unused `import os` was
  removed.

The timebox deadline / extension / grace / lapse / doctor-warning behavior each
test was written to cover is unchanged; only the eligibility precondition was
satisfied.

## Specification Links

(Carried forward from `-007`; LinkAGE specs cited under the canonical heading.)

- **GOV-SESSION-ROLE-AUTHORITY-001** — durable-role authority governs the
  `go_implementation` mint; eligibility resolves from the canonical registry /
  owner marker, never a session-id token.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the guard and test repair add no
  `bridge/INDEX.md` write surface.
- **DCL-SESSION-ROLE-RESOLUTION-001** — deterministic role resolution via the
  stdlib-only `scripts/harness_projection_reader.py` and the interactive marker.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — links carried
  forward into this report.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every named test has a
  real oracle; the previously-regressed timebox suite is repaired green with no
  weakening of the guard's negative cases.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-ROLE-AUTHORITY-001 and WI-4534
govern the guard; DELIB-20263205 authorizes the bounded scope expansion to repair
the timebox regression. No new or revised requirement is needed.

## Spec-to-Test Mapping

| Specification / criterion | Test(s) | Oracle | Result |
|---|---|---|---|
| GOV-SESSION-ROLE-AUTHORITY-001 — LO dispatch harness cannot hold go_implementation | `test_go_impl_rejected_for_lo_dispatch_harness` | `acquire()` raises; no persisted claim | PASS |
| GOV-SESSION-ROLE-AUTHORITY-001 — prime dispatch harness may hold go_implementation | `test_go_impl_allowed_for_prime_dispatch_harness` | `acquire()` True; `claim_kind == go_implementation` | PASS |
| F2 — unknown parsed harness id not authorized even with prime token | `test_go_impl_rejected_for_unknown_harness_id` | `acquire()` raises (harness id absent) | PASS |
| F2/d — registry authoritative over token | `test_go_impl_resolves_from_registry_not_token` | `acquire()` raises (registry says LO) | PASS |
| F3 — raw-UUID session, no/non-Prime marker rejected (no fail-open) | `test_go_impl_rejected_for_uuid_session_without_prime_marker` | `acquire()` raises | PASS |
| F3/b — owner-declared interactive Prime session accepted | `test_go_impl_allowed_for_uuid_session_with_prime_marker` | `acquire()` True | PASS |
| Guard scoped to go_implementation — LO may draft on NEW-latest | `test_draft_claim_unaffected_for_lo_harness_on_non_go_thread` | `acquire()` True; `claim_kind == draft` | PASS |
| Compat — registry acting-prime-builder is Prime-eligible | `test_go_impl_allowed_for_registry_acting_prime_builder` | `acquire()` True | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING — go deadline + non-go draft TTL (no regression) | `test_go_claim_records_deadline_and_non_go_keeps_draft_ttl` | deadline/grace/ttl fields | PASS |
| …extension increment + total-hold cap | `test_extend_adds_fixed_increment_and_refuses_past_total_hold_cap` | deadline progression + cap raise | PASS |
| …lapse-and-takeover after grace | `test_lapsed_go_claim_releases_for_takeover_after_grace` | takeover holder `session-b` | PASS |
| …report-latest-status stops lapsed detection | `test_report_latest_status_stops_lapsed_go_claim_detection` | empty lapsed list on NEW-latest | PASS |
| …CLI claim/extend/status report go_implementation fields (hermetic) | `test_cli_claim_extend_status_reports_go_implementation_fields` | subprocess returncodes + JSON fields | PASS |
| …doctor warns on lapsed go_implementation claim | `test_doctor_warns_on_lapsed_go_implementation_claim` | doctor check `warning` + slug in message | PASS |

## Verification Performed

The GO's required post-implementation verification, run verbatim:

```powershell
python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short
```

Result: **16 passed** (`test_work_intent_role_eligibility.py`: 8 passed;
`test_go_impl_claim_timebox.py`: 8 passed). Pre-implementation baseline in this
session was 11 passed / 5 failed (the 5 direct-registry timebox tests failed on
the new guard).

```powershell
python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
```

Result: **All checks passed!**

```powershell
python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py
```

Result: **3 files already formatted.**

### Strict-F3 preservation evidence (GO requirement)

The six repaired timebox tests now use Prime-eligible session evidence, while the
strict negative cases still **reject** when role evidence is absent:

```powershell
python -m pytest "platform_tests/scripts/test_work_intent_role_eligibility.py::test_go_impl_rejected_for_uuid_session_without_prime_marker" "platform_tests/scripts/test_work_intent_role_eligibility.py::test_go_impl_rejected_for_lo_dispatch_harness" "platform_tests/scripts/test_work_intent_role_eligibility.py::test_go_impl_rejected_for_unknown_harness_id" -q
```

Result: **3 passed** — F3 (no fail-open), F2/d (registry over token), and F2
(unknown harness) negative cases intact; the guard was not weakened.

### Hermeticity evidence (CLI test)

```powershell
GTKB_INHERITED_SESSION_ID="...-loyal-opposition-D-..." GTKB_BRIDGE_POLLER_RUN_ID="...-loyal-opposition-D-..." python -m pytest "platform_tests/scripts/test_go_impl_claim_timebox.py::test_cli_claim_extend_status_reports_go_implementation_fields" -q
```

Result: **1 passed** under a deliberately leaked LO-dispatch env. The prior
env-coupled form would have resolved the subprocess session to the leaked LO
dispatch id and failed; the repaired test passes regardless of ambient env,
which is required for stable verification in the LO (Codex) environment.

## Finding Disposition (GO prior-NO-GO findings)

- **F1 (resolved):** the timebox test file is in `target_paths` and is repaired.
- **F2 (resolved):** `DELIB-20263205` authorizes the scope expansion; cited here.
- **F3 (resolved):** the guard is preserved strict; repair adds positive Prime
  evidence rather than loosening the guard, with the negative-case evidence above.

## Files Changed

- `platform_tests/scripts/test_go_impl_claim_timebox.py` — added
  `_write_prime_marker` helper; added the marker call to the 5 direct-registry
  timebox tests; made the CLI test hermetic (marker + explicit `--session-id`);
  removed the now-unused `import os`.
- `scripts/bridge_work_intent_registry.py` — the GO'd `-003` guard (on disk from
  the guard implementation; unchanged in this session; verified green).
- `platform_tests/scripts/test_work_intent_role_eligibility.py` — the GO'd guard
  test module (on disk; unchanged in this session; 8 green).

No edits were made outside the three approved `target_paths`. No GO-event
dispatch routing, cutover, or canonical bridge-state-writer changes were made
(forbidden-scope exclusions preserved). No commit was made by this dispatched
worker; the changes are left in the working tree for owner/sweep commit.

## Owner Decisions / Input

- **DELIB-20263200** (owner AUQ): WI-4534 Slice A authorization + the bounded
  PAUTH (`source` + `test_addition`; forbids dispatch-routing / cutover).
- **DELIB-20263205** (owner AUQ, Option A): authorized expanding scope to edit
  `platform_tests/scripts/test_go_impl_claim_timebox.py` and update its failing
  timebox/CLI tests to Prime-eligible session evidence; preserve the strict F3
  contract; Option B (relax F3) rejected.

No new owner decision is required by this report.

## Recommended Commit Type

`fix:` — repairs a defect (registry-authoritative role-eligibility guard) and the
spec-derived regression it surfaced in the timebox suite, including a
non-deterministic (env-coupled) CLI test made hermetic. No new user-facing
capability surface.

## Prior Deliberations

- **DELIB-20263200** — WI-4534 Slice A authorization + bounded PAUTH.
- **DELIB-20263205** — scope-expansion authorization for the timebox-test repair.
- **DELIB-20263195** — TAFE cutover authorization (the work this defect blocked).
- `bridge/gtkb-wi4534-claim-role-eligibility-guard-006.md` — the verification
  NO-GO that the GO'd `-007` revision addressed.
- Superseded duplicate `gtkb-wi-4534-claim-role-eligibility-guard-slice-a`
  (WITHDRAWN) — token-only design improved upon here with
  registry-authoritative resolution.

## Risk / Rollback

- **Risk: low.** The guard is additive and already verified; the timebox repair
  is test maintenance that adds positive Prime evidence and makes one
  previously non-deterministic test hermetic. No production behavior beyond the
  guard changes.
- **Rollback:** revert the timebox-test session-evidence updates (and, if the
  guard itself is rolled back, the guard helpers in
  `bridge_work_intent_registry.py` and the new test module); no migration, no
  state change.
