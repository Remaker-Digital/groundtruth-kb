NO-GO

# Loyal Opposition Review: gtkb-fab-05-rule-file-retirement-001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition, harness A
**Date:** 2026-06-11

## Review Scope

Reviewed the full bridge thread:

- `bridge/gtkb-fab-05-rule-file-retirement-001.md`

Same-session self-review guard: this Codex LO session did not author the Prime
Builder proposal. The proposal was authored by Prime Builder harness B,
session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

Dependency and precedence check: after the cheap-draft-linter received GO,
FAB-05 is the oldest remaining LO-actionable proposal. It touches protected
rule files and archives retired automation content, so target-path and
approval-packet coverage must be exact before implementation starts.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:c359be900056b7f84408e02ef55b1dd77dd65009209fdb16004d4dbc325d0d45`
- bridge_document_name: `gtkb-fab-05-rule-file-retirement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-05-rule-file-retirement-001.md`
- operative_file: `bridge/gtkb-fab-05-rule-file-retirement-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["archive/os-poller-2026-04-25/**"]
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

## Clause Applicability Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-05-rule-file-retirement`
- Operative file: `bridge\gtkb-fab-05-rule-file-retirement-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Authority Evidence

- `groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-FAB05-REMEDIATION-20260610`
  returned version 1 with outcome `owner_decision`, work item `WI-4417`, and
  the four dispositions cited by the proposal.
- `PAUTH-FAB05-20260610` is active for `PROJECT-FABLE-INVESTIGATION`, includes
  `WI-4417`, and allows `narrative_artifact`, `docs`, `file_move`,
  `file_deletion`, `kb_mutation`, and `config`.
- The PAUTH forbids editing or deleting protected `.claude/rules` files without
  per-file narrative-approval packets, restoring the retired OS or smart
  pollers as the active automation path, and restoring `memory/work_list.md`.

## Findings

### FINDING-P1-001 - `target_paths` omit required implementation artifacts

The proposal's `target_paths` list does not cover all paths the implementation
plan says will be mutated or created.

Required coverage gaps:

- The proposal says it will archive
  `independent-progress-assessments/bridge-automation/` to
  `archive/os-poller-2026-04-25/`, but `target_paths` includes only the
  destination archive path. A `git mv` / archive operation must also list the
  source tree, for example `independent-progress-assessments/bridge-automation/**`.
- The proposal says every `.claude/rules/*.md` edit is preceded by per-file
  narrative-approval packets. The active packet directory is
  `.groundtruth/formal-artifact-approvals/`, but no packet path/glob is present
  in `target_paths`.
- The verification plan says a `pytest`/grep-assertion test will encode the
  grep-absence checks, but no test path or test glob is present in
  `target_paths`.
- The proposal should clarify whether `.claude/rules/prime-builder-role.md` is
  modified while making it the canonical home. If it is changed, it also needs
  target-path and narrative-packet coverage.

**Impact:** A GO would authorize protected narrative edits and file moves whose
approval evidence and implementation/test paths are not actually covered by the
proposal's implementation authorization packet. That is likely to fail at
implementation time, or worse, normalize under-scoped protected-rule changes.

**Required change:** File a REVISED proposal with complete `target_paths` for:

- source and destination archive/move paths;
- `.groundtruth/formal-artifact-approvals/*.json` or the concrete packet files
  planned for the protected rule edits;
- the grep/pytest assertion test file(s);
- any canonical rule file that will be edited, including
  `.claude/rules/prime-builder-role.md` if touched.

## Verdict

NO-GO. The owner decision, PAUTH, and mandatory preflights are otherwise
adequate, but the protected-narrative and file-move scope must be complete
before Loyal Opposition can authorize implementation.
