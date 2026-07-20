# Loyal Opposition Running Log

Recurring project risks, unresolved items, and cross-session context for the
Loyal Opposition role. Full evidence-based reports live in
`CODEX-INSIGHT-DROPBOX/`; this log tracks what remains open across sessions.

This file did not exist prior to the entry below (2026-07-17); created per
`.claude/rules/codex-knowledge-base-index.md`'s "existing running log"
convention and the standard Loyal Opposition wrap-up procedure.

## 2026-07-17 19:16 UTC — Implementation-start-gate chained-command + PowerShell-matcher investigation

Full report: `CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-17-19-16.md`

**Open / unresolved:**

- `WI-5480` — `scripts/implementation_start_gate.py` `_is_safe_command()`
  false-positive-blocks `&&`/`||`/`;`-chained read-only commands. Owner-
  approved scope; not yet implemented. P2.
- `WI-5481` — `implementation-start-gate.py`'s Claude-side hook matcher in
  `.claude/settings.json` excludes the `PowerShell` tool, letting protected-
  path mutations via PowerShell bypass the mandatory bridge-GO authorization
  check entirely. Owner-approved scope; not yet implemented. **P1 — higher
  severity than WI-5480**, since it is a silent under-protection rather than
  an over-block.
- `WI-5477` — sibling PowerShell-matcher gap in `lo-file-safety-gate.py`.
  Explicitly deferred by the owner to backlog (out of the WI-5480/5481
  proposal's scope).
- `WI-5475` — ~19 of ~36 duplicate copies of the bridge status-token regex
  across the codebase still missing `NO-ACTION` (and other tokens); no
  single canonical source of truth. Deferred to backlog by owner (larger
  blast radius than the approved scope).
- `WI-5479` — the `bridge_kind` taxonomy (`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`)
  has no role-neutral, domain-neutral value for the Advisory Report artifact
  class; both `loyal_opposition_advisory` (stale doc value) and
  `governance_advisory` (live enum value) mischaracterize it. Owner
  correction archived as
  `DELIB-20260717-BRIDGE-KIND-TAXONOMY-ROLE-DOMAIN-NEUTRAL-CORRECTION`.
- An intended ADVISORY bridge entry
  (`gtkb-impl-start-gate-chained-command-powershell-gap`) was drafted but
  never successfully filed this session — blocked in sequence by a missing
  work-intent claim, the invalid `bridge_kind`, a missing mandatory template
  section, claim expiry, and an unresolved `scanner-safe-writer`
  `bash_password_flag_p` false-positive deny. Not re-attempted after the
  taxonomy correction made the classification moot for a clean filing. The
  substance is fully preserved in `WI-5480`/`WI-5481`, so no bridge thread
  needs to exist for the finding to be actionable — but a future session may
  still want to complete the filing for the audit trail once `WI-5479` lands.

**Re-check before implementing `WI-5480`/`WI-5481`:** `WI-5178`
(`PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS`, open, P0) is a
different, currently in-flight effort also targeting
`scripts/implementation_start_gate.py`. No collision at filing time
(confirmed clean `git status` on that file), but state may have moved on.

**Minor, uncaptured:** the `scanner-safe-writer` `bash_password_flag_p`
credential pattern (`-p\s+['"]?[^\s]+['"]?\s`, case-sensitive) denied three
consecutive Write attempts on a long technical markdown document without a
root cause identified before session end. Worth a look if it recurs; not
worth a standalone WI without a confirmed trigger.
