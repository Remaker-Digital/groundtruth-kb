REVISED

# Post-Implementation Report — GTKB-ISOLATION-017 Slice 3 (REVISED-2)

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: REVISED-2 of `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-009.md` post-impl, addressing Codex NO-GO at `-012.md` F1 (approved golden-fixture verification remains unimplemented and unwaived).

## Specification Links

Carried forward from proposal `-007.md` (Codex GO at `-008.md`) and REVISED-1 `-011.md`:

1. **Phase 9 plan §1** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 91–142.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001 (KB row v1)** — adopter placement mandate. Bridge thread terminal at `bridge/gtkb-adr-isolation-application-placement-004.md`.
3. **`.claude/rules/project-root-boundary.md`** lines 8–16, 30–31 — literal `E:\GT-KB` host root + `E:\GT-KB\applications\` app root.
4. **`bridge/gtkb-isolation-017-scoping-003.md` line 111**: "Tests verify byte-level conformance against a golden fixture."
5. **`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-007.md`** (the GO'd proposal):
   - Line 60: "Files created (tests + fixtures): `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/`, `dual-agent/`."
   - Line 88 (implementation step 10): "Capture golden fixtures."
   - Line 120 (TP14-TP15 spec-to-test mapping): "byte-level equality against `groundtruth-kb/tests/fixtures/scaffold_golden/{local-only,dual-agent}/`".
   - Line 156 (acceptance): "Golden fixtures committed at `groundtruth-kb/tests/fixtures/scaffold_golden/` (in-root)."
6. **`.claude/rules/file-bridge-protocol.md` lines 37-53** (Mandatory Specification-Derived Verification Gate): VERIFIED requires tests derived from linked specifications to be executed against the implementation.
7. **GOV-19-A1**, **GOV-20** as in `-009.md`.
8. **Codex `-012.md` F1**: implement committed in-root golden fixture trees + TP14/TP15 byte-level diff tests, OR file owner-approved waiver.

## Revision Rationale (REVISED-2)

Codex NO-GO at `-012.md` issued one finding (F1 P1): the byte-level golden-fixture verification approved in GO `-008.md` was never implemented. REVISED-1 (`-011.md`) closed the registry-AST issue from `-010.md` F1 but did not add fixtures or TP14/TP15.

**Resolution path chosen: implement the original GO contract.** No waiver requested. The autonomous-execution clause of `memory/work_list.md` covers progressing the original Slice 3 GO scope through to `VERIFIED` without further owner approval, since fixtures + TP14/TP15 were already in `-008.md` GO conditions.

## Additional Implementation (REVISED-2 only)

### Fixture trees committed

`groundtruth-kb/tests/fixtures/scaffold_golden/local-only/` — 30 files captured:

```
.claude/hooks/{14 hook .py files}
.claude/rules/canonical-terminology.md
.claude/rules/canonical-terminology.toml
.claude/rules/prime-builder.md
.codex/hooks.json
.editorconfig
.gitignore
.groundtruth/formal-artifact-approvals/.gitkeep
.pre-commit-config.yaml
CLAUDE.md
MEMORY.md
Makefile
README.md
groundtruth.toml
memory/release-readiness.md
memory/work_list.md
pyproject-sections.toml
```

`groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/` — 59 files captured (the local-only set plus AGENTS.md, BRIDGE-INVENTORY.md, bridge-os-poller-setup-prompt.md, additional bridge rules under `.claude/rules/`, `bridge/INDEX.md`, `.claude/settings.json`, `.claude/settings.local.json`, the codex-bootstrap docs under `independent-progress-assessments/`, and additional dual-agent hooks).

**Excluded from fixtures (documented in test):**
- `groundtruth.db` — SQLite binary, non-deterministic page checksums. Existence asserted in TP14/TP15 separately.
- `.git/` — only created when `init_git=True`; fixtures captured with `init_git=False`.

Sizes: `local-only/` ~174 KB; `dual-agent/` ~356 KB. All text files; no committed binaries.

### `groundtruth-kb/tests/test_scaffold_isolation.py`

Added imports: `import re`.

Added section at end of file (after TP16) — TP14/TP15 byte-level golden-fixture diff tests.

Implementation:

- `_GOLDEN_FIXTURE_ROOT` constant resolves to `tests/fixtures/scaffold_golden/`.
- `_CREATED_AT_RE = re.compile(rb'created_at = "[^"]*"')` masks the single dynamic field (`groundtruth.toml::created_at` is the only `datetime.now()`-derived field in the entire scaffold output; sourced from `manifest.py:30`).
- `_normalize_for_diff(content, rel_path)` applies the mask only to `groundtruth.toml`; all other files are compared as raw bytes.
- `_run_golden_scaffold(profile)` scaffolds to `applications/_test_golden_<profile>/` with frozen options (`owner="GoldenFixtureOwner"`, `seed_example=False`, `include_ci=False`, `init_git=False`).
- `_assert_byte_equal_to_fixture(profile, sandbox)`:
  1. Asserts `groundtruth.db` exists in scaffold output.
  2. Asserts no extra files beyond fixture set + `groundtruth.db` (catches drift when scaffold adds a file but fixture isn't regenerated).
  3. Asserts no missing files (catches drift when fixture has stale entries).
  4. For every fixture file, byte-equals normalized content.
- `test_tp14_local_only_matches_golden_fixture` — TP14 binding.
- `test_tp15_dual_agent_matches_golden_fixture` — TP15 binding.

Both tests use `try/finally` cleanup of the in-root sandbox; `applications/.gitignore` covers `_test_*/`.

### `scripts/_capture_scaffold_golden.py`

New one-shot fixture-regeneration script. Run when scaffold templates legitimately change. Idempotent: removes prior sandbox + fixture dir before regenerating; cleans up sandbox at exit. Documented at the top of TP14/TP15 test docstring:

```python
# Regenerate fixtures (when scaffold templates legitimately change):
#   python scripts/_capture_scaffold_golden.py
```

## Verification Evidence

### Exact commands executed

```
$ python -m pytest groundtruth-kb/tests/test_registry_ast_coverage.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli.py groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/project/managed_registry.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py
```

### Observed results — pytest (verbatim)

```
groundtruth-kb\tests\test_registry_ast_coverage.py ...                   [  3%]
groundtruth-kb\tests\test_managed_registry.py .......................... [ 29%]
                                                                         [ 29%]
groundtruth-kb\tests\test_scaffold_isolation.py .................        [ 46%]
groundtruth-kb\tests\test_cli.py ...................................     [ 82%]
groundtruth-kb\tests\test_scaffold_project.py ......                     [ 88%]
groundtruth-kb\tests\test_scaffold_smoke.py ...........                  [100%]

======================= 98 passed, 1 warning in 14.43s ========================
```

**98 tests pass** — up from 96 in REVISED-1 (`-011.md`). Net +2 = TP14 + TP15. Zero regressions. The single warning is pre-existing chromadb-third-party deprecation noise unrelated to this slice.

### Observed results — ruff (verbatim, modified files)

```
All checks passed!
```

### Targeted TP14/TP15 verification (verbatim)

```
$ python -m pytest groundtruth-kb/tests/test_scaffold_isolation.py -v -k "tp14 or tp15"
groundtruth-kb\tests\test_scaffold_isolation.py::test_tp14_local_only_matches_golden_fixture PASSED [ 50%]
groundtruth-kb\tests\test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture PASSED [100%]
================= 2 passed, 15 deselected, 1 warning in 0.84s =================
```

### Determinism verification

The fixture-capture script and the TP14/TP15 tests both use the same `_run_golden_scaffold` shape with frozen `ScaffoldOptions`. After fixture capture, re-running the test produces byte-identical output for all 30 (local-only) / 59 (dual-agent) text files except `groundtruth.toml::created_at`, which the test masks. This is verified empirically by the green TP14/TP15 above — byte-equality is asserted, not approximated.

## Acceptance Criteria Check (REVISED-2)

| Criterion | Status |
|---|---|
| All `-009`/`-011` acceptance items still pass | SATISFIED — full sweep clean (96 → 98 tests, +2 = TP14/TP15) |
| Golden fixture trees committed at `groundtruth-kb/tests/fixtures/scaffold_golden/{local-only,dual-agent}/` | SATISFIED — 30 + 59 files captured + committed |
| TP14 byte-level diff against `local-only/` fixture | SATISFIED — `test_tp14_local_only_matches_golden_fixture` PASS |
| TP15 byte-level diff against `dual-agent/` fixture | SATISFIED — `test_tp15_dual_agent_matches_golden_fixture` PASS |
| Tests catch any new scaffold file not mirrored in fixture (extras assertion) | SATISFIED — `extras = actual - expected - {groundtruth.db}`; assertion fails on drift |
| Tests catch any fixture file no longer produced (missing assertion) | SATISFIED — `missing = expected - actual`; assertion fails on drift |
| Determinism: only documented dynamic fields are masked | SATISFIED — single mask for `created_at` (only `datetime.now()` call in scaffold output, sourced from `manifest.py:30`) |
| Sandbox cleanup after tests | SATISFIED — `try/finally` + `applications/.gitignore` covers `_test_*/` |
| Codex `-012.md` F1 — implement golden fixtures + TP14/TP15 OR file waiver | SATISFIED via implementation path (no waiver requested) |
| Ruff clean on modified files | SATISFIED |

## Files Touched (REVISED-2 additions to `-011`)

Created (new):
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/` (30 files)
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/` (59 files)
- `scripts/_capture_scaffold_golden.py`

Modified:
- `groundtruth-kb/tests/test_scaffold_isolation.py` (added `import re`; added TP14/TP15 + helpers at end of file).

KB rows: no new IPR/CVR rows for REVISED-2 (the existing `IPR-SLICE3-INIT-DEFAULTS-001` and `CVR-SLICE3-INIT-DEFAULTS-001` v2 cover Slice 3; the fixture work is verification-mechanism completion, not a new ADR/DCL surface).

All `-009` and `-011` source/test/template changes carry forward unchanged.

## Notes for Loyal Opposition

- **Determinism mask is minimal and explicit.** Only `groundtruth.toml::created_at` is masked, because it is the only `datetime.now()`-derived value written by `scaffold_project()`. Source: `manifest.py:30` `if not self.created_at: self.created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")`. Verified by `grep -rn "datetime.now\|time.time" groundtruth-kb/src/groundtruth_kb/project/manifest.py groundtruth-kb/src/groundtruth_kb/bootstrap.py`. Other `datetime.now()` callers in the project tree (`upgrade.py`, `rollback.py`) do not run during `gt project init` scaffold.
- **`groundtruth.db` exclusion is documented and sanity-checked.** The fixture excludes it; TP14/TP15 separately assert it exists in scaffold output. SQLite page checksums + B-tree ordering make literal byte-comparison infeasible; the integration-style coverage at TP-INTEG-1 already exercises database initialization properties.
- **Drift catches.** The `extras`/`missing` assertions catch:
  - Scaffold adds a file → `extras` fails until fixture is regenerated.
  - Scaffold drops a file → `missing` fails until fixture is regenerated.
  - Scaffold changes file content → byte-diff fails until fixture is regenerated.
  - Fixture content drifts (e.g., manual edit) → byte-diff fails.
- **Regen path is documented and committed.** `scripts/_capture_scaffold_golden.py` is the single source of truth for fixture content. Future scaffold changes follow this flow: edit scaffold → run `python scripts/_capture_scaffold_golden.py` → review fixture diff → commit.
- **Sandbox name collision is contained.** Both TP14 and TP15 use deterministic sandbox names (`_test_golden_local_only`, `_test_golden_dual_agent`) so concurrent test runs in the same checkout would collide. Mitigation: `applications/.gitignore` covers `_test_*/`; `_run_golden_scaffold` removes any pre-existing sandbox before scaffolding; `try/finally` cleans up. Standard `pytest` execution (sequential) works correctly.
- **Codex `-012.md` "Resolved From Prior NO-GO" remains valid.** The registry-AST coverage and FILE-class extension from REVISED-1 are unchanged in REVISED-2; the 96 baseline tests still pass.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
