REVISED

# Post-Implementation Report — GTKB-GOV-TERM-PRIMER-STARTUP Slice 1 (REVISED-3)

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: REVISED-3 of post-impl, addressing Codex NO-GO at `-013.md` F1 (harness-memory not a valid project profile).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source.
2. **`.claude/rules/operating-model.md` §1** — operating-model framing.
3. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol Mandatory Specification Linkage Gate.
4. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`.
5. **`.claude/rules/deliberation-protocol.md`** — DELIB archival; satisfied at -007.
6. **`AGENTS.md`** — content-extended at REVISED-2 with MEMORY.md glossary entry; preserved.
7. **`CLAUDE.md` § "Canonical Terminology"** — load model unchanged.
8. **`GOV-19-A1`** — outside-in testing.
9. **`GOV-20`** — architecture decisions; dogfood install of verified surface.
10. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — deterministic startup terminology coverage.
11. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch (Slice 3 future).
12. **`groundtruth-kb/templates/rules/canonical-terminology.{md,toml}`** — modified surfaces (carried forward from -007).
13. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** — `_check_canonical_terminology()` REVISED-1 with separate severity tracking (carried forward from -009).
14. **`groundtruth-kb/tests/test_doctor_canonical_terminology.py`** — `test_gt_kb_self_doctor_passes_canonical_terminology` updated to use `dual-agent` profile per REVISED-3.
15. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) — prior architecture preserved.
16. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract; 2 packets carried forward from -007.
17. **`bridge/gtkb-gov-term-primer-startup-2026-05-02-013.md`** — Codex NO-GO with F1 finding addressed by this REVISED-3.
18. **`groundtruth.toml`** — GT-KB checkout config; profile reverted to `dual-agent` per Codex `-011.md` recommended action 1.
19. **`.claude/rules/deliberation-protocol.md`** — content-extended at REVISED-2 with canonical-terminology anchor section; preserved.
20. **`groundtruth-kb/src/groundtruth_kb/project/profiles.py`** — referenced by Codex `-013.md` F1 evidence; only `local-only`, `dual-agent`, `dual-agent-webapp` are valid project profiles. UNCHANGED in REVISED-3.
21. **`MEMORY.md`** *(new in REVISED-3)* — small root redirect doc carrying the 5 canonical-startup-term content strings, satisfying the `dual-agent` profile's `required_files` content contract; defers operational notepad content to `memory/MEMORY.md`.

## Prior Deliberations

Carried forward from REVISED-2 scoping (`-005.md`); see that document §"Prior Deliberations".

## Revision Rationale (REVISED-3)

Codex NO-GO at `-013.md` F1: `harness-memory` is not a valid project profile per `profiles.py::PROFILES`. Setting `groundtruth.toml::[project].profile = "harness-memory"` (REVISED-2 fix) caused `gt project doctor --dir .` to crash with `ValueError: Unknown profile 'harness-memory'. Valid profiles: dual-agent, dual-agent-webapp, local-only`. The previous fix path replaced one failure with another.

Per Codex `-011.md` recommended action 1 (Codex `-011.md` lines 70-74) + owner direction this turn ("Revert to dual-agent + create root MEMORY.md (Recommended)"):

1. **Revert profile.** Restored `groundtruth.toml::[project].profile = "dual-agent"`. The dual-agent profile is a valid public project profile per `profiles.py::PROFILES`; `gt project doctor --dir .` no longer crashes.

2. **Create root MEMORY.md.** New small redirect document at `MEMORY.md` (repo root) carrying the 5 canonical-startup-term content strings (MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition). The file explains that GT-KB's actual operational notepad lives at `memory/MEMORY.md` per the checkout's elaborate `memory/` topic-file convention; this root file exists to satisfy the dual-agent profile's `required_files` content contract.

3. **Test updated.** `test_gt_kb_self_doctor_passes_canonical_terminology` now invokes with `dual-agent` profile (matching `groundtruth.toml::[project].profile`), verifying `_check_canonical_terminology(repo_root, "dual-agent").status == "pass"`.

The AGENTS.md + deliberation-protocol.md content fixes from REVISED-2 are preserved unchanged — they remain valuable canonical-terminology content additions independent of profile choice.

## Implementation Evidence (REVISED-3 only)

### Change 13 (REVISED-3) — Profile revert in `groundtruth.toml`

```diff
-profile = "harness-memory"
+profile = "dual-agent"
```

### Change 14 (REVISED-3) — Root `MEMORY.md` created

Content highlights:

- Header: "MEMORY.md — GroundTruth-KB"
- §"Canonical Terminology (anchored — required for doctor's `dual-agent` profile)" — explicit listing of the 5 canonical startup terms (MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition) with definitions.
- §"Where the live operational notepad lives" — pointer to `memory/MEMORY.md` for active session state.
- ~30 lines total. Compact; pedagogical purpose only (satisfies the doctor contract; doesn't duplicate operational state).

### Change 15 (REVISED-3) — Test updated to dual-agent profile

```diff
-    check = _check_canonical_terminology(repo_root, "harness-memory")
+    check = _check_canonical_terminology(repo_root, "dual-agent")
```

Test docstring updated to reflect the new fix path: dual-agent profile + root MEMORY.md (Codex `-011.md` recommended action 1) replaces the harness-memory profile choice that was structurally invalid.

## Verification Evidence

### Direct invocation against GT-KB self

```
$ python -c "from pathlib import Path; \
            import sys; sys.path.insert(0, 'groundtruth-kb/src'); \
            from groundtruth_kb.project.doctor import _check_canonical_terminology; \
            check = _check_canonical_terminology(Path('.'), 'dual-agent'); \
            print('status:', check.status); print('message:', check.message)"
status: pass
message: Canonical-terminology surface OK — 5 required terms present in 4 required files (profile: dual-agent)
```

The required-files count is now 4 (CLAUDE.md, AGENTS.md, MEMORY.md, .claude/rules/deliberation-protocol.md) per the dual-agent profile, vs 3 under harness-memory. The 5 canonical startup terms appear in all 4 required files (CLAUDE.md from existing content; AGENTS.md from REVISED-2 content fix; new root MEMORY.md from REVISED-3; deliberation-protocol.md from REVISED-2 content fix).

### Test sweep

```
$ python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py
86 passed, 1 warning in 18.84s
```

Same 86 tests as REVISED-2; the test count is unchanged (one test was modified, not added). Zero regressions.

### Ruff

```
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
All checks passed!
```

## Acceptance Criteria Check (REVISED-3)

| Criterion | Status |
|---|---|
| Codex `-013.md` F1: public `gt project doctor` against GT-KB self does not crash | SATISFIED — `dual-agent` profile is valid in `profiles.py::PROFILES`; doctor invocation reaches the canonical-terminology check |
| Canonical-terminology check passes on GT-KB self | SATISFIED — `_check_canonical_terminology(Path('.'), 'dual-agent')` returns `status="pass"` |
| Public-surface acceptance from `-005.md` T5 | SATISFIED — the dual-agent profile is the public CLI's accepted profile for GT-KB; canonical-terminology check passes under it |
| Profile change is structurally valid | SATISFIED — `dual-agent` is a registered profile in `PROFILES`; CLI accepts it |
| Content coverage on AGENTS.md + deliberation-protocol.md + root MEMORY.md | SATISFIED — all 4 required files contain all 5 canonical startup terms |
| All `-007`, `-009`, `-012` non-F1 acceptance items still satisfied | SATISFIED — 86/86 tests pass; primer contract + severity-tracking + content fixes all preserved |
| Ruff clean | SATISFIED |

## Files Touched (REVISED-3 additions to `-007` + `-009` + `-012`)

Modified:
- `groundtruth.toml` (profile: harness-memory → dual-agent; reverts the REVISED-2 change)
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py` (`test_gt_kb_self_doctor_passes_canonical_terminology` updated to use dual-agent profile)

Created:
- `MEMORY.md` (root redirect doc carrying canonical-startup-term content)

Preserved unchanged from REVISED-2:
- `AGENTS.md` (MEMORY.md glossary entry from REVISED-2)
- `.claude/rules/deliberation-protocol.md` (canonical-terminology anchor section from REVISED-2)
- All `-007` template + GT-KB-checkout-install + approval-packet + DELIB changes
- All `-009` doctor severity-tracking refactor changes

## Notes for Loyal Opposition

- **Public CLI no longer crashes.** `gt project doctor --dir .` (which uses `groundtruth.toml::[project].profile = "dual-agent"`) reaches the canonical-terminology check and returns `status="pass"`. Codex `-013.md` F1 is resolved.
- **Root MEMORY.md is intentionally compact.** It carries only the 5 canonical-startup-term content strings + a pointer to `memory/MEMORY.md`. Operational session state lives at `memory/MEMORY.md` per the GT-KB-checkout convention; the root marker exists strictly to satisfy the dual-agent profile's `required_files` content contract.
- **Profile choice respects existing public profile registry.** `dual-agent` is the only valid project profile applicable to GT-KB's bridge-using layout per `profiles.py::PROFILES`. No changes to `profiles.py` made; no scaffold-pipeline impact.
- **AGENTS.md + deliberation-protocol.md content fixes from REVISED-2 are preserved.** They remain valuable canonical-terminology content additions independent of the profile choice; both files now anchor canonical-term references to the 3-tier ADR-0001 vocabulary.
- **`harness-memory` remains valid as a terminology-config profile** in `templates/rules/canonical-terminology.toml` and the GT-KB-checkout dogfood install. It's selectable via the canonical-terminology check's `profile_name` parameter, but not via the public project profile registry — which is the intended boundary per this fix.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
