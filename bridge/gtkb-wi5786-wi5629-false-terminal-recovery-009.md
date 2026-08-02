NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; Prime Builder; build activity
author_metadata_source: open session envelope and current transcript

# WI-5786 WI-5629 False-Terminal Recovery — Factual Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5786-wi5629-false-terminal-recovery
Version: 009
Responds to: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-008.md
Approved proposal: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5786

target_paths: ["bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md"]

implementation_scope: governance_evidence_only
kb_mutation_in_scope: false
Recommended commit type: chore

KB Mutation: This report performs no MemBase write or mutation.

## Implementation Claim

The GO-authorized evidence-only recovery step is complete. Prime Builder made
no source, test, configuration, dispatcher, registry, projection, database, or
backlog mutation. This report re-derives the immutable WI-5629 implementation
and false-terminal provenance, binds the 30-file historical chain to an
explicit reproducible manifest serialization, executes the approved focused
verification, preserves versions 001–008, and requests independent terminal
review.

The original implementation remains in scoped commit
`1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4`. The historical terminal verdict
remains in unrelated 532-path commit
`db07f9dcfe7e7de8addc850729209278472cb0fe`. This report does not rewrite,
merge, relabel, or pretend those commits formed one scoped transaction.

## Implementation Start Evidence

- Independent GO:
  `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-008.md`, SHA-256
  `4684707e8de01d0b4c5d8726b01d6cbd56d70a1e9cfcb1f9a133d54787b40618`.
- Exact work-intent claim: rowid `35979`, `claim_kind: go_implementation`,
  session `019f9b59-52a0-75b2-9973-bd5601f98e9f`, acquired
  `2026-08-01T09:21:00Z`, implementation deadline `2026-08-01T09:51:00Z`,
  grace/TTL expiry `2026-08-01T10:01:00Z`.
- Schema-v3 packet hash:
  `sha256:3319661b8af2f2a8958727f31d55c238978064bfe8f096dc15d25e6bd8c93be1`.
- Packet created `2026-08-01T09:22:30Z`, expires
  `2026-08-01T11:22:30Z`, and admits only
  `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md`.
- Operation-time PAUTH evaluation: `allowed`, authorization v2, exact target
  classified `bridge`, normalized envelope hash
  `A66FAD26CAD6FA2F8E75FD19196C3D4785F1010DECC584AE9DF694C679466EE5`.

## Files Changed

- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md` — this factual
  report only.

The report helper observed zero dirty files in the approved implementation
scope before filing and excluded 1,140 unrelated shared-worktree paths. The two
by-reference subject paths were clean. No foreign path was restored, edited,
staged, attributed, or absorbed.

## Re-Derived Git And Artifact Evidence

All evidence below was freshly observed at HEAD
`75decbfa704fe50288aecbc5669def329a0825df` after GO and start authorization.

### Scoped implementation commit

- `git merge-base --is-ancestor 1aa2182b... HEAD` exited 0.
- `git diff-tree --no-commit-id --name-only -r 1aa2182b...` returned exactly
  two paths:
  - `platform_tests/scripts/test_implementation_authorization.py`
  - `scripts/implementation_authorization.py`
- Current live hashes are:
  - source:
    `bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891`
  - test:
    `d59aca8a1c31fc0a3b3cbc6bebc8bc542735feda79bcbeb0eeb19ccff337e98f`
- Both subject paths returned empty scoped `git status --short` output.

These current hashes establish live non-regression only. They do not backdate
or replace the immutable implementation snapshot.

### False terminal commit

- `git merge-base --is-ancestor db07f9dc... HEAD` exited 0.
- `git diff-tree --no-commit-id --name-only -r db07f9dc...` returned 532
  paths, not a scoped WI-5629 transaction.
- The first five paths were bridge/governance surfaces beginning with
  `.claude/hooks/bridge-axis-2-surface.py`; the last five ended with
  `scripts/verify_antigravity_dispatch.py`. The exact count was machine-derived,
  not inferred from the commit message.

### Historical WI-5629 manifest

Exactly 30 files matched
`bridge/gtkb-wi5629-corrected-malformed-verdict-chain-[0-9][0-9][0-9].md`.
The manifest serialization required by GO v008 is now explicit:

1. Sort paths by filename ascending.
2. For each file, emit `filename:lowercase_sha256_of_exact_file_bytes`.
3. Encode the records as UTF-8.
4. Join records with CRLF (`0x0d 0x0a`).
5. Append no final terminator.

The resulting SHA-256 is
`824d0aac5c592092af6fa01c21a7205d28506eacb6e61e480122fe5e56412049`.
The first record is
`gtkb-wi5629-corrected-malformed-verdict-chain-001.md:debe758a46e6c93947f1719bb572c0df2ce554aa511b4e65ff3728a307614608`;
the last is
`gtkb-wi5629-corrected-malformed-verdict-chain-030.md:9ab782102a78b44d7d6b7e053d2e1cdc6c7a2e3c20c9834eb4cafa1fe45a600b`.

### Recovery-chain preservation

Versions 001–003 each matched their HEAD blob (`git diff --quiet HEAD --`
exit 0):

| Path | Working SHA-256 | HEAD blob OID |
| --- | --- | --- |
| `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-001.md` | `1e18d39e879eae764b83e5dda9213f1de5a2e32da782e2c451d2b54e9e3ad7c5` | `16599eb7b54b0f2ed61a0ff367abb19b13a4544c` |
| `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-002.md` | `a242505dcb69faddcfa76e9f40ed84b1cecaa29ab38274b4a7f338d8fe3d74ab` | `5158f94c5737e69179e39300e60544da81141214` |
| `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-003.md` | `e130aa3f55eaf0e2c08d806b2c8cf4fbd24f3fa985c7590779d5b7e35629ab7e` | `6b321a50738ea94ed803d18967b36f1fb480b6dc` |

Before this report, versions 004–008 were the only untracked continuation
files. Versions 009 and the independent verdict 010 complete the declared
seven-path terminal cohort if and only if the finalizer revalidates it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification Plan And Results

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| Bridge authority and lifecycle | Exact v008 GO hash; claim row 35979; schema-v3 packet; strict report plan | PASS |
| Project operation-time authority | Active PAUTH v2 evaluation for exact v009 target | PASS (`allowed`) |
| Scoped immutable implementation | Ancestor check and exact two-path inventory for `1aa2182b` | PASS |
| Candid false-terminal provenance | Ancestor check and exact 532-path count for `db07f9dc` | PASS |
| Artifact preservation | Explicit 30-file manifest; HEAD-blob equality for recovery v001–003 | PASS |
| Focused specification-derived behavior | 163-test authorization suite | PASS (163/163) |
| Static correctness | Ruff check, Ruff format, compile, path-scoped diff check | PASS |
| Worktree hygiene | Subject status empty; exact untracked continuation census; 1,140 foreign paths excluded | PASS |
| Root isolation | Every target/evidence path resolved below `E:/GT-KB` | PASS |

## Commands Run And Observed Results

1. `python scripts/bridge_claim_cli.py claim ... --session-id
   019f9b59-... --ttl-seconds 7200` — exit 0; row 35979,
   `go_implementation`.
2. `python scripts/implementation_authorization.py begin --bridge-id ...
   --session-id 019f9b59-... --expires-minutes 120` — exit 0; schema v3,
   packet hash `3319661b...3be1`, exact v009 target.
3. `python -m pytest
   platform_tests/scripts/test_implementation_authorization.py -q
   --tb=short` — collected 163; `163 passed, 1 warning in 67.89s`.
4. `ruff check` on the source and test — `All checks passed!`.
5. `ruff format --check` on the source and test — `2 files already formatted`.
6. In-memory Python `compile()` on both files — `compile-pass 2 files`.
7. `git diff --check --` on both files — exit 0, no output.
8. Both `git merge-base --is-ancestor` commands — exit 0.
9. Both `git diff-tree` inventories — exact counts 2 and 532.
10. Deterministic manifest/HEAD-blob evidence script — 30 records, manifest
    `824d0aac...12049`, all three recovery versions `diff_exit: 0`.
11. `impl_report_bridge.py plan ... --compact` — latest GO v008, proposal v007,
    report v009, `files_changed_count: 0`, `excluded_dirty_count: 1140`.

### Authoritative combined-matrix disclosure

The owner-required current combined matrix was also run over the lifecycle
resolver, implementation authorization, and protected-commit checker suites.
Actual collection was 399 tests, not the historical estimate of 289. Result:
`398 passed, 1 failed, 1 warning in 197.62s`.

The sole deterministic failure was
`test_schema_v2_verdict_hash_passes_live_and_real_index_only_audits`, which
reproduced in isolation. It is a stale applicability `packet_hash` disagreement
inside the protected-commit checker fixture, not a failure in either WI-5786
by-reference subject. The same pre-existing failure is disclosed in current
WI-5824 report v009 and the poisoned/stale publication-capability recovery class
is tracked by open P0 `WI-5825`. This report does not suppress the failure,
claim a fully green combined matrix, or expand WI-5786 to modify its overlapping
checker/test targets.

Static checks across all six combined-matrix source/test files passed: Ruff
check, Ruff format, and in-memory compile all clean.

## Owner Decisions / Input

- `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` explicitly approves
  this bounded recovery under normal gates.
- `DELIB-202667721` controls the active list-free Housekeeping Hardening PAUTH.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and
  `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` establish that
  legacy per-WI `approval_state` is not authority.
- No new owner input was required or inferred during implementation.

## Prior Deliberations

- `DELIB-202667533` — commit-first, publish-after terminal finalization.
- `DELIB-202667348` — WI-5629 non-terminal recovery evidence.
- `DELIB-202667191`, `DELIB-202667519`, and
  `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` — bounded by-reference and
  exact-path stranded-terminal recovery discipline.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` — generous bounded
  waits and canonical-state checks under contention; no expiry gate weakened.

## Requirement Sufficiency

Existing requirements sufficient. No product or runtime behavior changed. The
report implements only the approved factual evidence and lifecycle recovery
step.

## Pre-Filing Preflight Subsection

Candidate applicability preflight against this exact report passed with
`preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, `blocking_errors: []`, and operation-time PAUTH
status `allowed`. Mandatory clause preflight evaluated five clauses, classified
four `must_apply`, found zero evidence gaps and zero blocking gaps, and exited
0. The live writer will rerun its content-bound compliance checks. Historical
chain paths and the existing source/test subjects appear only as by-reference
evidence; the sole declared mutation target remains version 009.

## Acceptance Criteria Status

1. Durable scoped owner approval cited and validated — MET.
2. Legacy `approval_state` neither used nor mutated as authority — MET.
3. Independent GO v008 authorizes only v009 — MET.
4. Fresh exact claim and schema-v3 start packet current during execution — MET.
5. Both commit inventories, ancestor checks, 30-file manifest, and live subject
   hashes re-derived — MET.
6. No source, test, configuration, database, dispatcher, registry, projection,
   or unrelated path modified — MET.
7. Immutable implementation evidence distinguished from current non-regression
   evidence — MET.
8. Independent verification creates exact commit-backed v010 or leaves the
   chain non-terminal — PENDING LO.
9. Terminal commit contains exactly versions 004–010 — PENDING FINALIZER.
10. Backlog reconciliation occurs only after commit-backed terminal evidence —
    PENDING TERMINAL VERDICT.
11. No push, release, deployment, credential work, external mutation, history
    rewrite, or destructive cleanup — MET.

## Deviations And Defects Disclosed

- The combined matrix collected 399 rather than the old 289 estimate.
- Its single checker-fixture failure is disclosed above and remains open under
  overlapping P0 recovery work; WI-5786 did not absorb it.
- The shared registry lane timed out twice at its hard-coded 30-second lock
  while publishing v007. Canonical passive observation then succeeded on the
  third bounded attempt, and the governed writer published without bypass.
- The requested two-hour work-intent TTL was constrained by the current
  lifecycle to a 30-minute implementation deadline plus 10-minute grace. The
  report was executed inside that authority; no timestamp was extended or
  backdated.

## Exact Terminal Finalization Request

If and only if independent verification passes, use the governed commit-first
finalizer and require the staged/committed cohort to be exactly:

- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-004.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-005.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-006.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-008.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md`
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-010.md`

Reject any extra staged path. Do not stage versions 001–003, any WI-5629
historical file, either by-reference subject, `groundtruth.db`, registry state,
or any foreign worktree change.

## Risk And Rollback

Residual risk is limited to a reviewer/finalizer accidentally absorbing foreign
paths or treating the old false terminal as valid. The exact seven-path cohort,
immutable manifest, and commit-first independent finalizer fail closed against
both. The separately disclosed checker-fixture failure remains visible and
cannot be laundered by this recovery.

Before terminal commit, rejection leaves the append-only chain non-terminal.
After a valid terminal commit, correction remains append-only. No source or
history rollback is part of this report.

## Loyal Opposition Asks

1. Independently re-run the exact manifest serialization, commit inventories,
   focused suite, and authority checks.
2. Independently disposition the disclosed combined-matrix failure without
   expanding or laundering WI-5786's scope.
3. Return VERIFIED only through exact commit-first v010 finalization; otherwise
   return NO-GO with concrete findings and leave the chain non-terminal.

## Recommended Commit Type

Recommended commit type: `chore(bridge): finalize WI-5786 false-terminal recovery`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
