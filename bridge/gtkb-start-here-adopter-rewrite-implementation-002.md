# GO Review: GT-KB Start Here Adopter Rewrite Implementation

**Verdict:** GO with conditions
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD inspected:** `e12aab3`

## Claim

The implementation plan is approved to proceed on a feature branch. It materially discharges the seven conditions from `bridge/gtkb-start-here-adopter-rewrite-002.md` and makes reasonable default calls for the two owner-pending choices: Mermaid rendered by MkDocs and a synthetic day-in-the-life protagonist.

This GO is conditional on the implementation applying the corrections below before filing the post-implementation bridge. The corrections are small, but they affect bridge auditability and machine-verifiable gates.

## Evidence

- The parent scope review required live evidence with command, commit, date, and source for each metric at `bridge/gtkb-start-here-adopter-rewrite-002.md:28`.
- The parent scope review required MkDocs discoverability at `bridge/gtkb-start-here-adopter-rewrite-002.md:30`, a diagram rendering contract at `bridge/gtkb-start-here-adopter-rewrite-002.md:32`, external Claude Code install stability at `bridge/gtkb-start-here-adopter-rewrite-002.md:34`, owner validation split at `bridge/gtkb-start-here-adopter-rewrite-002.md:36`, and repo-native docs gates at `bridge/gtkb-start-here-adopter-rewrite-002.md:38`.
- The implementation proposal distinguishes MemBase, MEMORY.md, the Deliberation Archive, and ChromaDB at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:20`.
- The target repo supports Mermaid fences through `mkdocs.yml:41` and `mkdocs.yml:43`.
- The target repo defines MemBase as Core Knowledge Database at `docs/architecture/product-split.md:13`, describes it as append-only SQLite at `docs/architecture/product-split.md:15`, and names it the canonical knowledge and specifications tier at `docs/architecture/product-split.md:27`.
- Current MkDocs nav includes Start Here but not Day in the Life, Evidence, Known Limitations, or Executive Overview at `mkdocs.yml:54`.
- `docs/evidence.md`, `docs/known-limitations.md`, and `scripts/collect_evidence_metrics.py` do not currently exist in the target repo.
- The target repo exposes assertions through `run_spec_assertions()` and `run_all_assertions()` at `src/groundtruth_kb/assertions.py:711` and `src/groundtruth_kb/assertions.py:762`, and the CLI invokes `run_all_assertions()` from `gt assert` at `src/groundtruth_kb/cli.py:184`.
- The assertion language docs show `gt assert` and `run_all_assertions(db, project_root)` as the supported runner at `docs/reference/assertion-language.md:188`.
- Current strict MkDocs build exits 0 while still reporting an existing missing-anchor info message. Command run: `python -m mkdocs build --strict --site-dir C:\Users\micha\AppData\Local\Temp\gtkb-mkdocs-bridge-codex`. Result: exit 0; output reported `method/13-deliberation-archive.md` links to `reference/cli.md#deliberation-commands`, but that anchor is absent.
- Current docs CLI coverage passes. Command run: `python scripts/check_docs_cli_coverage.py`. Result: exit 0, "All documentation checks passed."
- Current pytest collection is 1249 tests. Command run: `python -m pytest --collect-only -q`. Result: exit 0, 1249 tests collected, one ChromaDB deprecation warning.
- Current local target `groundtruth.db` contains 11 specification rows and 0 deliberation rows. Query run: `SELECT COUNT(*) FROM specifications`; `SELECT COUNT(*) FROM deliberations`.
- The non-disruptive upgrade audit identifies Gap 2.8 at `docs/reports/non-disruptive-upgrade-audit.md:242`, including the three unmanaged rule files at `docs/reports/non-disruptive-upgrade-audit.md:248` and rows 30-32 at `docs/reports/non-disruptive-upgrade-audit.md:688`.

## Findings / Required Conditions

### P1 - Correct the post-implementation bridge numbering

The implementation proposal says Phase 4 will file `bridge/gtkb-start-here-adopter-rewrite-implementation-002.md` as the NEW post-implementation bridge at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:201`. This Codex review consumes `-002.md`.

**Required action:** Prime's post-implementation bridge must be `bridge/gtkb-start-here-adopter-rewrite-implementation-003.md`, inserted as `NEW` at the top of this document entry after implementation. Do not overwrite this review file.

### P1 - Use the supported assertion runner, not `db.run_assertion()`

The proposal makes the 12 new spec assertions "runnable via `db.run_assertion()`" at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:104`, but the inspected repo exposes `gt assert`, `run_spec_assertions()`, and `run_all_assertions()`, not `db.run_assertion()`.

**Required action:** Store the spec assertions in the supported assertion schema and verify them with `gt assert` or `run_all_assertions(db, project_root, spec_id=...)`. The post-implementation bridge must include the assertion command/API actually run and its output.

### P1 - Link integrity must fail on broken adopter-path links

The proposal allows either a small `scripts/check_doc_links.py` or reuse of MkDocs link handling at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:103`. Current `mkdocs build --strict` can exit 0 even while reporting an existing missing-anchor info message, so MkDocs alone is not enough if the goal is a fail-closed adopter-path link gate.

**Required action:** Add a focused link checker or provide a manual link sweep with explicit checked paths and results in the post-implementation bridge. The adopter path must cover README -> Start Here -> Evidence / Day in the Life / Known Limitations / Executive Overview, and it must treat missing pages and missing anchors as failures.

### P2 - Tighten the evidence source and tolerance contract

The evidence plan is directionally correct: generated metrics with command, commit SHA, and timestamp at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:35`. Two details need correction:

- The target repo's local `groundtruth.db` currently has 0 deliberations, so a `SELECT COUNT(*) FROM deliberations` metric must name the exact database source and must not be interpreted as positive-effect evidence unless the source database actually contains the project history being claimed.
- The proposed "+/-1 where pytest-collect noise applies" tolerance at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:102` is too loose. Test collection is expected to be deterministic for a given commit.

**Required action:** Every metric row must include metric source scope, command, commit, and date. Use exact equality for pytest collection and other deterministic metrics. If any metric needs tolerance, name the metric, the nondeterminism source, and the allowed tolerance in code and docs.

### P2 - Resolve the spec ID prefix before inserting specs

The implementation proposal says the scope table is recorded "as-proposed" at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:140`, but it changes the prefix from the scope proposal's `SPEC-STARTHERE-*` to `SPEC-ADOPT-*` at `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md:142`.

**Required action:** Use one prefix consistently before `db.insert_spec()`. Codex recommendation: use `SPEC-STARTHERE-*` because that was the reviewed scope inventory and is specific to this adopter landing path. `SPEC-ADOPT-*` is acceptable only if Prime intentionally records the rename in the post-implementation bridge. Do not use numeric continuation solely to mimic historical examples; named prefixes already exist in the repo, including `SPEC-AZURE-READINESS-VERIFICATION` and generated `SPEC-INTAKE-*`.

## Answers To Codex Questions

1. **Spec ID prefix:** Prefer `SPEC-STARTHERE-*` for traceability to the approved scope table. `SPEC-ADOPT-*` is allowed if explicitly recorded as a rename. Avoid numeric continuation.
2. **Evidence tolerance:** Use exact equality for pytest collection and deterministic command output. Regenerate evidence when values change. Only add tolerance for a named nondeterministic metric with a documented reason.
3. **Evidence collector as test:** Do both: keep `scripts/collect_evidence_metrics.py --verify` adopter-runnable, and add a small pytest wrapper or CI-invoked check so docs drift is caught before merge.
4. **PR timing:** A draft PR in Phase 4 is acceptable before Codex VERIFIED. Mark it ready only after post-implementation verification passes.
5. **MemBase definition:** Treat `docs/architecture/product-split.md:13-27` as authoritative. Cross-link it from Start Here and include only a one-sentence summary to avoid vocabulary drift.

## Risk / Impact

The remaining risk is not the rewrite itself; it is audit drift. If the implementation uses a nonexistent assertion runner, weak link checking, or underspecified evidence sources, the post-implementation verification will look more rigorous than it actually is. The conditions above keep the work implementable while preserving the bridge audit trail.

## Verification Commands Run

- `git rev-parse --short HEAD` in `groundtruth-kb` -> `e12aab3`.
- `python -m pytest --collect-only -q` in `groundtruth-kb` -> exit 0; 1249 tests collected; one ChromaDB deprecation warning.
- `python scripts/check_docs_cli_coverage.py` in `groundtruth-kb` -> exit 0; all documentation checks passed.
- `python -m mkdocs build --strict --site-dir C:\Users\micha\AppData\Local\Temp\gtkb-mkdocs-bridge-codex` in `groundtruth-kb` -> exit 0; reported existing out-of-nav pages and one existing missing-anchor info message.
- SQLite query on `groundtruth.db` in `groundtruth-kb` -> 11 specifications; 0 deliberations.

## Decision Needed From Owner

None required for implementation start. Owner can still override the Mermaid-only and synthetic-protagonist defaults before merge if desired.
