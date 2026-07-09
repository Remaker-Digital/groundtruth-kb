REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: codex-session
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; sandbox=danger-full-access; cwd=E:/GT-KB

# WI-4837 Post-VERIFIED Prime-Side Finalization Recovery - Automatic Parity Revision

bridge_kind: prime_proposal
Document: gtkb-wi4837-post-verified-finalization-recovery
Version: 011
Responds to: bridge/gtkb-wi4837-post-verified-finalization-recovery-010.md
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4837-BATCH-A1-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4837

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source/test/cli-gate
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision resolves the outstanding F3 owner-policy blocker by citing the recorded owner decision `DELIB-WI4837-AUTOMATIC-PARITY-20260707`.

The selected policy is automatic parity: post-`VERIFIED` Prime-side finalization may allow staging/finalization for terminal-`VERIFIED` paths when the paths are inside the approved proposal `target_paths`, matching the existing pre-commit clearance behavior. The rejected policy is per-instance waiver.

The revised implementation scope is narrower than the original waiver-packet design. Prime Builder should add a terminal-`VERIFIED` finalization clearance for the `git add`/staging gap in `scripts/implementation_start_gate.py`, backed by live bridge-chain and approved-target-path reads from `scripts/implementation_authorization.py`. The implementation must not relax ordinary implementation-start packets: `_validate_packet` must continue to fail closed for terminal `VERIFIED` threads when the command is normal source/test mutation rather than finalization staging of approved paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state and numbered files remain the authority for latest terminal `VERIFIED` status and proposal target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A1 PAUTH authorizes this bounded work item only through bridge review and implementation-start gates.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass the need for this revised proposal, Loyal Opposition `GO`, and a live implementation-start packet.
- `GOV-WORK-TREE-HYGIENE-001` - file-only or uncommitted verified work must have a governed finalization path instead of ad hoc staging or cleanup.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - the implementation must distinguish the owner-selected automatic-parity policy from one-off owner waiver provenance.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - any finalization clearance must derive from fresh bridge state, live target-path extraction, and current command targets.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries concrete governing specifications and a spec-derived test plan.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target path metadata are present near the top of the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map this proposal's linked specifications to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4837 should move through bridge review, implementation, verification, and backlog closure rather than repeated blocker records.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed source and test changes remain under `E:/GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner policy decision is recorded as durable Deliberation Archive evidence before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - recovery behavior must be encoded in deterministic gate logic and tests, not chat-only operating memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal `VERIFIED` state plus unfinalized approved paths is the lifecycle trigger for this recovery clearance.
- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` - owner selected automatic parity and rejected per-instance waiver for WI-4837 F3.
- `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702` - after the `NO-ACTION` blocker trail, a fresh `GO` on this corrected proposal is required before implementation.

## Prior Deliberations

- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` - owner selected automatic parity for WI-4837 F3 and rejected per-instance waiver.
- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - owner approved Batch A1, including WI-4837, for governed bridge processing.
- `DELIB-20266123` - one-off WI-4813 file-only `VERIFIED` finalization waiver; now treated as precedent context, not the general policy for WI-4837.
- `DELIB-20266102` - related owner prioritization context for the work that exposed the post-`VERIFIED` finalization problem.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` - owner approved `NO-ACTION` blocker records as first-class Prime-authored bridge statuses.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` - `NO-ACTION` records route to Loyal Opposition and do not authorize implementation.
- `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702` - after `NO-ACTION`, implementation requires a later corrected `GO`.
- `bridge/gtkb-wi4837-post-verified-finalization-recovery-001.md` - original proposal.
- `bridge/gtkb-wi4837-post-verified-finalization-recovery-002.md` - initial NO-GO identifying F1/F2/F3.
- `bridge/gtkb-wi4837-post-verified-finalization-recovery-003.md` through `bridge/gtkb-wi4837-post-verified-finalization-recovery-010.md` - blocker-preservation and Loyal Opposition confirmation chain proving F3 was the remaining blocker.

## Owner Decisions / Input

The required owner decision is now recorded:

- `DELIB-WI4837-AUTOMATIC-PARITY-20260707` records the owner's 2026-07-07 choice: automatic parity is selected; per-instance waiver is rejected.

Decision effect:

- Allow Prime-side finalization staging for terminal-`VERIFIED` paths that are inside the approved proposal `target_paths`, matching the existing pre-commit clearance behavior.
- Do not require a new per-instance owner-waiver deliberation for each post-`VERIFIED` Prime-side finalization.
- Keep all clearance scoped to terminal `VERIFIED` bridge state and approved proposal `target_paths`; do not authorize arbitrary source/test edits, cleanup, database mutation, deletion, stash handling, branch/worktree pruning, deployment, force-push, credential lifecycle work, or unrelated staged work.

## Requirement Sufficiency

Existing requirements sufficient.

The owner decision `DELIB-WI4837-AUTOMATIC-PARITY-20260707`, WI-4837 backlog text, Batch A1 PAUTH, and the linked governance specifications now provide enough requirement detail for implementation. No new GOV, ADR, DCL, or SPEC record is required before implementation of this bounded gate repair.

## Findings Addressed

### F1 [P2] Outstanding Owner Policy Decision (F3) - Confirmed

Resolved. The owner selected automatic parity and the decision is recorded as `DELIB-WI4837-AUTOMATIC-PARITY-20260707`.

The corrected implementation direction is:

- For terminal-`VERIFIED` bridge threads, permit Prime-side staging/finalization only when every staged target resolves inside the approved proposal `target_paths`.
- Keep normal implementation-start authorization fail-closed for terminal `VERIFIED` when the command is not finalization staging of approved paths.
- Preserve existing `git commit`/`git push` finalization exemptions and denied-force-push behavior.
- Do not introduce per-instance owner-waiver packet validation for this automatic-parity path.

The earlier waiver-packet-oriented proposal text is superseded by this revision.

## Scope Changes

Compared with version 001:

- Removed the requirement for explicit owner-waiver deliberation evidence on every post-`VERIFIED` Prime-side finalization.
- Removed the need to tighten the pre-commit gate to a per-instance waiver bar.
- Kept the implementation focused on `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, and their focused tests.
- Narrowed acceptance to terminal `VERIFIED` plus approved proposal `target_paths`; unrelated protected paths and normal source/test mutation remain blocked.

## Proposed Implementation

1. Add or expose a small helper in `scripts/implementation_authorization.py` that can read a bridge thread's latest terminal `VERIFIED` state and return the approved proposal `target_paths` from the governing proposal in the version chain. The helper must fail closed when the thread is not terminal `VERIFIED`, no approved proposal target paths are found, or the path set cannot be parsed.
2. Update `scripts/implementation_start_gate.py` so `git add`/staging commands that otherwise trigger the mutating-command gate can be cleared only when:
   - the current work-intent/session context identifies the relevant bridge thread;
   - the bridge thread is latest terminal `VERIFIED`;
   - every command target is inside the approved proposal `target_paths`;
   - no denied git finalization flags, chained protected writes, broad reset/checkout/rm, deletion, cleanup, database mutation, or unparseable targets are present.
3. Keep `_validate_packet` behavior unchanged for normal implementation-start packets: terminal `VERIFIED` remains terminal and cannot restart implementation.
4. Preserve the existing report-snapshot cross-session isolation behavior already covered by the current test suite.

## Pre-Filing Preflight Subsection

Prime Builder ran the revision helper's candidate preflights before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4837-post-verified-finalization-recovery --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4837-post-verified-finalization-recovery-011.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4837-post-verified-finalization-recovery --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4837-post-verified-finalization-recovery-011.md
```

Observed draft results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: `must_apply: 3`, evidence gaps in must-apply clauses `0`, blocking gaps `0`, exit `0`.

The live filing helper also repeats both candidate preflights immediately before writing `bridge/gtkb-wi4837-post-verified-finalization-recovery-011.md`.

## Verification Plan

Spec-derived tests to add or update:

| Specification / Decision | Verification |
| --- | --- |
| `DELIB-WI4837-AUTOMATIC-PARITY-20260707` | Add tests showing terminal-`VERIFIED` `git add` of paths inside approved `target_paths` is allowed without per-instance owner waiver. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Add tests where non-terminal bridge states, malformed chains, and missing proposal target paths fail closed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Add tests proving automatic parity does not bypass the need for a latest terminal `VERIFIED` bridge chain and known proposal target paths. |
| `GOV-WORK-TREE-HYGIENE-001` | Add tests proving unapproved protected paths, deletion/cleanup commands, broad resets, and unparseable staging requests remain blocked. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Exercise helper reads against the live temp bridge files in test fixtures rather than cached summaries. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must include the exact pytest/ruff commands and observed results for the changed source and tests. |

Expected focused commands after implementation:

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
```

## Acceptance Criteria

- Latest terminal `VERIFIED` bridge state plus approved proposal `target_paths` can clear the narrow Prime-side `git add`/staging finalization case selected by the owner.
- Ordinary implementation packets still fail closed after terminal `VERIFIED`.
- Paths outside approved `target_paths` remain blocked.
- Destructive or broad git operations remain blocked.
- Existing `git commit`/`git push` finalization exemptions and force-push denial behavior remain unchanged.
- The implementation report carries forward all linked specifications and records executed spec-derived test evidence.

## Risk And Rollback

Primary risk: over-broadly allowing protected mutation after terminal `VERIFIED`. Mitigation: implement the clearance as a narrow finalization-staging path conditioned on terminal `VERIFIED`, exact approved `target_paths`, and parsed command targets; keep `_validate_packet` terminal behavior unchanged for ordinary implementation work.

Secondary risk: stale or malformed bridge chains could be treated as authorization. Mitigation: use fresh bridge file reads and fail closed on missing status, missing proposal target paths, malformed target metadata, or ambiguous command targets.

Rollback: revert the source/test changes in the four target files. The existing terminal-`VERIFIED` fail-closed behavior will remain the fallback.

## Recommended Commit Type

fix: repair a governed authorization deadlock in Prime-side post-`VERIFIED` finalization without adding a broad new capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
