REVISED

# WI-4534 MemBase Closure Reconciliation Proposal - Revised Scope

bridge_kind: prime_proposal
Document: gtkb-wi4534-membase-closure-reconciliation
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-21 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-21T23-43-44Z-prime-builder-A-ffd46a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: bridge auto-dispatch prime-builder worker

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4534

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_go_impl_claim_timebox.py", "groundtruth.db", "bridge/gtkb-wi4534-membase-closure-reconciliation-*.md"]

implementation_scope: focused_evidence_repair_then_membase_closure_reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Claim

This `REVISED` proposal addresses the `NO-GO` at
`bridge/gtkb-wi4534-membase-closure-reconciliation-002.md` by changing the
work from a closure-only MemBase mutation into a two-phase reconciliation:

1. Restore reproducible current focused evidence for the verified WI-4534
   role-eligibility guard by repairing the GO-latest test fixture/status-reader
   drift.
2. Only after that focused evidence is green, update the `WI-4534` MemBase row
   to closed/resolved with durable evidence linking the original verified
   implementation thread and this reconciliation thread.

No source, test, or MemBase mutation is authorized until Loyal Opposition
reviews this revision and records `GO`.

## Findings Addressed

### F1 - P1 - Current focused tests fail, so closure evidence is not reproducible

Response: Accepted. The closure-only proposal depended on current focused
pytest evidence that was red at review time. Prime Builder reproduced the same
failure shape during this auto-dispatch session:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_go_impl_claim_timebox.py -q --tb=short -o addopts= --basetemp .gtkb-state\pytest-wi4534-pb-revised-precheck
```

Observed result: `12 failed, 4 passed`. Representative failures still show
GO-latest fixtures being treated as non-GO: expected `go_implementation`
claims are persisted as `draft`, non-Prime rejection tests do not raise, and
the lapsed-GO doctor check reports `pass` instead of `warning`.

This revision therefore requires the implementation phase to repair the
focused test fixture/status-reader drift before any MemBase closure update is
attempted.

### F2 - P1 - The proposed target scope cannot repair the blocker

Response: Accepted. The `-001` target scope included only `groundtruth.db` and
this bridge thread, which could not repair failures in
`platform_tests/scripts/test_work_intent_role_eligibility.py`,
`platform_tests/scripts/test_go_impl_claim_timebox.py`, or the production
status-reader surface in `scripts/bridge_work_intent_registry.py`.

This revision expands `target_paths` to include those source/test surfaces plus
the eventual MemBase closure target. The implementation sequence is strict:
source/test repair first, focused verification second, MemBase closure last.

## Scope Changes

Changed from closure-only reconciliation to evidence-repair-first
reconciliation.

In scope:

- Repair the focused WI-4534 regression fixtures so GO-latest test setup is
  represented by status-bearing numbered bridge files, or otherwise align the
  tests with the current production `_latest_status` contract.
- Make the minimal production status-reader adjustment only if the tests reveal
  a genuine source defect rather than fixture drift.
- Run the focused WI-4534 pytest command and both Python code-quality gates
  before any implementation report.
- Update only `WI-4534` in MemBase after the focused tests pass, recording
  completion evidence that cites:
  - `bridge/gtkb-wi4534-claim-role-eligibility-guard-010.md`;
  - this reconciliation bridge thread;
  - the green focused pytest result.

Out of scope:

- GO-event dispatch routing changes.
- Canonical bridge-state writer/cutover changes.
- Dispatcher target-selection changes.
- Broad backlog reconciliation beyond `WI-4534`.
- Any Agent Red or adopter-application file mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - all implementation and closure work flows
  through this numbered bridge thread, a Loyal Opposition verdict, an
  implementation report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  carries concrete project linkage, target paths, findings disposition, and
  spec-derived verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision includes
  the required project authorization, project, and work-item header lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - closure cannot be
  verified until linked specifications are mapped to executed tests.
- `GOV-STANDING-BACKLOG-001` - the MemBase backlog row is the authoritative
  work-item lifecycle surface and must reflect durable closure evidence once
  reproducible evidence is restored.
- `GOV-SESSION-ROLE-AUTHORITY-001` - the focused tests prove that only
  Prime-eligible contexts can hold `go_implementation` claims.
- `DCL-SESSION-ROLE-RESOLUTION-001` - the focused tests exercise deterministic
  role/session resolution for dispatch and interactive claim eligibility.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are contained
  inside `E:\GT-KB` and no lifecycle-independent Agent Red repository is used.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation start must
  derive a live packet from the eventual `GO`; the packet must preserve this
  revision's bounded target path set and project/work-item linkage.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the reconciliation preserves the
  artifact graph between owner authorization, work item, bridge thread, tests,
  implementation report, verification, and MemBase closure.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal verified bridge evidence and
  green focused tests are the lifecycle trigger for closing the work item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the update is captured as governed
  artifact lifecycle work rather than harness memory or chat state.

## Prior Deliberations

- `DELIB-20263200` - owner AUQ authorizing WI-4534 Slice A and the bounded
  PAUTH for the claim role-eligibility guard.
- `DELIB-20263205` - owner AUQ choosing Option A: expand WI-4534 Slice A scope
  to repair the timebox regression suite while preserving strict positive
  Prime evidence.
- `bridge/gtkb-wi4534-claim-role-eligibility-guard-010.md` - terminal
  `VERIFIED` verdict for the original role-eligibility guard and timebox repair
  implementation thread.
- `bridge/gtkb-wi4534-claim-role-eligibility-guard-007.md` and `-008.md` -
  revised proposal and GO authorizing the guard plus timebox-regression scope.
- `bridge/gtkb-wi4534-membase-closure-reconciliation-002.md` - current
  `NO-GO` identifying the red focused evidence and target-scope mismatch this
  revision addresses.

Deliberation search was run before this revision:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-4534 MemBase closure reconciliation claim role eligibility guard timebox regression" --limit 8 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20263200 --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-20263205 --json
```

The search did not surface a newer owner decision superseding the WI-4534
Slice A authorization or changing the strict positive-Prime evidence contract.

## Owner Decisions / Input

No new owner decision is required for this revision. Existing owner evidence
authorizes WI-4534 Slice A source/test repair (`DELIB-20263200` and
`DELIB-20263205`). The MemBase closure phase is constrained to reflecting the
already-verified implementation outcome only after current focused evidence is
green. If Loyal Opposition determines that the final `groundtruth.db`
work-item closure requires a separate owner approval or PAUTH mutation class,
the expected review outcome is a targeted `NO-GO` on that authorization gap.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4534`,
`GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`,
`GOV-STANDING-BACKLOG-001`, `DELIB-20263200`, and `DELIB-20263205` define the
required behavior and closure condition. No new or revised requirement is
needed before implementation.

## Implementation Plan

1. Begin implementation only after Loyal Opposition records `GO` and Prime
   Builder successfully runs:

   ```text
   groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4534-membase-closure-reconciliation
   ```

2. Repair the focused fixtures and any minimal source mismatch needed for the
   current `_latest_status` contract. The expected normal repair is to update
   the focused tests to create status-bearing numbered bridge files instead of
   relying only on compatibility `bridge/INDEX.md` fixture text.
3. Run focused pytest and Python quality gates on changed source/test files.
4. If and only if focused pytest is green, update the `WI-4534` MemBase row to
   resolved/closed with completion evidence citing the original verified
   implementation thread, this reconciliation bridge, and the focused command
   result.
5. File a post-implementation report that carries forward linked specs,
   command evidence, observed results, changed paths, and rollback notes.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-wi4534-membase-closure-reconciliation --format json` shows `NEW`/`NO-GO`/`REVISED`/`GO`/report chain with no drift. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `bridge_applicability_preflight.py --bridge-id gtkb-wi4534-membase-closure-reconciliation` passes with no missing required specs. |
| `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` | `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short -o addopts=` passes, proving non-Prime `go_implementation` rejection and Prime eligibility. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps each linked spec to executed pytest, preflight, ruff, and backlog-readback evidence. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-4534 --json` after implementation returns a resolved/closed lifecycle state with completion/status evidence citing `bridge/gtkb-wi4534-claim-role-eligibility-guard-010.md` and this reconciliation bridge. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `implementation_authorization.py begin` emits a packet for this bridge whose target path globs match the revised target scope. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed paths are under `E:\GT-KB`; no external Agent Red repository or archive path is touched. |

Expected commands:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4534-membase-closure-reconciliation
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4534-claim-role-eligibility-guard --format json --preview-lines 20
groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi4534-membase-closure-reconciliation --format json --preview-lines 80
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_go_impl_claim_timebox.py -q --tb=short -o addopts=
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_go_impl_claim_timebox.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\bridge_work_intent_registry.py platform_tests\scripts\test_work_intent_role_eligibility.py platform_tests\scripts\test_go_impl_claim_timebox.py
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4534 --json
```

## Pre-Filing Preflight Subsection

Candidate preflights were run against this completed content file before live
filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4534-membase-closure-reconciliation --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4534-membase-closure-reconciliation-003.md
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4534-membase-closure-reconciliation --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi4534-membase-closure-reconciliation-003.md
```

Applicability result:

- packet_hash: `sha256:6b5c7effe23cacbd93e921b36b002dacbb7714bdf9af70fac19fa7366b57ffae`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-wi4534-membase-closure-reconciliation-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause result:

- mode: mandatory
- clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0

## Risk / Rollback

Primary risk: mixing evidence repair and MemBase closure in one revision could
hide which step failed. Mitigation: the implementation sequence is ordered and
observable; the MemBase closure must not run until the focused test command is
green.

Source/test rollback: revert only the changes to the listed source/test paths.

MemBase rollback: if Loyal Opposition later finds closure evidence
insufficient, restore only `WI-4534` to `resolution_status: open` and
`stage: backlogged`, preserving the bridge audit trail and any verified
source/test repair.

## Bridge Filing

This revision is intended as `bridge/gtkb-wi4534-membase-closure-reconciliation-003.md`.
It appends to the existing file chain and does not rewrite `-001` or `-002`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
