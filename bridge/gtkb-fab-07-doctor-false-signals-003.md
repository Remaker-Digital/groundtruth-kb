REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-07-doctor-false-signals
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-07-doctor-false-signals-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4419
Project Authorization: PAUTH-FAB07-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["AGENTS.md", ".claude/rules/canonical-terminology.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/project-root-boundary.md", ".groundtruth/formal-artifact-approvals/*.json", "groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py", "platform_tests/scripts/**"]

No KB mutation: FAB-07 READS the deliberations table (HYG-049) and memory/pending-owner-decisions.md (HYG-067); it does NOT mutate `groundtruth.db`. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-07 — Repair doctor false signals + demo-apps phantom claim

WI-4419 (FAB-07) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-049, HYG-035, HYG-067, HYG-068.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

## Revision Scope

REVISED-003 responds to the two NO-GO findings in
`bridge/gtkb-fab-07-doctor-false-signals-002.md`:

- **F1 (protected-narrative packet artifacts not in target_paths):** added
  `.groundtruth/formal-artifact-approvals/*.json` to `target_paths` so the per-file
  narrative approval packets the implementation must create (for the HYG-035 edits to
  `AGENTS.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/acting-prime-builder.md`,
  `.claude/rules/project-root-boundary.md`) fall inside the GO'd path-scope.
- **F2 (missing bridge doc not concretely identified):** REMOVED the
  create-the-doctor-surfaced-missing-bridge-doc step from FAB-07 scope. Per Codex's offered
  path 2, that creation is routed out as a separate item (see `## Deferred Follow-On`). FAB-07
  no longer defers a target_path identification to implementation time; every artifact the
  implementation creates or modifies is now concrete in `target_paths`.

No other substantive change; the four doctor false-signal fixes, the HYG-035 reword/carve-out,
the spec-derived verification plan, and the ruff gates are unchanged from -001.

## Summary

Four doctor false-signals that train alarm fatigue (burying real FAILs) + a phantom-artifact
narrative claim:

- **HYG-049:** the doctor's "DA harvest coverage 1.31% (2/153) FAIL" is a **false alarm** —
  real coverage is 100%. The check (`harvest_coverage.py`) matches only the old exact-wildcard
  `source_ref` while the harvester now writes per-file refs; the FAIL persists forever.
- **HYG-035:** AGENTS.md + the glossary + acting-prime-builder.md assert "four small demo
  applications" that resolve to **nothing** under `applications/`; the real artifacts are 5 dirs
  under `groundtruth-kb/examples/` — the phantom-artifact pattern the glossary itself warns about.
- **HYG-067:** the doctor's AUQ-coverage FAIL (92.0%, 46 non-AUQ) is **polluted** — the sampled
  non-AUQ entries are owner-decision-tracker prose-pattern false positives already resolved; the
  defect is detector precision, not missing decisions.
- **HYG-068:** the doctor isolation suite runs adopter-context checks (`product-scope-writable`,
  `subject-expected-application`) **unconditionally against the platform root**, producing standing
  miscalibrated FAILs.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4419 is the governed backlog authority.
- `GOV-ARTIFACT-APPROVAL-001` — the HYG-035 edits (AGENTS.md, canonical-terminology.md,
  acting-prime-builder.md, project-root-boundary.md) are protected narrative artifacts requiring
  per-file approval packets recorded under `.groundtruth/formal-artifact-approvals/`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — HYG-035 adds an owner-decided **examples carve-out**
  to project-root-boundary.md (examples are test/scaffold fixtures, not applications), and HYG-068
  fixes the isolation suite to run adopter-context checks only in an adopter context.

## Isolation Placement Compliance

FAB-07 edits only **in-root** files under `E:\GT-KB` and writes **no** out-of-root artifacts (this
bridge file is under `E:\GT-KB\bridge\`; the narrative packets are under
`E:\GT-KB\.groundtruth\formal-artifact-approvals\`). It **relocates nothing** — the HYG-035
examples carve-out narrows the project-root-boundary rule rather than moving any subtree, and the
HYG-068 fix makes the isolation suite adopter-conditional without changing any placement. Consistent
with `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (which governs application placement, not example
fixtures or doctor-check calibration).

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-049/035/067/068).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB07-REMEDIATION-20260610` — this cluster's owner-decision set.
- _`bridge/gtkb-da-harvest-coverage-implementation-004/-005` is the source-ref convention HYG-049
  supersedes (per-file refs replaced the wildcard form post-2026-05-11)._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB07-REMEDIATION-20260610`:

1. **HYG-035 = Reword + carve-out** — reword the three claims to cite `groundtruth-kb/examples/`
   (4 adopter fixtures + task-tracker, real count) and add a one-line examples carve-out to
   project-root-boundary.md. (Rejected: move-task-tracker; delete-claim.)
2. **HYG-049 = Fix the check (prefix match)** — change `harvest_coverage.py` to prefix-match
   `bridge/{name}-%`; no DB writes; doctor check becomes truthful (153/153). (Rejected: fix-harvester; both.)

Determined detector fixes (no owner AUQ — detector precision/calibration):
3. **HYG-067** — tighten the doctor AUQ-coverage check so resolved/false-positive entries don't
   count as missing coverage.
4. **HYG-068** — make the isolation suite conditional (adopter-context checks only in an adopter
   context, not against the platform root).

## Requirement Sufficiency

**Existing requirements sufficient.** The doctor-check fixes restore truthful signals (no new
requirement); the HYG-035 carve-out is the owner-decided narrowing of project-root-boundary.md per
`DELIB-FAB07-REMEDIATION-20260610`. No new requirement needed.

## Scope and Boundaries

In scope: the 4 doctor false-signal fixes + the HYG-035 reword/carve-out + the per-file narrative
packets the protected edits require. Out of scope: moving `groundtruth-kb/examples/` or
`task-tracker` into `applications/` (the owner chose reword, not relocate); the broader
isolation-contract work; and (per F2) the doctor-surfaced missing-bridge-doc creation, now routed
to a separate item.

## Proposed Implementation

1. **HYG-049:** in `harvest_coverage.py:104-117`, replace the exact `source_ref = 'bridge/{name}-*.md'`
   numerator with a regex-escaped prefix match (`LIKE 'bridge/{name}-%'`); update the helper's test.
2. **HYG-035:** reword AGENTS.md L11, the canonical-terminology.md Agent Red entry, and
   acting-prime-builder.md to name `groundtruth-kb/examples/` with the real count (4 fixtures +
   task-tracker); add a one-line examples carve-out to project-root-boundary.md (each a narrative
   packet recorded under `.groundtruth/formal-artifact-approvals/`).
3. **HYG-067:** tighten the doctor AUQ-coverage check (`doctor.py`) so entries already resolved in
   `memory/pending-owner-decisions.md` (and prose-pattern false positives) are excluded from the
   "missing AUQ" numerator.
4. **HYG-068:** gate `doctor_isolation.py:219-272` adopter-context checks on an adopter/application
   context so they no longer FAIL against the platform root.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| DA-harvest doctor check (HYG-049) | a test asserts `compute_active_bridge_thread_coverage` reports 153/153 under per-file refs; the doctor check passes; a genuine gap still FAILs |
| `GOV-ARTIFACT-APPROVAL-001` (HYG-035) | grep: the three files cite `groundtruth-kb/examples/` (no unresolvable "four demo applications"); project-root-boundary.md has the examples carve-out; each protected edit has a packet under `.groundtruth/formal-artifact-approvals/` |
| AUQ-coverage precision (HYG-067) | a test asserts resolved/false-positive entries don't count as missing; a genuinely-missing AUQ still FAILs |
| isolation-suite calibration (HYG-068) | a test asserts the adopter-context checks are skipped against the platform root and run in an adopter context |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check`/`format --check` on the changed `.py` |

## Acceptance Criteria

1. The DA-harvest doctor check reports true coverage (153/153) and FAIL means a real gap.
2. The three narrative files cite `groundtruth-kb/examples/`; project-root-boundary.md has the carve-out.
3. The AUQ-coverage check excludes resolved/false-positive entries; the isolation suite is adopter-conditional.
4. Each protected edit has its narrative packet under `.groundtruth/formal-artifact-approvals/`; tests pass; ruff-clean.

## Deferred Follow-On

The create-the-doctor-surfaced-missing-bridge-doc step from -001 is REMOVED from FAB-07 scope
(NO-GO F2). The doctor's missing-doc check surfaces a referenced-but-absent bridge documentation
artifact; identifying and creating it is routed as a **separate standing backlog item** so its
concrete path, overlap, and approval/verification path can be reviewed on its own merits rather than
deferred to FAB-07 implementation time. This keeps every FAB-07 target_path concrete and reviewable.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-07-doctor-false-signals-003.md` with a matching `REVISED` line inserted at
the top of this thread's entry in `bridge/INDEX.md`; append-only, no prior bridge version deleted or
rewritten. The HYG-049 fix corrects a *coverage-reporting* convention; it does not alter
`bridge/INDEX.md` as canonical workflow state or the bridge versioning discipline
(`GOV-FILE-BRIDGE-AUTHORITY-001` preserved) — it makes the DA-harvest coverage signal *truthful*.

## Backlog Visibility

FAB-07 is WI-4419 under `GOV-STANDING-BACKLOG-001`; this REVISED does not perform any bulk backlog
operation. The deferred missing-doc creation will be captured as its own inventory item in the
standing backlog (no DECISION DEFERRED beyond the routing already stated).

## Risk and Rollback

- **Risk:** loosening a check hides a real FAIL → each fix is verified to still FAIL on a genuine gap
  (the tests include a real-gap fixture); only false positives / convention artifacts are corrected.
- **Rollback:** revert the helper/doctor edits and the narrative packets; no MemBase mutation to undo.

## Recommended Implementation Routing

**Mixed.** The `harvest_coverage.py` prefix-match + the isolation-suite gating are mechanical
(cheap-model-eligible under supervision); the AUQ-coverage precision logic and the protected
narrative edits are Opus/Codex-supervised (the latter gated by per-file packets).

## Recommended Commit Type

`fix:` — corrects four false doctor signals (with `docs:`-class narrative corrections + the carve-out).
