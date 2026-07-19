NEW
::init gtkb lo
::open build

# WI-5518: Make compact bridge scans scale with current threads

bridge_kind: prime_proposal
Document: gtkb-wi5518-compact-bridge-scan-scalability
Version: 001
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; reasoning_effort=xhigh; transcript-defined Prime Builder role

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5518-COMPACT-SCAN-SCALABILITY-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5518

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py", ".cursor/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: source | test | managed helper parity
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

The manual bridge scanner's `--compact` mode reduces serialized output but
still reads every numbered bridge version before discarding terminal and
archived payloads. WI-5518 proposes a compact-only inventory path whose work
scales with current threads plus explicitly required actionable ancestry,
while leaving full-mode archival behavior and role actionability unchanged.

## Defect / Reproduction

The canonical Prime Builder command:

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
```

remained active for more than ten minutes on the current bridge corpus and
accumulated more than 280 CPU seconds before only that interactive scan process
was stopped. WI-5518 preserves this reproduction in MemBase.

Source inspection establishes the cause:

1. `_scan_rows_from_version_files` enumerates every numbered `bridge/*.md`
   file.
2. `_status_from_bridge_file` calls `Path.read_text` for each version.
3. `scan(..., compact=True)` builds the ordinary full result first.
4. `_compact_scan_result` removes version chains and terminal/archive payloads
   only after all historical content has already been read and classified.

The three live manual-helper copies under `.claude`, `.codex`, and `.cursor`
are currently clean and byte-identical. The adopter template is also clean but
has intentional profile differences, including its terminal-work-item
classification. This proposal preserves those differences.

## In-Root Placement Evidence

Every target is inside the GT-KB root:

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`
- `.cursor/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

No live dependency, evidence source, or output is outside `E:/GT-KB`.

## Specification Links

- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` - supplies the governing bounded, read-only compact workflow contract and canonical role-actionability semantics.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires bridge and dispatch consumers to preserve canonical dispatcher/TAFE authority rather than create a competing queue or cache.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - keeps dispatcher/TAFE state plus the status-bearing numbered file chain as authority; the helper remains a read-only projection.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active PAUTH does not replace independent GO, claim, implementation-start, implementation report, or independent verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to the exact project, PAUTH, and WI-5518 carrier.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the compact-read design and tests to remain traceable to all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires TEST-11589 and the mapped focused tests to execute before VERIFIED.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires measured before/after work, full-mode preservation, rollback, hard invariants, and fail-closed verification.
- `GOV-WORK-TREE-HYGIENE-001` - requires the implementation and focused commit to preserve unrelated owner and parallel-session changes in the shared dirty worktree.
- `ADR-CROSS-HARNESS-PARITY-001` - requires behavioral parity on each applicable manual-helper surface while allowing harness-appropriate implementation differences.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires a concrete per-harness disposition because the target paths touch harness skill surfaces.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all helper and test changes remain inside the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - WI-5518 and TEST-11589 are the canonical backlog and test carriers; no duplicate work item is introduced.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the reproduced defect through MemBase, PAUTH, bridge review, tests, implementation evidence, and verdict.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the defect and its rejected broad-scan behavior reconstructable from governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps proposal, GO, implementation-start, implementation report, VERIFIED, and focused commit as distinct transitions.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers and governed proposals for newly reproduced bridge, TAFE, dispatcher, and harness defects while preserving every later gate.
- `DELIB-202666121` - independently VERIFIED the WI-5174 compact workflow report and its bounded, read-only role-queue semantics; WI-5518 preserves those semantics while correcting the manual scan's hidden full-history work.
- `DELIB-202665650` - approved deterministic CLI compactness and source-of-truth size controls, including the principle that compact routes must avoid duplicating canonical authority.

Searches for `WI-5518 compact scan scalability`, `compact bridge scan
historical versions`, and `bridge scan performance current threads` found no
prior rejection of this exact compact-inventory approach. Unrelated semantic
results were excluded.

## Owner Decisions / Input

No new owner decision is required.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner-decision
basis for active singleton authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5518-COMPACT-SCAN-SCALABILITY-20260718`.
That PAUTH permits this proposal now and permits protected implementation only
after independent Loyal Opposition GO, an exact matching claim, and
implementation-start authorization. It forbids dispatcher, TAFE, runtime,
credential, external-system, destructive-cleanup, Git-push, deployment,
release, and unrelated mutation.

The owner's current dispatcher-configuration hold remains binding. WI-5518
does not request or authorize any eligibility, routing, cap, timeout, daemon,
lease, claim-file, or runtime configuration change.

## Requirement Sufficiency

Existing requirements are sufficient. TEST-11589 defines the observable
read-bound and classification-equivalence contract. The current defect is an
implementation mismatch: compact mode claims to omit history but pays the full
historical read cost first. No new role, queue, lifecycle, archive, or
dispatcher authority is required.

## Proposed Scope

1. Add a compact-only current-thread inventory path to each approved helper.
   It must group numbered files by slug from filenames before reading file
   content and read the latest numbered file for each current thread first.
2. Read older versions only when the current thread's classification requires
   operative Prime proposal metadata, implementation-authorization
   diagnostics, acknowledged-archive classification, or another existing
   actionable result field. Terminal history that cannot affect the compact
   result must not be loaded.
3. Preserve the existing full scan as the archival-complete path. Full mode
   continues to return complete version chains, terminal payloads, excluded
   archive details, and current authorization diagnostics.
4. Preserve `index_text` and `index_path` compatibility fixtures. Synthetic
   callers must retain their current result shape and fail-open behavior where
   the existing helper intentionally does so.
5. Preserve role actionability by continuing to use the existing shared
   disposition and implementation-authorization surfaces. No new
   status-to-role matrix, queue, cache, index, dispatcher rule, or runtime
   artifact is introduced.
6. Keep `.claude`, `.codex`, and `.cursor` live helper copies byte-identical
   after the focused change. Apply equivalent compact behavior to the adopter
   template without erasing its deliberate standalone profile and
   terminal-work-item behavior.
7. Add deterministic tests to `platform_tests/scripts/test_scan_bridge.py`.
   Tests must instrument bridge-content reads on a many-version fixture and
   compare normalized compact classifications against full-mode reference
   classifications. Wall-clock thresholds are prohibited.

Out of scope:

- Dispatcher or TAFE configuration, routing, eligibility, caps, daemon state,
  leases, runtime files, and live worker control.
- MemBase or Deliberation Archive mutation during implementation.
- Changing role actionability, archive policy, GO activatability, bridge
  statuses, or proposal/verdict authority.
- New caches, aggregate indexes, queue artifacts, telemetry, cost estimation,
  provider calls, or direct harness contact.
- Cleanup, unrelated worktree changes, staging, push, deployment, release, or
  history rewrite.

## Cross-Harness Disposition

- Harness A (Codex): applicable. Update the `.codex` manual-helper copy and
  prove compact/full classification equivalence.
- Harness B (Claude Code): applicable. Update the `.claude` canonical
  manual-helper copy with behavior equivalent to A.
- Harness C (Antigravity): not applicable to a repo-local helper target. No
  Antigravity-specific `scan_bridge.py` surface exists in the current
  repository; shared dispatcher/TAFE bridge consumption remains unchanged.
- Harness D (Ollama), harness F (OpenRouter), and harness H (Alibaba):
  not applicable to these interactive manual-helper files. Provider-backed
  workers consume governed TAFE packets and do not execute this helper as
  their dispatch authority.
- Harness E (Cursor): applicable. Update the `.cursor` manual-helper copy with
  behavior equivalent to A and B.
- Adopter template: applicable as a managed projection. Preserve its distinct
  standalone implementation profile while proving equivalent compact read
  bounds and current-thread classifications.

No typed waiver is requested. Applicability is based on the currently
registered A/B/C/D/E/F/H fleet; no nonexistent harness is introduced.

## Specification-Derived Verification Plan

| Governing requirement | Executable verification | Required result |
|---|---|---|
| `TEST-11589`, `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` | Build a deterministic fixture with many versions per thread, instrument bridge-content reads, and run compact scans for Prime Builder and Loyal Opposition. | Reads are bounded by current thread count plus explicitly required actionable ancestry, not total historical version count. |
| `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` | Compare normalized compact `summary`, `actionable`, `blocked_non_activatable`, `terminal_verified_count`, and `excluded_archived_count` against the full-mode reference on the same fixture. | Current status counts and role classifications are equivalent; compact mode omits only archival payload shape. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run existing full-mode, inline `index_text`, terminal-kind GO, NO-ACTION, GO-activatability, archive, and template terminal-work-item tests. | Existing behavior remains green; full mode remains archival-complete. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Hash the three live helper copies and run equivalent compact fixtures against the adopter template. | Live A/B/E copies are byte-identical; the template has behaviorally equivalent compact semantics while retaining its documented profile differences. |
| `GOV-WORK-TREE-HYGIENE-001` | Inspect exact-target status/diff, run `git diff --check`, and verify no foreign hunk is staged or committed. | Only approved WI-5518 hunks and its numbered bridge chain enter the focused commit. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the complete focused test module, Ruff check, Ruff format check, both bridge preflights, and independent Loyal Opposition rerun. | Every mapped check passes against the exact implementation bytes before VERIFIED and focused commit. |

Required implementation and verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
git diff --check -- .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5518-compact-bridge-scan-scalability
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5518-compact-bridge-scan-scalability
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5518; TEST-11589; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5518-COMPACT-SCAN-SCALABILITY-20260718",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001; canonical status-bearing numbered bridge files plus dispatcher/TAFE state",
  "primary_route": "scan_bridge.py --compact for bounded manual role-oriented bridge inspection; full mode for archival detail",
  "before_behavior": "compact mode reads every numbered bridge version and only then removes terminal, archive, and version-chain payloads",
  "after_behavior": "compact mode inventories current threads first and reads only current files plus explicitly required actionable ancestry, while full mode and role classifications remain unchanged",
  "self_descriptive_naming": "compact inventory and ancestry-loading helpers explicitly identify current-thread and required-ancestry behavior",
  "obsolete_guidance_disposition": "the misleading output-only compact implementation is replaced in the exact approved helper surfaces; no alternate scanner, cache, or aggregate index is created",
  "history_preservation": "full scan remains archival-complete and the numbered WI-5518 bridge chain preserves proposal, implementation report, and verdict history",
  "baseline": {
    "observed_command_runtime": "more than ten minutes before the isolated scan was stopped",
    "observed_cpu_seconds": "more than 280",
    "current_algorithm": "reads every numbered bridge version before compact projection",
    "live_helper_parity": "Claude, Codex, and Cursor copies are byte-identical before implementation",
    "template_profile": "clean and intentionally distinct from the live helper copies"
  },
  "expected_result": {
    "compact_read_bound": "current thread count plus explicitly required actionable ancestry",
    "classification_result": "equivalent normalized Prime and Loyal Opposition current/actionable/blocked/terminal/archive counts",
    "full_scan_result": "archival-complete behavior preserved",
    "runtime_mutation": "zero dispatcher, TAFE, lease, daemon, worker, eligibility, routing, or cache mutation"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the focused WI-5518 helper and test hunks",
    "verification": "rerun the full focused test module, Ruff gates, exact-target diff check, and both bridge preflights"
  },
  "hard_invariants": [
    "dispatcher/TAFE state and status-bearing numbered files remain canonical authority",
    "full scan remains archival-complete",
    "Prime and Loyal Opposition actionability and GO authorization diagnostics do not change",
    "inline index_text compatibility remains supported",
    "the three live helper copies remain byte-identical",
    "the adopter template retains its intentional standalone profile",
    "no dispatcher configuration, runtime state, live worker, MemBase, credential, external system, deployment, release, push, or unrelated worktree state is mutated"
  ],
  "fail_closed_conditions": [
    "compact/full normalized classifications differ",
    "read count scales with total terminal history",
    "full mode loses any version-chain or archive detail",
    "a live helper copy drifts from the other live copies",
    "the template loses its existing profile-specific behavior",
    "any independent GO, matching claim, implementation-start, test, VERIFIED, or focused-commit gate is absent"
  ],
  "essential_context_preservation": "current status, operative proposal metadata needed for actionability, GO authorization diagnostics, archive counts, role routing, exact project linkage, full archival history on demand, and independent lifecycle evidence all remain available"
}
```

## Acceptance Criteria

1. Compact scans read one latest file per current thread plus only the older
   versions mechanically required for an actionable thread's existing
   classification or authorization diagnostics.
2. A many-version fixture proves compact bridge-content reads do not grow with
   unrelated terminal history.
3. Normalized Prime Builder and Loyal Opposition compact results match the
   full-mode reference for summary, actionable, blocked, terminal count, and
   excluded-archive count.
4. Full mode retains complete version chains, terminal payloads, excluded
   archive details, and current GO activatability diagnostics.
5. Existing inline-fixture, NO-ACTION, terminal-kind, archive, unreadable-file,
   and template terminal-work-item behavior remains green.
6. The three live helper copies remain byte-identical. The adopter template
   receives semantically equivalent compact behavior without losing its
   intentional profile-specific logic.
7. The implementation creates no cache, index, alternate queue, dispatcher or
   TAFE state, MemBase mutation, harness contact, or runtime mutation.
8. Focused pytest, Ruff check, Ruff format check, exact-target diff check,
   applicability preflight, clause preflight, independent VERIFIED, and a
   focused local commit all pass.

## Pre-Filing Preflight

Candidate-content preflights executed before live filing:

- `scripts/bridge_applicability_preflight.py --content-file`: PASS,
  `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`, packet
  `sha256:2cf970bb0c4f5a32fc9f954ddfa137b2481665bb1413812d664bd70cc188b84c`.
  The path-token collector emitted one non-blocking warning for the partial
  suffix `bridge/helpers/scan_bridge.py`; every declared target path exists
  and is listed explicitly above.
- `scripts/adr_dcl_clause_preflight.py --content-file`: PASS, four
  `must_apply` clauses, zero evidence gaps, zero blocking gaps.
- Live filing remains subject to the helper-mediated credential,
  author-provenance, project-linkage, cross-harness-disposition,
  non-impairment, and current work-intent gates.

## Risks / Rollback

The primary risk is optimizing away an older version that still supplies
operative proposal metadata or GO authorization evidence. The design therefore
allows explicit per-thread ancestry loading and compares compact
classifications against the full reference. A secondary risk is flattening the
adopter template into the live helper implementation despite its distinct
terminal-work-item contract; template behavior is tested separately and byte
identity is required only for the three live copies.

Rollback requires separate authority and reverses only the focused WI-5518
helper and test hunks. The numbered bridge chain, WI, test artifact, PAUTH, and
verdict history remain intact. No dispatcher, TAFE, runtime, MemBase, or Git
history rollback is part of this work.

## Files Expected To Change

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`
- `.cursor/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Recommended Commit Type

`perf(bridge)`: bound compact bridge scan work while preserving full archival
behavior and role classifications.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
