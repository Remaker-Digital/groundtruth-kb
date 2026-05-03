NEW

# Post-Implementation Report — GTKB-GOV-TERM-PRIMER-STARTUP Slice 1

Implemented by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Post-implementation report for Slice 1 of `bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md` (REVISED-2; Codex GO at `-006.md`).

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology source; multi-source attribution per Codex `-002.md` F3.
2. **`.claude/rules/operating-model.md` §1** — operating-model framing for session-start primer access.
3. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol Mandatory Specification Linkage Gate.
4. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`.
5. **`.claude/rules/deliberation-protocol.md`** — deliberation search + DELIB archival; satisfied by §"DELIB Archival" below.
6. **`AGENTS.md`** — short glossary; verified non-conflicting with primer (Slice 4 future).
7. **`CLAUDE.md` § "Canonical Terminology"** — load model unchanged; primer auto-loads via `.claude/rules/*.md` convention.
8. **`GOV-19-A1`** — outside-in testing; tests exercise public doctor surface `_check_canonical_terminology`.
9. **`GOV-20`** — architecture decisions; this Slice 1 is dogfood install + extension of existing surface (no new ADR/DCL needed; the verified canonical-terminology thread `gtkb-canonical-terminology-surface-implementation-012.md` carries the architecture).
10. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — primer load is deterministic; no AI-mediated terminology recall in startup.
11. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch; primer reference deferred to Slice 3 (post-Slice-1 implementation).
12. **`groundtruth-kb/templates/rules/canonical-terminology.md`** + `**.toml`** — modified surfaces.
13. **`groundtruth-kb/templates/managed-artifacts.toml`** — registry rows `rule.canonical-terminology` + `rule.canonical-terminology-config` unchanged.
14. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** `_check_canonical_terminology()` — extended in this Slice 1.
15. **`groundtruth-kb/tests/test_doctor_canonical_terminology.py`** — extended in this Slice 1.
16. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) — prior architecture preserved.
17. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract; satisfied by 2 packets.

## Prior Deliberations

Carried forward from REVISED-2 (`-005.md`); see that document §"Prior Deliberations" for full citation set including DELIB-0722, DELIB-1180, DELIB-GTKB-IDP-TERMINOLOGY, DELIB-1138, DELIB-1016/1017/1018/1019, and DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE (now archived; see §"DELIB Archival" below).

## Implementation Evidence (Slice 1 deliverables)

### Change 1 — TOML schema extension

`groundtruth-kb/templates/rules/canonical-terminology.toml` modified:
- Added `required_primer_terms` field per profile (4 profiles: local-only, dual-agent, dual-agent-webapp, harness-memory). Each list contains 21 generic owner-required terms.
- Added `primer_missing_severity = "ERROR"` per profile.
- Added `primer_path = ".claude/rules/canonical-terminology.md"` in `[config.defaults]`.
- Existing `required_files` + `required_startup_terms` + `missing_severity` semantics preserved unchanged per Codex `-004.md` F1 option 1.
- Top-of-file comment updated to document the 21-generic-terms baseline + 22-with-Agent-Red GT-KB-self extension.

### Change 2 — MD primer extension (15 new term entries)

`groundtruth-kb/templates/rules/canonical-terminology.md` modified:
- New §"GT-KB Platform & Lifecycle Terms (S327, owner-required minimum)" section added between the existing 8 ADR-0001 core terms and the "Alias / Canonical Disposition" table.
- 15 new term entries (4-section format: Definition / Not to be confused with [optional] / Source / Implementation pointer [optional]):
  - GroundTruth-KB, GTKB, platform, application, hosted application, adopter, project, work item, backlog, specification, requirement, implementation proposal, implementation report, verification, dashboard, bridge.
- Multi-source attribution per Codex `-002.md` F3: each entry cites `.claude/rules/operating-model.md` §2, `AGENTS.md`, role rules, `DELIB-GTKB-IDP-TERMINOLOGY`, or other appropriate authoritative source.
- Existing 8 ADR-0001 core entries preserved verbatim.
- "Agent Red" entry NOT in template (added only in GT-KB checkout self-install per smoke-test no-leakage rule).

### Change 3 — Doctor extension

`groundtruth-kb/src/groundtruth_kb/project/doctor.py` `_check_canonical_terminology()` extended:
- Existing CONTRACT 1 (required_startup_terms vs required_files) preserved unchanged.
- New CONTRACT 2 (required_primer_terms vs primer file content) added after existing loop.
- Both contracts feed into the same `missing_report` list; status return preserved.
- Per Codex `-004.md` F1 option 1: dual-contract evaluation; no parallel doctor check.
- Lines added: ~30 new lines after existing `for term in required_terms` loop.

### Change 4 — GT-KB checkout dogfood install

Created at `.claude/rules/canonical-terminology.md` and `.claude/rules/canonical-terminology.toml`:
- MD: 19+ KB; rendered from extended template with `{{PROJECT_NAME}}` substituted to `"GroundTruth-KB"`; "Agent Red" entry added post-render (GT-KB-self-only) for the 22-term self-install contract.
- TOML: 5+ KB; copy of extended template with "Agent Red" added to each profile's `required_primer_terms` (post-render extension).
- Closes the dogfood gap that motivated the Slice 1 work.

### Change 5 — Tests

`groundtruth-kb/tests/test_doctor_canonical_terminology.py` extended with 5 new tests:
- `test_required_primer_terms_cover_21_template_minimum` (parametrized × 4 profiles): verifies template covers 21 generic terms + asserts "Agent Red" is NOT in template (GT-KB-self-only).
- `test_doctor_passes_when_primer_contains_all_required_primer_terms`: fresh dual-agent scaffold passes both contracts.
- `test_doctor_fails_when_primer_missing_a_required_term`: removing "GTKB" from primer triggers FAIL with `primer term` distinction in message.
- `test_doctor_does_not_force_22_terms_into_startup_files`: primer-only terms removed from CLAUDE.md → doctor still passes (existing required_startup_terms semantics preserved per Codex `-004.md` F1 option 1).
- `test_doctor_fails_when_primer_file_missing`: removing primer file triggers existing glossary-missing branch.

### Change 6 — Golden fixtures regenerated

`groundtruth-kb/tests/fixtures/scaffold_golden/{local-only,dual-agent}/` regenerated via `scripts/_capture_scaffold_golden.py` to reflect the extended primer template. TP14 + TP15 byte-level diff tests pass.

## Approval Packets

Two packets per `GOV-ARTIFACT-APPROVAL-001`:

1. `.groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1.json` — managed-rule template batch covering Changes 1, 2, 3, 4, 5 (TOML, MD, doctor.py, GT-KB install, tests).
   - artifact_type: `managed_rule_template_batch`
   - approved_by: `owner` via AskUserQuestion
2. `.groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1-delib.json` — DELIB archival packet.
   - artifact_type: `deliberation`
   - SHA256: `a1e6e85059d7a10dd616a72f0f1fb4aa62ae9466a81ae8c76894cef14e894efc`

## DELIB Archival

`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived:
- source_type: `owner_conversation`
- outcome: `owner_decision`
- session_id: `S327`
- source_ref: `owner_conversation:2026-05-02-S327-term-primer-startup-directive`

## Verification Evidence

### Test sweep — pytest

```
$ python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py
======================= 84 passed, 1 warning in 19.28s ========================
```

Net: existing 76 tests preserved + 8 new tests (4 parametrized + 4 standalone) added in this Slice 1. Single warning is pre-existing chromadb deprecation noise unrelated to this slice.

### Test breakdown

- `test_doctor_canonical_terminology.py`: 24 passed (16 existing + 8 new).
- `test_scaffold_smoke.py`: pass on all 3 leakage tests after Agent Red removal from template (initial regression caught and resolved).
- `test_scaffold_isolation.py` TP14/TP15 golden fixtures: pass after fixture regeneration (initial regression caught and resolved).
- `test_managed_registry.py` + `test_scaffold_project.py`: pass.

### Ruff

```
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
All checks passed!
```

## Acceptance Criteria Check (Slice 1)

| Criterion (from `-005.md` Acceptance) | Status |
|---|---|
| `.claude/rules/canonical-terminology.{md,toml}` installed in GT-KB checkout | SATISFIED |
| `required_primer_terms` field added per profile in TOML | SATISFIED — 4 profiles, 21 generic terms each (template); 22 with Agent Red (GT-KB self-install) |
| Existing `required_startup_terms` semantics preserved unchanged | SATISFIED — verified by T6b (`test_doctor_does_not_force_22_terms_into_startup_files`) |
| `_check_canonical_terminology()` extended to evaluate both contracts | SATISFIED — verified by T5 (`test_doctor_passes_when_primer_contains_all_required_primer_terms`) |
| Smart-poller dispatch additive (T8) | DEFERRED to Slice 3 — Slice 1 scope is dogfood install + doctor extension; dispatch wiring is Slice 3 |
| AGENTS.md non-conflicting subset | DEFERRED to Slice 4 — Slice 1 scope is template + dogfood install; AGENTS.md reconciliation is Slice 4 |
| T1-T14 + T6b pass | SATISFIED for T1-T7, T6b, T11, T14; T8/T10 deferred to Slice 3; T9 deferred to Slice 4; T12/T13 deferred to Slice 5 |
| Existing 15+ canonical-terminology tests still pass (T11) | SATISFIED — full sweep clean |
| IPR + CVR per `GOV-20` | NOT REQUIRED — Slice 1 is dogfood install + extension of verified canonical-terminology surface; no new ADR/DCL needed (the `gtkb-canonical-terminology-surface-implementation-012.md` thread carries the architecture) |
| Slice 1 template changes carry approval packet | SATISFIED — 2 packets at `.groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1{,-delib}.json` |
| `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` archived | SATISFIED |
| Ruff + lint clean | SATISFIED |

## Files Touched (Slice 1)

Modified (template + source code):
- `groundtruth-kb/templates/rules/canonical-terminology.toml`
- `groundtruth-kb/templates/rules/canonical-terminology.md`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/` (regenerated)
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/` (regenerated)

Created (GT-KB checkout dogfood install):
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/canonical-terminology.toml`

Created (formal-artifact-approval packets):
- `.groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1.json`
- `.groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1-delib.json`

KB rows inserted:
- `deliberations` table: `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` v1

No new spec rows for this Slice 1 (no new ADR/DCL/GOV; the verified `gtkb-canonical-terminology-surface-implementation-012` thread already carries the architecture).

## Notes for Loyal Opposition

- **22-term split (21 + 1).** The 22-term owner directive is split between adopter-applicable (21 generic) and GT-KB-self-only (1 instance term: "Agent Red"). Smoke test enforces the split via leakage detection. Test `test_required_primer_terms_cover_21_template_minimum` includes an inverse assertion that "Agent Red" must NOT be in the adopter template.
- **Initial regression caught + resolved.** First test run after the initial template extension produced 5 failures (3 smoke-test leakage + 2 golden fixture). Both clusters were caused by including "Agent Red" in the adopter template; resolved by moving it to the GT-KB-self-install layer + regenerating golden fixtures. This was the "Agent Red leakage incident" insight in the post-impl narrative.
- **Doctor message format preserved.** The success-path message in `_check_canonical_terminology` was preserved verbatim (existing tests check substring `"3 required terms"`/`"5 required terms"`). The error-path message naturally includes new "primer term" entries when the primer-content contract is violated.
- **Smart-poller dispatch + AGENTS.md reconciliation are Slice 3 + Slice 4.** Per `-005.md` §"Sequencing", Slice 1 covers the dogfood install + doctor extension; later slices add the dispatch and AGENTS.md integration.
- **No regression in adjacent test suites.** Full sweep over canonical-terminology + smoke + isolation + managed-registry + scaffold-project tests = 84 passed; 0 failed; 1 pre-existing warning.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
