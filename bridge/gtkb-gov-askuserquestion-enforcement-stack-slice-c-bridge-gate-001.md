NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice C: Bridge Review Gate for Owner-Decision Evidence

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK
**Mechanism:** 4 (per umbrella sub-slice plan: Bridge review gate for owner-decision evidence)
**Risk tier:** Medium (extends `bridge-compliance-gate.py` with conditional check; rule edits to `codex-review-gate.md` and `loyal-opposition.md`)
**Authorization:** S331 AUQ #3 "Autonomous progression"; umbrella -004 GO; Sub-slice A VERIFIED at `-014`; Sub-slice B VERIFIED at `-006`.

---

## Background

Sub-slice B (VERIFIED at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`) added the AUQ-only declaration to Prime Builder rules, including: "Bridge proposals/reports that depend on owner approval should cite this rule and include an `Owner Decisions / Input` section enumerating the AskUserQuestion answers that authorize the work. Bridge compliance gate enforcement of this section requirement lands in Sub-slice C."

Sub-slice C provides that mechanical gate enforcement: when a bridge proposal/report indicates dependence on owner approval (via specific markers in content), the `bridge-compliance-gate.py` hook requires presence of an `Owner Decisions / Input` section. Without this section, the hook denies the Write operation with a deny reason explaining the contract.

Sub-slice C also updates `codex-review-gate.md` and `loyal-opposition.md` to make the rule visible to both human and Loyal Opposition reviewers.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-001.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Sub-slice C does NOT create files under `applications/`; modifies `.claude/rules/`, `.claude/hooks/`, and `groundtruth-kb/tests/` only.

Topic-specific:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004).
- Sub-slice A precedent: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED).
- Sub-slice B precedent: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` (VERIFIED) — established the rule; Sub-slice C enforces it.
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315).
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED).
- `.claude/hooks/bridge-compliance-gate.py` — Target of modification: add conditional check for `Owner Decisions / Input` section presence on proposals/reports that indicate owner-approval scope.
- `.claude/rules/codex-review-gate.md` — Target of modification: require Owner Decisions / Input section when proposal claims owner approval.
- `.claude/rules/loyal-opposition.md` — Target of modification: NO-GO bridge entries lacking the section when applicable.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; Sub-slice C extends with the new section requirement.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `.claude/rules/project-root-boundary.md` — Sub-slice C operates entirely within `E:/GT-KB/`.

Advisory specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the Test Plan section derive from these linked specs as follows: hook gate behavior → T-hook-blocks-missing + T-hook-allows-present + T-hook-skips-non-claiming (3 hermetic synthetic-fixture tests); rule content → T-rule-codex-review-gate + T-rule-loyal-opposition (file-content membership assertions); placement contract → T-out-of-applications-C; platform smoke → T-platform-smoke.

## Prior Deliberations

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive | owner_conversation | owner_decision | Source rule for owner-decision surfacing |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Umbrella priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice C authorized |
| Sub-slice A VERIFIED at `-014` | bridge_thread | verified | Mechanical Stop-mode enforcement live |
| Sub-slice B VERIFIED at `-006` | bridge_thread | verified | AUQ-only rule landed; this Sub-slice enforces its `Owner Decisions / Input` section requirement |

## Goal

1. **Extend `.claude/hooks/bridge-compliance-gate.py`** with a conditional check: when a Write target file under `bridge/` has content that signals owner-approval-scope (heuristic markers), the hook requires presence of an `Owner Decisions / Input` heading.
2. **Update `.claude/rules/codex-review-gate.md`** to declare the new section requirement.
3. **Update `.claude/rules/loyal-opposition.md`** with the corresponding NO-GO obligation.
4. **Add tests** verifying: (a) hook denies a synthetic proposal that claims owner-approval but lacks the section; (b) hook allows the same proposal with the section present; (c) hook does NOT fire on a routine proposal that doesn't claim owner-approval scope.

## Design: Conditional Section Requirement

The check fires only when the proposal/report content indicates owner-approval dependence. Heuristic markers (any one triggers the requirement):

1. The literal string `Owner Decisions / Input` appears as a section heading already (self-citing — the proposal author already invoked the contract; the hook then verifies the section has substantive content).
2. The proposal cites Sub-slice B's AUQ-only rule (e.g., references `gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`) — implies owner-decision relevance.
3. The proposal references AskUserQuestion explicitly with an answer/decision context (regex: `\b(AUQ|AskUserQuestion)\b.*\b(answer|approval|decision|directive)\b` within ~200 chars).

When NONE of these markers appear, the hook does NOT require the section (routine refactors, scaffold updates, etc. are unaffected).

When AT LEAST ONE marker appears, the hook requires:
- A heading matching `^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$` (level-1-to-6 heading; allows `Owner Decisions / Input` or `Owner Decisions Input` minor variants)
- Section text under that heading is non-empty and does NOT contain placeholder words (`tbd`, `todo`, `n/a`, `none`, `not applicable`, `no relevant`)

This mirrors the existing `_has_concrete_spec_links()` pattern in `bridge-compliance-gate.py` (lines ~102-123), so the implementation reuses the same scaffolding.

## Implementation Plan

### Step 1: Extend `bridge-compliance-gate.py` with conditional section check

Add 3 module-level constants near existing patterns:

```python
OWNER_DECISIONS_HEADING_RE = re.compile(
    r"^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

OWNER_APPROVAL_MARKER_RES = (
    # Marker 1: cites Sub-slice B's VERIFIED rule
    re.compile(
        r"gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006\.md",
        re.IGNORECASE,
    ),
    # Marker 2: AUQ + decision-context phrase within ~200 chars
    re.compile(
        r"\b(?:AUQ|AskUserQuestion)\b[^.]{0,200}\b(?:answer|approval|decision|directive|authorize|authorization)\b",
        re.IGNORECASE,
    ),
)


def _proposal_claims_owner_approval(content: str) -> bool:
    """Return True when proposal content signals dependence on owner approval.

    Self-citing (Owner Decisions / Input heading present) also counts as a
    claim because the author invoked the contract. The hook then verifies
    the section is substantive, not placeholder-only.
    """
    if OWNER_DECISIONS_HEADING_RE.search(content):
        return True
    return any(p.search(content) for p in OWNER_APPROVAL_MARKER_RES)


def _has_concrete_owner_decisions_section(content: str) -> bool:
    """Section heading present AND section text non-empty AND not placeholder-only."""
    lines = content.splitlines()
    start = None
    for i, line in enumerate(lines):
        if OWNER_DECISIONS_HEADING_RE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return False
    section = []
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        section.append(line)
    text = "\n".join(section).strip()
    if not text:
        return False
    return not SPEC_PLACEHOLDER_RE.search(text)
```

Integrate into the existing PreToolUse handler (the function that processes Write/Edit on bridge files). The check fires AFTER the existing Spec Links and Spec-Derived Verification gates. If `_proposal_claims_owner_approval(content)` is True AND `_has_concrete_owner_decisions_section(content)` is False, return a deny decision.

### Step 2: Update `.claude/rules/codex-review-gate.md`

Append a new section after existing content:

```markdown
## Owner Decisions / Input Section Requirement

(Active per Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK; mechanically enforced by `.claude/hooks/bridge-compliance-gate.py`.)

Bridge proposals/reports that claim dependence on owner approval — citing the AUQ-only rule (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`), referencing AskUserQuestion answers, or otherwise indicating owner-decision scope — MUST include a non-empty `## Owner Decisions / Input` section enumerating the relevant AskUserQuestion evidence.

Codex review checks for the section's presence and substantive content. Loyal Opposition issues NO-GO when applicable proposals/reports lack the section. The bridge-compliance-gate hook fails the Write before submission to prevent ambiguous packets from reaching review.
```

### Step 3: Update `.claude/rules/loyal-opposition.md`

Append NO-GO obligation paragraph under the existing review-gate section.

### Step 4: Add hook tests

Add `groundtruth-kb/tests/test_owner_decisions_section_gate.py` with 3 hermetic tests:

```python
"""Tests for Sub-slice C: bridge-compliance-gate Owner Decisions / Input section check."""
import json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _run_hook(file_path: str, content: str) -> dict:
    payload = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
        "session_id": "test-slice-c",
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload, capture_output=True, text=True, timeout=10,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


# Synthetic proposal claiming owner-approval (cites Sub-slice B's VERIFIED rule)
# AND lacks Owner Decisions / Input section.
PROPOSAL_CLAIMS_NO_SECTION = """NEW

# Test Proposal

## Specification Links
- GOV-TEST-001
- bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md

## Specification-Derived Test Plan
python -m pytest test.py
"""

PROPOSAL_CLAIMS_WITH_SECTION = PROPOSAL_CLAIMS_NO_SECTION + """
## Owner Decisions / Input

Owner approval cited from S331 AskUserQuestion answer "Autonomous progression".
"""

# Routine proposal that does NOT claim owner-approval scope.
PROPOSAL_NO_CLAIM = """NEW

# Routine Refactor Proposal

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001

## Specification-Derived Test Plan
python -m pytest test.py
"""


def test_hook_blocks_proposal_claiming_approval_without_section():
    out = _run_hook("bridge/test-fixture-001.md", PROPOSAL_CLAIMS_NO_SECTION)
    assert out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    assert "Owner Decisions" in out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")


def test_hook_allows_proposal_claiming_approval_with_section():
    out = _run_hook("bridge/test-fixture-002.md", PROPOSAL_CLAIMS_WITH_SECTION)
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    assert decision != "deny" or "Owner Decisions" not in out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")


def test_hook_does_not_fire_on_non_claiming_proposal():
    out = _run_hook("bridge/test-fixture-003.md", PROPOSAL_NO_CLAIM)
    decision = out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")
    reason = out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    assert "Owner Decisions" not in reason, f"Owner Decisions check should not fire; got: {reason}"
```

Hermetic by construction: synthetic content; subprocess invocation; no live state mutation.

### Step 5: Commit on develop

Single commit on `develop` branch.

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-c" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT with executed evidence | Codex VERIFIED contingent |
| **T-out-of-applications-C** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only \| grep "^applications/"` | Empty |
| **T-hook-blocks-missing** | conditional gate fires when claim made + section missing | `pytest test_owner_decisions_section_gate.py::test_hook_blocks_proposal_claiming_approval_without_section -v` | PASS — deny decision; reason mentions Owner Decisions |
| **T-hook-allows-present** | gate passes when section present | `pytest ::test_hook_allows_proposal_claiming_approval_with_section -v` | PASS — no Owner-Decisions deny |
| **T-hook-skips-non-claiming** | gate does NOT fire on routine proposals | `pytest ::test_hook_does_not_fire_on_non_claiming_proposal -v` | PASS — Owner Decisions check not triggered |
| **T-rule-codex-review-gate** | `.claude/rules/codex-review-gate.md` declares the requirement | `grep -c "Owner Decisions / Input Section Requirement" .claude/rules/codex-review-gate.md` | `1` |
| **T-rule-loyal-opposition** | `.claude/rules/loyal-opposition.md` declares NO-GO obligation | `grep -c "Owner Decisions / Input" .claude/rules/loyal-opposition.md` | `≥ 1` |
| **T-platform-smoke** | platform integrity | `python -m pytest groundtruth-kb/tests/ -k "owner_decision or hook or rule" -x --timeout=60` | PASS (or pre-existing-known failures only) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-C | Direct |
| Hook conditional gate behavior | T-hook-blocks-missing, T-hook-allows-present, T-hook-skips-non-claiming | Direct (3 hermetic tests) |
| `.claude/rules/codex-review-gate.md` rule extension | T-rule-codex-review-gate | Direct |
| `.claude/rules/loyal-opposition.md` rule extension | T-rule-loyal-opposition | Direct |
| Platform integrity | T-platform-smoke | Direct |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice C proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Hook conditional logic reviewed (markers + section detection)
- [ ] Rule additions reviewed for clarity

VERIFIED when:

- [ ] All 10 tests T-bridge-1 through T-platform-smoke PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Hook fires on claim-without-section AND skips on non-claiming (T-hook-blocks-missing + T-hook-skips-non-claiming)
- [ ] Hook allows claim-with-section (T-hook-allows-present)
- [ ] Both rule files contain the new section requirement (T-rule-codex-review-gate + T-rule-loyal-opposition)
- [ ] No regression in GT-KB platform tests (T-platform-smoke; pre-existing failure documented)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Hook over-triggers on routine proposals via marker false-positives | Medium | Medium | Conditional design — markers are specific (Sub-slice B bridge filename + AUQ+decision regex); routine refactors won't match. T-hook-skips-non-claiming verifies. |
| Hook under-triggers — proposal claims owner-approval but doesn't match any marker | Medium | Medium | This proposal IS such a case (cites Sub-slice B's VERIFIED rule); hence the first marker. Owner-approval claims that cite none of the markers AND lack the section can still slip; future tightening can extend marker set. |
| Hook regex on long proposals slow | Low | Low | Single-pass regex search; well under 100ms even on 10K-line content |
| Test fixture content too small to trigger existing Spec Links check | Low | Low | Test fixtures include `## Specification Links` + spec token to satisfy that check first; the Owner Decisions check is then evaluated on its own merit |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter |

Rollback: `git revert` of the single commit reverses hook + rule + test changes atomically.

## Open Questions

| ID | Question | Resolution |
|----|----------|------------|
| OQ-C-1 | Marker specificity? | Conservative: 2 markers (Sub-slice B bridge filename, AUQ+decision regex) plus self-citing detection (Owner Decisions heading already present). Future Sub-slice can widen if under-trigger surfaces. |
| OQ-C-2 | Heading variant tolerance? | Allow `Owner Decisions / Input` and `Owner Decisions Input` (with or without `/`) at headings level 1-6; CASE INSENSITIVE |
| OQ-C-3 | Placeholder rejection in section text? | Yes — reuse existing `SPEC_PLACEHOLDER_RE` pattern (`tbd|todo|none|n/a|not applicable|no relevant`) for consistency with Spec Links check |

## Owner Decisions / Input

This sub-slice's authorization derives from S331 AskUserQuestion answers (umbrella priority + scope + autonomy) and Sub-slice A + B's VERIFIED enforcement infrastructure.

The owner answers cited as authorization for this sub-slice:

1. **AUQ #1 "Block ISOLATION-018; enforcement first"** — establishes enforcement-stack priority over remaining ISOLATION-018 sub-slices.
2. **AUQ #2 "Full 6-mechanism stack"** — confirms scope inclusion of the bridge-gate mechanism (Mechanism 4).
3. **AUQ #3 "Autonomous progression"** — authorizes filing this Sub-slice C bridge under standard lifecycle without per-sub-slice owner approval.

No additional owner input pending at sub-slice level.

## Out of Scope

- Audit pass over `memory/pending-owner-decisions.md` historical entries (Sub-slice D).
- Implementing the requirements-collection hook (Sub-slice E).
- Adding release-metric doctor checks (Sub-slice F).
- Resolution of pre-existing scaffold-golden fixture mismatch.
- Code-fence-aware structural FP guards (deferred to named follow-up per Sub-slice A's row P7 partial closure).
- Cross-harness Codex enforcement (Codex's local hook surface is governed separately).

## Project Root Boundary Compliance

Operates entirely within `E:/GT-KB/`. Targets `.claude/hooks/bridge-compliance-gate.py`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, and `groundtruth-kb/tests/test_owner_decisions_section_gate.py`. No `applications/` content. Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` |
| Sub-slice A VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` |
| Sub-slice B VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` |
| Source DELIB (S331 enforcement directive) | This conversation: 3 AUQ answers (priority + scope + autonomy) |
| Live probes | Read of `.claude/hooks/bridge-compliance-gate.py` (331 lines) (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
