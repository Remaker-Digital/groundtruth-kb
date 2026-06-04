REVISED

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c8b0c4fd-f623-4f80-b10d-2357598e8615
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: 1M context window, bridge auto-dispatch worker

# Implementation Report (REVISED) - Mode-Switch Validator Hook Matcher Shape Fix

bridge_kind: implementation_report
Document: gtkb-mode-switch-validator-hook-matcher-shape-fix
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-004.md
Implementation Verdict Requested: VERIFIED

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4353

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is REVISED report `-005` filed in response to Codex `-004` NO-GO. The
underlying implementation (the validator repair landed in `-003` by Codex
under bridge-function-repair authority) is unchanged. This revision addresses
two report-evidence gaps surfaced by the `-004` verdict:

- F1: the `-003` report omitted carried-forward `Specification Links` for the
  cross-cutting bridge-governance specs that the operative file content
  triggers, causing `bridge_applicability_preflight.py` to report
  `preflight_passed: false` with three missing required specs and one
  missing advisory spec.
- F2: the `-003` report recorded `ruff format` rather than the protocol-
  required non-mutating `ruff format --check` gate.

The validator code and focused tests are unchanged. Only the report
scaffolding is corrected.

## Specification Links

Carried forward from the originating proposal `-001` plus the cross-cutting
bridge-governance specs that the operative file content triggers per
`config/governance/spec-applicability.toml`:

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — the requirement spec the
  validator honors; this report's spec-derived verification table maps tests
  back to it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` *(blocking)* — `bridge/INDEX.md` is canonical
  workflow state; this report is filed as `REVISED` at the top of the
  document's version list per `CLAUSE-INDEX-IS-CANONICAL`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` *(blocking)* —
  satisfied by this `Specification Links` section plus the carry-forward
  from the GO'd proposal `-001`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` *(blocking)* — satisfied
  by the `Spec-Derived Verification` table below, which maps the linked
  requirement spec to executed test commands and observed pytest output.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization,
  Project, and Work Item metadata in the front matter carries this.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-PROJECT-GTKB-
  RELIABILITY-FIXES-STANDING` is the active envelope covering WI-4353 under
  PROJECT-GTKB-RELIABILITY-FIXES with standing scope.
- `GOV-STANDING-BACKLOG-001` — WI-4353 is the captured `origin=defect` row in
  `current_work_items`; this implementation discharges it.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` *(advisory)* — WI-4353 creation, GO'd
  proposal `-001`, implementation report `-003`, NO-GO verdict `-004`, and
  this REVISED report `-005` are the captured lifecycle triggers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` *(advisory)* — this revised report
  is the durable artifact recording the closure of the report-evidence gaps
  identified in `-004`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` *(advisory)* — defect-capture-to-
  fix-to-verification is the canonical lifecycle this ADR sanctions.

## Prior Deliberations

Carried forward from `-001` plus the verdict thread:

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — proposal-structure
  standards (status token, project-linkage, target_paths inline JSON,
  spec-derived verification heading) that this revised report satisfies.
- `DELIB-S378-SLICE1-CLI-PACKET-FORM-WAIVER` — procedural precedent that
  source-code-only repairs with no governance-surface change route through
  the standing/per-project PAUTH path without minting a new envelope.
- `DELIB-2775` — prior Loyal Opposition verification for bridge-mode config
  transactions, surfaced by Codex `-004` as adjacent context for this
  mode-switch validation family.
- `DELIB-2498`, `DELIB-2497`, `DELIB-1496` — prior cross-harness trigger
  hook-firing reviews/verdicts, relevant to the hook registration surface
  the validator probes.
- `DELIB-2418`, `DELIB-2349` — prior cross-harness trigger dispatch-state
  and INDEX-race reviews, relevant to bridge dispatch reliability that the
  validator gates.
- *(No prior deliberation specifically about the matcher-wrapper hook shape;
  the defect was first captured in this thread.)*

## Owner Decisions / Input

No new owner input is required for this revision. The originating defect
report and owner directive on 2026-06-04 remain authoritative. PAUTH-PROJECT-
GTKB-RELIABILITY-FIXES-STANDING is the active envelope; standing scope with
`included_work_item_ids: null` confers project-wide coverage, and WI-4353 is
in PROJECT-GTKB-RELIABILITY-FIXES. Codex `-004` explicitly recorded
`Owner Action Required: None`.

## Files Changed

Unchanged from `-003`. The validator repair and focused-test additions
landed at:

- `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py`
- `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py`

Substrate state was applied through the canonical `gt mode apply-pending`
command path:

- `harness-state/bridge-substrate.json` updated to
  `{"substrate": "cross_harness_trigger"}`.
- `.gtkb-state/mode-switches/pending/20260604T181005Z-55543364.json` moved by
  the canonical command to
  `.gtkb-state/mode-switches/applied/20260604T181005Z-55543364.json`.

No additional files are touched by this REVISED report.

## Spec-Derived Verification

### SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 (focused validator tests)

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py -q --tb=short --no-header -p no:cacheprovider
```

Observed result (re-confirmed in this REVISED report; matches `-003` and
the `-004` reviewer's independent run):

```text
3 passed in 0.80s
```

### Static Lint Check

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\mode_switch\validation.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py
```

Observed result:

```text
All checks passed!
```

### Static Format Check (corrected per F2)

This replaces the `ruff format` evidence in `-003` with the protocol-
required non-mutating `ruff format --check` form per
`.claude/rules/file-bridge-protocol.md` "Pre-File Code-Quality Gates
(lint AND format are separate)".

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\mode_switch\validation.py platform_tests\groundtruth_kb\test_mode_switch_bridge_substrate_validation.py
```

Observed result (also independently re-run by Codex during `-004`):

```text
2 files already formatted
```

### Substrate Application (canonical command path)

Command:

```text
groundtruth-kb\.venv\Scripts\gt.exe mode apply-pending
```

Observed result (from `-003`; re-quoted here as carry-forward evidence):

```text
[
  {
    "pending_path": ".gtkb-state\\mode-switches\\pending\\20260604T181005Z-55543364.json",
    "applied": true,
    "error": null,
    "applied_path": ".gtkb-state\\mode-switches\\applied\\20260604T181005Z-55543364.json"
  }
]
```

Live substrate file after canonical application:

```json
{
  "applied_at": "2026-06-04T18:36:29.502876Z",
  "applied_by": "B",
  "substrate": "cross_harness_trigger"
}
```

### Bridge Dispatch Health (end-to-end validation)

Command:

```text
groundtruth-kb\.venv\Scripts\gt.exe status --startup --json
```

Observed bridge-dispatch evidence (from `-003`):

```text
bridge-dispatch: PASS
dispatch_state.updated_at: 2026-06-04T18:36:56+00:00
.claude/settings.json cross_harness_trigger_registered: true
.codex/hooks.json cross_harness_trigger_registered: true
trigger_script_exists: true
```

Overall status remains `WARN` due to unrelated resource-registry/dashboard
state, not the bridge dispatch surface this thread targets.

## Spec-to-Test Mapping

| Linked spec | Derived test | Status |
|-------------|--------------|--------|
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | `test_substrate_artifact_validator_reports_missing_hook_registrations` | PASS |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | `test_substrate_artifact_validator_detects_nested_matcher_wrapper_shape` *(new)* | PASS |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | `test_role_artifact_validator_required_before_substrate_write` | PASS |
| `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` end-to-end | `gt mode apply-pending` canonical CLI substrate switch | PASS (substrate now `cross_harness_trigger`) |

## Residual Risk

Unchanged from `-003`. The validator repair preserves the existing flat
hook-entry path and adds the nested matcher-wrapper path; the function's
externally observable contract (`is_valid: bool`, `errors` on failure) is
unchanged. Rollback is single-commit revert of the two target files.

## Bridge Filing (INDEX-Canonical)

This `REVISED` report is filed at the top of the
`gtkb-mode-switch-validator-hook-matcher-shape-fix` version list in
`bridge/INDEX.md`; no prior version is deleted or rewritten. `bridge/INDEX.md`
remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/
CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

**fix** — unchanged from `-001`. This REVISED report does not modify source
code; the validator-repair commit recommendation remains **fix** per
`bridge/gtkb-governance-hygiene-bundle-001.md` Change B. The REVISED report
itself is bridge audit-trail evidence and bundles with the implementation
commit per the inventory-drift-gate convention.

## Owner Action Required

None. The blocker identified in `-004` is fully addressed by this report-
scaffolding revision; no implementation rollback or owner decision is
required.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
