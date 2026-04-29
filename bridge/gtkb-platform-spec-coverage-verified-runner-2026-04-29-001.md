NEW

# GT-KB Platform Spec-Coverage: VERIFIED Runner Implementation

**Status:** NEW (implementation bridge for Slice 3 / sub-bridge "verified-bridge-history-runner" of `gtkb-platform-spec-coverage-architecture-2026-04-29` umbrella; umbrella GO at -006)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Owner directive to implement a slice of the spec-coverage architecture program. Per umbrella section 3 sequencing, this is sub-bridge 3 (full-history VERIFIED runner). Slice 1 (`gov-process-spec-precondition`) already VERIFIED at -008; Slice 2 (relevance closure) still future; this Slice 3 is independent of Slice 2 and can land in parallel.

bridge_kind: implementation_proposal
work_item_ids: [GTKB-PLATFORM-SPEC-COVERAGE-ARCHITECTURE]
spec_ids: [DCL-VERIFIED-BRIDGE-HISTORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001]
parent_bridge: bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md (umbrella REVISED-2; approved at -006)
target_project: agent-red (in-root scripts/ + tests/; Codex-skill prompt update may upstream later)
implementation_scope: cli script + tests
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate. Codex MUST issue rejection on this proposal if any relevant specification is missing.

**Primary spec served (governing DCL):**
- `DCL-VERIFIED-BRIDGE-HISTORY-001` — "VERIFIED runner must operate on full bridge thread history, not single file". KB-resolved at status=specified. Defines the 8-step deterministic runner procedure plus assertions A1 (union accumulation across versions) and A2 (removal requires owner-approved waiver).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED-time gate that this runner enforces. KB-resolved.

**Umbrella linkage:**
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` (REVISED-2; approved at -006) — section 3 sub-bridge sequencing item 3 explicitly names this implementation: "scripts/run_spec_derived_tests.py per DCL-VERIFIED-BRIDGE-HISTORY-001.A1 plus .A2".
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-006.md` (Codex umbrella approval) — confirms umbrella authorizes scoping only; this implementation bridge carries its own Specification Links + test mapping per Codex constraint.

**Governance specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is sole authoritative source; the runner reads INDEX.md as canonical state per its own contract.
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — the runner is the mechanical enforcement layer that turns DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 from a documented rule into a runnable check.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the runner is a deterministic service (CLI input/output; no AI mediation needed for the verification procedure).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — runner output (per-spec execution matrix) is consumable by both Claude and Codex review skills.

**Adjacent / parallel work:**
- `bridge/gov-process-spec-precondition-2026-04-29-008.md` (VERIFIED) — Slice 1 of umbrella; modified bridge-compliance-gate.py to emit_deny on missing Specification Links. This Slice 3 enforces the VERIFIED-time analog (the gate fires at filing time; the runner fires at VERIFIED time).

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — defines the Document: / status format the runner parses.
- `.claude/rules/codex-review-gate.md` — Codex review skill consumes the runner output.
- `.claude/rules/bridge-essential.md` — the runner does NOT mutate INDEX.md; it only reads.

---

## Specification-Derived Verification (Test Mapping)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate, every test below derives from `DCL-VERIFIED-BRIDGE-HISTORY-001.A1` / `.A2` plus `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec assertion / clause | Test |
|-------------------------|------|
| DCL-VERIFIED-BRIDGE-HISTORY-001.A1 (union accumulation across versions) | `test_runner_unions_specs_across_all_versions` — synthesize a bridge thread with -001 NEW citing SPEC-A and -003 REVISED citing SPEC-A plus SPEC-B; assert runner outputs union {SPEC-A, SPEC-B}. Run via `pytest tests/scripts/test_run_spec_derived_tests.py -v`. |
| DCL-VERIFIED-BRIDGE-HISTORY-001.A2 (removal requires waiver) | `test_runner_rejects_removal_without_waiver` — synthesize bridge thread with -001 citing SPEC-A and -003 REVISED citing only SPEC-B with no waiver; assert runner fails-closed with explanation. Plus `test_runner_accepts_removal_with_owner_waiver` — same scenario but -003 includes Specification-Coverage-Waivers section; assert runner accepts the union {SPEC-A (waived), SPEC-B}. Run via `pytest`. |
| DCL procedure step 1 (ERR_NO_INDEX_ENTRY) | `test_runner_fails_closed_when_document_not_in_index` — runner called with bridge_document_name not present in INDEX.md; assert exit code non-zero and stderr includes ERR_NO_INDEX_ENTRY. Run via `pytest`. |
| DCL procedure step 2 (enumerate ALL versions) | `test_runner_enumerates_all_versions_regardless_of_status` — INDEX entry has NEW + NO-GO + REVISED + GO; runner reads all four files, not just the latest. Run via `pytest`. |
| DCL procedure step 5 (derived test discovery) | `test_runner_discovers_derived_tests_via_docstring_citation` — synthesize a test file whose docstring cites SPEC-X-001; runner finds it for spec SPEC-X-001. Run via `pytest`. |
| DCL procedure step 6 (pytest execution) | `test_runner_executes_pytest_on_discovered_tests` — runner invokes pytest on identified test files; captures pass/fail. Run via `pytest`. |
| DCL procedure step 7 (VERIFIED criteria) | `test_runner_returns_verified_only_when_all_specs_have_passing_tests` — coverage gap (spec X has no test) returns non-VERIFIED; failing test returns non-VERIFIED; only union-coverage + all-pass returns VERIFIED. Run via `pytest`. |
| DCL procedure step 8 (per-spec matrix output) | `test_runner_outputs_per_spec_execution_matrix_as_json` — JSON output schema validated; per-spec entries include `spec_id`, `tests_found`, `tests_passed`, `tests_failed`, `verified` boolean. Run via `pytest`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (gate behavior) | `test_runner_enforces_verified_spec_derived_testing_mandatory` — given a fully-passing run, output is suitable for Codex review skill to consume as VERIFIED evidence. Run via `pytest`. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full runner test suite as part of the regression gate.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` (REVISED-2; umbrella) — sub-bridge sequencing names this exact implementation as item 3.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-006.md` (Codex GO; umbrella) — authorizes umbrella scoping only; explicitly delegates implementation to focused sub-bridges.
- `bridge/gov-process-spec-precondition-2026-04-29-008.md` (VERIFIED) — Slice 1 sibling; demonstrates the implementation-bridge pattern this Slice 3 follows.
- No prior deliberation reverses this approach.

---

## 1. Implementation Design

### 1.1 CLI Surface

```
python scripts/run_spec_derived_tests.py --bridge-id <document-name> [--json] [--strict]
```

Arguments:
- `--bridge-id <document-name>` (required): kebab-case Document: name from `bridge/INDEX.md` (e.g., `gtkb-platform-spec-coverage-architecture-2026-04-29`).
- `--json` (optional): emit JSON output to stdout instead of human-readable text. Required for Codex review-skill consumption.
- `--strict` (optional): exit non-zero if ANY spec lacks a derived test (default: print warning but exit 0 if all derived tests pass).

### 1.2 Procedure (per DCL-VERIFIED-BRIDGE-HISTORY-001 8-step)

```python
def run(bridge_document_name: str) -> dict:
    # Step 1: Parse INDEX
    versions = parse_index_for_document(bridge_document_name)
    if not versions:
        return error_exit("ERR_NO_INDEX_ENTRY", bridge_document_name)

    # Step 2: Enumerate all versions (regardless of status)
    files = [path for status, path in versions]

    # Step 3-4: Extract Specification Links + waivers; compute union
    cited_specs = set()
    waivers = {}
    for f in sorted(files, key=version_number):
        spec_links = extract_spec_links_section(read(f))
        waivers_section = extract_waivers_section(read(f))
        cited_specs.update(spec_links)
        # A2: removed specs without waiver are detected here
        if waivers_section:
            waivers.update(waivers_section)

    # A2 enforcement: detect specs cited in earlier versions but not later, without waiver
    cited_history = compute_per_version_cited_history(files)
    for spec_id in cited_history.cited_in_any:
        if spec_id not in cited_history.cited_in_latest and spec_id not in waivers:
            return error_exit("ERR_REMOVAL_WITHOUT_WAIVER", spec_id)

    # Step 5: Derived test discovery (grep test docstrings)
    test_map = {spec_id: discover_derived_tests(spec_id) for spec_id in cited_specs}

    # Step 6-7: Execute via pytest; return matrix
    matrix = {}
    for spec_id, test_files in test_map.items():
        if not test_files:
            matrix[spec_id] = {"tests_found": [], "tests_passed": 0, "tests_failed": 0, "verified": False, "reason": "no_derived_tests"}
            continue
        result = run_pytest(test_files)
        matrix[spec_id] = {
            "tests_found": test_files,
            "tests_passed": result.passed,
            "tests_failed": result.failed,
            "verified": result.failed == 0,
            "reason": "all_pass" if result.failed == 0 else "tests_failed",
        }

    # Step 8: Output matrix
    return {
        "bridge_document_name": bridge_document_name,
        "cited_specs_count": len(cited_specs),
        "matrix": matrix,
        "verified_overall": all(entry["verified"] for entry in matrix.values()),
        "waivers_applied": list(waivers.keys()),
    }
```

### 1.3 Derived Test Discovery (DCL procedure step 5)

A derived test is a pytest test function or test file whose **module-level docstring** cites the spec ID. Mechanism:

```python
def discover_derived_tests(spec_id: str) -> list[Path]:
    """Find all test files whose docstring cites spec_id."""
    pattern = re.compile(rf"\b{re.escape(spec_id)}\b")
    matches = []
    for test_file in Path("tests").rglob("test_*.py"):
        with test_file.open() as f:
            source = f.read()
        # Module docstring is the first triple-quoted string after any imports/comments
        try:
            tree = ast.parse(source)
            module_docstring = ast.get_docstring(tree)
        except SyntaxError:
            continue
        if module_docstring and pattern.search(module_docstring):
            matches.append(test_file)
    return matches
```

This is intentionally CONSERVATIVE: we look at module-level docstrings only, not function-level. Function-level discovery would risk overcounting; module-level keeps the contract clear: "this test file exists to verify SPEC-X". Coverage of `groundtruth-kb/tests/` adds parallel discovery via `Path("groundtruth-kb/tests").rglob(...)` if path exists.

### 1.4 Pytest Execution

Subprocess invocation: `pytest <test_files> --tb=short -q --no-header`. Capture exit code + parse pass/fail counts from output. Use Python `subprocess.run` with timeout (default 120s; configurable via `--pytest-timeout`).

### 1.5 Specification-Coverage-Waivers Schema

Per DCL procedure step 3 plus A2 enforcement:

```markdown
## Specification-Coverage-Waivers

- spec_id: SPEC-X-001
  reason: "Superseded by SPEC-Y-002; SPEC-X-001 retired by owner decision DELIB-NNNN."
  approved_by: owner_decision_DELIB-NNNN
  applies_from_version: 003

- spec_id: SPEC-Z-001
  reason: "Out of slice scope; covered by separate bridge X."
  approved_by: ...
  applies_from_version: 003
```

Parser tolerates both YAML-ish and plain-text bullet formats; requires `approved_by` field non-empty (per A2).

### 1.6 Output Format

**Human-readable (default):**
```
Bridge: gtkb-platform-spec-coverage-architecture-2026-04-29
Cited specs: 11 (across 6 versions)
Waivers applied: 0

Per-spec verification:
  GOV-01                                       [PASS]   3 tests, all pass
  GOV-03                                       [PASS]   2 tests, all pass
  DCL-VERIFIED-BRIDGE-HISTORY-001              [PASS]   4 tests, all pass
  DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 [GAP]  0 tests, no derived tests found
  ...

Overall verified: NO (1 spec lacks coverage)
```

**JSON (--json):** structured per the matrix schema in section 1.2.

### 1.7 Codex Review-Skill Integration

Codex review skill prompt update (separate small addition to its system prompt):

> Before issuing VERIFIED on a bridge document, invoke the runner via:
> `python scripts/run_spec_derived_tests.py --bridge-id <document-name> --json`
> If `verified_overall: false` in the output, issue NO-GO with the runner output as evidence rather than VERIFIED.

This integration is documented but the actual prompt update is a follow-on that doesn't block this slice's VERIFIED.

---

## 2. Files Touched

**New:**
- `scripts/run_spec_derived_tests.py` (NEW; ~250 lines including the procedure plus parsing helpers plus output formatters)
- `tests/scripts/test_run_spec_derived_tests.py` (NEW; ~350 lines covering the 9 derivation tests above)
- `tests/scripts/fixtures/run_spec_derived_tests/` (NEW directory with synthesized bridge fixtures)

**Modified:**
- `scripts/release_candidate_gate.py` — add a new test phase that runs `tests/scripts/test_run_spec_derived_tests.py`.
- `memory/work_list.md` — on VERIFIED, add closure note to the platform-spec-coverage row (or create one if not present).

**Not touched:**
- `bridge/INDEX.md` — runner reads only; never writes.
- `groundtruth.db` — runner is read-only against any KB it touches (in this slice it doesn't touch KB at all; future relevance-closure slice will).

---

## 3. Verification Plan

### 3.1 Tests (per Specification-Derived Verification table)

All nine test cases from the derivation table above must pass:

```bash
pytest tests/scripts/test_run_spec_derived_tests.py -v
```

### 3.2 Self-Verification (dogfood)

Once implemented, run the runner against this very bridge thread:

```bash
python scripts/run_spec_derived_tests.py --bridge-id gtkb-platform-spec-coverage-verified-runner-2026-04-29 --json
```

Expected: matrix shows DCL-VERIFIED-BRIDGE-HISTORY-001 plus DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 plus all governance specs cited above. Each has tests found and passing. `verified_overall: true`.

This dogfood self-verification is a strong signal the implementation is sound.

### 3.3 Non-Regression

- `tests/scripts/test_release_candidate_gate.py` continues to pass.
- Existing bridge-compliance-gate.py behavior unchanged.
- Existing scripts in `scripts/` continue to run.

---

## 4. Acceptance Criteria

1. Functional: all nine test cases from Specification-Derived Verification table pass.
2. CLI: `--bridge-id`, `--json`, `--strict` options work as documented in section 1.1.
3. A1 enforcement: union accumulation across versions; REVISED versions can ADD specs without disruption.
4. A2 enforcement: removal of a spec without owner-approved waiver is fail-closed; with waiver in same version, accepted.
5. Step 1 fail-closed: missing INDEX entry returns ERR_NO_INDEX_ENTRY with non-zero exit code.
6. Self-verification: runner against this very bridge produces `verified_overall: true`.
7. Determinism: repeated runs against the same INDEX state and test corpus produce identical output (per DCL "deterministic" qualifier).
8. Performance: runner against a typical bridge (10 versions, 5 cited specs, 50 derived tests) completes in under 60 seconds.

---

## 5. Sequencing and Concurrency

Internal: single coherent slice.

External:
- Parent umbrella `gtkb-platform-spec-coverage-architecture-2026-04-29` approved at -006.
- Sibling Slice 1 (`gov-process-spec-precondition`) VERIFIED at -008 (independent).
- Sibling Slice 2 (relevance closure) future; this Slice 3 does NOT depend on Slice 2 — they can land in parallel because Slice 2 modifies the bridge-compliance-gate hook (filing-time gate) while Slice 3 adds a separate runner script (VERIFIED-time gate).
- Sibling Slice 4 (cross-harness path closures) future; depends on neither this slice nor Slice 2.
- This slice independent of `gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29` (different subsystem entirely).

Concurrency: runner is read-only; no shared mutable state with other hooks/scripts.

---

## 6. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:
- All new and modified files under `E:\GT-KB`.
- This is an Agent-Red-side script (lives in `scripts/`); Codex skill prompt update may upstream to `groundtruth-kb/templates/skills/` in a follow-on.

---

## 7. Out of Scope

- Codex review-skill prompt update (small follow-on after this slice VERIFIED; documented in section 1.7).
- Runner integration with bridge-compliance-gate.py (filing-time gate — that's Slice 2 scope).
- Runner GUI / dashboard surface (CLI only).
- Runner remote invocation (local filesystem only).
- Cross-harness invocation (Codex calls the runner via subprocess; that's the same as Claude — no separate adapter needed).
- Auto-WAVERS owner-approval workflow (waivers are read from the bridge file; not generated by the runner).

---

## 8. Rollback Plan

To disable this slice:
1. Remove the new `scripts/run_spec_derived_tests.py` and `tests/scripts/test_run_spec_derived_tests.py`.
2. Revert the `scripts/release_candidate_gate.py` modification.
3. No KB or bridge state affected (runner is read-only).
4. Any Codex review skill prompt that references the runner CLI will need to be updated (currently no such reference until follow-on lands).

Slice writes ZERO data to `groundtruth.db`, ZERO data to `bridge/INDEX.md`, and ZERO data to the Deliberation Archive. Rollback has no risk of state corruption.

---

## 9. Open Questions for Loyal Opposition Review

1. Derived-test discovery scope. Section 1.3 covers `tests/` plus `groundtruth-kb/tests/`. Are there other test directories in the project that should be in scope (e.g., `applications/Agent_Red/tests/` if Phase 7 isolation lands)?

2. Function-level docstring discovery. Section 1.3 explicitly excludes function-level docstrings (only module-level). Codex preference?

3. Pytest invocation flags. Section 1.4 uses `--tb=short -q --no-header`. Owner/Codex preference for additional flags (e.g., `-x` to stop on first failure)?

4. Waiver schema strictness. Section 1.5 tolerates YAML-ish and plain-text bullet formats. Should the parser be stricter (require canonical YAML) to prevent ambiguity?

5. Self-verification dogfood timing. Section 3.2 runs the runner against this very bridge as part of acceptance. Acceptable, or should the dogfood be deferred to a separate post-impl bridge to avoid circular dependency at first VERIFIED?

---

## 10. Aligns With

- DCL-VERIFIED-BRIDGE-HISTORY-001 (the spec being satisfied; assertions A1+A2 directly tested).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (the gate this runner enforces).
- Umbrella `gtkb-platform-spec-coverage-architecture-2026-04-29-005` approved at -006 (sub-bridge sequencing item 3).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (deterministic CLI runner; reduces AI mediation in verification).
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (runner output consumable by both Claude and Codex review skills).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
