REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-18-backlog-dignity
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-18-backlog-dignity-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4430
Project Authorization: PAUTH-FAB18-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*.json", "scripts/advisory_backlog_router.py", "scripts/harvest_session_deliberations.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/session_self_initialization.py", ".claude/rules/prompt-organize-reports-in-dropbox.md", "independent-progress-assessments/**", "independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md", "archive/**", "config/governance/advisory-routing-retention.toml", "platform_tests/scripts/**"]

KB mutation: YES. Two MemBase writes: (1) the DA-harvest of the advisory reports (deliberation inserts via the existing harvest mechanism) and (2) the bulk-close of the routing work items (append-only resolve, under GOV-15 + kb-batch dry-run). `groundtruth.db` is therefore in `target_paths`. No canonical specification or DA records are hard-deleted.

---

# FAB-18 — Backlog Dignity

WI-4430 (FAB-18) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-015 (advisory-routing flood), HYG-065
(PAUTH-coverage WARN inflation), HYG-060 (IPA root organization). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md`.

Common theme: the backlog and its measurement surfaces have lost their dignity as priority signals — a
routing flood buries real work, a miscalibrated coverage check inflates 930 false WARNs, and the IPA root
contradicts its own organize rule.

## Revision Scope

REVISED-003 responds to the two NO-GO findings in `bridge/gtkb-fab-18-backlog-dignity-002.md`:

- **F1 (protected organize-rule packet artifact missing from target_paths):** added
  `.groundtruth/formal-artifact-approvals/*.json` so the narrative-artifact-approval packet for the protected
  `.claude/rules/prompt-organize-reports-in-dropbox.md` allowlist refresh falls inside the GO'd path-scope.
- **F2 (archive destination + move-manifest paths not concrete):** added `archive/**` (the explicit
  archive-not-delete destination for the ~10 scratch/render directories) and a concrete move-manifest path
  `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md` to `target_paths`. The HYG-060 reorg
  now has its full move perimeter (source `independent-progress-assessments/**`, destinations
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` and `archive/**`) and a named provenance manifest
  in scope, so the archive-not-delete safety property is verifiable.

No other substantive change; the DA-harvest-before-close, kb-batch dry-run, and GOV-15 constraints for the
advisory-routing WI closure are unchanged from -001.

## Summary

- **HYG-015 (advisory flood):** the advisory_backlog_router has minted 758 open 'Route LO advisory' WIs
  (one per INSIGHTS report), now ~75% of the visible backlog, while DA-harvest coverage of those reports is
  ~1.3% — write-only at both ends, so real work items are needles in a routing-stub haystack.
- **HYG-065 (PAUTH coverage):** the doctor's '930 warn' backlog-health output is one orphaned-WI WARN per
  open WI not covered by any active PAUTH (~842 of ~1,004) — but most are future/unapproved backlog work
  that, by the approval-state model, should not need an active implementation authorization.
- **HYG-060 (IPA root):** independent-progress-assessments/ holds 89 entries (69 files + 20 dirs) against
  its organize rule's ~9-file allowlist; ~66 Agent-Red-era reports/renders, and the rule references archived
  CURSOR-* filenames that no longer exist (so the rule cannot be followed as written).

## Specification Links

- `GOV-STANDING-BACKLOG-001` — the backlog must function as a usable priority surface; the drain + the
  coverage recalibration restore that (HYG-015, HYG-065).
- `SPEC-DA-HARVEST-INCLUSION` — the DA-harvest of the advisory reports before bulk-closing their routing WIs
  (HYG-015).
- `GOV-15` (Test fix gate) — the bulk-close of routing WIs runs under GOV-15 gating + kb-batch dry-run
  (HYG-015).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the PAUTH-coverage model the recalibrated backlog-health
  check reflects (PAUTH = implementation-authorization envelope, not blanket WI coverage) (HYG-065).
- `GOV-SESSION-SELF-INITIALIZATION-001` — the startup-disclosure backlog metric whose accuracy the
  recalibration fixes (HYG-065).
- `GOV-ARTIFACT-APPROVAL-001` — the organize-rule allowlist refresh is a protected narrative artifact
  requiring a per-file approval packet recorded under `.groundtruth/formal-artifact-approvals/`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-18 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the WI resolution + DA harvest.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-015/060/065).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB18-REMEDIATION-20260610` — this cluster's three owner dispositions (below).
- _The 4402 item (Advisory Backlog Drain Policy) names the HYG-015 fix; this cluster executes it._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB18-REMEDIATION-20260610`:

1. **HYG-015 = DA-harvest all + bulk-close >60d + router age-out.** DA-harvest all 765 reports (fixes the
   1.31% coverage FAIL); bulk-close routing WIs older than 60 days via kb-batch with dry-run + GOV-15; triage
   the recent tail; add an age-out rule to the router so the population stays bounded.
2. **HYG-065 = Recalibrate the backlog-health check.** Treat 'uncovered by PAUTH' as normal for
   unapproved/future WIs (per the approval-state model); WARN only for implementation-active WIs lacking
   coverage; fix the startup-disclosure metric so its backlog counts reflect real actionable work.
3. **HYG-060 = Full reorg + rule refresh.** Move ~66 stale reports to CODEX-INSIGHT-DROPBOX/ and ~10
   scratch/render dirs to archive/ (archive-not-delete, with a file→destination manifest); refresh the
   organize rule's allowlist (narrative packet) to the filenames that actually exist.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB18-REMEDIATION-20260610`; the
governing specifications (`GOV-STANDING-BACKLOG-001`, `SPEC-DA-HARVEST-INCLUSION`, `GOV-15`,
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-SESSION-SELF-INITIALIZATION-001`) already constrain the
backlog-authority, DA-harvest, test-fix-gate, project-authorization, and startup-disclosure surfaces. No new
requirement is needed; the recalibration aligns the health check with the existing approval-state model.

## Scope and Boundaries

In scope: the advisory drain, the coverage recalibration + startup-metric fix, and the IPA reorg + rule
refresh (with the archive destination + move manifest now concrete). Out of scope and explicitly excluded:
any change to the PAUTH/authorization model itself (only the health-check's interpretation of it); deleting
reports (archive-not-delete); deploy/push. This proposal absorbs the advisory's overlap for FAB-18 (the 4402
drain-policy item, the 3327 and 3502 items) by executing or describing them here; backlog-state
reconciliation is a post-VERIFIED operational step.

## Proposed Implementation

**Area 1 — HYG-015 advisory drain.** DA-harvest all 765 CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md reports via
`harvest_session_deliberations.py` (clears the 1.31% coverage FAIL); bulk-close routing WIs older than 60
days through kb-batch with dry-run + GOV-15 owner gating; triage the recent tail; add an age-out rule to
`advisory_backlog_router.py` (+ `config/governance/advisory-routing-retention.toml`) so the routing-WI
population stays bounded.

**Area 2 — HYG-065 coverage recalibration.** Update the doctor backlog-health check (`doctor.py`) so
'uncovered by PAUTH' is reported as normal for unapproved/future WIs per the approval-state model, and WARN
fires only when a WI in an implementation-active state lacks PAUTH coverage. Update
`session_self_initialization.py` so the startup-disclosure backlog metric reflects real actionable work
rather than the orphan-WARN inflation.

**Area 3 — HYG-060 IPA reorg.** Move the ~66 stale reports into CODEX-INSIGHT-DROPBOX/ and the ~10
scratch/render dirs to `archive/` (preserving provenance per archive-not-delete) with an explicit
file→destination move manifest at `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md`;
refresh `.claude/rules/prompt-organize-reports-in-dropbox.md`'s allowlist (narrative-artifact-approval packet
under `.groundtruth/formal-artifact-approvals/`) to the post-Cursor filenames that actually exist.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-18 changes are in-root under `E:\GT-KB\` — the router +
harvest scripts under `scripts/`, the doctor + startup-init in the in-root `groundtruth-kb/src/groundtruth_kb/`
and `scripts/` trees, the organize rule under `.claude/rules/`, the report/render moves within
`independent-progress-assessments/` and `archive/` (both in-root), the move manifest under
`independent-progress-assessments/`, the approval packet under `.groundtruth/formal-artifact-approvals/`,
retention config under `config/governance/`, and this bridge file under `E:\GT-KB\bridge\`. The cluster
relocates reports within the in-root tree, touches no `applications/` subtree, and writes no out-of-root
artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-STANDING-BACKLOG-001` + `SPEC-DA-HARVEST-INCLUSION` + `GOV-15` (HYG-015) | test: each closed routing WI's report is DA-harvested first; the bulk-close runs only via kb-batch dry-run + GOV-15; the router age-out bounds new routing WIs; the routing-WI share of the backlog drops sharply |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (HYG-065) | test: the backlog-health check does NOT warn on an unapproved/future WI lacking PAUTH; it DOES warn on an implementation-active WI lacking PAUTH; the 930-warn count collapses to the genuine cases |
| `GOV-SESSION-SELF-INITIALIZATION-001` (HYG-065) | test: the startup-disclosure backlog count reflects actionable work, not orphan-WARN inflation |
| isolation/organize rule (HYG-060) | test: the IPA root contains only the allowlisted guides/logs after the reorg; the refreshed organize rule's allowlist names files that exist; every moved report is present under dropbox/`archive/` and listed in the move manifest (provenance preserved, nothing deleted) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. **Area 1:** all 765 reports DA-harvested; routing WIs >60 days bulk-closed (harvest-first, GOV-15-gated);
   the router has an age-out; the backlog's routing-WI share drops from ~75% to a bounded level.
2. **Area 2:** the backlog-health check warns only for implementation-active uncovered WIs; the 930-warn
   count collapses; the startup metric is accurate.
3. **Area 3:** the IPA root is allowlist-only; the organize rule names existing files (refresh packet under
   `.groundtruth/formal-artifact-approvals/`); moved reports retain provenance under dropbox/`archive/` and
   are listed in the `fab-18-ipa-reorg-move-manifest.md` manifest (nothing deleted).
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-18-backlog-dignity-003.md` with a matching `REVISED` line inserted at the top of
`bridge/INDEX.md`; append-only. The DA-harvest-before-close discipline preserves the advisory evidence in the
DA before its routing WI is closed. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until
Loyal Opposition records `GO`.

## Backlog Visibility

FAB-18 is WI-4430 under `GOV-STANDING-BACKLOG-001`. The bulk-close of routing WIs is a GOV-15-gated,
kb-batch-dry-run, DA-harvest-first operation over the inventory of routing WIs older than 60 days — not a
silent mass close; each closure carries its harvested DA evidence. The IPA reorg is archive-not-delete with
the move manifest as its provenance inventory. The formal-artifact-approval packet governs the organize-rule
edit.

## Risk and Rollback

- **Risk — bulk-close loses an advisory still needing action:** every routing WI is DA-harvested before
  close; close is append-only (re-openable) and GOV-15-gated via kb-batch dry-run. **Rollback:** re-open the
  WI; the report + DA row remain.
- **Risk — recalibration hides a real uncovered implementation-active WI:** the new WARN fires precisely for
  that case; only unapproved/future WIs are de-warned. **Rollback:** revert the doctor check.
- **Risk — IPA reorg moves a needed file:** archive-not-delete with the move manifest preserves every file;
  nothing is deleted. **Rollback:** move files back per the manifest.

## Recommended Implementation Routing

**Opus/Codex for Areas 1–2** (the kb-batch bulk-close + the doctor/startup recalibration are governance-
sensitive); **cheap-model-draftable for Area 3** (the file reorg + rule-allowlist refresh, with the
narrative packet for the rule edit) once GO'd.

## Recommended Commit Type

`fix:` — drains the advisory-routing flood, recalibrates the backlog-health/startup metrics, and
reorganizes the IPA root, with `feat:`-class additions (the router age-out + retention config).
