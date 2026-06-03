NEW

bridge_kind: implementation_proposal
Document: gtkb-wrap-scan-report-relocation-slice-1
Version: 001
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

# Implementation Proposal — Wrap-scan report relocation (WI-4259)

## Summary

WI-4259 remediates the `snapshots_non_manifest` error-noise the WI-4249 detector
surfaced. **Owner-chosen approach** (DELIB-20260630): fix at the source —
relocate the wrap-scan reports out of the manifest-only snapshot dir — rather
than exempting them in the severity check.

**Root cause (empirically confirmed):** the session-wrap SKILLs
(`kb-session-wrap`, `kb-session-wrap-scan`) write `wrap-scan-hygiene.md` and
`wrap-scan-consistency.md` *into* `.groundtruth/session/snapshots/<id>/` via the
scanners' `--write-report` argument. `check_snapshots_non_manifest`
(`scripts/wrap_scan_hygiene.py`) flags every non-`manifest.json` file under
`.groundtruth/session/snapshots/` as `SEVERITY_ERROR` — by design, to keep that
directory manifest-only and force the future WRAPUP-Slice-2A redaction slice.
So the scanners' own reports trip the scanner. (Inspection of the live tree
confirmed multiple `<session-id>/` dirs contain exactly those two `.md` files
beside `manifest.json`.)

**Fix:** relocate the two reports to a sibling directory
`.groundtruth/session/wrap-scan-reports/<session-id>/`. The snapshot dir stays
strictly manifest-only; `check_snapshots_non_manifest` is **unchanged** (no
weakening); and because the new dir is outside `.groundtruth/session/snapshots/`
the scanner never sees the reports. `.groundtruth/` is gitignored
(`.gitignore:527`), so both dirs remain untracked runtime artifacts.

## Specification Links

Blocking:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — thread lifecycle in `bridge/INDEX.md`.
- `GOV-STANDING-BACKLOG-001` — WI-4259 is a governed cluster backlog item.
- `GOV-08` — the wrap-scan output reflects real state without self-inflicted
  error noise; the manifest-only invariant is preserved.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — under
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` v2 (active;
  WI-4259 included; `documentation` + `test_addition` mutation classes).
- `GOV-17` — quality-first: a scanner that flags its own legitimate output is a
  defect.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`;
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all 5 target paths in-root).

Advisory:
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — removes a recurring false-error
  class from the deterministic wrap-scan surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — change lands via the bridge cycle.
- `bridge/gtkb-wrapup-enhancements-slice1-006.md` (GO) — origin of
  `check_snapshots_non_manifest` and the manifest-only W0 scope this fix
  preserves.

## Prior Deliberations

- `DELIB-20260630` — owner directive + AUQ "Doc-PAUTH, both WIs" choosing the
  source-fix approach and authorizing the doc-class PAUTH amendment (cited in
  § Owner Decisions / Input).
- `DELIB-20260623` — hygiene-cluster authorization (parent).
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-006.md` (VERIFIED) —
  WI-4249, the parallel detector that surfaced this `snapshots_non_manifest`
  class; WI-4259 is the authorized remediation it deferred. (WI-4249 referenced
  as prior sibling work; the declared work item here is WI-4259.)
- No prior deliberation proposes relocating the wrap-scan reports; this is the
  first remediation of the co-location defect.

## Problem & Evidence

- `scripts/wrap_scan_hygiene.py:262-288` (`check_snapshots_non_manifest`) flags
  every non-`manifest.json` file under `.groundtruth/session/snapshots/` as
  `SEVERITY_ERROR` (CI-blocking) — intentional manifest-only enforcement.
- `.claude/skills/kb-session-wrap-scan/SKILL.md:34,43,49,53,54`: `SNAP_DIR=".groundtruth/session/snapshots/${SESSION_ID}"`
  is reused as the report target (`--write-report "${SNAP_DIR}/wrap-scan-*.md"`
  and `cat "${SNAP_DIR}/wrap-scan-*.md"`).
- `.claude/skills/kb-session-wrap/SKILL.md:43-44`: explicit
  `--write-report .groundtruth/session/snapshots/<SESSION_ID>/wrap-scan-*.md`.
- `.codex/skills/kb-session-wrap/SKILL.md` + `.codex/skills/kb-session-wrap-scan/SKILL.md`:
  byte-parity mirrors carrying the same paths.

## Proposed Change

**`documentation` mutation (4 SKILL.md files).** Relocate the two reports to a
sibling dir; keep `manifest.json` in the snapshot dir.

- `kb-session-wrap-scan` (both `.claude` and `.codex`): add
  `REPORT_DIR=".groundtruth/session/wrap-scan-reports/${SESSION_ID}"` next to the
  existing `SNAP_DIR`, `mkdir -p "${REPORT_DIR}"`, and repoint the two
  `--write-report` targets and the two `cat` lines from `${SNAP_DIR}/wrap-scan-*.md`
  to `${REPORT_DIR}/wrap-scan-*.md`. `SNAP_DIR` continues to hold only the W0
  `manifest.json`.
- `kb-session-wrap` (both `.claude` and `.codex`): repoint the two explicit
  `--write-report .groundtruth/session/snapshots/<SESSION_ID>/wrap-scan-*.md`
  paths to `.groundtruth/session/wrap-scan-reports/<SESSION_ID>/wrap-scan-*.md`.

**`test_addition` (1 new test).** `platform_tests/scripts/test_wrap_scan_report_relocation.py`
(details in § Spec-Derived Verification Plan).

**Not changed:** `check_snapshots_non_manifest` and the scanners
(`wrap_scan_hygiene.py`, `wrap_scan_consistency.py`) are untouched — the
manifest-only enforcement stays strict (owner's explicit constraint).

**Out of scope (noted):** existing `wrap-scan-*.md` files already present under
`.groundtruth/session/snapshots/<id>/` are gitignored, uncommitted runtime
residue; they are not re-created at the old path after this change and age out
with their session dirs. No repo state is affected.

## Target Paths

```json
[".claude/skills/kb-session-wrap/SKILL.md", ".claude/skills/kb-session-wrap-scan/SKILL.md", ".codex/skills/kb-session-wrap/SKILL.md", ".codex/skills/kb-session-wrap-scan/SKILL.md", "platform_tests/scripts/test_wrap_scan_report_relocation.py"]
```

Mutation classes: `documentation` (4 SKILL.md) + `test_addition` (1 test) — both
in PAUTH v2. All in-root (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`).

## Requirement Sufficiency

Existing requirements sufficient. The owner directive (DELIB-20260630) fixes the
approach; GOV-08/GOV-17 + the manifest-only invariant from
`gtkb-wrapup-enhancements-slice1` fully constrain the change. No new or revised
requirement needed.

## Spec-Derived Verification Plan

Command: `PYTHONPATH=groundtruth-kb/src python -m pytest platform_tests/scripts/test_wrap_scan_report_relocation.py -q`

| Specification / behavior | Test | Derivation |
|---|---|---|
| Reports relocated out of snapshot dir (the fix; regression guard) | `test_session_wrap_skills_write_reports_to_sibling_dir` — read all 4 SKILL.md files; assert each references `.groundtruth/session/wrap-scan-reports/` for wrap-scan-hygiene/consistency, and that no `--write-report` (or `cat`) directs a `wrap-scan-*.md` under `.groundtruth/session/snapshots/`. | Pins the owner-chosen relocation; prevents regression to the old path. |
| `.claude`/`.codex` parity | `test_claude_codex_skill_report_paths_match` — assert the report-path lines are byte-equal between each `.claude` SKILL and its `.codex` mirror. | Parity is a standing invariant for dual-harness skills. |
| Manifest-only dir yields no findings (preserved invariant) | `test_manifest_only_snapshot_dir_clean` — build a temp `.groundtruth/session/snapshots/<id>/manifest.json` only; assert `check_snapshots_non_manifest` returns `[]`. | Confirms the snapshot dir is clean once reports live elsewhere. |
| Manifest-only enforcement still flags strays (unchanged check) | `test_stray_non_manifest_still_flagged` — add a stray `transcript.jsonl` under the snapshot dir; assert `check_snapshots_non_manifest` flags it `SEVERITY_ERROR`. | Proves the strict gate is NOT weakened (owner constraint). |

`check_snapshots_non_manifest` is imported from `scripts/wrap_scan_hygiene.py`
(via `sys.path.insert(0, "scripts")`), matching the existing
`platform_tests/scripts/test_wrap_scan_hygiene.py` pattern. No `ruff`-relevant
source changes beyond the new test (ruff check + format --check run on it
pre-report).

## Risk / Rollback

- **Risk:** a consumer reading `wrap-scan-*.md` from the old snapshot path would
  miss the relocated reports. Mitigation: the only readers are the same
  session-wrap SKILLs' `cat` lines, repointed in the same change; grep confirms
  no other reader references those report filenames except the historical
  `bridge/gtkb-phantom-index-cleanup-*` audit notes (point-in-time evidence, not
  live consumers).
- **Rollback:** revert the 4 SKILL.md edits + delete the test. Pure
  instruction/test change; no source, schema, or committed-data impact.

## Owner Decisions / Input

- `DELIB-20260630` — owner directive (2026-06-03): chose the **source-fix**
  approach for WI-4259 ("fix the snapshot generator's capture set"), and via
  AskUserQuestion (header "WI-4259 doc scope" → "Doc-PAUTH, both WIs")
  authorized the doc-class PAUTH amendment that this proposal relies on
  (`PAUTH-...-HYGIENE-CLUSTER` v2 adds the `documentation` mutation class).
- `DELIB-20260623` — parent hygiene-cluster authorization.

## Recommended Commit Type

`fix` — repairs the `snapshots_non_manifest` self-inflicted error-noise defect.
The mechanism is SKILL.md instruction edits, but the intent and effect are a
behavior fix (scanner stops flagging its own reports). `docs` is the alternative
read given the diff is SKILL.md + a test; flagged for reviewer discretion.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
