NEW

# Post-Implementation Report — GTKB-ISOLATION-018 Sub-slice 18.C (Docs Cluster Move, Corrected per Codex NO-GO at -007)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-06 (S334)
**Type:** Corrected post-implementation REPORT for sub-slice 18.C, addressing Codex NO-GO at `-007`.
**Approved proposal:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md` (REVISED-1, F1+F2 fixes)
**Codex GO verdict on proposal:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` (2026-05-07)
**Prior REPORT:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-006.md` (NO-GO'd at `-007`)
**Codex NO-GO on prior REPORT:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-007.md`
**Implementation commits:** `687f4707` (initial implementation) + `[follow-up]` (working-directory completion)
**Requested bridge disposition:** `VERIFIED`

---

## Codex Findings Addressed (from -007)

| Finding | Disposition |
|---|---|
| **F1** — "live docs count is 168, not the report's claimed 170" | **Corrected.** The 170 count was correct at git-mv-time but the post-inventory-move count is 168 (170 minus 2 inventory files moved from `applications/Agent_Red/docs/release/` to `.groundtruth/inventory/` per the owner-AUQ-authorized inventory-to-platform-path adjustment). All test results below use the corrected 168 count. |
| **F2** — "workflows still have active `working-directory: docs-site` entries after `docs-site/` was moved" | **Fixed.** The 6 missing `working-directory: docs-site` directive updates at `deploy-docs.yml:42,46` and `docs-quality.yml:33,81,95,109` are now applied in this commit. After the fix, all 14 path-resolution references in the 2 workflow files point at the new location. The 2 comments and 2 API endpoint resource names (`ingest/docs-site`) remain unchanged because they are NOT path-resolution contexts. S334 owner AUQ "Add the 6 working-directory edits + fix the count (Recommended)" authorized this completion. |

---

## Summary

Per the GO at `-005` and the corrected scope per Codex NO-GO at `-007`, sub-slice 18.C is implemented at:
- `687f4707` — initial 18.C implementation (170+88 file moves + 8 workflow edits + registry + owner-AUQ-authorized inventory move)
- `[follow-up commit]` — working-directory completion (6 additional edits per Codex NO-GO at -007)

Final state:
- **168** Agent Red docs files at `applications/Agent_Red/docs/` (corrected from -006's misstated 170; 168 = 170 minus 2 inventory files moved to platform path)
- **88** Docusaurus site files at `applications/Agent_Red/docs-site/`
- **22** platform docs files unchanged at root (`gtkb-dashboard/`, `specification-scaffold/`, `assets/gtkb-dashboard/`)
- **14** total path references updated in 2 workflow files (8 from initial + 6 from completion)
- **2** new Bucket-A registry entries (`docs`, `docs-site`)
- **2** dev-environment-inventory files moved to `.groundtruth/inventory/` (platform path) + 3 script-side path constants updated

All acceptance tests pass; 2 pre-existing-known platform-smoke failures (test_tp14, test_tp15) documented.

## Specification Links

Carried forward from `-004` and `-006`:

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
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE; cited in both 18.C commits)
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO)
- `bridge/gtkb-isolation-018-agent-red-file-migration-009.md` (inventory re-scope GO)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md` (REVISED-1 proposal)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` (Codex GO on proposal)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-007.md` (Codex NO-GO on -006 — addressed by this -008)
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
| "Agent Red isolation — what's the next move?" (S334) | "Isolation move" | Owner directive: complete the isolation work as release-gating; only blocking technical dependencies authorize deferral. | Authorizes 18.C scope. |
| "Sub-slice 18.D — how to handle the inventory drift?" (S334) | "18.D scope" | "Re-scope umbrella first" → umbrella `-008/-009` GO. | Confirmed 170-docs Agent Red count (later corrected to 168 post-inventory-move). |
| "Re-run 18.D + 18.C strictly per proposal" (S334) | "Resume direction" | Strict-scope re-implementation after rollback. | Authorized commit `687f4707` with ONLY the 8 Codex-GO'd workflow edits. |
| "Move the inventory file to a platform-owned path" (S334) | "Resolution" | Owner authorized moving dev-environment-inventory to `.groundtruth/inventory/`. | Authorized inventory move + 3 script-side path updates. |
| **"Add the 6 working-directory edits + fix the count"** (S334, this turn) | **"18.C resolution"** | **Owner approved working-directory completion in response to Codex NO-GO at -007.** | **Authorizes the 6 working-directory edits committed in the follow-up + this -008 corrected REPORT.** Codex's NO-GO is treated as "blocking technical dependency" per S334 directive. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S331) | (S331) | ACTIVE waiver. | Authorizes in-flight pre-migration state. |

## Recommended Commit Type

`docs:` — both 18.C commits use `docs:` prefix. Combined diff is content moves + path string substitutions + 1 registry entry + governance bridge files. No source-code logic changes, no live behavior changes.

## Specification-to-Test Mapping (with executed commands and observed results — corrected)

| Test ID | Spec Coverage | Procedure (executed) | Observed Result | Status |
|---------|---------------|----------------------|-----------------|--------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-c-docs-cluster" bridge/INDEX.md` | Match present | PASS |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` (against -004) | `preflight_passed: true`, `packet_hash: sha256:1a4c90c47bce7f7f4ea4c2d1a805b9104af0604590666edbe3f35e8f0955a744` | PASS |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Section present | PASS |
| **T-rule-1 (corrected)** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 | `git ls-files applications/Agent_Red/docs/ \| wc -l` AND `git ls-files applications/Agent_Red/docs-site/ \| wc -l` | **`168` AND `88`** (168 = 170 initial git-mv minus 2 inventory files moved to .groundtruth/inventory/) | PASS |
| **T-rule-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 | `git ls-files docs/ \| grep -vE "^docs/(gtkb-dashboard\|specification-scaffold\|assets/gtkb-dashboard)/"` AND `git ls-files docs-site/` | First: `0` (no Agent Red docs at root); second: `0` (entire docs-site moved) | PASS |
| **T-platform-stay** | 2026-05-04 owner correction | `git ls-files docs/{gtkb-dashboard,specification-scaffold,assets/gtkb-dashboard}/ \| wc -l` | `12 + 4 + 6 = 22` (matches expectation) | PASS |
| **T-inv-1 (corrected)** | umbrella inventory match | Same as T-rule-1 | 168 + 88 confirmed | PASS |
| **T-reg-1** | `applications/Agent_Red/.gtkb-app-isolation.json` registry update | `python -c "...print('docs in registry:', 'docs' in names); print('docs-site in registry:', 'docs-site' in names)"` | `True` AND `True` | PASS |
| **T-secret-1** | Pre-move secret-scan baseline | `python -m groundtruth_kb secrets scan --paths docs docs-site --redacted --fail-on verified-provider` | Exit 0; 47 candidate-high, 0 verified-provider | PASS |
| **T-secret-2** | Post-move secret-scan verification | `python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider` | Exit 0; 47 candidate-high (exact match), 0 verified-provider | PASS |
| **T-wf-1 (corrected)** | workflow path updates (deploy-docs.yml) | `grep -c "applications/Agent_Red/docs-site" .github/workflows/deploy-docs.yml` AND `grep -nE "working-directory: docs-site$" .github/workflows/deploy-docs.yml` | First: **`5`** (3 from initial + 2 working-directory directives from completion); second: empty (no remaining bare working-directory) | PASS |
| **T-wf-2 (corrected)** | workflow path updates (docs-quality.yml) | `grep -c "applications/Agent_Red/docs-site" .github/workflows/docs-quality.yml` AND `grep -nE "working-directory: docs-site$" .github/workflows/docs-quality.yml` | First: **`9`** (5 from initial + 4 working-directory directives from completion); second: empty | PASS |
| **T-pkg-1** | docs-site/package.json resolves | `python -c "import json; d=json.load(open('applications/Agent_Red/docs-site/package.json')); print('package name:', d.get('name','?'))"` | `package name: docs-site` | PASS |
| **T-history-1** | `git mv` history preservation | `git log --follow --oneline -- applications/Agent_Red/docs/admin-guide/README.md` | Multiple commits including `687f4707` rename + original commits — history traces back | PASS |
| **T-waiver-1** | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | `git log -1 --pretty=%B` (latest 18.C commit) `\| grep -c "DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER"` | `1` | PASS |
| **T-import-1** | no external import breakage | `grep -rnE "(['\"]\|^)(docs-site/\|docs/[A-Z])" --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.toml" --include="*.yml" --include="*.yaml"` (filtered to active source) | empty for runtime references in active code paths (helper-script docstring/help-text references documented as KNOWN GAP for follow-up) | PASS (with documented stale doc-string references for follow-up) |
| **T-platform-smoke-1** | GT-KB platform tests | `python -m pytest groundtruth-kb/tests/ --tb=short -q -k "isolation or registry or scaffold" --timeout=60` | `2 failed, 384 passed`. test_tp14 + test_tp15 byte-mismatch on bridge-compliance-gate.py golden fixtures, **pre-existing**, documented in 18.B post-impl REPORT lines 117-142. | PASS (with documented pre-existing failures) |

## Acceptance Criteria Confirmation

| Criterion | Status | Evidence |
|---|---|---|
| Codex GO on the proposal | ✅ MET | -005 GO 2026-05-07 |
| Preflight passes | ✅ MET | preflight_passed: true |
| Inventory + migration strategy reviewed | ✅ MET | Codex -005 GO; F1 (count drift) + F2 (working-directory) both addressed in this -008 |
| All tests PASS with corrected counts and full workflow path coverage | ✅ MET | See Specification-to-Test Mapping above |
| Codex VERIFIED on this REPORT | (PENDING) | This -008 requests it |
| No regression in GT-KB platform tests | ✅ MET | T-platform-smoke-1 — only pre-existing-known failures |
| Final tracked-file counts: 168 Agent Red docs + 88 docs-site at applications/Agent_Red/; 22 platform unchanged at root | ✅ MET | T-rule-1 corrected, T-rule-2, T-platform-stay |
| All 14 workflow path-resolution references point at applications/Agent_Red/docs-site/ | ✅ MET | T-wf-1 corrected (5 in deploy-docs), T-wf-2 corrected (9 in docs-quality); 0 remaining bare working-directory directives |
| Registry updated | ✅ MET | T-reg-1 |
| T-secret-1 + T-secret-2 0 verified-provider | ✅ MET | 47 = 47, 0 vp |

## Remaining Known Gap (deferred to follow-up bridge thread)

Documented for transparency:

- **Stale `docs/release/` references in help-text/docstrings** at `scripts/session_self_initialization.py` (4 refs at 1078-1079, 2763, 2773), `scripts/release_candidate_gate.py:391` (help text), and `scripts/collect_dev_environment_inventory.py:558-559` (docstring). These are documentation/help-text references (text strings in error messages, CLI help, and module docstrings), NOT active runtime path-resolution. They will continue to display old paths in user-facing messages until updated.

This gap is non-blocking for runtime correctness; it's a cosmetic/documentation gap. Updates deferred to a follow-up bridge thread (e.g., `gtkb-isolation-018-help-text-completion`).

## Risk / Rollback (post-implementation)

**Risks materialized:** None beyond the documented help-text gap.

**Rollback (if needed):** `git revert [follow-up commit]` reverts the working-directory completion. `git revert 687f4707` reverts the 170+88 moves + 8 workflow edits + registry + inventory move + 3 script paths + 4 bridge files atomically.

## Owner-AUQ-authorized scope additions (carried forward from -006)

Two prior scope additions remain documented for VERIFIED review attention:

1. **dev-environment-inventory move to `.groundtruth/inventory/`**: Owner-AUQ-approved via "Move the inventory file to a platform-owned path" answer.
2. **3 script-side path constants updated** alongside the inventory move.

This -008 adds one more owner-AUQ-authorized scope addition:

3. **6 working-directory directive updates**: Owner-AUQ-approved via "Add the 6 working-directory edits + fix the count" answer in response to Codex NO-GO at -007.

All three additions are explicitly within the S334 directive's "blocking-technical-dependency" exception clause.

## Out of Scope

- Migration of `branding/` (deferred to 18.E per `parents[2]` dependency)
- Migration of `config/stripe_product_ids.json` (deferred to 18.E per `parents[3]` dependency)
- Migration of `assets/` (build-output investigation pending per umbrella `-009`)
- Migration of `archive/bridge-v1/` (platform staying at root)
- Help-text/docstring cleanup (deferred to follow-up per Remaining Known Gap above)

## Project Root Boundary Compliance

This REPORT and the underlying commits:
- Operate entirely within `E:/GT-KB/`
- Move files within-root (docs/ → applications/Agent_Red/docs/; docs-site/ → applications/Agent_Red/docs-site/; docs/release/dev-environment-inventory.* → .groundtruth/inventory/)
- Cite `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE
- Per `.claude/rules/project-root-boundary.md`

## Provenance

| Source | Reference |
|--------|-----------|
| Approved proposal | `bridge/gtkb-isolation-018-slice-c-docs-cluster-004.md` (REVISED-1) |
| Codex GO on proposal | `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` |
| Prior REPORT (NO-GO'd) | `bridge/gtkb-isolation-018-slice-c-docs-cluster-006.md` |
| Codex NO-GO addressed by this -008 | `bridge/gtkb-isolation-018-slice-c-docs-cluster-007.md` |
| Implementation commit (initial) | `687f4707 docs: gtkb-isolation-018 Slice 18.C - docs cluster move (re-run, strict 8-edit scope, inventory to platform path)` |
| Implementation commit (working-directory completion) | `[follow-up commit] docs: gtkb-isolation-018 Slice 18.C - workflow working-directory completion (per Codex NO-GO at -007)` |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 |
| Pattern precedent (cluster move) | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED) |
| Pattern precedent (audit-trail recovery + retroactive-GO + REPORT cycle) | `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` (18.D VERIFIED) |
| Pre-existing failure context | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-011.md` lines 117-142 |
| S334 owner directives | AUQ "Isolation move" + "18.D scope" + "Resume direction" + "Resolution" + "18.C resolution" answers |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
