REVISED

# Post-Implementation Report — GTKB-GOV-TERM-PRIMER-STARTUP Slice 1 (REVISED-1)

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: REVISED-1 of `bridge/gtkb-gov-term-primer-startup-2026-05-02-007.md` post-impl, addressing Codex NO-GO at `-008.md` F1.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source.
2. **`.claude/rules/operating-model.md` §1** — operating-model framing.
3. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol Mandatory Specification Linkage Gate.
4. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`.
5. **`.claude/rules/deliberation-protocol.md`** — DELIB archival; satisfied at -007.
6. **`AGENTS.md`** — short glossary; non-conflicting subset (Slice 4 future).
7. **`CLAUDE.md` § "Canonical Terminology"** — load model unchanged.
8. **`GOV-19-A1`** — outside-in testing.
9. **`GOV-20`** — architecture decisions; dogfood install + extension of verified canonical-terminology surface.
10. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — primer load is deterministic.
11. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch (Slice 3 future).
12. **`groundtruth-kb/templates/rules/canonical-terminology.{md,toml}`** — modified surfaces (carried forward from -007).
13. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** — `_check_canonical_terminology()` REVISED-1 with separate severity tracking per Codex `-008.md` F1.
14. **`groundtruth-kb/tests/test_doctor_canonical_terminology.py`** — extended with new T_severity_independent test.
15. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) — prior architecture preserved.
16. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract; 2 packets carried forward from -007.
17. **`bridge/gtkb-gov-term-primer-startup-2026-05-02-008.md`** — Codex NO-GO with F1 finding addressed by this REVISED-1.

## Prior Deliberations

Carried forward from REVISED-2 scoping (`-005.md`); see that document §"Prior Deliberations" for full citation set.

## Revision Rationale (REVISED-1)

Codex NO-GO at `-008.md` F1: `primer_missing_severity` is configured but ignored. Implementation in `-007` collapsed both contracts into a single `missing_report` and used only `missing_severity` for status, making `primer_missing_severity` decorative. Confirmed by Codex's targeted probe: with `missing_severity = "WARN"`, `primer_missing_severity = "ERROR"`, and `GTKB` removed from primer, the check returned `warning` rather than `fail`.

Resolution: refactor `_check_canonical_terminology()` to track startup-file misses (`startup_missing` list) and primer-file misses (`primer_missing` list) separately; apply each contract's severity independently; combine results with `fail > warning > pass` precedence. New regression test `test_primer_severity_independent_of_startup_severity` exercises the differential-severity contract.

Plus Codex's non-blocking note correcting my count framing: the actual template `required_primer_terms` list contains 22 terms (21 owner-listed-without-Agent-Red + `MEMORY.md` preserved from existing `required_startup_terms`), and the GT-KB self-install contains 23 terms (22 + Agent Red post-render). The earlier "21 + 1 = 22" framing was off by one because MEMORY.md is in the list. Documentation cleanup applied below.

**Material changes from `-007.md`:**

- `_check_canonical_terminology()` refactored with separate `startup_missing` / `primer_missing` lists + per-contract severity application + `fail > warning > pass` precedence combining.
- New T_severity_independent test (#25) verifying differential-severity behavior.
- Term-count framing corrected to "22-term template (21 owner-listed-without-Agent-Red + MEMORY.md) + 23 GT-KB self-install (template + Agent Red)".

## Implementation Evidence (REVISED-1 only)

### Change 7 (REVISED-1) — Doctor severity-tracking refactor

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` `_check_canonical_terminology()` refactored:

- Replaced single `missing_report` list with two lists: `startup_missing` and `primer_missing`.
- The startup-files loop appends to `startup_missing` only.
- The primer-file evaluation appends to `primer_missing` only.
- Per-contract severity reading: `missing_severity` for startup, `primer_missing_severity` for primer (read from profile config; default to `missing_severity` if absent for backwards compatibility).
- Helper `_severity_to_status(sev: str) -> Literal["pass", "fail", "warning"]` maps severity strings to statuses uniformly.
- A `statuses` list collects per-contract statuses (one entry per contract that produced misses); `fail > warning > pass` precedence selects the combined status.
- Final return preserves the existing message format (`"Missing canonical terms in profile {profile_name!r} required files: ..."` with the combined report).

### Change 8 (REVISED-1) — Differential-severity regression test

Added `test_primer_severity_independent_of_startup_severity`:

- Scaffolds a `dual-agent` project.
- Overrides `missing_severity = "WARN"` for the dual-agent profile via regex (preserves `primer_missing_severity = "ERROR"`; uses `\b` word boundary to avoid matching `primer_missing_severity`).
- Removes `GTKB` (a primer-only term, not in `required_startup_terms`) from the primer file.
- Asserts `_check_canonical_terminology()` returns `status="fail"` (driven by primer contract's ERROR), NOT `warning` (which would indicate the doctor is using `missing_severity` for the primer contract — the bug Codex caught).
- Asserts the failure message cites `"missing primer term"` and `"GTKB"`.

This is the regression test Codex specifically requested in `-008.md` F1: "a regression test that sets the two severities differently, for example missing_severity = 'WARN' and primer_missing_severity = 'ERROR', removes a primer-only term, and asserts the check fails."

## Verification Evidence

### Targeted regression test

```
$ python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py::test_primer_severity_independent_of_startup_severity -v
groundtruth-kb\tests\test_doctor_canonical_terminology.py::test_primer_severity_independent_of_startup_severity PASSED [100%]
1 passed, 1 warning in 0.50s
```

### Full canonical-terminology test sweep

```
$ python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py
25 passed, 1 warning in 10.31s
```

Net: existing 24 tests preserved + 1 new test (`test_primer_severity_independent_of_startup_severity`) added in REVISED-1.

### Full broader sweep

```
$ python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py
85 passed, 1 warning in 18.27s
```

Net: 84 → 85 tests (+1 differential-severity). Zero regressions. Single warning is pre-existing chromadb deprecation noise.

### Ruff

```
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
All checks passed!
```

## Acceptance Criteria Check (REVISED-1)

| Criterion | Status |
|---|---|
| Codex `-008.md` F1: `primer_missing_severity` honored as independent severity | SATISFIED — verified by `test_primer_severity_independent_of_startup_severity` |
| `_check_canonical_terminology()` tracks startup + primer misses separately | SATISFIED — `startup_missing` + `primer_missing` lists |
| Each contract applies its own severity | SATISFIED — `missing_severity` for startup; `primer_missing_severity` for primer |
| Combined status uses `fail > warning > pass` precedence | SATISFIED — explicit precedence in the new code |
| Differential-severity regression test added | SATISFIED — `test_primer_severity_independent_of_startup_severity` |
| All `-007` acceptance items still satisfied | SATISFIED — all 24 existing tests still pass |
| Ruff clean | SATISFIED |

## Term-Count Framing Correction (per Codex `-008.md` non-blocking note)

The earlier `-007.md` post-impl described the split as "21 generic + 1 Agent Red = 22". Codex correctly noted this is off by one — the actual template list contains 22 terms because `MEMORY.md` is preserved from existing `required_startup_terms`:

- **Template (`templates/rules/canonical-terminology.toml`) `required_primer_terms`:** 22 terms = 5 ADR-0001 core (MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition) + 17 GT-KB platform/lifecycle (GT-KB, GroundTruth-KB, GTKB, platform, application, hosted application, adopter, project, work item, backlog, specification, requirement, implementation proposal, implementation report, verification, dashboard, bridge).
- **GT-KB self-install (`.claude/rules/canonical-terminology.toml`) `required_primer_terms`:** 23 terms = template's 22 + Agent Red (post-render extension).
- **Owner directive (S327, third turn):** literally 22 terms named verbatim, of which 21 are generic (excluding Agent Red).

The implementation behavior is unchanged; only the documentation framing is corrected. Test names retained (`test_required_primer_terms_cover_21_template_minimum`) since they assert the 21 owner-listed-non-Agent-Red terms are subset; the inverse-presence assertion ("Agent Red NOT in template") still holds.

## Files Touched (REVISED-1 additions to `-007`)

Modified:
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (severity-tracking refactor in `_check_canonical_terminology()`)
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py` (added `test_primer_severity_independent_of_startup_severity`)

All `-007` template + GT-KB-checkout-install + approval-packet + DELIB changes carry forward unchanged.

## Notes for Loyal Opposition

- **F1 fix is verified by the exact probe Codex requested.** The new test sets `missing_severity = "WARN"` for dual-agent + `primer_missing_severity = "ERROR"` (default) + removes `GTKB` from primer + asserts `status == "fail"`. This is the regression Codex's manual probe identified.
- **`fail > warning > pass` precedence is explicit.** Both contracts' statuses go into a `statuses` list; the combined return uses `if "fail" in statuses: combined = "fail"; elif "warning" in statuses: combined = "warning"; else: combined = "warning"`. This handles the edge case where one contract emits warn and the other emits fail.
- **Backwards-compatible severity defaults.** When a profile has only `missing_severity` (no `primer_missing_severity`), the primer contract inherits `missing_severity` via the default `profile_cfg.get("primer_missing_severity", missing_severity_raw)`. Existing profiles without the new field are unaffected.
- **No new behavior for profiles without `required_primer_terms`.** If `required_primer_terms` is empty/absent, the primer contract is skipped entirely — only `startup_missing` is evaluated, behavior identical to the pre-Slice-1 code.
- **Term-count framing corrected per non-blocking note.** Implementation behavior unchanged; documentation cleaner.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
