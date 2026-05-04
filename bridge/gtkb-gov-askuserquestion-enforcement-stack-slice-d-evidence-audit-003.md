REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice D: Durable Evidence Audit (REVISED-1)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-001.md` per Codex `-002` NO-GO (F1 orphan-ID, F2 schema validation, F3 cleanup-scope)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Revision Summary

Codex `-002` NO-GO surfaced three blocking findings + two non-blocking observations. REVISED-1 addresses all of them:

- **F1 (orphan-ID detection not implemented)** — REVISED-1 adds explicit reference-extraction logic (scans `notes`, `question`, `answer` fields for `DECISION-NNNN` patterns), cross-references against the parsed entry-ID set across `## Pending`/`## Resolved`/`## History`, reports orphans. New fixture-backed unit test + live-file integrity test.
- **F2 (schema validation too weak)** — REVISED-1 replaces ad hoc regexes with a copy-to-tempfile dance that uses the canonical `_read_pending_file` parser, then validates parsed `DecisionEntry` instances against the dataclass schema (required fields: `id` with `DECISION-` prefix, `asked_at`, `status`; recognized `detected_via` values; no duplicate IDs; entries in correct section). The copy-to-tempfile pattern is required because `_read_pending_file` has corruption-preservation rename behavior at `.claude/hooks/owner-decision-tracker.py:430-438` — running it directly against the live file on parse failure would rename the live file to `.corrupted-<ts>`. Tempfile isolation contains that mutation harmlessly.
- **F3 (cleanup-scope deviation from umbrella)** — Owner AUQ S332 selected "Include bounded cleanup in D" (Path 1). REVISED-1 adds a bounded mutating step: historical false-positive entries (entries in `## Pending` with `detected_via: prose:*` AND `asked_at` predating Sub-slice A `-014` VERIFIED) are moved to `## History` via atomic write (temp file + `os.replace`). The mutation is idempotent (re-runs produce no further changes), audit-evidenced (every mutation logged), and AUQ-entry-safe (`detected_via: ask_user_question` entries are never moved).
- **Non-blocking #1 (test commands lack file paths)** — REVISED-1 uses fully-qualified `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::<test>` invocations.
- **Non-blocking #2 (claim "reuses parsing helpers" without import)** — REVISED-1 makes the claim true by importing `_read_pending_file` into the audit script via `importlib.util.spec_from_file_location` (the hook is not a regular Python module — it's a `.py` file in `.claude/hooks/`).

## Specification Links

**Blocking (per applicability registry):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links section requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** all changes within `E:\GT-KB\` platform root; Sub-slice D modifies `scripts/`, `groundtruth-kb/tests/`, and (per F3) `memory/pending-owner-decisions.md` cleanup. No `applications/` content modified.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol rules including Mandatory Owner Decisions / Input Section Gate (Sub-slice C).
- `.claude/rules/codex-review-gate.md` — pre-implementation review requirement.
- `.claude/rules/loyal-opposition.md` — review verdict authority.
- `.claude/rules/project-root-boundary.md` — explicit root boundary.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice D" lines 181-184 — umbrella-approved scope (audit + cleanup pass).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) — Sub-slice A boundary date for historical-FP detection threshold.

**Topic-specific:**

- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` (VERIFIED) — Sub-slice B AUQ-only rule.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-006.md` (VERIFIED) — Sub-slice C bridge-compliance-gate.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED) — original durable-file format (`GOV-OWNER-DECISION-SURFACING-001`).
- `memory/pending-owner-decisions.md` — audit target (read for audit; bounded mutation for cleanup).
- `.claude/hooks/owner-decision-tracker.py` — hook owning the file format. Audit script imports `_read_pending_file` and `DecisionEntry` from this file.

**Advisory (cited per Codex `-002` Advisory Notes pattern):**

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — bias toward artifacts. **How this slice complies:** durable bridge artifact + durable test module + durable audit script.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — standard NEW → REVISED → GO → impl → REPORT → VERIFIED lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner-decision recorded via AUQ, not prose; spec mutations governed by formal-artifact-approval.

## Prior Deliberations

- `DELIB-S331-AUQ-1` (block ISOLATION-018; enforcement first), `DELIB-S331-AUQ-2` (full 6-mechanism stack), `DELIB-S331-AUQ-3` (autonomous progression) — umbrella authorization.
- `DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE` (this turn, S332): Owner AUQ selected Path 1 "Include bounded cleanup in D" over Path 2 "Formally defer cleanup" and Path 3 "Conditional no-op". `detected_via: ask_user_question`. Authorizes the F3 disposition in this REVISED-1.
- `DELIB-S309-PROSE-FP-DECISION-0001-DECISION-0002` — historical FP evidence; defines the pre-tightening false-positive class that the cleanup pass targets.
- Sub-slices A/B/C VERIFIED records (cited above in Spec Links).
- No prior NO-GO on the audit-and-cleanup design itself; the `-002` NO-GO was an under-specification finding, not a design rejection.

## Owner Decisions / Input

- **AUQ S332 #1 (this turn):** "Which next-actionable work should I take up while Codex reviews Sub-slice D `-001`?" → "Sub-slice A follow-up (code-fence guards)". `detected_via: ask_user_question`. Authorizes the parallel A code-fence-guards bridge thread; does not directly authorize this D revision.
- **AUQ S332 #2 (this turn):** "Sub-slice D NO-GO F3 (cleanup-scope) disposition" → "Include bounded cleanup in D" (Path 1). `detected_via: ask_user_question`. **This is the authorizing decision for the F3 cleanup-included design in this REVISED-1.** Owner explicitly chose to keep umbrella scope (audit + cleanup) intact and not amend the umbrella to defer cleanup.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice revisions.
- **No additional owner decisions required pre-implementation.** Codex GO/NO-GO governs proceed.

## Goal

1. **Audit script** `scripts/audit_pending_owner_decisions.py` reads `memory/pending-owner-decisions.md` (via copy-to-tempfile + canonical parser) and reports: schema-validation status per entry, malformed-entry list, orphan-ID list, `detected_via` distribution, historical-FP candidate list (entries that the cleanup step would move).
2. **Cleanup mode** (per owner Path 1): when invoked with `--cleanup`, atomically moves historical-FP entries from `## Pending` to `## History` via temp file + `os.replace`. Idempotent. AUQ-entry-safe. Logged.
3. **Tests** exercise audit logic (against fixture files + live file) AND cleanup logic (against fixture files only; live file is byte-stable in test mode).
4. **Live audit + cleanup** runs documented in post-impl REPORT.

## Implementation Plan

### Step 1: Audit script with canonical-parser-based validation + orphan detection + cleanup mode

Create `scripts/audit_pending_owner_decisions.py`. Key implementation points:

1. **Canonical parser import.** Load `_read_pending_file` and `DecisionEntry` from `.claude/hooks/owner-decision-tracker.py` via `importlib.util.spec_from_file_location` (the hook is not on `sys.path`).
2. **Copy-to-tempfile dance.** For audit and validation paths, copy `memory/pending-owner-decisions.md` to `tempfile.NamedTemporaryFile(suffix='.md', delete=False)`. Run `_read_pending_file(temp_path)`. If parse fails, the corruption-rename targets the temp copy (harmless). If parse succeeds, validate the resulting `dict[str, list[DecisionEntry]]` against schema rules below. Always clean up temp file in `finally`.
3. **Schema validation rules (F2):**
   - Every entry's `id` starts with `DECISION-` and matches `DECISION-\d+`.
   - Every entry has non-empty `asked_at` (parseable as ISO-8601 timestamp).
   - Every entry has `detected_via` in the recognized set: `ask_user_question`, `prose:offering_or_choice`, `prose:should_i_or`, `prose:awaiting_input_q`, `prose:awaiting_input_first_person`, `prose:standing_by_for_q`, `prose:standing_by_for_first_person`, `prose:your_decision_q`. Unrecognized values reported.
   - Every entry has `status` matching its section: `## Pending` → status `pending`; `## Resolved`/`## History` → status `resolved` (or other non-`pending`).
   - Entry IDs are unique across all three sections (no duplicates).
   - No entry in the wrong section (resolved-status entry under `## Pending`, etc.).
4. **Orphan-ID detection (F1):**
   - Build set of all entry IDs across all three sections.
   - Scan `notes`, `question`, `answer` fields for the pattern `DECISION-\d+`.
   - Reference-but-not-present IDs reported as orphans.
5. **Historical-FP detection (F3 prep):**
   - An entry qualifies as historical-FP iff: in `## Pending` AND `detected_via` starts with `prose:` AND `asked_at` parseable as a date earlier than Sub-slice A `-014` VERIFIED date (2026-05-04 UTC; cite the file's git mtime as the canonical reference).
6. **Cleanup mode (`--cleanup`) per owner Path 1:**
   - Run audit first. List historical-FP candidates.
   - For each candidate: append to `## History` section; remove from `## Pending` section.
   - Append a `notes` field to each moved entry: `notes: "Moved from ## Pending to ## History by Sub-slice D cleanup audit on 2026-05-04 per DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE; pre-tightening false positive (Sub-slice A -014 VERIFIED 2026-05-04)."`
   - Write rebuilt file to `<path>.tmp`, then `os.replace(<path>.tmp, <path>)`. Atomic.
   - Log each mutation to stdout AND to `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` (append-only).
   - **Idempotent guard:** if a candidate's `notes` field already contains "Sub-slice D cleanup audit", skip it (already moved; don't double-move).
   - **AUQ-entry safety guard:** if `detected_via == "ask_user_question"`, raise `RuntimeError` and abort cleanup before any mutation. AUQ entries never move.
7. **Output modes:** `--json` for machine, default for human.

### Step 2: Tests

Create `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` with the following test set:

| Test ID | Purpose | Fixture or Live |
|---|---|---|
| `test_audit_schema_valid_live` | Live file parses via canonical parser | Live (read-only, copy to temp) |
| `test_audit_schema_required_fields_live` | All entries have `id`, `asked_at`, `detected_via`, `status` | Live |
| `test_audit_no_duplicate_ids_live` | No duplicate IDs across sections | Live |
| `test_audit_correct_section_placement_live` | Each entry in correct section per status | Live |
| `test_audit_recognized_detected_via_live` | All `detected_via` values from recognized set | Live |
| `test_audit_orphans_fixture` | Synthetic orphan reference detected | Fixture (`tmp_path` with crafted entries) |
| `test_audit_orphans_live` | No orphan references in live file | Live |
| `test_cleanup_idempotency_fixture` | Re-running cleanup produces no further mutations | Fixture |
| `test_cleanup_auq_safety_fixture` | Cleanup raises and aborts when AUQ entry would be moved | Fixture |
| `test_cleanup_atomic_write_fixture` | Write is atomic (no `.tmp` left after success) | Fixture |
| `test_cleanup_does_not_mutate_live_in_test_run` | Test suite leaves live file byte-stable | Live (snapshot SHA-256 before + after, assert equal) |
| `test_audit_corruption_path_isolated` | Audit's tempfile copy absorbs corruption rename | Fixture (deliberately malformed input) |

The corruption-isolation test directly verifies the F2 fix: a deliberately malformed input causes `_read_pending_file` to invoke its corruption-rename path, but only the temp copy is renamed, not the test's live-file proxy.

### Step 3: Live audit + live cleanup runs (post-impl)

Post-impl REPORT captures:

```text
python scripts/audit_pending_owner_decisions.py --json > /tmp/audit-pre.json
python scripts/audit_pending_owner_decisions.py --cleanup
python scripts/audit_pending_owner_decisions.py --json > /tmp/audit-post.json
```

Pre/post JSON included in REPORT. Audit log at `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` committed.

### Step 4: Single commit on `develop`

Files added/modified in commit:
- `scripts/audit_pending_owner_decisions.py` (new)
- `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` (new)
- `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` (new; mutation evidence)
- `memory/pending-owner-decisions.md` (mutated; cleanup applied)

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify INDEX.md entry exists | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit` | `preflight_passed: true` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-impl REPORT carries spec-to-test mapping with executed evidence | Codex VERIFIED |
| **T-out-of-applications-D** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only \| grep "^applications/"` | Empty |
| **T-audit-schema-live** | F2 schema validation | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_schema_valid_live -v` | PASS |
| **T-audit-required-fields-live** | F2 required fields | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_schema_required_fields_live -v` | PASS |
| **T-audit-no-duplicate-ids-live** | F2 unique IDs | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_no_duplicate_ids_live -v` | PASS |
| **T-audit-section-placement-live** | F2 correct section | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_correct_section_placement_live -v` | PASS |
| **T-audit-detected-via-live** | F2 recognized values | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_recognized_detected_via_live -v` | PASS |
| **T-audit-orphans-fixture** | F1 orphan detection logic | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_orphans_fixture -v` | PASS |
| **T-audit-orphans-live** | F1 live integrity | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_orphans_live -v` | PASS |
| **T-cleanup-idempotent** | F3 idempotency | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_cleanup_idempotency_fixture -v` | PASS |
| **T-cleanup-auq-safe** | F3 AUQ-entry safety | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_cleanup_auq_safety_fixture -v` | PASS |
| **T-cleanup-atomic** | F3 atomic write | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_cleanup_atomic_write_fixture -v` | PASS |
| **T-cleanup-no-live-mutation-in-tests** | F3 + acceptance #2 | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_cleanup_does_not_mutate_live_in_test_run -v` | PASS |
| **T-corruption-isolation** | F2 corruption-rename containment | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_corruption_path_isolated -v` | PASS |
| **T-platform-smoke** | Platform integrity | `python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook" -x --timeout=60` | PASS or pre-existing-known-failures only |
| **T-audit-snapshot** | Pre/post audit captured | Pre-cleanup + post-cleanup `--json` outputs in REPORT | Both present |
| **T-cleanup-log** | F3 mutation evidence | `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` exists with one log line per mutation | Lines present |

## Specification-to-Test Mapping

| Spec / Finding | Tests |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-D |
| Codex `-002` F1 orphan-ID | T-audit-orphans-fixture, T-audit-orphans-live |
| Codex `-002` F2 schema validation | T-audit-schema-live, T-audit-required-fields-live, T-audit-no-duplicate-ids-live, T-audit-section-placement-live, T-audit-detected-via-live, T-corruption-isolation |
| Codex `-002` F3 cleanup (Owner Path 1) | T-cleanup-idempotent, T-cleanup-auq-safe, T-cleanup-atomic, T-cleanup-no-live-mutation-in-tests, T-cleanup-log |
| Umbrella `-003` §"Sub-slice D" cleanup pass | T-cleanup-* + T-audit-snapshot (pre/post evidence) |
| Platform integrity | T-platform-smoke |

## Acceptance Criteria

Pre-implementation:
- [ ] Codex GO on this REVISED-1 proposal
- [ ] Preflight passes (`missing_required_specs: []`)

Post-implementation (VERIFIED contingent):
- [ ] All 19 tests T-bridge-1 through T-cleanup-log PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Live `memory/pending-owner-decisions.md` shows expected cleanup mutation (historical FPs moved to `## History`); pre/post JSON snapshots in REPORT prove the change
- [ ] Live `memory/pending-owner-decisions.md` is byte-stable across the **test suite run** (mutation only happens via the explicit `--cleanup` invocation in Step 3, not via tests)
- [ ] Test suite leaves `git status --short` empty after running (test fixtures use `tmp_path`)
- [ ] No regression in GT-KB platform tests
- [ ] `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` committed with one line per mutation

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Cleanup mutation corrupts the live file | Low | High | Atomic write via `os.replace`; canonical parser used to parse temp copy first; pre-cleanup byte-snapshot captured for diff verification; post-cleanup parse re-validation |
| Cleanup moves an AUQ entry by mistake | Low | High | Explicit AUQ safety guard raises `RuntimeError` and aborts before any write if any candidate has `detected_via: ask_user_question` |
| Audit's canonical-parser invocation triggers corruption-rename of live file | Low | High | Copy-to-tempfile dance; corruption-rename targets temp copy only; live file untouched |
| Idempotency violation (re-run double-mutates) | Low | Medium | `notes` field marker check before move; tested via `test_cleanup_idempotency_fixture` |
| Sub-slice A `-014` VERIFIED date threshold wrong | Low | Medium | Threshold derived from git mtime of `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md`; cite computation in REPORT; owner can re-tune by updating threshold constant + re-running |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter |

**Rollback:** `git revert` of the single commit reverses script + tests + audit log. Live-file mutation rollback is bounded: the cleanup-moved entries can be moved back from `## History` to `## Pending` by reverse-applying the audit log; or simpler, `git checkout HEAD~1 -- memory/pending-owner-decisions.md` restores pre-cleanup state.

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit
python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py -v --timeout=60
python scripts/audit_pending_owner_decisions.py --json
git status --short
git diff --stat -- memory/pending-owner-decisions.md
```

Pre-impl expected: preflight PASS / N/A (no tests yet) / N/A / clean / clean.
Post-impl expected: PASS / 12 passed / valid JSON / shows scripts+tests+log+audit-target / shows mutation diff.

## Out of Scope

- Sub-slices E (requirements-collection hook impl), F (release metrics + promotion to enforcement) — pending after D VERIFIED.
- Code-fence-aware structural FP guards — separate parallel bridge `gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04` filed in same session.
- Mutation of `## Resolved` or `## History` sections — out of scope; cleanup only moves *into* `## History`, never out.
- Cleanup of post-Sub-slice A `-014` VERIFIED entries — out of scope (the threshold defines historical-FP class).

## Decision Needed From Owner

None pre-implementation. F3 cleanup-scope disposition resolved by AUQ S332 #2 (Path 1 selected). Codex GO/NO-GO governs proceed.

## Project Root Boundary Compliance

All changes within `E:/GT-KB/`:
- `E:/GT-KB/scripts/audit_pending_owner_decisions.py` (new)
- `E:/GT-KB/groundtruth-kb/tests/test_pending_owner_decisions_audit.py` (new)
- `E:/GT-KB/memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` (new)
- `E:/GT-KB/memory/pending-owner-decisions.md` (mutated; cleanup pass per Owner Path 1)

No `applications/` content. Per `.claude/rules/project-root-boundary.md`.
