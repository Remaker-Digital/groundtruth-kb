NO-GO

# Loyal Opposition Verification - Release-Candidate Gate Managed Skill

bridge_kind: verification_verdict
Document: gtkb-release-candidate-gate-managed-skill
Version: 008
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-release-candidate-gate-managed-skill-007.md
Work Item: GTKB-GOV-002

## Verdict

NO-GO.

The implementation report cannot receive VERIFIED because the mandatory clause
preflight fails a blocking `GOV-FILE-BRIDGE-AUTHORITY-001` clause on the indexed
operative report. The implementation report states that `impl_report_bridge.py`
will insert the live `NEW` row, but it does not record that `bridge/INDEX.md`
was updated with the correct indexed status or that prior versions remain
append-only. The live thread is indexed correctly; this is a report-evidence
defect, not an implementation correctness finding.

## Applicability Preflight

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:03fdcf7ec7106960910d8fb290b9fc7c63416f5372ac45a36409c1535475c475`
- bridge_document_name: `gtkb-release-candidate-gate-managed-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-release-candidate-gate-managed-skill-007.md`
- operative_file: `bridge/gtkb-release-candidate-gate-managed-skill-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-release-candidate-gate-managed-skill`
- Operative file: `bridge\gtkb-release-candidate-gate-managed-skill-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Blocking gaps (gate-failing): 1
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | **no** | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

### Blocking Gaps (gate-failing must_apply clauses without evidence or owner waiver)

- **`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`** (blocking, blocking)
  - Gap: Evidence missing: Bridge artifact filed under bridge/ with INDEX.md entry of correct status; no deletion or rewrite of prior versions.
  - Evidence required: Bridge artifact filed under bridge/ with INDEX.md entry of correct status; no deletion or rewrite of prior versions.
  - Detector note: evidence pattern `(?i)(?:bridge/INDEX\.md|INDEX update|insert.+top of.+(?:INDEX|entry))` did not match

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

Search command:

```text
groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.cli import main; main()" deliberations search "release candidate gate managed skill GTKB-GOV-002 implementation report index canonical" --limit 8
```

Relevant results:

- `DELIB-2368` - prior Loyal Opposition NO-GO on the original release-candidate
  gate managed-skill proposal.
- `DELIB-1074` - prior governance-adoption report identifying reusable release
  candidate gate follow-up work.
- `DELIB-0829` - original owner directive for GTKB-GOV-001/002/003 adoption and
  release-gate follow-up.
- `DELIB-2782`, `DELIB-2783`, and `DELIB-2803` - bridge INDEX compaction
  snapshots, relevant only as INDEX authority context.

No deliberation found that waives
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` for this report.

## Specifications Carried Forward

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill` | yes | failed; blocking INDEX-canonical evidence gap |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill` | yes | passed; no missing required/advisory specs |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-release-candidate-gate-managed-skill --format json --preview-lines 260` | yes | full thread loaded; latest report carries forward approved spec links |

## Positive Confirmations

- Live `bridge/INDEX.md` resolves the thread with latest `NEW:
  bridge/gtkb-release-candidate-gate-managed-skill-007.md`; the helper reported
  `drift: []`.
- `bridge/gtkb-release-candidate-gate-managed-skill-007.md` identifies itself
  as a Prime Builder implementation report and was not created by this Loyal
  Opposition session.
- `git log -1 -- bridge/gtkb-release-candidate-gate-managed-skill-007.md`
  reports commit `24e90671b5da9c71ba0dfefc2a491900d3fca62e` with subject
  `feat: add release candidate gate managed template`.
- Target-path `git status` showed no uncommitted changes for the implementation
  report's three claimed source/test paths.

## Findings

### F1 - Implementation report lacks canonical INDEX evidence required by the mandatory clause preflight

Severity: P1 / blocking

Observation:

The indexed operative implementation report does not include a completed
`bridge/INDEX.md` update/evidence statement. Its only matching bridge-write
sentence is prospective: `impl_report_bridge.py file` "will insert the live
`NEW` row after credential and concurrency gates."

Deficiency rationale:

The Clause Applicability gate for
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` requires evidence that
the bridge artifact was filed under `bridge/`, indexed with the correct status,
and preserved prior versions. Because the report speaks in future tense and
does not name `bridge/INDEX.md` or an completed INDEX update, the detector
rightly fails the blocking clause. The bridge protocol and Codex review gate
require LO to issue `NO-GO` when the mandatory clause preflight reports a
blocking gap without an owner waiver.

Evidence:

- `bridge/gtkb-release-candidate-gate-managed-skill-007.md` includes the
  prospective evidence sentence in its specification-derived verification plan.
- The mandatory clause preflight output above reports `Evidence found: no` and
  `Blocking gaps (gate-failing): 1`.
- `bridge/gtkb-release-candidate-gate-managed-skill-007.md` contains no owner
  waiver for the missing clause evidence.

Impact:

Recording `VERIFIED` despite the failed clause gate would weaken the mandatory
verification floor and make the bridge report less auditable than the live
INDEX state. Prime Builder would have an implementation report that cannot
reproduce the evidence needed by the hard preflight.

Proposed solution:

Prime Builder should file a revised implementation report that replaces the
prospective wording with completed filing evidence. At minimum, cite the live
`bridge/INDEX.md` row, state that `NEW:
bridge/gtkb-release-candidate-gate-managed-skill-007.md` was inserted at the
top of the document entry, and state that prior versions were preserved
append-only. Then rerun:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
```

Option rationale:

This is the smallest safe correction. It does not require changing the
implementation files, re-scoping the proposal, or adding owner input. It only
requires the report to carry the bridge-authority evidence that already exists
in live `bridge/INDEX.md`.

### F2 - Release gate defaults to the skill template directory instead of the adopter project root

Severity: P1 / blocking

Observation:

The bundled script sets `PROJECT_ROOT = Path(__file__).resolve().parent.parent`.
For the managed template path, that resolves to
`E:\GT-KB\groundtruth-kb\templates\skills\release-candidate-gate`, not the
adopter project root. All `_run(...)` calls execute with `cwd=PROJECT_ROOT`, and
the requirements-file lookup also uses `PROJECT_ROOT`. The focused test
`test_template_script_command_order` monkeypatches `PROJECT_ROOT` to
`Path.cwd()`, so the test does not prove default adopter-root execution.

Deficiency rationale:

The approved slice is an adopter-facing release-candidate gate. Its default
commands include `python -m groundtruth_kb project doctor .`, `pytest tests`,
`ruff check src tests`, dependency audit against `requirements.txt`, and
optional frontend builds. Running those commands from the skill template
directory checks the template package location, not the adopting project. That
can make the managed skill fail in normal adopter use or, worse, evaluate the
wrong root while the focused tests still pass under monkeypatched state.

Evidence:

- `groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py`
  defines `PROJECT_ROOT = Path(__file__).resolve().parent.parent`.
- The same script passes `cwd=PROJECT_ROOT` to `subprocess.run(...)` and checks
  `PROJECT_ROOT / config.requirements_file`.
- `groundtruth-kb/tests/test_release_candidate_gate_template.py` monkeypatches
  `module.PROJECT_ROOT` to `Path.cwd()` before asserting command order.
- Import probe result:
  `E:\GT-KB\groundtruth-kb\templates\skills\release-candidate-gate`.

Impact:

The implemented managed skill is not verified against its intended adopter
execution model. A future adopter could run the gate and have it look for
`src`, `tests`, `requirements.txt`, and governance state in the template
directory rather than the project under review.

Proposed solution:

Prime Builder should revise the implementation so the execution root is the
adopter project root by default, for example `Path.cwd()` or an explicit
`--project-root` argument defaulting to the current working directory. Then add
a focused regression test that imports/runs the unpatched module and proves
default command execution and requirements lookup use the adopter project root,
not the skill template directory.

Option rationale:

Fixing the execution-root selection is smaller and safer than broadening this
slice into registry binding. It preserves the template-only scope while making
the delivered artifact usable in the adopter context it is meant to support.

## Required Revisions

1. File a revised implementation report for this thread.
2. Add completed `bridge/INDEX.md` evidence for the post-implementation report
   filing and append-only version chain.
3. Rerun the clause preflight and include the passing output.
4. Correct the release-candidate-gate script's default project-root behavior so
   commands run against the adopter project root.
5. Add a focused regression test proving the default root behavior without
   monkeypatching `PROJECT_ROOT`.
6. Preserve the existing implementation/test evidence unless other changes are
   made.

## Commands Executed

```text
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python .claude\skills\bridge\helpers\scan_bridge.py --role prime-builder --format json
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-release-candidate-gate-managed-skill --format json --preview-lines 260
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-managed-skill
groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.cli import main; main()" deliberations search "release candidate gate managed skill GTKB-GOV-002 implementation report index canonical" --limit 8
git status --short -- groundtruth-kb\templates\skills\release-candidate-gate\SKILL.md groundtruth-kb\templates\skills\release-candidate-gate\scripts\release_candidate_gate.py groundtruth-kb\tests\test_release_candidate_gate_template.py bridge\gtkb-release-candidate-gate-managed-skill-007.md bridge\INDEX.md
git log -1 --format="%H %an %ad %s" -- bridge\gtkb-release-candidate-gate-managed-skill-007.md
Select-String -Path bridge\gtkb-release-candidate-gate-managed-skill-007.md -Pattern "INDEX|impl_report_bridge|bridge/INDEX|insert|NEW row|Owner waiver" -CaseSensitive:$false
rg -n "PROJECT_ROOT|Path\(|cwd|doctor|pytest|frontend|ROOT" groundtruth-kb\templates\skills\release-candidate-gate\scripts\release_candidate_gate.py
rg -n "PROJECT_ROOT|monkeypatch|release_candidate_gate|cwd|project root|tmp_path|doctor" groundtruth-kb\tests\test_release_candidate_gate_template.py
groundtruth-kb\.venv\Scripts\python.exe -c "import importlib.util, sys; from pathlib import Path; p=Path('groundtruth-kb/templates/skills/release-candidate-gate/scripts/release_candidate_gate.py'); spec=importlib.util.spec_from_file_location('rcg', p); m=importlib.util.module_from_spec(spec); sys.modules['rcg']=m; spec.loader.exec_module(m); print(m.PROJECT_ROOT)"
```

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
