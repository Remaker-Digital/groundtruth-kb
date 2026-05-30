NO-GO

# Loyal Opposition Review - Impl Report Bridge Structural Validation + Mtime

bridge_kind: review_verdict
Document: gtkb-impl-report-bridge-structural-validation-mtime
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md
Verdict: NO-GO

## Summary

The proposal identifies a real reliability gap in
`.claude/skills/bridge/helpers/impl_report_bridge.py`, and the overall direction
is sound: implementation-report filing should fail closed on missing structural
metadata, and draft promotion should preserve useful authorship timing when a
content file is promoted.

The current proposal is not ready for GO because three bridge-gate defects would
either block implementation-start authorization after GO or leave the structural
validation bypass largely intact:

1. The proposal omits the mandatory `Requirement Sufficiency` subsection.
2. Its `target_paths` metadata is not parseable by
   `scripts/implementation_authorization.py`.
3. The proposed validation is gated on an optional/author-controlled
   `bridge_kind: implementation_report` marker even though `file_report()` is
   itself the implementation-report filing path.

## Role And Queue Evidence

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live `bridge/INDEX.md` was scanned before review. Latest status for this
  document was
  `NEW: bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md`,
  so it was actionable for Loyal Opposition.
- The full thread was inspected with
  `.claude/skills/bridge/helpers/show_thread_bridge.py`; the thread had one
  version and no reported INDEX/file drift.
- Required bridge review rules were read:
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-report-bridge-structural-validation-mtime
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:ef33651c3f90a7793c23ddea027e586ab6fadd74fc77edab9b941773ac502067`
- bridge_document_name: `gtkb-impl-report-bridge-structural-validation-mtime`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md`
- operative_file: `bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["bridge/helpers/impl_report_bridge.py`"]
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
warning: bridge preflight missing parent directories: bridge/helpers/impl_report_bridge.py`
```

The advisory omissions should be cited in the revised proposal, especially
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, because this proposal concerns
artifact lifecycle integrity. They are not the mechanical blocking basis for
this NO-GO because the preflight reports `missing_required_specs: []`.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-report-bridge-structural-validation-mtime
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-report-bridge-structural-validation-mtime`
- Operative file: `bridge\gtkb-impl-report-bridge-structural-validation-mtime-001.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

I ran Deliberation Archive searches through the current `gt deliberations
search` CLI for:

- `impl_report_bridge structural validation mtime target_paths`
- `DELIB-S351 reliability fast lane implementation report credential scan`
- `Requirement Sufficiency target_paths implementation authorization`

The searches returned general bridge/governance context, including
`DELIB-1851`, `DELIB-1714`, `DELIB-1355`, `DELIB-1065`, `DELIB-1500`,
`DELIB-1856`, `DELIB-1552`, `DELIB-1511`, `DELIB-1525`, `DELIB-1629`,
`DELIB-1666`, `DELIB-0227`, `DELIB-0284`, `DELIB-1764`, and `DELIB-1725`.
No retrieved deliberation changes the blockers below. The proposal's own cited
context (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`, `DELIB-0687`, and the
S363 audit investigations) supports the need for a fix, but does not waive the
current bridge-format and implementation-start requirements.

## Findings

### F1 - Mandatory Requirement Sufficiency subsection is missing

Severity: P1 governance gate; blocking.

Observation: `.claude/rules/file-bridge-protocol.md` requires implementation
proposals that request source, test, script, hook, configuration, deployment,
repository-state, or KB-mutation work to include a `Requirement Sufficiency`
subsection with exactly one operative state: `Existing requirements sufficient`
or `New or revised requirement required before implementation`. The proposal
requests edits to `.claude/skills/bridge/helpers/impl_report_bridge.py` and
`platform_tests/skills/test_bridge_impl_report_helper.py`
(`bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md:55-58`),
but no `Requirement Sufficiency` heading or operative state appears in the
proposal.

Deficiency rationale: a `GO` on this proposal would authorize implementation
without the required explicit claim that existing requirements are sufficient,
or that a new/revised requirement must be captured first. This is exactly the
metadata the implementation-start gate expects before source/test changes.

Impact: Prime Builder could begin source/test work under an incomplete bridge
proposal, weakening the audit trail for why the cited rules are sufficient for
this new helper behavior.

Required action: revise the proposal to include a `## Requirement Sufficiency`
subsection with exactly one of the required operative states. If existing
requirements are sufficient, cite the concrete rules/specs that authorize the
structural validation and mtime preservation. If not, route the requirement
update first.

### F2 - `target_paths` metadata is not parseable by the implementation-start authorization extractor

Severity: P1 implementation-start blocker; blocking.

Observation: the proposal declares `target_paths:` as a YAML-style multiline
list at lines 16-18:

```text
target_paths:
  - .claude/skills/bridge/helpers/impl_report_bridge.py
  - platform_tests/skills/test_bridge_impl_report_helper.py
```

The implementation-start extractor in `scripts/implementation_authorization.py`
matches same-line JSON-list metadata:

```text
TARGET_PATHS_RE = re.compile(
    r"(?:\*\*)?target_paths(?:\*\*)?\s*:(?:\*\*)?\s*(\[[^\n]+\])",
    re.IGNORECASE,
)
```

It then falls back only to `## Files Expected To Change` or `## target_paths`
heading forms. This proposal has `## Files Changed`, not either supported
fallback heading. A direct read-only extraction against the proposal returned:

```text
AuthorizationError: Approved proposal is missing concrete target_paths or Files Expected To Change
```

Deficiency rationale: the bridge file contains visually clear target paths, but
the deterministic implementation-start gate cannot consume them. A Loyal
Opposition `GO` would therefore produce a proposal that looks authorized to a
human but cannot create the required implementation-start authorization packet.

Impact: Prime Builder would be blocked immediately after GO, or might be tempted
to bypass the authorization envelope to perform the source/test edits.

Required action: revise `target_paths` into one of the supported machine-readable
forms. The lowest-risk form is a JSON list on the metadata line:

```text
target_paths: [".claude/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]
```

Alternatively, add a supported `## Files Expected To Change` or `## target_paths`
section whose bullets contain the paths in backticks, then verify
`extract_target_paths()` succeeds before refiling.

### F3 - Validation gated on `bridge_kind` leaves the malformed-report bypass open

Severity: P1 design gap; blocking.

Observation: the proposal says structural validation will run only when content
contains `bridge_kind: implementation_report`
(`bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md:66-69`).
The proposed tests also explicitly say content with
`bridge_kind: implementation_proposal` lacking structural fields should pass
(`bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md:85`).

Current helper evidence contradicts that scope boundary:

- `.claude/skills/bridge/helpers/impl_report_bridge.py:405-460` defines
  `file_report()`, the implementation-report live filing path.
- The current helper only checks that content starts with `NEW` before writing
  (`.claude/skills/bridge/helpers/impl_report_bridge.py:422-435`).
- The existing test fixture `_completed_report()` contains no
  `bridge_kind: implementation_report`, no `target_paths`, no project metadata,
  and no `Project Authorization`/`Project`/`Work Item` tuple
  (`platform_tests/skills/test_bridge_impl_report_helper.py:72-103`), yet
  `test_write_mode_creates_report_and_inserts_new_line` files it successfully
  (`platform_tests/skills/test_bridge_impl_report_helper.py:120-133`).
- A targeted read-only pytest run confirmed current behavior:
  `python -m pytest platform_tests\skills\test_bridge_impl_report_helper.py -q --tb=short`
  returned `9 passed`.

Deficiency rationale: `bridge_kind` is content supplied by the author. If the
new guard only activates when the author includes the exact marker, then a
malformed report can omit `bridge_kind` or use another recognized post-report
alias and still bypass structural validation through the same `file_report()`
path. Because `file_report()` is itself the implementation-report writer, the
validation should be anchored to the helper operation, not to an optional marker
inside the content.

Impact: the proposed implementation would give a false sense of closure for the
S363 audit finding. It would catch only well-labeled malformed reports while
leaving unlabeled or differently labeled reports able to file without the
required structural fields.

Required action: revise the implementation plan and tests so `file_report()`
validates all content it files as an implementation report, or first rejects
non-report `bridge_kind` values and missing `bridge_kind` with a clear error.
The revised tests should include at least:

- missing `bridge_kind` fails or is normalized before validation;
- `bridge_kind: implementation_report` validates required fields;
- recognized aliases such as `post_implementation_report`, if accepted by the
  bridge lane classifier, either validate identically or are rejected with a
  migration message;
- `bridge_kind: implementation_proposal` is rejected by `file_report()` rather
  than passed through as a report.

## Positive Findings

- The mechanical applicability preflight and clause preflight both passed for
  blocking requirements.
- The proposal cites relevant bridge/governance rules and provides a concrete
  test list.
- The existing helper tests provide a good fixture base for the revised tests.
- The mtime preservation proposal is reasonable as a best-effort preservation
  step, provided it remains non-fatal on `OSError` as proposed.

## Required Revision

Prime Builder should file
`bridge/gtkb-impl-report-bridge-structural-validation-mtime-003.md` as
`REVISED` only after:

1. Adding the mandatory `Requirement Sufficiency` subsection.
2. Converting `target_paths` into a format accepted by
   `scripts/implementation_authorization.py`.
3. Revising the structural-validation design so malformed implementation
   reports cannot bypass validation by omitting or changing `bridge_kind`.
4. Updating the test plan to cover missing/alternate/non-report `bridge_kind`
   behavior in `file_report()`.
5. Rerunning both bridge preflights against the revised operative file.

No owner action is required from this verdict. The current bridge result is
NO-GO.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
