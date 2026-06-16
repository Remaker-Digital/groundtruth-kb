NEW

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: S375-gtkb-sweep-commit-pycache-prefix
author_model: Gemini 3.1 Pro High
author_model_version: gemini-3.1-pro-high
author_model_configuration: Antigravity desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4611-AND-WI-4612-DEFECT-FIXES
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4611

# Implementation Proposal - Staged Python compile verification should avoid source-tree pycache writes on Windows

## Claim

This proposal implements the fix for WI-4611 by updating `.claude/skills/gtkb-sweep-commit/SKILL.md` to use the `$env:PYTHONPYCACHEPREFIX=".tmp\pycache"` environment variable before invoking `py_compile`. This ensures that Python compilation checks during the sweep commit do not write `.pyc` files into source-tree `__pycache__` directories, preventing `WinError 5` locking and permission issues on Windows.

## Defect / Reproduction

During the 2026-06-16 sweep commit, staged Python byte-compilation failed with WinError 5 while `py_compile` attempted to replace a source-tree `__pycache__` file under `groundtruth-kb/src/groundtruth_kb/`. This occurs because `py_compile` ignores the `$env:PYTHONDONTWRITEBYTECODE="1"` flag and explicitly writes bytecode to disk. Setting `$env:PYTHONPYCACHEPREFIX=".tmp\pycache"` safely redirects all cache writes to a non-source directory.

## Target Paths

```json
{
  "target_paths": [
    ".claude/skills/gtkb-sweep-commit/SKILL.md"
  ]
}
```

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/gtkb-sweep-commit/SKILL.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Proposal must be filed on the file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This section links specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification section below map specs to tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project linkage is at the top of the file.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Target paths are within root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (Advisory) - Modifying canonical skill representation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (Advisory) - Updating the canonical `.claude/skills/...` triggers generation updates for Antigravity and Codex skill adapters.

## Prior Deliberations

<!-- Pre-populated by helper; review and prune. -->
- No prior deliberations related directly to pycache writing issues on Windows in `gtkb-sweep-commit`. The implementation is straightforward.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20260964` — seed=search; bridge_thread; Verification Verdict - gtkb-sweep-commit Skill Parity Registration
- DA: `DELIB-20261163` — seed=search; bridge_thread; Verification Verdict - gtkb-sweep-commit Skill Parity Registration
- DA: `DELIB-20260967` — seed=search; bridge_thread; Corrective Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- DA: `DELIB-20261166` — seed=search; bridge_thread; Corrective Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- DA: `DELIB-20261759` — seed=search; bridge_thread; Bridge thread: gtkb-sweep-commit-skill-parity-registration (9 versions, VERIFIED

## Owner Decisions / Input

- `DELIB-20260616-MAY29-HYGIENE-AUTHORIZATION` - Owner decision authorizing the defect fix for `WI-4611` under project authorization.

## Proposed Scope

### 1. Update `gtkb-sweep-commit/SKILL.md`

Modify the `gtkb-sweep-commit` verification script block to set `PYTHONPYCACHEPREFIX`.

```powershell
   if ($py.Count -gt 0) {
     $env:PYTHONPYCACHEPREFIX=".tmp\pycache"
     & $python -m py_compile @py
     & $python -m ruff check @py
     & $python -m ruff format --check @py
   }
```

## Specification-Derived Verification Plan

| Specification | Target Test / Manual Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Protocol path: NEW proposal -> LO Review -> GO -> Implementation -> Post-Impl -> VERIFIED |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute `python scripts/generate_antigravity_skill_adapters.py --update-registry` and `python scripts/generate_codex_skill_adapters.py --update-registry` and confirm adapters successfully generated with no errors. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify `git diff --cached --name-only` shows changes only inside root directory. |

## Acceptance Criteria

1. `.claude/skills/gtkb-sweep-commit/SKILL.md` correctly assigns `$env:PYTHONPYCACHEPREFIX=".tmp\pycache"`.
2. Antigravity and Codex skill adapters are regenerated to reflect the update.
3. No syntax or syntax checker errors are introduced.

## Risks / Rollback

- **Risk**: Very low risk. `PYTHONPYCACHEPREFIX` is supported natively in Python 3.8+ and redirects compilation files without changing program logic.
- **Rollback**: Use `git checkout HEAD -- .claude/skills/gtkb-sweep-commit/SKILL.md` and rerun the generator scripts.

## Files Expected To Change

- `.claude/skills/gtkb-sweep-commit/SKILL.md`
- `.agent/skills/gtkb-sweep-commit/SKILL.md` (Generated)
- `.codex/skills/gtkb-sweep-commit/SKILL.md` (Generated)

## Recommended Commit Type

`fix`


