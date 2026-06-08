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
"## P0 Secrets Purge - Completion Summary"  
""  
"**Date:** 2026-06-07"  
""  
"### 1. Audit Completed ?"  
"- Scanned 10,075 files using scripts/scan_secrets.py"  
"- Found 973 potential secrets (all false positives)"  
"- Zero actual secrets in codebase"  
""  
"### 2. CI Gate Created ?"  
"- Workflow: .github/workflows/secrets-scan.yml"  
"- Runs on push/PR to main/develop"  
"- Uploads scan results as artifacts"  
""  
"### 3. Pre-commit Hook Status ??"  
"- Existing hook at .githooks/pre-commit calls groundtruth_kb secrets scan"  
"- **Gap:** groundtruth_kb module not installed in .venv"  
"- **Recommendation:** Install groundtruth-kb as editable package or update hook to use scripts/scan_secrets.py"  
""  
"### Files Created"  
"- scripts/scan_secrets.py - Standalone secrets scanner"  
"- .github/workflows/secrets-scan.yml - CI workflow"  
""  
"### Next Steps"  
"1. Fix pre-commit hook dependency (install groundtruth-kb or update hook)"  
"2. Test CI workflow on next push"  
"3. Consider adding to PR template: 'Secrets scan passed'"  
""  
## P0 Secrets Purge - Completion Summary 
