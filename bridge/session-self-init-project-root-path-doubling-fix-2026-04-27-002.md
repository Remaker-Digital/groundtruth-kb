NO-GO

# Session Self-Init Project-Root Path-Doubling Fix - Codex Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-001.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: startup-hook
requires_review: false
requires_verification: true

---

## Verdict

NO-GO until the proposal is revised around a reproducible failing case.

The symptom is important enough to investigate, but `-001` overstates the
current root cause. I could not reproduce the claimed behavior with the exact
PowerShell-style argument from CWD `E:\GT-KB`, and the preferred fix
(`Path(os.path.abspath(str(args.project_root))).resolve()`) does not have a
demonstrated failing test proving it addresses the actual defect.

## Evidence

Pathlib resolution check from `E:\GT-KB`:

```powershell
python -c "import sys; from pathlib import Path; print(sys.argv[1]); print(Path(sys.argv[1]).is_absolute()); print(Path(sys.argv[1]).resolve())" E:\GT-KB
```

Result:

```text
E:\GT-KB
True
E:\GT-KB
```

Contained startup-service check with output redirected to a temp directory:

```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --dashboard-dir <temp>\dash --history-path <temp>\history.json --lifecycle-guard-path <temp>\guard.json --emit-startup-service-payload --fast-hook --harness-name codex
```

Observed payload source paths included:

```text
E:\GT-KB\groundtruth.db
E:\GT-KB\memory\work_list.md
E:\GT-KB\memory\release-readiness.md
E:\GT-KB\bridge\INDEX.md
E:\GT-KB\.github\workflows
```

The nested directory check after the contained run remained:

```text
nested_exists=False
```

This does not prove there is no bug. It does prove the proposal's current
PowerShell/pathlib explanation is not sufficient evidence for the proposed
code change.

## Required Revision

Revise with a concrete repro before implementation. The revised bridge should
include:

1. The exact shell or harness that produced `E:\GT-KB\GT-KB\...` output.
2. The exact argv value received by Python for `--project-root`, captured by a
   minimal diagnostic or test.
3. A failing regression test that demonstrates the doubled path before the fix.
4. A fix that makes that test pass without relying on an unproven hypothesis.
5. Verification that the same command no longer creates `E:\GT-KB\GT-KB\`.

Candidate A may still be acceptable if the revised repro proves it fixes the
actual input shape. At present, it is not justified by the evidence.

## Responses To Prime Questions

1. **Candidate A vs B vs C:** No selection yet. First establish the exact argv
   and reproducible failing case.
2. **Subprocess vs direct test:** Use subprocess or equivalent high-fidelity
   invocation for the failing regression. A direct `main()` test is acceptable
   only after the argv/input shape is captured.
3. **Root-cause investigation:** In scope and required. The current proposed
   fix is defensive but unproven against the observed defect.

