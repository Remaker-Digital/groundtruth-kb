REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.E.1: Atomic Code Cluster Move (REVISED-7)

**Document:** `gtkb-isolation-018-slice-e1-atomic-code-move`
**Status:** `REVISED`
**Date:** 2026-05-10
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (file relocation; no behavior change; preserves git history via `git mv`)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-014.md`. One finding addressed: F1 — Phase 3 containment check uses `str(Path(p)).startswith('applications/Agent_Red/')`, which fails on Windows because `Path()` normalizes separators to backslashes; valid in-scope paths get rejected as out-of-scope. Fixed by introducing a cross-platform `validate_agent_red_destination(path_text, repo_root)` helper using `Path.resolve()` + `Path.relative_to()`, plus positive and negative tests for parent traversal, absolute paths, and valid in-scope paths under both Windows and POSIX styles.
**Predecessors:** `-001` NEW; `-002` NO-GO (4 findings); `-003` REVISED-1; `-004` NO-GO (prefix-guard); `-005` REVISED-2 (manifest-derived write-set); `-006` NO-GO (step ordering); `-007` REVISED-3 (Step 0 → 0.5 → 1); `-008` NO-GO (source-only test paths); `-009` REVISED-4 (symmetric source+destination test paths); `-010` NO-GO (rollback leaves destinations untracked); `-011` REVISED-5 (4-phase rollback + completeness test); `-012` NO-GO (containment check scoped to dir branch only); `-013` REVISED-6 (hoisted containment + AssertionError); `-014` NO-GO (Windows path-normalization breaks lexical check).

---

## Codex Findings Addressed (from -014)

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Phase 3 lexical containment check fails on Windows host: `Path("applications/Agent_Red/foo")` stringifies to `applications\Agent_Red\foo`, which the forward-slash `startswith('applications/Agent_Red/')` predicate rejects | P1 | **Fixed.** Replaced the lexical string check with a cross-platform helper `validate_agent_red_destination(path_text, repo_root)` that uses `Path.resolve() + Path.relative_to()` to perform real filesystem containment. The helper accepts forward-slash repository-relative input, rejects absolute paths and parent traversal at the string layer (before any filesystem operation), and resolves+containment-checks against the resolved `applications/Agent_Red/` root. T-write-set-1 expanded with positive tests for valid in-scope paths (Windows and POSIX styles) AND negative tests for parent traversal and absolute paths. See § F1 Fix below. |

## Carry-Forward Statement

All sections of `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-013.md` (REVISED-6) carry forward UNCHANGED EXCEPT the F1 Fix below (containment helper signature + Phase 3 invocation + T-write-set-1 mutation-test expansion). REVISED-6's prior fixes carry forward intact.

Specifically carried forward unchanged:

- Goal (clusters, file counts, ~1,423 total moves)
- Specification Links (full set; re-cited below for preflight matching)
- Prior Deliberations (with one addition: Codex NO-GO at -014 itself)
- Owner Decisions / Input (no new owner decisions)
- Live State Probed (2026-05-10 data; +17 drift finding preserved)
- Implementation Plan content (Steps 0, 0.5, 1, 1.5, 2, 3, 4, 5, 5b, 6, 6.5, 7) — only the containment-helper definition and Phase 3 invocation change per F1 Fix below
- Tests Derived From Linked Specifications (T-write-set-1 expanded with 4 additional mutation tests; T-step-order-1 unchanged; T-import-2 unchanged; 15 from -001 unchanged) — total 18 tests; T-write-set-1 carries 10 mutation-coverage criteria (M1-M3 from -005/-009, M4 from -011, M5-M6 from -013, M7-M10 new in this revision)
- Verification Commands (carry forward; reference `python -m pytest`, `pytest`, `ruff`, `test_*.py` patterns required by clause detector)
- Risks and Rollback structure (R1-R7); rollback algorithm Phase 3 invocation corrected per F1 Fix
- Acceptance Criteria
- Out of Scope

---

## Specification Links

Carried forward from `-013`. Re-cited here for preflight matching:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This REVISED-7 is filed as `-015` and a `REVISED: bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md` line is inserted at the top of the thread's bridge/INDEX.md entry per the protocol; no prior versions are deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping; this proposal carries 18 spec-derived tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 — 5 binding rules.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 — machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE).
- `DELIB-S334-OQ-E3-OPTION-A` — owner decision selecting Option A.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle.
- `GOV-STANDING-BACKLOG-001` — work_list.md as governed work authority.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` — canonical umbrella plan.
- `bridge/gtkb-isolation-018-slice-e-code-cluster-003.md` — 18.E scoping proposal.
- `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-009.md` — E.3 disposition report.
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-011.md` — 18.C VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-d-non-functional-content-006.md` — 18.D VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — 18.B VERIFIED pattern precedent.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-002.md` — Codex NO-GO (REVISED-1 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-004.md` — Codex NO-GO (REVISED-2 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-006.md` — Codex NO-GO (REVISED-3 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-008.md` — Codex NO-GO (REVISED-4 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-010.md` — Codex NO-GO (REVISED-5 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-012.md` — Codex NO-GO (REVISED-6 trigger).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-014.md` — Codex NO-GO triggering this REVISED-7.
- `applications/Agent_Red/.gtkb-app-isolation.json` — current isolation registry.
- `.tmp/e3-disposition/manifest-v2.json` — E.3 disposition manifest (S334).
- `.tmp/e1-baseline/drift-probe-report-2026-05-10.json` — pre-implementation drift probe.
- `.claude/rules/project-root-boundary.md` — 5 binding rules.
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — pre-proposal deliberation-search obligation.

## Prior Deliberations

Carried forward from `-013`. Additional record from this revision:

- Codex NO-GO at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-014.md` (2026-05-10) — surfaced the Windows path-normalization defect addressed in this REVISED-7. Codex's review included an explicit Windows-host reproduction showing `applications/Agent_Red/src` stringifies to `applications\Agent_Red\src` and fails the forward-slash startswith check.

## Owner Decisions / Input

Carried forward from `-013`. No new owner decisions required. The F1 fix is a Prime Builder revision task per Codex `-014` line 122.

---

## F1 Fix — Cross-platform containment helper

### The defect

`-013`'s Phase 3 hoisted containment check used a lexical predicate:

```python
for p in destinations_to_clean:
    path = Path(p)
    if not str(path).startswith('applications/Agent_Red/'):
        raise AssertionError(f'Refusing to remove out-of-scope destination path: {path}')
    ...
```

On Windows, `str(Path("applications/Agent_Red/src"))` returns `applications\Agent_Red\src`. The forward-slash `startswith('applications/Agent_Red/')` predicate rejects every legitimate in-scope path on the project's Windows/PowerShell host. The rollback helper is the safety mechanism for ~1,423 file moves; the predicate's false-negative would abort all cleanup, leaving destination-side artifacts behind on partial Step 3 failure.

Codex's review-time probe (E:\GT-KB):

```text
input=applications/Agent_Red/src
str=applications\Agent_Red\src
startswith_forward=False
input=applications/Agent_Red/tests/a.txt
str=applications\Agent_Red\tests\a.txt
startswith_forward=False
input=applications/Agent_Red/config/stripe_product_ids.json
str=applications\Agent_Red\config\stripe_product_ids.json
startswith_forward=False
```

### Helper definition (NEW)

Add a small helper to `scripts/rollback_e1_write_set.py` (the same file authored at -011 for the 4-phase rollback):

```python
from pathlib import Path, PurePosixPath, PureWindowsPath


def validate_agent_red_destination(path_text: str, repo_root: Path) -> Path:
    """Validate that path_text is a repository-relative destination under
    applications/Agent_Red/. Returns the resolved Path on success.

    Cross-platform: accepts forward-slash repository-relative input regardless
    of host OS. Uses Path.resolve() + Path.relative_to() for real filesystem
    containment (not lexical string prefix), so Windows backslash normalization
    does not cause false negatives.

    Raises AssertionError when path_text is:
    - absolute under either POSIX or Windows path rules
    - contains parent-traversal segments ('..')
    - resolves outside the repo_root/applications/Agent_Red/ subtree
    """
    # 1. Reject absolute paths under EITHER OS's rules (cross-platform-safe).
    if PurePosixPath(path_text).is_absolute() or PureWindowsPath(path_text).is_absolute():
        raise AssertionError(
            f'Refusing to remove absolute destination path: {path_text}'
        )

    # 2. Reject parent traversal (string-level; before any filesystem operation).
    normalized_parts = path_text.replace('\\', '/').split('/')
    if '..' in normalized_parts:
        raise AssertionError(
            f'Refusing to remove destination path with parent traversal: {path_text}'
        )

    # 3. Resolve relative to repo_root and check containment via relative_to().
    candidate = (repo_root / path_text).resolve(strict=False)
    allowed_root = (repo_root / 'applications' / 'Agent_Red').resolve(strict=False)
    try:
        candidate.relative_to(allowed_root)
    except ValueError:
        raise AssertionError(
            f'Refusing to remove out-of-scope destination path: {path_text}'
        )

    return candidate
```

Why this approach:

- `PurePosixPath(text).is_absolute()` returns True for paths starting with `/`; `PureWindowsPath(text).is_absolute()` returns True for paths with drive letters or starting with `\\`. Checking both catches absolute paths in either style regardless of host OS.
- The parent-traversal check at the string layer (step 2) means we never call `.resolve()` on a path containing `..` segments, avoiding symlink-amplified escapes during resolution.
- `Path.resolve()` normalizes separators correctly for the host OS, follows symlinks, and produces canonical forms. `Path.relative_to()` returns the relative path if `candidate` is under `allowed_root`, else raises `ValueError`. This is the canonical Python idiom for "is X under Y" filesystem containment.
- `strict=False` on `resolve()` does not require the path to exist; the destination may not be present on disk after rollback Phase 2 already removed it, but the containment check still works against the abstract resolved path.

### Phase 3 invocation (UPDATED to use helper)

```python
from pathlib import Path

repo_root = Path.cwd()  # rollback runs from GT-KB project root

for p in destinations_to_clean:
    # Containment validation FIRST — cross-platform; protects BOTH unlink and rmtree branches.
    resolved_path = validate_agent_red_destination(p, repo_root)
    # After validation succeeds, resolved_path is the canonical filesystem path.
    if resolved_path.is_symlink() or resolved_path.is_file():
        resolved_path.unlink(missing_ok=True)
    elif resolved_path.is_dir():
        shutil.rmtree(resolved_path, ignore_errors=True)
```

The branch logic is unchanged from `-013`. Only the validation predicate changes: from a fragile lexical string check to the cross-platform helper.

### T-write-set-1 expansion (positive + negative coverage)

Four additional mutation tests added:

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-write-set-1.M7** (NEW): valid in-scope FILE destination passes the check. Synthetic write-set entry `tests_migrating_destination_paths: ['applications/Agent_Red/tests/a.txt']`; `validate_agent_red_destination` returns the resolved Path without raising; mocked `Path.unlink` is invoked exactly once. The test runs the validation with the host's actual `Path` behavior (so on Windows it covers the backslash-normalization case). | F1 Fix correctness — positive coverage; in-scope FILE passes | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| **T-write-set-1.M8** (NEW): valid in-scope DIRECTORY destination passes the check. Synthetic entry `cluster_destinations_dir_recursive: ['applications/Agent_Red/src']`; `validate_agent_red_destination` returns the resolved Path; mocked `shutil.rmtree` is invoked exactly once. | F1 Fix correctness — positive coverage; in-scope DIRECTORY passes | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| **T-write-set-1.M9** (NEW): parent-traversal destination fails. Synthetic entry `tests_migrating_destination_paths: ['applications/Agent_Red/../outside.txt']`; `validate_agent_red_destination` raises `AssertionError` containing 'parent traversal'; no `unlink`/`rmtree` call made. | F1 Fix correctness — parent-traversal rejected | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| **T-write-set-1.M10** (NEW): absolute destination fails. Two sub-tests: (a) POSIX-style `['/etc/passwd']` raises 'absolute destination path'; (b) Windows-style `['C:\\Windows\\foo']` raises 'absolute destination path'. Both must raise regardless of host OS, because `PurePosixPath.is_absolute()` and `PureWindowsPath.is_absolute()` are both checked. | F1 Fix correctness — absolute paths rejected under either OS | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |

Plus the existing M5/M6 from `-013` are kept but reframed to use the new helper:

| Test | Verifies | Linked spec |
|------|----------|-------------|
| **T-write-set-1.M5** (carried forward, helper-updated): outside FILE destination (e.g., `tests_migrating_destination_paths: ['some-platform-file.txt']`) — `validate_agent_red_destination` raises `AssertionError` containing 'out-of-scope' BEFORE unlink runs (mocked unlink never called). | F1 Fix correctness — outside FILE rejected | Same |
| **T-write-set-1.M6** (carried forward, helper-updated): outside DIRECTORY destination (e.g., `cluster_destinations_dir_recursive: ['some-platform-dir/']`) — `validate_agent_red_destination` raises `AssertionError` containing 'out-of-scope' BEFORE rmtree runs (mocked rmtree never called). | F1 Fix correctness — outside DIRECTORY rejected | Same |

T-step-order-1 from `-007` is unchanged. T-import-2 from `-003` is unchanged. The other 15 tests from `-001` carry forward unchanged. Total: 18 tests; T-write-set-1 carries 10 mutation-coverage criteria (M1-M4 from earlier revisions, M5-M10 covering helper correctness).

All T-write-set-1 mutation tests reside in `tests/governance/test_isolation_018_e1_rollback_completeness.py`, exercised via `python -m pytest tests/governance/test_isolation_018_e1_rollback_completeness.py -q`.

### Acceptance criteria addition

- **Criterion 22 (REPLACES `-013`'s criterion 22):** The same `.tmp/e1-drift/write-set.json` is consumed by the precondition guard, the 4-phase rollback at `scripts/rollback_e1_write_set.py`, AND the Step 3 per-file `git mv` loop. T-write-set-1 verifies non-drift, rollback completeness (M4), and cross-platform containment correctness (M5-M10): outside FILE/DIR rejected before deletion; in-scope FILE/DIR passes; parent-traversal rejected; absolute paths rejected under either OS's rules. Phase 3 uses `validate_agent_red_destination(path_text, repo_root)` which performs real filesystem containment via `Path.resolve() + Path.relative_to()`.

The other 23 acceptance criteria from `-013` carry forward unchanged.

---

## Out of Scope

Carried forward from `-013` unchanged.

## Pre-Filing Applicability Preflight

Will rerun after this REVISED-7 is written and INDEX is updated. Expected: still passes (only content changes are F1 fix; same spec citations, same content patterns; clause-detector regex satisfied via the spec-to-test verification language preserved from prior revisions).

### REVISED-7 packet hash (post-write capture)

After this REVISED-7 file was written and INDEX updated:

```text
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-015.md`
- packet_hash: `sha256:da8678c5bcad56ea9810acf00578aba8f370cd0e93c16278e29c08fa9c28fea5`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- Clause preflight: must_apply: 4, may_apply: 1; Evidence gaps: 0; Blocking gaps: 0; exit: 0
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
