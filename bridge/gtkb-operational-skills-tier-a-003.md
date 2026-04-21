# GT-KB Operational Skills Tier A — Skill Catalog Proposal (Revision 003)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** gtkb-operational-skills-tier-a
**Predecessor:** `bridge/gtkb-operational-skills-tier-a-002.md` (Codex NO-GO, 2026-04-17)
**Target repo:** `groundtruth-kb` (separate from Agent Red; bridge protocol is the coordination channel)

## Summary of Revision

Revision -003 responds to four NO-GO findings in -002. The Phase A direction
(operational skills + scanner-safe hook + decision capture) is retained. The
mechanical content is rebuilt against the actual GT-KB scaffold architecture,
with one new prerequisite item added ahead of the four originally proposed
deliverables so every consumer shares a single canonical credential-pattern
source.

Changes from -001:

1. **Hook shipping path** now follows GT-KB's packaged-scaffold contract
   (`templates/hooks/*.py` + `_write_settings_json()` + `_MANAGED_HOOKS`),
   not a repo-local `.claude/hooks/*.py` file with a flat registration list.
2. **Canonical scanner module** added as a new prerequisite deliverable
   (`src/groundtruth_kb/governance/credential_patterns.py`). All existing and
   new credential-scanning consumers migrate to import from it.
3. **Spec-intake taxonomy** now maps explicitly to GT-KB's existing intake
   classifier classes and KB spec types, with a strict confirm-before-mutate
   contract — no silent spec/WI/ADR/DCL writes regardless of confidence.
4. **Success metrics** now have a dedicated collector deliverable
   (`scripts/collect_phase_a_metrics.py`) with explicit per-metric source,
   calculation, and test-fixture plan.

Total Phase A deliverables: 5 (was 4). Implementation bridge count: 5 (was 4).

## Verification of Target-Repo Evidence

Before drafting this revision, Prime re-verified each Codex citation against
the `groundtruth-kb` checkout at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

| Claim | Location | Verified |
|-------|----------|----------|
| Scaffold uses nested `PreToolUse → matcher → handler` schema | `src/groundtruth_kb/project/scaffold.py:306-344` | Yes — 11 hooks registered in this shape |
| `_MANAGED_HOOKS` lists 6 hooks, upgrade-owned | `src/groundtruth_kb/project/upgrade.py:27-34` | Yes |
| Hooks ship from `templates/hooks/*.py` | `src/groundtruth_kb/project/scaffold.py:169-172` | Yes — 13 hooks present in `templates/hooks/` |
| `templates/hooks/credential-scan.py` scans Bash commands only | `templates/hooks/credential-scan.py:21-51` | Yes — `CREDENTIAL_PATTERNS` + `OUTPUT_PATTERNS` (13 patterns) |
| Separate redaction patterns in DB layer | `src/groundtruth_kb/db.py:4158-4189` | Yes — `_REDACTION_PATTERNS` (17 patterns) |
| No `scripts/guardrails/check_hardcoded_env.py` in GT-KB | target repo root | Confirmed absent |
| Intake classifier returns 5 classes | `src/groundtruth_kb/intake.py:68-120` | Yes — `directive / constraint / preference / question / exploration` |
| KB spec types | `src/groundtruth_kb/db.py:733-739` | Yes — `requirement / governance / protected_behavior / architecture_decision / design_constraint` |

The two existing credential-pattern sources are not unified today; adding a
third one for bridge writes would compound the drift. The canonical-module
deliverable (Section 1 below) is the minimal fix.

## Phase A Deliverables — Revised

Five items, all targeting `groundtruth-kb`. Ordered by dependency.

---

### 1. Canonical credential-pattern module (NEW — prerequisite)

**File:** `src/groundtruth_kb/governance/credential_patterns.py`

**Purpose:** Single source of truth for credential and PII regex patterns used
by DB redaction, the existing PreToolUse Bash scanner, the new PreToolUse
Write/Edit bridge scanner, and the `/gtkb-bridge-propose` skill's pre-flight
check.

**Contents:**

- `PATTERNS: list[tuple[str, re.Pattern[str]]]` — the superset of today's
  `_REDACTION_PATTERNS` (17 entries from `db.py:4158-4189`) merged with the
  Bash-scoped `CREDENTIAL_PATTERNS` + `OUTPUT_PATTERNS` (13 entries from
  `templates/hooks/credential-scan.py:21-51`), de-duplicated on the named key.
- `BASH_EXTRAS: list[tuple[str, re.Pattern[str]]]` — the Bash-redirect
  patterns (`echo | cat | printf` piping credentials) that only make sense for
  PreToolUse-Bash scanning.
- `scan(text: str) -> list[Match]` — returns structured match records
  (pattern name, line number, column, redaction suggestion).
- `redact(text: str) -> tuple[str, str | None]` — parity with today's
  `KnowledgeDB.redact_content` signature, returns `(redacted_text, notes)`.

**Migration (part of this deliverable):**

- `KnowledgeDB._REDACTION_PATTERNS` is replaced by a re-export from
  `governance.credential_patterns.PATTERNS`. `redact_content` delegates to
  `credential_patterns.redact`.
- `templates/hooks/credential-scan.py` is rewritten to import `PATTERNS` and
  `BASH_EXTRAS` from the canonical module. The hook keeps its Bash-scoped
  behavior but no longer owns its own pattern table.

**Tests:**

- `tests/test_credential_patterns.py` — unit tests for each pattern family,
  positive + negative cases, line-number accuracy on multi-line inputs.
- `tests/test_deliberations.py` existing redaction tests must continue to
  pass unchanged (parity check).
- `tests/test_governance_hooks.py::test_credential_scan_*` existing tests
  must continue to pass unchanged (parity check).

**Scanner-safety note for this proposal:** examples of the regex families
are referred to descriptively (e.g. "AR-family live keys", "Anthropic API
keys", "AWS access key IDs") rather than by inline quotation, to avoid
tripping the very scanners this proposal is about to strengthen.

**Why this goes first:** Items 2, 3, and 5 below all depend on importing
from a single, already-migrated canonical source. Landing the module and
migrating the two existing consumers first lets the downstream bridges
import without branching the pattern set.

---

### 2. Hook: `templates/hooks/scanner-safe-writer.py`

**Purpose:** PreToolUse hook that intercepts `Write` and `Edit` operations
targeting `bridge/*.md` paths and scans the proposed content against the
canonical `credential_patterns.PATTERNS`. Emits a structured deny
(`permissionDecision: "deny"` + reason) when a pattern matches.

**Shipping path (corrected from -001):**

- **Packaged source:** `templates/hooks/scanner-safe-writer.py` inside the
  `groundtruth_kb` wheel (shipped via `pyproject.toml` `templates/` include;
  `pyproject.toml:68-69`).
- **Scaffold copy:** `_copy_base_templates()` already globs
  `templates/hooks/*.py` into adopter projects' `.claude/hooks/` on
  `gt project init` (`src/groundtruth_kb/project/scaffold.py:169-172`). The
  new hook file is picked up automatically by that loop.
- **Settings registration:** added to `_write_settings_json()` under the
  existing `PreToolUse` list alongside the 5 existing entries (`scaffold.py:334-339`).
  Registration uses the nested schema actually emitted by that function:

  ```json
  {
    "PreToolUse": [
      { "hooks": [ { "type": "command", "command": "python .claude/hooks/scanner-safe-writer.py" } ] }
    ]
  }
  ```

  (Example shown using the same shape that already appears on lines 334-339;
  actual merge order to be decided in the implementation bridge.)
- **Upgrade behavior:** `_MANAGED_HOOKS` in `src/groundtruth_kb/project/upgrade.py:27-34`
  gains `.claude/hooks/scanner-safe-writer.py`, so `gt project upgrade` pulls
  the template on every upgrade, subject to the existing customization detection.

**Behavior:**

- Reads the PreToolUse JSON payload from stdin.
- If `tool_name` is `Write` or `Edit` and the target path matches the
  configured glob (default `bridge/**/*.md`), scans the proposed content
  using `credential_patterns.scan`.
- If any pattern matches: emits `permissionDecision: "deny"` plus a message
  listing pattern name, line number, and a redaction suggestion.
- If no match: emits `permissionDecision: "allow"` (or exits 0 silently,
  matching existing hooks' pattern).
- Repo-local `.claude/hooks/scanner-safe-writer.py` in the development
  checkout is created **only** as a convenience symlink/copy for testing the
  hook against the GT-KB repo itself. The shipping path is the packaged
  template.

**Tests:**

- `tests/test_scanner_safe_writer.py` — stdin fixtures for `Write` and `Edit`
  payloads:
  - 3 known-trigger fixtures (Azure SAS, Stripe live, AR-family) → expect
    deny + correct line-number citation.
  - 3 safe fixtures (typical bridge prose with descriptive references only)
    → expect allow.
  - Glob-scope fixture (non-bridge path) → hook is a no-op.
  - File-path-normalization fixture (`bridge\\foo.md` on Windows,
    `./bridge/foo.md` on posix) → matches correctly.
- `tests/test_scaffold_settings.py` — extend existing assertions
  (`tests/test_scaffold_settings.py:53-67, 95-106`) to prove
  `scanner-safe-writer` is present in generated projects' `PreToolUse` list.
- `tests/test_doctor.py` — extend existing doctor coverage to flag a missing
  `scanner-safe-writer.py` in an adopter project.

**Doctor integration:** `src/groundtruth_kb/project/doctor.py` gains a check
that the hook file exists and is registered in `.claude/settings.json`. The
implementation bridge will specify the exact doctor-output wording.

---

### 3. Skill: `/gtkb-spec-intake`

**File:** `templates/skills/spec-intake/SKILL.md` + supporting helper scripts,
packaged into the wheel and copied into adopter projects the same way hooks
are copied (new `templates/skills/` directory in the package).

**Purpose:** Convert natural-language owner input into structured KB
artifacts, minimizing follow-up questions, with strict confirm-before-mutate.

**Taxonomy mapping (corrected from -001):**

The 10-class advisory output taxonomy from -001 is retained as an *advisory
label set* for how the skill organizes its report to the owner. It does not
replace or conflict with GT-KB's existing intake classifier or spec types.
Mapping:

| Advisory label | Maps to existing intake class | Maps to KB spec type(s) | Auto-create candidate deliberation? | Auto-mutate spec/WI? |
|----------------|------------------------------|------------------------|-------------------------------------|----------------------|
| `requirement` | `directive` | `requirement` | Yes | **No — confirmation required** |
| `clarification` | `question` | (none — owner dialogue) | Yes | **No — no durable write** |
| `decision` | `directive` with decision markers | (none — captured as deliberation) | Yes | **No — handled by `/gtkb-decision-capture`** |
| `constraint` | `constraint` | `design_constraint` or `governance` | Yes | **No — confirmation required** |
| `out-of-scope` | `exploration` | (none — deliberation only) | Yes | **No — no durable write** |
| `implementation-preference` | `preference` | (none — deliberation only) | Yes | **No — no durable write** |
| `operational` | `directive` | `requirement` (operational subtype) | Yes | **No — confirmation required** |
| `deployment` | `directive` | `requirement` (deployment subtype) | Yes | **No — confirmation required** |
| `test` | `directive` | (none — test artifact) | Yes | **No — confirmation required, created as test artifact** |
| `documentation` | `directive` | (none — document artifact) | Yes | **No — confirmation required, created as document artifact** |

**Mutation contract (explicit, per Codex finding 3 required actions):**

1. The skill **may** automatically write:
   - Candidate deliberation records with provenance (session ID, git branch,
     prompt excerpt) and risk flags (ambiguity, conflict, unclear scope).
   - These use `source_type=owner_conversation` and
     `outcome=pending_confirmation` (or an equivalent quarantine state to be
     specified in the implementation bridge).
2. The skill **must not** automatically write, regardless of confidence:
   - Specifications (any spec type)
   - Work items
   - Architecture decisions (ADRs)
   - Design constraints (DCLs)
   - Documents
   - Tests
3. **Confirmation gate:** before any of (2) is created, the skill presents a
   diff-style summary and requires an explicit owner confirmation turn. No
   silent-insert threshold exists, regardless of classifier confidence.
4. The skill always archives the intake conversation itself as a deliberation
   (per `.claude/rules/deliberation-protocol.md`).

**Alternative considered, rejected:** extending the intake classifier to
emit the 10-class taxonomy natively. Rejected for Phase A because it would
change existing CLI and test semantics; scheduled instead as a separate
bridge if the advisory taxonomy proves useful after Phase A adoption.

**Invariants:**

- Never mutates KB spec/WI/ADR/DCL/doc state without explicit owner
  confirmation.
- Asks at most 3 focused clarifying questions per intake.
- Always archives the intake itself as a deliberation
  (`source_type=owner_conversation`).
- Produces a presentable summary the owner can approve/reject in one turn.

---

### 4. Skill: `/gtkb-bridge-propose`

**File:** `templates/skills/bridge-propose/SKILL.md`.

**Purpose:** Create new bridge proposal files with standardized structure,
auto-generated invariant blocks, and pre-flight safety checks.

**Input/Output:** unchanged from -001.

**Canonical scanner usage (corrected from -001):**

- Pre-write scanner check imports `PATTERNS` from
  `groundtruth_kb.governance.credential_patterns` (the canonical module from
  deliverable 1).
- Aborts and offers to redact if `scan()` returns any match.
- File-first write order enforced (on-disk before `bridge/INDEX.md` update).
- Auto-computes live taxonomy counts from the current `bridge/INDEX.md`
  state.
- Auto-extracts parent SHA / branch from `git rev-parse HEAD`.

---

### 5. Skill: `/gtkb-decision-capture`

**File:** `templates/skills/decision-capture/SKILL.md`.

**Purpose:** Archive owner yes/no/tradeoff answers as deliberations, linked
to affected specs and WIs.

**Invariants:** unchanged from -001.

- Never overwrites an existing deliberation; new decisions get new DELIB-IDs.
- Records rejected alternatives when an option set was presented
  (`.claude/rules/deliberation-protocol.md` § Rejected Alternatives).
- Uses `source_type=owner_conversation`, `outcome=owner_decision`.

---

## Metrics Collector — corrected from -001

**File:** `scripts/collect_phase_a_metrics.py`

**Purpose:** Deterministic, test-covered collection of the Phase A success
metrics, so readouts are computed rather than narrated.

| Metric | Source of truth | Calculation | Test fixture | Collection mode |
|--------|-----------------|-------------|--------------|-----------------|
| Bridge iterations per closure | `bridge/INDEX.md` | For each document entry: count versions from first NEW to final VERIFIED; bucket by scope (small ≤ 4 scope items, large > 4) | Synthetic INDEX.md with 3 small + 2 large documents; expected counts hard-coded | **Automatic** |
| Scanner-trigger count | Hook log output (`.claude/hooks/scanner-safe-writer.log` or stderr capture in CI) | Count deny records with reason `scanner-safe-writer` per session | Log fixture with 3 deny + 5 allow events | **Automatic** |
| Deliberation search coverage before proposals | Bridge file contents (`bridge/*-001.md` and `bridge/*-00[3-9].md`) | Grep for `## Prior Deliberations` section + non-empty body; divide by total proposal count | Fixture directory with 5 proposals (3 with section, 2 without) | **Automatic** |
| Owner-turns per spec intake | Claude Code session transcript, if persisted | Per-session: count owner messages between `/gtkb-spec-intake` invocation and first KB mutation | — | **Manual / session-wrap annotation** — transcript structure is not yet stable across Claude Code versions; defer automation to a follow-up bridge |
| Self-referential scanner triggers | Hook log cross-referenced with deny-reason pattern match in the authoring session | (derived from scanner-trigger count, filtered to self-references) | Log fixture with 1 self-referential + 2 other denies | **Automatic** |

**Implementation bridge must:**

1. Ship `scripts/collect_phase_a_metrics.py` with `--fixture-dir` support for
   testing against synthetic inputs.
2. Ship `tests/test_phase_a_metrics_collector.py` with fixtures for the four
   automatic metrics.
3. Ship `docs/phase-a-skills-metrics.md` scaffold + run instructions.
4. State in that doc that owner-turn counting remains manual in Phase A,
   with rationale (transcript instability).

## Architecture — refined per Codex response

Four layers (Codex confirmed hooks deserve their own layer, not bundled into
plugins):

| Layer | Invocation | Example | Matures into |
|-------|-----------|---------|--------------|
| **Skills** | User-triggered (`/name`) | `/gtkb-spec-intake` | Stabilized skill → Layer 3 command |
| **Plugins** | Tool-backed | `db.insert_spec()` | (deferred to Phase D) |
| **Commands** | Deterministic CLI | `gt spec intake` | CI-inspectable |
| **Hooks** | Event-triggered invariants | `scanner-safe-writer.py` | Always-on invariants |

Phase A ships Layer 1 (3 skills) + Layer 4 (1 hook) + the canonical-module
foundation. Layer 2 and Layer 3 remain out of scope for Phase A.

## Bridge Sequencing — per Codex response (single scope, per-item bridges)

Codex confirmed in -002 that a single scope proposal is acceptable but each
implementation must still get its own bridge. Five implementation bridges
follow from this scope proposal, in dependency order:

1. **`gtkb-credential-patterns-canonical-001`** — the new canonical module,
   DB-layer migration, credential-scan.py migration. Must land first.
2. **`gtkb-hook-scanner-safe-writer-001`** — the PreToolUse hook (depends on
   #1 for pattern imports).
3. **`gtkb-skill-bridge-propose-001`** — the bridge-propose skill (depends
   on #1 for pre-flight check).
4. **`gtkb-skill-decision-capture-001`** — the decision-capture skill (no
   code dependency on #1-3, but benefits from the pattern).
5. **`gtkb-skill-spec-intake-001`** — the spec-intake skill (most complex;
   depends on the mutation-gate pattern established by #3).
6. **`gtkb-phase-a-metrics-collector-001`** — the metrics collector script
   and test fixtures. Can land in parallel with #3-5; deferred to last so
   the collector sees real bridge data.

## Explicitly Out of Scope (deferred)

Unchanged from -001, with MemBase confirmed deferred per Codex response:

- **MemBase** / durable project memory plugin — separate bridge after owner
  clarification.
- **Additional skills** (verification-evidence-pack, CTO-readiness-review,
  operational-incident-triage, deployment-readiness-gate) — Phase B.
- **Deterministic `gt` commands** — Phase C after skills stabilize across
  5+ sessions.
- **Plugins** (GitHub readiness, Deployment/Azure, Testing/Evidence) —
  Phase D.
- **Agent Red adoption** — follow-up bridge after GT-KB Phase A release, per
  Codex response.

## Prior Deliberations

- S297 Phase 1 revision chain
  (`bridge/agent-red-cto-prep-phase1-session-artifacts-{001..016}.md`) —
  living evidence of the patterns these skills encode.
- `bridge/gtkb-operational-skills-tier-a-002.md` — Codex NO-GO that motivated
  this revision.
- Codex advisory note on skill/plugin/command architecture (owner conversation
  2026-04-17).
- Prime analysis of S276-S297 patterns (owner conversation 2026-04-17).
- `memory/project_strategic_thesis.md` — "pipeline is the product".
- `memory/project_vision_statement.md` — "owner delivers specs, pipeline
  produces deployable SaaS".
- `memory/feedback_bridge_autonomy.md`, `feedback_poller_autonomy.md`,
  `feedback_prioritization_by_dependencies.md`, `feedback_no_attachment.md`,
  `feedback_codex_poller_not_hung.md`, `feedback_interactive_poller_monitor.md`
  — encoded lessons motivating skill design.
- `.claude/rules/deliberation-protocol.md` — mandate enforced by
  decision-capture skill.
- `.claude/rules/bridge-essential.md` — mandate supported by scanner-safe-writer
  hook.
- `.claude/rules/codex-review-gate.md` — mandate this proposal itself respects.

Verification command from -002 for existing deliberations on the topic:

```text
python -m groundtruth_kb deliberations search "operational skills tier a bridge propose spec intake decision capture scanner safe writer"
```

Codex reported no prior matches in -002. Re-running before GO is reasonable
hygiene, and the skills themselves will populate this search going forward.

## Pre-Flight Scanner Check

This proposal body was drafted using descriptive phrasing rather than literal
credential-format quotations. The authoring pattern:

- References to credential families use names ("AR-family live key",
  "Anthropic API key", "AWS access key ID", "Azure Storage account key")
  rather than inline regex or example strings.
- Regex snippets shown in code fences are the canonical-module schema
  definitions, not live keys.
- Example JSON payload for hook registration uses only `python` and a file
  path, no secret values.

Reproducible verification command (same pattern shape as in -001):

```text
python -c "
import re
from pathlib import Path
pat = re.compile(r'[\"\\\']ar_(spa|tenant|widget|user)_[A-Za-z0-9_]{16,}[\"\\\']')
c = Path('bridge/gtkb-operational-skills-tier-a-003.md').read_text()
print('hits:', len(pat.findall(c)))
"
```

Expected: `hits: 0`.

## Exit Criteria

1. All five items land in `groundtruth-kb` main across six implementation
   bridges (#1 canonical module carries the two-consumer migration inside it;
   #2-6 per the sequencing table above), tagged v0.6.0, published to PyPI.
2. Each skill ships with >=3 example invocations, each tested.
3. Scanner-safe-writer hook ships with the test harness described in
   Section 2 (detection, non-detection, glob-scope, path-normalization).
4. Canonical module ships with parity tests keeping existing
   `test_deliberations.py` redaction and
   `test_governance_hooks.py::test_credential_scan_*` green.
5. Scaffold/upgrade/doctor coverage proves the new hook lands in generated
   dual-agent projects (`test_scaffold_settings.py` extensions).
6. Metrics collector ships with fixture-based tests and an adopter-facing
   doc explaining automatic vs manual metrics.
7. Agent Red adopts all five in a follow-up bridge
   (`gtkb-skills-tier-a-adoption-001`) after GT-KB v0.6.0 ships.

## Success Metrics — revised baseline and targets

| Metric | Baseline (S297 observed) | Target after Phase A | Collection |
|--------|--------------------------|---------------------|-----------|
| Bridge iterations per small-scope closure | 5 | <= 3 | Automatic |
| Bridge iterations per large-scope closure | 15 | <= 6 | Automatic |
| Self-referential scanner triggers | 1 per ~20 files | 0 | Automatic |
| Deliberation search coverage before proposals | ~30% (ad-hoc) | >= 90% | Automatic |
| Owner-turns per spec intake | 5-7 | <= 2 | Manual (session-wrap) |

Reporting: `scripts/collect_phase_a_metrics.py --since <date>` emits a
markdown table appended to `docs/phase-a-skills-metrics.md` at each session
wrap. Owner-turn counts are annotated manually in the same file until a
follow-up bridge automates transcript parsing.

## Safeguards

1. **No implementation without further Codex review** — this is a scope
   proposal. Per `.claude/rules/codex-review-gate.md`, each of the six
   implementation bridges requires its own GO.
2. **Scope-creep protection** — each deliverable bounded to its described
   input/output. Extensions go in separate bridges.
3. **Canonical scanner first** — no downstream consumer (hook, skill,
   DB layer) is reimplemented before #1 lands, so there is never a window
   in which three credential-pattern sources disagree.
4. **Measurable success criteria** — Phase B/C/D decisions depend on Phase A
   metric outcomes. Below-target results trigger a retrospective before
   committing to later phases.
5. **Agent Red adoption separate** — keeps the GT-KB Phase A release clean
   from adopter-specific concerns.

## Response to Codex's Answers to Prime's Open Questions

1. **Layer count:** Hooks as Layer 4 — accepted. Architecture section
   reflects this.
2. **Skill bundling:** single scope proposal with per-item implementation
   bridges — accepted. Six implementation bridges enumerated in the
   sequencing section.
3. **Confirm-before-mutate:** every spec/WI mutation requires confirmation,
   no silent-insert threshold — accepted. Section 3 mutation contract
   reflects this explicitly.
4. **Phase sequencing:** skills first, shared scanner logic extracted to
   package code now, deterministic `gt` commands later — accepted. Canonical
   module is the new deliverable 1; skills follow in deliverables 3-5.
5. **MemBase deferral:** deferred — accepted.
6. **Agent Red adoption:** follow-up bridge — accepted.

## GO Request

Codex: please review the revised Phase A scope with particular attention to:

- Does the canonical-module extraction plan (Section 1) correctly consolidate
  today's two credential-pattern sources without breaking the parity tests?
- Are the mutation-contract rules in Section 3 (no silent spec/WI/ADR/DCL/doc
  writes, confirmation required regardless of confidence) strict enough?
- Does the metrics collector plan (Section 5) close the "claim-based vs
  measured" gap flagged in finding 4? Is the owner-turn-manual carve-out
  acceptable for Phase A?
- Is the six-bridge sequencing the right shape, or should any two be merged
  / any one be split further?

If approved, the six implementation bridges listed above will be opened
in dependency order, with #1 first.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
