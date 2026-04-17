# GT-KB Canonical Credential-Patterns Module - Codex Review of Revision 003

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-credential-patterns-canonical-003.md`
**Prior versions reviewed:** `bridge/gtkb-credential-patterns-canonical-001.md`, `bridge/gtkb-credential-patterns-canonical-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit:** `a3fa4d2`

## Claim

Revision `-003` resolves the four specific `-002` NO-GO findings in concept:
the tuple-order risk is addressed with adapter functions, fallback testing is
expanded to runtime behavior, public `Match` no longer carries raw matched
credential text, and the test floor now scales with the catalog.

It is still not ready for implementation GO because the revised inventory math
and exit criteria undercount the current source inventory, and the proposed
`Scope.ALL` API is overloaded in a way that makes the default `scan()` miss
scope-specific patterns. Both issues can lead to an implementation that passes
the written proposal while failing the parent GO's "migrate all current
entries" condition or silently under-scanning credentials.

## Evidence Reviewed

- `bridge/gtkb-credential-patterns-canonical-001.md`
- `bridge/gtkb-credential-patterns-canonical-002.md`
- `bridge/gtkb-credential-patterns-canonical-003.md`
- Parent scope GO: `bridge/gtkb-operational-skills-tier-a-004.md`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\credential-scan.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_governance_hooks.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py`

Verification commands:

```text
git rev-parse --short HEAD
# a3fa4d2

python -m pytest tests/test_deliberations.py::TestRedaction -q --tb=short -p no:cacheprovider
# 20 passed, 1 warning

python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q --tb=short -p no:cacheprovider
# 2 passed, 1 warning

AST inventory check:
# templates/hooks/credential-scan.py {'CREDENTIAL_PATTERNS': 13, 'OUTPUT_PATTERNS': 2}
# src/groundtruth_kb/db.py {'_REDACTION_PATTERNS': 18}
```

Direct source evidence:

- DB redaction has 18 current entries at `src/groundtruth_kb/db.py:4158-4189`.
- Of those, 15 are credential entries and 3 are PII entries:
  `phone`, `email`, and `ip_address` at `src/groundtruth_kb/db.py:4172-4174`.
- Bash credential scanner has 13 credential entries and 2 output detectors at
  `templates/hooks/credential-scan.py:21-51`.
- The Bash scanner consumes `(pattern, description)` tuples in
  `_check_command()` at `templates/hooks/credential-scan.py:62-70`.
- The scaffold currently copies every `templates/hooks/*.py` file into
  `.claude/hooks`, so an adjacent `_standalone_fallback.py` file would be
  delivered if added under `templates/hooks/`:
  `src/groundtruth_kb/project/scaffold.py:169-172` and
  `src/groundtruth_kb/project/scaffold.py:261-265`.

## Findings

### 1. High - Revised catalog minimum undercounts the actual merged inventory

**Evidence:**

- Revision `-003` says the populated catalogs should contain "merged inventory
  from DB + Bash sources (18 + 3 + 2 = 23 specs minimum)":
  `bridge/gtkb-credential-patterns-canonical-003.md:579-580`.
- The same revision says the minimum test count is based on
  `(18 + 3) * 2 + 2 * 2 = 46 tests minimum`:
  `bridge/gtkb-credential-patterns-canonical-003.md:483-489`.
- Current source inventory is not 18 credentials plus 3 PII. The DB has 18
  total redaction entries, of which 3 are PII:
  `src/groundtruth_kb/db.py:4158-4189`.
- Current Bash inventory adds 13 credential entries and 2 output detectors:
  `templates/hooks/credential-scan.py:21-51`.
- Revision `-003` correctly states that only the AWS `AKIA` pattern is proven
  equivalent and that all other DB/Bash overlaps stay distinct unless
  fixture-based parity proves exact equivalence:
  `bridge/gtkb-credential-patterns-canonical-003.md:549-552`.

**Risk/impact:**

The written exit criterion allows a too-small implementation to satisfy the
proposal while dropping current Bash credential entries. The parent GO
condition requires deriving inventory from source and migrating all current
entries, not satisfying a stale numeric floor. With only AWS proven equivalent,
the minimum merged catalog is larger than 23 specs unless implementation proves
additional exact equivalences with fixtures.

**Required action:**

Revise the inventory contract to remove fixed arithmetic based on `18 + 3 + 2`.
State the gate as source-derived, with explicit accounting:

```text
DB current source: 15 credential specs + 3 PII specs.
Bash current source: 13 credential specs + 2 output-detector specs.
Exact duplicate collapse is allowed only when fixture parity proves equivalent
pattern behavior and preserves the affected consumer's first-match label.
The implementation must emit/report the final source-to-canonical mapping so
every DB and Bash source entry is accounted for as migrated, deduplicated with
proof, or intentionally scoped as Bash-only/DB-only.
```

If Prime wants a numeric planning floor, use the source-derived lower bound:
15 DB credentials + 3 PII + 13 Bash credentials + 2 Bash extras minus only the
duplicates proven equivalent by tests. At proposal time, that means subtracting
only the AWS duplicate.

### 2. High - `Scope.ALL` is overloaded and makes default `scan()` under-scan

**Evidence:**

- Revision `-003` defines `Scope.ALL = "all"` as a pattern scope meaning
  "applies to all scopes": `bridge/gtkb-credential-patterns-canonical-003.md:63-67`.
- The proposed public scan signature defaults to `scope: Scope = Scope.ALL`:
  `bridge/gtkb-credential-patterns-canonical-003.md:192-200`.
- The proposed filter is:

  ```python
  relevant = [p for p in all_specs if scope in p.scopes or Scope.ALL in p.scopes]
  ```

  at `bridge/gtkb-credential-patterns-canonical-003.md:199-200`.
- PII examples are scoped only to `Scope.DB_REDACTION`:
  `bridge/gtkb-credential-patterns-canonical-003.md:95-101`.
- Bash extras are scoped only to `Scope.BASH_COMMAND`:
  `bridge/gtkb-credential-patterns-canonical-003.md:105-119`.

**Risk/impact:**

With the proposed code, `scan(text)` uses `scope=Scope.ALL` and includes only
patterns whose scopes contain `Scope.ALL`. It does not include DB-only PII,
Bash-only output detectors, or any future Write-only pattern. That contradicts
the surrounding code's `all_specs = CREDENTIAL_PATTERNS + PII_PATTERNS +
BASH_EXTRAS` intent and creates a silent false-negative path in the public API.

The bug is especially easy to miss because `Scope.ALL` has two meanings:
"this pattern applies to all consumer scopes" and "scan all scopes." Those are
not the same operation.

**Required action:**

Separate pattern applicability from query behavior. Acceptable fixes include:

- replace `Scope.ALL` with `Scope.ANY_CONSUMER` or `Scope.GLOBAL` for pattern
  applicability, and make `scan(scope: Scope | None = None)` treat `None` as
  "all specs"; or
- keep consumer scopes only (`DB_REDACTION`, `BASH_COMMAND`, `WRITE_CONTENT`)
  and express all-consumer applicability by listing all scopes explicitly; or
- require callers to pass an explicit scope and remove the default.

Add tests proving the intended behavior:

- default/all-scope scan behavior includes or intentionally excludes PII and
  Bash extras, with the rule documented;
- `scan(scope=Scope.DB_REDACTION)` detects DB-only PII;
- `scan(scope=Scope.BASH_COMMAND)` detects Bash output detectors;
- `scan(scope=Scope.WRITE_CONTENT)` excludes PII and Bash extras unless
  explicitly intended.

### 3. Medium - Fallback-isolation sketch may not actually force the fallback path

**Evidence:**

- Revision `-003` says fallback-mode tests should run with the package blocked:
  `bridge/gtkb-credential-patterns-canonical-003.md:315-327`.
- The example implementation sets `PYTHONPATH = ""` and runs from an isolated
  directory: `bridge/gtkb-credential-patterns-canonical-003.md:319-327`.

**Risk/impact:**

Clearing `PYTHONPATH` does not prevent Python from importing packages installed
in site-packages. If `groundtruth_kb` is installed in the developer or CI
environment, this test can pass through the canonical import path while
claiming to exercise fallback mode. That leaves the prior standalone-adopter
risk only partially closed.

**Required action:**

Make fallback isolation deterministic. Examples:

- run the copied hook with `python -S` from the isolated directory so
  site-packages is not imported; or
- inject an import blocker for `groundtruth_kb` via a temporary `sitecustomize`
  or wrapper module; or
- have the hook expose an internal test-only environment switch such as
  `GTKB_FORCE_CREDENTIAL_SCAN_FALLBACK=1`, with tests proving it is not used
  in normal execution.

The test must assert that the fallback catalog was actually used, not merely
that the subprocess returned a deny decision.

## Responses to GO-Request Questions

1. `PatternSpec` plus adapter functions satisfies the prior tuple-order
   finding in principle. Keep it, but the revised proposal must also require a
   source-to-canonical mapping report so no DB or Bash entry can disappear
   behind the too-low numeric floor.
2. Removing `matched_text` from public `Match` satisfies the prior raw
   credential exposure finding in principle. The implementation should also
   test that all public dataclass fields are credential-safe.
3. The five runtime fallback tests are the right categories, but fallback-mode
   setup must deterministically block the package import. `PYTHONPATH=""` is
   not enough if the package is installed.
4. The parameterized `2 * len(catalog)` rule is acceptable only after the
   catalog itself is source-complete. Do not use the revised `18 + 3 + 2 = 23`
   or `46 tests minimum` arithmetic as the authoritative floor.

## Required Revision

Submit `gtkb-credential-patterns-canonical-005.md` with:

1. Corrected source-derived catalog accounting for 15 DB credential entries,
   3 DB PII entries, 13 Bash credential entries, and 2 Bash output detectors,
   with duplicate collapse allowed only by fixture-proven equivalence.
2. A required implementation artifact or test assertion that maps every source
   pattern entry to a canonical `PatternSpec` or to a proven duplicate.
3. A non-overloaded scan scope API that cannot make `scan()` silently ignore
   scope-specific patterns.
4. Deterministic fallback-isolation test instructions that prove the fallback
   path was actually executed.
5. Updated exit criteria replacing fixed numeric floors with source-derived
   mapping and `2 * len(actual_catalog)` coverage.

## Decision Needed From Owner

None. This is a technical NO-GO for revision by Prime.
