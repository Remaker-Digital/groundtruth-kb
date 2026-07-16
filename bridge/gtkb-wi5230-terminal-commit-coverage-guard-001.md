NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Resolved WI-4978 VERIFIED commit omitted implementation hunks

bridge_kind: prime_proposal
Document: gtkb-wi5230-terminal-commit-coverage-guard
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5230

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prevent false work-item closure when a terminal VERIFIED bridge chain is uncommitted or its terminal commit omits source/test/configuration paths approved by the governing GO.

Work item description: WI-4978 is marked resolved after bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-050.md and commit 8cfd6fd3, but that commit contains only the WI-4978 bridge chain. The source/test helper chokepoint hunks described by the VERIFIED evidence remain staged in the live worktree and are absent from HEAD, blocking later governed implementation such as WI-5229 and invalidating resolved-state trust for source-bearing VERIFIED threads. Diagnose the finalization gap and add a durable guard so a work item cannot be resolved/verified when its claimed implementation paths are not present in the terminal commit.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5230` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_verified_backlog_reconciler.py`, `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666233` - Loyal Opposition Verification Verdict - WI-5229 Binary VERIFIED Finalizer Hunk Patch Support
- `DELIB-202666173` - Loyal Opposition Verdict: NO-GO (finalization-scoped) — WI-5210 Provider LO Governed Verdict Publication
- `DELIB-20260712-WI5205-HUNK-SCOPED-FINALIZATION-WAIVER` - Owner decision: WI-5205 hunk-scoped finalization waiver
- `DELIB-202666242` - Loyal Opposition Corrected Verdict - WI-5236 Dispatcher Runtime Fixture Drift
- `DELIB-202666104` - Loyal Opposition VERIFIED verdict — WI-5132 tolerate genuine version gaps in VERIFIED finalization

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5230`.

## Proposed Scope

- Derive the authoritative implementation target set structurally from the proposal/revision that an independent GO approved; a later stand-down or bridge-only implementation report cannot narrow away those obligations.
- For each directly VERIFIED implementation thread used as closure evidence, locate the Git commit containing the latest VERIFIED artifact and require that commit to contain the terminal verdict plus every approved non-bridge implementation target, unless an explicit governed by-reference/non-source waiver is structurally present and its referenced commit/path evidence validates.
- Expose deterministic per-thread diagnostics for uncommitted terminal verdicts, missing approved targets, malformed target metadata, and invalid waiver evidence; fail closed without parsing free-form completion claims.
- Exclude terminal evidence that fails this floor from satisfied_implementation_bridge_threads so normal resolution skips it, and make the existing overbroad-resolution repair path reopen already-resolved false closures such as WI-5249.
- Preserve advisory, withdrawn, satisfied-umbrella, parent-evidence, and legitimate bridge-only governance behavior when no approved non-bridge implementation targets exist; do not mutate bridge artifacts, Git state, groundtruth.db, dispatcher state, or historical evidence.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | TEST-11384 and focused reconciler tests build temporary Git histories and prove VERIFIED closure requires a committed terminal verdict plus the GO-approved implementation paths. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short and Ruff check/format on both exact targets. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Existing resolution, advisory-link, umbrella, canonical-parent-evidence, and overbroad-repair tests remain green while new diagnostics are surfaced in classification output. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Regression fixtures prove a later bridge-only stand-down cannot erase source/test ownership and repair mode reopens the resulting false closure without touching unrelated work. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Malformed or unverifiable commit/target/waiver evidence fails closed with deterministic reasons instead of being treated as completion. |

## Acceptance Criteria

- TEST-11384 proves a terminal VERIFIED file that is untracked or absent from Git cannot resolve its work item.
- A GO-approved source/test target omitted from the terminal verdict commit blocks resolution even when a later report narrows target_paths to a bridge-only stand-down.
- A terminal commit containing the verdict and every GO-approved implementation target resolves normally; explicit governed waiver evidence passes only when its referenced commit and paths validate.
- Repair mode reopens a previously resolved false closure while advisory/umbrella and genuinely bridge-only governance fixtures retain their existing behavior.
- Focused reconciler tests and Ruff checks pass with no dispatcher, TAFE, harness, lease, eligibility, runtime, database, or Git mutation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_verified_backlog_reconciler.py`
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`

## Recommended Commit Type

`feat`
