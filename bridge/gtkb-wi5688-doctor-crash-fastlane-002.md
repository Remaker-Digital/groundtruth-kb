NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; build review context with test verdict envelope

bridge_kind: lo_verdict
Document: gtkb-wi5688-doctor-crash-fastlane
Version: 002
Responds to: bridge/gtkb-wi5688-doctor-crash-fastlane-001.md
Date: 2026-07-28 America/Los_Angeles

# Loyal Opposition Proposal Review — WI-5688 Doctor Crash Fast-Lane

## Verdict

NO-GO. The crash is real and the fast-lane/project authorization chain is valid, but the proposed one-line fallback fixes only the final `AttributeError` while converting an unreadable `git grep` result into a false `PASS`. Live evidence identifies the actual root cause as Windows locale decoding in stock `subprocess`, not a synthetic enforcement adapter. A revision must fix decoding at the subprocess boundary and prove that the check preserves the real warning/finding set.

No owner decision is required. The defect remains eligible for the reliability fast lane after the revision.

## First-Line Role Eligibility Check

- Resolved interactive session role: Loyal Opposition. `gt session envelope show --harness-name codex` reports `role_resolved: loyal-opposition`, `authority_mode: interactive_transcript`, `interactive_role_source: transcript_init_keyword`, and open session `019fac54-c55c-75c0-8332-d7fdaf03b20a`.
- Status authored here: `NO-GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5688-doctor-crash-fastlane-001.md`, latest status `NEW`.
- Author session metadata is present and readable: `de7aad12-9b24-41c8-849c-de48e349ff62`.
- Reviewer session `019fac54-c55c-75c0-8332-d7fdaf03b20a` differs from the author session; this is not same-session self-review.

## Positive Confirmations

- WI-5688 is an open P1 defect and an active member of `PROJECT-GTKB-RELIABILITY-FIXES` through `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-5688`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry, covers active project members, and permits `source` plus `test_addition` mutations.
- The proposal's two `target_paths` are scoped to the affected source and focused regression test.
- Applicability preflight passes with no missing required or advisory specifications; the mandatory ADR/DCL clause preflight has zero blocking gaps.
- Current target source/test files are clean in the worktree. The proposal file is untracked as expected for the fresh audit-chain entry.
- Existing focused tests pass: `4 passed`.

## Findings

### P1 — The proposed fallback converts a decode failure with real matches into a false sweep-complete PASS

**Observation.** `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2576-2581` invokes the standard-library `subprocess.run` with `capture_output=True` and `text=True`, but without an explicit encoding or error policy. On this Windows host, `locale.getencoding()` is `cp1252`. A live call against the repository raises a stock `subprocess.py` reader-thread `UnicodeDecodeError` on byte `0x90`; the completed process then has `returncode=0` and `stdout=None`, and `doctor.py:2603` raises the reported `AttributeError`.

The output is UTF-8. One concrete trigger is `bridge/gtkb-command-surface-003.md:266`, which contains a Unicode left arrow. Running the same `git grep` with `encoding="utf-8", errors="replace"` returns a string and exit code 0. Injecting that deterministic decode into the current check yields `status="warning"` with 711 nonexcluded stale skill references.

`doctor.py:2590` correctly states that `git grep` exit 0 means matches and exit 1 means no matches. The proposal's `(completed.stdout or "").splitlines()` turns the exit-0/matches condition into zero parsed hits, falls through to `doctor.py:2627-2632`, and claims `0 ... sweep complete`.

**Deficiency rationale.** Missing captured output is not equivalent to a no-match result. The proposal would replace a visible hard failure with a more dangerous false-green health claim. The source advisory's leading interception-layer hypothesis is disproved by the stock Python traceback and must not remain the proposal's root-cause basis.

**Impact.** The doctor would report the sweep complete while 711 live, nonexcluded references remain. That violates the WI-5668 owner contract that the doctor WARN while the sweep is incomplete (`DELIB-202667193`; `DELIB-20260724-WI5668-SEVERITY-CONTRACT`) and undermines the mechanical completion gate.

**Required action.** Revise the implementation to decode `git grep` output deterministically and resiliently at the subprocess boundary (for example explicit UTF-8 with a documented error policy, or bytes capture followed by explicit decoding). If exit 0 ever still arrives without usable output, return a non-PASS unavailable/scan-skipped result; never claim sweep complete. Preserve the focused source/test target scope.

**Owner decision needed.** No.

### P1 — The proposed regression test would bless the false-success behavior

**Observation.** The new test is specified only to assert a non-crashing, well-formed `ToolCheck` for `stdout=None`. It does not require a non-PASS status, preserve any finding, exercise Unicode output, or prove deterministic decoding. The existing four tests in `platform_tests/scripts/test_doctor_skill_rename_sweep.py` use ASCII-only fixtures and therefore do not cover the Windows decode path.

**Deficiency rationale.** A test that accepts any well-formed status passes when the implementation falsely reports completion. It does not derive from the WI-5668 behavior contract: warn while real references remain, pass only at zero.

**Impact.** The focused test suite and the live doctor acceptance could both turn green while the completion gate silently discards its evidence.

**Required action.** Add a Unicode-output regression that demonstrates the actual Windows failure mode and asserts the resulting `ToolCheck` remains `warning` with the offending tracked path visible. Add a direct missing-output case that asserts a non-PASS unavailable/scan-skipped result. Make the end-to-end acceptance criterion require the correct semantic result, not merely absence of `AttributeError`.

**Owner decision needed.** No.

### P1 — The proposal does not carry durable evidence that the prior owner routing decision was superseded

**Observation.** `DELIB-202667509` is the only WI-5688-linked owner deliberation returned by the governed query, and it explicitly chose the WI-5441 route over a competing fast-lane proposal. The current proposal says a 2026-07-28 AUQ superseded that routing decision, but supplies no DELIB-ID or other governed owner-decision record for that answer. WI-5688's Prime Builder-authored status detail shows that WI-5441 ended without the repair; it does not itself prove the claimed owner choice to supersede the earlier route. `DELIB-202667523` authorizes manual worker fan-out, not this routing change.

**Deficiency rationale.** The standing PAUTH validly covers eligible project members, but it does not silently supersede a contrary item-specific owner decision. A proposal whose Owner Decisions / Input section depends on a superseding AUQ must cite durable evidence for that AUQ.

**Impact.** Implementation could proceed under a route the owner previously rejected, with the only claimed reversal left in ephemeral or uncited conversation state.

**Required action.** Cite the archived 2026-07-28 superseding owner decision if it already exists. If it was not captured, route the existing choice through the governed owner-decision capture path before refiling. No new implementation preference is needed if the owner already made the stated decision; the missing requirement is durable evidence.

**Owner decision needed.** Potentially Prime Builder-side only if no prior answer can be recovered; this review does not require a new decision from the owner now.

### P1 — The proposal omits a directly governing freshness requirement and does not map every linked control to verification evidence

**Observation.** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` explicitly applies to doctor checks and reporting surfaces that make numeric or state claims about a source of truth. The proposed fallback makes exactly such a state claim (`0 ... sweep complete`) from unavailable output, yet the proposal does not cite this GOV. Its test table also maps only the WI-5668 behavior summary, the WI-5688 condition, and the fast-lane procedure; it does not map each of its listed bridge, project-authorization, placement, lifecycle, spec-linkage, and artifact-governance controls to either code tests or explicit procedural evidence.

**Deficiency rationale.** Applicability and clause preflights are a mechanical floor. Manual review identified a governing state-freshness rule whose omission allowed the false-green design to appear acceptable. The specification-derived test gate also requires an auditable mapping for every relevant linked constraint, including procedural bridge evidence where a code test is not the right mechanism.

**Impact.** The revision could fix the exception without proving that its state claim is fresh and fail-honest, and later verification would lack a complete spec-to-evidence matrix.

**Required action.** Add `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and the directly applicable WI-5668 owner deliberations to the governing surface. Map every linked requirement to a concrete code test or named procedural evidence, and ensure the freshness requirement maps to the Unicode/fail-honest regressions.

**Owner decision needed.** No.

### P2 — Exclusion filtering occurs after decoding, so excluded content can still break the scan

**Observation.** Exclusion filtering happens at `doctor.py:2600-2608`, after `subprocess.run` has decoded all `git grep` output. The observed Unicode trigger is under `bridge/`, an intentionally excluded tree.

**Impact.** Excluded content can still crash or corrupt the scan before filtering, and the command emits megabytes of avoidable output.

**Recommended action.** Resilient decoding is mandatory for this revision. Prime Builder may also move stable exclusions into `git grep` pathspecs if that remains within the same behavior contract and focused tests prove parity; otherwise retain this as an optimization follow-up.

**Owner decision needed.** No.

### P3 — The proposal retains contradictory helper placeholder text

**Observation.** The substantive `## Prior Deliberations` list is immediately followed by `### Helper-suggested candidates` and `_No prior deliberations: <fill in reason before filing>._`.

**Impact.** The filed artifact simultaneously cites prior deliberations and asserts none exist, leaving an unresolved template marker in the audit chain.

**Required action.** Remove the placeholder from the REVISED proposal and cite the directly applicable WI-5668 owner decisions identified by the mandatory search.

**Owner decision needed.** No.

## Required Revisions

1. Replace the synthetic-interception root-cause hypothesis with the reproduced stock `subprocess` Windows decoding mechanism and its evidence.
2. Fix decoding at the subprocess boundary; do not coerce missing output to an empty match set.
3. Preserve fail-honest semantics: exit 0 with unusable output must never yield `status="pass"` or `sweep complete`.
4. Add Unicode-output coverage that asserts `warning` plus a real offending path, and a missing-output test that asserts a non-PASS result.
5. Tighten the live acceptance criterion to verify the correct warning/finding behavior as well as no crash.
6. Add `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, map every linked control to code-test or procedural evidence, and add `DELIB-202667193` plus `DELIB-20260724-WI5668-SEVERITY-CONTRACT` to Prior Deliberations.
7. Cite durable evidence for the 2026-07-28 owner routing supersession (or complete the governed owner-decision capture if that evidence does not yet exist).
8. Remove the contradictory helper placeholder.

## Options Considered

### Option A — Proposed empty-string fallback

- Strength: one-line change; stops the final `AttributeError`.
- Weakness: discards an exit-0 match set and emits a false completion PASS.
- Disposition: reject.

### Option B — Deterministic resilient decode with fail-honest missing-output handling

- Strength: addresses the reproduced root cause, preserves the WI-5668 warning contract, and remains within the same two-file fast-lane scope.
- Weakness: slightly more than one source expression and requires stronger test fixtures.
- Disposition: recommended.

### Option C — Revert the WI-5668 check

- Strength: removes the crash.
- Weakness: removes the owner-directed mechanical completion signal and does not satisfy the work item's intent.
- Disposition: reject.

## Applicability Preflight

- packet_hash: `sha256:52b27af0d7f551a948d04a09a867104bc63e57a924d0f12cb25d5cfc9ebdf782`
- candidate_evidence_hash: `sha256:ded7ae9789f5fe8c761a113fa310efa9346a1777f9df9538641e3b89d91cb04e`
- bridge_document_name: `gtkb-wi5688-doctor-crash-fastlane`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]
- applicability_path_evidence: ["bridge/gtkb-wi5668-sweep-completion-gate-004.md`", "bridge/gtkb-wi5678-genericize-advisory-role-framing-008.md`", "bridge/gtkb-wi5688-doctor-skill-rename-sweep-crash-001.md", "bridge/gtkb-wi5688-doctor-skill-rename-sweep-crash-001.md`", "bridge/gtkb-wi5688-doctor-skill-rename-sweep-crash-001.md`:", "groundtruth-kb/src/groundtruth_kb/project/**`", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py:2603`", "groundtruth-kb/src/groundtruth_kb/project/doctor.py`:", "platform_tests/scripts/test_doctor_skill_rename_sweep.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py`", "platform_tests/scripts/test_doctor_skill_rename_sweep.py`).", "platform_tests/scripts/test_doctor_skill_rename_sweep.py`."]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5688-doctor-crash-fastlane-001.md`
- operative_file: `bridge/gtkb-wi5688-doctor-crash-fastlane-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5688-doctor-crash-fastlane`
- Operative file: `bridge\gtkb-wi5688-doctor-crash-fastlane-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Specification-Derived Review

| Governing requirement | Review evidence | Result |
|---|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` eligibility | WI-5688 origin/priority, active project membership, active PAUTH, two-file scope | PASS |
| WI-5668 behavior contract | `DELIB-202667193`; `DELIB-20260724-WI5668-SEVERITY-CONTRACT`; live UTF-8-resilient diagnostic | NO-GO — proposed fallback reports PASS where contract requires WARN |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | live exit-0/`stdout=None` reproduction and proposed fallback analysis | NO-GO — relevant GOV omitted and unavailable evidence is converted into a current-state completion claim |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | applicability preflight and proposal spec links | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | proposed `stdout=None` test and four existing focused tests | NO-GO — test assertions permit false PASS and omit Unicode failure path |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | live thread chain, author/reviewer session comparison, next version 002 | PASS |

## Prior Deliberations

- `DELIB-202667509` — owner originally routed WI-5688 into WI-5441; WI-5688 v2 records that route as superseded after WI-5441 reached VERIFIED without this repair.
- `DELIB-202667193` — owner requires the WI-5668 doctor completion gate to WARN until zero live pre-rename references remain.
- `DELIB-20260724-WI5668-SEVERITY-CONTRACT` — owner explicitly selected WARN doctor plus a failing release gate while references remain.
- `DELIB-202667445` — prior Loyal Opposition NO-GO context for WI-5668.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner established the standing fast-lane mechanism used by WI-5688.
- `DELIB-202667523` — owner authorized the manual worker fan-out that produced the proposal while preserving independent bridge review.

Mandatory-search note: no governed owner-decision record for the proposal's claimed 2026-07-28 routing supersession was found. The revision must cite it if present or capture it through the governed path.

## Methodology and Commands Executed

- Read the full current WI-5688 child thread and the source advisory.
- Inspected `doctor.py:2529-2632`, the focused test file, and the concrete Unicode-trigger line.
- Queried WI-5688 history, project membership, standing PAUTH, fast-lane specification, related backlog items, and Deliberation Archive records.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5688-doctor-crash-fastlane` — exit 0.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5688-doctor-crash-fastlane` — exit 0, zero blocking gaps.
- Ran `python -m pytest platform_tests/scripts/test_doctor_skill_rename_sweep.py -q --tb=short` — 4 passed, one unrelated pytest configuration warning.
- Ran the live doctor check under the repository venv — reproduced stock reader-thread `UnicodeDecodeError` followed by `AttributeError`.
- Ran the exact `git grep` with the host default cp1252 decode — exit 0, `stdout=None`; with explicit UTF-8 resilient decode — exit 0 and string output.
- Injected the UTF-8-resilient subprocess behavior into the current check — `warning`, 711 nonexcluded references.
- Checked scoped git state: target source/test files clean; fresh proposal untracked.

## Risk / Rollback for the Revision

- A deterministic decoding correction is still a small, reversible fast-lane change in the same target files.
- The revision should retain the existing `returncode > 1` error handling and explicitly cover missing output so future subprocess anomalies fail honestly.
- Rollback remains a single commit, but verification must demonstrate warning fidelity before finalization.

## Decision Needed From Owner

None. Prime Builder can revise within the existing fast-lane authorization and resubmit.

## Skills Applied

- `gtkb-bridge`
- `gtkb-proposal-review`
- `gtkb-query`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
