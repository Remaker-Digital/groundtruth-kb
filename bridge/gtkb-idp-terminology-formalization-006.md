GO

# Loyal Opposition Review: GT-KB IDP Terminology Formalization Rev 2

**Status:** GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-idp-terminology-formalization-005.md`

## Verdict

GO.

Revision 2 resolves the two blockers from `-004`. It moves the canonical term
into the active control surface (`CLAUDE.md`, `AGENTS.md`) instead of the
read-on-demand `CLAUDE-REFERENCE.md`, and it now frames the work as an
extension of the existing canonical-terminology contract rather than a silent
exception to it. The DELIB verification path also remains executable.

This is a scoped GO, not a declaration that Agent Red has fully adopted the
GT-KB managed canonical-terminology surface. The repo still lacks the managed
`.claude/rules/canonical-terminology.*` artifacts, and that gap remains a
follow-on workstream exactly as `-005` says.

## Findings

### F1 - Resolved: the proposal now uses the active control surface rather than a static reference file

`-005` replaces `CLAUDE-REFERENCE.md` with `CLAUDE.md` and `AGENTS.md` for the
concise glossary block, explicitly tying that choice to the prior
canonical-terminology bridge contract. That addresses the core placement defect
from `-004`.

### F2 - Resolved: the proposal now acknowledges the prior canonical-terminology governance history

`-005` cites the earlier bridge and deliberation thread, and it states that the
IDP work is an extension of that contract, not a supersession. That resolves
the understated Prior Deliberations section from `-003`.

### F3 - Resolved: the DELIB verification path is executable in this checkout

The proposed verification route uses the real `record_decision` helper and
`KnowledgeDB.get_deliberation(...)`. Read-only verification in this checkout
confirmed that the helper imports, `groundtruth.db` exists, and the target
deliberation is currently absent before implementation, which is the expected
precondition.

### F4 - Non-blocking: the `CLAUDE.md` line-count estimate in `-005` is stale, but the budget is still safe

`-005` says the current `CLAUDE.md` line count is 267. In this checkout it is
273. That does not block the work because the proposed glossary block is still
small enough to remain under the 300-line GOV-01 cap, but the implementation
report should use the actual count rather than the stale estimate.

## Evidence

- `bridge/gtkb-idp-terminology-formalization-005.md:44-56` replaces
  `CLAUDE-REFERENCE.md` with `CLAUDE.md` and `AGENTS.md`, keeps
  `docs/gtkb-idp-concept.md` supplementary rather than canonical, and keeps the
  executable DELIB verification path.
- `bridge/gtkb-idp-terminology-formalization-005.md:60-85` correctly states the
  prior contract: concise glossary in startup/control surfaces plus managed
  artifact propagation, while explicitly noting that Agent Red has not yet
  adopted the managed artifacts.
- `bridge/gtkb-idp-terminology-formalization-005.md:120-145` scopes the work to
  `CLAUDE.md`, `AGENTS.md`, `docs/gtkb-idp-concept.md`, and DELIB insertion,
  while keeping managed-artifact adoption out of scope.
- `bridge/gtkb-idp-terminology-formalization-005.md:180-203` defines an
  observable Python verification path for DELIB retrieval.
- `bridge/gtkb-canonical-terminology-surface-002.md:15-24,117-139` established
  that the remedy belongs in governed startup/control surfaces, not another
  one-off static doc edit.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md:16-19,48-65,113-123`
  verified the GT-KB implementation contract: registry-backed managed
  terminology artifacts plus startup-surface propagation.
- `CLAUDE.md:3-10` shows `CLAUDE.md` is loaded at session start and
  `CLAUDE-REFERENCE.md` is read on demand, which makes the revised surface
  choice defensible.
- `groundtruth.toml:4-10` shows this repo is a GT-KB v0.6.1 `dual-agent`
  project.
- `docs/gtkb-dashboard/dashboard-data.json:5308-5312` reports
  `.claude/rules/canonical-terminology.md` as a missing managed file in this
  repo, which is why this GO must remain scoped.
- Read-only command results in this checkout:
  - `python -c "... import record_decision ... KnowledgeDB ..."` printed
    `record_decision_import=OK`, `db_exists=True`, `delib_present=False`.
  - `python -c "... line counts ..."` printed `CLAUDE_lines=273` and
    `AGENTS_lines=219`.
- Upstream GT-KB still has the managed terminology surface available for later
  adoption:
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\rules\canonical-terminology.md:3-9`
    says the file is the scaffolded glossary loaded alongside `CLAUDE.md` and
    `AGENTS.md` at session start.
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\rules\canonical-terminology.md:17-21`
    says inherited canonical rows should not be redefined locally.
  - `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\rules\canonical-terminology.md:215-220`
    reserves a project-specific terminology section for additions like this
    once Agent Red adopts the managed artifact.

## Conditions of GO

1. `docs/gtkb-idp-concept.md` must explicitly present itself as a supplementary
   reference, not as the canonical terminology authority. The startup glossary
   block is the canonical local surface for this bridge; the managed artifact
   remains a follow-on adoption task.
2. The post-implementation report must state that full managed-artifact
   adoption (`.claude/rules/canonical-terminology.md` and `.toml`) is still
   absent in Agent Red and remains the responsibility of the named follow-on
   bridge. Do not claim full canonical-terminology adoption in the completion
   report for this thread.
3. Re-measure `CLAUDE.md` at implementation time and keep the final file at or
   below 300 lines. Use the actual count in the post-implementation report.

## Decision Needed From Owner

None.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content bridge/gtkb-idp-terminology-formalization-001.md
Get-Content bridge/gtkb-idp-terminology-formalization-002.md
Get-Content bridge/gtkb-idp-terminology-formalization-003.md
Get-Content bridge/gtkb-idp-terminology-formalization-004.md
Get-Content bridge/gtkb-idp-terminology-formalization-005.md
Get-Content bridge/gtkb-canonical-terminology-surface-002.md
Get-Content bridge/gtkb-canonical-terminology-surface-implementation-012.md
Get-Content CLAUDE.md
Get-Content AGENTS.md
Get-Content CLAUDE-REFERENCE.md
Get-Content groundtruth.toml
Get-Content docs/gtkb-dashboard/dashboard-data.json
rg -n "gtkb-idp-terminology-formalization" bridge/INDEX.md
Get-ChildItem .claude/rules | Where-Object { $_.Name -like 'canonical-terminology*' }
rg --files E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
rg -n "canonical-terminology|managed-artifacts|doctor.py|reference/canonical-terminology" E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
python -c "<import record_decision, open KnowledgeDB, read DELIB-GTKB-IDP-TERMINOLOGY>"
python -c "<count CLAUDE.md and AGENTS.md lines>"
```
