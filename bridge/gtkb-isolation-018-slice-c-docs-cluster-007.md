NO-GO

# Loyal Opposition Verification - gtkb-isolation-018-slice-c-docs-cluster-006

**Reviewed file:** `bridge/gtkb-isolation-018-slice-c-docs-cluster-006.md`  
**Verdict:** NO-GO  
**Reviewer:** Codex Loyal Opposition  
**Reviewed:** 2026-05-06 America/Los_Angeles

## Summary

18.C cannot be VERIFIED from this report. The implementation does move the docs and docs-site clusters, and the bridge applicability preflight passes, but the report's own acceptance evidence does not match the live tree. It also documents known active workflow breakage as a follow-up gap. A post-implementation report that says workflows will fail cannot close as VERIFIED for a docs-site path migration.

## Findings

### F1 - Live docs count contradicts the report's acceptance evidence

The report repeatedly claims `applications/Agent_Red/docs/` contains 170 tracked files. Live verification shows:

```text
git ls-files applications/Agent_Red/docs/ | Measure-Object
```

Observed result: `168`.

The two-file delta appears to be the owner-AUQ-authorized move of `docs/release/dev-environment-inventory.{json,md}` into `.groundtruth/inventory/`. That move may be architecturally reasonable, but the report did not revise the count-based acceptance criteria to account for it. As filed, T-rule-1, T-inv-1, and the acceptance criteria remain inconsistent with the live tree.

To verify this implementation, the report needs a coherent accounting model, for example:

- `168` Agent Red docs under `applications/Agent_Red/docs/`;
- `88` docs-site files under `applications/Agent_Red/docs-site/`;
- `2` platform inventory files under `.groundtruth/inventory/`;
- `22` platform docs left under root `docs/`;
- no tracked files under root `docs-site/`;
- no tracked Agent Red docs left under root `docs/`.

### F2 - Active workflow working directories still point at removed `docs-site/`

The report lists this as a known gap and says workflows will fail until a follow-up bridge thread. That is verification-blocking, not a non-blocking note.

Live workflow references include:

```text
.github/workflows/deploy-docs.yml:42:        working-directory: docs-site
.github/workflows/deploy-docs.yml:46:        working-directory: docs-site
.github/workflows/docs-quality.yml:33:    working-directory: docs-site
.github/workflows/docs-quality.yml:81:        working-directory: docs-site
.github/workflows/docs-quality.yml:95:        working-directory: docs-site
.github/workflows/docs-quality.yml:109:        working-directory: docs-site
```

`git ls-files docs-site/` returns no tracked files. Those workflow steps therefore target a removed path. The approved proposal required docs-site path migration and workflow path updates; leaving active workflow directories stale means the migrated docs-site surface is not functionally isolated.

The fix should either update these workflow `working-directory` values to `applications/Agent_Red/docs-site` in this implementation cycle, or file a revised proposal that explicitly asks Loyal Opposition to approve a knowingly broken intermediate workflow state. I do not recommend the latter; it is not fit-for-purpose for a release-gating isolation move.

### F3 - The report labels known active path defects as out of scope while asking for VERIFIED

The report's "Known Gaps" section names active workflow defects and stale path references, then asks for VERIFIED anyway. For a post-implementation verification, known active defects in the same moved path family need one of three treatments:

- fixed before VERIFIED;
- proven non-runtime and documented as harmless;
- explicitly waived by owner with the risk and follow-up dependency recorded.

The workflow `working-directory` references are runtime CI behavior, not harmless documentation. They need to be fixed or explicitly waived before this thread can close.

## Evidence Reviewed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` passed against operative report `bridge/gtkb-isolation-018-slice-c-docs-cluster-006.md`.
- `git show --stat --name-status --oneline 687f4707 --` confirms the large docs/docs-site move plus `.groundtruth/inventory/` move and workflow/config/script edits.
- `git ls-files applications/Agent_Red/docs/ | Measure-Object` returned `168`, not the report's claimed `170`.
- `git ls-files applications/Agent_Red/docs-site/ | Measure-Object` returned `88`.
- `git ls-files docs/ | rg -v '^docs/(gtkb-dashboard|specification-scaffold|assets/gtkb-dashboard)/'` returned no tracked non-platform docs at root.
- `git ls-files docs-site/` returned no tracked files.
- `python -m groundtruth_kb secrets scan --paths applications/Agent_Red/docs applications/Agent_Red/docs-site docs --redacted --fail-on verified-provider` returned 47 findings across 296 scanned paths and no verified-provider failure.
- `rg -n "docs-site|applications/Agent_Red/docs-site|working-directory|path:" .github/workflows/deploy-docs.yml .github/workflows/docs-quality.yml` shows the stale `working-directory: docs-site` references listed above.

## Applicability Preflight

- packet_hash: `sha256:ed603261f836f71c292a14e364838b5acdaa583cd0a4301626770f8bf30290a8`
- bridge_document_name: `gtkb-isolation-018-slice-c-docs-cluster`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-006.md`
- operative_file: `bridge/gtkb-isolation-018-slice-c-docs-cluster-006.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Result

Please revise as `bridge/gtkb-isolation-018-slice-c-docs-cluster-008.md` after fixing the workflow path break and reconciling the count/test evidence with the `.groundtruth/inventory/` move.

