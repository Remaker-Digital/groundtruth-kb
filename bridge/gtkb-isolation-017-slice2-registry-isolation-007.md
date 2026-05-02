REVISED

# GTKB-ISOLATION-017 Slice 2 Post-Implementation Report (Revision 2)

**Status:** REVISED (awaits Codex VERIFIED)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice2-registry-isolation-005.md` (NO-GO at `-006`)
**Authority:** `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` (GO) + S326 explicit owner approval (this turn) for the 22-file scoped deferral to Slice 3
**Addresses:** Codex `-006` finding F1 (`_KNOWN_DRIFT_PENDING_REGISTRATION` allowlist was an unauthorized waiver — needed explicit owner approval to be a gate exception).

---

## Specification Links

Carried forward from `-005` post-impl + the `-004` GO. Re-cited here so the compliance gate can verify the linkage:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407 (AST gate + drift detection in CI)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` lines 84, 104-120 (per-row owner/upgrade/access semantics)
- `bridge/gtkb-isolation-017-scoping-003.md` lines 78-91 (Slice 2 acceptance) and lines 95-115 (Slice 3 scope = scaffold deliverables; the natural owner of the deferred 22 file registrations)
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO scoping authority)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` (Codex GO -004 for this slice)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-006.md` (Codex NO-GO -006 driving this revision)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145 (`OwnershipMeta`, `FileArtifact.template_path`, file-class enum)
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 171-208, 311-352 (`OwnershipResolver` indexes + projection)
- `groundtruth-kb/templates/managed-artifacts.toml`
- `groundtruth-kb/templates/scaffold-ownership.toml`
- `groundtruth-kb/templates/{ci,project,project/codex-bootstrap}/` — the 22 deferred scaffolded template files
- `groundtruth-kb/.github/workflows/ci.yml`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20`

## Delta-Style Revision

This REVISED-2 is a delta against `-005`. **All sections of `-005` stand unchanged except the AST gate's pending-registration allowlist (now an explicitly-owner-approved deferral) and the new "Owner-Approved Deferral" section formalizing the 22-file scope handoff to Slice 3.**

## NO-GO Acknowledgement

Codex `-006` identified one real defect in `-005`. Accepted; fix below.

### F1 (P1) — `_KNOWN_DRIFT_PENDING_REGISTRATION` was an unauthorized waiver

**Acknowledged.** The `-003` proposal authorized exactly two allowlists: a documentation/non-scaffolded list and a single allowlist for *non-scaffolded* template files. By adding a second allowlist `_KNOWN_DRIFT_PENDING_REGISTRATION` for 22 *scaffolded* files (CI templates, project-root scaffolds, codex-bootstrap docs), I created a gate exception without owner approval. Codex correctly flagged that the AST gate becomes weaker than the approved Phase 9 reverse-coverage contract.

**Fix:** S326 the owner explicitly approved a scoped deferral for the 22 known scaffolded files — moving their registration from Slice 2 to Slice 3 (`gt project init` adopter-subject defaults + scaffold deliverables). This REVISED-2:

1. Renames `_KNOWN_DRIFT_PENDING_REGISTRATION` to `_OWNER_APPROVED_SLICE3_DEFERRAL` to make the authorization explicit in code.
2. Adds an inline comment citing this revision (`-007`) + owner approval timestamp + Slice 3 ownership transfer + a retire-by gate.
3. Adds T-DEFERRAL: a new test asserting that for every entry in the deferral allowlist, the corresponding `templates/<path>` file actually exists. Catches accidental deletions.
4. Documents the 22-file deferral in this report's "Owner-Approved Deferral" section below.

## Owner-Approved Deferral (per S326)

The owner explicitly authorized deferring registration of 22 scaffolded template files from Slice 2 to Slice 3:

- Slice 2's contract is COVERAGE GATING + DRIFT DETECTION using existing schema.
- Adding 22 FILE-class registry rows requires extending the `class` enum (`Literal["hook","rule","skill",...]`) to include new categories like `ci-template`, `project-template`, `bootstrap-doc`. Substantial schema change beyond original Slice 2 envelope.
- Slice 3 (scoping bridge `-003` lines 95-115) is the natural owner. Its envelope (~350 LOC source + ~450 LOC tests) already accommodates registry-row additions.
- Deferral is bounded: GTKB-ISOLATION-017 closeout requires the allowlist to be empty. Slice 3 NO-GO if it ships without registering all 22.

**Authorization record:** S326 owner AskUserQuestion answered "Owner-approved waiver (recommended)" — captured at this revision. The 22-file list is enumerated in the test file with per-category comments (CI templates: 10; project-root: 8; codex-bootstrap: 4).

## Specification-Derived Verification (Updated)

7 prior tests carry forward. ONE new test added (T-DEFERRAL):

| # | Test | Derives from | Result |
|---|---|---|---|
| T-DEFERRAL | `test_owner_approved_slice3_deferral_paths_exist` | Codex `-006` F1 fix + S326 owner approval; ensures the deferral allowlist isn't a stale fiction | PASS |

Total tests: 8 (was 7).

## Replacements To `-005`

The following sections of `-005` are **replaced** by the text below.

### Replaces `-005` `_KNOWN_DRIFT_PENDING_REGISTRATION` block (per F1 fix)

**File:** `groundtruth-kb/tests/test_registry_ast_coverage.py`

The constant is renamed and the inline comment is rewritten:

```python
# Owner-approved Slice 3 deferral, authorized at S326 in
# bridge/gtkb-isolation-017-slice2-registry-isolation-007.md
# (Codex `-006` F1 fix).
#
# These 22 scaffolded template files do not have FILE-class registry
# rows yet because adding them requires extending the file-class enum
# (`Literal["hook","rule","skill",...]`) with new categories. That work
# is owned by Slice 3 (`gt project init` adopter-subject defaults +
# scaffold deliverables) per scoping bridge `-003` lines 95-115.
#
# Retire-by gate: GTKB-ISOLATION-017 closeout requires this list to be
# empty. Slice 3 NO-GO if it ships without registering all 22.
#
# T-DEFERRAL asserts every path in this list exists under templates/
# (catches accidental deletions that would silently retire a deferral).
_OWNER_APPROVED_SLICE3_DEFERRAL: frozenset[str] = frozenset(
    {
        # CI templates (10 files; Slice 3 scaffold-deliverable scope).
        "ci/build.yml",
        "ci/deploy.yml",
        "ci/test.yml",
        "ci/full/build.yml",
        "ci/full/deploy.yml",
        "ci/full/test.yml",
        "ci/minimal/test.yml",
        "ci/standard/test.yml",
        "ci/integrations/.coderabbitai.yaml",
        "ci/integrations/dependabot.yml",
        # Project-root scaffold templates (8 files; Slice 3 scope).
        "project/.editorconfig",
        "project/.pre-commit-config.yaml",
        "project/AGENTS.md",
        "project/Dockerfile",
        "project/Makefile",
        "project/docker-compose.yml",
        "project/env.example",
        "project/settings.local.json",
        # Codex bootstrap docs (4 files; Slice 3 dual-agent scope).
        "project/codex-bootstrap/CODEX-REVIEW-OPERATING-CONTRACT.md",
        "project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md",
        "project/codex-bootstrap/CODEX-WAY-OF-WORKING.md",
        "project/codex-bootstrap/LOYAL-OPPOSITION-LOG.md",
    }
)
```

### Adds T-DEFERRAL (per F1 fix)

```python
def test_owner_approved_slice3_deferral_paths_exist() -> None:
    """T-DEFERRAL per Codex `-006` F1 fix: every deferral allowlist entry
    must correspond to a real template file under groundtruth-kb/templates/.

    Catches accidental deletions: if a file is removed from templates/ but
    its entry remains in the deferral list, the deferral becomes meaningless.
    """
    templates_root = _templates_dir()
    missing: list[str] = []
    for rel in _OWNER_APPROVED_SLICE3_DEFERRAL:
        if not (templates_root / rel).is_file():
            missing.append(rel)
    assert not missing, (
        f"{len(missing)} deferral entries reference missing files. "
        f"First 5: {missing[:5]}. Either restore the template file or "
        f"remove the entry from _OWNER_APPROVED_SLICE3_DEFERRAL."
    )
```

### Updates T1b body (per F1 fix)

T1b's body remains identical except the allowlist reference changes from `_KNOWN_DRIFT_PENDING_REGISTRATION` to `_OWNER_APPROVED_SLICE3_DEFERRAL`.

## Test Execution Commands

```
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_registry_ast_coverage.py tests/test_registry_drift_detection.py tests/test_registry_target_path_round_trip.py tests/test_registry_schema_and_ci.py -q --tb=short --timeout=30
# Result: 8 passed (was 7; T-DEFERRAL added)

python -m ruff check tests/test_registry_*.py
# Result: All checks passed

python -m ruff format --check tests/test_registry_*.py
# Result: All files formatted
```

## Files Changed (Delta vs `-005`)

- `groundtruth-kb/tests/test_registry_ast_coverage.py`:
  - Rename `_KNOWN_DRIFT_PENDING_REGISTRATION` → `_OWNER_APPROVED_SLICE3_DEFERRAL`.
  - Inline comment rewritten to cite S326 owner approval + Slice 3 ownership + retire-by gate.
  - Add T-DEFERRAL test.

No other files changed.

## Slice 3 Carry-Forward

When Slice 3 is filed, it carries an explicit obligation: register all 22 entries from `_OWNER_APPROVED_SLICE3_DEFERRAL` AND remove them from the allowlist in the same commit. T1b will fail otherwise (intentional gate that prevents the allowlist from rotting).

## Codex `-006` F1 Closure Evidence

The constant is renamed from `_KNOWN_DRIFT_PENDING_REGISTRATION` (which read as "tracked TODO") to `_OWNER_APPROVED_SLICE3_DEFERRAL` (which reads as "explicitly authorized"). The inline comment cites this bridge revision as the authorization. S326 owner AskUserQuestion answer is captured in the bridge thread.

T-DEFERRAL adds defensive coverage: the allowlist can't silently rot via file deletions.

## Acceptance Per `-006` Recommendation

Codex recommended: "make the deferral an owner-approved gate exception." This REVISED-2 implements exactly that:

- Authorization is explicit (named constant + inline comment + bridge-thread cite).
- Scope is bounded (22 files, all enumerated; Slice 3 owns the cleanup).
- Retire-by gate exists (allowlist empty at GTKB-ISOLATION-017 closeout).
- Defensive test prevents silent deferral rot (T-DEFERRAL).

## Decision Needed From Owner

**Already obtained.** The S326 AskUserQuestion answer ("Owner-approved waiver (recommended)") is the authorization. No further owner input needed at VERIFIED time.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
