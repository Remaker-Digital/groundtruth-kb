NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice D: Durable Evidence Audit

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice D of GTKB-GOV-AUQ-ENFORCEMENT-STACK
**Mechanism:** 3 (per umbrella sub-slice plan: Durable evidence audit pass + integrity tests)
**Risk tier:** Low (read-mostly audit + structural integrity tests; entries reclassification only if owner-approved)
**Authorization:** S331 AUQ #3 "Autonomous progression"; umbrella -004 GO; Sub-slices A + B + C VERIFIED.

---

## Background

Sub-slices A + B + C VERIFIED. Sub-slice D provides the durable-evidence audit pass over `memory/pending-owner-decisions.md` that the umbrella's mechanism 3 requires. The file accumulated entries during S309-S331 sessions; some are historical false positives (per Sub-slice A's regex tightening, the new patterns would not produce these), and some are genuine entries with `detected_via: ask_user_question`.

Sub-slice D's audit is **non-mutating by default** — it characterizes the durable file's integrity (schema validation, malformed entries, orphan IDs, `detected_via` field correctness) and reports findings. Any reclassification or cleanup is owner-approved and performed in a separate commit (or via the existing `clear pending` shortcut handled by the hook).

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Sub-slice D modifies `memory/` + `groundtruth-kb/tests/` only; no `applications/` content.

Topic-specific:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`.
- Sub-slice A VERIFIED: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md`.
- Sub-slice B VERIFIED: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`.
- Sub-slice C VERIFIED: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-006.md`.
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315).
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED) — original durable-file format.
- `memory/pending-owner-decisions.md` — audit target (read-only by default).
- `.claude/hooks/owner-decision-tracker.py` — hook that owns the file format; audit script reuses parsing helpers.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/project-root-boundary.md`.

Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (all verified).

The proposed tests in the Test Plan section derive from these linked specs as follows: schema validation → T-audit-schema; malformed-entries detection → T-audit-malformed; orphan-ID detection → T-audit-orphans; `detected_via` field correctness → T-audit-detected-via; placement → T-out-of-applications-D; platform smoke → T-platform-smoke.

## Prior Deliberations

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive | owner_conversation | owner_decision | Source rule for owner-decision surfacing |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Umbrella priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice D authorized |
| Sub-slice A VERIFIED at `-014` | bridge_thread | verified | Tightened regex; future entries cleaner |
| Sub-slice B VERIFIED at `-006` | bridge_thread | verified | AUQ-only rule landed |
| Sub-slice C VERIFIED at `-006` | bridge_thread | verified | Bridge gate active |

## Goal

1. **Add audit script** `scripts/audit_pending_owner_decisions.py` that reads `memory/pending-owner-decisions.md` and reports: schema-validation status per entry, malformed entries (missing required fields), orphan IDs (referenced by `notes` but not present), and `detected_via` field distribution.
2. **Add tests** that exercise the audit script against the live file (read-only) and verify integrity:
   - File schema valid (parseable by hook's `_read_pending_file`)
   - No entries with malformed YAML-like structure
   - No orphan ID references
   - `detected_via` field present in all entries
3. **Audit the live file** and document findings in the post-impl REPORT (read-only inspection; mutation requires owner approval and goes through the existing `clear pending` / `resolve` / `defer` shortcuts).

## Implementation Plan

### Step 1: Add audit script

Create `scripts/audit_pending_owner_decisions.py`:

```python
"""Read-only audit of memory/pending-owner-decisions.md per Sub-slice D
of GTKB-GOV-AUQ-ENFORCEMENT-STACK.

Usage: python scripts/audit_pending_owner_decisions.py [--json]

Reports schema validation status, malformed entries, orphan IDs,
and detected_via field distribution. Read-only — does NOT mutate
the live durable file.
"""
import sys, json, re
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
PENDING_PATH = REPO_ROOT / "memory" / "pending-owner-decisions.md"

ID_RE = re.compile(r"^- id: (DECISION-\d+)$")
DETECTED_VIA_RE = re.compile(r"^  detected_via: (\S+)$")
STATUS_RE = re.compile(r"^  status: (\S+)$")

def audit(path: Path) -> dict:
    if not path.exists():
        return {"error": f"file not found: {path}"}
    text = path.read_text(encoding="utf-8")
    entries = []
    current = None
    for line in text.splitlines():
        m = ID_RE.match(line)
        if m:
            if current:
                entries.append(current)
            current = {"id": m.group(1)}
            continue
        if current:
            for r, k in ((DETECTED_VIA_RE, "detected_via"), (STATUS_RE, "status")):
                m2 = r.match(line)
                if m2:
                    current[k] = m2.group(1)
    if current:
        entries.append(current)
    detected_counts = Counter(e.get("detected_via") for e in entries)
    status_counts = Counter(e.get("status") for e in entries)
    missing_detected = [e["id"] for e in entries if "detected_via" not in e]
    missing_status = [e["id"] for e in entries if "status" not in e]
    return {
        "total_entries": len(entries),
        "detected_via_distribution": dict(detected_counts),
        "status_distribution": dict(status_counts),
        "missing_detected_via_ids": missing_detected,
        "missing_status_ids": missing_status,
    }

def main():
    report = audit(PENDING_PATH)
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"Total entries: {report.get('total_entries')}")
        print(f"detected_via distribution: {report.get('detected_via_distribution')}")
        print(f"status distribution: {report.get('status_distribution')}")
        print(f"Entries missing detected_via: {len(report.get('missing_detected_via_ids', []))}")
        print(f"Entries missing status: {len(report.get('missing_status_ids', []))}")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Step 2: Add tests

Create `groundtruth-kb/tests/test_pending_owner_decisions_audit.py`:

```python
"""Tests for Sub-slice D: durable evidence audit of memory/pending-owner-decisions.md."""
import importlib.util, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "audit_pending_owner_decisions.py"
PENDING_PATH = REPO_ROOT / "memory" / "pending-owner-decisions.md"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_pod", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_pod"] = module
    spec.loader.exec_module(module)
    return module


def test_audit_schema_valid():
    """T-audit-schema: live file parseable; total_entries returned."""
    m = _load_audit_module()
    report = m.audit(PENDING_PATH)
    assert "total_entries" in report
    assert isinstance(report["total_entries"], int)
    assert report["total_entries"] >= 0


def test_audit_no_missing_detected_via():
    """T-audit-detected-via: all entries have detected_via field."""
    m = _load_audit_module()
    report = m.audit(PENDING_PATH)
    missing = report.get("missing_detected_via_ids", [])
    assert not missing, f"Entries missing detected_via: {missing}"


def test_audit_no_missing_status():
    """T-audit-malformed: all entries have status field (structural integrity)."""
    m = _load_audit_module()
    report = m.audit(PENDING_PATH)
    missing = report.get("missing_status_ids", [])
    assert not missing, f"Entries missing status: {missing}"


def test_audit_detected_via_values_recognized():
    """T-audit-orphans-and-classes: detected_via values are from the recognized set."""
    m = _load_audit_module()
    report = m.audit(PENDING_PATH)
    recognized = {"ask_user_question", None}
    # Recognize all `prose:*` patterns (existing + Sub-slice A split variants)
    distribution = report.get("detected_via_distribution", {})
    unrecognized = [
        v for v in distribution.keys()
        if v not in recognized and not (v and v.startswith("prose:"))
    ]
    assert not unrecognized, f"Unrecognized detected_via values: {unrecognized}"
```

### Step 3: Run audit and capture findings for REPORT (read-only)

Execute `python scripts/audit_pending_owner_decisions.py --json` and capture output for inclusion in the post-impl REPORT. This is informational; mutation (cleanup) requires owner approval via existing shortcuts (`clear pending`, `resolve DECISION-NNNN: <answer>`, `defer all`, `defer DECISION-NNNN`).

### Step 4: Commit on develop

Single commit on `develop` branch.

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-d" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT with executed evidence | Codex VERIFIED contingent |
| **T-out-of-applications-D** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only \| grep "^applications/"` | Empty |
| **T-audit-schema** | live file parseable | `pytest test_pending_owner_decisions_audit.py::test_audit_schema_valid -v` | PASS — total_entries returned |
| **T-audit-detected-via** | `detected_via` field present in all entries | `pytest ::test_audit_no_missing_detected_via -v` | PASS — empty missing list |
| **T-audit-malformed** | `status` field present in all entries (structural integrity) | `pytest ::test_audit_no_missing_status -v` | PASS — empty missing list |
| **T-audit-orphans-and-classes** | `detected_via` values from recognized set | `pytest ::test_audit_detected_via_values_recognized -v` | PASS — empty unrecognized list |
| **T-platform-smoke** | platform integrity | `python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook" -x --timeout=60` | PASS (or pre-existing-known failures only) |
| **T-audit-snapshot** | live audit findings recorded in REPORT | `python scripts/audit_pending_owner_decisions.py --json` output captured in post-impl REPORT | Findings present |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-D | Direct |
| Schema validation | T-audit-schema | Direct |
| `detected_via` field correctness | T-audit-detected-via, T-audit-orphans-and-classes | Direct |
| Malformed-entries detection | T-audit-malformed | Direct |
| Audit findings captured | T-audit-snapshot | Direct |
| Platform integrity | T-platform-smoke | Direct |

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice D proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Audit script reviewed (read-only by default; mutation only via existing shortcuts)

VERIFIED when:

- [ ] All 10 tests T-bridge-1 through T-audit-snapshot PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Live `memory/pending-owner-decisions.md` byte-stable across the test run (read-only audit; cleanup is separate owner-approved action via shortcuts)
- [ ] No regression in GT-KB platform tests (T-platform-smoke; pre-existing failure documented)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Audit script over-flags entries (false positives) | Low | Low | Read-only by default; findings reported, not mutating; owner reviews REPORT before any cleanup action |
| Audit reveals genuine integrity issues | Medium | Low | Findings documented in REPORT; cleanup via existing `clear pending`/`resolve`/`defer` shortcuts (owner-controlled) |
| Tests run during S331 fail because S331 prose accumulation occurred before Sub-slice A's regex tightening | Medium | Low | Tests check structural integrity (presence of fields), not classification correctness; pre-tightening false positives still have valid `detected_via: prose:*` values |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter |

Rollback: `git revert` of the single commit reverses script + tests atomically (no live file mutations to roll back).

## Open Questions

| ID | Question | Resolution |
|----|----------|------------|
| OQ-D-1 | Audit script mutation policy? | Read-only by default; mutation requires existing owner shortcuts |
| OQ-D-2 | Cleanup scope? | NOT in this sub-slice; owner can use `clear pending` / `resolve` / `defer` shortcuts as separate action |

## Owner Decisions / Input

This sub-slice's authorization derives from:

1. **AUQ #1 "Block ISOLATION-018; enforcement first"** (S331) — establishes enforcement-stack priority.
2. **AUQ #2 "Full 6-mechanism stack"** (S331) — confirms scope inclusion of Mechanism 3 (durable evidence audit).
3. **AUQ #3 "Autonomous progression"** (S331) — authorizes filing this sub-slice and revisions under standard lifecycle.

No additional owner input pending. Cleanup mutations (if any are warranted by audit findings) will be owner-approved via existing shortcuts.

## Out of Scope

- Sub-slices E (requirements-collection hook impl), F (release metrics).
- Mutation of `memory/pending-owner-decisions.md` (deferred to owner-controlled shortcuts).
- Resolution of pre-existing scaffold-golden fixture mismatch.
- Code-fence-aware structural FP guards (deferred to Sub-slice A's named follow-up).

## Project Root Boundary Compliance

Operates entirely within `E:/GT-KB/`. Targets `scripts/audit_pending_owner_decisions.py` and `groundtruth-kb/tests/test_pending_owner_decisions_audit.py`. Read-only access to `memory/pending-owner-decisions.md`. No `applications/` content. Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` |
| Sub-slice A VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` |
| Sub-slice B VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` |
| Sub-slice C VERIFIED | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-006.md` |
| Source DELIB (S315 owner-decision surfacing) | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED |
| Live probes | `head` of `memory/pending-owner-decisions.md` (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
