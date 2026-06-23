NO-GO

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019ef047-lo-floater-keep-working-lo-2026-06-22-wi3326
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex automation LO FLOATER; approval_policy=never; workspace=E:\GT-KB
author_metadata_source: explicit automation metadata plus live harness registry

# Loyal Opposition Review: WI-3326 SessionStart phantom spec citation repoint

bridge_kind: lo_verdict
Document: gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-22 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3326
status: NO-GO

## Verdict

NO-GO.

The proposal is directionally correct: the cited phantom spec ids are real live
residue, the replacement init-keyword spec family exists, WI-3326 is an active
member of both `PROJECT-GTKB-RELIABILITY-FIXES` and
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001`, and the generic bridge preflights
pass. The proposal cannot be approved as filed because its target path and
verification plan omit existing regression tests that currently assert the
phantom ids. Prime Builder would either leave tests failing after the intended
string repoint, or need to mutate test files outside the proposal's explicit
target path envelope.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
```

Result: PASS.

Key output:

```text
preflight_passed: true
content_file: bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-001.md
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
```

Result: PASS.

Key output:

```text
must_apply: 4
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Live Backlog and Authorization Checks

- `python -m groundtruth_kb.cli backlog show WI-3326 --json` reports `resolution_status: open`, `stage: created`, `origin: defect`, and `approval_state: auq_required`.
- `python -m groundtruth_kb.cli projects show PROJECT-GTKB-RELIABILITY-FIXES --json` reports active membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3326`.
- `python -m groundtruth_kb.cli projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` reports active membership `PWM-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-3326`.
- `python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json` reports active standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, whose scope covers fast-lane work items by active project membership.

## Positive Confirmations

- The live source surfaces named by WI-3326 still contain the phantom ids:
  - `scripts/session_self_initialization.py:4452`, `:4472`, and `:4481`
  - `scripts/workstream_focus.py:2000`
  - `scripts/_session_init_keyword.py:4-6`
- The replacement specifications exist in MemBase:
  - `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
  - `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
  - `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- The current affected test suites pass before implementation, confirming the current checkout is internally consistent with the old strings:
  - `python -m pytest platform_tests\hooks\test_workstream_focus.py -q --tb=short --no-header`: 60 passed, 3 skipped.
  - `python -m pytest platform_tests\scripts\test_session_self_initialization.py -q --tb=short --no-header`: 76 passed.
  - `python -m pytest platform_tests\scripts\test_session_init_keyword_matching.py -q --tb=short --no-header`: 35 passed.

## Findings

### F1 - Target paths omit tests that assert the strings being removed

Severity: P1.

The proposal's `target_paths` line lists only:

```text
scripts/session_self_initialization.py
scripts/workstream_focus.py
scripts/_session_init_keyword.py
platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py
```

Live search shows additional tests already assert the phantom ids or document
them as specification provenance:

```text
platform_tests/hooks/test_workstream_focus.py:1043 asserts ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001
platform_tests/scripts/test_session_self_initialization.py:1031 asserts ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001
platform_tests/scripts/test_session_self_initialization.py:1058 asserts DCL-SESSION-START-INIT-KEYWORD-MATCHING-001
platform_tests/scripts/test_workstream_focus_hook_parity.py:8 cites ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001
platform_tests/scripts/test_session_init_keyword_matching.py:7-9 cites all three planned phantom ids
```

Deficiency rationale: this proposal is a citation-string repoint. Removing the
phantom ids from the three proposed source files changes the expected text of
existing tests that assert those ids. Because those test files are outside the
proposal's target path envelope, a conforming implementation cannot update all
necessary regression expectations without exceeding the reviewed scope.

Impact: Codex could issue GO on an implementation plan that is either
unbuildable under the current tests or requires out-of-scope test mutations at
implementation time. That weakens the bridge target-path gate and shifts a
known scope defect from review into implementation.

Required revision: include the affected existing test files in `target_paths`
and the allowed mutation description, or explicitly justify why each cited test
surface will remain unchanged and still pass after the source repoint. At
minimum, include:

```text
platform_tests/hooks/test_workstream_focus.py
platform_tests/scripts/test_session_self_initialization.py
platform_tests/scripts/test_workstream_focus_hook_parity.py
platform_tests/scripts/test_session_init_keyword_matching.py
```

### F2 - Verification plan omits the existing affected suites

Severity: P1.

The proposal adds a new guard test, but its implementation-time verification
commands run only that new file plus ruff. They do not run the existing suites
that currently assert or document the phantom ids.

Deficiency rationale: `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
requires verification to map to the affected behavior, not only to a new guard.
The affected behavior already has tests. Those tests must be updated and run as
part of the implementation report evidence.

Required revision: expand the verification plan to run the new guard and the
existing affected suites or focused nodes. The plan should include at least:

```powershell
python -m pytest platform_tests\hooks\test_workstream_focus.py -q --tb=short --no-header
python -m pytest platform_tests\scripts\test_session_self_initialization.py -q --tb=short --no-header
python -m pytest platform_tests\scripts\test_session_init_keyword_matching.py -q --tb=short --no-header
```

If `platform_tests/scripts/test_workstream_focus_hook_parity.py` remains only a
docstring/provenance update and has no runnable node that exercises the string,
the revised proposal should say that explicitly.

### F3 - The out-of-scope config residue now has a hygiene work item

Severity: P3.

The proposal correctly excludes `config/agent-control/system-interface-map.toml`
from WI-3326 because this bridge proposal is scoped to SessionStart/UserPromptSubmit
payload sources and standing reliability fast-lane source/test changes. However,
the proposal says the config residue is "recorded as a separable one-line config
follow-on"; live backlog search found no pre-existing item for that exact
residue.

LO filed `WI-4758` in `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` for that
cleanup:

```text
WI-4758 - Repoint system-interface-map init-keyword phantom spec citation
```

Required revision: update the Scope Boundary to cite `WI-4758` as the explicit
follow-on, or include the config citation in a separate authorized proposal.

## Required Revisions

1. Add the affected existing test files to the target path envelope, or provide
   a file-by-file justification for excluding each one.
2. Expand the spec-derived verification plan to update and run the existing
   affected test suites, not only the new guard.
3. Cite `WI-4758` for the intentionally out-of-scope config residue.

## Commands Executed

```powershell
python .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
python -m groundtruth_kb.cli backlog show WI-3326 --json
python -m groundtruth_kb.cli projects show PROJECT-GTKB-RELIABILITY-FIXES --json
python -m groundtruth_kb.cli projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
python -m groundtruth_kb.cli projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
python -m groundtruth_kb.cli spec show SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 --json
python -m groundtruth_kb.cli spec show DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 --json
python -m groundtruth_kb.cli spec show DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 --json
rg -n "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001|DCL-SESSION-START-INIT-KEYWORD-MATCHING-001|DCL-SESSION-START-APP-SCOPE-BINDING-001" -g "!groundtruth-kb/.venv/**" -g "!.git/**" -g "!*.pyc"
python -m pytest platform_tests\hooks\test_workstream_focus.py -q --tb=short --no-header
python -m pytest platform_tests\scripts\test_session_self_initialization.py -q --tb=short --no-header
python -m pytest platform_tests\scripts\test_session_init_keyword_matching.py -q --tb=short --no-header
python -m groundtruth_kb.cli backlog add --json --title "Repoint system-interface-map init-keyword phantom spec citation" ...
python -m groundtruth_kb.cli backlog show WI-4758 --json
```

## Owner Action Required

None.

File bridge scan contribution: 1 selected entry processed.

## Final Decision

NO-GO. The target-path envelope and verification plan need to cover the
existing tests that currently assert the phantom ids before this proposal can
receive GO.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
