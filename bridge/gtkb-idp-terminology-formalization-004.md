NO-GO

# Loyal Opposition Review: GT-KB IDP Terminology Formalization Rev 1

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-idp-terminology-formalization-003.md`

## Verdict

NO-GO.

Revision 1 fixes the two execution defects called out in `-002`: it removes the
nonexistent `memory/MEMORY.md` target and replaces the broken `db.py
get_deliberation` CLI claim with an executable Python/helper path. Those fixes
are real.

The proposal is still not ready to GO because it formalizes a new canonical
GT-KB term in `CLAUDE-REFERENCE.md`, which this repo explicitly treats as a
read-on-demand static reference, while prior canonical-terminology governance
for GT-KB requires canonical terms to live in the governed startup/control
surface and managed terminology artifacts. As written, this would create a new
one-off static definition path instead of extending the already-established
canonical terminology system.

## Prior Deliberations

- `bridge/gtkb-canonical-terminology-surface-002.md` is the direct prior
  governance review for where canonical GT-KB terminology belongs.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md` is the
  verified implementation record for that terminology-surface contract in
  GT-KB.
- `DELIB-0716` / `DELIB-0722` are the compressed deliberation records for that
  bridge thread and implementation thread.
- `DELIB-0877` remains relevant context for the GT-KB/application-isolation
  direction, but it is not the only relevant prior terminology record.

## Findings

### F1 - Blocking: the proposal uses a non-startup static reference file as the canonical terminology surface

The proposal now limits scope to `CLAUDE-REFERENCE.md` and a new
`docs/gtkb-idp-concept.md`, and it says future governance artifacts should use
the IDP terminology by documenting that convention in `CLAUDE-REFERENCE.md`.
That conflicts with the already-reviewed canonical-terminology direction for
GT-KB work: canonical terms are supposed to live in the governed startup/control
surface and managed terminology artifacts, not in another one-off doc edit.

This matters because `CLAUDE-REFERENCE.md` is explicitly "not loaded
automatically" and points readers back to `CLAUDE.md` for active guidance,
while `CLAUDE.md` is the file loaded at the start of every session. A canonical
term meant to govern future bridge proposals, reports, and other artifacts is
misplaced if its authoritative definition lives only in an on-demand static
reference file.

### F2 - Blocking: the Prior Deliberations section is incomplete and understates existing GT-KB terminology governance history

The revision says there is "No prior DELIB on GT-KB terminology itself." That is
not defensible against the existing bridge and deliberation history. The
canonical-terminology bridge already established the governing rule that GT-KB
canonical terms belong in startup/control surfaces and managed terminology
artifacts, and that implementation was later verified upstream.

If Prime wants this IDP term to be a deliberate exception to that earlier
contract, the proposal has to say so explicitly and justify the exception. If
Prime does not want an exception, the proposal needs to be refilled against the
existing canonical terminology system rather than against `CLAUDE-REFERENCE.md`
alone.

## Evidence

- `bridge/gtkb-idp-terminology-formalization-003.md:100`-`:118` scopes the
  canonical terminology work to `CLAUDE-REFERENCE.md`,
  `docs/gtkb-idp-concept.md`, and a first-mention convention documented in
  `CLAUDE-REFERENCE.md`.
- `bridge/gtkb-idp-terminology-formalization-003.md:135`-`:139` lists only
  `DELIB-0877`, says "No prior DELIB on GT-KB terminology itself," and omits
  the earlier canonical-terminology bridge/history.
- `CLAUDE-REFERENCE.md:1`-`:5` defines that file as "Static Reference Material,"
  says it is "**not** loaded automatically," and points active guidance back to
  `CLAUDE.md`.
- `CLAUDE.md:3` says `CLAUDE.md` is loaded at the start of every session, and
  `CLAUDE.md:7`-`:10` classifies `CLAUDE-REFERENCE.md` as read-on-demand
  reference data rather than the active control surface.
- `bridge/gtkb-canonical-terminology-surface-002.md:15`-`:24` states that the
  right remediation for canonical terminology is "not another one-off doc edit"
  but a governed terminology record plus startup, template, doctor, and
  bridge-gate propagation.
- `bridge/gtkb-canonical-terminology-surface-002.md:117`-`:139` requires the
  concise glossary block to live in `CLAUDE.md` and `AGENTS.md` and to point to
  the full terminology record.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md:16`-`:19`
  verifies the GT-KB implementation contract: canonical terminology artifacts
  are managed as registry-backed rule artifacts under `.claude/rules/`.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md:48`-`:65`
  verifies the managed artifact and doctor integration for
  `.claude/rules/canonical-terminology.md` and
  `.claude/rules/canonical-terminology.toml`.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md:113`-`:123`
  verifies that fresh scaffolds surface terminology through `CLAUDE.md`,
  `AGENTS.md`, `MEMORY.md`, and the managed canonical-terminology rule artifacts
  rather than through a static reference-only file.
- Read-only command result in this checkout:
  `Get-ChildItem .claude/rules | Where-Object { $_.Name -like 'canonical-terminology*' }`
  returned `NO_MATCHES`, which means Agent Red currently lacks the managed
  terminology artifacts that the earlier GT-KB thread expected projects to
  carry. That makes a new one-off `CLAUDE-REFERENCE.md` definition even more
  likely to create drift rather than close it.
- Read-only verification of the revised DELIB path succeeded:
  importing `.claude/skills/decision-capture/helpers/record_decision.py` and
  `groundtruth_kb.db.KnowledgeDB(Path('groundtruth.db'))` worked, and
  `db.get_deliberation('DELIB-GTKB-IDP-TERMINOLOGY')` returned `absent` before
  implementation. So the new verification approach is executable; it is not the
  remaining blocker.

## Required Action Items

1. Refile this as a canonical-terminology surface update, not as a
   `CLAUDE-REFERENCE.md`-only terminology formalization. Name the exact
   governed surfaces to update in Agent Red for canonical GT-KB terminology.
2. Either extend the existing canonical-terminology control surface contract to
   carry the IDP term, or explicitly state and justify a deliberate exception to
   that contract. Do not leave the relationship implicit.
3. Update the Prior Deliberations section to cite the earlier canonical
   terminology thread (`DELIB-0716` / `DELIB-0722` or the corresponding bridge
   files) and explain how this proposal relates to it.
4. Keep the revised helper/Python DELIB verification path from `-003`; that
   portion no longer needs rework.

## Decision Needed From Owner

None, unless Prime intends to supersede the prior canonical-terminology surface
contract rather than extend it.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-idp-terminology-formalization' -Context 0,20
Get-Content bridge/gtkb-idp-terminology-formalization-001.md
Get-Content bridge/gtkb-idp-terminology-formalization-002.md
Get-Content bridge/gtkb-idp-terminology-formalization-003.md
Get-Content tools/knowledge-db/db.py
Get-Content .claude/skills/decision-capture/helpers/record_decision.py
Get-Content CLAUDE.md
Get-Content CLAUDE-REFERENCE.md
Get-Content docs/operations/gtkb-session-startup-dashboard.md
Get-Content docs/vision/groundtruth-kb-user-experience-scenario.md
Get-Content bridge/gtkb-canonical-terminology-surface-002.md
Get-Content bridge/gtkb-canonical-terminology-surface-implementation-012.md
Get-ChildItem E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
rg -n "class KnowledgeDB|get_deliberation|insert_deliberation" E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src
rg -n "GT-KB|GroundTruth-KB|Internal Developer Platform|IDP" CLAUDE-REFERENCE.md docs
Get-ChildItem .claude/rules | Where-Object { $_.Name -like 'canonical-terminology*' }
python - <<read-only sqlite/KnowledgeDB queries against groundtruth.db for DELIB-0715, DELIB-0716, DELIB-0722, DELIB-0804, DELIB-0877 and terminology matches>>
python - <<read-only import check for record_decision and KnowledgeDB(Path('groundtruth.db'))>>
```
