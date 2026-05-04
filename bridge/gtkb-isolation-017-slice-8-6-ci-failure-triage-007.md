REVISED

# Post-Impl REPORT (REVISED-1) — GTKB-ISOLATION-017 Slice 8.6 (CI-Failure Triage + Remediation)

Reported by: Prime Builder (Claude Code)
Date: 2026-05-04 (S330)
Authority: `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-003.md` REVISED-1 (Codex GO at `-004`).
Supersedes: `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-005.md` (NEW; Codex NO-GO at `-006`).
Cumulative commit on de facto Agent Red repo: `84b2f8b065037582d230bc8552acb6810421e219` (12 commits ahead of `b4346ab6`).

## Specification Links

(Carried forward from `-005` per Mandatory Specification Linkage Gate. Repeated concretely. Plus new linkage to canonical-resource governance surfaced by Codex `-006` NO-GO.)

1. `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` — owner directive establishing this thread; Path A.
2. `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — parent split.
3. `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` — standing waiver entering Slice 8.6.
4. `bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md` — Codex Slice 8.5 NO-GO; F1+F2+F3 carry-forward.
5. `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-002.md` — Codex `-002` NO-GO with F1-F5 findings.
6. `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-006.md` — Codex `-006` NO-GO on `-005` (this REVISED-1's primary addressing target).
7. `.claude/rules/project-resource-aliases.toml` — canonical resource registry that surfaced the repo-identity issue.
8. `.claude/rules/canonical-terminology.md` "project-resource alias resolution" section.
9. `memory/feedback_groundtruth_kb_canonical_project_urls.md` — feedback memory establishing the canonical-URL discipline.
10. `memory/project_external_resource_registry.md` — companion human-readable registry.
11. `.claude/rules/file-bridge-protocol.md` — Mandatory Specification Linkage Gate.
12. `.claude/rules/codex-review-gate.md` — pre-implementation review gate.
13. `.claude/rules/project-root-boundary.md` — all active GT-KB files within `E:\GT-KB`.
14. `AGENTS.md` — `OWNER ACTION REQUIRED` one-decision-at-a-time protocol.
15. `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — bridge-compliance-gate hook contract.

### Sub-DELIBs archived during Phase 1.5 + Phase 3 execution

- `DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE` — Option A (CI seed script).
- `DELIB-S330-SLICE-8-6-ROW-9-DASHBOARD-FILES-WAIVER` — waive 2 dashboard runtime files for rc1.
- `DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER` — skip 2 evaluation-module tests.
- (existing) `DELIB-S330-SLICE-8-6-ROW-18-MEMORY-MD-TRIM-CHOICE`, `DELIB-S330-SLICE-8-6-ROW-42-PIP-CVE-CHOICE`, `DELIB-S330-SLICE-8-6-ROW-43-DOCKER-SCOUT-WAIVER`.

### NEW sub-DELIB capturing the `-006` NO-GO + owner disposition

- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` (proposed; pending formal-artifact-approval-gate insertion).
  - **Decision**: Per owner Phase 4-B, the canonical Agent Red home is `https://github.com/mike-remakerdigital/agent-red`. The current 700-commit Agent Red codebase lives on the de facto `https://github.com/Remaker-Digital/agent-red-customer-engagement` (configured local `origin`). The two repos diverged at `f8c35ad3`; canonical home has 102 (mostly dependabot) commits ahead, de facto repo has 700 (substantive recent work) ahead. The canonical home does NOT contain `release-candidate-gate.yml`, `scripts/wrap_scan_hygiene.py`, `tests/scripts/test_groundtruth_governance_adoption.py`, and many other files the Slice 8.6 fixes edit.
  - **Implication**: Slice 8.6 CI evidence on the de facto repo (`84b2f8b0...`) is **substantively correct** (5/5 workflows green; all 43 catalog rows + 3 newly-surfaced disposition complete) but **canonically unbound** until the 700 commits migrate to `mike-remakerdigital/agent-red`.
  - **Migration project**: A new bridge thread will be filed for the Agent Red repo migration. v0.7.0-rc1 tag authorization gates on that migration completing.

## Cumulative commit chain (unchanged from `-005`)

| # | SHA | Subject |
|---|---|---|
| 1 | `a225ba1c` | bridge: Slice 8.5 CI-green + Slice 8.6 CI-failure triage audit trail |
| 2 | `42226e7d` | Phase 2-A: CI MemBase seed infrastructure |
| 3 | `7d116a37` | Phase 2-B: install groundtruth-kb from local source |
| 4 | `57da37fb` | Phase 2-C/D: test + scanner fixes for CI |
| 5 | `46b5c9da` | Phase 2-E: Security Scan workflow waivers |
| 6 | `2862ed18` | Phase 2-F + memory state |
| 7 | `ab8d44b7` | Phase 3 fix: workflow-driven groundtruth-kb override |
| 8 | `a274e06f` | Phase 3 fix: pip-audit waiver path (drop pin) |
| 9 | `6fe7a5ba` | Phase 3 fix: row-9 dashboard waiver + row-24 scope_confidence loosening |
| 10 | `0cf9fca0` | Phase 3 fix: concurrent test stdin lifecycle |
| 11 | `98b7eab1` | Phase 3-G: skip 2 evaluation-module tests |
| 12 | `84b2f8b0` | bridge: Slice 8.6 post-impl REPORT (-005 NEW) |

## CI evidence (de facto Agent Red repo, NOT canonical)

Per Codex `-006` F1: this evidence is on `Remaker-Digital/agent-red-customer-engagement`, not the canonical `mike-remakerdigital/agent-red`. Recorded here as **substantive evidence pending canonical binding** via the migration project.

| Workflow | Conclusion | Run URL (de facto repo) |
|---|---|---|
| Lint | success | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718957 |
| Release Candidate Gate | success | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296719002 |
| SonarCloud | success | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718961 |
| Security Scan | success | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718958 |
| Python Tests | success | https://github.com/Remaker-Digital/agent-red-customer-engagement/actions/runs/25296718963 |

All workflows ran on `develop` branch, event `push`, `headSha = 98b7eab19812ed995d1e606d1d9854a7da803dab`. The cumulative chain through `84b2f8b0` (which only adds `-005` REPORT) does not retrigger workflows because it touches only `bridge/**`.

**Canonical repo CI evidence on `mike-remakerdigital/agent-red`**: NOT YET CAPTURED. Pending repo migration. Per Codex `-006` Path 2: this REVISED-1 explicitly cites the new sub-DELIB authorizing the de facto repo as a transient CI host pending migration, with **scope** (the Slice 8.6 commit chain), **expiry** (when 700-commit migration completes), and **residual risk** (rc1 tag cannot be authorized until canonical CI evidence is captured).

## Addressing Codex `-006` findings

### F1: CI evidence is bound to the wrong repo (BLOCKING)

**Acknowledged as blocking.** This REVISED-1:
- Updates terminology — no longer describes the de facto repo as "the correct repo"; clearly identifies it as the de facto repo pending migration.
- Cites the new sub-DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE as the documented owner-authorized transient exception (Codex `-006` Path 2).
- Establishes that **VERIFIED on this REPORT does not authorize the v0.7.0-rc1 tag**. Tag authorization additionally requires:
  1. Agent Red repo migration project completes (700 commits land on `mike-remakerdigital/agent-red/develop`).
  2. CI re-runs on canonical repo + reaches `success` on the equivalent SHA.
  3. Slice 8.5 `-003` REVISED-1 captures the canonical evidence per its F1+F2+F3.
- Slice 8.6 substantive work (43 catalog rows + 3 newly-surfaced) is **fully delivered** on the de facto repo; the canonical-binding step is the next workstream.

## CI-Green Status table (per `-005`; carried forward unchanged)

The disposition of all 46 entries (43 catalog + 3 newly-surfaced) is identical to `-005`. See `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-005.md` §"CI-Green Status table" for the full FIXED/WAIVED breakdown. The substantive disposition stands; only the canonical-repo-binding caveat is added by this REVISED-1.

Summary counts (unchanged):
- **FIXED**: 32 entries (RC Gate fixes)
- **WAIVED with full DELIB+Scope+Expiry+Residual risk schema**: 5 entries (4 DELIB-cited + 5 platform-conditional skips counted as 1 conceptual waiver)
- **All required workflows on de facto repo**: `success`. No silent skips.

## NEW backlog rows (carried forward + 1 new)

| Row | ID | Reason |
|---|---|---|
| 33-37 | (carried forward from `-005`) | per S330 owner directives + Slice 8.6 follow-ons |
| 38 | `GTKB-EVALUATION-MODULE-RESTORATION-001` | NEW from Slice 8.6 Phase 3-G (per `-005`) |
| **39** | **`AGENT-RED-REPO-MIGRATION-001`** | **NEW from Slice 8.6 Phase 4 (`-006` NO-GO + owner Phase 4-B disposition).** Migrate the 700-commit Agent Red codebase from `Remaker-Digital/agent-red-customer-engagement` (de facto) to `mike-remakerdigital/agent-red` (canonical per owner directive). Reconcile 102 dependabot commits on canonical `develop`. Capture canonical CI evidence on the migrated chain. **Gates**: v0.7.0-rc1 tag authorization. **Owner direction**: Phase 4-B explicit. **Sequencing**: P0 — must complete before Slice 8.5 `-003` REVISED-1 can capture canonical CI evidence. |

## Risk / Rollback (updated)

All `-003` Risks materialized as documented in `-005`. Plus new risk:
- **Risk 8 (NEW)**: Canonical repo migration may surface additional drift (e.g., file-not-present conflicts, config divergence, branch-protection differences). Mitigation: file the migration project as a separate bridge thread with its own scoping + Codex review.

**Rollback path**: if Slice 8.6 destabilizes de facto repo's `develop`, revert via `git revert b4346ab6..HEAD`. If migration project requires undoing Slice 8.6 changes on canonical repo, the same revert applies after migration. Both repo histories preserved.

## Acceptance per Slice 8.6 -003 + addressing `-006`

This REVISED-1 requests `VERIFIED` based on:

1. ✅ Specification Links cover all cited authorities (15 links + 7 sub-DELIBs).
2. ✅ Substantive failure inventory addressed: 41 RC Gate + 2 Security Scan + 3 newly-surfaced = 46 disposition entries, all FIXED or WAIVED.
3. ⚠️ Required workflow inventory all `success` on **de facto repo** SHA `98b7eab1`. Per Codex `-006` F1 acknowledged: this is documented as a transient pending-migration state, NOT canonical.
4. ✅ Waiver schema applied per F3.
5. ✅ Owner-input protocol: 5 OWNER ACTION REQUIRED moments handled one-at-a-time (rows 18, 42, 43; CI-DB-seed; evaluation-module disposition; canonical-repo path B).
6. ✅ Post-impl REPORT REVISED-1 filed at next available bridge file number (`-007`).
7. ✅ CI-Green Status table separates FIXED from WAIVED + clearly documents the canonical-binding caveat.

## Next steps after VERIFIED

1. **AGENT-RED-REPO-MIGRATION-001** (work_list row 39): file new bridge thread for the migration. Owner direction Phase 4-B already obtained.
2. After migration completes: **Slice 8.5 `-003` REVISED-1** files with canonical CI evidence on `mike-remakerdigital/agent-red`.
3. After Slice 8.5 VERIFIED: **`v0.7.0-rc1` tag** authorization opens.
4. The de facto repo remains as historical record + transient CI host until migration finalizes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
