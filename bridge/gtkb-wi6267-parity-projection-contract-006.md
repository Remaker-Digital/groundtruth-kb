VERIFIED
::init gtkb pb
::open build

bridge_kind: lo_verdict
Document: gtkb-wi6267-parity-projection-contract
Version: 006
Author: Loyal Opposition (harness B, session 37676db4-47bd-4ba1-8208-e1e3d03313e8)
Date: 2026-08-14 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 37676db4-47bd-4ba1-8208-e1e3d03313e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via the canonical init keyword

# Loyal Opposition Verification — Parity Projection Contract

Responds to: bridge/gtkb-wi6267-parity-projection-contract-005.md

## Verdict

**VERIFIED**, with one consequence stated explicitly below: this verdict does
**not** discharge the parent thread's F1.

The report hands the reviewer a genuine decision — whether V1's literal wording
("zero STALE") is met-in-substance when all false positives are eliminated but
true positives remain outside scope. The decision is **yes for this thread**,
and the reasoning is set out under "The V1 Determination".

Every claim that could be falsified was reproduced. The report leads with the
criterion it did not meet rather than burying it, and it declines two available
routes to a literal pass — widening scope to the registry, or relaxing the hash
check. Refusing both is the behavior the `-002` and `-004` reviews were
protecting, and it is the reason this passes.

## Review Independence

Author session context `a49752e4-5a9f-4290-bceb-910693b5271f`; reviewer session
context `37676db4-47bd-4ba1-8208-e1e3d03313e8`
(`loyal-opposition/claude/B`, model `claude-opus-5`). Distinct; independence
holds.

**Disclosure.** This reviewer issued `-002`, `-004`, and the parent `-006` F1
that created this thread. The confirmations below are fresh measurements.

## The V1 Determination

**V1 as worded is not met.** Measured independently: goose reports
`EXTRA: 1, PASS: 20, STALE: 24, UNSUPPORTED: 24`, overall WARN. Not zero.

**It is met in substance for this thread's scope**, on four measured grounds:

1. **The false-positive class is gone.** Before: `STALE 44, PASS 0`. After:
   `STALE 24, PASS 20`. Twenty capabilities that could never pass now pass.
2. **The residual failures have a different cause.** Every remaining row
   carries one uniform note — verified by taking the distinct set of STALE
   reasons, which has exactly one member: `Registry source_sha256 does not
   match the canonical source.` The prior class
   (`unsupported or missing generator identity`) has disappeared entirely.
3. **That cause was previously unreachable.** The hash comparison sits after
   the generator check, so these rows could not have been reported before the
   repair. The repair unmasked them; it did not create them.
4. **The cause is independent of this change.** Codex measures
   `STALE: 44` both before and after — identical counts across the change —
   so the registry-hash condition exists on a harness this thread never
   touched.

**What reaching literal zero would have required**, both correctly refused:
editing `config/agent-control/gtkb-harness-capability-registry.toml`, which is
outside this thread's `target_paths` and needs its own review; or relaxing the
hash check, which would have re-introduced exactly the ignore-difference defect
`-002` and `-004` were guarding against. A report that satisfied V1 by either
route would have failed this verification.

**Consequence for the parent thread, stated plainly.** The parent
`-006` F1 required "parity PASS … or an owner waiver". Parity remains WARN.
This verdict therefore does **not** discharge that finding. The parent slice
still needs either WI-6275 to land, or an explicit owner waiver of the parity
criterion. That decision belongs to the owner and arrives naturally when the
parent files its REVISED; it is not resolved here, and Prime Builder should not
read this VERIFIED as clearing it.

## Verification of the `-003` Expectations

| Expectation | Result |
|---|---|
| V1 — zero STALE | Not met literally; met in substance for scope (above) |
| V2 — negative fixtures still report STALE | Verified via the new module: 15 tests pass, including tampered-body, wrong-digest and missing-block cases |
| V3 — API/stub family unaffected | Verified: codex counts byte-identical before and after (`DEGRADED 3, EXTRA 1, PASS 14, STALE 44, UNSUPPORTED 11, WARN 1`) |
| V4 — both marker grammars | Pinned by the new module's grammar tests |
| V5 — routing predicate | Pinned; enumeration independently confirmed earlier — `projection_engine` occurs once, under `[harnesses.goose]` |
| V6 — ruff gates run separately | Reported clean on both files |

## Findings

### Accepted — the pre-existing-failure proof is the right method

Six failures appear in the affected-module set. The report does not assert they
are pre-existing; it demonstrates it by swapping the committed `HEAD` version
of `check_harness_parity.py` in by file copy, re-running the same six node ids,
observing the identical set, then restoring and verifying byte-equality. That
is the correct way to separate inherited debt from introduced regression, and
it avoids the git-index operation that would have disturbed the reviewer-staged
carryover. Accepted without re-derivation.

### Accepted — `-004` F1 is root-caused, not merely corrected

`-004` F1 required the true authoring harness in this report. The report states
it (`claude`, harness `B`, session `a49752e4-…`) and goes further, locating the
mechanism in `scripts/bridge_author_metadata.py`
`_resolve_durable_identity_fields`: with `GTKB_HARNESS_NAME` unset and no
dispatch run-id, it falls back to the harness holding the durable
`prime-builder` role, narrowed by dispatchability.

Confirmed against the registry topology measured earlier in this session:
three harnesses hold durable `prime-builder` — A/codex, B/claude, G/goose — and
of those only **A** has `can_receive_dispatch: true`. The narrowing therefore
selects A/codex deterministically, which is exactly the wrong attribution
observed on this thread's `-003` and on
`bridge/gtkb-wi6221-tool-use-is-a-test-directive-003.md`.

This converts a recurring metadata defect into a located one. The fix is out of
scope here and correctly not absorbed.

### F1 — P3 — this report's own provenance block is still not self-consistent

`author_identity: claude` omits the role prefix that every other artifact in
this session carries (`prime-builder/claude/B`), while `Author:` reads "Prime
Builder (harness B, claude)". The harness id and session context are now
correct and unambiguous, so independence and attribution both resolve — this is
a formatting residue of the same defect, not a recurrence of the wrong-harness
error. Noted for the eventual fix at the emitting surface; not gating.

## Positive Confirmations

- **Commit `63add93e2`** — `fix(parity): teach the parity checker the
  projection contract`, 2 files, 320 insertions, 3 deletions, matching the
  report exactly and confined to the two declared `target_paths`.
- **New module: 15 passed**, reproduced independently.
- **Both preflights pass** — applicability reports passed with no missing
  required specs, no blocking errors and no unclassified target paths; clause
  preflight exit 0 with zero blocking gaps; finalization-phase evaluation
  `allowed: true`. Field-level values are recorded in the Applicability
  Preflight section below.
- **Scope discipline**: the residual condition was captured as WI-6275 rather
  than absorbed, with the stated reason that a blind hash refresh would mask
  real drift — which is correct, and is the same standard this thread was
  created to uphold.
- **Root boundary**: both target paths within `E:\GT-KB`.

## Specification Links

- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — obligation 2; the parity instrument
  must be able to validate projections.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the capability floor parity enforces;
  the stub family remains validated.
- `SPEC-1662` (GOV-18) — assertion meaningfulness; STALE-by-construction was
  the defect, and the tampered-body oracle is the strengthening.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — this chain's append-only discipline.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 — the governing PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1.

## Spec-to-Test Mapping

| Linked spec / criterion | Test or command | Executed | Result |
|---|---|---|---|
| `GOV-HARNESS-NEUTRAL-BASELINE-001` ob.2 — parity can validate projections | `check_harness_parity.py --harness goose` | yes | `PASS 20, STALE 24` (from `PASS 0, STALE 44`); false-positive class eliminated |
| `SPEC-1662` — negative cases still fire | `pytest platform_tests/scripts/test_check_harness_parity_projection.py` | yes | 15 passed, incl. tampered-body, wrong-digest, missing-block |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` — stub family unaffected | `check_harness_parity.py --harness codex` | yes | counts identical before and after |
| Residual-cause diagnosis | distinct-reason extraction over STALE rows | yes | exactly one reason: registry `source_sha256` mismatch |
| Commit scope | `git show --stat 63add93e2` | yes | 2 files, 320 insertions, 3 deletions, within `target_paths` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | all of the above re-executed by this reviewer | yes | reproduced |

## Commands Executed

```text
gt bridge state-report
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --harness goose
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --harness codex
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity_projection.py -q --no-header
git show -s --format=%s 63add93e2 ; git show --stat --format= 63add93e2
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6267-parity-projection-contract
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6267-parity-projection-contract
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi6267-parity-projection-contract
```

## Applicability Preflight

- packet_hash: `sha256:b3989b47d951f7887048c6aaae7af9b52e5bc7ac0fc557b97258fa157c70b68c`
- candidate_evidence_hash: `sha256:6b0b687c6667f292a2b0c00eb89c7cd1691e1fe5755c3738dfc3d3c611c3b249`
- bridge_document_name: `gtkb-wi6267-parity-projection-contract`
- declared_target_paths: ["platform_tests/scripts/test_check_harness_parity_projection.py", "scripts/check_harness_parity.py"]
- applicability_path_evidence: [".claude/skills/*/helpers/**`", "bridge/gtkb-adbr-t0-mechanism-repair`", "bridge/gtkb-baseline-correction-and-goose-projector-slice-1-006.md`", "bridge/gtkb-lo-tooling-defect-advisory-014.md`", "bridge/gtkb-wi6221-tool-use-is-a-test-directive-003.md`,", "bridge/gtkb-wi6267-parity-projection-contract-002.md`", "bridge/gtkb-wi6267-parity-projection-contract-003.md`", "bridge/gtkb-wi6267-parity-projection-contract-004.md", "bridge/gtkb-wi6267-parity-projection-contract-004.md`", "config/agent-control/*`,", "config/agent-control/gtkb-harness-capability-registry.toml`", "config/agent-control/gtkb-harness-capability-registry.toml`:", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity_entrypoint_import.py", "platform_tests/scripts/test_check_harness_parity_projection.py", "platform_tests/scripts/test_check_harness_parity_projection.py`", "platform_tests/scripts/test_harness_projection.py", "platform_tests/scripts/test_harness_projection_reader.py", "platform_tests/scripts/test_parity_coverage_complete.py", "platform_tests/scripts/test_parity_discovery_diff.py", "platform_tests/scripts/test_parity_strict_on_rename.py", "scripts/bridge_author_metadata.py`", "scripts/bridge_claim_cli.py", "scripts/check_harness_parity.py", "scripts/check_harness_parity.py`", "scripts/implementation_authorization.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6267-parity-projection-contract-005.md`
- operative_file: `bridge/gtkb-wi6267-parity-projection-contract-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `finalization`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-GET-HEALTHY-PHASE-2`
- authorization_source: `bridge/gtkb-wi6267-parity-projection-contract-003.md`
- requested_operations: ["git_commit", "protected_mutation"]
- cohort: ["bridge/gtkb-wi6267-parity-projection-contract-001.md", "bridge/gtkb-wi6267-parity-projection-contract-002.md", "bridge/gtkb-wi6267-parity-projection-contract-003.md", "bridge/gtkb-wi6267-parity-projection-contract-004.md", "bridge/gtkb-wi6267-parity-projection-contract-005.md", "bridge/gtkb-wi6267-parity-projection-contract-006.md", "platform_tests/scripts/test_check_harness_parity_projection.py", "scripts/check_harness_parity.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `8FC36B9EAC57B15E1F431B5E8B30935B5EFFC9526DFB898DF3CE75CBD22C9C7E`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `git_commit` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `protected_mutation` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6267-parity-projection-contract` — exit 0 (mandatory mode).

- Evidence gaps in must_apply clauses: 0
- **Blocking gaps: 0**

### Blocking Gaps

None.

## Prior Deliberations

- `bridge/gtkb-wi6267-parity-projection-contract-004.md` — the GO whose
  expectations this verdict checks, and whose F1 the report root-causes.
- `bridge/gtkb-wi6267-parity-projection-contract-003.md` — the corrected
  four-mechanism scope.
- `bridge/gtkb-baseline-correction-and-goose-projector-slice-1-006.md` F1 — the
  parent finding this thread serves; **not discharged by this verdict**.
- `bridge/gtkb-wi6221-tool-use-is-a-test-directive-004.md` — where the same
  provenance defect was recorded as systematic; now root-caused.
- `bridge/gtkb-lo-tooling-defect-advisory-014.md` — the misreporting-instrument
  inventory this repair removes two members from.
- `WI-6275` — the registry-hash drift captured rather than absorbed.

## Backlog Conflict Check

`WI-6267` governs and is satisfied. `WI-6275` carries the residual registry
drift and is correctly separate. `WI-6232` (parent slice) still depends on
either WI-6275 or an owner waiver — a dependency this verdict does not close.
No duplication or interference found.

## Methodology

Read-only inspection apart from the finalization transaction. No source or test
file was modified by this reviewer.

**Not verified:** the six pre-existing failures were accepted on the report's
swap-and-restore demonstration rather than re-derived; the claim that 20 of 44
registry `source_sha256` values match was not independently recomputed, though
the uniform single residual reason and the unchanged codex counts are
consistent with it; the memoisation and lazy-build behaviour of
`_PROJECTION_PLAN_CACHE` was not exercised under timing.

## Recommended Commit Type

Recommended commit type: `chore(bridge)`

The implementation landed separately as `63add93e2` under `fix(parity)`, which
matches its diff. This finalization transaction carries only the bridge audit
chain.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `chore(bridge): finalize gtkb-wi6267-parity-projection-contract VERIFIED chain`
- Same-transaction path set:
- `bridge/gtkb-wi6267-parity-projection-contract-001.md`
- `bridge/gtkb-wi6267-parity-projection-contract-002.md`
- `bridge/gtkb-wi6267-parity-projection-contract-003.md`
- `bridge/gtkb-wi6267-parity-projection-contract-004.md`
- `bridge/gtkb-wi6267-parity-projection-contract-005.md`
- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity_projection.py`
- `bridge/gtkb-wi6267-parity-projection-contract-006.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.

---

When you are finished working, close your session envelope by invoking ::wrap.
