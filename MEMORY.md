# MEMORY.md — GroundTruth-KB

This is the GT-KB checkout's **MEMORY.md** root marker. The actual operational
notepad for active session state lives at `memory/MEMORY.md` (per the
`memory/` topic-file pattern this checkout uses for its elaborate governance
state). This root file exists to satisfy the `dual-agent` doctor profile's
`required_files` content contract for the canonical-terminology check.

## Canonical Terminology (anchored — required for doctor's `dual-agent` profile)

The five canonical startup terms required in every `required_files` entry per
`.claude/rules/canonical-terminology.toml`:

- **MemBase** — the canonical, authoritative store of specifications and
  governed knowledge for the project (`groundtruth.db`). Append-only/versioned.
- **Deliberation Archive** — the design-reasoning tier of ADR-0001;
  `deliberations` table in `groundtruth.db`; searchable via
  `gt deliberations search <query>`.
- **MEMORY.md** — the operational notepad tier of ADR-0001. This root file is
  the doctor-required marker; `memory/MEMORY.md` carries the active session
  state in this GT-KB checkout's organic governance layout.
- **Prime Builder** — the implementing agent in the dual-agent protocol;
  proposes changes, writes code, runs tests.
- **Loyal Opposition** — the reviewing agent in the dual-agent protocol;
  inspects, critiques, issues GO / NO-GO / VERIFIED verdicts.

Full glossary at `.claude/rules/canonical-terminology.md`.

## Where the live operational notepad lives

For active session state (recent sessions, in-flight work, version pointers,
operational context), see [memory/MEMORY.md](memory/MEMORY.md). That file
follows the GT-KB-checkout convention of placing memory artifacts under the
`memory/` topic-file directory.

This root MEMORY.md is intentionally compact — it carries the canonical-term
content contract but defers all operational state to the topic file.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
