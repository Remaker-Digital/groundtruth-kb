NEW

# Post-Implementation Report — GTKB-ISOLATION-018 Sub-slice 18.B: PDF Cluster Move

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Implementation commit:** `6724817b` on `develop`
**Approved proposal:** `bridge/gtkb-isolation-018-slice-b-pdf-cluster-007.md` (Codex GO at `bridge/gtkb-isolation-018-slice-b-pdf-cluster-008.md`)
**Shell used for verification commands:** Git Bash on Windows (`/usr/bin/bash`). Per Codex `-008` non-blocking observation, identifying the shell so PowerShell-environment reviewers can reproduce equivalents.

---

## Specification Links

Carried forward from approved proposal `bridge/gtkb-isolation-018-slice-b-pdf-cluster-007.md`.

Cross-cutting (blocking):
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — bridge index canonical authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — proposal spec-linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires executed spec-derived tests.

Topic-specific:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision) — source rule.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — 5 binding rules.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (owner_decision) — ACTIVE waiver covering this work.
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` — umbrella scoping (Codex GO).
- `applications/Agent_Red/.gtkb-app-isolation.json` — isolation registry (extended this slice).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — placement contract.
- `DCL-APP-ROOT-MINIMIZATION-001` (proposed) — minimization principle.
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (all verified).

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster
```

Observed result (re-run for `-009`):

```text
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS.

## Implementation Summary

Single commit on `develop`: `6724817b — gtkb-isolation-018 Slice 18.B: PDF cluster move to applications/Agent_Red/pdf-tooling/`.

12 files changed: 3 renames (R100, history preserved), 8 plain moves (ignored files), 3 in-place edits to generator scripts, 1 `.gitignore` rewrite, 1 registry insert, 1 INDEX entry, 3 new bridge thread files.

Migration steps executed (per approved proposal):
1. `mkdir -p applications/Agent_Red/pdf-tooling` ✓
2. `git mv` 3 tracked files (.docx ×2, .png ×1) ✓
3. plain `mv` 7 ignored files (.ps1, .js, .py, .bat, .md, .md, .txt) ✓
3.5. plain `mv` `package-pdf.json` ✓
3.6. Edited `OUTPUT_PATH` in `scripts/generate_{agentred,orbatech,orbatech_v2}_report.py` ✓
4. `.gitignore` updated: 8 root patterns removed, 8 corresponding new-path patterns added (consolidated `PRODUCTION-READINESS-*` from "Ephemeral session/evaluation artifacts" section into the "PDF Generation" section since the cluster is now contiguous). ✓
5. Single commit on develop with waiver citation in message body. ✓

## Specification-to-Test Mapping with Observed Results

| Test ID | Spec Coverage | Command | Observed Result | Verdict |
|---------|---------------|---------|-----------------|---------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-b-pdf-cluster" bridge/INDEX.md` | `Document: gtkb-isolation-018-slice-b-pdf-cluster` | PASS |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-b-pdf-cluster` | `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` | PASS |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This REPORT contains spec links + spec-to-test mapping + executed commands + observed results | All sections present | PASS (Codex VERIFIED gate) |
| **T-rule-1** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 | `ls applications/Agent_Red/pdf-tooling/` | 11 files: AgentRed-Technical-Evaluation-Report.docx, Generate-PDF-Report.ps1, OrbaTech-Technical-Evaluation-Report.docx, PDF-Generation-Instructions.md, PRODUCTION-READINESS-ASSESSMENT.md, PRODUCTION-READINESS-SUMMARY.txt, generate-pdf-report.js, generate-pdf-report.py, generate-pdf.bat, package-pdf.json, prechat-form-phone-screenshot.png | PASS |
| **T-rule-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 | `for f in <11 cluster files>; do test ! -f "$f" \|\| echo "STILL AT ROOT: $f"; done` | (no STILL AT ROOT lines) | PASS |
| **T-inv-1** | umbrella inventory match | `find applications/Agent_Red/pdf-tooling -type f \| wc -l` | `11` | PASS |
| **T-reg-1** | `.gtkb-app-isolation.json` registry update | `python -c "import json; r=json.load(open('applications/Agent_Red/.gtkb-app-isolation.json')); names=[a['name'] for a in r['top_level_artifacts']]; print('pdf-tooling' in names)"` | `True` | PASS |
| **T-gi-1** | `.gitignore` update preserves ignored-status for all 8 moved ignored files | `cd applications/Agent_Red/pdf-tooling && count=0; for f in <8 files>; do git check-ignore "$f" >/dev/null 2>&1 && count=$((count+1)); done; echo "ignored: $count/8"` | `ignored: 8/8` | PASS |
| **T-import-1** | no external import breakage | `grep -rn "<8 cluster filename patterns>" --include="*.py" --include="*.js" --include="*.json" --include="*.toml" --include="*.yml" --include="*.yaml" \| grep -vE "^(bridge/\|memory/\|independent-progress-assessments/\|applications/Agent_Red/pdf-tooling/\|scripts/generate_agentred_report\.py\|scripts/generate_orbatech_report\.py\|scripts/generate_orbatech_report_v2\.py\|\.codex/\|\.claude/\|harness-state/)"` | (empty) | PASS |
| **T-output-1** | per Codex F3: generator OUTPUT_PATH resolves under applications/Agent_Red/pdf-tooling/ | `python -c "for f in [3 scripts]: src = open(f, encoding='utf-8').read(); ..."` (UTF-8 fix vs proposal's missing encoding= kwarg, see Deviation Notes §1) | All 3 scripts contain `applications`, `Agent_Red`, `pdf-tooling`. Evidence: `scripts/generate_agentred_report.py:OUTPUT_PATH = os.path.join(BASE, "applications", "Agent_Red", "pdf-tooling", "Ag...`; `scripts/generate_orbatech_report.py:OUTPUT_PATH = os.path.join(BASE, "applications", "Agent_Red", "pdf-tooling", "Or...` | PASS |
| **T-manifest-1** | per Codex F2: package-pdf.json moved with cluster; main resolves | `cat applications/Agent_Red/pdf-tooling/package-pdf.json \| python -c "...check os.path.exists(main) at applications/Agent_Red/pdf-tooling/<main>..."` | `main=generate-pdf-report.js; resolves at applications/Agent_Red/pdf-tooling\generate-pdf-report.js: True` | PASS |
| **T-history-1** | tracked files preserve history via `git mv` | `git log --follow --oneline applications/Agent_Red/pdf-tooling/AgentRed-Technical-Evaluation-Report.docx \| wc -l` | `3` (3 historical commits found across the rename — confirms `R100` rename detection) | PASS |
| **T-waiver-1** | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | `git log -1 --pretty=%B \| grep -c "DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER"` | `1` (waiver cited in commit message body) | PASS |
| **T-platform-1** | GT-KB platform integrity preserved | `python -m pytest groundtruth-kb/tests/ -x --tb=short -q -k "isolation or registry or app_root or gitignore" --timeout=60` | `1 failed, 141 passed, 1771 deselected`. Failure: `test_tp14_local_only_matches_golden_fixture` on `.claude/hooks/bridge-compliance-gate.py` byte-mismatch — pre-existing, unrelated to 18.B (see Pre-existing Failures §). | PASS (with documented pre-existing failure) |

## Codex `-008` GO Conditions Coverage

| Condition | Test(s) | Status |
|-----------|---------|--------|
| 1. all 11 cluster files moved to `applications/Agent_Red/pdf-tooling/` | T-rule-1, T-inv-1 | ✅ |
| 2. none of the 11 cluster files remains at GT-KB root | T-rule-2 | ✅ |
| 3. all 8 ignored moved files, including `package-pdf.json`, are ignored at the new path | T-gi-1 | ✅ (8/8) |
| 4. the 3 generator scripts write outputs under `applications/Agent_Red/pdf-tooling/` | T-output-1 | ✅ |
| 5. `package-pdf.json` resolves `generate-pdf-report.js` in the moved directory | T-manifest-1 | ✅ |
| 6. the registry and `.gitignore` changes match the approved proposal | T-reg-1, manual diff inspection | ✅ |
| 7. platform smoke verification is captured with observed output or documented pre-existing failures only | T-platform-1 | ✅ (1 pre-existing failure documented) |

## Pre-existing Failures (Documented, Not Caused By 18.B)

`test_tp14_local_only_matches_golden_fixture` (`groundtruth-kb/tests/test_scaffold_isolation.py:462`) — fails with byte-level mismatch on `.claude/hooks/bridge-compliance-gate.py` between live workspace and the local-only golden fixture at `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/hooks/bridge-compliance-gate.py`.

Evidence this is pre-existing:
- `git log -1 --pretty="%h %ai %s" -- .claude/hooks/bridge-compliance-gate.py` returns `95fee022 2026-05-04 00:32:24 -0700 S331 wrap: ...` — the live hook was last modified in commit `95fee022`, which predates 18.B commit `6724817b`.
- 18.B did not touch `.claude/hooks/bridge-compliance-gate.py` or any scaffold-golden fixture.
- The mismatch indicates the local-only golden fixture is stale relative to the active hook; the fixture refresh is out of scope for 18.B (PDF cluster move) and belongs in a separate scaffold-fixture-refresh slice.

Recommendation: file as a follow-up backlog item; not a blocker for 18.B VERIFIED.

## Deviation Notes (Differences From Approved Proposal -007)

1. **T-output-1 UTF-8 encoding fix (non-substantive):** The proposal's T-output-1 Python one-liner used `open(f).read()` without an `encoding=` kwarg. On Windows (cp1252 default codec), this raised `UnicodeDecodeError` on byte 0x90 in `scripts/generate_orbatech_report.py`. The verification command was re-run with `open(f, encoding='utf-8').read()`. The substantive contract (all 3 scripts contain `applications`, `Agent_Red`, `pdf-tooling`) is unchanged.

2. **T-import-1 exclusion regex correction (non-substantive):** The proposal's T-import-1 grep used the exclusion fragment `^scripts/generate_(agentred|orbatech|orbatech_v2)_report\.py`, but the actual filename is `generate_orbatech_report_v2.py` (suffix `_report_v2`, not `_v2_report`). The verification command was run with the corrected exclusion: `^(scripts/generate_agentred_report\.py|scripts/generate_orbatech_report\.py|scripts/generate_orbatech_report_v2\.py)`. With the correction the grep returns empty (PASS).

3. **`.gitignore` consolidation (within-spec):** The proposal Step 4 said "Add 8 corresponding patterns under `applications/Agent_Red/pdf-tooling/`". Implementation consolidated all 8 new-path patterns into the existing "PDF Generation" `.gitignore` section, including the 2 `PRODUCTION-READINESS-*` patterns previously located in the "Ephemeral session/evaluation artifacts" section (lines 366-367). The "Ephemeral" section retains a pointer comment to the new location. Net behavior identical; section organization more coherent.

4. **OQ resolution (defaults applied):** OQ-A `pdf-tooling/`, OQ-B preserve-ignored, OQ-C flat — all proposal defaults applied per owner pre-approval in session brief ("If GO: execute the migration").

## Side-effect Observations (Non-blocking; Not Part of 18.B Scope)

- **Spurious `.claude/session/` directory created at `applications/Agent_Red/pdf-tooling/.claude/`:** A session-tracker hook (`spec-events-seen.jsonl.lock` lock file) was instantiated when verification commands `cd`'d into the new directory before commit. The directory is untracked (not in commit `6724817b`). The destructive-gate hook blocked `rm -rf` without owner approval. Recommend either (a) owner-approved cleanup of this stray directory, or (b) hook hygiene to anchor session state at project root regardless of cwd. Belongs in a separate hygiene slice, not 18.B.

## Subsequent Commits in This Session (Scoped Separately Per Bridge Protocol)

Per `.claude/rules/bridge-essential.md` "Scoped commits only" mandate:

- `17e23d03 — S331 hygiene: clear 13 pending-decision-tracker false positives` — owner-invoked `clear pending` shortcut moved 13 prose-pattern false-positive entries from `## Pending` to `## Resolved` in `memory/pending-owner-decisions.md`. Unrelated to 18.B; committed separately.

## Project Root Boundary Compliance

All changes operate entirely within `E:/GT-KB/`. File moves go from `E:/GT-KB/<root>` → `E:/GT-KB/applications/Agent_Red/pdf-tooling/`. Waiver `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 SCOPE clause cited in commit message authorizes the in-flight Agent Red root-file work. Per `.claude/rules/project-root-boundary.md`.

## Acceptance Criteria Status

- [x] Codex GO on proposal (`-008`)
- [x] Preflight passes (T-spec-1)
- [x] Inventory and migration strategy reviewed; no missing files; no incorrect destinations
- [x] OQ-A/B/C defaults accepted (per owner pre-approval)

VERIFIED requires:
- [x] All 13 tests T-bridge-1 through T-platform-1 PASS with command output captured (T-platform-1 with documented pre-existing failure)
- [ ] Codex VERIFIED on this REPORT
- [x] No regression in GT-KB platform tests (T-platform-1 — only pre-existing failure)
- [x] `applications/Agent_Red/pdf-tooling/` exists with all 11 files
- [x] All 8 ignored moved files retain ignored-status at the new path (T-gi-1 returns `ignored: 8/8`)
- [x] Registry updated; isolation contract satisfied at the entry-level (T-reg-1)

## Provenance

| Source | Reference |
|--------|-----------|
| Approved proposal | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-007.md` |
| Codex GO verdict | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-008.md` |
| Implementation commit | `6724817b` on `develop` |
| Subsequent scoped commit | `17e23d03` (pending-decisions clear; unrelated) |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 |
| Umbrella scoping | `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` |
| Verification shell | Git Bash on Windows (`/usr/bin/bash`) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
