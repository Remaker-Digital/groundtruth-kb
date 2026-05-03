NEW

# Implementation Proposal — GTKB-ISOLATION-017 Slice 7

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S329)
Subject: 4 example projects under `groundtruth-kb/examples/` per Phase 9 §7. Each example ships its own `README.md` + `groundtruth.toml` + `.gitignore` and a dashboard-render walkthrough that exercises overlay + service paths together (per Phase 9 Exit Criterion 4 line 349-350). CI verifies each example passes `gt project doctor` invariants on every commit. **Owner Decision 6 resolved: No 5th Agent Red example** (per S329 owner answer; the 4 generic examples carry the v0.7.0-rc1 contract).

## Context

GTKB-ISOLATION-017 Slices 1, 2, 2.5, 3, 4, 5, 6 are VERIFIED. Per the scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` lines 173-184 + GO at `-004`, Slice 7 is the examples slice. Per sequencing constraint at scoping `-003.md` line 208, Slice 7 unblocks after Slice 5 VERIFIED — which closed at `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-006.md` (commit `dc8e58f8` on develop). Slice 6 (docs) is also VERIFIED (commit `9efd29bf`).

Per work_list TOP release-path directive, Slice 7 advances the v0.7.0-rc1 release path. Slice 7 owns Phase 9 Decision 6 per the Decision Map at scoping `-003` line 50.

**Owner Decision 6 (resolved):** No 5th Agent Red example. The 4 generic examples (clean-adopter-minimal, adopter-with-transport-tests, adopter-with-release-gate, existing-adopter-migration) are sufficient for v0.7.0-rc1. Recorded as S329 owner answer to AskUserQuestion at proposal-draft time. To be archived as a Deliberation Archive entry per `.claude/rules/deliberation-protocol.md` at session-wrap time.

## Specification Links

The implementation is constrained by, and shall not depart from, the following specifications, ADRs, DCLs, governance rules, and proposal carry-forwards:

1. **Phase 9 plan §7 — Examples Using Application-Only Project Roots** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 284-302. This enumerates the 4 minimum examples + per-example file set + CI verification + production-path/secrets prohibition.
2. **Phase 9 plan §"Exit Criteria" §4** at the same plan lines 341-352, specifically lines 349-350 (each example must contain a dashboard rendering step that exercises overlay + service paths together).
3. **Phase 9 plan §"Open Decisions"** at the same plan lines 369-396, specifically Decision 6 (Agent Red as Phase 9 example): resolved No per S329 owner directive.
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — adopters live at `<gt-kb-root>/applications/<name>/`. Examples are scaffold-shape templates; they do not need to be placed under `applications/` at rest because they are template fixtures that an operator instantiates.
5. **`.claude/rules/project-root-boundary.md`** — examples live within `E:\GT-KB\groundtruth-kb/examples/`; root-boundary contract satisfied.
6. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol; this proposal complies with the spec-linkage gate.
7. **`.claude/rules/codex-review-gate.md`** — codex review gate.
8. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 173-184 (Slice 7 acceptance criteria) + `-004` GO.
9. **GOV-09**, **GOV-19** (outside-in: examples exercise the user-facing CLI), **GOV-20** (IPR + CVR — drafts to be embedded in post-impl REPORT).
10. **Prior Slice GOs (carry-forward; the examples must work against the actual implemented surfaces):**
    - Slice 1 `-012` VERIFIED — 9 isolation doctor checks.
    - Slice 2 `-008` VERIFIED — managed-artifact registry.
    - Slice 3 `-014` VERIFIED — `gt project init` adopter-subject defaults.
    - Slice 4 `-012` VERIFIED — `gt project upgrade --accept-migration` flow.
    - Slice 5 `-006` VERIFIED — clean-adopter test suite (the `existing-adopter-migration` example reuses Slice 5's `pre_isolation_minimal` fixture pattern).
    - Slice 6 `-004` VERIFIED — isolation chapter (the examples cite the chapter for adopter-walkthrough context).
11. **Existing reference surfaces cross-linked (NOT modified):**
    - `scripts/release_candidate_gate.py` — workspace-level release gate; the `adopter-with-release-gate` example wires a stripped-down adopter-side equivalent.
    - `groundtruth-kb/examples/task-tracker/` — pre-existing elaborate example; Slice 7 examples follow its layout convention but are minimized.
    - `groundtruth-kb/tests/fixtures/adopter/pre_isolation_minimal/` — Slice 5's pre-isolation fixture; the `existing-adopter-migration` example reuses this tree shape.
    - `groundtruth-kb/docs/architecture/isolation.md` — Slice 6's chapter; the example READMEs link to it for context.
12. **Prior Deliberations:**
    - S329 owner directive resolving Decision 6 (Agent Red as 5th example: No) — to be archived.
    - `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 — Slice 4 owner decisions; the `existing-adopter-migration` example's WALKTHROUGH cites the chosen mandatory-at-upgrade + one-shot-migration + out-of-band-recipe modes.
    - `python -m groundtruth_kb.cli deliberations search --query "Phase 9 examples adopter"` — to be re-run by Codex review per `.claude/rules/deliberation-protocol.md`.

## Scope

### In-scope

Files created (new):

**4 example trees under `groundtruth-kb/examples/`:**

#### `examples/clean-adopter-minimal/`

Smallest possible adopter passing doctor checks. Per Phase 9 §7 line 288-289.

- `README.md` — quickstart + dashboard-rendering walkthrough + cross-link to `docs/architecture/isolation.md`.
- `groundtruth.toml` — `[service].endpoint = "configure-me://placeholder/v1"`, `[project].profile = "local-only"`, minimal manifest.
- `.gitignore` — adopter-side gitignore (mirrors scaffold output).

Estimated: 3 files.

#### `examples/adopter-with-transport-tests/`

Adopter with a transport contract test suite scaled down from Agent Red's Phase 3/4/5 pattern. Per Phase 9 §7 line 290-292.

- `README.md` — explanation of the transport-test pattern + dashboard-rendering walkthrough.
- `groundtruth.toml` — `[service].endpoint` + `[project].profile = "dual-agent"`.
- `.gitignore` — adopter-side.
- `src/transport/__init__.py` — minimal transport module (request/response shapes).
- `tests/test_transport_contract.py` — 2-3 contract tests with placeholder assertions (the example demonstrates the structure, not the production behavior).
- `pyproject.toml` — minimal pyproject for the example (so `pytest` can collect).

Estimated: 6 files.

#### `examples/adopter-with-release-gate/`

Adopter wiring a release-gate to its own CI. Per Phase 9 §7 line 293-294.

- `README.md` — release-gate walkthrough + cross-link to `scripts/release_candidate_gate.py`.
- `groundtruth.toml` — `[service].endpoint` + `[project].profile = "dual-agent"`.
- `.gitignore` — adopter-side.
- `.github/workflows/release-gate.yml` — minimal CI workflow that invokes a stripped-down release-gate check (placeholder; the example demonstrates the wiring, not the production gate).
- `scripts/release_gate_check.sh` — minimal shell stub showing the gate-invocation pattern.

Estimated: 5 files.

#### `examples/existing-adopter-migration/`

Pre-isolation fixture tree + documented upgrade walkthrough. Per Phase 9 §7 line 295-297.

- `README.md` — context block describing the pre-isolation shape.
- `WALKTHROUGH.md` — step-by-step upgrade walkthrough ending in a clean post-migration state. Cites Slice 4's `--accept-migration` flow + `DELIB-S328-...-DECISIONS-1-3-7-OWNER-DIRECTIVE`.
- `groundtruth.toml` — pre-isolation manifest (raw-DB endpoint to trigger Slice 1 check #2; `scaffold_version = "0.6.0"` to trigger upgrade-required path).
- `.gitignore` — adopter-side.
- `.claude/hooks/.workstream-focus-state.json` — `current_subject=platform` to trigger Slice 1 check #3.
- `.claude/hooks/workstream-focus.py` — legacy hook to trigger Slice 1 check #6.
- `memory/release-readiness.md` — wrong header to trigger Slice 1 check #8.

Estimated: 7 files.

**Verification harness:**

- `groundtruth-kb/tests/test_examples_pass_doctor.py` — pytest suite that walks `examples/`, instantiates each example into a sandbox, and asserts `gt project doctor` invariants. ~80 LOC. Slice 5's clean-adopter conftest pattern is reused (in-root sandbox vs tmp_path decision per example).

**Documents (per GOV-20 advisory pilot):**

- `IPR-SLICE7-EXAMPLES-001` — pre-implementation review citing this proposal, ADR-ISOLATION-APPLICATION-PLACEMENT-001, Phase 9 §7 obligations, and the resolved Decision 6. To be embedded in post-impl REPORT.
- `CVR-SLICE7-EXAMPLES-001` — post-implementation proof (filed at post-impl + Codex VERIFIED time).

**Total estimated:** 21 example files + 1 verification test file + ~80 LOC verification logic.

### Out-of-scope (explicitly deferred)

- **`examples/agent-red-minimized-fixture/`** (5th example). Owner Decision 6 resolved to No; the 4 generic examples carry the v0.7.0-rc1 contract.
- **Real production behavior in any example.** Per Phase 9 §7 line 298-302, examples must not reference Agent Red production paths, Azure workspace names, or live secrets. The transport-tests example contains placeholder request/response shapes; the release-gate example contains a stub gate; the migration example contains a synthetic pre-isolation tree.
- **Modifications to existing reference surfaces** (`scripts/release_candidate_gate.py`, `groundtruth-kb/examples/task-tracker/`, Slice 5's fixtures). The new examples cross-link them; they do not modify them.
- **Slice 8 release-ops** (release notes, version-tagging, post-program acceptance gate) — separate slice scope.
- **Multi-platform CI matrix expansion.** The verification test runs on the existing CI lane (Ubuntu base/no-search per `groundtruth-kb/.github/workflows/ci.yml`); platform-sensitive variants are out of scope.

## Implementation Plan

1. **Create the 4 example tree directories** under `groundtruth-kb/examples/`.

2. **Author each example's content** per the scope tables above. Each `README.md` includes:
    - 1-paragraph overview.
    - "Run the example" section with concrete CLI commands.
    - "Dashboard rendering" section showing how to invoke `gt dashboard` against the example's adopter root + what the rendered dashboard surfaces (service health from `[service].endpoint` + overlay state from `.groundtruth-chroma/`). Per Phase 9 Exit Criterion 4 line 349-350.
    - "See also" section linking to `docs/architecture/isolation.md` + `docs/reference/cli.md`.

3. **Author the verification harness** at `groundtruth-kb/tests/test_examples_pass_doctor.py`. The test:
    - Iterates over `examples/<example_name>/` for each of the 4 examples.
    - For `clean-adopter-minimal` and `adopter-with-transport-tests` and `adopter-with-release-gate`: copies the example into a `tmp_path` sandbox, runs `run_isolation_checks(adopter, "<profile>", product_root=tmp_path)`, asserts no `fail` statuses (warnings + info acceptable).
    - For `existing-adopter-migration`: copies the example into a `tmp_path` sandbox, runs the isolation checks, asserts the EXPECTED failures fire (the example is a pre-isolation tree by design — the test verifies it's correctly pre-isolation-shaped).
    - Total ~80 LOC.

4. **Cross-link from `docs/architecture/isolation.md`** §"See also" — add a single line pointing to `examples/`. ~1 LOC change.

5. **Author IPR + CVR documents** per GOV-20. Embedded in post-impl REPORT.

## Test Plan (spec-to-content mapping)

Slice 7 ships example trees + a verification test. Verification is twofold: (a) the verification test asserts each example passes/fails the right doctor invariants, and (b) content-presence checks confirm each Phase 9 §7 minimum-section requirement is met.

| Spec source | Test/content assertion |
|---|---|
| Phase 9 §7 line 288-289 (clean-adopter-minimal) | `examples/clean-adopter-minimal/` exists; verification test asserts `run_isolation_checks` returns 0 `fail` statuses |
| Phase 9 §7 line 290-292 (adopter-with-transport-tests) | `examples/adopter-with-transport-tests/` exists with `src/transport/` + `tests/test_transport_contract.py`; verification test asserts doctor passes; `pytest tests/` collects without error |
| Phase 9 §7 line 293-294 (adopter-with-release-gate) | `examples/adopter-with-release-gate/` exists with `.github/workflows/release-gate.yml`; verification test asserts doctor passes; cross-link to `scripts/release_candidate_gate.py` resolves |
| Phase 9 §7 line 295-297 (existing-adopter-migration) | `examples/existing-adopter-migration/` exists with WALKTHROUGH.md; verification test asserts the EXPECTED failures fire (pre-isolation-shape); WALKTHROUGH.md cites `--accept-migration` + DELIB |
| Phase 9 §7 line 298 (each example has README + groundtruth.toml + .gitignore) | grep confirms all 3 files exist in each of the 4 example dirs |
| Phase 9 §7 line 299-300 (CI verifies each example) | `tests/test_examples_pass_doctor.py` is collected by the existing CI lane via `pytest -v --tb=short` (no workflow changes needed; auto-discovery covers `tests/`) |
| Phase 9 §7 line 301-302 (no production paths/secrets) | grep `Agent Red\|agent-red\|azure\|prod\|secret\|api_key\|password` returns 0 hits in any example file (case-insensitive; the migration example may reference "Agent Red" only in passing for context, not as a production reference) |
| Phase 9 Exit Criterion 4 line 349-350 (dashboard rendering step) | each example's `README.md` contains a `## Dashboard rendering` (or equivalent) section that names the overlay (`.groundtruth-chroma/`) AND the service endpoint together |

Verification commands:

```bash
# From E:\GT-KB\groundtruth-kb
python -m pytest tests/test_examples_pass_doctor.py -v --tb=short

# Cross-test interference check
python -m pytest tests/ -q --tb=short
```

Plus a content-check script at `scripts/_verify_slice7_examples.py` mirroring the Slice 6 pattern: confirms required files, prohibits production-path tokens, validates cross-link integrity.

## Acceptance Criteria

This NEW is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the resolved Decision 6.
2. The 4 example trees have the file lists in §"Scope" §"In-scope" with no Agent Red 5th example (per Decision 6 = No).
3. Each example's `README.md` contains a dashboard-rendering section per Phase 9 Exit Criterion 4 line 349-350.
4. `existing-adopter-migration` has a WALKTHROUGH.md citing `--accept-migration` + the Slice 4 DELIB.
5. Verification test at `tests/test_examples_pass_doctor.py` exists and exercises the documented assertion shapes.
6. No example file references production paths, Azure workspace names, or live secrets per Phase 9 §7 line 301-302.
7. Each test exercises an outside-in surface (GOV-19; `run_isolation_checks` + `run_doctor` + filesystem walk) — not internal helpers.
8. Each test assertion is meaningful (GOV-18; named expected status values, not rubber-stamp).
9. Estimated envelope ~21 example files + 1 test file + ~80 LOC verification logic + 1 LOC cross-link to docs/architecture/isolation.md.

## Risk / Rollback

**Risk 1 — Production-path/secret leakage (medium).** The migration example mirrors Agent Red's pre-isolation shape; accidental references to production paths or secrets would violate Phase 9 §7 line 301-302. Mitigation: `_verify_slice7_examples.py` includes a banned-token grep covering `Agent Red`, `agent-red` (path-form), `azure`, `prod`, `secret`, `api_key`, `password` patterns; manual review during Codex VERIFIED.

**Risk 2 — Cross-test interference with example pytests (medium).** The `adopter-with-transport-tests` example contains a `tests/` directory. If the example's tests are collected by the workspace pytest lane, they could fail spuriously (the example's tests are placeholders, not production tests). Mitigation: the example's `pyproject.toml` declares its own pytest config; the workspace pytest lane (rooted at `groundtruth-kb/`) does not descend into `examples/<name>/tests/` because `examples/` is outside `tests/`. Verified by adding the example pytest config; the verification test at `tests/test_examples_pass_doctor.py` runs the example's tests via subprocess from the example dir, isolating them.

**Risk 3 — Dashboard rendering instructions stale-on-arrival (low).** The dashboard-rendering section in each README walks through `gt dashboard` invocation. If `gt dashboard`'s CLI surface changes, the README sections drift. Mitigation: cross-links rather than duplication where possible; the README content is anchored to the public CLI form documented in `docs/reference/cli.md`.

**Risk 4 — Migration example fixture overlap with Slice 5 (low).** The `existing-adopter-migration` example uses the same pre-isolation shape as Slice 5's `pre_isolation_minimal` fixture. If Slice 5's fixture changes, the example might drift. Mitigation: the example is a SHAPE-IDENTICAL but CONTENT-INDEPENDENT tree (no symlink or shared state); WALKTHROUGH.md is example-specific.

**Rollback path:** Slice 7 ships only example trees + a verification test + 1 docs cross-link. No source code changes. Reversible via `git revert` of the implementation commit.

## Decision Needed From Owner

**None at NEW time.** Decision 6 was resolved at S329 proposal-draft time (No 5th Agent Red example) per the AskUserQuestion answer cited in §"Context".

## Open Items

- The `python -m groundtruth_kb.cli deliberations search --query "Phase 9 examples adopter"` probe will run as part of Codex review's Prior Deliberations check.
- Decision 6's deliberation archive insertion is owner-gated per `GOV-ARTIFACT-APPROVAL-001`; for now, the answer is cited inline + will be archived at session-wrap time.
- The `task-tracker` example (pre-existing, not Slice 7 scope) shows a more elaborate adopter shape than the 4 Slice 7 examples; if a future slice consolidates them, that's a separate work_list row.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
