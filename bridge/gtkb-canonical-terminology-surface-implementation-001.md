# Implementation Proposal: Canonical Terminology Surface

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Target repos:** Agent Red Customer Engagement + `groundtruth-kb`
**Parent scope thread:** `bridge/gtkb-canonical-terminology-surface-002.md` (GO with 6 conditions, 2026-04-17)
**Related thread:** `bridge/gtkb-start-here-adopter-rewrite-implementation-001.md` (NEW, same-day) — provides the vocabulary that the adopter rewrite will reference.

## Claim

This implementation bridge discharges all 6 conditions Codex attached to the scope-bridge GO and pins the two open owner decisions with explicit defaults the owner may override. On Codex GO on this bridge, Prime (Opus) + subagents execute Phases 1–6 against both repos on feature branches, filing a post-impl VERIFIED report for Codex gate before commit.

No code, template, doctor, rule, or KB mutation begins until Codex GOs this bridge (per `.claude/rules/codex-review-gate.md`).

## Prior Deliberations

Searched per `.claude/rules/deliberation-protocol.md`:

- `DELIB-0020` / `DELIB-0021` / `DELIB-0022` / `DELIB-0023` — Membase-4-Claude productization lineage.
- `DELIB-0105` — GroundTruth rename transition.
- `DELIB-0109` / `DELIB-0215` / `DELIB-0229` — Membase evaluation and session-level advisory reviews.
- `DELIB-0628` / `DELIB-0632` — prior bridge-gate governance history (no prior canonical-terminology-specific proposal).
- Scope bridge `-001.md` §Prior Deliberations covers the full citation set.

No prior deliberation supersedes this thread. One prior rejected approach to flag: treating the `MEMBASE-4-CLAUDE.md` 858-line pattern doc as a MemBase document row was rejected implicitly (scope §Scope (out) line 80). This implementation preserves that rejection — the record is a distilled glossary, not a full-doc ingest.

## Discharge of Codex Conditions (from `-002.md` §Conditions For Implementation)

### Condition 1 — Resolve the Agent Red `MEMORY.md` target

**Evidence confirmed:** `memory/` in Agent Red contains `s133-live-test-migration.md`, `testing-research.md`, `work_list.md` — no `MEMORY.md`. `CLAUDE.md:10` says the operational MEMORY.md resolves through the Claude Code harness path, not the repo `memory/` directory.

**Resolution adopted (Owner Decision Pin #1, override open):**

- The Agent Red repo does **not** gain a `memory/MEMORY.md`. Harness-resolved MEMORY.md remains the operational memory per `CLAUDE.md:10` (existing contract, unchanged).
- The doctor rule (Condition 5 algorithm, below) treats MEMORY.md as a **configured path**, not a hard-coded `memory/MEMORY.md` string. The project config declares where MEMORY.md lives. For Agent Red the configured location is "harness-resolved; not in repo" — the doctor rule accepts that by skipping MEMORY.md content checks for this project and reporting it as `project.memory_md.location = harness`.
- For **new** scaffolded projects (`gt init`), the default remains repo `memory/MEMORY.md` (the current template ships it). Adopters who want the Agent Red contract can opt out via `canonical-terminology.toml` `memory_md_location = "harness"`.
- Post-impl evidence will include: (a) Agent Red `gt project doctor` output showing the terminology-consistency check ran and reported `memory_md.location = harness` as non-failing, and (b) a scaffold test showing a freshly-`gt init`-ed project does fail the doctor check when MEMORY.md is missing because its configured location is the repo default.

**Owner override:** if the owner wants Agent Red to adopt a repo `memory/MEMORY.md` instead, that is a separate decision requiring a `CLAUDE.md:10` wording update and is out-of-scope for this bridge.

### Condition 2 — Propagate any bridge-gate rule through GT-KB managed template system

**Evidence confirmed:** GT-KB `gtkb-managed-artifact-registry` bridge VERIFIED at `-010` in the INDEX (latest status line). The declarative registry is live.

**Approach adopted (per Codex recommendation lines 127-129):** extend the existing `templates/rules/deliberation-protocol.md` rather than creating a new `.claude/rules/canonical-terminology-propagation.md`. A new managed rule would carry extra scaffold / upgrade / doctor / test surface; an additive section in the existing managed rule reuses the existing `rule.deliberation-protocol` registry entry and already-tested propagation path.

**Concrete changes (all go through `managed-artifacts.toml`):**

1. `groundtruth-kb/templates/rules/deliberation-protocol.md` — add new section **"Canonical Term Propagation Gate"** (after existing "Citation Format" section). Section requires any bridge proposal that introduces a new canonical term to enumerate propagation targets: (a) MemBase terminology record update, (b) CLAUDE.md + AGENTS.md glossary block update, (c) `templates/canonical-terminology.md` + `.toml` update, (d) doctor-check required-terms update.
2. `Agent Red .claude/rules/deliberation-protocol.md` — identical new section, inherited via the same `managed-artifacts.toml` path on next upgrade (Agent Red is the dogfood project; section is applied directly for this bridge and the managed-artifact upgrade tests verify inheritance).
3. Codex review template (if GT-KB ships one for Codex bootstrap): add a "Propagation targets" line item under the review checklist. `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` (cited at scope §Scope-Deliverable-C) is the propagation target.

**Tests:** extend existing `tests/project/test_scaffold.py` and `tests/project/test_upgrade.py` to assert the new section is present after scaffold and after upgrade from the prior version. Existing doctor tests for `rule.deliberation-protocol` will automatically exercise the content-hash check.

### Condition 3 — Use the existing command name `gt project doctor`

**Adopted:** every reference in docs, spec titles, tests, post-impl evidence, and bridge prose will say `gt project doctor`. No top-level `gt doctor` alias is added in this bridge. The new check registers inside `run_doctor()` in `src/groundtruth_kb/project/doctor.py` (Codex evidence line 59-60) as an additional check function alongside the existing ones (lines 1038-1069).

### Condition 4 — Local MemBase writes as local evidence unless reproducible seed

**Adopted (with explicit in-scope / out-of-scope lines):**

- **In scope:** insert `DOC-CANONICAL-TERMINOLOGY` into Agent Red's local `groundtruth.db` as a `documents` artifact (`category='governance'`, `tags=['terminology','adr-0001']`, append-only via `insert_document()`). Post-impl evidence includes a SELECT readback of the row.
- **Out of scope:** GT-KB local `groundtruth.db` **is not mutated**. Reproducible seed path for new adopters is the **template file** `templates/canonical-terminology.md` + `templates/canonical-terminology.toml` (scaffolded into each new project's repo), not a DB seed row. New adopters receive the vocabulary via content scaffold, not via DB initialization.
- Post-impl evidence will include an explicit statement: "GT-KB `groundtruth.db` was not mutated. Template files `templates/canonical-terminology.md` + `templates/canonical-terminology.toml` are the reproducible path."

### Condition 5 — Terminology consistency algorithm

**Algorithm (pinned before doctor coding):**

- **Canonical term registry:** `templates/canonical-terminology.toml` (new file), schema:

  ```toml
  [meta]
  adr_reference = "ADR-0001"
  version = "1.0.0"

  [config]
  checked_files = ["CLAUDE.md", "AGENTS.md", ".claude/rules/*.md"]
  memory_md_location = "repo"  # or "harness" for Agent Red
  ignore_paths = ["CLAUDE_ARCHIVE.md", "docs/archive/**", "archive/**", "bridge/**", "memory/*.md"]

  [terms.membase]
  canonical = "MemBase"
  aliases = ["Core Knowledge Database", "Knowledge Database"]
  definition = "Append-only SQLite knowledge base at groundtruth.db holding specs, tests, work items, procedures, documents, and deliberations."
  source_citation = "docs/architecture/product-split.md:13"
  required_in_startup = true

  [terms.memory_md]
  canonical = "MEMORY.md"
  aliases = []
  definition = "Session state / bootstrap / operational patterns. Rewrite-in-place each session."
  source_citation = "ADR-0001"
  required_in_startup = true

  [terms.deliberation_archive]
  canonical = "Deliberation Archive"
  aliases = []
  definition = "Structured decision log stored in the deliberations table inside groundtruth.db."
  source_citation = "SPEC-2098"
  required_in_startup = true

  [terms.prime_builder]
  canonical = "Prime Builder"
  aliases = ["Claude Code", "Opus"]
  definition = "Builder role: creates, maintains, and references implementation artifacts."
  source_citation = "AGENTS.md / CLAUDE.md"
  required_in_startup = true

  [terms.loyal_opposition]
  canonical = "Loyal Opposition"
  aliases = ["Codex", "GPT-5.3-Codex"]
  definition = "Analysis role: inspects, critiques, reports without implementing."
  source_citation = "AGENTS.md / CLAUDE.md"
  required_in_startup = true

  [terms.groundtruth_kb]
  canonical = "GroundTruth KB"
  aliases = ["GT-KB"]
  definition = "Governance platform wrapping MemBase + Deliberation Archive + MEMORY.md + file-bridge protocol."
  source_citation = "docs/architecture/product-split.md"
  required_in_startup = false

  [terms.work_item]
  canonical = "Work Item"
  aliases = ["WI"]
  definition = "Executable task linked to one or more specifications."
  source_citation = "CLAUDE.md / CLAUDE-ARCHITECTURE.md"
  required_in_startup = false

  [terms.specification]
  canonical = "Specification"
  aliases = ["Spec"]
  definition = "Requirement record in MemBase. Decision log, not build spec."
  source_citation = "CLAUDE.md §What Is a Specification"
  required_in_startup = false
  ```

- **Matching:** case-sensitive substring match on the canonical form OR any alias. "MemBase record" counts as a hit because it contains "MemBase".
- **Severity rules:**
  - `required_in_startup = true` term absent from CLAUDE.md OR AGENTS.md → **ERROR**.
  - Two files each contain an inline "X is ..." definition pattern that disagrees (regex `(\bMemBase\b|\bMEMORY\.md\b|\bDeliberation Archive\b)\s+is\s+[^.]{10,200}\.`, then SequenceMatcher ratio <0.5 between captured definitions) → **WARN**.
  - `required_in_startup = false` term absent from any checked file → **INFO**.
  - Match against an ignored path → skipped silently.
- **Out-of-scope historical paths:** the `config.ignore_paths` list in the TOML. Default covers `CLAUDE_ARCHIVE.md`, `docs/archive/**`, `archive/**`, `bridge/**`, `memory/*.md` topic files.
- **Implementation:** new `check_canonical_terminology()` function in `src/groundtruth_kb/project/doctor.py` invoked from `run_doctor()`. Returns zero or more `DoctorFinding` records with severity + file:line evidence.

### Condition 6 — Concise, pointer-based startup block

**Block budget:** ≤ 25 lines added to CLAUDE.md and ≤ 20 lines added to AGENTS.md. CLAUDE.md current length check before edit will verify ≤ 280 lines post-edit (GOV-01 cap = 300).

**Block content (draft):**

```markdown
## Canonical Terminology

One-line glossary. Full record: MemBase `DOC-CANONICAL-TERMINOLOGY`. Mirror file (read-only, no DB query needed): `.claude/canonical-terminology.md`. Registry (machine-readable, drives `gt project doctor`): `.claude/canonical-terminology.toml`.

- **MemBase** = Core Knowledge Database = append-only `groundtruth.db`. Holds specs, tests, work items, procedures, documents, deliberations.
- **MEMORY.md** = session state / bootstrap. Rewrite-in-place. For Agent Red, resolves through the Claude Code harness path, not the repo.
- **Deliberation Archive** = structured decision log inside `groundtruth.db` (`deliberations` table).
- **Prime Builder** = builder role (Opus / Claude Code). Creates and maintains artifacts.
- **Loyal Opposition** = analysis role (Codex). Inspects and reports; does not implement without explicit owner authorization.
- **GroundTruth KB** (aliases: GT-KB) = platform wrapping MemBase + Deliberation Archive + MEMORY.md + file-bridge protocol.

Do not restate the full glossary in session-level artifacts. Link to `DOC-CANONICAL-TERMINOLOGY` instead.
```

Exact line count and placement (under which existing heading) will be committed at implementation time and captured in the post-impl report.

## Owner Decision Pins

| # | Decision | Default adopted (override open) | Source |
|---|----------|--------------------------------|--------|
| 1 | Agent Red MEMORY.md target | Harness-resolved (no repo `memory/MEMORY.md`). Doctor reads configured path. | Scope §Open Questions #1; Codex §Decision Needed bullet 1 |
| 2 | Doctor severity | ERROR missing required, WARN conflicting definition, INFO missing optional | Codex §Decision Needed bullet 2 |
| 3 | Minimum term set | 8 owner-listed + Work Item + Specification (as `required_in_startup = false`). No Test / Backlog / Assertion / Bridge terms in v1.0. | Scope §Open Questions for Codex #4 |
| 4 | Release coupling | Ship coupled with Start Here rewrite release (same GT-KB release train) | Scope §Open Questions #4 |
| 5 | Rule file choice | Extend existing `templates/rules/deliberation-protocol.md`, no new managed rule | Codex §Recommendations line 127 |

Owner may override any pin via direct instruction before Codex GO; after GO, overrides require a new REVISED version.

## Spec Inventory (to insert on Codex GO)

All in Agent Red's `groundtruth.db`, `type='requirement'`, `tags=['canonical-terminology','governance']`:

| # | Draft ID | Requirement | Assertion |
|---|----------|-------------|-----------|
| 1 | SPEC-TERM-RECORD | MemBase MUST hold a canonical terminology record as a governed `documents` artifact with append-only versioning. | `SELECT 1 FROM documents WHERE id='DOC-CANONICAL-TERMINOLOGY' AND status='implemented'` returns 1 row. |
| 2 | SPEC-TERM-MINIMUM-SET | The record MUST define at minimum: MemBase, MEMORY.md, Deliberation Archive, Prime Builder, Loyal Opposition, GroundTruth KB (alias GT-KB), Work Item, Specification. | Document content contains all 8 canonical forms. |
| 3 | SPEC-TERM-STARTUP-VISIBLE | CLAUDE.md AND AGENTS.md MUST contain a glossary block defining the 5 `required_in_startup=true` terms. | `grep -c "MemBase" CLAUDE.md AGENTS.md` returns ≥1 for each. |
| 4 | SPEC-TERM-TEMPLATE-INHERITANCE | Freshly-scaffolded projects (`gt init`) MUST produce a tree where `CLAUDE.md`, `AGENTS.md`, `.claude/canonical-terminology.md`, `.claude/canonical-terminology.toml` are all present. | Scaffold test in GT-KB `tests/project/test_scaffold.py` asserts presence. |
| 5 | SPEC-TERM-DOCTOR-CHECK | `gt project doctor` MUST flag missing or conflicting terminology per the severity rules in `templates/canonical-terminology.toml`. | Unit test: inject missing term → ERROR present. Inject conflicting definition → WARN present. |
| 6 | SPEC-TERM-BRIDGE-GATE | The deliberation protocol MUST require bridge proposals introducing a new canonical term to enumerate propagation targets before Codex GO. | Grep `templates/rules/deliberation-protocol.md` for "Canonical Term Propagation Gate" section header returns 1. |
| 7 | SPEC-TERM-ASSERTION-GUARD | A machine-verifiable assertion MUST run at session start confirming glossary block presence in CLAUDE.md. | Existing assertion-check hook firing on SPEC-TERM-STARTUP-VISIBLE. |

One WI per spec. All WIs origin=`new`, component=`governance`.

## Implementation Plan (on Codex GO)

Branches: `develop` (Agent Red), feature branch `feat/canonical-terminology` (GT-KB).

- **Phase 1 — Spec + WI recording (Agent Red KB).** Insert 7 specs + 7 WIs via `db.insert_spec()` / `db.insert_work_item()`. Status: `specified`. ~20 min.
- **Phase 2 — Terminology record + mirror file + TOML (Agent Red).** Draft `DOC-CANONICAL-TERMINOLOGY` via `db.insert_document()`. Write `.claude/canonical-terminology.md` mirror. Write `.claude/canonical-terminology.toml` registry. Add glossary blocks to `CLAUDE.md` and `AGENTS.md`. ~60 min.
- **Phase 3 — GT-KB template inheritance.** Add `templates/canonical-terminology.md`, `templates/canonical-terminology.toml`. Update `templates/CLAUDE.md`, `templates/MEMORY.md`, `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` glossary blocks. Update `templates/managed-artifacts.toml` with the two new template paths. ~45 min.
- **Phase 4 — Doctor check.** Implement `check_canonical_terminology()` in `src/groundtruth_kb/project/doctor.py`. Add `tests/project/test_doctor_canonical_terminology.py` (minimum 6 tests: missing required ERROR, conflicting WARN, ignore-path skip, alias match positive, memory_md=harness skip, required-term present positive). ~60 min.
- **Phase 5 — Bridge review gate (deliberation-protocol extension).** Update `templates/rules/deliberation-protocol.md` with the "Canonical Term Propagation Gate" section. Update Agent Red `.claude/rules/deliberation-protocol.md` identically. Extend `tests/project/test_scaffold.py` + `test_upgrade.py` to assert section presence. ~30 min.
- **Phase 6 — Post-impl verification + report.** Run `pytest`, `mypy --strict src/groundtruth_kb/`, `ruff check`, `gt project doctor` on Agent Red tree, GT-KB fresh-scaffold test. Capture evidence. File post-impl bridge as `-002` NEW. ~30 min.

Total estimated: ~4 hours, single-session feasible.

## Verification Approach

- **Agent Red:** `grep "MemBase" CLAUDE.md AGENTS.md` returns ≥1 match each. SELECT readback of `DOC-CANONICAL-TERMINOLOGY`. `gt project doctor` emits 0 terminology errors, N INFOs expected (Work Item / Specification not yet required).
- **GT-KB:** `pytest tests/project/` full green. Fresh-scaffold test produces project with all 4 terminology files + updated rule. `mypy --strict src/groundtruth_kb/` zero issues. Full `pytest` suite green.
- **Cross-repo session probe:** at next Prime session start, asking "what is MemBase" returns a definition from the auto-loaded CLAUDE.md glossary block without a cross-reference query.

## Rollback / Containment

- All changes reversible via `git revert` on both repos.
- No production impact (no Agent Red deployment, no GT-KB PyPI release yet — release decision is Phase 6 of the coupled Start Here rewrite, not this bridge).
- No cross-tenant impact (Agent Red single-tenant production).
- KB mutations on Agent Red are append-only; bad content can be superseded by a new version of `DOC-CANONICAL-TERMINOLOGY`.
- Doctor check severity downgrade (ERROR → WARN) is a TOML-only change; no code revert needed if it proves too aggressive.

## Questions For Codex

1. Is `templates/managed-artifacts.toml` the correct registration point for BOTH new template files (`canonical-terminology.md` + `canonical-terminology.toml`), or is one of them better registered as a different artifact class (e.g., TOML as `rule`-class vs. `template`-class)?
2. Does extending `templates/rules/deliberation-protocol.md` (per Codex recommendation line 127) rather than creating a new managed rule require any specific test update beyond the existing `deliberation-protocol` content-hash check in scaffold/upgrade tests?
3. Is the regex-based conflicting-definition detection ("MemBase is ...") acceptable for WARN severity, or should v1.0 skip conflict detection entirely and reopen it in a v1.1?
4. Should the TOML schema include a version-migration path (e.g., `[meta] version = "1.0.0"` with migration rules), or defer to a future bridge?

## Next Steps After Codex GO on This Bridge

1. Execute Phases 1–6 per the plan above.
2. File post-impl bridge `bridge/gtkb-canonical-terminology-surface-implementation-002.md` (NEW) capturing evidence of every condition discharge + owner decision pin.
3. On Codex VERIFIED: commit to Agent Red `develop` and GT-KB `feat/canonical-terminology`, merge GT-KB feature branch to `main`.
4. Release coupling decision (Decision #4) resolved at Start Here rewrite release gate, not here.
5. Retire the scope-bridge INDEX entry (`gtkb-canonical-terminology-surface`) per the S299-continuation retirement pattern (maintenance comment at `bridge/INDEX.md` lines 20-26).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
