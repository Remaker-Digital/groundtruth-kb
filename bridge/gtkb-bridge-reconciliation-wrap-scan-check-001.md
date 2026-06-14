NEW

bridge_kind: implementation_proposal
Document: gtkb-bridge-reconciliation-wrap-scan-check
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 37191790-3efe-4e97-a707-f8d798f7f238
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4238
target_paths: ["scripts/wrap_scan_reconciliation.py", "platform_tests/scripts/test_wrap_scan_reconciliation.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4238: Integrate bridge reconciliation detection into the session-wrap scan (routine report-only check)

## Summary

WI-4238 ("Integrate bridge reconciliation checks into hygiene sweep or session-wrap scan") operationalizes the VERIFIED bridge-reconciliation detector so deviation detection runs **routinely**, not only on operator demand. The detector already exists and is VERIFIED: `scripts/bridge_reconciliation_audit.py` exposes a read-only public `run_audit(*, project_root, db_path, bridge_index) -> dict` (the function behind `gt bridge reconcile audit`) that returns `issues` plus `counts` keyed by **deviation class** (`bridge_index_drift`, `work_item_linkage`, `stale_backlog`, `terminal_without_evidence`, `verified_bridge_backlog`). The done-but-unreconciled gap this detector surfaces (e.g., VERIFIED bridge threads whose work-item rows stay `open`) is real and recurring; making it a routine wrap-scan signal is the WI's value.

The session-wrap scan is the correct routine surface (the existing `gt hygiene sweep` is **pattern-set/text-match driven** per `scripts/../hygiene/sweep.py` and does not accommodate the detector's *structural* INDEX↔work-item analysis). This slice adds one new report-only wrap-scan scanner, `scripts/wrap_scan_reconciliation.py`, that follows the established `wrap_scan_*` contract (`scripts/wrap_scan_consistency.py`, `scripts/wrap_scan_cross_artifact_drift.py`, `scripts/wrap_scan_hygiene.py`): it composes with — and does not replace — those scanners. It is **additive** (one new module + one new test), reuses the VERIFIED detector unchanged, and modifies no existing scanner, no canonical surface, and no `gt` CLI file.

It is **non-duplicative** of `gt bridge reconcile audit`: that command is the on-demand operator surface; this scanner is the routine session-wrap surface that emits deviation counts by class as informational, report-only findings for the wrap-scan harvest.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — the scanner surfaces backlog/bridge reconciliation drift (work items whose lifecycle state has drifted from their VERIFIED bridge evidence); WI-4238 is the backlog authority for this slice.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the scanner is read-only over `bridge/INDEX.md` and the canonical bridge files; it writes nothing to them and changes no bridge authority. The reused `run_audit` reads INDEX + `groundtruth.db` read-only.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implementation proceeds under the active `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` (which includes WI-4238 and allows `source` + `test_addition`).
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** — reconciliation drift is precisely a lifecycle-state divergence between artifacts (bridge thread VERIFIED vs work-item open); routinely surfacing it serves artifact-lifecycle governance.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH/project/work-item/target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each linked spec/acceptance criterion to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements sufficient. The PAUTH `scope_summary` authorizes "deterministic read-only bridge/backlog deviation detection ... [as a] reusable read-only hygiene-sweep check, session-wrap scan, or equivalent command surface." `GOV-STANDING-BACKLOG-001` and the VERIFIED audit detector (WI-4234) define the deviation classes; the established `wrap_scan_*` contract defines the report-only scanner shape. No new or revised formal specification is required — this slice is a routine-surface integration of an already-specified, already-VERIFIED detector.

## Prior Deliberations

- **`DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT`** — the owner decision backing `PROJECT-GTKB-BRIDGE-RECONCILIATION` and its `...-DETECTION-CORRECTION` PAUTH, which enumerates WI-4238.
- **`bridge/gtkb-bridge-backlog-reconciliation-audit-cli` (VERIFIED, WI-4234)** — shipped `scripts/bridge_reconciliation_audit.py` with the `run_audit()` public detector this slice reuses unchanged.
- **`bridge/gtkb-bridge-index-chain-deviation-detector` (VERIFIED, WI-4235)** and **`bridge/gtkb-bridge-reconciliation-correction-packets` (VERIFIED, WI-4236)** — sibling reconciliation slices (chain-deviation detection, governed correction packets) the deviation taxonomy aligns with.
- **`bridge/gtkb-reconciler-wi-bridge-linkage-derivation` (VERIFIED, WI-4533)** — the WI↔bridge linkage reconciler; this routine wrap-scan check is the read-only *surfacing* counterpart to that corrective service.
- **`bridge/gtkb-wrapup-enhancements-next-slice-003.md` (GO at -004)** — established the report-only `wrap_scan_*` session-wrap scanner pattern this module follows.
- **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive routine checks belong in deterministic services, not ad-hoc sessions; this slice moves reconciliation drift detection into a routine service surface.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT`** — recorded as `owner_decision_deliberation_id` on the active `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION`, whose scope authorizes the reusable read-only reconciliation check as a "session-wrap scan or equivalent command surface."
- The slice stays within the PAUTH's `allowed_mutation_classes` (`source`, `test_addition`): one new source module + one new test. It performs no MemBase mutation, no formal-artifact mutation, no canonical-INDEX write, and no change to any existing scanner or CLI. No expanded owner authorization is requested.

## Design (Slice)

New module `scripts/wrap_scan_reconciliation.py`, following the `wrap_scan_*` report-only contract:

- Module constants `SCANNER_ID = "wrap_scan_reconciliation"`, `SEVERITY_INFORMATIONAL = "informational"`, `EXIT_OK = 0`.
- Imports the VERIFIED detector via the supported public surface: `run_audit` from `scripts/bridge_reconciliation_audit.py` (loaded the same way the other wrap-scan scanners load sibling helpers — by path, since `scripts/` is not an installed package). No private (`_`-prefixed) audit functions are used; the module depends only on `run_audit`'s documented `dict` result (`issues`, `counts`).
- **Pure transform** `build_reconciliation_findings(audit_result) -> list[dict]`: converts the audit result into the wrap-scan `_finding(check, message, **details)` shape — one informational, `report_only=True` finding per non-zero deviation class carrying that class's count, plus a single roll-up finding with the total and the per-class breakdown. Zero deviations ⇒ a single "no reconciliation drift" informational finding (never an error; report-only by design).
- **`scan(project_root, *, db_path=None, bridge_index=None) -> dict`**: calls `run_audit(...)` read-only and returns a `SweepResult`-style dict (`scanner_id`, `generated_at` injected, `finding_count`, `findings`, `counts_by_class`).
- **`main(argv=None) -> int`**: argparse entrypoint; resolves the project root, runs `scan`, writes `reconciliation-scan.json` + `.md` to the session-wrap output dir via `_wrap_io._atomic_write_text`, or `--stdout`. **Always returns `EXIT_OK` (0)** — findings are informational/report-only, matching the established wrap-scan exit contract. Runnable via `python scripts/wrap_scan_reconciliation.py`.
- Determinism: `generated_at` injected for tests; findings sorted by deviation class; no `Date.now`/random; identical inputs ⇒ identical output.

The session-wrap-scan skill (`kb-session-wrap-scan`) can invoke this scanner alongside the existing `wrap_scan_*` modules; the orchestration wiring (skill doc) is a thin follow-on and is **out of scope** for this code slice, which ships the scanner + its tests.

## Verification Plan (Specification-Derived)

| Spec / Acceptance criterion | Test (in `platform_tests/scripts/test_wrap_scan_reconciliation.py`) | Method |
|---|---|---|
| GOV-STANDING-BACKLOG-001 — deviation counts by class | `test_findings_one_per_nonzero_class`, `test_rollup_finding_totals` | synthetic audit-result fixtures → assert one finding per non-zero class + a roll-up with correct totals/breakdown |
| GOV-FILE-BRIDGE-AUTHORITY-001 — read-only, report-only | `test_main_exit_code_always_zero`, `test_no_mutation_surface_ast` | `main()` returns 0 even with deviations; AST scan asserts no canonical-write/MemBase-mutation surface in the module |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — lifecycle drift surfaced | `test_verified_bridge_backlog_class_surfaced`, `test_zero_deviations_informational` | a `verified_bridge_backlog` deviation fixture is surfaced; empty audit ⇒ single informational finding (no error) |
| Determinism + wrap-scan contract conformance | `test_determinism_same_input_same_output`, `test_finding_shape_matches_contract` | same fixture + same `generated_at` ⇒ byte-identical output; each finding has `check`/`severity`/`report_only`/`message` |
| Integration with the VERIFIED detector | `test_scan_invokes_run_audit_readonly` | `scan()` calls `run_audit` against a controlled fixture root/DB; asserts read-only (inputs unchanged) |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_wrap_scan_reconciliation.py -q --tb=short`; plus a smoke run `python scripts/wrap_scan_reconciliation.py --stdout` against the live repo (expect exit 0).

## Risk / Rollback

- **Risk: low.** Additive (2 new files), read-only, report-only (always exit 0). It reuses the VERIFIED `run_audit` unchanged and modifies no existing scanner, CLI, or canonical surface — so it cannot regress the session-wrap scan or the bridge/backlog state.
- **Duplication risk** vs `gt bridge reconcile audit`: addressed by surface separation — on-demand operator CLI vs routine report-only wrap-scan scanner — both reusing the single VERIFIED detector (no detector logic is copied).
- **Coupling risk** to `run_audit`'s result shape: mitigated by depending only on its documented public `dict` keys (`issues`, `counts`) and by `test_scan_invokes_run_audit_readonly`, which fails if the contract drifts.
- **Rollback:** delete the two new files. No migration, no KB mutation, no canonical artifact changed.

## Recommended Commit Type

`feat:` — adds a net-new report-only session-wrap reconciliation scanner (routine surface) plus tests, reusing the VERIFIED detector; no behavior change to existing scanners/CLI, no canonical change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
