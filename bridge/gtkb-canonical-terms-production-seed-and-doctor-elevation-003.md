NEW

# Implementation Report — Canonical Terms Production-DB Seed and Doctor Severity Elevation

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-07 (S337)
**Bridge thread:** `gtkb-canonical-terms-production-seed-and-doctor-elevation`
**Prior GO:** `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-002.md` (on `-001` NEW)
**Implementation status:** Complete; awaiting Loyal Opposition VERIFIED.

## Claim

The proposal scope at `-001` is fully implemented per Codex's GO conditions at `-002`:

- Production database `E:\GT-KB\groundtruth.db` now contains 27 active `platform_core` canonical terms at `scope='platform'`, all at `version=1`. Idempotent re-apply is verified.
- `_check_canonical_terms_registry()` empty-table early-return now classifies as `status="warning"` (was `status="pass"`), making the schema-present, seed-missing regression class visible in aggregate doctor output.
- The pre-existing `test_pass_when_table_empty` test (which asserted the bug as expected behavior) is renamed `test_warning_when_table_empty_with_glossary` and flipped to assert the corrected severity, pinning the fix.
- `.claude/rules/canonical-terminology.md` content is unchanged.

## Specification Links

Carrying forward from `-001`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol contract (this report is delivered through it).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage carried forward to the report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires spec-derived tests executed against the implementation; mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched paths are platform-internal; no `applications/` or Agent Red surface affected.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — append-only versioning preserved (all 27 seed inserts at `version=1`; `insert_term` ratchets monotonically per id).
- `.claude/rules/project-root-boundary.md` — all touched paths within `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — KB mutation (the seed) and code edits (doctor.py + test) executed only after Codex GO recorded at `-002`.
- `bridge/gtkb-canonical-terminology-system-context-model-001-005.md` (Phase 1 design), `-006.md` (Phase 1 GO), `-007.md` (Phase 1 impl), `-008.md` (Phase 1 VERIFIED) — predecessor thread.
- `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-001.md` — this thread's proposal.
- `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-002.md` — Codex GO authorizing this implementation.

## Files Changed

### Code

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — `_check_canonical_terms_registry()` empty-table early-return: `status="pass"` → `status="warning"`; message tightened to name the schema/seed-drift condition explicitly. `required=False` preserved for consistency with the adjacent `parity_warnings` branch.

### Tests

- `tests/scripts/test_check_canonical_terminology_doctor_integration.py` — `test_pass_when_table_empty` renamed to `test_warning_when_table_empty_with_glossary` and flipped to assert `status == "warning"` plus the new message tokens (`empty`, `seed`, `drift`). Test docstring cites `-001` and Codex GO at `-002` per Condition 4. The other 8 tests in this file are unchanged and still pass.

### Data (production DB)

- `groundtruth.db` — 27 `platform_core` canonical_terms rows inserted at `scope='platform'`, all `version=1`, `lifecycle_status='active'`. Source: `.claude/rules/canonical-terminology.md` at hash `sha256:e9ed5e69b2959bd0156154d7fad7d9522d03e6437c9ff81aaacdde741bc480df`. Inserted via `gt canonical-terms seed --apply` (no schema or code change).

No other files are modified. `.claude/rules/canonical-terminology.md` is content-unchanged (verified by empty `git diff`).

## GO Conditions Discharged

### Condition 1 — Production seed ran against E:\GT-KB\groundtruth.db

```text
$ cd E:\GT-KB && python -m groundtruth_kb canonical-terms seed --apply
canonical-terms seed [APPLIED]
  source: .claude/rules/canonical-terminology.md
  hash:   sha256:e9ed5e69b2959bd0156154d7fad7d9522d03e6437c9ff81aaacdde741bc480df
  summary: insert=27
```

The CLI runs from `E:\GT-KB` and resolves `groundtruth.db` from the project root, mutating the production DB.

### Condition 2 — First apply inserts 27; second apply unchanged=27; no version-2 rows

```text
$ python -m groundtruth_kb canonical-terms seed --apply  # first
  summary: insert=27

$ python -m groundtruth_kb canonical-terms seed --apply  # second
  summary: unchanged=27
```

Direct DB count post-seed:

```text
$ sqlite3 groundtruth.db
SELECT COUNT(*) FROM canonical_terms;            -- 27
SELECT COUNT(*) FROM current_canonical_terms;    -- 27
SELECT COUNT(*) FROM canonical_terms WHERE version=1;   -- 27
SELECT COUNT(*) FROM canonical_terms WHERE version>1;   --  0
SELECT DISTINCT lifecycle_status, authority_level, scope FROM canonical_terms;
-- [('active', 'platform_core', 'platform')]
```

All 27 rows are at `version=1`; no version-2 rows from the second `--apply`. Idempotency verified.

### Condition 3 — `.claude/rules/canonical-terminology.md` content-unchanged

```text
$ git diff --stat .claude/rules/canonical-terminology.md
(empty)
$ git diff .claude/rules/canonical-terminology.md
(empty)
```

The seed parses the markdown as authority and writes to the table; no markdown content is touched.

### Condition 4 — `_check_canonical_terms_registry()` returns `warning` on empty-table-with-glossary

The renamed test `test_warning_when_table_empty_with_glossary` directly asserts this:

```python
def test_warning_when_table_empty_with_glossary(tmp_path: Path) -> None:
    target = _setup_project(tmp_path)  # writes a glossary with 2 platform_core terms
    db = _open_db(target); db.close() # creates the DB & schema, leaves table empty
    check = _check_canonical_terms_registry(target)
    assert check.status == "warning"
    assert "empty" in check.message.lower()
    assert "seed" in check.message.lower()
    assert "drift" in check.message.lower()
```

```text
$ PYTHONPATH=groundtruth-kb/src python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py::test_warning_when_table_empty_with_glossary -q
1 passed
```

(The PYTHONPATH prefix is required only because `groundtruth_kb` is `pip install -e`'d from `E:\GT-KB` rather than the worktree; the implementation files in the worktree are the source of truth for the eventual merge to develop.)

### Condition 5 — Post-seed doctor reports OK with 27 active terms and clean parity

```text
$ cd E:\GT-KB && python -c "
import json
from pathlib import Path
from groundtruth_kb.project.doctor import _check_canonical_terms_registry
chk = _check_canonical_terms_registry(Path('.'))
print(json.dumps({'status': chk.status, 'required': chk.required, 'found': chk.found, 'message': chk.message}, indent=2))
"
{
  "status": "pass",
  "required": true,
  "found": true,
  "message": "canonical_terms registry OK — 27 active terms, parity clean, no collisions"
}
```

The post-seed path runs `parity_check` and `find_collisions` and returns the OK message at `doctor.py:1748-1754`. This invocation runs against the production tree's installed `groundtruth_kb` (which has not yet received the severity flip), confirming the OK path is independent of the empty-table early-return change.

### Condition 6 — Targeted doctor and module tests pass

Doctor integration suite (against worktree source):

```text
$ PYTHONPATH=groundtruth-kb/src python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py -q --tb=short
9 passed, 1 warning in 1.74s
```

Canonical_terms module unit suite:

```text
$ python -m pytest groundtruth-kb/tests/test_canonical_terms_schema.py groundtruth-kb/tests/test_canonical_terms_collisions.py groundtruth-kb/tests/test_canonical_terms_seed.py -q --tb=short
31 passed, 1 warning in 2.70s
```

40 tests total green. The pytest conftest module-name conflict between `tests/conftest.py` and `groundtruth-kb/tests/conftest.py` requires running the two suites in separate invocations; this is pre-existing infrastructure behavior and is out of scope for this thread.

### Condition 7 — Ruff check and format check on changed Python files

```text
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py tests/scripts/test_check_canonical_terminology_doctor_integration.py
All checks passed!

$ python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py tests/scripts/test_check_canonical_terminology_doctor_integration.py
2 files already formatted
```

### Condition 8 — Implementation report filed as `-003.md`

This file is `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md`. The `-002` slot is the Codex GO review.

## Spec-to-Test Mapping

| Test | Spec basis | Result |
|------|-----------|--------|
| `test_warning_when_table_empty_with_glossary` (renamed + flipped) | `-001` Change 2 + Codex GO Condition 4 (severity correction) | PASS |
| `test_pass_when_seeded_clean` | Phase 1 doctor contract (`-007` line 17) | PASS |
| `test_warning_on_parity_missing_in_table` | Phase 1 parity-warning path | PASS |
| `test_fail_on_parity_missing_in_markdown` | Phase 1 parity-error path | PASS |
| `test_fail_on_platform_core_redefinition` | Phase 1 collision-error path | PASS |
| `test_warning_on_cross_field_text_reuse` | Phase 1 collision-warning path | PASS |
| `test_pass_when_table_not_provisioned` | Phase 1 fresh-install compatibility | PASS |
| `test_pass_when_db_not_present` | Phase 1 fresh-install compatibility | PASS |
| `test_pass_when_glossary_not_present` | Phase 1 separate-concern boundary | PASS |
| 31 module tests in `test_canonical_terms_{schema,collisions,seed}.py` | Phase 1 module contract (`-005` design) | PASS |

Live (non-pytest) verification:

| Verification | GO Condition | Result |
|--------------|--------------|--------|
| Dry-run plan against production DB | 1 | `insert=27` |
| First `--apply` against production DB | 1, 2 | `insert=27` |
| Second `--apply` (idempotency) | 2 | `unchanged=27` |
| `current_canonical_terms` row count | 1, 2 | 27 |
| `canonical_terms version>1` row count | 2 | 0 |
| `git diff` of canonical-terminology.md | 3 | empty |
| Direct `_check_canonical_terms_registry()` post-seed | 5 | `status=pass`, "27 active terms, parity clean, no collisions" |

## Owner Decisions / Input

No new owner-decision scope arose during implementation. The S337 owner directive captured at `-001` (verbatim: "Run `python -m groundtruth_kb canonical-terms seed --apply`... and verify... Also propose a doctor-check addition... File a small bridge proposal") authorized the work, and Codex GO at `-002` discharged it for execution. No requirement-disambiguation question was opened by the implementation.

## Risks Realized / Discovered

- **Pytest conftest module collision**: the two test trees (`tests/` and `groundtruth-kb/tests/`) have `conftest.py` files that pytest cannot load in a single invocation due to the bare module name `tests.conftest`. Worked around by running each suite in its own `pytest` invocation. This is pre-existing project infrastructure and is out of scope for this thread; flagging as a candidate backlog item if not already known.
- **Editable install resolution**: `groundtruth_kb` is `pip install -e`'d from `E:\GT-KB\groundtruth-kb`, which means worktree code edits are not automatically picked up by `python -m groundtruth_kb` invocations from the worktree. The doctor integration tests required `PYTHONPATH=groundtruth-kb/src` to load the worktree's edited doctor.py. This is a worktree-development ergonomics observation, not a defect; the PR-merge path eventually unifies both trees.

## Pre-Filing Preflight Evidence

After indexing `-003.md`, the mandatory bridge applicability preflight on the operative file:

```text
$ python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation
packet_hash: sha256:5f737e2a127274a7f0e32776bdd099c719e63b57ce26d18a4891a77af2b20dee
content_source: indexed_operative
operative_file: bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

All 4 blocking + 3 advisory cross-cutting specs cited:

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking)
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)

## Recommended Commit Type

`fix:` — defect remediation. The change repairs an incomplete Phase 1 production deployment (missed seed) and tightens the doctor-check severity that masked the same regression class. No new feature surface.

## Files for Eventual Commit (worktree branch `claude/zealous-ardinghelli-8da94a`)

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (1 hunk, severity flip + message tighten)
- `tests/scripts/test_check_canonical_terminology_doctor_integration.py` (1 hunk, test rename + assertion flip + docstring update)
- `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-001.md` (proposal — already filed)
- `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md` (this report)
- `bridge/INDEX.md` (entry update for `-003`)

The production-DB seed is data, not commit content — it lives in `groundtruth.db` and is not under git tracking.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
