REVISED

# Implementation Proposal (Slice 0 - Scoping) - GTKB-ARTIFACT-RECORDER-CLI - REVISED-2

**Document:** `gtkb-artifact-recorder-cli`
**Status:** `REVISED`
**Version:** 003 (REVISED-2 post NO-GO at `-002`)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Slice:** 0 (scoping only; per-slice implementation proposals follow Codex GO)
**Recommended commit type:** `docs:` (scoping bridge artifact only; no source changes; per-slice implementations will land as `feat:` / `refactor:` commits)
**Supersedes:** `bridge/gtkb-artifact-recorder-cli-001.md` (NEW; NO-GO at `-002`).

## Revision Notes (REVISED-2)

Codex NO-GO at `-002` identified two findings:

- **F1 (P1 blocking):** `GOV-STANDING-BACKLOG-001` was applicable per clause preflight but missing from `## Specification Links` of `-001`, creating an incomplete authority set for a scoping parent that references `memory/work_list.md` as owner-approval evidence (`-001:52`) and coupled-thread state (`-001:203-207`).
- **F2 (P2 blocking for scoping parent):** Coupled-thread status claims in `-001:203-207` were stale against live `bridge/INDEX.md`. The narrative-extension thread is now VERIFIED, not awaiting review; the bridge-skill-unified thread is in a NO-GO revision loop; the docs-quality umbrella is VERIFIED.

REVISED-2 adds `GOV-STANDING-BACKLOG-001` to `## Specification Links` with the governance-contract explanation (per `.claude/rules/operating-model.md:102` which ties `memory/work_list.md` to that GOV), refreshes the `## Coupling with Other In-Flight Threads` section against live INDEX (verified 2026-05-11 S341 during this revision), and clarifies that Slice 0 GO authorizes only per-slice bridge filings, not implementation code for any slice.

The original `-001` proposal's substantive scope (the 6-slice plumbing-to-service migration for `gt <artifact-type> record`) is unchanged; only the authority set and current-state references are corrected.

## Claim

This proposal formalizes the scoping of `GTKB-ARTIFACT-RECORDER-CLI` - the named first concrete manifestation of the Deterministic Services Principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, citing `.claude/rules/acting-prime-builder.md` § Deterministic Services Principle). The proposal does NOT request authorization for any individual implementation slice; each implementation slice will file its own bridge thread and independently satisfy the Mandatory Specification Linkage Gate and the Mandatory Specification-Derived Verification Gate before receiving `GO` or `VERIFIED`.

The work moves formal-artifact insertion plumbing (deliberations, GOV/SPEC/PB/ADR/DCL/REQ records, owner-decision packets) behind a `gt <artifact-type> record` CLI in `groundtruth-kb`. The service handles ID generation, SHA computation, approval-packet construction, KB insertion, and ChromaDB indexing as deterministic operations rather than AI-mediated boilerplate. AI surface drops from ~150 LOC of orchestration to a single CLI call with 6-8 structured arguments. The formal-artifact-approval-gate hook remains as defense-in-depth for raw-API anomalies.

This Slice 0 scoping proposal, if granted GO, authorizes ONLY the filing of per-slice bridge threads. It does NOT authorize source code, MemBase mutations, or any implementation commit. Each per-slice proposal must independently pass the bridge protocol gates.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `DELIB-0874`
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/deliberation-protocol.md`

**GOV-STANDING-BACKLOG-001 governance-contract note (F1 fix):** This proposal cites `memory/work_list.md` row 113 (`-001:52`) as historical owner-approval evidence and references the standing backlog as the active-pursuit driver for the Deterministic Services Principle. Per `.claude/rules/operating-model.md:102`, `memory/work_list.md` is the transitional standing-backlog view that converges into MemBase under `GOV-STANDING-BACKLOG-001`. Per S337 owner directive (`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`), the file is deleted at migration conclusion. Per-slice proposals SHOULD refresh MemBase/work-item and bridge state at filing time rather than inheriting row statuses from this scoping proposal; this Slice 0 record is a snapshot of authority and state at S341, not a perpetual ground truth.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (owner decision; load-bearing) - establishes the active-pursuit mandate for plumbing-to-service work and names `GTKB-ARTIFACT-RECORDER-CLI` as the first concrete manifestation.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` (2026-04-27 S312) - the original friction surface; ~150 LOC of manual orchestration prompted owner approval of this work.
- `DELIB-0874` - artifact-oriented governance broader framing.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` (2026-05-07) - lifted the freeze that previously blocked this thread.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - reinforces that `memory/work_list.md` is transitional, not final authority (cited by Codex `-002` review).
- `DELIB-0835` - formal-artifact approval/audit-trail owner decision; directly constrains approval-packet behavior the CLI must preserve.
- Owner approval at S312 (2026-04-27) - captured at `memory/work_list.md` row 113.
- S341 hygiene-plan AUQ (this session, 2026-05-11) - the owner's autonomous-execution directive authorizes filing this REVISED-2.

## Owner Decisions / Input

This scoping proposal depends on the following owner authorizations:

1. **Owner approval at S312 (2026-04-27)** captured at `memory/work_list.md` row 113. Authorizes the GTKB-ARTIFACT-RECORDER-CLI work as the named first manifestation of `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
2. **Owner directive at S340 (2026-05-11)** - "Proceed with: Filing the GTKB-ARTIFACT-RECORDER-CLI proposal (largest principle-affirming win)". Authorized the original `-001 NEW`.
3. **Autonomous-execution directive at S341 (2026-05-11)** - "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context". Authorizes this REVISED-2 filing in response to the Codex `-002` NO-GO.

Outstanding owner decisions before VERIFIED: none for this Slice 0 scoping proposal. Per-slice implementation proposals will each carry their own owner-decision section.

## Scope

Same scope as `-001`. Six follow-on implementation slices were enumerated in `-001`'s scope section, covering: (1) `gt deliberations record` CLI surface; (2) `gt spec record` for GOV/SPEC/PB/ADR/DCL/REQ; (3) approval-packet auto-generation; (4) ChromaDB indexing integration; (5) gate-compatibility (the path-matched formal-artifact-approval-gate is preserved); (6) owner-decision packet recording. This REVISED-2 does not modify scope; each per-slice proposal will redefine its own concrete scope at filing time.

This Slice 0 GO, if granted, authorizes ONLY per-slice bridge filings.

## Coupling with Other In-Flight Threads

(F2 fix: refreshed against live `bridge/INDEX.md` at 2026-05-11 S341.)

- `gtkb-narrative-artifact-approval-extension-001`: **VERIFIED** at `bridge/gtkb-narrative-artifact-approval-extension-001-011.md`. The narrative-artifact-approval-gate is operational; when the artifact-recorder CLI lands, its service surface must emit narrative-artifact-approval packets where applicable (matching the `[[protected_artifacts]] role-and-governance-rules` pattern in `config/governance/narrative-artifact-approval.toml`).
- `gtkb-bridge-skill-unified-001`: **NO-GO** at `bridge/gtkb-bridge-skill-unified-001-004.md`. The unified bridge skill thread is in a revision loop; per-slice artifact-recorder proposals should not assume the unified-skill surface is available. Once that thread VERIFIEDs, the CLI's bridge-related artifact recording (if any) may delegate to it.
- `gtkb-docs-quality-remediation`: **VERIFIED** at `bridge/gtkb-docs-quality-remediation-004.md` (umbrella) and `gtkb-docs-quality-remediation-slice-1-root-readme-rewrite` **VERIFIED** at `-006`. Cited as adjacent scoping-pattern precedent (7-slice umbrella that successfully landed); the artifact-recorder thread will mirror its per-slice-independent-gate structure.

## Test Plan (Slice 0 only)

This Slice 0 scoping proposal is verifying that its own authority and current-state references are accurate. No source-code execution or test runs are in scope for Slice 0.

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli` - expect PASS.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli` - expect exit 0.
3. Re-verify the 3 coupled-thread INDEX statuses at GO/VERIFIED time match this proposal's text.

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | Step 1 PASS + this thread reaches VERIFIED through INDEX. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All scoping work and any future implementation slices stay inside `E:\GT-KB`. |
| GOV-STANDING-BACKLOG-001 | Citation governance-contract note above + per-slice proposals refresh state at filing. |
| All other cited specs | Per-slice proposals will independently re-cite and provide per-slice test mappings. |

## Acceptance Criteria

- [ ] Applicability preflight PASS (`missing_required_specs: []`, `missing_advisory_specs: []`).
- [ ] Clause preflight exit 0; 0 blocking gaps.
- [ ] Codex VERIFIED on this REVISED-2.
- [ ] Per-slice proposals subsequently filed with refreshed MemBase / bridge state at their filing time.

## Risk + Rollback

This Slice 0 scoping proposal has no execution surface. Rollback is `git revert <commit-sha>` for the bridge file + INDEX entry; per-slice implementations have their own rollback contracts.

## Loyal Opposition Asks

1. Confirm `GOV-STANDING-BACKLOG-001` citation + governance-contract note resolves F1.
2. Confirm the refreshed coupling section resolves F2 (each coupled thread cited with current INDEX status + latest file path).
3. Confirm the "Slice 0 GO authorizes ONLY per-slice bridge filings" clarification (paragraph in `## Claim` + acceptance criterion) addresses Codex `-002:135-137`'s required action #3.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
