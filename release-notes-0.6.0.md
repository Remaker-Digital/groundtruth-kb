# GT-KB v0.6.0 — Phase A Tier A Operational Skills

Release date: 2026-04-17

## Highlights

v0.6.0 is the **Phase A Tier A milestone** — GT-KB ships its first full
suite of operational governance primitives: a canonical credential-pattern
module, a Write-tool guard hook, three skills (one for owner decisions,
one for writing bridge proposals, one for requirement intake), and a
metrics collector to observe the guard hook's behavior in practice. Six
Phase A bridges represented by seven commits, all reviewed by Loyal
Opposition with evidence-based verdicts, all landed with mypy --strict
clean and `--cov-fail-under=70` green.

### What is Phase A?

Phase A is the first installment of GT-KB's operational-skills program.
The goal: make the governance primitives GT-KB already had (the
Knowledge Database, the deliberation archive, the intake pipeline)
accessible from the adopter's Claude Code session as named skills with
stable contracts, and give adopters visibility into what the guard
hooks are actually blocking.

### What's in this release

**New hook:** `scanner-safe-writer` — a PreToolUse hook that intercepts
Write tool events targeting `bridge/*.md` and blocks them if the content
matches a credential-class pattern. Emits a JSONL deny record per
block to `.claude/hooks/scanner-safe-writer.log` (schema v1, stable
interface).

**Three new skills:**

- `/gtkb-decision-capture` — record an owner decision as an append-only
  Deliberation Archive row with fixed governance metadata. Never mutates
  specs/WIs/docs.
- `/gtkb-bridge-propose` — write a bridge proposal file with credential
  pre-flight scan, overlap-safe redaction, and atomic INDEX update.
- `/gtkb-spec-intake` — capture a requirement candidate at
  `outcome="deferred"` and wait for explicit owner confirm/reject
  before writing a spec. Confirm-before-mutate contract.

**New canonical module:** `governance.credential_patterns` unifies the
credential-class regex catalog (`CREDENTIAL_PATTERNS + BASH_EXTRAS +
PII_PATTERNS`) that was previously duplicated across the DB redaction
layer and the credential-scan hook. One module = one authority.

**New script:** `scripts/collect_phase_a_metrics.py` aggregates the
scanner-safe-writer deny log and emits per-pattern / per-session /
per-date metrics in JSON (automation) or Markdown (humans). Indexes
only on stable interface fields.

**Quality track (also in this release):**

- Phase 4C: structured logging migration (`_logging.py` with split-level
  defaults; `tests/_print_guard.py` as single source of truth).
- Phase 4D: broad-exception governance (narrowed 2 sites, removed 1
  redundant handler, annotated 21 intentional catches with
  `# intentional-catch:` markers; AST-based CI gate).
- Phase 1 operational governance hooks + `source_paths` migration.

**Docs:** 30 files aligned to the ADR-0001 three-tier memory
architecture vocabulary.

## Upgrade guidance

`pip install --upgrade groundtruth-kb==0.6.0` in any venv where GT-KB
is installed. No API breakage. Existing callers of `intake.*` keep
their `"intake-pipeline"` attribution because the new `changed_by`
kwarg defaults to it.

For adopter projects scaffolded at v0.5.0 or earlier: run
`gt project upgrade --apply` to receive the three new skill files and
the updated managed hook registrations. The new `_plan_missing_managed_files`
infrastructure (landed in v0.5.0) handles missing-file repair at any
scaffold version.

## Verification evidence

- `ruff check src/ tests/ templates/` — clean
- `ruff format --check` — 127 files already formatted
- `mypy --strict src/groundtruth_kb/` — Success: no issues in 39 source files
- Full pytest suite — 1209 passed
- Wheel build — `groundtruth_kb-0.6.0-py3-none-any.whl` includes all
  three skill trees (`decision-capture`, `bridge-propose`, `spec-intake`)
  with both `SKILL.md` and helper files in each

## Commit range

`v0.5.0..v0.6.0` — 14 commits. All verified via the file-bridge
protocol with Codex Loyal Opposition review. See `CHANGELOG.md` for
the full per-feature breakdown.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
