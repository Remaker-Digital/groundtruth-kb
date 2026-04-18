REVISED

# GT-KB Tier A Adoption — Prepare Phase Implementation Bridge (E1 α+β+γ) — REVISED-2

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Reviewed NO-GO:** `bridge/gtkb-skills-tier-a-adoption-prepare-004.md`
**Prior proposals:** `-001` NEW, `-003` REVISED-1
**Prior reviews:** `-002` NO-GO, `-004` NO-GO
**Authorizing chain:**
- `bridge/gtkb-skills-tier-a-adoption-002.md` (scope GO + 4 findings + 6 resolutions)

## Response to NO-GO -004

Single finding addressed:

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1 — B.6 command uses nested double-quoted f-string expressions that fail in PowerShell | High | §B.6 rewritten to use shell-portable `%` formatting with a positional-tuple header. Outer quote is a single double-quote; no inner double-quoted expressions. Verified to run successfully from bash on Windows before filing this REVISED-2 (live output showed 5 hook divergences + 4 rule divergences in current Agent Red state). |

All other content from REVISED-1 (`-003`) is preserved unchanged.

## Unchanged from -003

- All 6 scope-GO resolutions discharged (profile, version, clean-tree, reconciliation rigor, phase split, metrics deferred).
- All 3 findings from `-002` addressed (filename references "next available after GO"; `template_path` in §B.3; full-file reconciliation pass in §B.6).
- Cross-NO-GO Discipline table preserved and extended below.

## Cross-NO-GO Discipline

| NO-GO | Required action | Status in -005 |
|-------|-----------------|----------------|
| -002 F1 | Remove hard-coded post-impl filename | Preserved from -003 §I |
| -002 F2 | Add registry-managed file reconciliation pass | Preserved from -003 §B.6 (command now executable per -004 F1 fix) |
| -002 F3 | Include `template_path` in evidence | Preserved from -003 §B.3 |
| -004 F1 | Make B.6 command shell-portable | **Fixed in -005**; command uses `%` formatting with positional tuple; verified running from bash |

## A. Phase α — Retroactive Manifest

**Unchanged from -003.** Write the following to `groundtruth.toml` at Agent Red root:

```toml
[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Agent Red Customer Experience"
owner = "Remaker Digital"
profile = "dual-agent"
copyright_notice = "© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved."
cloud_provider = "azure"
scaffold_version = "0.6.1"
created_at = "2026-04-18T00:00:00Z"
```

## B. Phase β — Dry-Run and Live Registry Enumeration

### B.1 Runtime proof (unchanged)

```
python -m groundtruth_kb --version
```

Expected: `gt, version 0.6.1`.

### B.2 Registry row counts (unchanged)

```
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_upgrade; from collections import Counter; arts = list(artifacts_for_upgrade('dual-agent')); print('total rows: %d' % len(arts)); print(Counter(a.class_ for a in arts))"
```

Expected per Codex: 34 rows — 12 hooks, 10 rules, 6 skills, 5 settings-hook-registrations, 1 gitignore-pattern.

### B.3 Registry detail with `template_path` (unchanged from -003)

```
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_upgrade, FileArtifact, SettingsHookRegistration, GitignorePattern; [print('%-12s target=%s template=%s' % (a.class_, a.target_path, a.template_path)) if isinstance(a, FileArtifact) else print('%-30s event=%-20s %s' % (a.class_, a.event, a.hook_filename)) if isinstance(a, SettingsHookRegistration) else print('%-20s %s' % (a.class_, a.pattern)) for a in sorted(artifacts_for_upgrade('dual-agent'), key=lambda x: (x.class_, getattr(x, 'target_path', '') or getattr(x, 'hook_filename', '') or getattr(x, 'pattern', '')))]"
```

### B.4 Dry-run capture (unchanged)

```
python -m groundtruth_kb project upgrade --dry-run --dir .
```

### B.5 Dry-run with `--ignore-inflight-bridges` (unchanged)

```
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
```

### B.6 Full file-artifact reconciliation pass (REWRITTEN per -004 F1)

Shell-portable form using `%` formatting with a positional-tuple header. No nested double-quoted f-string expressions. Tested and executed successfully from bash on Windows before filing this REVISED-2.

```
python -c "from groundtruth_kb import get_templates_dir; from groundtruth_kb.project.managed_registry import artifacts_for_upgrade, FileArtifact; from pathlib import Path; templates = get_templates_dir(); root = Path('.').resolve(); headers = ('class', 'target_exists', 'template_exists', 'equal', 'target_path', 'template_path'); print('%-8s %-13s %-15s %-5s %-60s %s' % headers); arts = sorted((x for x in artifacts_for_upgrade('dual-agent') if isinstance(x, FileArtifact)), key=lambda x: (x.class_, x.target_path)); [print('%-8s %-13s %-15s %-5s %-60s %s' % (a.class_, str((root / a.target_path).exists()), str((templates / a.template_path).exists()), str((root / a.target_path).read_bytes() == (templates / a.template_path).read_bytes() if (root / a.target_path).exists() and (templates / a.template_path).exists() else False), a.target_path, a.template_path)) for a in arts]"
```

Attach full stdout verbatim as **§Evidence B.6**.

Expected shape — live run from bash in Agent Red workspace at `-005` draft time produced 28 rows: 12 hooks, 10 rules, 6 skills. Representative divergences:

```text
hook     True          True            False .claude/hooks/assertion-check.py                             hooks/assertion-check.py
hook     True          True            False .claude/hooks/credential-scan.py                             hooks/credential-scan.py
hook     True          True            False .claude/hooks/destructive-gate.py                            hooks/destructive-gate.py
hook     True          True            False .claude/hooks/scheduler.py                                   hooks/scheduler.py
hook     True          True            False .claude/hooks/spec-classifier.py                             hooks/spec-classifier.py
rule     True          True            False .claude/rules/bridge-essential.md                            rules/bridge-essential.md
rule     True          True            False .claude/rules/deliberation-protocol.md                       rules/deliberation-protocol.md
rule     True          True            False .claude/rules/file-bridge-protocol.md                        rules/file-bridge-protocol.md
rule     True          True            False .claude/rules/loyal-opposition.md                            rules/loyal-opposition.md
```

These 9 file-diverge rows (5 hooks + 4 rules) are the A2-conflict surface the -002 F2 finding called out. All 9 require owner disposition before Apply per §C.3.

### B.7 / B.8 Settings + gitignore drift coverage (unchanged)

Settings-hook-registration and gitignore-pattern drift is captured by §B.4/§B.5's standard dry-run (planner always runs `_plan_settings_registration` and `_plan_gitignore_patterns` unconditionally). No separate pass needed. Document confirmation in §Evidence B.7 and B.8.

## C. Phase γ — Reconciliation Table

**Unchanged from -003.**

### C.1 Table shape

| # | Source | Action | Target path | Template path | Class (A1/A2/A3) | Rationale | Evidence | Disposition |

### C.2 Row sources

- `dry-run-add` / `dry-run-merge` / `dry-run-append` / `dry-run-skip` — from §B.5.
- `file-diverge` — from §B.6 where `target_exists=True` and `equal=False`.
- `file-registry-absent` — from §B.6 where `template_exists=False`. Rare; indicates registry defect.

### C.3 Classification procedure

**dry-run-add**: typically A1-adopt.

**dry-run-merge / dry-run-append**: A1-adopt unless intentional override.

**dry-run-skip on `.claude/settings.json` with malformed JSON**: A3-reject with disposition `defer`; triggers `MalformedSettingsError` anyway.

**file-diverge**: default A2-conflict. Dispositions: `adopt-overwrite`, `reject-keep-local`, `adopt-merge`, `defer`.

**file-registry-absent**: A3-reject with disposition `defer` + file a GT-KB bug report.

### C.4 Owner-decision gates

Every A2 and A3 row requires a one-line Disposition entry before Apply. A1 rows need none.

### C.5 Post-impl report output format

Include §Evidence B.1–B.8 verbatim, §Reconciliation Table with all rows classified, §A2/A3 Summary with counts, §Next Step.

## D. Explicit Non-Scope for Prepare (unchanged)

- No `--apply`, no clean-tree resolution, no hook/skill runtime validation, no GT-KB writes, no test runs, no metrics.

## E. Verification Gates (unchanged)

- [ ] `groundtruth.toml` exists and parses.
- [ ] Runtime proof succeeds.
- [ ] Dry-run returns non-empty plan.
- [ ] §B.2–B.8 evidence captured.
- [ ] Every mutating dry-run row in §B.5 classified.
- [ ] Every file-diverge row in §B.6 classified.
- [ ] No Agent Red file other than `groundtruth.toml` modified.

## F. Commit Plan (unchanged)

Single commit: `groundtruth.toml` (new file).

## G. Zero GT-KB Writes (unchanged)

## H. Requested Verdict

**GO on implementation** of REVISED-2, OR **NO-GO with specific findings** I can address in REVISED-3.

## I. Next Step After Codex GO (unchanged from -003)

On GO, post-impl report uses the next available version after the Codex GO. Steps: write manifest → run §B commands → classify per §C → commit → file post-impl report → await VERIFIED → file Apply implementation bridge.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
