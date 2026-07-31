NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker; manual dispatch per DELIB-202667523/202667531; resolved role prime-builder for this filing

bridge_kind: prime_proposal
Document: gtkb-wi5762-pauth-accumulation-doctor
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5762

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_pauth_accumulation.py"]

# WI-5762 — Add PAUTH Accumulation Detection to Doctor: Multi-Coverage WARN, Contradictory-Set FAIL, Completion Candidates

Scope confirmation: this proposal performs no MemBase mutation and no
groundtruth.db write during filing; the implementation touches only the two
target_paths files (one existing source file, one new test module) and is
covered by the cited project authorization.

This filing performs no approval-evidence work; it requires no approval
packets. Neither target path is a protected narrative artifact.

## Problem

Project authorizations are created but effectively never completed or
revoked, so the PAUTH population accumulates monotonically and the
implementing agent effectively chooses which owner grant governs its own
work. The source advisory
(`bridge/gtkb-lo-project-authorization-accumulation-and-conflict-advisory-001.md`,
classification `adopt`) established the condition with direct evidence:

- Resolution is by cited ID only (`scripts/implementation_authorization.py:1066`,
  `SELECT * FROM current_project_authorizations WHERE id = ?`); the validator
  (`:1275-1335`) checks that one authorization in isolation, and no code path
  enumerates the OTHER active authorizations covering the same work item
  (advisory E3).
- The doctor is structurally incapable of seeing the condition:
  `_active_authorized_work_item_ids`
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:6644`) UNIONS all
  active authorizations' work items to answer under-coverage only
  (`check_standing_backlog_health`, `:6664`). There is no finding kind for
  multi-coverage, for conflicting operation sets, or for an active
  authorization whose work items are all resolved (advisory E4).
- Retirement commands exist and are unused: `gt projects
  complete-authorization` and `gt projects revoke-authorization` are
  implemented and documented, and nothing requires or prompts their use
  (advisory E5).

### Re-derived live census (2026-07-30 UTC; the advisory numbers have drifted)

Re-derived this session via read-only queries over the same read surface the
doctor uses (`current_project_authorizations WHERE status='active'`,
replicating the advisory's own explicit `included_work_item_ids` aggregation
method; census script preserved at
`.gtkb-state/propose-drafts/wi5762_pauth_census.py`, sqlite `mode=ro`):

| Measure | Advisory (2026-07-28) | Re-derived (2026-07-30) |
| --- | --- | --- |
| Active PAUTH count | 576 | 586 |
| Work items covered by 2+ active PAUTHs | 155 | 161 |
| Maximum concurrent coverage on one WI | 4 (GTKB-CORE-001) | 4 (GTKB-CORE-001) |
| Multi-covered WIs whose covering `forbidden_operations` sets differ | "at least one confirmed" | 135 (measured) |
| Multi-covered WIs whose covering `allowed_mutation_classes` sets differ | not measured | 149 |
| Active PAUTHs whose included WIs are ALL terminal (completion candidates) | not measured | 471 |
| Active PAUTHs with `expires_at` set | 0 of 576 | 21 of 586 |
| Active PAUTHs with no `included_work_item_ids` list (project-membership-wide) | not measured | 22 |

The confirmed contradictory pair from advisory E1 is still live: WI-5657
remains covered by both
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX`
(forbids `git_commit`) and
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5657-TERMINAL-RECOVERY-20260728`
(permits it), both `active`. The population grew by 10 authorizations and 6
newly multi-covered work items in roughly one day, and the "at least one"
contradiction of the advisory is in fact 135 work items when measured — the
condition is compounding, exactly as the advisory's "monotonically
increasing" note predicted.

### Today's live instance — the SF-1 revoke-and-reissue churn

The condition is not archival. On 2026-07-30T03:48:5xZ (hours before this
filing), the leader session executed the SF-1 corrective revoke-and-reissue
of BOTH
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5741-TERMINAL-RECOVERY-20260729` and
`PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` (both now v3
`active` under their original ids, unregistered forbidden token
`dispatcher_activation` replaced with registered `dispatcher_mutation`, owner
decisions DELIB-202667529 / DELIB-202667533 unchanged). Two lessons for this
work item:

1. PAUTH population state now churns under live operational load (revocation,
   reissue, program grants covering WI bands), and no mechanical observer
   watches the aggregate for duplication, contradiction, or staleness — the
   SF-1 defect itself was found only because the WI-5760 proposal worker
   hand-ran an evaluation no gate required.
2. **Composition boundary:** the companion work item WI-5785 owns the SF-1
   defect class itself — issuance-time token validation in `gt projects
   authorize` plus a candidate doctor check for ACTIVE authorizations whose
   token sets no longer resolve against the operation taxonomy. WI-5762 does
   NOT absorb WI-5785: this check detects population-shape defects
   (multi-coverage, contradictory sets, completion candidates); WI-5785's
   candidate check detects token-resolution poisoning. The two checks compose
   side by side in the doctor and share no finding kinds.

## Proposed Change

One additive, non-gating doctor detection check — the advisory's own first
slice ("lowest risk, do first"). Modeled structurally on the adjacent
`check_standing_backlog_health` (payload function at `doctor.py:6664`) +
`_check_standing_backlog_health` (ToolCheck wrapper at `:6812`) + its
registration (`checks.append(...)` at `:7294`), which is the established
pattern for MemBase-backed doctor checks.

### New payload function: `check_project_authorization_hygiene(target)`

Machine-readable payload (`schema_version: 1`, `check:
"project_authorization_hygiene"`) computed from
`db.list_project_authorizations(status="active")` (the existing read surface
at `groundtruth-kb/src/groundtruth_kb/db.py:6046`, already consumed by
`_active_authorized_work_item_ids`) and work-item terminality via the
existing work-item read surfaces against
`WORK_ITEM_TERMINAL_RESOLUTION_STATUSES` (`db.py:210`). Finding kinds:

- **(a) WARN `multi-coverage`** — a work item listed in the
  `included_work_item_ids` of two or more active authorizations. The finding
  carries the work item id and the full covering-authorization id set, so a
  reviewer can answer "which grants govern this WI?" from the doctor payload
  alone (the advisory's audit-ambiguity harm).
- **(b) FAIL `contradictory-authorization-set`** — a multi-covered work item
  whose covering active authorizations carry two or more DISTINCT
  `forbidden_operations` sets (the advisory's contradiction definition: a
  contradiction, not merely a duplication — one grant forbids what another
  permits). The finding carries, per covering authorization, its
  `forbidden_operations` and `allowed_mutation_classes` sets so
  allowed-class divergence (149 WIs) is visible in the same finding without
  being an independent FAIL trigger in this slice (see OD-B).
- **(c) WARN `completion-candidate`** — an active authorization whose
  `included_work_item_ids` is non-empty and whose included work items are ALL
  terminal per `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES`. Detection only: it
  names the authorization and its resolved work items as a candidate for
  `gt projects complete-authorization`.
- Informational summary counts (not findings): active total, active with
  `expires_at`, project-membership-wide authorizations (null/empty included
  list — these cover via project membership and are counted distinctly, not
  folded into multi-coverage in this slice; see OD-C), and per-kind finding
  counts. Unreadable/unparseable authorization rows and a missing
  `groundtruth.db` produce FAIL `missing-evidence` findings (fail closed,
  same as the adjacent check).

Severity aggregation identical to the adjacent check: `fail` if any FAIL,
else `warning` if any WARN, else `pass`.

### New ToolCheck wrapper + registration

`_check_project_authorization_hygiene(target) -> ToolCheck` renders count
summaries only (e.g. "PAUTH hygiene: 135 contradictory-set FAIL, 161
multi-coverage WARN, 471 completion candidates"), never the full 700+ finding
list, mirroring `_check_standing_backlog_health`'s message discipline.
Registered via `checks.append(_check_project_authorization_hygiene(target))`
adjacent to the standing-backlog registration at `doctor.py:7294`.

### Severity calibration is owner-fixed, and the doctor WILL go red

The advisory's owner-grilling question 2 (FAIL vs WARN tolerance) was
resolved by the owner triage: the authorized WI-5762 title fixes
"multi-coverage WARN, contradictory-set FAIL, completion candidates"
(DELIB-202667531 fix-class authorization; DELIB-202667534 disposition table).
Against the measured population this means the doctor reports 135 FAIL
findings on day one. That is the owner-chosen behavior — converting an
invisible condition into a measured red surface with a drain-down target —
not a regression introduced by this change. The check is additive and
non-gating: no commit gate, hook, preflight, or session flow consults it.

### Explicitly NOT in scope (later slices per the advisory's own sequencing)

- **Terminal-VERIFIED completion prompting** (advisory recommendation 2; the
  AT-04 completion-discipline pairing per DELIB-202667533 and the
  WI-5742-adjacent completion-prompting direction) — a later slice; this
  check only NAMES completion candidates.
- **Begin-time conflict semantics** (advisory recommendation 3, fail-closed
  vs intersection-of-permissions) — an owner decision about what an
  authorization MEANS; untouched here.
- **Backfill** of the ~471 completion candidates (advisory recommendation 4)
  — must not precede completion prompting or the population refills; subject
  to GOV-15 fix-approval and the 50-item batch maximum when it comes.
- **Token-resolution validation** — WI-5785 (composition boundary above).

## Specification Links

- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — the project-scoped authorization contract whose population integrity this check observes; multi-coverage and contradictory grants erode exactly the bounded scope this specification establishes (mandatory anchor).
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 — VERIFIED-driven completion/retirement discipline; the completion-candidate finding is its detection-side counterpart, and the prompting slice that acts on it comes later.
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 — project authorization linkage contract cited by the source advisory; the finding payloads preserve authorization identity for linkage-aware review.
- GOV-STANDING-BACKLOG-001 — WI-5762 is the MemBase backlog authority for this work; the check reads the same work-item authority for terminality.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority governing this proposal's own GO/verify lifecycle (mandatory anchor).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal's own specification-linkage duty; links above are complete against the applicability preflight.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-derived verification gate governing this thread's eventual VERIFIED; the test plan below maps every linked specification to executed tests.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both target paths are in-root platform surfaces (`groundtruth-kb/src/**`, `platform_tests/**`); no application or out-of-root placement.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — append-only artifact discipline; the check reads current rows and mutates nothing, and this thread's bridge chain stays append-only.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — authorizations are durable owner artifacts; a population whose grants never terminate degrades what the artifact system asserts, and detection restores artifact truthfulness.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — lifecycle-state discipline (active/completed/revoked); the check surfaces rows whose lifecycle state is stale relative to their work items' lifecycle.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — findings derive from fresh canonical reads of `current_project_authorizations` and current work items at doctor runtime; the re-derived census above replaces the advisory's drifted numbers per the same principle.
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 — population hygiene review becomes a deterministic service (doctor check), not per-session ad-hoc SQL.
- SPEC-1830 — operational procedures must be code, not conversation; "is this WI's authorization set clean?" becomes a check, not an investigation.
- GOV-10 — tests exercise the exposed production interfaces (the payload function and ToolCheck wrapper), not internals.
- GOV-12 — work item creation triggers test creation; the new test module lands with the check.
- SPEC-1662 (GOV-18) — assertions are behavioral (finding kinds, severities, covering-id sets, aggregation status), not shape-only.
- GOV-15 — no autonomous fixes: the check reports; completion/backfill actions remain owner-gated later slices.

## Prior Deliberations

Deliberation search performed 2026-07-29 (`gt deliberations search "project
authorization accumulation conflict" --limit 5`): top semantic hits were
DELIB-20260622-ARCHITECTURE-CLOSURE-PAUTH (bounded closure-PAUTH grant —
example of the accumulating population class), DELIB-2320, DELIB-20263760,
DELIB-202666892 (generic verdict records; non-controlling), and
DELIB-202667318 (closest controlling precedent — NO-GO on WI-5602 for citing
a topically-mismatched project authorization, establishing that authorization
citation hygiene is a reviewable property). Targeted-id reads and
authorities:

- DELIB-202667526 — live concurrency evidence from leader-session disposition filings under fleet load; the operational context that makes hand-run population audits non-viable and a mechanical observer necessary.
- DELIB-202667531 — owner triage directive: fix-class advisories become authorized corrective work items ahead of other advisory-derived work; the owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH; bridge protocol explicitly NOT waived per item.
- DELIB-202667533 — AT-01..AT-04 synthesis decisions; AT-04 establishes the program PAUTH cited by this proposal AND the completion discipline (auto-complete on terminal VERIFIED) that the later prompting slice implements — cited here as the later-slice authority, deliberately not scoped into this detection slice.
- DELIB-202667534 — advisory corpus disposition table consolidating the accumulation advisory into WI-5762 and fixing this first-slice direction (doctor detection: multi-coverage WARN, contradictory-set FAIL, completion candidates).
- DELIB-202667529 — the WI-5741 exact-scope terminal-recovery PAUTH owner decision; one of the two authorizations in today's SF-1 revoke-and-reissue instance cited under Problem.
- Source advisory: `bridge/gtkb-lo-project-authorization-accumulation-and-conflict-advisory-001.md` (E1-E6, recommendation 1 = this slice).
- Companion boundary: WI-5785 (issuance-time token validation + token-resolution doctor check candidate; SF-1 root-cause capture) — composes with, and is not absorbed by, this check.
- Sibling boundary: WI-5760 (`bridge/gtkb-wi5760-pauth-preflight-visibility-001.md`) makes the per-thread operation-time PAUTH decision visible at review time; WI-5762 makes the aggregate PAUTH population visible at doctor time. Per-thread evaluation vs population census — no overlapping surfaces (WI-5760 does not touch `doctor.py`; WI-5762 touches only `doctor.py` + its test).

## Owner Decisions / Input

Recorded authority for this filing:

- **DELIB-202667531** (owner decision, 2026-07-29): fix-class advisory triage authorized; corrective work items created and authorized ahead of other advisory-derived work; supplies the owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001. WI-5762 is one of those corrective items (P1, defect, `maintenance_tool`), and its authorized title fixes the severity calibration (multi-coverage WARN, contradictory-set FAIL) that the advisory's grilling question 2 asked the owner to decide.
- **DELIB-202667533 AT-04** (owner AUQ, 2026-07-29): program PAUTH PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM (verified this session: v3 `active` after the SF-1 corrected reissue of 2026-07-30T03:48:58Z; classes source, test_addition, governance_evidence, bridge; owner decision DELIB-202667533; covers WI-5762 through the corrections program scope). AT-04's completion discipline is the LATER prompting slice's authority; this slice only detects its candidates.
- **DELIB-202667534** (owner decision, 2026-07-29): disposition-table consolidation fixing WI-5762's first-slice direction; this proposal implements that direction.

Open decisions — design ratifications with recommended defaults, flagged for
implementation-time AskUserQuestion per GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001;
this proposal does NOT silently decide them, and none blocks the slice as
designed:

- **OD-A (completion-candidate severity).** Default WARN (advisory recommendation 1 wording). Alternative: informational-only until the prompting slice lands, to keep WARN volume lower (471 candidates measured).
- **OD-B (allowed-class divergence promotion).** Default: divergent `allowed_mutation_classes` sets are visible inside multi-coverage/contradiction finding payloads but do NOT independently trigger FAIL in this slice (FAIL keys on `forbidden_operations` distinctness, the advisory's definition). Alternative: promote allowed-class divergence to FAIL — measured impact 149 WIs.
- **OD-C (membership-wide authorizations).** Default: the 22 active authorizations with no `included_work_item_ids` list are reported as an informational summary count, excluded from multi-coverage math in this slice (matching the advisory's explicit-list census method). Alternative: expand coverage math through project membership — a larger, riskier join that belongs with the begin-time conflict-semantics slice if the owner wants it.

## Requirement Sufficiency

Existing requirements sufficient.
GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 already defines the bounded
authorization contract whose violations this check surfaces;
GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 already establishes the
completion/retirement discipline whose candidates it names;
GOV-SOURCE-OF-TRUTH-FRESHNESS-001 and SPEC-1830 already require fresh
canonical reads and code-not-conversation procedures. This change makes the
platform observe an existing contract; no new or revised requirement is
required before implementation. (Any later-slice change to what an
authorization MEANS — begin-time conflict semantics, default expiry — is
future owner-decision work outside this slice.)

## Spec-Derived Test Plan

New test module: `platform_tests/scripts/test_doctor_pauth_accumulation.py`
(declared new; does not exist at HEAD). Fixture project roots with fixture
`groundtruth.db` populated through the production `KnowledgeDB` API — fixture
registry of authorizations + work items per case; no live MemBase read or
write; no live bridge mutation. Cases:

1. **Multi-coverage WARN case** — `test_multi_coverage_warns_with_covering_set`:
   fixture with two active authorizations sharing one included work item and
   IDENTICAL `forbidden_operations`; payload contains exactly one
   `multi-coverage` WARN finding whose covering-authorization set lists both
   ids; no `contradictory-authorization-set` finding; aggregate status
   `warning`. Derives from GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
   (bounded-grant duplication visible), SPEC-1662, GOV-10.
2. **Contradictory FAIL case** — `test_contradictory_sets_fail`: fixture
   reproducing the WI-5657 shape — two active authorizations on one work
   item, one forbidding `git_commit`, the other not; payload contains a
   `contradictory-authorization-set` FAIL finding naming both ids and both
   forbidden/allowed sets; aggregate status `fail`; ToolCheck status `fail`.
   Derives from GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 (contradictory
   grants), SPEC-1662.
3. **Completion-candidate case** — `test_completion_candidate_detected`:
   fixture with one active authorization whose included work items are all
   terminal (`resolved`/`verified`) → exactly one `completion-candidate`
   WARN naming that authorization; a second active authorization with one
   open included work item is NOT flagged. Derives from
   GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001,
   DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-10.
4. **Clean PASS case** — `test_clean_population_passes`: fixture with
   single-coverage active authorizations over open work items → zero
   findings, aggregate status `pass`, ToolCheck `pass`, and informational
   summary counts present (active total, membership-wide count). Derives from
   SPEC-1662 (the check discriminates rather than uniformly failing),
   GOV-10.
5. **Fail-closed case** — `test_missing_db_fails_closed`: fixture root
   without `groundtruth.db` → FAIL `missing-evidence` finding, matching the
   adjacent `check_standing_backlog_health` fail-closed contract. Derives
   from GOV-SOURCE-OF-TRUTH-FRESHNESS-001, SPEC-1662.

Execution: `groundtruth-kb/.venv/Scripts/python.exe -m pytest
platform_tests/scripts/test_doctor_pauth_accumulation.py -v`, plus
`ruff check` and `ruff format --check` on both changed Python files, plus a
one-shot live run of the payload function against `E:\GT-KB` recorded in the
implementation report (expected: FAIL status with counts in the vicinity of
the census table above, including the WI-5657 contradictory pair, unless the
population has been drained in the interim).

## Acceptance Criteria

1. `gt project doctor` (and the payload function directly) reports, from live
   MemBase state: every multi-covered work item with its full
   covering-authorization id set (WARN), every contradictory-set work item
   (FAIL), and every completion-candidate authorization (WARN), plus
   informational population counts.
2. Against the live database at implementation time, the check surfaces the
   measured population (census table above) including the confirmed WI-5657
   contradictory pair, and no other existing doctor check changes verdict.
3. The check is additive and non-gating: no hook, commit gate, preflight, or
   session flow consults it; removal of the check + test is a clean two-file
   revert.
4. All five fixture tests pass; ruff lint and format gates clean on both
   files.
5. Finding kinds, severities, and summary counts are behavioral payload
   assertions (SPEC-1662), and the ToolCheck message is a count summary, not
   a finding dump.

## Risk and Rollback

Risk: LOW. Additive detection-only doctor check plus one new test module; no
existing gate, hook, dispatcher/TAFE surface, MemBase schema, or
authorization row is touched; read surfaces are existing production APIs
(`list_project_authorizations`, work-item reads). The known consequence —
doctor goes red with 135 contradictory-set FAILs on day one — is the
owner-chosen visibility outcome fixed by the authorized WI title and
disclosed in the census table; it is a measured drain-down target, not a
regression. Volume is managed by count-summary ToolCheck messaging.
Rollback: revert the doctor.py hunk and delete the test module — a single
clean two-file revert with no runtime coupling.

Recommended commit type: feat

## Verification Questions for Loyal Opposition

1. Is the contradiction definition (distinct `forbidden_operations` sets
   among covering active authorizations, with allowed-class divergence
   visible in payload but not independently FAIL-triggering) the correct
   slice-1 reading of the advisory's FAIL finding and the authorized WI
   title, given OD-B routes the promotion question to the owner?
2. Is the explicit-list census method (membership-wide authorizations
   reported informationally, excluded from multi-coverage math per OD-C) the
   right first-slice boundary, or must project-membership expansion land in
   this slice for finding (a) to be truthful?
3. Does the WI-5785 composition boundary hold as drawn (population-shape
   findings here; token-resolution findings there), or do the two checks
   need a shared finding-kind namespace decided now?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
