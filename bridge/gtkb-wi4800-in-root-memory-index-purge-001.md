NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4800

# INDEX.md Residue Strip — In-Root Memory Tranche (WI-4800)

Document: gtkb-wi4800-in-root-memory-index-purge
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4800
Recommended commit type: docs

## Summary

Complete the Prime-Builder-actionable portion of WI-4800 by stripping obsolete
`bridge/INDEX.md` operational guidance from editable **in-root** memory surfaces only.
The stale S4 memory references still teach agents to treat the retired aggregate as
live bridge authority, or to re-read it before bridge work. They now conflict with the
post-WI-4510 bridge model: dispatcher/TAFE-backed bridge state plus status-bearing
numbered files under `bridge/` are canonical.

This proposal deliberately narrows WI-4800 from its original June 2026 wording. The
work item and classification contract mentioned home-directory Claude memory, but the
current mandatory root-boundary gate is now explicit: bridge items depending on live
paths outside `E:\GT-KB` are `NO-GO`. This proposal therefore excludes all out-of-root
harness memory from implementation scope and performs only the in-root portion of S4.

<!-- in-root-disclosure -->
Historical contention note: `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624`
AUQ Q3 and `bridge/gtkb-index-md-classified-inventory-001.md` described a cross-root
home-directory memory purge. The active `.claude/rules/project-root-boundary.md` and
`.claude/rules/file-bridge-protocol.md` now supersede that implementation shape for
bridge work: all live GT-KB artifact reads, writes, verification, and dependency
closure must remain inside `E:\GT-KB`; a bridge item depending on a live path outside
that root is `NO-GO`. No owner waiver is requested here.
<!-- /in-root-disclosure -->

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — significant retirements require
  stale load-bearing references to the retired implementation to be removed or
  quarantined with justification.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — the STRIP set for a purge work item
  cannot be treated complete until stale operational references in the in-scope
  surface are removed or reclassified.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is retired as live authority;
  dispatcher/TAFE bridge state plus numbered bridge files are canonical.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — memory notes must not route agents to stale
  bridge authority when fresh canonical bridge-state readers exist.
- `GOV-STANDING-BACKLOG-001` — WI-4800 is the MemBase backlog work item being
  processed under this proposal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the project authorization cited
  above is owner-approval evidence for proceeding through normal bridge review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links
  governing specifications and maps verification back to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must
  execute the spec-derived test plan below before `VERIFIED`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) and
  `.claude/rules/project-root-boundary.md` — every target path in this proposal is
  inside `E:\GT-KB`; out-of-root memory is explicitly excluded.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — this cleanup preserves the
  purge decision as durable bridge evidence while keeping the editable memory layer
  aligned with current authority.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` — owner directive and
  AUQ decisions authorizing the obsolete-reference purge project, including S4 memory
  cleanup.
- `gtkb-obsolete-reference-purge-methodology-adr-dcl` (GO at `-004`) — methodology
  thread that established the purge ADR/DCL.
- `gtkb-index-md-classified-inventory` (GO at `-002`, withdrawn later as review-only
  after preserving the classification contract) — STRIP/KEEP/QUARANTINE contract
  for the `bridge/INDEX.md` residue family; S4 is editable harness memory.
- `gtkb-index-md-strip-docs` (WI-4797, VERIFIED) — created the shared classification
  contract test file that this tranche extends.
- `gtkb-index-md-strip-tests` (WI-4798, VERIFIED) and `gtkb-index-md-strip-skill-docs`
  (WI-4799, VERIFIED) — prior strip tranches under the same PAUTH.
- `bridge/gtkb-wi4801-legacy-harness-language-scan-001.md` through `-004` — peer
  obsolete-reference project tranche that stayed in-root and excluded audit/runtime
  surfaces.

## Requirement Sufficiency

Existing requirements sufficient. WI-4800 names the memory cleanup tranche, and the
obsolete-reference purge ADR/DCL plus the current root-boundary gate determine the
safe implementation scope. No new requirement is needed; the only scope correction is
to exclude the out-of-root portion that current bridge rules would reject.

## Target Paths

target_paths: ["memory/antigravity-integration-status.md", "memory/fable-campaign-monitor-envelope.md", "memory/fable-investigation-campaign.md", "memory/project_role_status_orthogonality_dispatch.md", "memory/feedback/feedback_interactive_poller_monitor.md", "memory/feedback/feedback_read_index_comments_before_executing_go.md", "memory/feedback/feedback_session_start_orient_block.md", "memory/feedback/feedback_worktree_drift_pattern.md", "platform_tests/governance/test_index_md_classification_contract.py"]

The target set is concrete and in-root. It excludes:

- `memory/CLAUDE_ARCHIVE.md`, `memory/pending-owner-decisions.md`, and
  `memory/archive/**` as QUARANTINE/history records.
- `bridge/**`, `independent-progress-assessments/**`, `.groundtruth/**`,
  `.gtkb-state/**`, and all generated/cache surfaces.
- All home-directory or other out-of-root harness memory.

## Per-File Disposition

**STRIP / UPDATE:**

| File | Disposition |
|---|---|
| `memory/antigravity-integration-status.md` | Replace live-authority `bridge/INDEX.md` wording with dispatcher/TAFE bridge-state wording; preserve historical NO-GO context without treating the aggregate as current. |
| `memory/fable-campaign-monitor-envelope.md` | Replace "Canonical state = `bridge/INDEX.md` + MemBase" and "Read live `bridge/INDEX.md`" guidance with MemBase plus dispatcher/TAFE bridge-state guidance. |
| `memory/fable-investigation-campaign.md` | Rewrite operational "live queue" / "read live bridge/INDEX first" / "single bridge/INDEX write" instructions to current bridge-state and governed writer language. |
| `memory/project_role_status_orthogonality_dispatch.md` | Remove stale evidence wording that treats `bridge/INDEX.md` as a live bridge-thread glob/authority surface. |
| `memory/feedback/feedback_interactive_poller_monitor.md` | Reframe the old poller-monitor note as retired historical guidance or dispatcher/TAFE-state guidance. |
| `memory/feedback/feedback_read_index_comments_before_executing_go.md` | Rewrite the old "scan bridge/INDEX.md comments" guidance to current thread-chain/dispatcher-state inspection, or quarantine it as historical if it is no longer actionable. |
| `memory/feedback/feedback_session_start_orient_block.md` | Replace startup "bridge/INDEX.md scan" instructions with dispatcher/TAFE bridge-state scan instructions. |
| `memory/feedback/feedback_worktree_drift_pattern.md` | Preserve the historical incident lesson while rephrasing the stale authority surface to "stale bridge-state snapshot" rather than current `bridge/INDEX.md` guidance. |
| `platform_tests/governance/test_index_md_classification_contract.py` | Extend the shared S1 contract test with S4 in-root memory strip-completeness and quarantine-history assertions. |

**QUARANTINE / no edit:**

- `memory/CLAUDE_ARCHIVE.md` — chronological wrap archive; references are historical evidence.
- `memory/pending-owner-decisions.md` — owner-decision tracker/archive; references are quoted historical questions/answers.
- `memory/archive/**` — archived memory records.

## Cross-Harness Disposition

This tranche touches in-root editable memory and one shared governance test only. It does
not modify `.claude/skills`, `.codex/skills`, `.cursor`, `.agent`, hooks, harness
registry files, or generated skill adapters. No cross-harness adapter regeneration is
required. The cross-harness concern from the original WI title is handled by scope:
out-of-root harness memory is excluded, and any future cross-harness memory-store work
would need a separate root-boundary-compliant proposal or explicit new owner-approved
exception.

## Verification Plan

### Specification-Derived Verification — Spec-to-Test Mapping

| Linked spec / requirement | Test or command | Expected result |
|---|---|---|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` S4 STRIP completion | Extend `platform_tests/governance/test_index_md_classification_contract.py` with an S4 test over the eight STRIP memory files | No STRIP memory target contains obsolete live-authority `bridge/INDEX.md` guidance after implementation. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` removal-not-prohibition principle | Same S4 test plus manual diff review | The stale instructions are rewritten to current dispatcher/TAFE language, not merely annotated with "do not use." |
| QUARANTINE/history preservation | New or extended test asserts `memory/CLAUDE_ARCHIVE.md`, `memory/pending-owner-decisions.md`, and `memory/archive/pending-owner-decisions-202605.md` are outside the STRIP target set and may retain historical references | Historical memory records are not edited for this tranche. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / root-boundary gate | Test target list contains only relative paths under `memory/` and `platform_tests/`; implementation report states no out-of-root files were read or edited | In-root only. |
| Existing S1 KEEP/QUARANTINE contract | Existing tests in `platform_tests/governance/test_index_md_classification_contract.py` | Existing docs/guard/quarantine tests still pass. |
| Code quality | `python -m ruff check platform_tests/governance/test_index_md_classification_contract.py` and `python -m ruff format --check platform_tests/governance/test_index_md_classification_contract.py` | Pass. |

Required implementation commands:

```text
python -m pytest platform_tests/governance/test_index_md_classification_contract.py -q --tb=short
python -m ruff check platform_tests/governance/test_index_md_classification_contract.py
python -m ruff format --check platform_tests/governance/test_index_md_classification_contract.py
rg -n "bridge/INDEX\\.md|read live bridge/INDEX|live bridge/INDEX|Canonical state = `bridge/INDEX\\.md` \\+ MemBase|Canonical truth is MemBase \\(`groundtruth\\.db`\\) \\+ `bridge/INDEX\\.md`" memory/antigravity-integration-status.md memory/fable-campaign-monitor-envelope.md memory/fable-investigation-campaign.md memory/project_role_status_orthogonality_dispatch.md memory/feedback/feedback_interactive_poller_monitor.md memory/feedback/feedback_read_index_comments_before_executing_go.md memory/feedback/feedback_session_start_orient_block.md memory/feedback/feedback_worktree_drift_pattern.md
```

The final `rg` command should return no STRIP-class live-authority guidance in the
targeted memory files.

## Risk / Rollback

- **Risk: over-stripping historical memory.** Mitigated by the explicit QUARANTINE set:
  archive and pending-owner-decision records are not targets.
- **Risk: the original owner authorization expected home-directory memory cleanup.**
  Mitigated by this proposal's explicit root-boundary narrowing; the out-of-root portion
  is not silently implemented and can be reconsidered only through a separate governed
  exception if still desired.
- **Risk: memory notes lose useful historical context.** Mitigated by rewriting active
  instructions to current authority rather than deleting incident context wholesale.
- **Rollback:** revert the eight memory files plus the single test-file extension.
  No KB mutation, formal spec mutation, or out-of-root file mutation is in scope.

## Owner Decisions / Input

No new owner decision is required for the in-root tranche. This proposal proceeds under:

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` — owner AUQ authorizing the
  obsolete-reference purge project and S4 memory cleanup.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25` — active
  project authorization including WI-4800.

The proposal does not request a waiver for out-of-root memory. It instead excludes that
portion as superseded by the current root-boundary bridge gate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
