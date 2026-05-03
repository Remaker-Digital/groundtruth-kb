VERIFIED

# Loyal Opposition Verification - GTKB-GOV-TERM-PRIMER-STARTUP Slice 1 REVISED-3

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed report: `bridge/gtkb-gov-term-primer-startup-2026-05-02-014.md`
Verdict: VERIFIED

## Claim

Slice 1 is verified. REVISED-3 resolves the `-013.md` blocker by restoring a
registered public profile (`dual-agent`) and satisfying the canonical
terminology public-surface check against the GT-KB checkout.

## Evidence

- `groundtruth.toml` now sets `[project].profile = "dual-agent"`, which is a
  registered public project profile in
  `groundtruth-kb/src/groundtruth_kb/project/profiles.py`.
- A root `MEMORY.md` now exists and carries the five canonical startup terms
  required by the `dual-agent` profile: MemBase, Deliberation Archive,
  MEMORY.md, Prime Builder, and Loyal Opposition.
- The REVISED-2 content fixes in `AGENTS.md` and
  `.claude/rules/deliberation-protocol.md` are preserved.
- The public doctor command reaches the canonical terminology check and reports
  the required OK result:

```text
uv run --project groundtruth-kb gt project doctor --dir . --profile dual-agent
```

Observed canonical-terminology line:

```text
[OK] Canonical-terminology surface OK — 5 required terms present in 4 required files (profile: dual-agent)
```

- The auto-detected public doctor path also resolves `dual-agent` from
  `groundtruth.toml` and reports the same canonical-terminology OK line:

```text
uv run --project groundtruth-kb gt project doctor --dir .
```

## Verification Results

Commands run:

```text
Get-Content -LiteralPath bridge/INDEX.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-013.md
Get-Content -LiteralPath bridge/gtkb-gov-term-primer-startup-2026-05-02-014.md
Get-Content -LiteralPath groundtruth.toml
Get-Content -LiteralPath MEMORY.md
Get-Content -LiteralPath groundtruth-kb/src/groundtruth_kb/project/profiles.py
rg -n "harness-memory|test_.*harness|gt project doctor|run_doctor\(|get_profile\(|list_profiles\(" groundtruth-kb/tests groundtruth-kb/src/groundtruth_kb/project groundtruth-kb/src/groundtruth_kb/cli.py
uv run --project groundtruth-kb gt project doctor --dir . --profile dual-agent
uv run --project groundtruth-kb gt project doctor --dir .
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
```

Observed results:

- Explicit public doctor path: reaches canonical terminology and reports OK.
- Auto-detected public doctor path: reaches canonical terminology and reports
  OK.
- Focused/broader cited sweep: `86 passed, 1 warning`.
- Ruff: `All checks passed!`.

The doctor command's overall process exit remains non-zero because of existing
unrelated checks outside this slice, including missing hook artifacts,
DA-harvest coverage, and isolation writability findings. Those were not
introduced by this bridge item and are not part of the term-primer Slice 1
acceptance criterion. The relevant public canonical-terminology surface is
verified.

## Residual Risk

The new automated regression still calls the private
`_check_canonical_terminology()` helper rather than `run_doctor()` or the CLI.
That leaves a smaller regression-test gap around profile-resolution plumbing.
I am not treating it as blocking because this verification executed both public
doctor paths and confirmed the prior crash is resolved, but a follow-on test
should assert the canonical-terminology check is present and OK in a
`run_doctor(repo_root, "dual-agent")` report.

## Decision Needed From Owner

None.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
