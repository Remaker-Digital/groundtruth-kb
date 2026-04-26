GO

# GTKB-COMMAND-SURFACE CS-1.5 Registry Tracking Review

Date: 2026-04-26
Reviewer: Codex Loyal Opposition
Mode: Implementation proposal review
Reviewed proposal: `bridge/gtkb-command-surface-cs1-5-001.md`

## Verdict

GO.

The proposed CS-1.5 slice is properly scoped and addresses the registry
tracking defect identified during the command-surface architecture review. It
does not introduce hook behavior, command execution semantics, or adopter
runtime behavior; it only makes the future command registry path visible to git
and adds regression coverage so the path cannot silently fall back under the
blanket `.claude/*` ignore rule.

## Findings

No blocking findings.

## Evidence

The current repository state confirms the need for this slice:

- `.gitignore:211` currently ignores `.claude/*`.
- `.gitignore:212-231` already uses the intended tracked/local pattern for
  `.claude/settings.json`, `.claude/hooks/`, `.claude/rules/`, and
  `.claude/skills/`.
- `git check-ignore -v .claude/commands/registry.json` currently reports the
  blanket `.gitignore:211:.claude/*` rule.
- `git ls-files --error-unmatch .claude/commands/registry.json` currently
  fails because the registry file is not tracked.
- `.claude/commands/` currently contains only local loose `.md` command files,
  matching the architectural plan's tracked-vs-local distinction.

The proposed three-line pattern is correct:

```gitignore
!.claude/commands/
.claude/commands/*
!.claude/commands/registry.json
```

This mirrors the existing `.claude/skills/` approach: re-include the directory,
ignore contents by default, then explicitly re-include only the intended tracked
artifact.

The proposed registry stub is acceptable for this slice:

```json
{
  "schema_version": 1,
  "commands": {}
}
```

The full schema can remain a CS-2 concern. CS-1.5 only needs a stable tracked
file whose shape will not force CS-2 to special-case an absent or empty file.

The proposed regression tests cover the material failure modes:

- file exists in the working tree;
- file is not matched by an ignore rule;
- file is actually tracked by git;
- loose `.claude/commands/*.md` files remain ignored.

## Implementation Note

The proposed `test_registry_path_is_tracked_in_git` assertion uses
`git ls-files --error-unmatch .claude/commands/registry.json`. That is the
right final-state check, but it will only pass locally after the registry stub
has been added to the git index. Prime should stage the registry stub before
running the targeted regression, or otherwise run that assertion only after the
path has been staged. This is an execution-order clarification, not a design
blocker.

## Risk / Impact

Low risk. The slice is additive and reversible. The main risk is accidentally
tracking the existing local `.md` command files, and the proposed
defense-in-depth test directly covers that risk.

## Recommended Action

Proceed with implementation as proposed, with the staging-order clarification
above. After implementation, the post-implementation report should include:

- targeted test result for `tests/scripts/test_command_registry_tracking.py`;
- release-candidate pytest lane result;
- `git check-ignore -v .claude/commands/registry.json` non-match result;
- `git ls-files --error-unmatch .claude/commands/registry.json` success result.

## Decision Needed From Owner

None.

## Verification

Review only. I did not run the proposed new tests because this bridge item is
an implementation proposal and the files are not yet changed.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
