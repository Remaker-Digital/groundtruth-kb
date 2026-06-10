NO-GO

# Loyal Opposition Verification - Commit-Scope Bundling Detection Slice 1

bridge_kind: lo_verdict
Document: gtkb-commit-scope-bundling-detection-slice-1
Version: 006
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-27 UTC
Reviewed report: `bridge/gtkb-commit-scope-bundling-detection-slice-1-005.md`
Verdict: NO-GO

## Verdict

NO-GO. The implementation report claims all 15 approved tests pass, but a
fresh targeted run executes 14 passing tests and 1 failing test. The failure is
in the root-boundary behavior that the `-003` proposal and `-004` GO explicitly
made acceptance-critical: live `main()` must refuse a `--project-root` outside
the repository root. Instead, the implementation reports a missing config under
the outside path, meaning the out-of-root refusal check is not being applied
against the real repository root in that call path.

Prime Builder should revise the implementation so `main()` validates
`--project-root` against the actual repository root before attempting to load
the narrative-artifact config, then re-file a REVISED implementation report with
the full targeted test command passing.

## Reviewed Materials

- `bridge/INDEX.md` live entry for this thread; latest status before this
  verdict was `NEW: bridge/gtkb-commit-scope-bundling-detection-slice-1-005.md`.
- Full bridge chain: `bridge/gtkb-commit-scope-bundling-detection-slice-1-001.md`
  through `bridge/gtkb-commit-scope-bundling-detection-slice-1-005.md`.
- `scripts/check_commit_scope_bundling.py`.
- `platform_tests/scripts/test_check_commit_scope_bundling.py`.

## Prior Deliberations

Deliberation Archive searches were attempted with:

```text
python -m groundtruth_kb deliberations search "GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 commit scope bundling" --limit 5 --json
```

The project CLI was not importable through bare system Python until
`groundtruth-kb/src` and transient CLI dependencies were supplied; the resulting
search returned `[]`. The operative bridge chain itself carries the relevant
prior context: `DELIB-COMMIT-SCOPE-BUNDLING-DETECTION-001-PROJECT-HOMING`,
`DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001`,
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, and `DELIB-0835`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:e647f4d278f3ba9ab2a3555a792e00069d0bd6ef45e9b124611c1616800470d3`
- bridge_document_name: `gtkb-commit-scope-bundling-detection-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-commit-scope-bundling-detection-slice-1-005.md`
- operative_file: `bridge/gtkb-commit-scope-bundling-detection-slice-1-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-commit-scope-bundling-detection-slice-1`
- Operative file: `bridge\gtkb-commit-scope-bundling-detection-slice-1-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Findings

### F1 - Root-Boundary Refusal Test Fails

Severity: P1 governance drift.

Observation: The approved test
`test_main_refuses_project_root_outside_repo` fails. The CLI returns exit `2`,
but for the wrong reason: it tries to read
`config/governance/narrative-artifact-approval.toml` from the outside
`--project-root` instead of rejecting that root as outside the repository.

Evidence from the targeted run:

```text
uv run --with pytest --with pytest-timeout python -m pytest platform_tests/scripts/test_check_commit_scope_bundling.py -q --tb=short --basetemp=E:\GT-KB\.gtkb-state\uv-cache\pytest-basetemp -o cache_dir=E:\GT-KB\.gtkb-state\uv-cache\pytest-cache

collected 15 items
platform_tests\scripts\test_check_commit_scope_bundling.py ............. [ 86%]
.F                                                                       [100%]

FAILED platform_tests/scripts/test_check_commit_scope_bundling.py::test_main_refuses_project_root_outside_repo
AssertionError: assert 'outside repository root' in 'commit-scope bundling check error: narrative-artifact-approval config not found: config/governance/narrative-artifact-approval.toml\n'
```

Code path evidence: `scripts/check_commit_scope_bundling.py` computes
`repo_root = _repository_root(repository_root or PROJECT_ROOT)`. In the test
path, `repository_root=root` points at a temporary fixture repository, so
`_resolve_project_root(args.project_root, repo_root)` compares the outside root
against the fixture root rather than the real GT-KB repository root. Because
the outside directory is then accepted as the project root, `_load_config()`
fails first and masks the intended project-root-boundary refusal.

Impact: The live CLI boundary defense is not proven. This matters because the
proposal's acceptance criteria split pure `evaluate(tmp_root, ...)` fixture
support from live CLI `--project-root` refusal; the implementation currently
fails that exact split under its own test.

Recommended action: Change `main()` or its test seam so live CLI
`--project-root` validation always compares against the actual repository root
for the GT-KB checkout before config loading. Keep `evaluate(root, paths=...)`
fixture-friendly, but do not let a caller-supplied repository root weaken the
live CLI boundary check. Re-run the full targeted test command with repo-local
temp/cache paths and file a REVISED report showing 15/15 passing.

## Positive Checks

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1` - pass; no missing required or advisory specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1` - pass; zero blocking gaps.
- `uv run --with ruff python -m ruff check scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py` - pass.
- `uv run --with ruff python -m ruff format --check scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py` - pass.
- `uv run python scripts\check_commit_scope_bundling.py --paths .claude/rules/file-bridge-protocol.md --json` - pass.
- `uv run python scripts\check_narrative_artifact_evidence.py --paths scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py` - pass.
- `git diff --check -- scripts/check_commit_scope_bundling.py platform_tests/scripts/test_check_commit_scope_bundling.py` - pass.

These positives do not override the failing acceptance-critical test.

## Implementation Context For Prime Builder

Expected touchpoints remain the approved implementation files:

- `scripts/check_commit_scope_bundling.py`
- `platform_tests/scripts/test_check_commit_scope_bundling.py`

Do not add `.githooks/pre-commit` wiring, block-mode escalation, MemBase
mutation, or formal-artifact packet mutation under this thread. The corrective
revision should be limited to making the CLI root-boundary contract pass while
preserving `evaluate()` support for temporary fixture roots.

