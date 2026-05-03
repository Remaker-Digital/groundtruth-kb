REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 3 (REVISED-3)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: `gt project init` — adopter-subject defaults bound to **the literal in-root host path** (`E:\GT-KB`), application-specific validator **split from the legacy bootstrap helper**, and Phase 9 §1 scaffold deliverables.
Supersedes: `-001` NEW, `-002` NO-GO, `-003` REVISED-1, `-004` NO-GO, `-005` REVISED-2, `-006` NO-GO.

## Revision Rationale (REVISED-3)

Codex NO-GO at `-006.md` issued two findings:
- **F1 (P1)**: Marker-validation still permits out-of-bound roots. Required: bind to active in-root boundary (`E:\GT-KB`) literally; tests use either real in-root sandbox or pure non-writing validation.
- **F2 (P2)**: `bootstrap_desktop_project()` calls the legacy `_validate_target(target)` and would break if the shared helper changed signature. Required: split application-specific validation from the legacy bootstrap helper.

Both addressed. **The marker-based contract is fully replaced** by literal-path binding derived from package introspection (`Path(__file__).resolve().parents[4]` = `E:/GT-KB` per probe at impl time). **A new `_validate_application_target()` helper** is introduced; the existing `_validate_target()` is left untouched so `bootstrap_desktop_project()` continues to function. **Test-fixture strategy** is restructured per Codex direction: pure validation tests (no I/O) for the validator surface; out-of-root tmp_path used only in REFUSAL tests; one in-root integration test under `E:\GT-KB\applications\_test_<uuid>/` with cleanup + gitignore entry.

The prior revision's resolved findings (per `-006.md` §"Resolved From Prior NO-GO") carry forward: template paths, scope expansion, ADR citations remain correct.

## Specification Links

1. **Phase 9 plan §1** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 91–142.
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001 (KB row v1)** — `<gt-kb-root>/applications/<name>/` placement mandate.
3. **`.claude/rules/project-root-boundary.md`** lines 8–16, 30–31 — literal `E:\GT-KB` host root and `E:\GT-KB\applications\` app root. **No exceptions** clause is the binding the validator enforces.
4. **`bootstrap_desktop_project()` legacy caller** at `groundtruth-kb/src/groundtruth_kb/bootstrap.py:45-49` and CLI surface at `groundtruth-kb/src/groundtruth_kb/cli.py:119-176`. Existing tests at `groundtruth-kb/tests/test_cli.py:315-325` and `:392-397` continue to use `tmp_path`. **Legacy contract preserved**: `_validate_target(target)` keeps its current signature and semantics.
5. **Probed package introspection** (verified live, this session):
   - `Path("groundtruth-kb/src/groundtruth_kb/project/scaffold.py").resolve().parents[4]` → `E:\GT-KB`.
   - This is the same precedent as `_PRODUCT_ROOT = Path(__file__).resolve().parents[3]` at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1867` (which gives the package root); `parents[4]` walks up one more to the workspace root.
6. **GOV-09**, **GOV-19-A1**, **GOV-20**, prior Slice GOs as in `-005`.
7. **Codex `-006.md`** §"Resolved From Prior NO-GO": prior `-004` F2 (template paths) is materially closed; this revision keeps those corrections.
8. **Prior Deliberations search**: pending probe at impl start.

## Scope

### In-scope

Files modified:
- **`groundtruth-kb/src/groundtruth_kb/cli.py`** — extend `gt project init` (line 826 region):
  - Add `--gt-kb-root <path>` Click option (no default; `None` triggers auto-detect).
  - Call `_resolve_gt_kb_host_root(explicit)`. Resolved root must equal `_GT_KB_HOST_ROOT` (literal binding); if `explicit` is supplied and resolves to a different path, refuse with `click.UsageError`.
  - Compute default target as `host_root / "applications" / project_name` = `E:\GT-KB\applications\<project_name>`.
  - Pass `host_root` into `ScaffoldOptions`.
- **`groundtruth-kb/src/groundtruth_kb/project/scaffold.py`**:
  - `_GT_KB_HOST_ROOT: Path = Path(__file__).resolve().parents[4]` — module-level constant (the literal workspace root).
  - `_resolve_gt_kb_host_root(explicit: Path | None) -> Path` — returns `_GT_KB_HOST_ROOT` if `explicit is None`; if `explicit is not None`, raises `ValueError` unless `explicit.resolve() == _GT_KB_HOST_ROOT`.
  - `_validate_application_target(target: Path, host_root: Path) -> None` — **NEW HELPER, separate from `bootstrap.py`'s `_validate_target`**. Refusal A: `target.parent.resolve()` must equal `(host_root / "applications").resolve()`. Refusal B: if `(target / "groundtruth.toml").exists()`: refuse, recommend `gt project upgrade`.
  - Add `gt_kb_root: Path` to `ScaffoldOptions`.
  - `scaffold_project(options)` calls `_validate_application_target(options.target_dir, options.gt_kb_root)` BEFORE the existing `_validate_target` call (which preserves emptiness check).
  - Emit adopter-facing README quickstart block.
- **`groundtruth-kb/src/groundtruth_kb/bootstrap.py`** — extend `_write_groundtruth_toml` (lines 86–116) with `[service]` block. **`_validate_target(target)` UNCHANGED** — preserves `bootstrap_desktop_project()` legacy behavior per F2.
- **`groundtruth-kb/templates/managed-artifacts.toml`** — register newly-scaffolded files.

Files created (new templates):
- `groundtruth-kb/templates/project/README-quickstart.md`
- `groundtruth-kb/templates/project/release-readiness-banner.md`

Files created (tests + fixtures):
- `groundtruth-kb/tests/test_scaffold_isolation.py` — pure validation tests (TP-VAL-*) + library-surface tests (TP1-TP16) + supplemental (TS*).
- `groundtruth-kb/tests/test_cli_init.py` — primary CLI tests (TP-CLI-*) using `CliRunner`.
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/`, `dual-agent/`.
- **`E:\GT-KB\applications\.gitignore`** *(new)* — adds `_test_*/` to keep in-root sandbox test directories out of git.

### Test-fixture strategy (per Codex `-006.md` F1 direction)

- **Pure validation tests** (TP-VAL-*) — call `_validate_application_target(target, host_root)` and `_resolve_gt_kb_host_root(explicit)` with constructed `Path` objects. **No filesystem writes**. Cover refusal A, refusal B, host-root resolution accept/reject, override-mismatch refusal.
- **CLI refusal tests** (TP-CLI-REFUSE-*) — use `tmp_path` fixtures that are deliberately out-of-root. Assert `gt project init` exits non-zero with appropriate error.
- **CLI auto-detect test** (TP-CLI-DETECT-1) — uses pytest's `monkeypatch` to override `_GT_KB_HOST_ROOT` to a sandbox path, AND uses an in-root sandbox at `E:\GT-KB\applications\_test_<uuid>/` for the actual scaffold output, with explicit `pytest` fixture cleanup. The sandbox path is gitignored.
- **Library integration test** (TP-INTEG-1) — single end-to-end test using the same in-root sandbox pattern.
- **Library unit tests** (TP1-TP16) — for properties of scaffold output that can be verified by inspecting return values or single-file content, use pure approach (call `scaffold_project` with `dry_run`-like mode, OR use the in-root sandbox once and inspect its contents).

### Out-of-scope

- Future arbitrary workspace roots (e.g., post-install layouts where `parents[4]` doesn't yield workspace root). Slice 3 binds to current dev/install layout. Generalization is a follow-on if/when GT-KB ships installable binaries.
- `gt project upgrade` (Slice 4); examples (Slice 7); release ops (Slice 8) — unchanged.
- `bootstrap_desktop_project()` migration to new validator. Legacy caller stays on legacy helper.

## Implementation Plan

1. Probe `ScaffoldOptions(...)` callers + existing `_validate_target` callers. Confirm `bootstrap_desktop_project()` is the only legacy-helper caller.
2. Add `_GT_KB_HOST_ROOT` constant + `_resolve_gt_kb_host_root` + `_validate_application_target` to `scaffold.py`.
3. Wire `scaffold_project()` to call new helper.
4. Extend CLI per Scope.
5. Extend `_write_groundtruth_toml` with `[service]` block.
6. Place README + banner templates at corrected paths.
7. Register new files in `managed-artifacts.toml`.
8. Add `applications/.gitignore` for `_test_*/`.
9. Tests: pure validation first, then CLI refusal, then in-root integration.
10. Capture golden fixtures.
11. IPR + CVR documents.

## Spec-to-test mapping

### Pure validation (no I/O — primary GOV-19-A1 surface)

| # | Test | Asserts |
|---|---|---|
| TP-VAL-1 | `test_resolve_gt_kb_host_root_returns_constant_when_explicit_none` | `_resolve_gt_kb_host_root(None)` returns `_GT_KB_HOST_ROOT` |
| TP-VAL-2 | `test_resolve_gt_kb_host_root_accepts_matching_explicit` | `_resolve_gt_kb_host_root(_GT_KB_HOST_ROOT)` returns `_GT_KB_HOST_ROOT` |
| TP-VAL-3 | `test_resolve_gt_kb_host_root_refuses_mismatched_explicit` | `_resolve_gt_kb_host_root(Path('/some/other'))` raises ValueError |
| TP-VAL-4 | `test_validate_application_target_accepts_under_applications` | `_validate_application_target(_GT_KB_HOST_ROOT/'applications/x', _GT_KB_HOST_ROOT)` returns None |
| TP-VAL-5 | `test_validate_application_target_refuses_outside_applications` | `_validate_application_target(_GT_KB_HOST_ROOT/'other/x', _GT_KB_HOST_ROOT)` raises ValueError citing ADR |
| TP-VAL-6 | `test_validate_application_target_refuses_existing_adopter` | fixture: pre-create `target/groundtruth.toml`; assert refusal recommending `gt project upgrade` |
| TP-VAL-7 | `test_legacy_validate_target_unchanged_signature` | static check that `bootstrap._validate_target(target)` accepts single argument (preserves legacy) |

### CLI surface (refusal tests use out-of-root tmp_path; success uses sandbox)

| # | Test | Asserts |
|---|---|---|
| TP-CLI-REFUSE-1 | `test_init_refuses_explicit_root_mismatch` | `gt project init my-app --gt-kb-root <tmp>` exits non-zero (tmp != _GT_KB_HOST_ROOT) |
| TP-CLI-REFUSE-2 | `test_init_refuses_dir_outside_applications` | `gt project init my-app --dir <tmp>/random` exits non-zero |
| TP-CLI-REFUSE-3 | `test_init_refuses_existing_adopter` | running init twice on same in-root sandbox path; second exits non-zero with upgrade recommendation |
| TP-CLI-DETECT-1 | `test_init_uses_GT_KB_HOST_ROOT_when_explicit_none` | call without `--gt-kb-root`; verify the resolved target prefix equals `_GT_KB_HOST_ROOT/applications/` (path-prefix only, no actual scaffold write needed) |

### Library + integration

| # | Test | Asserts |
|---|---|---|
| TP-INTEG-1 | `test_scaffold_project_creates_in_root_sandbox` | uses `applications/_test_<uuid>/`; verifies all Phase 9 §1 enumeration items present; cleanup at teardown |
| TP1-TP13 | scaffold-output property checks (Phase 9 §1 enumeration) | each runs against the same `_test_<uuid>/` fixture; verifies a single property of scaffold output |
| TP14-TP15 | golden-fixture diffs | byte-level equality against `groundtruth-kb/tests/fixtures/scaffold_golden/{local-only,dual-agent}/` |
| TP16 | managed-registry coverage | every new scaffold file registered in `groundtruth-kb/templates/managed-artifacts.toml` |

### Supplemental helper-level

| # | Test | Asserts |
|---|---|---|
| TS1 | `test_write_groundtruth_toml_emits_service_block` | `[service]` block matches `_SCOPED_SERVICE_URL_RE` |
| TS2 | `test_managed_registry_includes_new_files` | direct registry check |

## Verification Commands

```
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli_init.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_cli.py -v -k "bootstrap_desktop"  # confirms legacy caller still works
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_managed_registry.py -v
$ uv run --project groundtruth-kb ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli_init.py
```

## Risk and Rollback

- **Risk: `parents[4]` ancestry breaks on installed package layouts.** Mitigation: dev/CI uses the dev checkout layout where `parents[4] == E:\GT-KB`; runtime test asserts the constant is `_PRODUCT_ROOT.parent` so the relationship is checked. Generalization is a follow-on slice if installed layouts are added.
- **Risk: in-root sandbox tests leave artifacts after failures.** Mitigation: pytest fixture uses `try/finally` cleanup + `applications/.gitignore` ensures any leftover `_test_*` directories don't pollute git status.
- **Risk: existing scaffold tests break.** Mitigation: probe call sites first; adjust same commit. `bootstrap_desktop_project()` legacy contract preserved per F2.
- **Rollback:** revert commit; new helpers go away; legacy unchanged.

## Acceptance Criteria

- TP-VAL-1 through TP-VAL-7 pass.
- TP-CLI-REFUSE-1 through TP-CLI-REFUSE-3 pass.
- TP-CLI-DETECT-1 passes.
- TP-INTEG-1 + TP1–TP16 pass.
- TS1, TS2 pass.
- `bootstrap_desktop_project()` legacy tests at `groundtruth-kb/tests/test_cli.py:315-325` and `:392-397` still pass unchanged.
- Ruff clean.
- IPR/CVR document rows inserted with explicit owner-approval evidence.
- Golden fixtures committed at `groundtruth-kb/tests/fixtures/scaffold_golden/` (in-root).
- `applications/.gitignore` covers `_test_*/`.

## Open Items (probed at impl start)

- Exact `ScaffoldOptions(...)` caller list.
- Confirmation that `bootstrap_desktop_project()` is the sole `_validate_target` caller.
- `python -m groundtruth_kb.cli deliberations search` for the topic.

## Deliberation Capture

Bridge thread + IPR/CVR are the substantive record. No pre-impl owner decisions required.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
