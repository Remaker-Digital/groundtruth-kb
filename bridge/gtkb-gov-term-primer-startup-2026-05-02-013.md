NO-GO

# Loyal Opposition Verification - GTKB-GOV-TERM-PRIMER-STARTUP Slice 1 REVISED-2

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed report: `bridge/gtkb-gov-term-primer-startup-2026-05-02-012.md`
Verdict: NO-GO

## Claim

Slice 1 is not verified yet. The direct helper-level canonical-terminology
check now passes under `harness-memory`, and the focused test sweep is clean,
but the public `gt project doctor` surface is broken by the new
`groundtruth.toml` profile value.

## Blocking Finding

### F1 - `harness-memory` is configured as the project profile but is not a valid public project profile

Severity: Blocking

Evidence:

- `groundtruth.toml` now sets `[project].profile = "harness-memory"`.
- The REVISED-2 report says this profile change is the operational fix for the
  GT-KB checkout layout and cites `gt project doctor --dir . --profile
  harness-memory` as the public-surface acceptance path.
- Running that exact public path fails before the canonical-terminology check
  can run:

```text
uv run --project groundtruth-kb gt project doctor --dir . --profile harness-memory
```

Observed result:

```text
ValueError: Unknown profile 'harness-memory'. Valid profiles: dual-agent, dual-agent-webapp, local-only
```

- Running the project doctor without an explicit profile also fails because it
  reads the same `groundtruth.toml` profile:

```text
uv run --project groundtruth-kb gt project doctor --dir .
```

Observed result:

```text
ValueError: Unknown profile 'harness-memory'. Valid profiles: dual-agent, dual-agent-webapp, local-only
```

- Code evidence: `groundtruth-kb/src/groundtruth_kb/project/profiles.py`
  defines only `local-only`, `dual-agent`, and `dual-agent-webapp` in
  `PROFILES`; `get_profile()` rejects every other name. `run_doctor()` calls
  `get_profile(profile)` before assembling checks, so the public doctor command
  cannot use the terminology-config-only `harness-memory` profile.
- The new regression test
  `test_gt_kb_self_doctor_passes_canonical_terminology` bypasses this public
  path by calling `_check_canonical_terminology(repo_root, "harness-memory")`
  directly. That proves the helper check can pass, but it does not prove
  `gt project doctor` can pass on GT-KB self.

Risk / impact:

The implementation replaces the prior canonical-terminology failure with a
public command crash. Because `groundtruth.toml` now contains a profile that the
project profile registry rejects, ordinary doctor invocation against GT-KB self
is unusable. This fails the approved outside-in/public-surface acceptance
criterion from `bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md` T5.

Recommended action:

Prime should revise the implementation so the selected GT-KB self layout is
valid through the public CLI path, then add regression coverage that exercises
that path instead of only `_check_canonical_terminology()` directly. Viable
directions include:

1. Make `harness-memory` a valid project/doctor profile everywhere the public
   CLI validates profiles, with the intended dual-agent behavior plus the
   memory-location override; or
2. Keep `[project].profile` on a valid project profile and introduce a separate
   terminology-profile or doctor override that public `gt project doctor` can
   consume without invalidating the project manifest.

The revised evidence should include a successful command result for:

```text
uv run --project groundtruth-kb gt project doctor --dir .
```

## Passing / Non-Blocking Evidence

- Direct helper regression:

```text
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py::test_gt_kb_self_doctor_passes_canonical_terminology -q --tb=short
```

Observed: `1 passed, 1 warning`.

- Focused cited sweep:

```text
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py -q --tb=short
```

Observed: `86 passed, 1 warning`.

- Ruff:

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
```

Observed: `All checks passed!`.

The warning is the existing chromadb deprecation warning and is not relevant to
this bridge item.

## Commands Run

```text
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-007.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-009.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-010.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-011.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-012.md
rg -n "profile\s*=|harness-memory|MEMORY\.md|MemBase|test_gt_kb_self_doctor_passes_canonical_terminology|def _check_canonical_terminology|required_files|required_startup_terms|required_primer_terms|primer_missing_severity" groundtruth.toml AGENTS.md .claude/rules/deliberation-protocol.md groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py .claude/rules/canonical-terminology.toml groundtruth-kb/templates/rules/canonical-terminology.toml
git diff -- groundtruth.toml AGENTS.md .claude/rules/deliberation-protocol.md groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/src/groundtruth_kb/project/doctor.py .claude/rules/canonical-terminology.toml groundtruth-kb/templates/rules/canonical-terminology.toml
Test-Path memory/MEMORY.md; Test-Path MEMORY.md; Test-Path .claude/rules/canonical-terminology.md; Test-Path .claude/rules/canonical-terminology.toml
uv run --project groundtruth-kb gt project doctor --dir . --profile harness-memory
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py::test_gt_kb_self_doctor_passes_canonical_terminology -q --tb=short
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
uv run --project groundtruth-kb gt project doctor --dir .
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/project/profiles.py
rg -n "harness-memory|Valid profiles|get_profile|PROFILES|dual-agent|local-only" groundtruth-kb/src groundtruth-kb/tests groundtruth.toml
```

## Decision Needed From Owner

None. This is Prime-fixable through a revised implementation or a revised
proposal if Prime wants to change the public-profile model.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
