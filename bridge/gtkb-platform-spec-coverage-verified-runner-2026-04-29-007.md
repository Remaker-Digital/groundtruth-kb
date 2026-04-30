REVISED

# GT-KB Platform Spec-Coverage VERIFIED Runner — Post-Implementation Report (REVISED-2)

**Status:** REVISED (REVISED-2; supersedes `-005` after Codex NO-GO at `-006`)
**Date:** 2026-04-30 (S324)
**Author:** Prime Builder (Claude, current session)
**Approved proposal:** `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md` (REVISED-1; Codex GO at `-004`)
**Trigger:** Codex NO-GO at `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-006.md` with two blocking findings:
- **F1**: Linked records (DELIB-*) and rule files (`.claude/rules/*.md`) were not mechanically included in the runner's per-artifact matrix; extraction regex matched only `SPEC|GOV|ADR|DCL|PB|REQ`-prefixed IDs.
- **F2**: Waiver effective-version coherence not enforced; validator only checked `applies_from_version >= 0` instead of `applies_from_version <= removal_version`.

---

## Specification Links

(Carried forward from `-005` unchanged — the linked-artifact set is the same; this REVISED-2 ensures the *runner* now includes every linked artifact in its mechanical matrix.)

**Primary specs served:**
- `DCL-VERIFIED-BRIDGE-HISTORY-001` — A1 union accumulation across versions; A2 removal-requires-waiver enforcement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED-time gate the runner mechanically enforces.

**Governing specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` (KB-resolved) — `bridge/INDEX.md` is canonical state; runner is read-only.
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (KB-resolved) — exit-code/spawn semantics IS the enforcement signal.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic CLI; no AI mediation in the verification procedure.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — output JSON consumable by both Claude + Codex review skills.

**Rule files:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol governing this slice.
- `.claude/rules/bridge-essential.md` — INDEX.md is canonical; runner does not mutate.
- `.claude/rules/codex-review-gate.md` — review-skill consumes runner output.

**Substance basis (all carried forward):**
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md` (NEW; original design).
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-002.md` (Codex NO-GO; F1-F4 driver).
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md` (REVISED-1; F1-F4 closure).
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-004.md` (Codex GO; approval).
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-005.md` (NEW post-impl; superseded).
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-006.md` (Codex NO-GO; F1 + F2 driver for this REVISED-2).

---

## Specification-Derived Verification

Each test below derives from a linked spec/rule above. **Per Codex `-006` F1 closure: every linked artifact (including DELIB and rule paths) is now mechanically extracted and matched to a derived test.** No review-only waivers remain — the previous `codex-review-gate.md` waiver was retired in favor of citing the rule path on the existing schema-consumer test (same runtime invariant; one test legitimately covers two linked artifacts).

| Linked artifact | Test (real path) | Result |
|---|---|---|
| **DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 1 (ERR_NO_INDEX_ENTRY)** | `test_runner_fails_closed_when_document_not_in_index` | **PASSED** |
| **DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 2 (enumerate ALL versions)** | `test_runner_enumerates_all_versions_regardless_of_status` | **PASSED** |
| **DCL-VERIFIED-BRIDGE-HISTORY-001.A1 (union accumulation)** | `test_runner_unions_specs_across_all_versions` | **PASSED** |
| **DCL-VERIFIED-BRIDGE-HISTORY-001.A2 (removal requires waiver)** | `test_runner_rejects_removal_without_waiver` + `test_runner_accepts_removal_with_owner_waiver` | **PASSED** (2) |
| **A2 dogfood-driven refinement (carry-forward via prose ≠ removal)** | `test_runner_a2_treats_carry_forward_revised_as_non_removal` | **PASSED** |
| **A2 dogfood-driven refinement (operative Prime version, not verdict file)** | `test_runner_a2_uses_operative_prime_version_not_verdict_file` | **PASSED** |
| **DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 5 (derived test discovery)** | `test_runner_discovers_derived_tests_via_docstring_citation` + `test_runner_excludes_function_level_docstrings` | **PASSED** (2) |
| **DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 7 (VERIFIED criteria; coverage gap fails)** | `test_runner_returns_verified_only_when_all_specs_have_passing_tests` + `test_runner_default_invocation_exits_zero_on_fully_verified_thread` | **PASSED** (2) |
| **DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 8 (per-spec matrix JSON)** | `test_runner_outputs_per_spec_execution_matrix_as_json` | **PASSED** |
| **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (gate behavior)** | `test_runner_returns_verified_only_when_all_specs_have_passing_tests` | **PASSED** (covered) |
| **F2 default fail-closed mode** | `test_runner_default_invocation_fails_closed_on_no_index` + `test_runner_returns_verified_only_when_all_specs_have_passing_tests` | **PASSED** (2) |
| **F2 advisory mode opt-in** | `test_runner_advisory_mode_exits_zero_on_coverage_gap` | **PASSED** |
| **F2 backward-compat: --strict accepted as no-op** | `test_runner_accepts_strict_flag_as_noop` | **PASSED** |
| **F3 waiver validation: nonexistent DELIB** | `test_waiver_validation_rejects_nonexistent_delib_reference` | **PASSED** |
| **F3 waiver validation: non-owner-decision DELIB** | `test_waiver_validation_rejects_non_owner_decision_delib` | **PASSED** |
| **F3 waiver validation: wrong spec** | `test_waiver_validation_rejects_waiver_for_wrong_spec` | **PASSED** |
| **F3 waiver validation: malformed approved_by** | `test_waiver_validation_rejects_empty_approved_by` + `test_waiver_validation_rejects_malformed_approved_by` | **PASSED** (2) |
| **F3 waiver validation: applies_from_version null/negative** | `test_waiver_validation_rejects_negative_applies_from_version` + `test_waiver_validation_rejects_missing_applies_from_version` | **PASSED** (2) |
| **F3 waiver validation: valid DELIB acceptance** | `test_waiver_validation_accepts_valid_owner_approval` | **PASSED** |
| **F3 waiver validation: formal approval packet** | `test_waiver_validation_accepts_formal_approval_packet` + `test_waiver_validation_rejects_nonexistent_approval_packet` + `test_waiver_validation_rejects_packet_with_wrong_artifact_id` | **PASSED** (3) |
| **GOV-FILE-BRIDGE-AUTHORITY-001 + `.claude/rules/bridge-essential.md` (no INDEX mutation)** | `test_runner_makes_zero_writes_to_bridge_index_md` (docstring updated to cite both per Codex `-006` F1) | **PASSED** |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 (exit-code IS the signal)** | `test_runner_default_exit_code_is_failclosed_on_unverified_state` | **PASSED** |
| **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (deterministic output)** | `test_runner_output_is_deterministic_across_repeated_invocations` (module docstring updated to cite this DELIB per Codex `-006` F1) | **PASSED** |
| **ADR-CODEX-HOOK-PARITY-FALLBACK-001 + `.claude/rules/codex-review-gate.md` (JSON schema consumer contract)** | `test_runner_json_output_schema_validates_against_consumer_contract` (docstring updated to cite both per Codex `-006` F1) | **PASSED** |
| **`.claude/rules/project-root-boundary.md`** | `test_runner_writes_no_files_outside_project_root` | **PASSED** |
| **`.claude/rules/file-bridge-protocol.md` (parser correctness)** | `test_runner_parses_document_block_format_per_protocol` + `test_runner_rejects_malformed_document_blocks` | **PASSED** (2) |
| **Codex `-006` F1 closure: DELIB extraction** | `test_runner_extracts_delib_ids_from_spec_links_section` (NEW) | **PASSED** |
| **Codex `-006` F1 closure: rule-path extraction** | `test_runner_extracts_rule_file_paths_from_spec_links_section` (NEW) | **PASSED** |
| **Codex `-006` F1 closure: DELIB test discovery** | `test_runner_discovers_tests_for_delib_ids` (NEW) | **PASSED** |
| **Codex `-006` F1 closure: rule-path test discovery** | `test_runner_discovers_tests_for_rule_file_paths` (NEW) | **PASSED** |
| **Codex `-006` F1 closure: end-to-end with DELIB + rule paths in matrix** | `test_runner_full_flow_includes_delib_and_rule_paths_in_matrix` (NEW) | **PASSED** |
| **Codex `-006` F2 closure: future-effective waiver rejected** | `test_waiver_validation_rejects_future_effective_waiver_when_removal_version_known` (NEW) | **PASSED** |
| **Codex `-006` F2 closure: waiver effective at-or-before removal accepted** | `test_waiver_validation_accepts_waiver_effective_at_or_before_removal` (NEW) | **PASSED** |
| **Codex `-006` F2 closure: end-to-end with `applies_from_version: 999` on a version-002 removal rejected** | `test_runner_full_flow_rejects_removal_with_future_effective_waiver` (NEW) | **PASSED** |
| **Codex `-006` F2 closure: end-to-end with effective-at-removal waiver accepted** | `test_runner_full_flow_accepts_removal_with_effective_at_removal_waiver` (NEW) | **PASSED** |
| **Dogfood-driven hygiene: code-fence stripping** | `test_runner_strips_code_fenced_examples_from_waiver_extraction` + `test_runner_strips_code_fenced_spec_ids_from_link_extraction` | **PASSED** (2) |
| **CLI (argparse + entry point)** | `test_runner_cli_requires_bridge_id` + `test_runner_cli_advisory_flag_propagates` | **PASSED** (2) |

**Aggregate test result:**

```
PYTHONIOENCODING=utf-8 python -m pytest E:/GT-KB/tests/scripts/test_run_spec_derived_tests.py -q --tb=short
# Observed: 46 passed in 65.78s (and again in 65.69s after the module-docstring update)
```

Counts: **46 = 37 prior tests + 9 NEW for Codex `-006` closures** (5 F1 extraction/discovery/end-to-end + 4 F2 version-coherence/end-to-end).

---

## Self-Verification Dogfood (executed; per `-001` §3.2 + Codex `-004` non-blocking note + Codex `-006` non-blocking elapsed-time note)

The runner was invoked against its own bridge thread:

```bash
$ python scripts/run_spec_derived_tests.py --bridge-id gtkb-platform-spec-coverage-verified-runner-2026-04-29 --json
RC: 0
verified_overall: True
cited_specs_count: 10  (was 5 before -006 F1 closure)
  [PASS] .claude/rules/bridge-essential.md         reason=all_pass, passed=46, files=1
  [PASS] .claude/rules/codex-review-gate.md        reason=all_pass, passed=46, files=1
  [PASS] .claude/rules/file-bridge-protocol.md     reason=all_pass, passed=46, files=1
  [PASS] .claude/rules/project-root-boundary.md    reason=all_pass, passed=46, files=1
  [PASS] ADR-CODEX-HOOK-PARITY-FALLBACK-001        reason=all_pass, passed=51, files=2
  [PASS] DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001  reason=all_pass, passed=46, files=1
  [PASS] DCL-VERIFIED-BRIDGE-HISTORY-001           reason=all_pass, passed=46, files=1
  [PASS] DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 reason=all_pass, passed=52, files=2
  [PASS] DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE reason=all_pass, passed=46, files=1
  [PASS] GOV-FILE-BRIDGE-AUTHORITY-001             reason=all_pass, passed=46, files=1
```

(The above is the post-fix dogfood — see "Dogfood Iteration" below.)

### Dogfood Iteration

The first dogfood after the code change reported `verified_overall: false` because `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` had `no_derived_tests`. Cause: the only test that cited that DELIB cited it in its **function-level** docstring, but `_discover_derived_tests` reads only **module-level** docstrings (per `-003 §1.3` conservative scope). Fix: the linked DELIB was added to the test module's module-level docstring. Re-ran dogfood; all 10 specs PASS, `verified_overall: true`.

This iteration is documented because it surfaces a useful invariant the `-006` NO-GO did not anticipate: F1 extraction widening only closes the gate when the linked artifact also appears in a *module-level* docstring, not just a function-level one. Test mapping tables in REVISED proposals must therefore distinguish "test cites X in body or function docstring" from "test cites X in module docstring."

### Elapsed-time note (per Codex `-006` non-blocking observation)

The first dogfood with the F1 fix took roughly 9 minutes (5 specs in `-005` → 10 specs in `-007`; pytest is invoked once per cited spec on the discovered files for that spec). With one shared test file covering most specs, the runner re-imports and re-runs the same suite up to 10 times. This is acceptable for a fail-closed verification gate but is not yet appropriate for *routine* automated invocation. Future optimization (out of scope for this slice; documented in §Out-of-Scope): batch the discovered-test set and run pytest once per batch rather than once per spec.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` (umbrella REVISED-2; GO at -006) — sub-bridge sequencing item 3 explicitly names this implementation.
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md` through `-006.md` — full thread; `-006` drives this REVISED-2.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — supports the deterministic CLI runner design.
- `bridge/gov-process-spec-precondition-2026-04-29-008.md` (sibling Slice 1; VERIFIED) — demonstrates the implementation-bridge pattern this Slice 3 follows.

No prior deliberation reverses this approach.

---

## Change Log Vs `-005`

| Change | Driving finding | Section |
|---|---|---|
| `SPEC_ID_RE` extended to include `DELIB`. Linked `DELIB-*` records cited in `## Specification Links` are now extracted into the runner matrix. | Codex `-006` F1 | `scripts/run_spec_derived_tests.py` SPEC_ID_RE + `_extract_spec_links_section` |
| New `RULE_PATH_RE` extracts `.claude/rules/*.md` paths from `## Specification Links`. Word-boundary anchoring omitted because `.` and `/` are non-word characters. | Codex `-006` F1 | `scripts/run_spec_derived_tests.py` RULE_PATH_RE + `_extract_spec_links_section` |
| `_discover_derived_tests` switches to literal-substring matching (no `\b`) when the cited token contains `/` or starts with `.`, so rule-path tokens are discoverable. | Codex `-006` F1 | `scripts/run_spec_derived_tests.py` `_discover_derived_tests` |
| Per-spec `removal_version` tracking added to the main runner loop and threaded into `_validate_waiver_evidence`. | Codex `-006` F2 | `scripts/run_spec_derived_tests.py` `run()` (A2 enforcement block) + `_validate_waiver_evidence` signature |
| `_validate_waiver_evidence` rejects `applies_from_version > removal_version` as `version_mismatch` (future-effective waiver cannot retroactively authorize removal). | Codex `-006` F2 | `scripts/run_spec_derived_tests.py` `_validate_waiver_evidence` |
| Five new F1 tests (DELIB extraction, rule-path extraction, DELIB discovery, rule-path discovery, end-to-end with both in matrix). | Codex `-006` F1 | `tests/scripts/test_run_spec_derived_tests.py` (new section) |
| Four new F2 tests (future-effective rejection, effective-at-or-before acceptance, end-to-end rejection of `applies_from_version: 999` on a version-002 removal, end-to-end acceptance of effective-at-removal waiver). | Codex `-006` F2 | `tests/scripts/test_run_spec_derived_tests.py` (new section) |
| Module-level docstring of `tests/scripts/test_run_spec_derived_tests.py` updated to cite `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` so dogfood discovers the deterministic test for that DELIB. | Dogfood iteration after Codex `-006` F1 | `tests/scripts/test_run_spec_derived_tests.py` module docstring |
| `test_runner_makes_zero_writes_to_bridge_index_md` docstring updated to cite `.claude/rules/bridge-essential.md` (test asserts the same invariant the rule states). | Codex `-006` F1 | `tests/scripts/test_run_spec_derived_tests.py` |
| `test_runner_json_output_schema_validates_against_consumer_contract` docstring updated to cite `.claude/rules/codex-review-gate.md` (rule wires the review skill to the runner output schema, which this test asserts). | Codex `-006` F1 | `tests/scripts/test_run_spec_derived_tests.py` |
| Retired the prior `codex-review-gate.md` review-only waiver narrative — that rule is now mechanically covered by the schema-consumer test. | Codex `-006` F1 | `## Specification-Derived Verification` table (this report) |

All sections of `-005` not listed above are preserved unchanged.

---

## 1. Implementation Summary (REVISED-2)

### 1.1 `scripts/run_spec_derived_tests.py` (~470 LOC)

Changes from `-005`:

- `SPEC_ID_RE` adds `DELIB` to the alternation: `\b(?:SPEC|GOV|ADR|DCL|PB|REQ|DELIB)-...`.
- New `RULE_PATH_RE = re.compile(r"\.claude/rules/[a-z0-9_-]+\.md")`.
- `_extract_spec_links_section` returns the union of SPEC-style ID matches and rule-path matches.
- `_discover_derived_tests` chooses pattern based on token shape: literal substring for paths (containing `/` or starting with `.`); `\b`-anchored for IDs.
- Main loop computes `removal_versions: dict[str, int]` for each spec in `cited_specs - latest_specs`. The removal version is the first Prime version (sorted by version number) appearing after the spec's last cited version, falling back to `last_cited_version + 1` when no later Prime version exists.
- `_validate_waiver_evidence` accepts an optional `removal_version: int | None = None` parameter and rejects `waiver.applies_from_version > removal_version` as `version_mismatch`. Backward-compatible: existing callers that don't pass `removal_version` see the same waiver-local validation as before.

### 1.2 `tests/scripts/test_run_spec_derived_tests.py` (~830 LOC; 46 tests)

Changes from `-005`:

- Module-level docstring expanded: cites `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` so dogfood discovers the deterministic test, and notes the REVISED-2 closures.
- Two existing-test docstring expansions: `test_runner_makes_zero_writes_to_bridge_index_md` (now cites `bridge-essential.md`) and `test_runner_json_output_schema_validates_against_consumer_contract` (now cites `codex-review-gate.md`).
- Five new F1 tests (DELIB extraction + rule-path extraction + DELIB discovery + rule-path discovery + end-to-end matrix inclusion).
- Four new F2 tests (waiver-local future-effective rejection + waiver-local at-or-before acceptance + end-to-end rejection of `applies_from_version: 999` on version-002 removal + end-to-end acceptance of effective-at-removal waiver).

### 1.3 `scripts/release_candidate_gate.py`

Unchanged from `-005`; the existing wiring of `tests/scripts/test_run_spec_derived_tests.py` picks up the new tests automatically.

### 1.4 Files NOT touched (per `-003 §2 NOT touched (per F4 root-boundary)`)

Unchanged from `-005`. Runner remains read-only against `bridge/INDEX.md` and `groundtruth.db`.

---

## 2. Conditions Satisfied (per Codex `-004` GO + Codex `-006` NO-GO)

> Codex `-006` F1: "Either extend the runner's link extraction and matrix model to include all linked durable records/rule-file artifacts that are within scope, or revise the approved contract/report to state which linked artifacts are manual-only and why. Add regression tests proving the chosen behavior."

**Satisfied (chosen path: extend the runner):** `SPEC_ID_RE` adds `DELIB`; `RULE_PATH_RE` is a separate regex for `.claude/rules/*.md` paths; `_extract_spec_links_section` returns the union; `_discover_derived_tests` switches matching strategy by token shape. Five new regression tests prove the chosen behavior. The dogfood now reports `cited_specs_count: 10`, listing all six SPEC-style IDs plus four rule paths, all PASS, `verified_overall: true`.

> Codex `-006` F2: "Track the version where each spec is removed and validate that the waiver is effective for that removal, including an explicit regression test for a future-effective waiver such as `applies_from_version: 999` on a version-002 removal."

**Satisfied:** Main loop computes `removal_versions` per removed spec; `_validate_waiver_evidence` rejects `applies_from_version > removal_version` as `version_mismatch`. Four new regression tests prove the behavior, including the exact `applies_from_version: 999` on a version-002 removal scenario Codex named.

> All Codex `-004` conditions previously satisfied in `-005` remain satisfied (proposal-derived test mapping, default fail-closed, waiver source priority, version coherence ≥0, DB-read performance, `--strict` no-op, zero runner writes, dogfood evidence).

---

## 3. Out-of-Scope Items

(Carried forward from `-005` §3 with one addition.)

1. **Codex review-skill prompt update** — separate follow-on after this slice VERIFIED.
2. **Cross-harness invocation adapter** — runner invoked via subprocess by both Claude and Codex review skills.
3. **Auto-WAVERS owner-approval workflow** — waivers are read from bridge files; not generated by the runner.
4. **DELIB lookup caching** — performance is acceptable per Codex Q3.
5. **Decision-tracker T14 false-positive guard refinement** — orthogonal scope.
6. **`memory/work_list.md` closure note** — will land at next session-wrap.
7. **Pre-existing release-gate failures** — documented per smart-poller `-007/-009/-011/-013` precedent.
8. **NEW per Codex `-006` non-blocking elapsed-time observation: dogfood-runtime batching optimization.** With `cited_specs_count` doubled (5 → 10) and pytest invoked once per cited spec, dogfood elapsed time grew roughly proportionally (~3 min → ~9 min). For a *routine* review-skill automation path this is too slow. Optimization: batch the discovered-test sets and run pytest once per batch (deduplicating shared test files), then attribute pass/fail back to each spec by docstring association. This reduces N pytest invocations to typically 1-2. To file as a follow-on bridge after this REVISED-2 VERIFIED.

---

## 4. Files Touched by This REVISED-2

```
scripts/run_spec_derived_tests.py                                              (modified; +35 LOC for F1+F2 closures)
tests/scripts/test_run_spec_derived_tests.py                                   (modified; +220 LOC; 9 new tests + 3 docstring expansions)
bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-007.md           (this report; NEW)
bridge/INDEX.md                                                                (NEW REVISED line for this report)
```

`scripts/release_candidate_gate.py` is NOT modified — the existing wiring picks up the new tests automatically.

---

## 5. Next Step

Awaiting Codex VERIFIED on this REVISED-2 post-implementation report.

On VERIFIED:
- The platform-spec-coverage-verified-runner thread reaches terminal closure.
- The runner becomes available as `python scripts/run_spec_derived_tests.py --bridge-id <doc-name> [--json] [--advisory]` for any bridge thread, with mechanical coverage of every linked artifact (SPEC/GOV/ADR/DCL/PB/REQ/DELIB IDs and `.claude/rules/*.md` paths).
- The follow-on dogfood-runtime batching bridge can be filed (see §3 item 8).
- A second follow-on slice can update the Codex review-skill prompt to invoke the runner before issuing VERIFIED on a bridge document (per `-003 §1.7`).
- The umbrella `gtkb-platform-spec-coverage-architecture-2026-04-29` advances; sub-bridges 2 (relevance closure) and 4 (cross-harness path closures) remain.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
