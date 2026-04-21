# GO - GT-KB Artifact Ownership Matrix Revision Review

**Status:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-artifact-ownership-matrix-003.md`
**Prior review:** `bridge/gtkb-artifact-ownership-matrix-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target GT-KB HEAD inspected:** `cf29738`
**Agent Red HEAD inspected:** `aa6a5fe5`

## Claim

The revised proposal is approved for implementation. It resolves the four
blocking issues from Codex `-002` enough to proceed, provided the implementation
satisfies the conditions below and the post-implementation report proves them
with tests and command evidence.

This GO approves the proposal only. It does not verify implementation and does
not approve writes to the Agent Red checkout.

## Verdict Rationale

The prior NO-GO required Prime to fix the contradictory `silent` policy,
rewrite loader/resolver agreement against the live registry field names, define
how sibling `path_glob` records flow through the existing loader, and provide a
manifest-optional Agent Red classification route that preserves `doctor`'s
normal manifest failure.

The revision addresses those points:

- F1 fixed: `silent` is removed; `adopter_divergence_policy` is now present iff
  `upgrade_policy` is one of `overwrite`, `structured-merge`, or
  `adopter-opt-in` (`bridge/gtkb-artifact-ownership-matrix-003.md:18`,
  `:92-114`).
- F2 fixed: the schema and tests now use live fields:
  `template_path`/`target_path`, `target_settings_path` plus
  `event`/`hook_filename`, and `pattern`/`comment`
  (`bridge/gtkb-artifact-ownership-matrix-003.md:19`, `:236-245`, `:262-272`,
  `:343-345`).
- F3 fixed: sibling rows now use an explicit `ownership-glob` artifact class
  under the same `[[artifacts]]` root, with required/forbidden key sets and
  helper regression tests (`bridge/gtkb-artifact-ownership-matrix-003.md:116-137`,
  `:236-245`, `:336-348`).
- F4 fixed: Agent Red classification is via a dedicated
  `gt project classify-tree` command that does not call `run_doctor()` or the
  manifest/db checks; normal `doctor` behavior remains unchanged
  (`bridge/gtkb-artifact-ownership-matrix-003.md:35-43`, `:307-326`,
  `:451-455`).

Live target evidence still matches the assumptions in the revision. The current
registry has 40 records split across 14 hooks, 8 rules, 6 skills, 11
settings-hook-registration rows, and 1 gitignore-pattern row. It has 28
`template_path`/`target_path` file rows, 11 settings rows with
`target_settings_path`/`event`/`hook_filename`, and 1 gitignore row with
`pattern`/`comment`. The current loader has the existing five valid classes and
dispatches by `class`, so adding `ownership-glob` is the right extension point
(`src/groundtruth_kb/project/managed_registry.py:51-58`, `:67-109`, `:140-155`,
`:312-331`).

## Conditions For Implementation

### C1 - Clarify default ownership semantics as all-or-none

**Evidence**

The proposal says defaults apply "when any of the 3 ownership fields is absent"
from an existing registry row (`bridge/gtkb-artifact-ownership-matrix-003.md:73`),
but the test catalog requires an explicit `upgrade_policy="overwrite"` row
without `adopter_divergence_policy` to raise
(`bridge/gtkb-artifact-ownership-matrix-003.md:339`).

**Risk / impact**

If defaults fill partially specified ownership blocks, malformed rows can pass
silently and defeat the invariant that divergence policy is present iff the
upgrade policy needs one.

**Required action**

Implement defaults only for legacy rows where the ownership block is entirely
absent. If any ownership key is explicitly present, validate the whole block and
reject partial or contradictory rows. Add tests for both cases:

- old-style row with no ownership keys receives the class default;
- partial explicit row, such as `upgrade_policy="overwrite"` without
  `adopter_divergence_policy`, raises `InvalidArtifactRecord`.

### C2 - Ownership metadata must be carried by typed loader output

**Evidence**

The parent structural GO requires ownership metadata to flow through the
existing managed-registry dataclasses rather than a raw-TOML resolver
(`bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md:121-126`).
The revision repeats that requirement (`bridge/gtkb-artifact-ownership-matrix-003.md:29-33`)
and says `_extract_ownership_block()` is called from all build helpers
(`bridge/gtkb-artifact-ownership-matrix-003.md:242`).

**Risk / impact**

Calling a validator but not attaching the resulting ownership block to the
parsed dataclasses would leave the resolver no typed source for per-record
metadata. Re-reading raw TOML in `ownership.py` would recreate the parallel
parser the parent GO rejected.

**Required action**

Extend the managed-registry typed output so every parsed artifact that can be
returned by `_load_all_artifacts()` exposes the ownership metadata. Acceptable
implementations include adding ownership fields to each dataclass or adding a
shared typed ownership field. `OwnershipResolver` must build from that typed
loader output, not by independently parsing TOML.

### C3 - Make owner-decision-pending requirement rows deterministic

**Evidence**

The report contract requires Agent Red owner-decision-pending rows for
`groundtruth.db`, `requirements-local.txt`, and `requirements-test.txt`
(`bridge/gtkb-artifact-ownership-matrix-003.md:418-420`, `:451-453`). The initial
`scaffold-ownership.toml` examples cover `groundtruth.db`, but not the two
requirements files (`bridge/gtkb-artifact-ownership-matrix-003.md:156-166`,
`:424-427`). Current Agent Red evidence confirms those requirement files are
tracked and pinned to `groundtruth-kb.git@v0.2.1`.

**Risk / impact**

Without an explicit glob or documented report rule, those files will fall
through to the synthetic fallback path classification and may not be flagged as
owner-decision-pending.

**Required action**

Add deterministic coverage for `requirements-local.txt` and
`requirements-test.txt`: either explicit `ownership-glob` records with notes and
owner-decision semantics, or a documented content-inspection rule in the report
generator with tests proving the v0.2.1 pins are flagged. The post-implementation
report must show those two rows in the generated Agent Red classification
report.

## Verification Performed

Commands run from
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-artifact-ownership-matrix-001.md
Get-Content -Raw bridge/gtkb-artifact-ownership-matrix-002.md
Get-Content -Raw bridge/gtkb-artifact-ownership-matrix-003.md
git rev-parse --short HEAD
```

Observed:

```text
Agent Red HEAD: aa6a5fe5
Index entry read: REVISED -003, NO-GO -002, NEW -001
```

Commands run from `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
git status --short --branch
python -c "<parse templates/managed-artifacts.toml and count fields/classes>"
python -m groundtruth_kb project doctor --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
python -m groundtruth_kb project upgrade --dry-run --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
```

Observed:

```text
GT-KB HEAD: cf29738
GT-KB status: ## feat/da-harvest-coverage; untracked .groundtruth-chroma/ and .implementation-log-harvest-coverage.md
Registry records: 40
Classes: hook=14, rule=8, skill=6, settings-hook-registration=11, gitignore-pattern=1
Field counts: template_path=28, target_path=28, target_settings_path=11, event=11, hook_filename=11, pattern=1, comment=1
Current ownership field counts: path_glob=0, ownership=0, upgrade_policy=0, adopter_divergence_policy=0, workflow_targets=0
Agent Red doctor: exits 1 and fails on "groundtruth.toml not found"
Agent Red upgrade dry-run: exits 0 with one SKIP for missing groundtruth.toml
```

Commands run from
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
git status --short -- groundtruth.db requirements-local.txt requirements-test.txt
git ls-files groundtruth.db requirements-local.txt requirements-test.txt
rg -n "groundtruth-kb|v0\.2\.1" requirements-local.txt requirements-test.txt
```

Observed:

```text
 M groundtruth.db
 M requirements-local.txt
 M requirements-test.txt
groundtruth.db
requirements-local.txt
requirements-test.txt
requirements-local.txt:17:groundtruth-kb[web,search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1
requirements-test.txt:49:groundtruth-kb[search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1
```

## Required Action Items For Prime

1. Proceed with implementation on a GT-KB feature branch, not in Agent Red.
2. Satisfy conditions C1-C3 during implementation.
3. Include the proposed test catalog plus the condition-specific tests in the
   implementation branch.
4. File the post-implementation bridge report as the next numbered document.
5. In that report, include full test results, ruff/format/mypy evidence,
   generated Agent Red classification evidence, `doctor` no-weakening evidence,
   helper regression evidence, and byte-identical Agent Red pre/post
   `git status --short` captures.

