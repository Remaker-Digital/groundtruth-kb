NEW
::init gtkb lo
::open build

# WI-6216 Slice 1 — Close the High-Recurrence Gate Defects

bridge_kind: prime_proposal
Document: gtkb-wi6216-tool-and-gate-defect-corpus-slice-1
Version: 001
Author: Prime Builder (harness B)
Date: 2026-08-14 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 2da3617e-95da-4957-bd9e-c277c7c6d051
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword

Work Item: WI-6216
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814

target_paths: [".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/destructive-gate.py", "scripts/implementation_authorization.py", ".harness-baseline-configuration/hooks/bridge-compliance-gate.py", ".harness-baseline-configuration/hooks/destructive-gate.py", ".goose/hooks/bridge-compliance-gate.py", ".goose/hooks/destructive-gate.py", ".goose/.projection-manifest.json", "platform_tests/scripts/test_bridge_compliance_gate_pending_banner.py", "platform_tests/scripts/test_destructive_gate_target_resolution.py", "platform_tests/scripts/test_report_no_go_resume_tolerance.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation; it repairs three gate scripts,
projects the repaired hooks, and adds three regression-test modules.

---

## Summary

WI-6216 carries the tool/gate defect corpus (13 items in
`DELIB-20260813-TOOL-AND-GATE-FLAWS`, extended by this session's live
reproductions). Slice 1 closes the three highest-recurrence, highest-misdirection
defects — chosen because each fired repeatedly against governed work this
session and each has a fully diagnosed mechanism with file:line evidence:

- **D1 — wrong-thread pending banner** (six live instances):
  `bridge-compliance-gate.py` `_pending_proposal_ask_reason` (lines
  1892–1918) matches an edited file against every thread whose latest status
  is NEW/REVISED/NO-GO and returns the FIRST match — no recency ordering, no
  live-packet awareness, suffix-based path matching. A months-old parked
  NO-GO thread claims files a live GO'd packet authorizes, and the banner
  instructs the implementer to review the wrong thread's findings.
- **D2 — destructive-gate target misresolution** (three false-positive
  modes): a single-file `Remove-Item .git/index.lock` was blocked as
  "Remove-Item on system path 'E:\\GT-KB'"; a multi-path Remove-Item was
  rejected the same way (inventory item 8); and a `git commit` whose
  MESSAGE contained deletion verbs was blocked outright — command PROSE is
  reaching the target resolver.
- **D3 — report-NO-GO resume strict-parse** (WI-6237): the draft-claim
  resumption authority in `implementation_authorization.py`
  (`_report_no_go_resumption_authority`) rejects a verdict whose
  `Responds to:` line carries a trailing annotation, stranding the designed
  recovery path; empirically proven the sole blocker on a live thread while
  the writer-side parser accepted the same line.

Remaining corpus items (window-spawn hygiene, duplicate hook registrations,
PowerShell gate gap, read-only git verbs, packet self-invalidation, claim
TTL semantics, backlog CLI ergonomics, ls-files sweep cost, and the
role-flip WI-6263 / envelope-CLI WI-6264 family) are explicitly deferred to
later slices — several interact with surfaces other live threads are
changing.

## Scope

1. **D1 repair** in `_pending_proposal_ask_reason`: (a) suppress the banner
   when a live implementation-start packet authorizes the edited path for a
   GO'd thread; (b) among matching threads prefer the most recently active
   (newest bridge-file mtime in chain); (c) replace the suffix match with
   root-anchored exact or glob matching; (d) long-parked NO-GO threads (no
   version appended in 30 days) do not claim paths.
2. **D2 repair** in `destructive-gate.py`: resolve targets only from parsed
   command ARGUMENTS (never message/prose flag values like `-m` bodies);
   report the actual offending path in the block message; never resolve a
   bare relative single-file target to the repo root.
3. **D3 repair** in `_report_no_go_resumption_authority`: tolerate a
   trailing parenthetical annotation after the report path (match prefix,
   strip annotation), keeping every other check intact.
4. Projection parity: the two repaired hook scripts re-projected to the
   cutover harness surface (baseline copies + `.goose` render + ownership
   manifest).
5. Three regression-test modules (exact paths in `target_paths`), red-first
   against the current defects where reproducible in-fixture.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — D1/D3 repair the bridge protocol's
  own guidance and recovery surfaces.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — D3's stranded path is the lawful
  post-NO-GO revision route the resume authority exists to serve.
- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — obligation 2: hook repairs land in
  the baseline and project mechanically; the live `.claude` copy and the
  baseline copy change in lockstep in this slice (the `.claude` projector
  cutover is Phase D).
- `SPEC-1662` (GOV-18) — the new assertions are behavioral, not structural.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 — protocol gates
  governing this document.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every defect mechanism above was
  established by direct source read and live reproduction, cited by
  file:line.

## Requirement Sufficiency

Existing requirements sufficient: each repair restores behavior the cited
specifications already require (correct thread guidance, argument-scoped
destructive gating, functioning post-NO-GO recovery). No new requirement
surface is created.

## Spec-Derived Verification Plan

| Defect | Test | Expected |
|---|---|---|
| D1 | `test_bridge_compliance_gate_pending_banner.py` | a fixture path claimed by an old parked NO-GO thread AND authorized by a live packet produces NO banner; without the packet, the banner names the most recently active matching thread; suffix collisions do not match |
| D2 | `test_destructive_gate_target_resolution.py` | single-file lock removal inside `.git/` passes; commit messages containing deletion verbs do not trigger; a genuine repo-root removal still blocks with the actual path named |
| D3 | `test_report_no_go_resume_tolerance.py` | an annotated `Responds to:` line yields a valid resumption authority identical to the unannotated form; proposal-level NO-GO still refuses resume |
| Regression floor | full `test_implementation_authorization.py` module + affected hook test modules | green; counts stated in the report |

## Owner Decisions / Input

- Owner standing directive (2026-08-13/14): capture and fix tool defects;
  WI-6216 is the owner-created carrier for exactly this corpus.
- Owner goal directive (session goal): complete Phase 2 implemented, tested,
  committed — WI-6216 is one of the eight ordered items.
- No new owner decision is required for Slice 1; deferred-item sequencing
  returns to the owner with the Slice 2 proposal.

## Prior Deliberations

- `DELIB-20260813-TOOL-AND-GATE-FLAWS` — the 13-item inventory (items 3, 6,
  7, 8 inform D2's argument-scoping; this slice's D1/D3 extend the corpus
  with this session's diagnoses).
- `DELIB-20260814-PB-TOOL-TEST-FINDINGS-ADVISORY-BLOCKED` — carries D1's
  full mechanism and recommended remedy as finding 2.
- `WI-6237` / `TEST-11901` — D3's dedicated work item and its acceptance
  test contract.
- `bridge/gtkb-operation-taxonomy-baseline-path-rules-005.md` — the live
  NO-ACTION whose necessity D3's repair removes for future threads.

## Cross-Harness Disposition

- **Claude Code (.claude/hooks/)**: repaired in place this slice (live
  enforcement surface); behavioral parity with the baseline copy is
  byte-lockstep by construction (same edit applied to both, verified by
  diff in the implementation report).
- **Goose (.goose/hooks/)**: behavioral parity via mechanical re-projection
  from the repaired baseline (engine `--check` 0-drift evidence in the
  report).
- **Codex (.codex/gtkb-hooks/), Cursor, Antigravity, API harnesses**: these
  surfaces do not carry the three affected gate scripts today (the
  bridge-compliance gate's pending-banner and the destructive-gate
  PowerShell parser are Claude-side registrations; the resume authority is
  a shared project script, not a per-harness copy). No behavioral change
  reaches them this slice; full parity arrives with their Phase D projector
  cutovers under `GOV-HARNESS-NEUTRAL-BASELINE-001` obligation 2. Typed
  disposition: `deferred-to-projector-cutover`, no waiver required because
  no divergent behavior is introduced on those surfaces.

## Risk / Rollback

All three repairs narrow false-positive behavior; none loosens a true
block: D1 still banners genuinely-unauthorized edits, D2 still blocks real
root-scoped removals, D3 still refuses proposal-level NO-GO resumes.
Rollback is reverting the three scripts and re-projecting; the tests pin
the repaired behavior either way.

## Recommended Commit Type

`fix` — repairs to broken gate behavior with regression tests; no new
capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
