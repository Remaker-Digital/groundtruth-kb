NEW

bridge_kind: implementation_report
Document: gtkb-wrap-scan-report-relocation-slice-1
Version: 003
Responds to GO: bridge/gtkb-wrap-scan-report-relocation-slice-1-002.md
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER
Work Item: WI-4259
Owner Decision: DELIB-20260630
Recommended commit type: fix
target_paths: [".claude/skills/kb-session-wrap/SKILL.md", ".claude/skills/kb-session-wrap-scan/SKILL.md", ".codex/skills/kb-session-wrap/SKILL.md", ".codex/skills/kb-session-wrap-scan/SKILL.md", "platform_tests/scripts/test_wrap_scan_report_relocation.py"]

# Post-Implementation Report — Wrap-scan report relocation (WI-4259)

## Summary

Implemented WI-4259 per the GO at `-002` (Codex LO), strictly within the 5 GO'd
target paths. The session-wrap SKILLs now write `wrap-scan-hygiene.md` and
`wrap-scan-consistency.md` to the sibling dir
`.groundtruth/session/wrap-scan-reports/<session-id>/` instead of into the
manifest-only `.groundtruth/session/snapshots/<session-id>/`. The snapshot dir
stays manifest-only and `scripts/wrap_scan_hygiene.py::check_snapshots_non_manifest`
is **unchanged** (GO Implementation-Start Condition 1). 4 spec-derived tests
pass; `ruff check` + `ruff format --check` clean on the new test.

## GO -002 Implementation-Start Conditions — Disposition

1. **`check_snapshots_non_manifest` unchanged.** `scripts/wrap_scan_hygiene.py`
   was not edited. Confirmed by `test_stray_non_manifest_still_flagged` (the
   gate still flags a stray non-manifest file SEVERITY_ERROR). **Satisfied.**
2. **Changes inside the 5 target paths.** Only the 4 SKILL.md files + the new
   test were modified (see § Files Changed). **Satisfied.**
3. **Report includes relocation pytest + ruff evidence.** Below. **Satisfied.**

## Specification Links

Carried forward from `-001` (GO at `-002`):

Blocking: `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-STANDING-BACKLOG-001`, `GOV-08`,
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-17`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

Advisory: `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and (carried forward per the GO's
advisory note, as this report touches deferred/transient residue behavior)
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wrap-scan-report-relocation-slice-1
-> latest_status: GO; go_file: bridge/gtkb-wrap-scan-report-relocation-slice-1-002.md; expires_at: 2026-06-04T03:31:50Z
```

## Implementation Detail

**`documentation` mutation — 4 SKILL.md files:**

- `.claude/skills/kb-session-wrap-scan/SKILL.md` and
  `.codex/skills/kb-session-wrap-scan/SKILL.md`: added
  `REPORT_DIR=".groundtruth/session/wrap-scan-reports/${SESSION_ID}"` beside the
  retained `SNAP_DIR` (now annotated "manifest-only (W0)"), and repointed the two
  `--write-report` targets and the two `cat` lines from `${SNAP_DIR}/wrap-scan-*.md`
  to `${REPORT_DIR}/wrap-scan-*.md`. The scanners' `--write-report` creates
  `REPORT_DIR` atomically (`scripts/_wrap_io.py::_atomic_write_text` does
  `mkdir(parents=True, exist_ok=True)`), so no explicit `mkdir` is needed —
  matching the existing W0 pattern.
- `.claude/skills/kb-session-wrap/SKILL.md` and
  `.codex/skills/kb-session-wrap/SKILL.md`: repointed the two literal
  `.groundtruth/session/snapshots/<SESSION_ID>/wrap-scan-*.md` report paths to
  `.groundtruth/session/wrap-scan-reports/<SESSION_ID>/wrap-scan-*.md`.

The 2 `.codex` skills are hand-maintained mirrors (no generated-adapter marker),
so they were edited directly to preserve parity — verified by
`test_claude_codex_report_paths_parity`.

**`test_addition` — 1 new test:** `platform_tests/scripts/test_wrap_scan_report_relocation.py`.

**Not changed:** `scripts/wrap_scan_hygiene.py`, `scripts/wrap_scan_consistency.py`,
and `check_snapshots_non_manifest` — the manifest-only gate stays strict.

**Existing residue (out of scope, noted in `-001`):** prior `wrap-scan-*.md`
files already under `.groundtruth/session/snapshots/<id>/` are gitignored,
uncommitted runtime artifacts; they are no longer re-created at the old path and
age out with their session dirs. No committed repo state is affected.

## Spec-to-Test Mapping / Verification Evidence

Command: `PYTHONPATH=groundtruth-kb/src python -m pytest platform_tests/scripts/test_wrap_scan_report_relocation.py -q`
→ **4 passed in 0.09s**.

| Specification / behavior | Test | Result |
|---|---|---|
| Reports relocated to sibling dir; none under snapshots (the fix) | `test_session_wrap_skills_write_reports_to_sibling_dir` | PASS |
| `.claude`/`.codex` report-path parity | `test_claude_codex_report_paths_parity` | PASS |
| Manifest-only snapshot dir → no findings (preserved invariant, GOV-08) | `test_manifest_only_snapshot_dir_clean` | PASS |
| Stray non-manifest still SEVERITY_ERROR (gate NOT weakened; GO cond. 1) | `test_stray_non_manifest_still_flagged` | PASS |

Code-quality gates (the new Python test; the 4 SKILL.md are markdown, not
ruff-applicable):
- `ruff check platform_tests/scripts/test_wrap_scan_report_relocation.py` → **All checks passed!**
- `ruff format --check` (same file) → **1 file already formatted**.

SKILL.md correctness is verified behaviorally by the relocation + parity tests
above (they read all 4 files and assert the new paths + absence of any wrap-scan
report path under `snapshots/`).

## No-MemBase-Mutation Evidence

`groundtruth.db` is not written. Tests use temp trees; only the 5 target files
changed.

## Files Changed

- `.claude/skills/kb-session-wrap/SKILL.md` (2 report paths repointed)
- `.claude/skills/kb-session-wrap-scan/SKILL.md` (+`REPORT_DIR`; 4 refs repointed)
- `.codex/skills/kb-session-wrap/SKILL.md` (2 report paths repointed — parity)
- `.codex/skills/kb-session-wrap-scan/SKILL.md` (+`REPORT_DIR`; 4 refs repointed — parity)
- `platform_tests/scripts/test_wrap_scan_report_relocation.py` (new — 4 tests)

No other files touched. All in-root (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`).

## Owner Decisions / Input

- `DELIB-20260630` — owner chose the source-fix approach for WI-4259 and
  authorized the doc-class PAUTH amendment (`PAUTH-...-HYGIENE-CLUSTER` v2 adds
  `documentation`) via AskUserQuestion ("Doc-PAUTH, both WIs").
- `DELIB-20260623` — parent hygiene-cluster authorization.

## Recommended Commit Type

`fix` — repairs the `snapshots_non_manifest` self-inflicted error-noise defect
by relocating the scanner-owned reports. Mechanism is SKILL.md instruction edits
+ a test; `docs` is the alternative read given the diff, flagged for reviewer
discretion.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
