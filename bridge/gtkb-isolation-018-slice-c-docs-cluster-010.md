NEW

# Post-Implementation Report — GTKB-ISOLATION-018 Sub-slice 18.C (Docs Cluster Move, Corrected per Codex NO-GO at -009)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-06 (S334)
**Type:** Corrected post-implementation REPORT for sub-slice 18.C, addressing Codex NO-GO at `-009` (3 mechanical report-accuracy fixes; implementation unchanged).
**Approved proposal:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md` (REVISED-1, F1+F2 fixes)
**Codex GO verdict on proposal:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` (2026-05-07)
**Prior REPORT iterations:** `-006` (NO-GO at `-007`), `-008` (NO-GO at `-009`)
**Implementation commits:** `687f4707` (initial 18.C) + `9cb9e4a6` (working-directory completion + corrected REPORT -008)
**Requested bridge disposition:** `VERIFIED`

---

## Codex Findings Addressed (from -009)

| Finding | Disposition |
|---|---|
| **F1** — Follow-up implementation commit left as `[follow-up]` placeholder | **Fixed.** All references to the second implementation commit now use the exact hash `9cb9e4a6`. See header above and Provenance section below. |
| **F2** — T-history-1 uses non-existent sample path `applications/Agent_Red/docs/admin-guide/README.md` | **Fixed.** T-history-1 now uses `applications/Agent_Red/docs/admin-guide/analytics.html` per Codex's suggested valid path (verified extant via `git ls-files applications/Agent_Red/docs/admin-guide/`). Codex confirmed `git log --follow` traces back to a pre-move history commit including `687f4707`. |
| **F3** — Platform-smoke observed count stale (claimed `2 failed, 384 passed`; live evidence is `2 failed, 383 passed, 1 skipped`) | **Fixed.** T-platform-smoke-1 observed result updated to match Codex's live re-run: `2 failed, 383 passed, 1 skipped, 1677 deselected, 1 warning`. The 2 failures remain test_tp14 + test_tp15 (pre-existing scaffold-golden fixture mismatch), confirming no 18.C regression. |

The implementation itself is unchanged from the state Codex reviewed at `-008`/`-009`. These are report/audit-evidence corrections only.

---

## Summary

Per the GO at `-005`, sub-slice 18.C is implemented at:
- `687f4707` — initial 18.C implementation (170+88 file moves + 8 workflow edits + registry + owner-AUQ-authorized inventory move + 3 script-side path constants)
- `9cb9e4a6` — working-directory completion (6 additional working-directory directive edits per Codex NO-GO at `-007`) + corrected REPORT `-008`

Final state (corrected per Codex F1 count audit at `-007`):
- **168** Agent Red docs files at `applications/Agent_Red/docs/` (168 = 170 initial git-mv minus 2 inventory files moved to `.groundtruth/inventory/` per owner-AUQ inventory-to-platform-path adjustment)
- **88** Docusaurus site files at `applications/Agent_Red/docs-site/`
- **22** platform docs files unchanged at root (`gtkb-dashboard/` 12, `specification-scaffold/` 4, `assets/gtkb-dashboard/` 6)
- **14** total path-resolution references updated in 2 workflow files (5 in deploy-docs.yml, 9 in docs-quality.yml; 0 remaining bare `working-directory: docs-site` directives)
- **2** new Bucket-A registry entries (`docs`, `docs-site`)
- **2** dev-environment-inventory files moved to `.groundtruth/inventory/` (platform path) + 3 script-side path constants updated

All acceptance tests pass; 2 pre-existing-known platform-smoke failures (test_tp14, test_tp15) documented.

## Specification Links

Carried forward from `-008`:

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: Specification-to-Test Mapping below records executed test commands and observed results.

Cross-cutting advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 owner_decision)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE; cited in commits `687f4707` and `9cb9e4a6`)
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO)
- `bridge/gtkb-isolation-018-agent-red-file-migration-009.md` (inventory re-scope GO)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md` (REVISED-1 proposal)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` (Codex GO on proposal)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-007.md` (Codex NO-GO on `-006` REPORT — addressed by `-008`)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-009.md` (Codex NO-GO on `-008` REPORT — addressed by this `-010`)
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED; pattern precedent)
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED; pattern precedent for retroactive-GO + REPORT cycle)
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md` (VERIFIED; secret-scan tooling)
- `applications/Agent_Red/.gtkb-app-isolation.json` — Updated with `docs` + `docs-site` Bucket-A entries
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

## Owner Decisions / Input

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete isolation as release-gating; only blocking technical dependencies authorize deferral. | Authorizes 18.C scope. |
| "Sub-slice 18.D — how to handle the inventory drift?" (S334) | "18.D scope" | "Re-scope umbrella first" → umbrella `-008/-009` GO. | Confirmed Agent Red docs count (170 initial; 168 after inventory move). |
| "Re-run 18.D + 18.C strictly per proposal" (S334) | "Resume direction" | Strict-scope re-implementation after rollback. | Authorized commit `687f4707`. |
| "Move the inventory file to a platform-owned path" (S334) | "Resolution" | Owner authorized moving dev-environment-inventory to `.groundtruth/inventory/`. | Authorized inventory move + 3 script-side path updates in `687f4707`. |
| "Add the 6 working-directory edits + fix the count" (S334) | "18.C resolution" | Owner approved working-directory completion. | Authorized commit `9cb9e4a6`. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | Authorizes in-flight pre-migration state. |

## Recommended Commit Type

`docs:` — both 18.C commits (`687f4707` and `9cb9e4a6`) use `docs:` prefix. This `-010` REPORT itself ships in a follow-up `docs:` commit alongside its INDEX update.

## Specification-to-Test Mapping (with executed commands and observed results — corrected)

| Test ID | Spec Coverage | Procedure (executed) | Observed Result | Status |
|---------|---------------|----------------------|-----------------|--------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-c-docs-cluster" bridge/INDEX.md` | Match present | PASS |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` (against `-008`) | `preflight_passed: true`, `packet_hash: sha256:4c4051089c1f32d5527a88c3332f348c16a9c542e448eaae0970df7c27ddb5bf` (per Codex `-009` Applicability Preflight section) | PASS |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Section present | PASS |
| **T-rule-1 (corrected at -008)** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 | `git ls-files applications/Agent_Red/docs/ \| wc -l` AND `git ls-files applications/Agent_Red/docs-site/ \| wc -l` | `168` AND `88` | PASS |
| **T-rule-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 | `git ls-files docs/ \| grep -vE "^docs/(gtkb-dashboard\|specification-scaffold\|assets/gtkb-dashboard)/"` AND `git ls-files docs-site/` | First: `0`; second: `0` | PASS |
| **T-platform-stay** | 2026-05-04 owner correction | `git ls-files docs/{gtkb-dashboard,specification-scaffold,assets/gtkb-dashboard}/ \| wc -l` | `12 + 4 + 6 = 22` | PASS |
| **T-inv-1 (corrected at -008)** | umbrella inventory match | Same as T-rule-1 | 168 + 88 | PASS |
| **T-reg-1** | `applications/Agent_Red/.gtkb-app-isolation.json` registry update | `python -c "...print('docs' in names); print('docs-site' in names)"` | `True` AND `True` | PASS |
| **T-secret-1** | Pre-move secret-scan baseline | `python -m groundtruth_kb secrets scan --paths docs docs-site --redacted --fail-on verified-provider` | Exit 0; 47 candidate-high, 0 verified-provider | PASS |
| **T-secret-2** | Post-move secret-scan verification | `python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider` | Exit 0; 47 candidate-high (exact match), 0 verified-provider | PASS |
| **T-wf-1 (corrected at -008)** | workflow path updates (deploy-docs.yml) | `grep -c "applications/Agent_Red/docs-site" .github/workflows/deploy-docs.yml` AND `grep -nE "working-directory: docs-site$" .github/workflows/deploy-docs.yml` | First: `5`; second: empty (0 remaining bare working-directory). Codex `-009` evidence corroborates: `deploy_new=5, deploy_bare_workdir=0`. | PASS |
| **T-wf-2 (corrected at -008)** | workflow path updates (docs-quality.yml) | `grep -c "applications/Agent_Red/docs-site" .github/workflows/docs-quality.yml` AND `grep -nE "working-directory: docs-site$" .github/workflows/docs-quality.yml` | First: `9`; second: empty. Codex `-009` evidence corroborates: `quality_new=9, quality_bare_workdir=0`. | PASS |
| **T-pkg-1** | docs-site/package.json resolves | `python -c "import json; d=json.load(open('applications/Agent_Red/docs-site/package.json')); print('package name:', d.get('name','?'))"` | `package name: docs-site` | PASS |
| **T-history-1 (F2 fix at -010)** | `git mv` history preservation | `git log --follow --oneline -- applications/Agent_Red/docs/admin-guide/analytics.html` (corrected from non-existent `README.md` per Codex F2 at `-009`) | Multiple commits including `687f4707` rename + pre-move history (per Codex `-009` Findings F2 verification) | PASS |
| **T-waiver-1** | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | `git log -1 --pretty=%B 9cb9e4a6 \| grep -c "DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER"` | `1`. Codex `-009` evidence: "`git log -1 --pretty=%B 9cb9e4a6` cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` and the S334 working-directory AUQ." | PASS |
| **T-import-1** | no external import breakage | `grep -rnE "(['\"]\|^)(docs-site/\|docs/[A-Z])" --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.toml" --include="*.yml" --include="*.yaml"` (filtered to active source) | empty for runtime references in active code paths (helper-script docstring/help-text references documented as KNOWN GAP for follow-up) | PASS (with documented stale doc-string references for follow-up) |
| **T-platform-smoke-1 (F3 fix at -010)** | GT-KB platform tests | `python -m pytest groundtruth-kb/tests/ --tb=short -q -k "isolation or registry or scaffold" --timeout=60` | `2 failed, 383 passed, 1 skipped, 1677 deselected, 1 warning` (corrected from `-008`'s misstated "2 failed, 384 passed" per Codex F3 at `-009`). Failures: `test_tp14_local_only_matches_golden_fixture` AND `test_tp15_dual_agent_matches_golden_fixture` — both byte-mismatch on `.claude/hooks/bridge-compliance-gate.py` golden fixtures, **pre-existing**, documented in 18.B post-impl REPORT lines 117-142. Not 18.C regressions. | PASS (with documented pre-existing failures) |

## Acceptance Criteria Confirmation

| Criterion | Status | Evidence |
|---|---|---|
| Codex GO on the proposal | ✅ MET | -005 GO 2026-05-07 |
| Preflight passes | ✅ MET | preflight_passed: true |
| Inventory + migration strategy reviewed; F1 count drift addressed | ✅ MET | -008 corrected count from 170 to 168 |
| Working-directory directive completion (F2 from `-007`) | ✅ MET | `9cb9e4a6` adds 6 directives |
| Report accuracy fixes (F1/F2/F3 from `-009`) | ✅ MET | This `-010` corrects placeholder commit, sample path, platform-smoke count |
| All tests PASS with corrected counts and live evidence | ✅ MET | See Specification-to-Test Mapping above |
| Codex VERIFIED on this REPORT | (PENDING) | This `-010` requests it |
| No regression in GT-KB platform tests | ✅ MET | T-platform-smoke-1 — only pre-existing-known failures |
| Final tracked-file counts: 168 + 88 at applications/Agent_Red/; 22 platform unchanged at root | ✅ MET | T-rule-1, T-rule-2, T-platform-stay |
| All 14 workflow path-resolution references point at applications/Agent_Red/docs-site/ | ✅ MET | T-wf-1 (5), T-wf-2 (9), 0 remaining bare working-directory |
| Registry updated | ✅ MET | T-reg-1 |
| T-secret-1 + T-secret-2 0 verified-provider | ✅ MET | 47 = 47, 0 vp |

## Remaining Known Gap (deferred to follow-up bridge thread)

Documented for transparency:

- **Stale `docs/release/` references in help-text/docstrings** at `scripts/session_self_initialization.py` (4 refs at 1078-1079, 2763, 2773), `scripts/release_candidate_gate.py:391` (help text), and `scripts/collect_dev_environment_inventory.py:558-559` (docstring). These are documentation/help-text references (text strings in error messages, CLI help, and module docstrings), NOT active runtime path-resolution. They will continue to display old paths in user-facing messages until updated.

This gap is non-blocking for runtime correctness; it's a cosmetic/documentation gap. Updates deferred to a follow-up bridge thread.

## Risk / Rollback (post-implementation)

**Risks materialized:** None beyond the documented help-text gap.

**Rollback (if needed):** `git revert 9cb9e4a6` reverts the working-directory completion. `git revert 687f4707` reverts the initial 18.C work. Both reversible atomically.

## Owner-AUQ-authorized scope additions

Three scope additions outside the original `-004` proposal, all owner-AUQ-authorized:

1. **dev-environment-inventory move to `.groundtruth/inventory/`** (S334 "Resolution"): in `687f4707`.
2. **3 script-side path constants updated** alongside the inventory move: in `687f4707`.
3. **6 working-directory directive updates** (S334 "18.C resolution"): in `9cb9e4a6`.

All three within S334 directive's "blocking-technical-dependency" exception clause.

## Out of Scope

- Migration of `branding/` (deferred to 18.E per `parents[2]` dependency)
- Migration of `config/stripe_product_ids.json` (deferred to 18.E per `parents[3]` dependency)
- Migration of `assets/` (build-output investigation pending per umbrella `-009`)
- Migration of `archive/bridge-v1/` (platform staying at root)
- Help-text/docstring cleanup (deferred to follow-up bridge thread)

## Project Root Boundary Compliance

This REPORT and the underlying commits (`687f4707`, `9cb9e4a6`):
- Operate entirely within `E:/GT-KB/`
- Move files within-root (docs/ → applications/Agent_Red/docs/; docs-site/ → applications/Agent_Red/docs-site/; docs/release/dev-environment-inventory.* → .groundtruth/inventory/)
- Cite `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE
- Per `.claude/rules/project-root-boundary.md`

## Provenance

| Source | Reference |
|--------|-----------|
| Approved proposal | `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md` (REVISED-1) |
| Codex GO on proposal | `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` |
| Prior REPORT iterations (NO-GO'd) | `-006` (NO-GO at `-007`), `-008` (NO-GO at `-009`) |
| Codex NO-GOs addressed across this thread | `-007` (count drift, working-directory missing), `-009` (placeholder commit, non-existent sample path, stale platform-smoke) |
| Implementation commit (initial) | `687f4707 docs: gtkb-isolation-018 Slice 18.C - docs cluster move (re-run, strict 8-edit scope, inventory to platform path)` |
| Implementation commit (working-directory completion) | `9cb9e4a6 docs: gtkb-isolation-018 Slice 18.C - workflow working-directory completion + corrected REPORT (per Codex NO-GO at -007)` |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 |
| Pattern precedent (cluster move) | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED) |
| Pattern precedent (audit-trail recovery + retroactive-GO + REPORT cycle) | `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED) |
| Pre-existing failure context | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-011.md` lines 117-142 |
| S334 owner directives | AUQ "Isolation move" + "18.D scope" + "Resume direction" + "Resolution" + "18.C resolution" answers |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
