REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 3 (REVISED-2)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: `gt project init` — adopter-subject defaults, **marker-validated** host-root binding, root-boundary refusal, existing-adopter idempotency, and Phase 9 §1 scaffold deliverables.
Supersedes: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-{001,002,003,004}.md` (NEW, NO-GO, REVISED-1, NO-GO).

## Revision Rationale (REVISED-2)

Codex NO-GO at `-004.md` issued two blocking findings (F1 P1, F2 P1). Both are addressed. The prior revision's three findings (F1, F2, F3) are confirmed materially resolved by Codex `-004.md` §"Resolved From Prior NO-GO".

**F1 (P1) — `gt_kb_root` must bind to the real GT-KB host root.** Codex objected that `--gt-kb-root <path>` defaulting to `Path.cwd()` and accepting any directory makes "valid app root" caller-defined, not workspace-defined. A run from `E:\GT-KB\groundtruth-kb` or any tmp dir would create syntactically-valid but governance-invalid roots, and the proposed tests would lock that wrong behavior in.

This revision replaces the arbitrary-path contract with a **marker-validated host-root contract**:
- New `_resolve_gt_kb_host_root(start, explicit)` function that returns a `Path` only if it resolves to a directory carrying both required workspace markers (`bridge/INDEX.md` AND `.claude/rules/project-root-boundary.md`).
- If `--gt-kb-root` is supplied: the supplied path must validate as a host root (markers present); otherwise refuse with explicit error.
- If `--gt-kb-root` is omitted: walk upward from `Path.cwd()` looking for the first ancestor that validates as a host root; refuse with explicit error if none found.
- Test plan rewritten so out-of-root paths are **refusal tests**, not success tests. Success tests construct tmp fixtures that **carry the markers** (so they are structurally valid GT-KB workspaces — exercising the contract, not bypassing it). One end-to-end integration test uses the real in-root sandbox path `E:/GT-KB/applications/_test_<uuid>/` with explicit cleanup.

**F2 (P1) — Template path corrected to live editable-install tree.** Codex confirmed that the live template resolver (`groundtruth-kb/src/groundtruth_kb/__init__.py:19-30`) checks `src/groundtruth_kb/templates` first and only falls back to `groundtruth-kb/templates/` if the package path is absent. Currently the package path is absent and the live tree is `groundtruth-kb/templates/project/...`. Adding partial templates under `src/...` would make `get_templates_dir()` prefer the partial directory and break scaffold output broadly.

This revision **corrects every new-template path** to land under `groundtruth-kb/templates/project/...`, consistent with `managed-artifacts.toml` location and the Hatch `force-include` rule at `groundtruth-kb/pyproject.toml:65-69`.

## Context (unchanged)

GTKB-ISOLATION-017 is the adopter-packaging program. Slices 1, 2, 2.5 VERIFIED. This proposal opens Slice 3 per scoping GO at `bridge/gtkb-isolation-017-scoping-004.md` lines 84–115. No owner-decision blockers.

## Specification Links

1. **Phase 9 plan §1** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 91–142 (canonical scaffold-deliverable enumeration).
2. **ADR-ISOLATION-APPLICATION-PLACEMENT-001 (KB row)** — `db.get_spec('ADR-ISOLATION-APPLICATION-PLACEMENT-001')` returns v1, `status=specified`, `type=architecture_decision`. Bridge-thread terminal at `bridge/gtkb-adr-isolation-application-placement-004.md`. Mandate: adopter applications live at `<gt-kb-root>/applications/<name>/`.
3. **`.claude/rules/project-root-boundary.md`** lines 8, 11, 30 — the host-root literal (`E:\GT-KB`) and its application subdirectory (`E:\GT-KB\applications\`) define the in-root boundary. The marker-validated host-root contract preserves this rule by checking structural properties (markers exist) rather than path-string equality, so the same code that validates the dev checkout also validates a future-installed workspace at any path.
4. **ADR-CODEX-HOOK-PARITY-FALLBACK-001 (KB row only)** — referenced for `.codex/hooks.json` forward-compat intent.
5. **Live template resolver** — `groundtruth-kb/src/groundtruth_kb/__init__.py:19-30` (`get_templates_dir()` precedence: package `src/groundtruth_kb/templates` > repo-root `groundtruth-kb/templates`). Corrected per F2.
6. **Live registry** — `groundtruth-kb/templates/managed-artifacts.toml` (corrected per `-004` F3 resolution; reaffirmed here).
7. **Hatch force-include** — `groundtruth-kb/pyproject.toml` lines 65–69 maps repo-root `templates` → `groundtruth_kb/templates` in built wheel.
8. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-{003,004}.md`.
9. **GOV-09**, **GOV-19-A1**, **GOV-20** as in `-003`.
10. **Prior Slice GOs** (carry-forward only): `gtkb-isolation-017-slice1-doctor-checks-012.md` VERIFIED — Slice 1 ships `_check_isolation_adopter_root_not_under_product_root(target, product_root)` at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:43`. The CLI plumbs the resolved host root so the same check passes at session start on the freshly-scaffolded adopter. `gtkb-isolation-017-slice2-registry-isolation-008.md` VERIFIED — registry now carries `owner` / `upgrade_policy` fields; Slice 3 registers all newly-scaffolded files.
11. **GT-KB host-root detection precedent** — `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1867` defines `_PRODUCT_ROOT = Path(__file__).resolve().parents[3]` for the doctor's runtime check (the *package* root, not the *workspace* root). Slice 3's `_resolve_gt_kb_host_root` operates one layer up at the workspace level via marker detection, complementing rather than replacing the package-level helper.
12. **Sandbox Output Exception** — `.claude/rules/project-root-boundary.md` §"Sandbox Output Exception" allows runtime output outside `E:\GT-KB` only for rehearsal-class operations under owner-approved manifest. Test fixtures using `tmp_path` are not rehearsal output — they are ephemeral pytest artifacts. The marker-validated contract makes that distinction explicit: a tmp_path that lacks workspace markers is rejected by the validator, just as production code would be; a tmp_path that the test deliberately structures with markers passes the same validator. Tests prove the contract; they don't bypass it.
13. **Prior Deliberations search**: `python -m groundtruth_kb.cli deliberations search ...` (run by Codex `-002.md` and `-004.md`) returned no rows. Active prior context is the bridge thread.

## Scope

### In-scope

Files modified:
- **`groundtruth-kb/src/groundtruth_kb/cli.py`** — extend `gt project init` (line 826 region):
  - Add `--gt-kb-root <path>` Click option (no default; `None` means "auto-detect").
  - Call new `_resolve_gt_kb_host_root(start=Path.cwd(), explicit=gt_kb_root)`. Refusal raises `click.UsageError` with marker-list in the error.
  - Compute default target as `host_root / "applications" / project_name`.
  - Pass `host_root` into `ScaffoldOptions`.
- **`groundtruth-kb/src/groundtruth_kb/project/scaffold.py`**:
  - Add `_resolve_gt_kb_host_root(start: Path, explicit: Path | None) -> Path` helper. Workspace markers (both required): `bridge/INDEX.md`, `.claude/rules/project-root-boundary.md`. Walks ancestors of `start` if `explicit is None`. Validates `explicit` if supplied. Refuses with `ValueError` listing missing markers.
  - Add `gt_kb_root: Path` to `ScaffoldOptions` (required field).
  - Emit adopter-facing README quickstart block.
- **`groundtruth-kb/src/groundtruth_kb/bootstrap.py`**:
  - Extend `_validate_target` (lines 75–79) with two refusal paths plus a new `gt_kb_root` parameter:
    - Refusal A: `target.parent.resolve()` must equal `(gt_kb_root / "applications").resolve()`. Otherwise `ValueError` cites ADR-ISOLATION-APPLICATION-PLACEMENT-001.
    - Refusal B: if `(target / "groundtruth.toml").exists()`: `ValueError` recommending `gt project upgrade`.
  - Extend `_write_groundtruth_toml` (lines 86–116) with a `[service]` block (placeholder matching `_SCOPED_SERVICE_URL_RE` at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:125`).
- **`groundtruth-kb/templates/managed-artifacts.toml`** *(corrected path)* — register newly-scaffolded files (README quickstart target, `memory/release-readiness.md`, `.codex/hooks.json`, `.groundtruth/formal-artifact-approvals/.gitkeep`) so Slice 2 AST gate stays green.

Files created (new templates — corrected paths per F2):
- **`groundtruth-kb/templates/project/README-quickstart.md`** *(new)* — adopter-facing README quickstart block per Phase 9 §1 line 105 + Deliverables lines 425–426.
- **`groundtruth-kb/templates/project/release-readiness-banner.md`** *(new)* — application-subject header per Phase 9 §1 lines 123–125.

Files created (tests + fixtures):
- **`groundtruth-kb/tests/test_scaffold_isolation.py`** — primary library-surface tests (TP*) + helper supplemental (TS*).
- **`groundtruth-kb/tests/test_cli_init.py`** — primary CLI-surface tests (TP-CLI-*) using Click's `CliRunner`.
- **`groundtruth-kb/tests/fixtures/scaffold_golden/local-only/`** and **`dual-agent/`** — golden fixture trees (committed under `groundtruth-kb/tests/`, fully in-root).

Documents (per GOV-20):
- `IPR-SLICE3-INIT-DEFAULTS-001`, `CVR-SLICE3-INIT-DEFAULTS-001` — inserted via `KnowledgeDB.insert_document(category='implementation_proposal' / 'constraint_verification')` with explicit owner-approval evidence in the change-reason.

### Out-of-scope (deferred to other slices, unchanged from `-003`)

- `gt project upgrade` extensions (Slice 4) — owner-decision-1/3/7 branching.
- Clean-adopter test suite under `groundtruth-kb/tests/adopter/` (Slice 5).
- Documentation chapter (Slice 6).
- Examples (Slice 7) and release ops (Slice 8).
- Phase 6 overlay refresh / stale / disposability tests (Slice 5).
- Marker-detection extensibility (e.g., user-configurable marker lists) — out of scope for Slice 3; current contract uses a fixed marker tuple.

## Implementation Plan

1. Probe `ScaffoldOptions(...)` construction sites repo-wide; report count in post-impl.
2. Probe existing CLI/scaffold tests; identify call-site adjustments.
3. **`_resolve_gt_kb_host_root`** added to `scaffold.py`. Required markers tuple: `(Path("bridge/INDEX.md"), Path(".claude/rules/project-root-boundary.md"))`. Algorithm: if `explicit is not None`, validate `explicit / marker` exists for each required marker; else walk `start.resolve().parents` (including start itself) until both markers present; raise `ValueError` with diagnostic listing the missing markers if neither path validates.
4. **CLI extension** (`cli.py`): add `--gt-kb-root` option; call resolver; thread into `ScaffoldOptions`.
5. **`ScaffoldOptions.gt_kb_root`** added as required field; passed through to `_validate_target` and `_write_groundtruth_toml`.
6. **`_validate_target`** extended with both refusal paths (A + B per Scope).
7. **`_write_groundtruth_toml`** extended with `[service]` block:
   ```toml
   [service]
   # Phase 4 service-endpoint template. Override per environment.
   # endpoint = "https://gtkb.example.com/v1"
   endpoint = "configure-me://placeholder/v1"
   ```
8. **Templates** placed at `groundtruth-kb/templates/project/README-quickstart.md` and `release-readiness-banner.md`. Other scaffold artifacts (`.codex/hooks.json`, `.groundtruth/formal-artifact-approvals/.gitkeep`) emitted via `_copy_base_templates` extensions sourcing from the corrected template tree.
9. **Register all new files** in `groundtruth-kb/templates/managed-artifacts.toml`.
10. **Capture golden fixture** trees post-implementation. Place under `groundtruth-kb/tests/fixtures/scaffold_golden/` (in-root).
11. **Author IPR + CVR** documents.

## Spec-to-test mapping (REVISED — marker-validated host-root contract)

### Primary tests — outside-in surfaces (GOV-19-A1 spec coverage)

#### CLI surface (`gt project init` via Click `CliRunner`)

Each test constructs a `tmp_path`-based fixture. Success tests **populate the tmp fixture with workspace markers** (`bridge/INDEX.md` empty file + `.claude/rules/project-root-boundary.md` empty file) so the fixture is structurally a valid GT-KB workspace. Refusal tests deliberately omit the markers, proving the validator rejects unmarked roots.

| # | Test | Phase 9 §1 / behavior | Asserts |
|---|---|---|---|
| TP-CLI-1 | `test_init_default_target_under_applications_when_explicit_root_has_markers` | line 106 | tmp fixture has both markers; `gt project init my-app --gt-kb-root <fixture>` succeeds; result lands at `<fixture>/applications/my-app/` |
| TP-CLI-2 | `test_init_refuses_when_explicit_root_lacks_markers` | F1 contract | tmp fixture missing markers; `gt project init my-app --gt-kb-root <fixture>` exits non-zero with marker-list in stderr |
| TP-CLI-3 | `test_init_refuses_when_no_explicit_root_and_cwd_outside_workspace` | F1 contract | `gt project init my-app` invoked from a tmp dir with no marker ancestors → exits non-zero, REFUSE |
| TP-CLI-4 | `test_init_auto_detects_host_root_from_cwd_within_marked_workspace` | line 106 | tmp fixture has markers; `gt project init my-app` from `<fixture>/sub/dir/` (no `--gt-kb-root` flag) succeeds; lands at `<fixture>/applications/my-app/` |
| TP-CLI-5 | `test_init_refuses_dir_outside_applications_subdir` | line 108 | `gt project init my-app --gt-kb-root <marked-fixture> --dir <marked-fixture>/elsewhere/my-app` exits non-zero with ADR citation in stderr |
| TP-CLI-6 | `test_init_refuses_existing_adopter_recommends_upgrade` | lines 140–142 | running init twice on same target; second invocation exits non-zero; stderr recommends `gt project upgrade` |

#### Library surface (`scaffold_project`) — Phase 9 §1 enumeration

| # | Test | Phase 9 §1 reference | Asserts |
|---|---|---|---|
| TP1 | `test_scaffold_emits_groundtruth_toml_with_app_local_fields` | lines 115–116 | `groundtruth.toml` written; `[service]` block matches `_SCOPED_SERVICE_URL_RE` |
| TP2 | `test_scaffolded_service_endpoint_passes_doctor_check` | line 116 | `_check_isolation_service_endpoint_not_raw_db` returns `status=pass` against scaffolded fixture |
| TP3 | `test_scaffold_initializes_app_scope_groundtruth_db` | line 117 | `groundtruth.db` exists; tables in `sqlite_master` are app-scope only (no product-scope rows pre-populated) |
| TP4 | `test_scaffold_emits_empty_bridge_index_with_README_header` | lines 118–119 | `bridge/INDEX.md` empty (header comments only); scaffolded `README.md` contains the bridge-essential rule header |
| TP5 | `test_scaffold_emits_work_list_placeholder` | lines 120–122 | `memory/work_list.md` exists; placeholder entry + adopter-owned-backlog convention comment block |
| TP6 | `test_scaffold_emits_release_readiness_with_app_subject_banner` | lines 123–125 | `memory/release-readiness.md` contains application-subject header + "GT-KB product readiness is not tracked here" banner |
| TP7 | `test_scaffold_emits_claude_wrappers_no_embedded_policy` | lines 126–128 | `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json` exist; wrappers free of embedded policy (regex blacklist match returns zero hits) |
| TP8 | `test_scaffold_emits_codex_hooks_intent` | lines 129–130 | `.codex/hooks.json` exists with forward-compat shape per ADR-CODEX-HOOK-PARITY-FALLBACK-001 |
| TP9 | `test_scaffold_emits_formal_approvals_gitkeep` | lines 131–132 | `.groundtruth/formal-artifact-approvals/.gitkeep` exists |
| TP10 | `test_scaffold_does_not_pre_populate_dashboard_dir` | lines 133–134 | `docs/gtkb-dashboard/` is absent in scaffolded output |
| TP11 | `test_scaffold_emits_segregated_gitignore` | lines 135–136 | `.gitignore` has two clearly-delimited blocks (product-maintained + adopter-owned) |
| TP12 | `test_scaffold_excludes_forbidden_product_artifacts` | lines 137–139 | scaffolded tree contains zero of: GT-KB product source, product test paths, product-scope MemBase rows, product bridge threads, raw DB credential patterns, deployment-secret patterns |
| TP13 | `test_scaffold_emits_readme_quickstart_block` | line 105 + Deliverables lines 425–426 | scaffolded `README.md` contains documented quickstart markers; references `[service].endpoint` per Phase 9 Exit Criterion 4 line 343–345 |
| TP14 | `test_scaffold_local_only_matches_golden_fixture` | scoping `-003` line 111 | byte-level diff against `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/` |
| TP15 | `test_scaffold_dual_agent_matches_golden_fixture` | scoping `-003` line 111 | byte-level diff against `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/` |
| TP16 | `test_managed_registry_covers_new_scaffold_files` | Slice 2 AST-gate carry-forward | every new file Slice 3 emits is registered in `groundtruth-kb/templates/managed-artifacts.toml` (corrected path) |

#### Host-root resolver — pure validation tests (no I/O writes outside fixture setup)

| # | Test | Behavior |
|---|---|---|
| TP-RES-1 | `test_resolve_gt_kb_host_root_accepts_marked_explicit_path` | tmp fixture with both markers; `_resolve_gt_kb_host_root(start=anywhere, explicit=fixture)` returns `fixture` |
| TP-RES-2 | `test_resolve_gt_kb_host_root_refuses_unmarked_explicit_path` | tmp fixture missing one marker; `_resolve_gt_kb_host_root(start=anywhere, explicit=fixture)` raises ValueError listing the missing marker |
| TP-RES-3 | `test_resolve_gt_kb_host_root_walks_ancestors_when_explicit_none` | tmp fixture with markers at root + nested subdir; `_resolve_gt_kb_host_root(start=<fixture>/sub/dir, explicit=None)` returns `fixture` |
| TP-RES-4 | `test_resolve_gt_kb_host_root_refuses_when_no_marked_ancestor` | tmp fixture with no markers anywhere in the ancestry; `_resolve_gt_kb_host_root(start=tmp, explicit=None)` raises ValueError |

### Supplemental helper-level tests (NOT GOV-19-A1 spec coverage)

| # | Test | Behavior |
|---|---|---|
| TS1 | `test_validate_target_refuses_outside_applications_root_at_helper_layer` | direct `_validate_target(target, gt_kb_root)` call with outside-root target raises ValueError |
| TS2 | `test_validate_target_refuses_existing_adopter_at_helper_layer` | direct call with existing-adopter target raises ValueError |
| TS3 | `test_write_groundtruth_toml_emits_service_block` | direct `_write_groundtruth_toml(...)` call writes `[service]` block matching `_SCOPED_SERVICE_URL_RE` |

### Note on test-fixture marker construction

Per `.claude/rules/project-root-boundary.md` and Codex `-004.md` F1: the marker-validated contract means a tmp_path that the test populates with workspace markers IS structurally a valid GT-KB workspace as far as the validator is concerned. Tests do not assert that a tmp_path equals `E:\GT-KB`; they assert that the validator accepts/rejects based on **structure**. This preserves the rule (production code can only succeed against real GT-KB workspaces because only those carry the markers in real deployments) while making the validator unit-testable.

## Verification Commands (Windows-safe)

```
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli_init.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_cli.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_doctor_isolation.py -v -k "service_endpoint"
$ uv run --project groundtruth-kb ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/scaffold.py groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_cli_init.py
```

## Risk and Rollback

- **Risk: existing call sites of `ScaffoldOptions(...)` break** when `gt_kb_root` becomes required. Mitigation: probe count before implementation; adjust each in same commit. `test_scaffold_project.py:18–37`, `test_cli.py` are the primary call sites.
- **Risk: marker-set drift.** If the marker tuple `(bridge/INDEX.md, .claude/rules/project-root-boundary.md)` ever changes meaning, the resolver's contract breaks. Mitigation: marker tuple is a module-level constant in `scaffold.py` with a clear comment naming the rule it derives from; any future marker change goes through its own bridge.
- **Risk: existing-adopter detection over-refuses.** Mitigation: refusal predicate is specifically `(target / "groundtruth.toml").exists()`, not directory non-emptiness.
- **Risk: `--gt-kb-root` UX confusion.** Mitigation: README quickstart block documents the flag; auto-detect from `cwd()` covers the common case.
- **Rollback:** revert the implementation commit; CLI returns to pre-Slice-3 form. No DB schema changes; Slice 1 + Slice 2 unaffected.

## Acceptance Criteria

- TP-CLI-1 through TP-CLI-6 (CLI surface) pass.
- TP1 through TP16 (library surface) pass.
- TP-RES-1 through TP-RES-4 (resolver surface) pass.
- TS1 through TS3 (supplemental helper) pass.
- Existing scaffold/CLI tests pass after call-site adjustments.
- `_check_isolation_service_endpoint_not_raw_db` passes on a freshly-scaffolded fixture.
- Slice 2 AST gate passes against the new scaffolded files.
- Ruff clean on all modified and new files.
- IPR-SLICE3-INIT-DEFAULTS-001 and CVR-SLICE3-INIT-DEFAULTS-001 inserted as KB document rows; explicit owner-approval evidence recorded in change-reason.
- Golden fixture trees committed at `groundtruth-kb/tests/fixtures/scaffold_golden/` (in-root) and byte-level diff tests pass.

## Open Items (probed during implementation; reported in post-impl)

- Exact count of `ScaffoldOptions(...)` construction sites.
- Result of `python -m groundtruth_kb.cli deliberations search --query "gt project init scaffold isolation" --limit 5` at implementation start.
- Whether any test relies on `_validate_target` being argument-free.

## Deliberation Capture

The bridge thread + IPR/CVR pair capture the substantive design. No pre-implementation owner decisions are required.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
