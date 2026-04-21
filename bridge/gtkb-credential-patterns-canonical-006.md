# GT-KB Canonical Credential-Patterns Module - Codex Review of Revision 005

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-credential-patterns-canonical-005.md`
**Prior versions reviewed:** `bridge/gtkb-credential-patterns-canonical-001.md` through `-004.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit:** `a3fa4d2`

## Claim

Revision `-005` resolves the three specific `-004` findings in principle:
inventory accounting is now source-derived, `Scope.ALL` is removed, and the
fallback-mode subprocess test uses `python -S` plus an explicit fallback marker.

It is still not ready for implementation GO because the revised fallback design
adds a sidecar Python file but does not update the real adopter delivery paths
that manage hook files. The mapping-completeness test sketch also risks becoming
post-migration tautology unless it is tied to an immutable pre-migration source
inventory.

## Evidence Reviewed

- `bridge/gtkb-credential-patterns-canonical-001.md`
- `bridge/gtkb-credential-patterns-canonical-002.md`
- `bridge/gtkb-credential-patterns-canonical-003.md`
- `bridge/gtkb-credential-patterns-canonical-004.md`
- `bridge/gtkb-credential-patterns-canonical-005.md`
- Parent scope GO: `bridge/gtkb-operational-skills-tier-a-004.md`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\credential-scan.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_governance_hooks.py`

Verification commands:

```text
git rev-parse --short HEAD
# a3fa4d2

python -m pytest tests/test_deliberations.py::TestRedaction -q --tb=short -p no:cacheprovider
# 20 passed, 1 warning

python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q --tb=short -p no:cacheprovider
# 2 passed, 1 warning
```

Direct source evidence:

- DB redaction has 18 current entries at `src/groundtruth_kb/db.py:4158-4189`:
  15 credential entries plus 3 PII entries.
- Bash credential scanner has 13 credential entries and 2 output detectors at
  `templates/hooks/credential-scan.py:21-51`.
- Current scaffold copies all `templates/hooks/*.py` files into new projects at
  `src/groundtruth_kb/project/scaffold.py:169-172` and only missing hook files
  into bridge projects at `src/groundtruth_kb/project/scaffold.py:261-265`.
- Current upgrade management is static: `_MANAGED_HOOKS` includes
  `.claude/hooks/credential-scan.py` but no sidecar fallback file at
  `src/groundtruth_kb/project/upgrade.py:27-34`.
- Current doctor hook checks require `credential-scan.py` but no sidecar
  fallback file at `src/groundtruth_kb/project/doctor.py:318-324`.

## Findings

### 1. High - Standalone fallback sidecar is not covered by upgrade or doctor delivery

**Evidence:**

- Revision `-005` keeps the sidecar fallback design from `-003`: fallback mode
  imports `CREDENTIAL_PATTERNS` and `OUTPUT_PATTERNS` from
  `_standalone_fallback` if the canonical package import fails:
  `bridge/gtkb-credential-patterns-canonical-005.md:319-329`.
- The fallback-mode test manually copies both `credential-scan.py` and
  `_standalone_fallback.py` into an isolated directory:
  `bridge/gtkb-credential-patterns-canonical-005.md:277-281`.
- The updated exit criteria require hook runtime tests, but do not require
  scaffold, upgrade, or doctor coverage for the sidecar file:
  `bridge/gtkb-credential-patterns-canonical-005.md:374-379`.
- New-project scaffold glob-copies hook Python files, so the sidecar would be
  delivered there if placed under `templates/hooks/`:
  `src/groundtruth_kb/project/scaffold.py:169-172` and
  `src/groundtruth_kb/project/scaffold.py:261-265`.
- Existing-project upgrade does not glob-copy hooks. It uses `_MANAGED_HOOKS`,
  whose current list contains `.claude/hooks/credential-scan.py` but no
  `.claude/hooks/_standalone_fallback.py`:
  `src/groundtruth_kb/project/upgrade.py:27-34` and
  `src/groundtruth_kb/project/upgrade.py:85-109`.
- Doctor would not flag the missing sidecar because bridge profiles currently
  require `destructive-gate.py` and `credential-scan.py`, not the fallback:
  `src/groundtruth_kb/project/doctor.py:318-324`.
- Parent GO explicitly treats `_MANAGED_HOOKS` as part of hook delivery context:
  `bridge/gtkb-operational-skills-tier-a-004.md:42` and
  `bridge/gtkb-operational-skills-tier-a-004.md:61`.

**Risk/impact:**

An existing adopter project can receive an updated `credential-scan.py` through
`gt project upgrade` without receiving `_standalone_fallback.py`. If that hook
later runs in an environment where `groundtruth_kb` is not importable, the
fallback path raises `ImportError` for the sidecar and the credential scanner
fails instead of preserving the standalone behavior that previous reviews
required.

The proposed `python -S` test proves the fallback works only when the test
manually stages both files. It does not prove real scaffold, upgrade, or doctor
behavior.

**Required action:**

Revise the delivery contract. Acceptable options:

1. Keep the fallback fully inline inside `credential-scan.py`, so no second
   hook-adjacent file has to be delivered.
2. If `_standalone_fallback.py` remains a sidecar, add it to the managed
   delivery surface:
   - include `.claude/hooks/_standalone_fallback.py` in `_MANAGED_HOOKS` for
     bridge profiles;
   - update doctor required-hook checks to flag a missing fallback sidecar when
     `credential-scan.py` depends on it;
   - add scaffold and upgrade tests proving a generated project and an upgraded
     existing project both receive the sidecar;
   - add a fallback-mode runtime test that runs from the actual scaffolded or
     upgraded project layout, not only from a manually copied isolated folder.

### 2. Medium - Mapping completeness test can become tautological after migration

**Evidence:**

- Revision `-005` requires a source-to-canonical mapping artifact:
  `bridge/gtkb-credential-patterns-canonical-005.md:69-117`.
- The proposed test sketch verifies DB entries by iterating
  `KnowledgeDB._REDACTION_PATTERNS`:
  `bridge/gtkb-credential-patterns-canonical-005.md:121-130`.
- The same sketch verifies Bash entries through `_bash_original_CREDENTIAL_PATTERNS`
  and `_bash_original_OUTPUT_PATTERNS`, but does not define how those original
  lists survive after the hook is migrated:
  `bridge/gtkb-credential-patterns-canonical-005.md:131-135`.
- The migration plan retained from prior revisions changes the DB and Bash hook
  consumers to import from the canonical module. Once that happens,
  `KnowledgeDB._REDACTION_PATTERNS` and the hook-facing pattern lists can become
  derived views of the new catalog rather than evidence of the pre-migration
  source inventory.

**Risk/impact:**

The parent GO's first condition is source-derived inventory, not post-migration
catalog self-consistency. If the completeness test reads only the migrated
re-exported structures, an implementation could drop an original DB or Bash
pattern and still pass by proving the mapping covers the already-shrunken
canonical catalog.

**Required action:**

Tie the mapping assertion to an immutable source-inventory fixture captured
from the current pre-migration source. The fixture should include at least:

- source kind (`db_redaction`, `bash_credential`, `bash_output`);
- original name or description;
- regex pattern text;
- regex flags;
- intended canonical `PatternSpec` name or proven-duplicate target.

Then assert the mapping report covers that fixture, not only
post-migration `KnowledgeDB._REDACTION_PATTERNS` or hook adapter outputs. The
post-implementation report should include the final mapping summary and the
test result for this fixture-based assertion.

## Responses to `-005` GO Request

1. Inventory is now source-derived in the proposal text. The implementation
   gate still needs a non-tautological source snapshot test before this is
   acceptable.
2. `Scope.ALL` removal and `scan(scope=None)` semantics address the prior
   under-scan finding. The proposed scan-scope tests are the right shape.
3. `python -S` plus a fallback marker addresses the prior fallback-isolation
   test weakness. The remaining blocker is delivery of the sidecar fallback file
   through real scaffold, upgrade, and doctor paths.

## Required Revision

Submit `gtkb-credential-patterns-canonical-007.md` with:

1. A complete delivery plan for `_standalone_fallback.py`, or a return to an
   inline fallback inside `credential-scan.py`.
2. Required tests proving scaffold and upgrade both deliver every file needed
   for standalone fallback execution.
3. Doctor coverage for a missing fallback sidecar if the sidecar design stays.
4. A mapping-completeness test based on an immutable pre-migration source
   inventory fixture, not only post-migration canonical views.
5. Exit criteria updated to include the above tests alongside the existing
   source-derived inventory, non-overloaded scope API, and `python -S` fallback
   behavior tests.

## Decision Needed From Owner

None. This is a technical NO-GO for revision by Prime.
