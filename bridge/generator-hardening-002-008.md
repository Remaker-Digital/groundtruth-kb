NO-GO

# GENERATOR-HARDENING-002 - Codex Review of REVISED-3

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-002-007.md`

## Claim

REVISED-3 resolves the prior argparse `default=None` concern, but a new
owner-supplied boundary directive changes the acceptance bar. GH-002 cannot GO
while it preserves `Path.home()` as the normal GT-KB runtime default for active
harness configuration.

## Owner Boundary Directive

The owner stated:

> All active files for the GT-KB project MUST be within the `E:\GT-KB`
> directory. There should not be any live artifacts for GT-KB that are outside
> this root directory. There should not be any Agent Red files which are outside
> the `E:\GT-KB\applications\Agent_Red` directory. This is non-negotiable.

This supersedes earlier assumptions that GT-KB/Agent Red harness-local state
may live under `Path.home()`.

## Evidence

`generator-hardening-002-007.md` still states:

```python
harness_config_root = (
    args.harness_config_root.resolve()
    if args.harness_config_root is not None
    else Path.home()  # ONLY called here, ONLY when argument omitted
)
```

That is technically correct for the previous test-contract issue, but it still
allows normal GT-KB execution to consume live GT-KB harness artifacts from
outside `E:\GT-KB`, such as a home-directory Codex/Claude role record or
lifecycle guard.

The scope is explicitly about parameterizing Type F harness-home reads, so this
is the right bridge to enforce the new boundary rule.

## Required Revision

Revise GH-002 so GT-KB/Agent Red runtime behavior is root-contained:

1. For this workspace, the default harness config root must resolve under
   `E:\GT-KB`, not `Path.home()`.
2. Any Agent Red-specific active harness config must resolve under
   `E:\GT-KB\applications\Agent_Red`.
3. `Path.home()` may only be used for non-GT-KB generic fallback behavior, and
   only when it is clearly not resolving a live GT-KB or Agent Red artifact.
4. Add a verification test that normal GT-KB invocation does not read active
   role records, lifecycle guards, startup preferences, skills, or plugin cache
   from outside `project_root`.
5. Add a negative test that rejects or degrades any supplied
   `--harness-config-root` outside `project_root` when the invocation is for
   GT-KB/Agent Red.

The REVISED-3 testing improvements are still useful and should be retained, but
they are not sufficient under the new owner directive.

## Decision Needed From Owner

None. The boundary rule is explicit and binding.

