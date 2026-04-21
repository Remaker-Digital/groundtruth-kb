# GT-KB v0.6.1 Release — In-Flight Addendum 3 (CI failures on release-prep commit)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Prior:** `-012` GO (Addendum 2 applied + test fix commit), `-011` NEW (Addendum 2), `-010` GO (Addendum 1 applied), `-006` GO (release authorization)
**Reason for addendum:** GO Condition 5 of `-012` — "If the targeted run, full suite, mypy, or ruff exposes any additional failure, stop and file another bridge addendum instead of patching manually."

## Current Execution State

v0.6.1 release-prep commit `d11e39c` pushed to `origin/main` with 18 commits total (backlog + 5 new v0.6.1 commits). Branch CI triggered on push. **Release gate NOT green:**

| Workflow | Status | Time |
|----------|--------|------|
| Docstring Coverage | ✓ success | 19s |
| Security | ✓ success | 40s |
| Docs | ✓ success | 37s |
| CodeQL | ✓ success | 1m21s |
| SonarCloud | ✓ success | 2m56s |
| **Docs Check** | **✗ failure** | 16s |
| **CI (ci.yml)** | **✗ failure** | 4m5s |

No tag. No GitHub Release. No `publish.yml` workflow triggered. Release is halted per Codex GO Condition 2 of `-006` which requires CI green on the release-prep commit SHA before tagging.

## Root Cause Analysis

Both failures are **pre-existing hygiene gaps on feature branches that branch-CI did not catch but integration-CI did**. None are product defects; all are surgical doc/lint fixes. No conflict-resolution error, no test regression.

### F1 — Ruff lint (3 violations in `scripts/`)

Full-tree `ruff check .` catches issues my local `ruff check src/groundtruth_kb/ tests/` missed because I scoped to src+tests. CI scans the whole tree.

- `scripts/check_doc_links.py:36` — `import sys` present but unused (F401). Likely stale from prior iteration. Fix: remove line.
- `scripts/record_canonical_terminology_specs.py:8-12` — import block not properly grouped per ruff/isort rules (I001). Fix: `ruff check --fix` autofix (marked fixable).
- `scripts/startere_phase1_multiline_fix.py:10` — docstring contains `\d` regex which ruff treats as invalid escape (W605). The `\d` appears inside a module docstring describing an assertion pattern. Fix: prefix the docstring with `r` to make it a raw string: `r"""..."""` (marked fixable by ruff).

All 3 marked `[*] fixable with the --fix option` by ruff.

### F2 — Docs Check (2 doc-drift issues)

`scripts/check_docs_cli_coverage.py` runs 9 documentation-consistency checks on every CI pipeline. Two currently fail:

1. **Missing `gt project classify-tree` entry in `docs/reference/cli.md`**. The `classify-tree` subcommand was added by the ownership-matrix branch but its adopter-facing documentation was not added. Branch CI likely didn't fail because `docs-check` may have different gating at branch level, or the command was added after the branch CI pass.
2. **`docs/start-here.md:197` pins `gt, version 0.6.0`**. Hard-coded to the prior release. Release-prep commit correctly bumped `__version__` to 0.6.1 but did not cascade to the sample output shown in adopter docs. Fix: update the version string in start-here.md.

## Proposed Fixes

### Fix 1 — `scripts/check_doc_links.py` (remove unused import)

```diff
 import argparse
 import re
-import sys
 from dataclasses import dataclass, field
 from pathlib import Path
```

### Fix 2 — `scripts/record_canonical_terminology_specs.py` (ruff autofix)

Run `ruff check --fix scripts/record_canonical_terminology_specs.py`. Ruff autofix for I001 is deterministic and only reorders/regroups the existing imports without changing any symbols.

### Fix 3 — `scripts/startere_phase1_multiline_fix.py` (raw string on docstring)

```diff
-"""Fix SPEC-STARTHERE-* assertions that used ^ anchor.
+r"""Fix SPEC-STARTHERE-* assertions that used ^ anchor.

 Python's re.findall (used by the assertion engine) does not enable MULTILINE
 ...
 - SPEC-STARTHERE-BLOCKDIAGRAM   (^```mermaid)
 - SPEC-STARTHERE-PREREQ-ORDERING (^## Prerequisites, ^## Install)
 - SPEC-STARTHERE-DAYINLIFE      (^### Activity \d)
 """
```

Single-character addition (`r` prefix) on the opening triple-quote. No semantic change; `\d` becomes literal rather than an escape attempt.

### Fix 4 — `docs/reference/cli.md` (document `gt project classify-tree`)

Add a new section immediately after the `### gt project upgrade` section (line 446) and before the `---` separator at line 448. Proposed content:

```markdown
### gt project classify-tree

Classify every path in a target tree against the artifact-ownership matrix.
Manifest-independent: does NOT require `groundtruth.toml` in the target
tree and does NOT call `gt project doctor`.

\`\`\`
gt project classify-tree --dir <path> --output <report>
\`\`\`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--dir` | path | `.` | Target tree to walk |
| `--output` | path | `-` (stdout) | Report destination (Markdown or JSON based on extension) |
| `--format` | choice | auto | Force `markdown` or `json` output |

**Output format:** Deterministic header block + rows ordered by ownership
enum then alphabetical by path. Rows with ownership `legacy-exception` are
flagged `owner_decision_pending = "YES"`.

**Example:**

\`\`\`bash
# Classify the current tree, write Markdown report
gt project classify-tree --output classification.md

# Classify a specific project tree
gt project classify-tree --dir ../other-project --output other-report.md
\`\`\`

**Read-only:** The command does not modify any file in the target tree.
Suitable for legacy projects without GT-KB manifests.

---
```

### Fix 5 — `docs/start-here.md:197` (version bump)

```diff
-gt, version 0.6.0
+gt, version 0.6.1
```

Single-line substitution.

## Why These Are Hygiene Not Defects

None of the 5 items change product behavior. They close gaps between the product state (which is correct and tested) and the CI-enforced discipline (which legitimately rejected the release-prep commit).

The classify-tree doc gap is the most substantive — it's a user-visible omission — but classify-tree itself works correctly and is tested. The doc section simply hadn't been added.

## Meta-Observation (unchanged from -011)

This is the **third integration-surfaced class failure** (-007/-009, -011, -013). Branches pass their own CI but integration CI catches what per-branch gates missed. The pattern is worth formalizing as a post-release hygiene item: either tighten branch-CI scope to match integration-CI scope, or add a pre-merge full-tree smoke-check. Out of scope for v0.6.1 ship; flagged for v0.6.2+.

## Execution Plan Post-GO

On Codex GO of this addendum:

1. Apply Fix 1 (remove `import sys`).
2. Apply Fix 2 via `ruff check --fix scripts/record_canonical_terminology_specs.py` (autofix).
3. Apply Fix 3 (r-prefix the docstring).
4. Apply Fix 4 (add classify-tree section to cli.md).
5. Apply Fix 5 (version string bump in start-here.md).
6. Verify locally:
   ```bash
   ruff check .                                    # expect: All checks passed
   ruff format --check .                           # expect: all files formatted
   python scripts/check_docs_cli_coverage.py       # expect: exit 0 with no issues
   ```
7. Commit the 5 fixes as a single follow-up commit:
   ```
   fix(ci): release-prep CI hygiene — 3 ruff + 2 docs-drift fixes
   
   Per gtkb-v061-release-013 (Codex GO).
   ```
8. Push to origin/main.
9. Poll CI until all workflows on the new commit SHA complete successfully.
10. Resume Phase 5 (tag + `gh release create` + publish monitor).

If local verification at step 6 fails on any check, stop and file another addendum.

## Files this addendum touches (pending GO)

- `scripts/check_doc_links.py` — 1 line removed.
- `scripts/record_canonical_terminology_specs.py` — ruff autofix (imports reorganized).
- `scripts/startere_phase1_multiline_fix.py` — 1-character addition (r-prefix).
- `docs/reference/cli.md` — 1 new section (~30 lines).
- `docs/start-here.md` — 1-line substitution.

No source, test, template, or config file changes. No CHANGELOG changes (these are pre-release hygiene, not user-visible features).

## Out of Scope (unchanged)

- `gtkb-da-governance-completeness-implementation-016` GO — separate track.
- `gtkb-rollback-receipts-008` NO-GO — needs REVISED-4.
- Zero Agent Red commits.
- Stale "40-row" narration cleanup in upgrade.py (deferred per `-012` N2).
- Branch-CI tightening to match integration-CI scope (deferred to v0.6.2+ per meta-observation).

## Next Step

Codex review of this addendum.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
