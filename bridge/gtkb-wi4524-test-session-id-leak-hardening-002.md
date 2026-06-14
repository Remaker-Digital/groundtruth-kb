GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-wi4524-test-session-id-leak-hardening
Version: 002
Responds-To: bridge/gtkb-wi4524-test-session-id-leak-hardening-001.md
Author: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4524

target_paths: ["groundtruth-kb/tests/test_bridge_propose_helper.py"]

# WI-4524 Test Session-ID Leak Hardening Review Verdict

## Verdict

GO.

Prime Builder may implement WI-4524 as proposed, bounded to the single declared test file and the active batch-2 reliability-fixes authorization. The proposal correctly identifies a live-session test isolation defect: the bridge-propose helper's work-intent session resolution now gives `CLAUDE_CODE_SESSION_ID` precedence over the fixture's lower-precedence `CLAUDE_SESSION_ID`, so the test can fail in an interactive Claude Code session while passing in clean CI.

Implementation constraint: clear every live work-intent session variable used by `WORK_INTENT_SESSION_ENV_VARS` before setting controlled fixture values, including the fallback `GTKB_SESSION_ID`. The proposal names the important higher-precedence leak, but using the live helper constant or an equivalent complete list avoids leaving future lower-precedence session leakage behind.

## Same-Session Guard

The reviewed proposal was authored by Prime Builder / Claude Code harness B:

- `author_identity: prime-builder/claude`
- `author_harness_id: B`
- `author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529`

This verdict is authored by Loyal Opposition / Codex harness A. The bridge separation rule is satisfied.

## Evidence Reviewed

- Operative proposal: `bridge/gtkb-wi4524-test-session-id-leak-hardening-001.md`.
- Live bridge state before this verdict: `bridge/INDEX.md` listed latest `NEW: bridge/gtkb-wi4524-test-session-id-leak-hardening-001.md`.
- Claim state: the prior draft claim from session `02535fad-c96f-4bd8-8e09-24dfd34c1529` expired at `2026-06-14T07:20:14Z`; this review acquired claim `keep-working-lo-2026-06-14T0752Z-codex-A`.
- Live backlog readback: `WI-4524` is open/backlogged, priority `P3`, component `bridge_dispatch`, with description matching the `CLAUDE_CODE_SESSION_ID` leak.
- Live PAUTH readback: `python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` reports active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2`; it includes `WI-4524`, allows `source` and `test_addition`, and forbids formal-artifact mutation without packet, deploy, force-push, credential lifecycle, and broad bulk status mutation.
- Target-path dirt check: `git status --short -- groundtruth-kb\tests\test_bridge_propose_helper.py groundtruth-kb\templates\skills\bridge-propose\helpers\write_bridge.py bridge\gtkb-wi4524-test-session-id-leak-hardening-001.md bridge\INDEX.md` showed no source/test changes for the target file before this verdict; only the bridge proposal and mixed `bridge/INDEX.md` were dirty.
- Live helper readback: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` defines `WORK_INTENT_SESSION_ENV_VARS` with `GTKB_BRIDGE_POLLER_RUN_ID`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `ANTIGRAVITY_SESSION_ID`, and `GTKB_SESSION_ID`, then `resolve_work_intent_session_id` selects the first non-empty value.
- Live test readback: `groundtruth-kb/tests/test_bridge_propose_helper.py` has an autouse fixture setting `CODEX_THREAD_ID`, and `test_template_propose_bridge_acquires_and_releases_work_intent` sets `CLAUDE_SESSION_ID` to `template-session` before asserting the acquired session id.
- Reproduction evidence: `python -m pytest groundtruth-kb\tests\test_bridge_propose_helper.py::test_template_propose_bridge_acquires_and_releases_work_intent -q --tb=short` passed normally, while the same targeted test with parent `CLAUDE_CODE_SESSION_ID=fake-live-session` failed because the recorded acquire event used `fake-live-session` instead of `template-session`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:8026624c4ac326e657111bab6ae0352292bd1b427339b2cbd45a3050ce36ca3d`
- bridge_document_name: `gtkb-wi4524-test-session-id-leak-hardening`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4524-test-session-id-leak-hardening-001.md`
- operative_file: `bridge/gtkb-wi4524-test-session-id-leak-hardening-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4524-test-session-id-leak-hardening`
- Operative file: `bridge\gtkb-wi4524-test-session-id-leak-hardening-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Citation Freshness

```text
## Citation Freshness

No stale cross-thread citations detected.
```

## Prior Deliberations

Reviewer-run DA searches returned no relevant matches:

- `python -m groundtruth_kb.cli deliberations search "WI-4524 CLAUDE_CODE_SESSION_ID bridge propose helper session id leak" --limit 10 --json` -> `[]`
- `python -m groundtruth_kb.cli deliberations search "test_bridge_propose_helper resolve_work_intent_session_id CLAUDE_CODE_SESSION_ID" --limit 10 --json` -> `[]`

The proposal cites the owner-admission record `DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`, and the live PAUTH readback confirms that owner decision authorizes this source/test batch. The authoring-time DA-search caveat is therefore not a GO blocker for this narrow test-only proposal.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---:|---|
| `GOV-STANDING-BACKLOG-001` | Live backlog readback for `WI-4524` | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Live PAUTH readback for `PROJECT-GTKB-RELIABILITY-FIXES` | yes | PASS; batch 2 includes WI-4524 and allows source/test_addition |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4524-test-session-id-leak-hardening` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposal maps acceptance criteria to live-session env, clean-env, affected-test, and helper-locality checks | yes | PASS at proposal stage; post-implementation execution required |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path is `groundtruth-kb/tests/test_bridge_propose_helper.py` under `E:\GT-KB` | yes | PASS |

## Baseline Commands Executed

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4524-test-session-id-leak-hardening
  -> PASS: preflight_passed=true; missing_required_specs=[]; missing_advisory_specs=[]

python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4524-test-session-id-leak-hardening
  -> PASS: must_apply=5; blocking gaps=0

python scripts\bridge_citation_freshness_preflight.py --bridge-id gtkb-wi4524-test-session-id-leak-hardening
  -> PASS: no stale cross-thread citations detected

python -m pytest groundtruth-kb\tests\test_bridge_propose_helper.py::test_template_propose_bridge_acquires_and_releases_work_intent -q --tb=short
  -> 1 passed

CLAUDE_CODE_SESSION_ID=fake-live-session python -m pytest groundtruth-kb\tests\test_bridge_propose_helper.py::test_template_propose_bridge_acquires_and_releases_work_intent -q --tb=short
  -> FAILS before implementation: acquired session id is fake-live-session, expected template-session
```

## Required Implementation Evidence

The implementation report must include:

- Code evidence that the new module-local helper clears the complete work-intent env set before controlled fixture `setenv` calls.
- Static grep evidence that every affected session-id `monkeypatch.setenv` test calls the helper first, or a narrower explanation proving no other setenv site depends on controlled session resolution.
- Targeted pytest under simulated `CLAUDE_CODE_SESSION_ID=fake-live-session`.
- Targeted pytest under all session-id vars unset.
- Full `groundtruth-kb/tests/test_bridge_propose_helper.py` pytest.
- `ruff check` and `ruff format --check` for `groundtruth-kb/tests/test_bridge_propose_helper.py`.

No owner action is required for this GO.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
