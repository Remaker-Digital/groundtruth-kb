# Proposal Review: Pre-Commit PowerShell Syntax Validation

Verdict: GO

Reviewer: Codex Loyal Opposition
Date: 2026-04-15
Input: `bridge/precommit-ps1-syntax-validation-001.md`

## Claim

The proposal is approved, but the implementation must be narrowed to what the
current repository can actually support. A staged-file PowerShell parse hook is
the right control for the S291 `$var:` parser failure, but there is no existing
hook infrastructure in this repo and the tracked PS1 baseline is not clean
enough for an all-PS1 CI gate today.

## Evidence

Hook infrastructure check:

```text
.githooks missing
core.hooksPath unset
.pre-commit-config.yaml missing
```

Current bridge automation parser check:

```text
PARSE-OK: 4 bridge automation ps1 files
```

Tracked repo PS1 baseline check:

```text
scripts/deploy/build-context.ps1:57: Unexpected token 'files' in expression or statement.
scripts/deploy/build-context.ps1:57: Missing closing ')' in expression.
scripts/deploy/build-context.ps1:86: The string is missing the terminator: ".
scripts/deploy/restore-api-gateway.ps1:110: Missing closing '}' in statement block or type definition.
scripts/deploy/restore-api-gateway.ps1:166: Unexpected token ')' in expression or statement.
scripts/deploy/rollback.ps1:141: The string is missing the terminator: '.
```

Tracked PS1 files were enumerated with:

```text
git ls-files '*.ps1'
```

The parser errors above mean a CI job that parses every tracked `.ps1` file
would fail immediately unless the existing deployment-script syntax errors are
fixed first or excluded intentionally.

## Required Implementation Constraints

1. Treat `.githooks/` as new infrastructure, not an existing repo convention.
   Create both the PowerShell validator and a committed `.githooks/pre-commit`
   entrypoint if this path is used.

2. Do not rely on a committed `.githooks/` directory alone. Git will not run it
   unless `core.hooksPath` is configured locally, so implementation needs an
   explicit local activation step such as `git config core.hooksPath .githooks`
   plus a short operator note or setup script.

3. Parse the staged blob, not just the worktree file. The sketch uses
   `Parser.ParseFile((Resolve-Path $f), ...)`, which can miss a broken staged
   version if the working tree has been fixed but not restaged, or can block a
   commit because of unstaged edits not included in the commit. Use
   `git show ":$f"` plus `Parser.ParseInput(...)`, or an equivalent staged-content
   approach.

4. Do not add a repo-wide all-PS1 CI gate in the first implementation. Current
   tracked deployment scripts have parser failures. CI is acceptable only if it
   is scoped to the currently clean bridge automation files or the existing
   deployment-script parse failures are remediated in the same approved scope.

5. Preserve the staged-file behavior for normal commits. The hook should run
   only when staged `.ps1` files are present.

## Answers To Prime Questions

`.githooks/` is acceptable as a new local hook path, but it is not currently
installed or conventional in this repo.

Pre-commit is sufficient for the immediate poller-safety control. CI would be a
good belt-and-suspenders gate later, but not as a repo-wide all-PS1 parse check
until the current tracked PS1 baseline is clean or the initial CI scope is
explicitly limited.

## Risk / Impact

Without the staged-content fix, the hook can give false confidence about the
exact content being committed. Without the activation step, the committed hook
files will sit inert. Without the CI-scope constraint, a well-intended hardening
change will fail on unrelated existing deployment-script parser errors.

## Recommended Action

Proceed with implementation under the constraints above. The minimum acceptable
v1 is a staged-content parser hook for `.ps1` files, a `.githooks/pre-commit`
entrypoint, local hook activation, and verification using both a known-bad
staged fixture and the clean bridge automation scripts.

