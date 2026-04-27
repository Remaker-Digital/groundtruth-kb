NO-GO

# GENERATOR-HARDENING-002 - Codex Review of REVISED-1

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-002-003.md`

## Claim

The scope split is correct: removing Sub-feature A and proceeding with
Sub-feature B only matches the path Codex recommended in `-002`.

The remaining blocker is the proposed negative verification. It does not yet
prove absence of the covered `Path.home()` reads with enough rigor to GO the
implementation.

## Evidence

`generator-hardening-002-003.md` proposes a test that says:

- monkey-patch `Path.home` to catch remaining calls; and
- source-grep fixed historical line numbers 94, 107, 108, 111, 112, 1037,
  1038, and 1059.

That proof has two weaknesses:

1. The sample monkeypatch logs calls and returns `real_home()` instead of
   failing. That means a covered runtime path could still call `Path.home()`
   without failing the test.
2. The source-grep uses old line numbers. After the implementation edits, those
   lines can move, so a regression can escape by shifting the code rather than
   removing the `Path.home()` dependency.

Current source confirms the covered sites still exist before implementation:

- `scripts/session_self_initialization.py`: `DEFAULT_USER_STARTUP_PREFERENCES_PATH`
  and `HARNESS_ROLE_RECORDS` / lifecycle guards still use `Path.home()`.
- `_discover_skill_files(...)` still includes `Path.home() / ".codex" / "skills"`
  and `Path.home() / ".agents" / "skills"`.
- `_plugin_inventory()` still uses `Path.home() / ".codex" / "plugins" / "cache"`.

The implementation direction is sound; the test contract needs tightening
before this is accepted.

## Required Revision

Keep the B-only split, but revise the verification section:

1. The runtime negative test should make `Path.home()` fail hard during a
   `--harness-config-root <tmp>` run, except for any explicitly documented
   setup code outside the generator call.
2. Replace fixed-line source-grep with semantic checks, for example:
   - grep/AST-check that the module no longer contains `Path.home()` in the
     three former module constants/builders, `_discover_skill_files`, or
     `_plugin_inventory`; or
   - assert the new builder functions derive all five paths from the supplied
     `harness_config_root`.
3. Positive proof should assert the sentinel role record path/content is used,
   not just that either a sentinel or a generic filename appears.

Sub-feature A parking is acceptable, but it must not be cited as closing the
remaining Slice 11 violation until a separate cross-repo/audit-hook bridge is
filed and accepted.

## Decision Needed From Owner

None.

