# GT-KB Canonical Credential-Patterns Module - Codex Review of Revision 007

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-credential-patterns-canonical-007.md`
**Prior versions reviewed:** `bridge/gtkb-credential-patterns-canonical-001.md` through `-006.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit:** `a3fa4d2`

## Claim

Revision `-007` addresses the two remaining `-006` blockers well enough to
approve implementation.

The fallback catalog is now inline in `credential-scan.py`, so the prior
sidecar delivery gap across scaffold, upgrade, and doctor no longer applies.
The source-to-canonical mapping gate is now tied to an immutable
pre-migration inventory fixture, avoiding the tautology risk where tests read
only post-migration canonical views.

This GO approves the implementation bridge subject to the implementation
conditions below. It does not approve a post-implementation verification in
advance.

## Evidence Reviewed

- `bridge/gtkb-credential-patterns-canonical-001.md` through `-007.md`
- Parent scope GO: `bridge/gtkb-operational-skills-tier-a-004.md`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\credential-scan.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_governance_hooks.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\pyproject.toml`

Verification commands:

```text
git rev-parse --short HEAD
# a3fa4d2

AST inventory check:
# templates/hooks/credential-scan.py {'CREDENTIAL_PATTERNS': 13, 'OUTPUT_PATTERNS': 2}
# src/groundtruth_kb/db.py {'_REDACTION_PATTERNS': 18}

python -m pytest tests/test_deliberations.py::TestRedaction -q --tb=short -p no:cacheprovider
# 20 passed, 1 warning

python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q --tb=short -p no:cacheprovider
# 2 passed, 1 warning
```

Direct source evidence:

- DB redaction currently has 18 entries at `src/groundtruth_kb/db.py:4158-4189`,
  including 15 credential entries and 3 PII entries.
- Bash credential scanning currently has 13 credential entries and 2 output
  detectors at `templates/hooks/credential-scan.py:21-51`.
- The hook's current consumer contract is still `(pattern, description)` in
  `_check_command()` at `templates/hooks/credential-scan.py:62-70`.
- New-project scaffold copies `templates/hooks/*.py` at
  `src/groundtruth_kb/project/scaffold.py:169-172` and fills missing bridge
  hooks at `src/groundtruth_kb/project/scaffold.py:261-265`.
- Upgrade already manages `.claude/hooks/credential-scan.py` through
  `_MANAGED_HOOKS` at `src/groundtruth_kb/project/upgrade.py:27-34`.
- Doctor's bridge hook requirement already includes `credential-scan.py` at
  `src/groundtruth_kb/project/doctor.py:318-324`.
- The templates tree is force-included in the wheel at `pyproject.toml:68-69`.

## Findings

No blocking findings remain.

### 1. Resolved - Inline fallback removes the sidecar delivery gap

**Evidence:**

- Revision `-007` removes `_standalone_fallback.py` and keeps the fallback
  catalog at module scope inside `templates/hooks/credential-scan.py`:
  `bridge/gtkb-credential-patterns-canonical-007.md:51-89`.
- Revision `-007` explicitly states no sidecar file is staged in fallback
  tests and no `_MANAGED_HOOKS`, scaffold, or doctor delivery-surface entries
  are required: `bridge/gtkb-credential-patterns-canonical-007.md:166-172`
  and `bridge/gtkb-credential-patterns-canonical-007.md:345-354`.
- Target-repo delivery paths already deliver or check `credential-scan.py`
  itself: scaffold at `src/groundtruth_kb/project/scaffold.py:169-172` and
  `src/groundtruth_kb/project/scaffold.py:261-265`, upgrade at
  `src/groundtruth_kb/project/upgrade.py:27-34`, and doctor at
  `src/groundtruth_kb/project/doctor.py:318-324`.

**Risk/impact:**

The prior `-006` risk was that an upgraded adopter could receive
`credential-scan.py` without the sidecar file needed for standalone fallback.
Inlining the fallback catalog removes that failure mode.

**Required implementation condition:**

Keep the fallback catalog fully inline in `credential-scan.py`. Do not add a
hook-adjacent fallback sidecar in this implementation unless a new bridge
revision also covers scaffold, upgrade, and doctor delivery for that sidecar.

### 2. Resolved - Immutable pre-migration fixture closes the mapping tautology

**Evidence:**

- Revision `-007` requires
  `tests/fixtures/credential_pattern_source_inventory_pre_migration.json` as
  an immutable snapshot of the current source inventory:
  `bridge/gtkb-credential-patterns-canonical-007.md:185-258`.
- The proposed fixture contains all 33 current source entries: 18 DB redaction,
  13 Bash credential, and 2 Bash output entries:
  `bridge/gtkb-credential-patterns-canonical-007.md:199-247`.
- The refreshed mapping test reads the fixture rather than
  `KnowledgeDB._REDACTION_PATTERNS` or hook adapter outputs after migration:
  `bridge/gtkb-credential-patterns-canonical-007.md:260-315`.
- Current source counts were re-verified by AST inventory:
  `templates/hooks/credential-scan.py {'CREDENTIAL_PATTERNS': 13, 'OUTPUT_PATTERNS': 2}`
  and `src/groundtruth_kb/db.py {'_REDACTION_PATTERNS': 18}`.

**Risk/impact:**

The prior `-006` risk was that the migration could drop a source pattern and
still pass by comparing the new catalog to itself. A frozen source fixture
prevents that, provided the fixture is captured from `a3fa4d2` before the
consumer migrations are applied.

**Required implementation condition:**

Create the fixture before or alongside the migration using the `a3fa4d2`
pre-migration inventory, and make the mapping-completeness test fail if any
fixture entry lacks a migrated or fixture-proven-deduplicated canonical target.
The post-implementation report must include the final mapping summary and the
mapping test result.

## Implementation Conditions

1. Preserve the non-overloaded scope API from `-005`/`-007`: no `Scope.ALL`;
   `scan(scope=None)` scans all specs, while explicit scopes narrow behavior.
2. Preserve a credential-safe public `Match` API with no `matched_text` or
   other public raw-credential field.
3. Keep the Bash hook adapter shape explicit:
   `bash_credential_pattern_list()` and `bash_output_pattern_list()` must
   return `(pattern, description)` tuples compatible with the existing
   `_check_command()` contract.
4. Add the inline fallback parity test required by `-007`, comparing regex
   pattern strings, flags, and descriptions between the inline fallback and
   canonical Bash adapters.
5. Add a canonical-mode hook test that asserts the hook actually used the
   canonical catalog, not only that it denied a credential. The existing
   `CANONICAL_CATALOG_USED` / `FALLBACK_CATALOG_USED` marker mechanism is
   sufficient. This prevents broad `ImportError` fallback behavior from masking
   a broken canonical import path.
6. Run and report the targeted parity commands from this review, plus the new
   per-pattern, mapping, scope, inline-fallback, and `python -S` fallback-mode
   tests. If full-suite, ruff, or mypy gates are skipped, the post-implementation
   report must say so explicitly and explain why.

## Decision Needed From Owner

None. Prime can proceed with the implementation bridge under the conditions
above.
