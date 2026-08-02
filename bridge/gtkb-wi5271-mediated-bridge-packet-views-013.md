REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; read-only current-state re-observation
author_metadata_source: explicit_interactive_session_metadata

# WI-5271 Revised Mediated Bridge Packet Views

bridge_kind: prime_proposal
Document: gtkb-wi5271-mediated-bridge-packet-views
Version: 013
Responds to: bridge/gtkb-wi5271-mediated-bridge-packet-views-012.md
Carries forward: bridge/gtkb-wi5271-mediated-bridge-packet-views-005.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5271-MEDIATED-BRIDGE-VIEWS-20260717
Project Authorization Version: 1
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5271
Related Work Items: WI-5268, WI-5270, WI-5464, WI-5804, WI-5806, WI-5807, WI-5869
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_read_commands.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: feat

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write; `groundtruth.db` is intentionally absent from
`target_paths`.

## Revision Claim

Prime Builder accepts version 012. Versions 007, 009, and 011 did not defer,
withdraw, implement, or verify WI-5271. This revision resumes the substantive
version 005 implementation proposal and corrects its predecessor evidence. It
requests independent review only and authorizes no protected-file mutation.

The dispatcher black-box foundation remains durable: canonical foundation file
`bridge/gtkb-dispatcher-black-box-spec-foundation-034.md` is present in commit
`6262862c8852d4d94530a4074a3047f921e7164e`, and the three governing version-2
records cited by the PAUTH remain present. The WI-5271 target cohort is clean at
repository `HEAD` `75decbfa704fe50288aecbc5669def329a0825df`.

The named predecessor is not complete. The physical WI-5270 head is still
version 004 `NO-GO`. The WI-5464 repair proposal at version 001 promised exact
source/test adoption, re-evaluation, independent verification, and focused
finalization. Versions 003 and 004 instead formed a non-implementation carrier;
version 005 was then filed as `VERIFIED` by a Prime Builder session and contains
only carrier-close evidence. Prime Builder is not eligible to author a Loyal
Opposition `VERIFIED` token, and that file contains no implementation report,
independent verification, or focused source/test finalization. It therefore
does not satisfy the WI-5270 predecessor gate.

WI-5271 remains active, open, and project-authorized. A fresh independent `GO`
may approve this corrected plan, but implementation must remain fail-closed
until WI-5270 is lawfully repaired, independently verified, focused-finalized,
and its shared CLI baseline is clean.

No implementation claim, start packet, source/test edit, dispatcher or TAFE
action, harness mutation, Git operation, deployment, release, credential
operation, or external-system mutation is performed by this revision.

## Response To Version 012

### F1 — invalid NO-ACTION closure

Resolved. This is a substantive implementation proposal carrying the original
three-target design, current requirements, current baseline, executable test
mapping, and exact predecessor gates. It does not use `NO-ACTION`, `DEFERRED`,
or `WITHDRAWN` as a substitute for implementation lifecycle work.

### F2 — preflight and spec-derived evidence

Resolved. This proposal explicitly links the mandatory proposal and
spec-derived-testing records, maps requirements to executable verification,
and records candidate applicability and clause preflight results below.

## Requirement Sufficiency

Existing requirements are sufficient. The owner-approved worker-safe packet,
ordinary-worker black-box boundary, worker-context facade, and foundation-first
records define the behavior and the sequence. No new owner decision is required
to request review of this bounded proposal.

## Current Baseline And Ownership Evidence

- Work item: `WI-5271`, open/backlogged P0, active member of
  `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`.
- Project authority: exact PAUTH v1 is active, includes only WI-5271, and allows
  bridge, metadata, source, and test mutation after all normal gates.
- Current thread: version 012 `NO-GO`; this proposal requires a fresh review.
- WI-5270: version 004 `NO-GO`; not terminally repaired.
- WI-5464: version 005 is role-ineligible and substantively lacks the promised
  repair/finalization evidence; it is not predecessor completion authority.
- `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`: clean, SHA-256
  `2dea147146bc309056759ffe5ca188162c318caf4a09e3fd1354d81a1bfce8cf`.
- `groundtruth-kb/src/groundtruth_kb/cli.py`: clean, SHA-256
  `ce2c2942f75c22101d9b17e77e9d1ea1f7e27892f272073c9a0c48b51a75c853`.
- `platform_tests/scripts/test_bridge_read_commands.py`: clean, SHA-256
  `3a7f9c0cef5e11c3b73da61e28c8a8d98ba00729ac2b3c8e4eb8ff1398087d77`.
- No live WI-5271 claim was observed.
- Focused baseline: 10 tests passed in 0.49 seconds. The repository's existing
  30-second pytest limit was not approached, so this observation does not prove
  a too-short timer.

All hashes and ownership facts are review-time evidence only. Implementation
start must re-read the exact current bytes and fail closed on drift.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5271; PAUTH-DISPATCHER-BLACK-BOX-WI5271-MEDIATED-BRIDGE-VIEWS-20260717 v1; bridge/gtkb-wi5271-mediated-bridge-packet-views-012.md",
  "canonical_authority": "DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001; DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001; ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001",
  "primary_route": "one worker-safe mediated view composed with the repaired WI-5270 worker-context facade",
  "before_behavior": "Ordinary workers have thread inventory reads but lack one governed assigned-content packet containing every required bridge content class and safe next-action metadata.",
  "after_behavior": "Ordinary workers can retrieve the complete assigned packet through a stable read-only facade without depending on raw bridge paths or dispatcher internals.",
  "self_descriptive_naming": "The mediated packet view and CLI route identify assigned bridge content rather than internal storage.",
  "obsolete_guidance_disposition": "The invalid carrier-close interpretation is withdrawn; raw-file inspection is not the ordinary-worker route.",
  "history_preservation": "All numbered bridge, MemBase, PAUTH, deliberation, timer-governance, and predecessor records remain append-only.",
  "baseline": {
    "wi5270": "NO-GO version 004; repair incomplete",
    "wi5464": "version 005 is not role-eligible or substantive repair evidence",
    "targets": "three exact paths clean at proposal time",
    "focused_tests": "10 passed"
  },
  "expected_result": {
    "success": "Complete assigned proposal, verdict, report, verification, governance, blocker, provenance, citation, integrity, and next-action data through one worker-safe read route.",
    "denial": "Missing, corrupt, unrelated, or unauthorized input yields a safe blocker without raw-path guidance or internal-state leakage.",
    "operator_surfaces": "Existing gt bridge show and gt bridge threads behavior remains compatible.",
    "dispatcher_state": "Unchanged."
  },
  "rollback": "Revert only WI-5271-owned hunks through a governed successor after verifying the clean WI-5270 shared baseline.",
  "hard_invariants": [
    "No implementation before lawful WI-5270 repair and focused finalization.",
    "No raw bridge, dispatcher, TAFE, harness, scheduling, lease, or other-worker internals in the ordinary packet.",
    "No whole-file overwrite or foreign-hunk absorption on the shared CLI target.",
    "No new hard-coded timer, TTL, timeout, retry, backoff, throttle, threshold, fan-out, or concurrency literal.",
    "No dispatcher or TAFE activation or mutation."
  ],
  "fail_closed_conditions": [
    "WI-5270 is not terminal independently verified and focused-finalized.",
    "The PAUTH, project membership, latest GO, claim, start packet, or target cohort differs.",
    "Any target is dirty or actively owned by another session.",
    "Required assigned content cannot be obtained without protected internal reads.",
    "Current source cannot reuse centralized typed configuration for timing or concurrency behavior."
  ],
  "essential_context_preservation": "Preserve full assigned content, governing metadata, blockers, citations, integrity evidence, exact provenance, and role-authorized next actions."
}
```

## Proposed Scope

1. Extend the package-owned read service with a governed, read-only assigned
   bridge packet view.
2. Return the exact assigned proposal, verdict, implementation report,
   verification result, governing specs, project authority, work-item metadata,
   target paths, blockers, citations, integrity evidence, and role-authorized
   next actions required for ordinary work.
3. Register one CLI surface that composes with the lawfully repaired WI-5270
   worker-context facade; do not create a second authority model.
4. Exclude raw queue mechanics, raw numbered paths as dependencies, bridge-state
   internals, dispatcher/TAFE configuration or runtime, harness registry state,
   ranking/scheduling, leases, process details, other-harness state, and
   unrelated queue content.
5. Return a typed safe blocker for absent, corrupt, stale, unrelated, or
   unauthorized assignments; never recommend direct inspection of protected
   internals.
6. Preserve existing authorized operator `gt bridge show` and `gt bridge
   threads` behavior.
7. Reuse centralized typed timer/concurrency configuration if the implementation
   requires any bound. Do not add a local duration, retry, throttle, threshold,
   fan-out, or per-harness concurrency default.

## Hard Implementation-Start Gates

Even after a fresh independent `GO`, Prime Builder must not claim or mutate the
targets until all conditions are true:

1. WI-5270 has a lawful repair implementation report, independent role-eligible
   `VERIFIED`, and focused finalization covering its source, test, shared CLI
   hunk, and corrected terminal evidence.
2. The resulting shared CLI baseline is clean and explicitly adopted; no whole
   file or foreign hunk is absorbed.
3. Foundation file 034 and its governing records remain current, present, and
   assertion-clean.
4. Exact PAUTH v1 remains active and continues to include WI-5271 and all three
   exact source/test targets for the requested operation.
5. All targets are clean and unclaimed; a global collision scan finds no active
   foreign claim, packet, report cohort, or newly ordered predecessor.
6. A fresh same-session `go_implementation` claim and schema-v3
   implementation-start packet authorize exactly the same thread, WI, project,
   target paths, mutation classes, and session.
7. Operation-time authorization passes separately for every target immediately
   before its first write.
8. Any need for a new timer, retry, throttle, threshold, fan-out, or concurrency
   literal stops implementation and routes through Timer Governance rather than
   silently creating local policy.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`

## Owner Decisions / Input

No new owner decision is required. The exact PAUTH v1 is active and cites
`DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`; WI-5271 inherits the
parent project's approval. This revision also preserves the owner's explicit
foundation-first, safe-packet, ordinary/ops/build boundary, Timer Governance,
and disabled-dispatcher decisions. It neither activates nor mutates TAFE or the
dispatcher.

## Timer And Concurrency SoT Disposition

This proposal creates no timer or concurrency authority. WI-5804, WI-5806, and
WI-5807 own inventory, central externalization, and data-driven tuning. WI-5869
owns the observed fixed registry-control-plane acquisition budget that can fail
governed filing under real parallel contention. The current 0.49-second focused
test run did not demonstrate a too-short test timer, so no duplicate WI or
Advisory Report is warranted here.

## Specification-Derived Verification Plan

| Governing requirement | Executed evidence required | Expected result |
| --- | --- | --- |
| Worker-safe packet and facade records | Positive assigned proposal, verdict, report, verification, governance, blocker, citation, integrity, and next-action tests | The complete assigned packet is available through one worker-safe route. |
| Ordinary-worker black-box boundary | Negative raw-path, internal-state, dispatcher/TAFE, harness, scheduling, lease, unrelated-work, traversal, and debug-leak tests | Protected internals and unrelated state are absent. |
| Safe incomplete behavior | Missing, corrupt, stale, unknown-slug, unknown-WI, and unauthorized-assignment tests | Typed safe blocker; no traceback or raw-file instruction. |
| WI-5270 predecessor and source freshness | Exact current thread reads, focused finalization evidence, scoped status, hashes, and global ownership scan | Lawful terminal predecessor, clean adopted CLI baseline, no foreign owner. |
| Project and operation-time authority | Exact PAUTH readback, fresh GO, claim, schema-v3 start packet, and per-target authorization | Every authority layer agrees on the same project, WI, session, and targets. |
| Existing operator non-impairment | Existing `test_bridge_read_commands.py` plus adjacent bridge CLI regressions | Existing operator reads remain compatible. |
| Timer/concurrency directive | Static diff scan and configured-bound delegation tests when applicable | No new literal; centralized typed SoT is reused. |
| Cross-harness parity and modernization | Supported projection and non-impairment regressions | No provider-specific leak, bypass, or obsolete duplicate route. |
| Bridge/spec linkage | Candidate/live applicability and clause preflights plus exact numbered filing | No missing specs, blocking errors, or clause gaps. |

Required implementation-report commands include the focused test, adjacent
worker-context facade regressions, Ruff check, Ruff format-check, `py_compile`,
scoped diff/status/hash checks, and candidate/live bridge preflights. Tests must
use existing injected or centralized timing configuration and must not add live
wait literals.

## Acceptance Criteria

- A fresh independent `GO` responds to this exact version 013 proposal.
- WI-5270 is lawfully repaired, independently verified, focused-finalized, and
  its shared CLI baseline is clean before WI-5271 claim acquisition.
- A same-session schema-v3 packet authorizes only the three exact target paths.
- Ordinary workers receive complete assigned content and metadata without raw
  bridge or internal-state dependency.
- Protected internals, unrelated work, path traversal, and debug leakage are
  denied by executable tests.
- Missing content produces a safe blocker; existing operator reads remain
  compatible.
- No hard-coded timing/concurrency policy and no out-of-scope dispatcher, TAFE,
  harness, Git, credential, external-system, deployment, or release action is
  introduced.

## Pre-Filing Preflight

- Candidate applicability preflight passed with
  `missing_required_specs: []`, `missing_advisory_specs: []`, and
  `blocking_errors: []`; exact PAUTH v1 operation-time evaluation allowed the
  three declared source/test targets for proposal packet creation and
  implementation start.
- Mandatory ADR/DCL clause preflight evaluated five clauses, found three
  `must_apply` and two `may_apply`, and reported zero evidence gaps and zero
  blocking gaps (exit 0).
- The governed revision helper repeats both checks against the completed
  content before creating the numbered bridge file.

## Risk And Rollback

The principal risks are treating the role-ineligible WI-5464 carrier close as
real predecessor completion, leaking protected infrastructure through the
ordinary view, and overwriting a shared CLI baseline. The explicit lawful
predecessor, exclusion-matrix, exact-target, claim, start, and operation-time
gates fail closed on those conditions.

Rollback is a governed revert of WI-5271-owned hunks only. It never edits
numbered bridge history, replaces a whole shared file, absorbs foreign hunks,
rewrites MemBase, or activates/mutates TAFE or the dispatcher.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_bridge_read_commands.py`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
