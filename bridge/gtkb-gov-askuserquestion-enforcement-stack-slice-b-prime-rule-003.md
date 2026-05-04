REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice B: Prime Builder Rule Formalizing AUQ-Only Decision Channel (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice B of GTKB-GOV-AUQ-ENFORCEMENT-STACK
**Mechanism:** 1
**Risk tier:** Low

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-002.md` — F1 (acting-prime-builder.md test coverage was heading-only; missed parity with prime-builder-role.md substance assertions) and F2 (decision-class grep used `>= 1` semantics — passes if any single class is present rather than proving all 8).

---

## Codex Findings Addressed

### Cycle 1 (NO-GO at -002, addressed in -003)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — Acting-Prime rule under-tested. T-rule-content-acting only checked heading; missed parity with substance assertions on Sub-slice A citation, prose-invalid language, `detected_via: ask_user_question`, Owner Decisions / Input reference, and decision-class list. | "Add acting-file assertions equivalent to the Prime Builder assertions. At minimum verify the acting rule file contains the AUQ-only heading, the Sub-slice A VERIFIED bridge citation, the prose-invalid/block-emission language, `detected_via: ask_user_question`, the `Owner Decisions / Input` section reference, and every listed decision class." | This revision adopts a per-file per-token test design implemented as a Python script `groundtruth-kb/tests/test_prime_builder_auq_only_rule.py` that asserts ALL required tokens are present in BOTH files. Required-token set per file: (1) heading `## AskUserQuestion as the Only Valid Owner-Decision Channel`; (2) Sub-slice A VERIFIED bridge filename; (3) `detected_via: ask_user_question`; (4) `PROSE_DECISION_PATTERNS`; (5) `block` (referencing block emission); (6) all 8 decision classes literally; (7) `Owner Decisions / Input` section reference. Test fails (with diagnostic listing missing tokens) if ANY token absent in EITHER file. |
| **F2** — Decision-class assertion was `>= 1` (passes if any single class present); rule contract requires all 8. | "Replace single alternation-count assertion with one assertion per decision class per applicable file, or use deterministic script that checks the required token set in both files and prints missing classes." | Same Python script as F1: iterates 8 decision-class strings × 2 files = 16 assertions; reports missing classes by name. |

---

## Background

(Carry forward from `-001`.) Sub-slice B adds the formal AUQ-only decision-channel declaration to Prime Builder rule files, complementing Sub-slice A's mechanical enforcement (VERIFIED at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md`).

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Sub-slice B does NOT create files under `applications/`; modifies `.claude/rules/` only.

Topic-specific:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004).
- Sub-slice A precedent: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED).
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315)
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` (relevant per work_list row 21)
- `.claude/rules/prime-builder-role.md` — Target of modification (extension only; no removal).
- `.claude/rules/acting-prime-builder.md` — Target of modification (extension only; no removal).
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; Sub-slice B references the Owner Decisions / Input section pattern.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `.claude/rules/project-root-boundary.md` — Sub-slice B operates entirely within `E:/GT-KB/`.

Advisory specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the Test Plan section derive from these linked specs as follows: rule declaration contract → T-rule-tokens-prime + T-rule-tokens-acting (16 token presence assertions across both files); placement contract → T-out-of-applications-B; platform smoke → T-platform-smoke.

## Prior Deliberations

(Carry forward from `-001` plus add Codex `-002` NO-GO.)

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive | owner_conversation | owner_decision | Source rule for owner-decision surfacing |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Umbrella priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice B authorized |
| Sub-slice A VERIFIED at `-014` | bridge_thread | verified | Mechanical enforcement live |
| Codex Sub-slice B `-002` NO-GO | bridge_thread | no_go | F1 + F2 (test rigor) addressed in -003 |
| `DELIB-S323-GOV-CHAT-DERIVED-SPEC-APPROVAL-APPROVAL` | owner_conversation | owner_decision | Confirms AUQ as owner-approved channel |

## Goal

(Carry forward from `-001`.) Add an explicit AUQ-only-decision-channel declaration to `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md` covering the same content in both files (heading, Sub-slice A citation, prose-invalid language, `detected_via: ask_user_question`, 8 decision classes, Owner Decisions / Input reference).

## Implementation Plan

### Step 1: Add AUQ-only section to `.claude/rules/prime-builder-role.md`

Append a new level-2 section after the existing "Operational implications" bullet list. The full section text (verbatim, all 7 required tokens included):

```markdown
## AskUserQuestion as the Only Valid Owner-Decision Channel

(Active per S331 owner directive; mechanically enforced by `.claude/hooks/owner-decision-tracker.py` per `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED.)

Prime Builder collects owner decisions through `AskUserQuestion` exclusively. Prose decision-asks are invalid:

- The Stop-mode hook detects prose decision-ask patterns (`PROSE_DECISION_PATTERNS`) and emits `{"decision": "block", ...}` to refuse turn-end when no `AskUserQuestion` tool_use occurred in the same turn (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED + Sub-slice A tightening).
- All accepted owner decisions are recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`.

In-scope decision classes (use `AskUserQuestion`, never prose):

- approvals
- waivers
- priority choices
- formal artifact approvals
- requirement clarifications
- destructive actions
- deployments
- blocking owner decisions

Bridge proposals/reports that depend on owner approval should cite this rule and include an `Owner Decisions / Input` section enumerating the AskUserQuestion answers that authorize the work. Bridge compliance gate enforcement of this section requirement lands in Sub-slice C.

When in doubt, ask via `AskUserQuestion`. Verbose status updates that mention pending decisions DO NOT count as owner-decision asks; they are factual reporting (and the tightened regex per Sub-slice A no longer detects them as decision asks).
```

### Step 2: Add equivalent declaration to `.claude/rules/acting-prime-builder.md`

Append the SAME level-2 section text to the end of `.claude/rules/acting-prime-builder.md`. Per Codex `-002` F1: the section must include all 7 required tokens (heading + Sub-slice A citation + prose-invalid language + `PROSE_DECISION_PATTERNS` + `block` + all 8 decision classes + Owner Decisions / Input reference + `detected_via: ask_user_question`).

The acting-prime-builder rule applies to whichever harness is currently assigned Prime Builder (per existing role-mapping abstraction); the AUQ-only contract applies regardless of which harness embodies the role. Implementation reads existing file content first, identifies appropriate insertion point at end-of-file, and preserves existing structure.

### Step 3: Create test module + commit

Create `groundtruth-kb/tests/test_prime_builder_auq_only_rule.py` with the following test design (per Codex `-002` F2: explicit per-token per-file assertions, NOT alternation count):

```python
"""Tests for Sub-slice B: AUQ-only declaration in Prime Builder rule files.

Per Codex -002 F1+F2: explicit per-token per-file assertions that prove
the AUQ-only contract is present in both target rule files.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRIME_RULE = REPO_ROOT / ".claude" / "rules" / "prime-builder-role.md"
ACTING_RULE = REPO_ROOT / ".claude" / "rules" / "acting-prime-builder.md"

REQUIRED_TOKENS = [
    "## AskUserQuestion as the Only Valid Owner-Decision Channel",
    "gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md",
    "PROSE_DECISION_PATTERNS",
    '"decision": "block"',
    "detected_via: ask_user_question",
    "Owner Decisions / Input",
]

DECISION_CLASSES = [
    "approvals",
    "waivers",
    "priority choices",
    "formal artifact approvals",
    "requirement clarifications",
    "destructive actions",
    "deployments",
    "blocking owner decisions",
]


def _check_file_contains_all(path: Path, tokens: list[str]) -> list[str]:
    """Return list of missing tokens (empty list = all present)."""
    content = path.read_text(encoding="utf-8")
    return [t for t in tokens if t not in content]


def test_prime_builder_role_has_auq_only_section():
    missing = _check_file_contains_all(PRIME_RULE, REQUIRED_TOKENS)
    assert not missing, f"prime-builder-role.md missing tokens: {missing}"


def test_prime_builder_role_lists_all_decision_classes():
    missing = _check_file_contains_all(PRIME_RULE, DECISION_CLASSES)
    assert not missing, f"prime-builder-role.md missing decision classes: {missing}"


def test_acting_prime_builder_has_auq_only_section():
    missing = _check_file_contains_all(ACTING_RULE, REQUIRED_TOKENS)
    assert not missing, f"acting-prime-builder.md missing tokens: {missing}"


def test_acting_prime_builder_lists_all_decision_classes():
    missing = _check_file_contains_all(ACTING_RULE, DECISION_CLASSES)
    assert not missing, f"acting-prime-builder.md missing decision classes: {missing}"
```

This design provides:
- Per-file token presence: every required structural token must appear in EACH file (16 assertions: 6 tokens × 2 files + 8 classes × 2 files = 28 substring checks)
- Diagnostic output: missing tokens are reported by name in the assertion message, so a partial implementation produces actionable feedback

### Step 4: Commit on develop

Single commit on `develop` branch with message:

```
gtkb-gov-auq-enforcement-stack Slice B: Prime Builder rule formalizes AUQ-only decision channel (per Codex -002 F1+F2)

Adds AskUserQuestion-only-decision-channel declaration to:
- .claude/rules/prime-builder-role.md (full section)
- .claude/rules/acting-prime-builder.md (full section, parity with prime)

Adds test module groundtruth-kb/tests/test_prime_builder_auq_only_rule.py
verifying 6 required tokens + 8 decision classes are present in BOTH
files (28 substring assertions; per Codex -002 F1+F2).

Refs: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md
(Slice A VERIFIED); bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-003.md
(this REVISED-1 proposal).
```

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-b" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains spec links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-out-of-applications-B** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff <Sub-B-baseline>..<Sub-B-VERIFIED-commit> --name-only \| grep "^applications/"` | Empty |
| **T-rule-tokens-prime** (REVISED per `-002` F1+F2) | rule declaration contract: 6 required tokens in `.claude/rules/prime-builder-role.md` | `python -m pytest groundtruth-kb/tests/test_prime_builder_auq_only_rule.py::test_prime_builder_role_has_auq_only_section -v` | PASS — all 6 required tokens present (heading, Sub-slice A bridge, PROSE_DECISION_PATTERNS, block JSON literal, detected_via: ask_user_question, Owner Decisions / Input) |
| **T-rule-classes-prime** (REVISED per `-002` F2) | all 8 decision classes in `.claude/rules/prime-builder-role.md` | `pytest ::test_prime_builder_role_lists_all_decision_classes -v` | PASS — all 8 decision-class names present (approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, blocking owner decisions) |
| **T-rule-tokens-acting** (REVISED per `-002` F1) | rule declaration contract: 6 required tokens in `.claude/rules/acting-prime-builder.md` | `pytest ::test_acting_prime_builder_has_auq_only_section -v` | PASS — same 6 tokens as T-rule-tokens-prime |
| **T-rule-classes-acting** (REVISED per `-002` F1+F2) | all 8 decision classes in `.claude/rules/acting-prime-builder.md` | `pytest ::test_acting_prime_builder_lists_all_decision_classes -v` | PASS — same 8 classes as T-rule-classes-prime |
| **T-platform-smoke** | platform integrity | `pytest groundtruth-kb/tests/ -k "rule or owner_decision or hook" -x --timeout=60` | PASS (or pre-existing-known failures only) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-B | Direct |
| Rule declaration parity (per `-002` F1) | T-rule-tokens-prime + T-rule-tokens-acting (BOTH files; same required-token set) | Direct |
| Decision-class enumeration completeness (per `-002` F2) | T-rule-classes-prime + T-rule-classes-acting (BOTH files; ALL 8 classes) | Direct |
| Platform integrity | T-platform-smoke | Direct |

Every required spec has direct test coverage. Per Codex `-002` F2 the class-enumeration coverage is now ALL-class (not any-class).

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice B REVISED-1 proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Rule declaration text reviewed for clarity, scope completeness, and parity between both target files

VERIFIED when:

- [ ] All 9 tests T-bridge-1 through T-platform-smoke PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Both rule files contain all 6 required tokens (T-rule-tokens-prime + T-rule-tokens-acting)
- [ ] Both rule files contain all 8 decision classes (T-rule-classes-prime + T-rule-classes-acting)
- [ ] No regression in GT-KB platform tests (T-platform-smoke)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Rule additions conflict with existing rule structure | Low | Low | Append at end of file; no removal |
| Sub-slice C bridge gate doesn't recognize the section heading format | Low | Low | Sub-slice C will define exact heading pattern; Sub-slice B uses level-2 `## AskUserQuestion as the Only Valid Owner-Decision Channel` for machine-discoverability |
| Token-set drift over time as decision classes evolve | Low | Medium | Decision-class list maintained in both rule files AND test module; future additions require updating all 3 locations (rule × 2 + test) — drift detected at next test run |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter |

Rollback: `git revert` of the single commit reverses both rule additions + test module additions atomically.

## Open Questions

| ID | Question | Resolution |
|----|----------|------------|
| OQ-B-1 | Heading style for AUQ-only section? | `## AskUserQuestion as the Only Valid Owner-Decision Channel` (level-2; machine-discoverable) |
| OQ-B-2 | Should the rule cite Sub-slice C's forthcoming gate? | No — Sub-slice C will update both rules to add the bridge-gate citation when its own scope lands |
| OQ-B-3 (per `-002` F1) | Test depth for acting-prime-builder.md? | Same depth as prime-builder-role.md: per-token + per-class assertions |
| OQ-B-4 (per `-002` F2) | Decision-class assertion semantics? | All 8 must be present (not any) in both files |

## Owner Decisions / Input

This sub-slice's authorization derives from S331 AskUserQuestion answers (umbrella priority + scope + autonomy) and Sub-slice A's VERIFIED enforcement infrastructure. No additional owner input pending at sub-slice level.

## Out of Scope

- Bridge-compliance-gate hook check for `Owner Decisions / Input` section presence (Sub-slice C scope).
- Codex-side rule updates in `.claude/rules/loyal-opposition.md` for the bridge gate (Sub-slice C scope).
- Audit pass over `memory/pending-owner-decisions.md` historical entries (Sub-slice D).
- Implementing the requirements-collection hook (Sub-slice E).
- Adding release-metric doctor checks (Sub-slice F).
- Resolution of pre-existing scaffold-golden fixture mismatch.

## Project Root Boundary Compliance

Operates entirely within `E:/GT-KB/`. Targets `.claude/rules/prime-builder-role.md`, `.claude/rules/acting-prime-builder.md`, and `groundtruth-kb/tests/test_prime_builder_auq_only_rule.py`. No `applications/` content. Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` |
| Sub-slice A VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` |
| Sub-slice B Codex NO-GO `-002` | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-002.md` (F1 acting-file under-tested + F2 decision-class alternation-count too weak) |
| Source DELIB (S315 owner-decision surfacing) | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED |
| Live probes | `head` of `.claude/rules/prime-builder-role.md` (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
