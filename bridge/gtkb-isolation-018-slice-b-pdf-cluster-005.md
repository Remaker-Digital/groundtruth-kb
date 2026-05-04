REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.B: PDF Cluster Move (REVISED-2)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice of GTKB-ISOLATION-018 (umbrella scoping `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` GO'd 2026-05-04)
**Cluster:** PDF tooling + Agent Red identity reports (11 files moved + 3 generator scripts edited in-place)
**Risk tier:** Low (no Python/JS imports affected; no source-code references to any cluster file)
**Waiver basis:** `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE (per `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` VERIFIED). The waiver's SCOPE clause authorizes Agent Red root-file work during ISOLATION-018 execution.

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-isolation-018-slice-b-pdf-cluster-002.md` — F1 (no-reference premise was false; missed `scripts/generate_*report*.py` + `package-pdf.json` references), F2 (`package-pdf.json` split unsafe; manifest's `main` field references `generate-pdf-report.js`), F3 (generator scripts would recreate root-level Agent Red outputs even after the move).

---

## Codex Findings Addressed

### Cycle 2 (NO-GO at -004, addressed in -005)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — Internal inconsistency: -003 expanded scope to 11 files but left 6 sites referring to 10 files (rationale text, T-rule-1, T-rule-2, T-inv-1, acceptance criteria, Out of Scope). | "Make package-pdf.json scope consistent across goal, inventory, migration steps, test plan, acceptance criteria, and Out of Scope." | All 6 sites updated to 11 files. T-rule-2 explicitly lists `package-pdf.json` in the root-absence assertion. T-inv-1 expects `wc -l` to return 11. Out of Scope explicitly notes `package-pdf.json` is now IN scope (was deferred to 18.H but moved here per cycle-1 F2). |
| **F2** — `package-pdf.json` is gitignored, not tracked. Proposed `git mv` would fail. `.gitignore:177` has exact-name pattern. | "Classify `package-pdf.json` correctly as an ignored root file. Move it with the same plain-move path used for other ignored files." | Inventory table updated to ❌ gitignored. Step 3.5 changed from `git mv` to plain `mv`. `.gitignore` migration in Step 4 updated to remove 8 patterns (was 7) and add 8 new-path patterns. T-gi-1 default-behavior coverage extends to all 8 ignored files including `package-pdf.json`. |

### Cycle 1 (NO-GO at -002, addressed in -003)


| Finding | Recommendation | Disposition in this revision |
|---------|----------------|------------------------------|
| **F1** — `rg` revealed live references in `package-pdf.json:5,7` (`"main": "generate-pdf-report.js"`, `"generate-pdf": "node ..."`); `scripts/generate_agentred_report.py:34` (writes `AgentRed-Technical-Evaluation-Report.docx` to BASE = repo root); `scripts/generate_orbatech_report.py:35` (writes Orba report to root); `scripts/generate_orbatech_report_v2.py:18` (same). | "Revise the slice to account for all live references before moving files." | This revision EXPANDS scope to include `package-pdf.json` (moved with the cluster) and IN-PLACE EDITS the 3 generator scripts to update `OUTPUT_PATH` to `applications/Agent_Red/pdf-tooling/`. T-import-1 is rewritten to allow self-references within the moved cluster directory while still flagging external references. New test T-output-1 checks generator `OUTPUT_PATH` resolution. |
| **F2** — Splitting `package-pdf.json` from `generate-pdf-report.js` would break the manifest's `main` field. | "Move `package-pdf.json` with the PDF tooling in 18.B." | This revision moves `package-pdf.json` together with the JS script. The manifest's `main: generate-pdf-report.js` continues to resolve correctly because both files end up in the same `applications/Agent_Red/pdf-tooling/` directory. The umbrella's earlier 18.H scope is correspondingly narrowed (handled in revised umbrella if needed; but no current umbrella conflict because manifests are now Agent-Red-specific in 18.H). |
| **F3** — Generator scripts hardcode `OUTPUT_PATH = os.path.join(BASE, "<filename>.docx")` where BASE is the repo root, so running them post-move would recreate root-level Agent Red files in violation of `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3. | "Update the generator scripts in the same slice to write to `applications/Agent_Red/pdf-tooling/`." | This revision EDITS the 3 generator scripts in-place: `OUTPUT_PATH = os.path.join(BASE, "applications", "Agent_Red", "pdf-tooling", "<filename>.docx")`. The scripts themselves stay in `scripts/` (their migration is part of 18.E's scripts-cluster work); only their output path is corrected. New test T-output-1 verifies the OUTPUT_PATH values resolve to `applications/Agent_Red/pdf-tooling/`, not the repo root. |

---

## Background

This is the first concrete file-move sub-slice of the ISOLATION-018 program. The umbrella scoping (now GO'd at `-006`) defined 12 sub-slices 18.A through 18.L; 18.A is the scoping itself; 18.B is this proposal. Sub-slice 18.B is selected as the program's first execution because:

- Live references identified: `package-pdf.json` references `generate-pdf-report.js` as `main`; `scripts/generate_{agentred,orbatech,orbatech_v2}_report.py` write Agent Red reports to repo root via hardcoded `OUTPUT_PATH`. This revision addresses both via in-scope inclusion of `package-pdf.json` + in-place OUTPUT_PATH edits in the 3 generator scripts (per Codex F1+F2+F3 findings on `-002`).
- The cluster is pre-scoped per the existing isolation registry (`applications/Agent_Red/.gtkb-app-isolation.json` `out_of_scope_for_sub_slice_1[3]`: "PDF cluster move into pdf-tooling/ (sub-slice 4)") — destination directory is named: `applications/Agent_Red/pdf-tooling/`.
- The cluster is the smallest active cluster by file count (11 files including `package-pdf.json`).
- Risk tier is LOW per the umbrella's risk register.

This proposal is the first manifestation of the Agent Red migration; its outcome demonstrates the migration mechanics work end-to-end before sub-slices touching code/imports begin.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this Specification Links section enumerates all governing specs (cross-cutting + topic-specific + advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section maps every spec clause to a concrete test command and expected result.

Topic-specific governance for this work:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330) — Source rule that authorizes the migration program; this sub-slice executes the rule's required end state for the PDF cluster.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — 5 binding rules including RULE 3 (Agent Red files MUST live in `applications/Agent_Red/`). Compliance: this sub-slice moves PDF cluster files into compliance.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract whose `exceptions[0]` clause cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`. Compliance: this sub-slice's commits are covered by the waiver's SCOPE clause until ISOLATION-018 reaches VERIFIED.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (owner_decision, S331) — **ACTIVE waiver** authorizing in-flight Agent Red root-file work. Compliance: this proposal cites the waiver by ID per the CITATION OBLIGATION clause; sub-slice's commits during the migration window are within the waiver's SCOPE.
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (Codex GO 2026-05-04) — Umbrella scoping that defines this sub-slice. The umbrella's inventory at "Migrates to applications/Agent_Red/ (Agent Red product)" lists 9 PDF-cluster files plus the package.json companion `package-pdf.json` (which moves separately in 18.H per the umbrella). This proposal extends the umbrella's pre-scoping with live-probed gitignore status.
- `applications/Agent_Red/.gtkb-app-isolation.json` — Existing isolation registry; `out_of_scope_for_sub_slice_1[3]` named the destination directory `applications/Agent_Red/pdf-tooling/`. This proposal extends the registry with a new top-level entry for `pdf-tooling/` once moved.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Placement contract authorizing `applications/Agent_Red/` as the destination namespace. Triggered by content matches `applications/`, `Agent Red`, `project root boundary` in this proposal.
- `DCL-APP-ROOT-MINIMIZATION-001` (proposed; pending sub-slice 6 of the application-isolation-contract program) — Minimization principle for `applications/Agent_Red/` root. The new `pdf-tooling/` top-level entry will be added to the isolation registry's `top_level_artifacts[]` array as Bucket=A "Agent Red PDF tooling and identity reports".
- `.claude/rules/project-root-boundary.md` — Project root boundary rule; auto-loaded at session start. This sub-slice operates entirely within `E:/GT-KB/`.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; this proposal complies with Mandatory Specification Linkage Gate + Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for review.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via Prior Deliberations section.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts. Compliance: this sub-slice produces a per-slice post-impl REPORT, an updated `.gtkb-app-isolation.json` registry entry, and updated `.gitignore` lines.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, decisions. Compliance: this proposal cites the umbrella, the waiver, the registry, and the source rule; the implementation will preserve git history via `git mv` for tracked files.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states. Compliance: this sub-slice transitions tracked PDF-cluster files from "active at GT-KB root (in violation, waiver-covered)" to "active at applications/Agent_Red/pdf-tooling/ (rule-compliant)".

The proposed tests in the Test Plan section derive from these linked specs as follows: GOV RULE 3 → T-rule-1 + T-rule-2 (Agent Red files at applications/Agent_Red/, no longer at root); DCL machine-checkable contract → T-dcl-1 (registry entry exists); waiver SCOPE compliance → T-waiver-1 (waiver cited in commits); umbrella inventory match → T-inv-1 (all 11 cluster files accounted for (10 originally + package-pdf.json per Codex F2 cycle 1)); registry update → T-reg-1; gitignore update → T-gi-1; no-import-break → T-import-1; bridge protocol → T-bridge-1; preflight → T-spec-1; spec-derived testing → T-spec-2.

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table (per `.claude/rules/deliberation-protocol.md`):

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source rule authorizing this work |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` | owner_conversation | owner_decision | ACTIVE waiver covering in-flight Agent Red root-file work |
| Bridge thread DELIBs at `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO) and `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (waiver VERIFIED) | bridge_thread | go / verified | Programmatic predecessors |
| `DELIB-0921` (IR-0.1 inventory at `applications/Agent_Red/incident-response/`) | bridge_thread | go | Pattern precedent for moving Agent Red content into `applications/Agent_Red/` |
| `DELIB-0912` / `DELIB-0926` / `DELIB-0927` (ISOLATION-016 Phase 8 Wave 2) | bridge_thread | go / no_go | Isolation harness foundations |

No prior deliberation rejects moving the PDF cluster into `applications/Agent_Red/pdf-tooling/`.

## Goal

Move the 11 PDF-cluster files (10 originally proposed + `package-pdf.json` per Codex F2) from `E:/GT-KB/` root to `E:/GT-KB/applications/Agent_Red/pdf-tooling/`, update `OUTPUT_PATH` in 3 generator scripts to resolve under the new location (per Codex F3), update `.gitignore` and the isolation registry, and verify all 5 binding rules from `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` are satisfied for the cluster.

## Live-probed Inventory (2026-05-04)

| File | Size | Tracked? | Action |
|------|-----:|---------|--------|
| `AgentRed-Technical-Evaluation-Report.docx` | 1,575,017 B | ✅ tracked | `git mv` to `applications/Agent_Red/pdf-tooling/` |
| `OrbaTech-Technical-Evaluation-Report.docx` | 1,177,283 B | ✅ tracked | `git mv` to `applications/Agent_Red/pdf-tooling/` |
| `prechat-form-phone-screenshot.png` | 35,504 B | ✅ tracked | `git mv` to `applications/Agent_Red/pdf-tooling/` |
| `Generate-PDF-Report.ps1` | 3,198 B | ❌ gitignored at root by exact name | plain `mv` to `applications/Agent_Red/pdf-tooling/`; remove `.gitignore` line; new path becomes untracked-not-ignored |
| `generate-pdf-report.js` | 2,518 B | ❌ gitignored at root by exact name | same |
| `generate-pdf-report.py` | 2,119 B (executable) | ❌ gitignored at root by exact name | same |
| `generate-pdf.bat` | 3,187 B | ❌ gitignored at root by exact name | same |
| `PDF-Generation-Instructions.md` | 4,853 B | ❌ gitignored at root by exact name | same |
| `PRODUCTION-READINESS-ASSESSMENT.md` | 7,352 B | ❌ gitignored at root by exact name | same |
| `PRODUCTION-READINESS-SUMMARY.txt` | 7,322 B | ❌ gitignored at root by exact name | same |
| `package-pdf.json` | ~250 B | ❌ gitignored at root by exact name (corrected from -003 per Codex `-004` F2; `.gitignore:177` matches by filename) | plain `mv` to `applications/Agent_Red/pdf-tooling/`; manifest `main: generate-pdf-report.js` resolves correctly because both files land in the same directory; `.gitignore` updated to preserve ignored-status under new path |

Verified via `git ls-files | grep -E '^(generate-pdf|Generate-PDF|PDF-Gener|PRODUCTION-READ|AgentRed-Tech|OrbaTech-Tech|prechat-form)'` (returns 3 lines) and `for f in ...; do git check-ignore $f; done` (returns 7 ignore-pattern matches).

Out of cluster:
- (none — `package-pdf.json` was originally deferred to 18.H but Codex F2 correctly identified the manifest split as unsafe; this revision includes it.)

In-place generator-script edits (NOT moved; their migration is 18.E's scripts-cluster scope):
- `scripts/generate_agentred_report.py` — UPDATE `OUTPUT_PATH` from `os.path.join(BASE, "AgentRed-Technical-Evaluation-Report.docx")` to `os.path.join(BASE, "applications", "Agent_Red", "pdf-tooling", "AgentRed-Technical-Evaluation-Report.docx")`.
- `scripts/generate_orbatech_report.py` — same pattern with `OrbaTech-Technical-Evaluation-Report.docx`.
- `scripts/generate_orbatech_report_v2.py` — same pattern with `OrbaTech-Technical-Evaluation-Report.docx`.

The LOGO_PATH and CHART_DIR references in these scripts continue to point at `BASE/branding/...` and `BASE/scripts/_report_charts*` respectively; those paths are out of 18.B's scope (handled in 18.D for branding, 18.E for scripts).

## Migration Strategy

### Step 1: Create destination directory + registry update

```
mkdir -p applications/Agent_Red/pdf-tooling
```

Update `applications/Agent_Red/.gtkb-app-isolation.json` to add a new entry in `top_level_artifacts[]`:

```json
{
  "name": "pdf-tooling",
  "type": "DIR",
  "bucket": "A",
  "purpose": "Agent Red PDF generation tooling and identity-report artifacts (migrated from GT-KB root in S331 sub-slice 18.B; covered by DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 SCOPE clause)"
}
```

### Step 2: Move tracked files (preserves history)

```
git mv AgentRed-Technical-Evaluation-Report.docx applications/Agent_Red/pdf-tooling/
git mv OrbaTech-Technical-Evaluation-Report.docx applications/Agent_Red/pdf-tooling/
git mv prechat-form-phone-screenshot.png applications/Agent_Red/pdf-tooling/
```

### Step 3: Move gitignored files (no history; just disk move)

```
mv Generate-PDF-Report.ps1 applications/Agent_Red/pdf-tooling/
mv generate-pdf-report.js applications/Agent_Red/pdf-tooling/
mv generate-pdf-report.py applications/Agent_Red/pdf-tooling/
mv generate-pdf.bat applications/Agent_Red/pdf-tooling/
mv PDF-Generation-Instructions.md applications/Agent_Red/pdf-tooling/
mv PRODUCTION-READINESS-ASSESSMENT.md applications/Agent_Red/pdf-tooling/
mv PRODUCTION-READINESS-SUMMARY.txt applications/Agent_Red/pdf-tooling/
```

### Step 3.5: Move gitignored manifest (per Codex F2 cycle 1, corrected per Codex F2 cycle 2)

```
mv package-pdf.json applications/Agent_Red/pdf-tooling/
```

`package-pdf.json` is gitignored at GT-KB root by exact-name pattern (verified live: `git ls-files package-pdf.json` returns empty; `.gitignore:177` matches). Plain `mv` not `git mv`. The manifest's `main: generate-pdf-report.js` continues to resolve because both files now share `applications/Agent_Red/pdf-tooling/` as their working directory.

### Step 3.6: Update generator script OUTPUT_PATH (per Codex F3 fix)

Edit the 3 generator scripts to point OUTPUT_PATH at the new location:

- `scripts/generate_agentred_report.py` line 34: change `os.path.join(BASE, "AgentRed-Technical-Evaluation-Report.docx")` → `os.path.join(BASE, "applications", "Agent_Red", "pdf-tooling", "AgentRed-Technical-Evaluation-Report.docx")`.
- `scripts/generate_orbatech_report.py` line 35: change `os.path.join(BASE, "OrbaTech-Technical-Evaluation-Report.docx")` → `os.path.join(BASE, "applications", "Agent_Red", "pdf-tooling", "OrbaTech-Technical-Evaluation-Report.docx")`.
- `scripts/generate_orbatech_report_v2.py` lines 16-19: change the OUTPUT_PATH expression to resolve under `applications/Agent_Red/pdf-tooling/`.

The scripts themselves stay in `scripts/` (their migration is 18.E scope). LOGO_PATH and CHART_DIR are unchanged (out of 18.B scope).

### Step 4: Update `.gitignore`

Remove the 8 root-anchored exact-name `.gitignore` patterns (7 originally + package-pdf.json per Codex F2 cycle 2) for the moved files. Add a single replacement pattern under `applications/Agent_Red/pdf-tooling/` that matches their new paths (or leave the new locations untracked-but-not-ignored — owner-confirmable; default below).

**Default behavior for the moved gitignored files:** preserve their ignored status by adding `applications/Agent_Red/pdf-tooling/Generate-PDF-Report.ps1` (and the 6 others) as exact-path patterns, OR a single `applications/Agent_Red/pdf-tooling/*.ps1`-style pattern + similar for the other extensions. **Owner alternative:** drop the gitignore entries entirely so the new locations become tracked. The default preserves prior intent (these files were locally generated/regenerable; not committed to GT-KB git history); the alternative would commit them as Agent Red identity content.

This proposal's default = preserve ignored status under the new path. OQ-B in Open Questions surfaces the alternative for owner override at GO time.

### Step 5: Commit on develop

Single commit on `develop` branch with message:

```
gtkb-isolation-018 Slice 18.B: PDF cluster move to applications/Agent_Red/pdf-tooling/

Moves 3 tracked files (git mv preserves history) + 7 gitignored files
(plain mv) into applications/Agent_Red/pdf-tooling/. Updates .gitignore
to preserve ignored-status under new path. Updates
applications/Agent_Red/.gtkb-app-isolation.json registry with new
Bucket-A entry.

Authorized by DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 SCOPE
clause (in-flight Agent Red root-file work covered until ISOLATION-018
VERIFIED).

Refs: bridge/gtkb-isolation-018-slice-b-pdf-cluster-001.md (Codex GO);
bridge/gtkb-isolation-018-agent-red-file-migration-006.md (umbrella GO).
```

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-b-pdf-cluster" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-rule-1** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 (Agent Red files at applications/Agent_Red/) | `ls applications/Agent_Red/pdf-tooling/` | Returns all 11 cluster files |
| **T-rule-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 (no Agent Red files at GT-KB root for this cluster) | `for f in AgentRed-Technical-Evaluation-Report.docx OrbaTech-Technical-Evaluation-Report.docx prechat-form-phone-screenshot.png Generate-PDF-Report.ps1 generate-pdf-report.js generate-pdf-report.py generate-pdf.bat PDF-Generation-Instructions.md PRODUCTION-READINESS-ASSESSMENT.md PRODUCTION-READINESS-SUMMARY.txt package-pdf.json; do test ! -f "$f" || echo "STILL AT ROOT: $f"; done` | Empty (all moved out of root) |
| **T-inv-1** | umbrella inventory match | `find applications/Agent_Red/pdf-tooling -type f \| wc -l` | 11 files |
| **T-reg-1** | `applications/Agent_Red/.gtkb-app-isolation.json` registry update | `python -c "import json; r=json.load(open('applications/Agent_Red/.gtkb-app-isolation.json')); names=[a['name'] for a in r['top_level_artifacts']]; print('pdf-tooling' in names)"` | `True` |
| **T-gi-1** | `.gitignore` update preserves ignored-status (default path) | `cd applications/Agent_Red/pdf-tooling && git check-ignore Generate-PDF-Report.ps1` | Returns matching pattern (file remains ignored) |
| **T-import-1** | no external import breakage (per Codex F1 revised) | `grep -rn "Generate-PDF-Report\|generate-pdf-report\|PDF-Generation\|prechat-form-phone-screenshot\|AgentRed-Technical-Evaluation\|OrbaTech-Technical-Evaluation\|PRODUCTION-READINESS-ASSESSMENT\|PRODUCTION-READINESS-SUMMARY" --include="*.py" --include="*.js" --include="*.json" --include="*.toml" --include="*.yml" --include="*.yaml" \| grep -v "^bridge/\|^memory/\|^independent-progress-assessments/\|^applications/Agent_Red/pdf-tooling/\|^scripts/generate_(agentred\|orbatech\|orbatech_v2)_report\.py"` | Empty (no files OUTSIDE the moved directory and the 3 known generator scripts reference cluster filenames). The 3 generator scripts in `scripts/` retain references to the .docx filenames after Step 3.6 OUTPUT_PATH update (they reference the filename inside `applications/Agent_Red/pdf-tooling/`, which is correct). |
| **T-output-1** | per Codex F3: generator OUTPUT_PATH resolves under applications/Agent_Red/pdf-tooling/, not root | `python -c "import re; import sys; failed=False; \nfor f in ['scripts/generate_agentred_report.py','scripts/generate_orbatech_report.py','scripts/generate_orbatech_report_v2.py']:\n    src=open(f).read()\n    if 'applications' not in src or 'Agent_Red' not in src or 'pdf-tooling' not in src: print(f'FAIL: {f} OUTPUT_PATH does not reference applications/Agent_Red/pdf-tooling/'); failed=True\nsys.exit(1 if failed else 0)"` | exit 0 (all 3 scripts reference the new path) |
| **T-manifest-1** | per Codex F2: package-pdf.json moved with cluster; main resolves | `cd applications/Agent_Red/pdf-tooling && cat package-pdf.json \| python -c "import json,sys,os; m=json.load(sys.stdin)['main']; print(os.path.exists(m))"` | `True` (the JS script exists in the same directory as the manifest) |
| **T-history-1** | tracked files preserve history via `git mv` | `git log --follow --oneline applications/Agent_Red/pdf-tooling/AgentRed-Technical-Evaluation-Report.docx \| wc -l` | >= 1 (history preserved across rename) |
| **T-waiver-1** | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | `git log -1 --pretty=%B` (most recent commit on develop) | Contains "DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER" |
| **T-platform-1** | GT-KB platform integrity preserved | `python -m pytest groundtruth-kb/tests/ -x --tb=short` (smoke) | Pass (or pre-existing-known failures only) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `find`, `grep`, `ls` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct (preflight pass) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct (Codex VERIFIED gate) |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 | T-rule-2 | Direct |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 | T-rule-1, T-inv-1 | Direct |
| `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` waiver-coverage | T-waiver-1 | Direct (commit cites waiver) |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | T-waiver-1 | Direct |
| `applications/Agent_Red/.gtkb-app-isolation.json` registry | T-reg-1 | Direct |
| `.gitignore` integrity | T-gi-1 | Direct |
| no-import-break invariant | T-import-1 | Direct |
| `git mv` history preservation | T-history-1 | Direct |
| GT-KB platform integrity | T-platform-1 | Direct |
| Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | (no new tests; satisfied by registry update + REPORT structure + lifecycle-state transition) | Indirect |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Inventory and migration strategy reviewed; no missing files; no incorrect destinations
- [ ] OQ-B owner default accepted, OR explicit override (preserve-ignored vs. track-at-new-path)

VERIFIED when:

- [ ] All 13 tests T-bridge-1 through T-platform-1 (including new T-output-1, T-manifest-1) PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] No regression in GT-KB platform tests (T-platform-1)
- [ ] `applications/Agent_Red/pdf-tooling/` exists with all 11 files (including package-pdf.json); root no longer contains any cluster file (T-rule-2 + T-rule-1)
- [ ] Registry updated; isolation contract still satisfied at the entry-level (T-reg-1)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Hidden import in code references the moved files | Low | Medium | T-import-1 explicitly checks; current grep shows no references |
| `git mv` fails on Windows path separators | Low | Low | Use forward-slash destination paths; tested in prior sub-slice 1 of application-isolation-contract |
| `.gitignore` update breaks other root-anchored ignores | Low | Low | Edit only the 7 specific lines; other patterns untouched |
| Owner prefers track-at-new-path instead of preserve-ignored | Medium | Low | OQ-B surfaces the choice; impl branches on owner answer |
| `applications/Agent_Red/pdf-tooling/` directory creation fails (permissions, sync conflict) | Low | Medium | `mkdir -p` is idempotent; check `applications/Agent_Red/` writeability before move |
| Drive sync conflict (per S311 incident) interferes mid-move | Low | Medium | `.driveignore` covers `applications/Agent_Red/.git` and similar; PDF cluster destination is within in-tree migration scope |

Rollback: `git revert` of the single commit reverses all moves atomically. Plain-mv files would re-appear at root in the working tree but `git revert` only handles tracked-file rename commits; the 7 gitignored files would need a manual `mv` back to root after revert (documented in the post-impl REPORT).

## Open Questions

| ID | Question | Default if unanswered |
|----|----------|-----------------------|
| **OQ-A** | Confirm destination directory name `pdf-tooling/` (vs `pdf/`, `tooling/`, `evaluation-reports/`)? | Default: `pdf-tooling/` per existing isolation-registry sub-slice-4 prescript |
| **OQ-B** | Preserve ignored-status for the 7 currently-gitignored files at the new path, or track them at the new path (commit content into Agent Red git tree)? | Default: preserve ignored-status (matches prior intent: these were locally generated; not committed) |
| **OQ-C** | Should the 2 evaluation-report `.docx` files (Agent Red + OrbaTech) move to a separate `evaluation-reports/` subdirectory under `pdf-tooling/`, or stay flat? | Default: flat (11 files in one directory; subdivision deferred to a future cleanup if needed) |

## Out of Scope

- (`package-pdf.json` is now IN scope per Codex F2 cycle 1; it was originally deferred to 18.H but the manifest split was unsafe.)
- Any other Agent Red files outside the 11-file PDF cluster (handled in their respective sub-slices).
- New PDF tooling features.
- Conversion of the .docx files to PDF or .md (these are identity reports; preserved as-is).

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Moves files from `E:/GT-KB/<root>` → `E:/GT-KB/applications/Agent_Red/pdf-tooling/` (within-root operation).
- Cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE as the authorization for in-flight Agent Red root-file work during the migration window.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping (Codex GO) | `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (2026-05-04) |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Authorizing GOV | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 |
| Authorizing DCL | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (S331) |
| Existing isolation registry | `applications/Agent_Red/.gtkb-app-isolation.json` |
| Pre-scoped destination | sub-slice-4 of application-isolation-contract program (`applications/Agent_Red/.gtkb-app-isolation.json` `out_of_scope_for_sub_slice_1[3]`) |
| Live probes | `git ls-files`, `git check-ignore`, `ls -la`, `grep -rn` (executed 2026-05-04) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
