REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.C: Docs Cluster Move (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-06 (S334)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-c-docs-cluster-003.md` (F1 inventory drift; F2 missing secret-scan gate). Carries forward `-001` substantive content + `-002` Owner Decisions section unchanged except for the specific F1 + F2 fixes.
**Predecessors:** `-001` (parked draft substantive content), `-002` (promotion with Owner Decisions section), `-003` (Codex NO-GO).

---

## Codex Findings Addressed

| Finding | Disposition |
|---|---|
| **F1 (P1)** — Live docs inventory has 170 non-platform tracked files (not 166); `docs/release/` (2 files) missing from migration strategy Step 2 | This revision: (a) adds `git mv docs/release applications/Agent_Red/docs/` to Step 2; (b) updates expected counts from 166 → 170 in T-rule-1, T-inv-1, and Acceptance Criteria; (c) cites Codex's verification command as evidence. Codex's verification was `git ls-files docs | rg -v '^docs/(gtkb-dashboard|specification-scaffold|assets/gtkb-dashboard)/' | Measure-Object` returning 170. Live re-confirmed via `git ls-files docs/ | grep -vE "^docs/(gtkb-dashboard|specification-scaffold|assets/gtkb-dashboard)/" | wc -l` = 170. |
| **F2 (P2)** — Test plan omits redacted secret-scan gate for moved docs surfaces (47 candidate-high findings, 0 verified-provider in pre-move probe) | This revision adds T-secret-1 + T-secret-2 to the Test Plan: pre-move baseline scan (must record candidate-high count for delta verification); post-move scan with `--fail-on verified-provider` against new and old paths. Post-impl REPORT must record both scan results. Codex's exact recommended command form preserved. |

---

## Specification Links

All `-001` Specification Links carry forward unchanged. Re-cited here for preflight matching:

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 owner_decision)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE)
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO)
- `bridge/gtkb-isolation-018-agent-red-file-migration-009.md` (umbrella REVISED-3 GO at -009; confirms 170 docs/ Agent Red count in re-scoped inventory)
- `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (waiver VERIFIED)
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md` (VERIFIED; secret-scan tooling that F2's T-secret-1 invokes)
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush-004.md` (VERIFIED)
- `bridge/gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006.md` (VERIFIED)
- `applications/Agent_Red/.gtkb-app-isolation.json`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-007.md` (VERIFIED at -012; pattern precedent)

Advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

The Test Plan derives from these specs as documented in `-001` line 51, plus the new T-secret-1 + T-secret-2 derivation from the secret-purge VERIFIED bridge threads cited above.

## Owner Decisions / Input

This REVISED is filed in response to Codex F1 + F2 findings; it does NOT re-engage owner decisions. The S334 directive's broad pre-approval covers Codex-finding revisions per the file-bridge-protocol's NO-GO → REVISE → GO cycle.

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "Agent Red isolation — what's the next move?" (S334, 2026-05-06) | "Isolation move" | Owner replied "Other": full directive approving completion of the isolation workstream as release-gating; only blocking technical dependencies authorize deferral. | Authorizes this REVISED-1 to address Codex F1 + F2 without re-engaging owner. |
| "Sub-slice 18.D — how to handle the inventory drift?" (S334, 2026-05-06) | "18.D scope" | Owner chose "Re-scope umbrella first" → umbrella `-008` filed and GO'd at `-009`. | Umbrella `-009` GO confirms 170 docs/ count; this revision aligns 18.C with that count. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 AUQ) | (S330) | Owner directive establishing 5 binding rules. | Source authority preserved; revision does not change scope authorization. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S330/S331 AUQ) | (S331) | ACTIVE waiver. | Continues to authorize the in-flight pre-migration state. |
| OQ-A, OQ-B, OQ-C (S331 AUQ) — platform exclusions, in-place workflow edits, atomic docs-site dir-rename | Per `-001` Background §S331 AUQ | All resolved by S331 AUQ as documented in `-002`. | Resolutions carry forward unchanged. |

## F1 Fix — Migration Strategy Step 2 update

`-001`'s Migration Strategy Step 2 (lines 157–179) lists 19 Agent Red subdirectories of `docs/`. This revision adds one subdirectory:

**Add to Step 2 (alphabetical position between `docs/proposals` and `docs/reports`):**

```text
git mv docs/release applications/Agent_Red/docs/
```

After this addition, Step 2 lists 20 Agent Red subdirectories of `docs/`. The `docs/release/` directory contains 2 tracked files (`dev-environment-inventory.json`, `dev-environment-inventory.md`) per live probe `git ls-files docs/release/`.

All other elements of Step 2 (the 19 existing `git mv` commands), Steps 1, 3, 4, 5, 6, 7 carry forward from `-001` unchanged.

## F1 Fix — Test Plan count updates

`-001`'s Test Plan T-rule-1, T-inv-1, and the Acceptance Criteria expect 166 Agent Red docs files. Updated to 170:

| Test ID | `-001` value | REVISED-1 value |
|---|---|---|
| **T-rule-1** | "docs: 166 tracked + 0 untracked = 166" | **"docs: 170 tracked + 0 untracked = 170"** |
| **T-inv-1** | "166 and 88 respectively" | **"170 and 88 respectively"** |
| Acceptance Criteria | "applications/Agent_Red/docs/ exists with 166 tracked files" | **"applications/Agent_Red/docs/ exists with 170 tracked files"** |

`-001` Migration Strategy live-probe footnote (line 209: "Final list re-confirmed via `git ls-files docs/` to catch drift") remains operative — implementation re-confirms at execution time and updates expected counts accordingly.

## F2 Fix — Add T-secret-1 + T-secret-2 to Test Plan

Added between T-pkg-1 (manifest co-location) and T-history-1 (history preservation) in `-001` Test Plan table (after line 288):

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-secret-1** | Pre-move secret-scan baseline (per `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md` VERIFIED tooling contract); F2 fix | `python -m groundtruth_kb secrets scan --paths docs docs-site --redacted --fail-on verified-provider` (run BEFORE Step 2 git mv operations; record candidate-high count) | Exit 0; 0 verified-provider findings; candidate-high count recorded for delta verification (Codex's pre-move probe found 47 candidate-high findings; this baseline must match within reasonable variance) |
| **T-secret-2** | Post-move secret-scan verification; F2 fix | `python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider` (run AFTER Step 6 in-place workflow edits; record candidate-high count) | Exit 0; 0 verified-provider findings; candidate-high count is approximately T-secret-1 count (± 5% tolerance for path-string changes in moved files); post-impl REPORT records both counts and any path-specific delta WITHOUT exposing raw matched values per `--redacted` invariant |

## F2 Fix — Specification-to-Test Mapping additions

Added to `-001`'s Specification-to-Test Mapping table (after line 313, before "Advisory" row):

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| Pre-move secret-scan baseline (per `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md`) | T-secret-1 | Direct |
| Post-move secret-scan verification (no verified-provider findings; candidate-high delta within tolerance) | T-secret-2 | Direct |

## F2 Fix — Acceptance Criteria addition

Added to `-001`'s "VERIFIED when:" list (after line 334):

- [ ] T-secret-1 baseline scan recorded with explicit candidate-high count and 0 verified-provider findings
- [ ] T-secret-2 post-move scan returns 0 verified-provider findings
- [ ] Post-impl REPORT records both candidate-high counts (pre-move and post-move) using `--redacted` invariant; no raw matched values exposed

## Carry-Forward Statement

All other sections of `-001` and `-002` are carried forward VERBATIM:

- Background (`-001` lines 14–18)
- Specification Links (`-001` lines 20–51) — re-cited above for preflight matching, additional secret-scan VERIFIED bridge threads added
- Prior Deliberations (`-001` lines 53–64)
- Goal (`-001` lines 66–68; updated count 166 → 170 implicitly via Migration Strategy)
- Live-Probed Inventory (`-001` lines 70–126; addresses 166-vs-170 discrepancy via update note: "Live count is 170 per Codex F1; this section's 166 figure is updated to 170 in T-rule-1, T-inv-1, and Acceptance Criteria")
- Migration Strategy Steps 1, 3, 4, 5, 6, 7 (`-001` lines 128–271; only Step 2 modified)
- Specification-Derived Test Plan (`-001` lines 273–294; T-secret-1 and T-secret-2 added)
- Specification-to-Test Mapping (`-001` lines 296–316; secret-scan rows added)
- Acceptance Criteria (`-001` lines 318–335; count update + secret-scan rows added)
- Risk / Rollback (`-001` lines 337–350)
- Open Questions (`-001` lines 352–360)
- Out of Scope (`-001` lines 362–370)
- Project Root Boundary Compliance (`-001` lines 372–378)
- Provenance (`-001` lines 380–393)

This `-004` adds only the F1 + F2 fixes and Owner Decisions / Input section; it does NOT re-author the substantive content.

## Pre-Filing Preflight Subsection

This `-004` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` after INDEX update points at `-004`. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

`packet_hash` recorded in post-Write preflight evidence.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
