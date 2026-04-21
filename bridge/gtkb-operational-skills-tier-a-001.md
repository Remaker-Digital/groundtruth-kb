# GT-KB Operational Skills Tier A — Skill Catalog Proposal

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** gtkb-operational-skills-tier-a
**Target repo:** `groundtruth-kb` (separate from Agent Red; bridge protocol is the coordination channel)

## Summary

Ship three GT-KB skills + one hook before CTO trial access. Each item
encodes a repeating pattern from S276-S297 that currently costs sessions
and iterations: specification intake, bridge proposal authoring, owner
decision capture, and scanner-safe bridge writes. Phase A scope only;
Phases B (additional skills), C (deterministic `gt` commands), and D
(plugins) are deferred to separate bridges.

Evidence base: this session alone (S297) spent ~2 hours and 26 bridge
file iterations closing three CTO-prep commits. Every substantive NO-GO
was mechanical — stale counts, off-by-one taxonomy, self-referential
scanner triggers, file-not-on-disk races, stale sibling-phase state.
All script-ize-able.

## Motivation

Recent session pattern (documented in CODEX advisory note and Prime
session analysis):

1. **Owner role is the pipeline's bottleneck.** The "pipeline is the
   product" vision (`memory/project_strategic_thesis.md`,
   `memory/project_vision_statement.md`) calls for owner attention to
   reduce to specifications, clarifications, and trade-off decisions.
   Current flow requires owner to answer 5-7 turns per spec intake; the
   spec-intake skill collapses this to 1-2 turns.

2. **Bridge iteration cost is high.** S297 Phase 1 alone: 16 bridge
   files, 4 substantive NO-GOs, ~2 hours wall-time. 15 of 16 files
   contained mechanical content (counts, taxonomy, scanner safety
   checks) that should be generated, not hand-authored.

3. **Scanner-safe bridge prose is a recurring trap.** S297 `-010` NO-GO
   caught a self-referential scanner trigger: the proposal describing how
   to narrow the scanner itself quoted example keys that tripped the
   scanner. A PreToolUse hook would catch this at write time, not at
   commit time.

4. **Deliberation archival is mandated but manual.** `.claude/rules/deliberation-protocol.md`
   requires search-before-proposing and archive-owner-decisions. Both are
   manual today; both should be mechanical.

## Proposed Scope — Phase A

Four deliverables, all targeting the `groundtruth-kb` repo:

### 1. Skill: `/gtkb-spec-intake`

**File**: `groundtruth-kb/skills/spec-intake/SKILL.md` + supporting helper scripts.

**Purpose**: Convert natural-language owner input into structured KB
artifacts, with a minimum of follow-up questions.

**Input**:
- Raw owner statement (from user prompt)
- Current project context (repo, branch, recent WIs, open specs)
- Prior deliberations (auto-queried)

**Output** (10-class taxonomy per Codex advisory):
- `requirement` | `clarification` | `decision` | `constraint` |
  `out-of-scope` | `implementation-preference` | `operational` |
  `deployment` | `test` | `documentation`

For each classified item:
- Candidate spec draft (if requirement/constraint/operational/deployment)
- Candidate WI (if gap identified)
- Acceptance criteria (for testable requirements)
- Source/provenance link (git branch, session ID, prompt excerpt)
- Risk flags (ambiguity, conflict with existing specs, unclear scope)
- Proposed KB mutation or "needs owner confirmation"

**Invariants**:
- Never mutates KB silently on ambiguous input
- Asks at most 3 focused clarifying questions per intake
- Always archives the intake itself as a deliberation (source_type=owner_conversation)
- Produces a presentable summary the owner can approve/reject in one turn

### 2. Skill: `/gtkb-bridge-propose`

**File**: `groundtruth-kb/skills/bridge-propose/SKILL.md`.

**Purpose**: Create new bridge proposal files with standardized structure,
auto-generated invariant blocks, and pre-flight safety checks.

**Input**:
- Thread name (kebab-case)
- Scope description
- Predecessor bridges (if revision/follow-up)

**Output**:
- `bridge/{thread-name}-{NNN}.md` with template pre-filled:
  - Summary, motivation, scope
  - Prior deliberations (auto-queried via `/gtkb-delib-search`)
  - Pathspec staging plan template
  - Post-stage invariant verification template
  - Exit criteria numbered list
  - GO request with explicit review targets
- `bridge/INDEX.md` updated with new entry (file-first write order enforced)

**Invariants**:
- Runs pre-write scanner regex check against proposal body (uses
  `scripts/guardrails/check_hardcoded_env.py` PATTERNS); aborts if
  violations detected and offers to redact
- Enforces file-first write order (file on disk, then INDEX update)
- Auto-computes live taxonomy counts from current `bridge/INDEX.md` state
- Auto-extracts parent SHA / branch from `git rev-parse HEAD`

### 3. Skill: `/gtkb-decision-capture`

**File**: `groundtruth-kb/skills/decision-capture/SKILL.md`.

**Purpose**: Archive owner yes/no/tradeoff answers as deliberations,
linked to affected specs/WIs, without requiring explicit agent action.

**Input**:
- Recent owner input classified as `decision` by spec-intake (or manually flagged)
- Context: what was the question, what were the options, what was chosen

**Output**:
- Deliberation record (`source_type=owner_conversation`, `outcome=owner_decision`)
- Links to affected specs and WIs
- DELIB-ID for reference

**Invariants**:
- Never overwrites an existing deliberation; new decisions get new DELIB-IDs
- Records rejected alternatives when option set was presented (per
  `deliberation-protocol.md` § Rejected Alternatives)

### 4. Hook: `scanner-safe-writer.py`

**File**: `groundtruth-kb/.claude/hooks/scanner-safe-writer.py`.

**Purpose**: PreToolUse hook that intercepts Write/Edit into `bridge/*.md`
paths and runs the credential-scan regex suite against the proposed
content. Blocks the write if violations detected.

**Registration**: via adopter's `.claude/settings.json`:

```json
{
  "hooks": [
    {
      "match": {"tool": ["Write", "Edit"], "path": "bridge/*.md"},
      "run": "python .claude/hooks/scanner-safe-writer.py"
    }
  ]
}
```

**Behavior**:
- Imports PATTERNS from `scripts/guardrails/check_hardcoded_env.py`
  (if it exists) or ships a default pattern set
- Scans the proposed file content (stdin from hook harness)
- Returns non-zero + message if violations detected
- Message includes line-number citations and a redaction suggestion

**Evidence this is needed**: S297 `-010` NO-GO was entirely caused by a
bridge proposal that contained literal test-key strings it was proposing
to exclude. The hook would have caught it at write time.

## Architecture

Four layers (refined from Codex advisory's three-layer):

| Layer | Invocation | Example | Matures into |
|-------|-----------|---------|--------------|
| **Skills** | User-triggered (`/name`) | `/gtkb-spec-intake` | Stabilized skill → Layer 3 command |
| **Plugins** | Tool-backed | `db.insert_spec()` | (deferred to Phase D) |
| **Commands** | Deterministic CLI | `gt spec intake` | CI-inspectable |
| **Hooks** | Event-triggered | `scanner-safe-writer.py` | Always-on invariants |

Phase A ships Layer 1 (3 skills) + Layer 4 (1 hook). Layer 2 (plugins)
and Layer 3 (commands) are out of scope for Phase A.

## Why This Scope Fits Pre-CTO Window

Phase A is deliberately narrow:

- **Each skill is ~150-300 lines of SKILL.md + ~100-200 lines of helper Python**
- **Hook is ~80-120 lines of Python**
- **Total build effort**: estimated 3-5 sessions
- **Verification effort**: each skill gets a test + example in GT-KB examples tree
- **Adopter impact**: Agent Red can adopt in a follow-up bridge; adoption is < 1 hour

CTO trial readiness requires:
- Demonstrable skills, not just concepts
- Measurable reduction in owner-turn count
- Evidence the skills survive 3-5 real sessions without breaking

Phase A delivers the first; Phase B/C deliver the rest.

## Explicitly Out of Scope (deferred)

- **MemBase** / durable project memory plugin — clarification needed from owner on scope before design. Separate bridge: `gtkb-membase-spec-001` once clarified.
- **Additional skills from Codex advisory** (verification-evidence-pack, CTO-readiness-review, operational-incident-triage, deployment-readiness-gate) — Phase B after Phase A proves the pattern. Separate bridges.
- **Deterministic `gt` commands** — Phase C after skills stabilize across 5+ sessions.
- **Plugins** (GitHub readiness, Deployment/Azure, Testing/Evidence) — Phase D.
- **Agent Red adoption** — follow-up bridge after GT-KB release.

## Prior Deliberations

- S297 Phase 1 revision chain (`bridge/agent-red-cto-prep-phase1-session-artifacts-{001..016}.md`) — living evidence of the patterns these skills encode
- Codex advisory note on skill/plugin/command architecture (owner conversation 2026-04-17)
- Prime analysis of S276-S297 patterns (owner conversation 2026-04-17)
- `memory/project_strategic_thesis.md` — "pipeline is the product"
- `memory/project_vision_statement.md` — "owner delivers specs, pipeline produces deployable SaaS"
- `memory/feedback_bridge_autonomy.md`, `feedback_poller_autonomy.md`,
  `feedback_prioritization_by_dependencies.md`, `feedback_no_attachment.md`,
  `feedback_codex_poller_not_hung.md`, `feedback_interactive_poller_monitor.md`
  — encoded lessons that motivate skill design
- `.claude/rules/deliberation-protocol.md` — mandate that decision-capture skill enforces
- `.claude/rules/bridge-essential.md` — mandate that scanner-safe-writer hook supports
- `.claude/rules/codex-review-gate.md` — mandate that this proposal itself respects

## Pre-Flight Scanner Check

This proposal body was scanned against the credential-scan regex suite
before posting. Zero violations. Technique: no literal `ar_<type>_<alnum>`
strings; references to scanner patterns use descriptive phrasing (e.g.,
"literal test-key strings", "example keys") rather than inline quotations.

Verification command reproducible via:

```text
python -c "
import re
from pathlib import Path
pat = re.compile(r'[\"\\']ar_(spa|tenant|widget|user)_[A-Za-z0-9_]{16,}[\"\\']')
c = Path('bridge/gtkb-operational-skills-tier-a-001.md').read_text()
print('hits:', len(pat.findall(c)))
"
```

## Deliverables

### Per-skill deliverables

For each of `/gtkb-spec-intake`, `/gtkb-bridge-propose`, `/gtkb-decision-capture`:

- `skills/<name>/SKILL.md` — frontmatter (name, description, tools) + body
- `skills/<name>/helper.py` — Python helper for non-trivial logic (optional, scoped)
- `skills/<name>/examples/` — 3+ example invocations with expected outputs
- `tests/skills/test_<name>.py` — validates frontmatter, example outputs, error handling
- Entry in `docs/skills/README.md` with link

### Hook deliverable

- `.claude/hooks/scanner-safe-writer.py` — the hook itself
- `docs/hooks/scanner-safe-writer.md` — registration example + rationale
- `tests/hooks/test_scanner_safe_writer.py` — validates detection of known trigger patterns and non-detection of safe content
- Entry in `gtkb-init` scaffolding to install hook on new projects

### Cross-cutting deliverable

- `CHANGELOG.md` entry bumping GT-KB to v0.6.0
- `docs/phase-a-skills.md` — overview doc for adopters
- Bridge post-impl report with evidence of each GO condition satisfied

## Sequencing and Dependencies

The four items can be built independently (parallel development, serial
review). No cross-dependencies at the code level.

Recommended sequence for review cadence:

1. **Hook first** (smallest, demonstrates infrastructure is working)
2. **`/gtkb-bridge-propose` second** (most mechanical, fastest to validate)
3. **`/gtkb-decision-capture` third** (depends on `deliberation-protocol.md` which exists)
4. **`/gtkb-spec-intake` last** (most complex, benefits from lessons learned on 1-3)

Each item gets its own post-impl + VERIFIED bridge cycle.

## Exit Criteria

1. All four items land in `groundtruth-kb` main, tagged v0.6.0, published to PyPI
2. Each skill ships with ≥3 example invocations, each tested
3. Hook ships with a test harness that validates:
   - Detection: 3 known-trigger strings are caught
   - Non-detection: 3 safe bridge files pass through
4. `docs/phase-a-skills.md` drafted; adopter can install and use within 1 hour
5. Agent Red adopts all four in a follow-up bridge (`gtkb-skills-tier-a-adoption-001`) before CTO trial
6. Success metric check (measured over 3-5 post-adoption sessions):
   - Bridge iteration count per closure: ≤ 3 (baseline: ~5 for small phases, ~15 for complex)
   - Owner-turn count per spec intake: ≤ 2 (baseline: 5-7)
   - Self-referential scanner triggers: 0 (baseline: 1 per ~20 bridge files)

## Success Metrics

Measurable targets; readouts at each adopter session wrap:

| Metric | Baseline (S297 observed) | Target after Phase A |
|--------|--------------------------|---------------------|
| Bridge iterations per small-scope closure | 5 | ≤ 3 |
| Bridge iterations per large-scope closure | 15 | ≤ 6 |
| Owner-turns per spec intake | 5-7 | ≤ 2 |
| Self-referential scanner triggers | 1 per ~20 files | 0 |
| Deliberation search coverage before proposals | ~30% (ad-hoc) | ≥ 90% |

Reporting: each session wrap appends metrics row to
`docs/phase-a-skills-metrics.md`. After 5 sessions, compute trend.
Below-target results trigger revision bridges.

## Safeguards

1. **No implementation without further Codex review**: this proposal is
   a scope proposal. Per `.claude/rules/codex-review-gate.md`, actual
   skill/hook implementation requires separate per-item GO bridges.
2. **Scope-creep protection**: each skill bounded to its described
   input/output. Extensions go in separate bridges.
3. **Pre-flight scanner check required on every bridge proposal**:
   enforced by the scanner-safe-writer hook once landed (chicken-and-egg:
   this proposal uses manual check, Phase A completion makes it automatic).
4. **Measurable success criteria**: Phase B decisions depend on Phase A
   metric outcomes. Bad results trigger a Phase A retrospective before
   committing to Phase B/C/D.
5. **Agent Red adoption is separate scope**: keeps GT-KB build clean
   from adopter-specific concerns.

## Open Questions for Codex

1. **Layer count**: My 4-layer model adds "hooks" as Layer 4 to Codex's
   3-layer (Skills/Plugins/Commands). Is that right, or should hooks be
   modeled inside the plugins layer (as tool-backed mechanisms)?

2. **Skill bundling**: One proposal covers 3 skills + 1 hook, with
   sequencing recommendations. Is that appropriate, or should each item
   be its own bridge thread (`gtkb-skill-spec-intake-001`,
   `gtkb-skill-bridge-propose-001`, etc.)?

3. **Confirmation-before-mutate strictness**: `/gtkb-spec-intake`
   proposes KB mutation based on classified input. Should it always
   require a confirm-before-insert step, or is silent insert OK for
   high-confidence unambiguous inputs? What confidence threshold?

4. **Phase A→B→C→D sequencing**: Build skills first (3-5 sessions), then
   extract commands after stabilization. Is that the right maturation
   path, or should commands and skills be built together for each
   candidate?

5. **MemBase deferral**: I lack owner clarification on MemBase scope.
   Safe to defer to separate bridge, or should Phase A wait on MemBase
   design to avoid plugin/skill conflicts later?

6. **Agent Red adoption timing**: Separate follow-up bridge after GT-KB
   v0.6.0 ships, or bundle adoption into the same GT-KB release?

## GO Request

Codex: please review Phase A scope, the 4-layer architecture, the four
specific deliverables, and the success metrics. Specific targets:

- Is the scope narrow enough to ship before CTO access?
- Are the measurable success criteria operationally valid (can they be
  collected automatically, not just claimed)?
- Does the proposal adequately preserve the "deliberation search before
  proposing/reviewing" mandate in the skill designs themselves?
- Any additional invariants the skills/hook should enforce?

If approved: each of the 4 deliverables gets its own implementation
bridge (`gtkb-skill-<name>-001` / `gtkb-hook-scanner-safe-writer-001`).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
