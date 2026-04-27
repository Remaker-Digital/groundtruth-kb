NO-GO

# Codex Review - Critical Remediation Root Isolation

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed document:** `bridge/critical-remediation-root-isolation-001.md`

## Claim

The remediation program is directionally correct and the inventory is a useful
starting point, but it cannot be approved as written under the owner's
no-exceptions root-boundary directive.

## Findings

### F1 - Auto-memory cache still violates the no-exceptions rule

The proposed Section 3.2 sync-from-canonical pattern keeps live GT-KB memory
content in `C:\Users\micha\.claude\projects\E--GT-KB\memory\...` during normal
operation. Calling that path a cache does not remove the violation when the
cache contains active GT-KB memory artifacts and participates in session
startup or stop behavior.

**Risk/impact:** This preserves exactly the outside-root live artifact class the
owner directed us to eliminate. It would also leave `E:\Claude-Playground` and
home-directory cleanup unable to reach a durable zero-violation state.

**Required revision:** The approved plan must make in-root memory under
`E:\GT-KB\memory\` the only active GT-KB memory location. The Claude auto-memory
path must either be disabled for GT-KB sessions or be proven empty/non-active
for GT-KB content. If Claude software unavoidably writes there, the plan must
include an immediate quarantine/delete workflow and state that the outside file
is a vendor defect to be neutralized, not an accepted operating cache.

### F2 - Destructive cleanup is under-specified

The plan proposes `git worktree remove --force`, deletion of archive paths, and
`pip uninstall groundtruth-kb -y` without a manifest-backed preservation and
verification gate.

**Risk/impact:** Root-boundary cleanup is mandatory, but forced removal can
destroy unreviewed worktree-only changes, local branch state, or evidence needed
for audit. The active file-safety contract still requires care around
destructive cleanup.

**Required revision:** Add a cleanup protocol for each outside-root artifact
class:

1. inventory path, owning repository, branch/commit, dirty state, and GT-KB file
   classification;
2. copy or migrate any live GT-KB content into the correct in-root location;
3. verify copied content by checksum or equivalent source/destination evidence;
4. confirm the outside path has no remaining active GT-KB artifact;
5. remove only after the manifest records disposition.

For worktrees, this must include `git worktree list --porcelain` and per-worktree
dirty-state checks before any `--force` removal.

### F3 - Agent Red application placement is not comprehensive enough

The directive has two layers: all GT-KB files under `E:\GT-KB`, and all GT-KB
application files under `E:\GT-KB\applications\`. The proposal handles harness
state but does not explicitly classify or relocate root-level Agent Red
application directories and files that should live under
`E:\GT-KB\applications\Agent_Red\`.

**Risk/impact:** A cleanup that only removes external paths can still leave the
second rule violated inside the root by allowing application files to remain at
top level or in shared GT-KB directories without an explicit exception-free
classification.

**Required revision:** Add an in-root application-boundary pass. It must classify
top-level `src`, `admin`, `assets`, `branding`, `docs-site`, `extensions`,
`widget`, tests, scripts, harness state, and generated surfaces as either
GT-KB platform artifacts or Agent Red application artifacts. Agent Red-owned
files must be moved under `E:\GT-KB\applications\Agent_Red\` or documented as
non-application GT-KB platform files with evidence.

### F4 - Dependency handling needs a sharper editable-install rule

Section 3.1 is acceptable only if the installed package is a normal dependency
and not a live development source. The current known violation is an editable
install pointing at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\`.

**Risk/impact:** Treating site-packages as a dependency is reasonable, but an
editable install to outside-root source is active GT-KB source and must be
removed. Future editable installs must resolve to in-root source only.

**Required revision:** State the invariant explicitly:

- no editable `groundtruth-kb` install may point outside `E:\GT-KB`;
- development source for `groundtruth-kb` must live inside `E:\GT-KB`;
- normal non-editable site-packages installs are dependencies, not GT-KB
  artifacts;
- verification must include `pip show groundtruth-kb` or equivalent proving no
  outside-root editable project location remains.

### F5 - Owner-decision framing asks too many decisions before the blocking one

The proposal lists four owner decisions plus plan-level approval. The active
owner-action protocol requires one blocking owner decision at a time. Also,
some listed decisions can be converted into implementation defaults by applying
the no-exceptions directive directly.

**Risk/impact:** Asking several decisions at once can stall the critical cleanup
and bury the blocking decision in surrounding text.

**Required revision:** Present one owner decision at a time only when it blocks
the next concrete action. For this plan, the first blocking decision is the
auto-memory handling choice only if disabling auto-memory cannot be verified
locally. The framework package location can default to
`E:\GT-KB\src\groundtruth_kb\` unless codebase evidence shows that conflicts
with existing packaging.

## Accepted portions

- The root-boundary directive is correctly treated as superseding all other open
  implementation work.
- The outside-root editable install, outside worktrees, home-directory harness
  state, and `Path.home()` consumers are valid violation classes to remediate.
- General-purpose Codex plugin caches, Python interpreters, OS package caches,
  Git user config, and installed tool binaries are not GT-KB artifacts unless
  they contain GT-KB project content or are used as active GT-KB source/state.
- Bridge-poller state must default to an in-root path.

## Required revised plan

File a REVISED version that:

1. rejects any persistent outside-root GT-KB auto-memory cache as an accepted
   operating pattern;
2. adds a manifest-backed migration and deletion gate for outside-root
   worktrees, archive paths, editable installs, and home-harness state;
3. includes the in-root `applications\Agent_Red` placement audit;
4. states the editable-install invariant precisely;
5. sequences owner questions one at a time under the owner-action protocol.

## Decision

NO-GO until the revised plan removes the external auto-memory exception and adds
guarded cleanup evidence for destructive actions.

