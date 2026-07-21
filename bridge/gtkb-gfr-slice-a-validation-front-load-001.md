NEW
::init gtkb lo
::open build

# Implementation Proposal — GFR Slice A: Validation front-load

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-a-validation-front-load
Version: 001
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Project Authorization: PAUTH-GFR-PROGRAM-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5644

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/implementation_authorization.py", "scripts/bridge_author_metadata.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_implementation_authorization.py"]

Implementation proposal for governance friction reduction — Slice A (validation front-load).

## Claim

Slice A of the Governance Friction Reduction program (per GO'd advisory `bridge/gtkb-governance-friction-reduction-002.md`) eliminates the highest-leverage friction source: staggered, one-error-at-a-time validation failures at `begin` time. The advisory documented **six** consecutive `begin` failures, each naming a new missing field, after GO was already received. The fix is to **front-load** metadata and target-path checks to preflight (filing) time, **auto-resolve** PAUTH references in error messages, and **warn** on unclassified target paths — without weakening any control.

This slice implements four findings from the advisory:

1. **Finding 2.1 — Extend preflight with begin-time metadata checks**: `bridge_applicability_preflight.py` already parses `target_paths` and `Responds to` and emits a packet hash, but it does NOT check for the metadata fields that `implementation_authorization.py begin` requires: `author_identity`, `author_session_context_id`, `author_model`, `author_model_version`, `author_model_configuration`. The fix extends the preflight packet to include an `author_metadata_warnings` list that flags missing required author-metadata fields. This catches format issues at filing time (NEW/REVISED), before any review cycle — not after GO. **Safe because the rules do not change; only when they are checked does.**

2. **Finding 2.2 — Auto-stamp mechanical bridge metadata**: `bridge_author_metadata.py` already has `REQUIRED_AUTHOR_METADATA_FIELDS` and per-field env-var resolution (`FIELD_ENV_NAMES`), but there is no function that resolves ALL fields at once and emits them in a format ready to paste into a bridge file. The fix adds a `resolve_author_metadata()` function that returns a dict of all resolved metadata fields from env vars, and a `--emit` CLI mode that outputs resolved metadata as YAML frontmatter lines. This allows agents to get correct metadata without guessing or discovering fields one error at a time. **Safe because the metadata is mechanical facts (session ID, harness ID, model name), not judgments.**

3. **Finding 2.3 — Auto-resolve PAUTH references in begin errors**: When `begin` fails because no PAUTH covers the target_paths, the error message currently says "Project Authorization is required" without surfacing which PAUTH(s) might cover the targets. The fix adds a lookup in `create_authorization_packet` (or the error path) that searches active PAUTHs for ones whose `allowed_mutation_classes` and `included_work_item_ids` cover the proposal's target_paths and work item, and includes matching PAUTH IDs in the error message. **Safe because it is lookup, not grant.**

4. **Finding 2.4 — Unclassified target_paths warning**: `classify_target` in `project_authorization_operation_time.py` returns `"unclassified"` when no classifier rule matches, but the preflight does not surface this. The fix extends `bridge_applicability_preflight.py` to classify each declared `target_path` using `classify_target` and add an `unclassified_target_paths` warnings list when any path resolves to `unclassified`. This prevents the trial-and-error glob refinement documented in the advisory. **Safe because it removes a trial-and-error loop, not a control.**

## Requirement Sufficiency

Existing requirements are sufficient for this slice. The advisory's findings are all enforcement-timing and surfacing changes — no new specifications or requirement changes are needed. The governing specifications cited below provide the authority and linkage requirements; this slice implements within their scope.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/bridge_applicability_preflight.py` ✅
- `scripts/implementation_authorization.py` ✅
- `scripts/bridge_author_metadata.py` ✅
- `platform_tests/scripts/test_bridge_applicability_preflight.py` ✅
- `platform_tests/scripts/test_implementation_authorization.py` ✅

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specifications; implementation does not proceed without LO GO.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines who may author which status tokens; this proposal is authored by Prime Builder (prime-builder/goose).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance is the default interpretation stance; these changes preserve durable artifacts (preflight extensions, metadata resolver).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification will require spec-to-test mapping; the linked test (TEST-11689) verifies that new preflight checks and PAUTH auto-resolve work correctly.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes the three mandatory header lines (Project Authorization, Project, Work Item).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are within the GT-KB root boundary.
- `GOV-STANDING-BACKLOG-001` — the GFR program was added to the standing backlog via WIs WI-5643 through WI-5646.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — these changes convert informal session-discovered friction into durable code-level enforcement.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the preflight extensions and metadata resolver are durable artifacts triggered by the advisory's threshold crossing.
- `DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-FORMAT-001` — relevant to target_paths extraction format (Finding 2.4 classification).

## Prior Deliberations

- `DELIB-202667078` — Owner approval: Governance Friction Reduction program. Owner approved proceeding with the 4-slice program per GO'd advisory `gtkb-governance-friction-reduction-002`.
- `DELIB-20263490` — Loyal Opposition Progress & Verification Report — Terminology & Bridge Reconciliation. Relevant to metadata field naming and provenance.
- `DELIB-20265747` — Loyal Opposition GO verdict: WI-4716 bridge-propose semantic-search doc sync. Relevant to bridge metadata validation.

### Helper-suggested candidates

_No prior deliberations beyond those listed above._

## Owner Decisions / Input

- `DELIB-202667078` (AUQ GFR-PAUTH-001) — Owner answer: "1 - Yes, proceed". Authorizes creating the GFR project, 4 per-slice WIs, PAUTH, and filing per-slice implementation proposals.
- `PAUTH-GFR-PROGRAM-20260721` — Active project authorization covering WI-5643 through WI-5646 with source/test/config mutation classes. This PAUTH was created under formal-artifact-approval DELIB-202667078.

## Cross-Harness Disposition

This proposal touches only `scripts/` and `platform_tests/` files — no harness-surface files (`.claude/skills/`, `.codex/skills/`, etc.) are modified. No adapter regeneration is required.

| Harness | Surface | Parity Status | Disposition |
|---|---|---|---|
| Claude Code | `scripts/` (platform scripts) | N/A — platform code | Changes are to platform scripts, not harness-surface files. |
| Codex | `scripts/` (platform scripts) | N/A — platform code | Same; no adapter regeneration needed. |
| All others | N/A | N/A | No harness-surface files touched. |

**No typed waiver required.** No downstream adapter regeneration needed.

## Proposed Scope

### Finding 2.1 — Extend preflight with begin-time metadata checks

**File:** `scripts/bridge_applicability_preflight.py`

Add a new function `_check_author_metadata_presence(content: str) -> list[str]` that:
- Parses the content for each field in `REQUIRED_AUTHOR_METADATA_FIELDS` (imported from `bridge_author_metadata`)
- Returns a list of warning strings for any missing field
- Does NOT raise or set `preflight_passed = False` — these are advisory warnings, not blocking errors, because some proposal types (advisory, governance review) may not need all fields

Integrate into `build_packet()`:
- Add `author_metadata_warnings` to the packet dict
- Include in the `warnings` sub-dict alongside existing `missing_parent_dirs` and `spec_links_section`
- Display in `format_markdown()` output

**Import:** Add `from bridge_author_metadata import REQUIRED_AUTHOR_METADATA_FIELDS` (with fallback import for direct script execution).

**Key design decision:** These are warnings, not blocking errors, because:
1. Advisory proposals don't need PAUTH or `Responds to`
2. The preflight runs at filing time when some fields may not yet be relevant
3. The `begin` validator remains the authoritative gate (LO note N1)

### Finding 2.2 — Auto-stamp metadata resolver

**File:** `scripts/bridge_author_metadata.py`

Add a new function `resolve_author_metadata() -> dict[str, str]` that:
- Iterates over `REQUIRED_AUTHOR_METADATA_FIELDS` and `OPTIONAL_AUTHOR_METADATA_FIELDS`
- For each field, tries the env vars listed in `FIELD_ENV_NAMES[field]` in order
- Returns a dict of `{field_name: resolved_value}` for all fields that resolve
- Fields that don't resolve are omitted from the dict (caller can check for completeness)

Add a `--emit` CLI mode to the existing `main()` (or create a new `main()` if none exists):
- Outputs resolved metadata as YAML-like frontmatter lines: `author_identity: <value>`
- Exit code 0 if all required fields resolve, 1 if any are missing
- This allows agents to run `python scripts/bridge_author_metadata.py --emit` and paste the output into their proposal draft

**Key design decision:** This is a read-only resolver — it does not write to any file. The agent or filing helper decides whether to use the output. The existing `AUTHOR_METADATA_RELATIVE_PATH` write path is NOT extended (WI-4522 removed the loader's read of that file; we don't re-introduce a write path).

### Finding 2.3 — PAUTH auto-resolve in begin errors

**File:** `scripts/implementation_authorization.py`

In `create_authorization_packet()`, when the `extract_and_validate_project_authorization` call raises an `AuthorizationError` (caught and appended to `errors`), add a lookup that:
- Queries `current_project_authorizations` for active PAUTHs
- For each active PAUTH, checks if its `included_work_item_ids` contains the proposal's work item ID
- If matches are found, appends a hint to the error message: `"Hint: active PAUTH(s) covering work item <WI-ID>: PAUTH-XXX, PAUTH-YYY. Add 'Project Authorization: PAUTH-XXX' to the proposal header."`
- If no matches are found, the error remains as-is (no false hint)

Add a helper function `_suggest_pauth_for_work_item(project_root: Path, work_item_id: str | None) -> list[str]` that:
- Opens `groundtruth.db` read-only
- Queries `SELECT id FROM current_project_authorizations WHERE status = 'active'`
- For each row, checks if `included_work_item_ids` (JSON list) contains `work_item_id`
- Returns matching PAUTH IDs

**Key design decision (LO note N1):** The PAUTH lookup happens AFTER `target_paths` extraction (which is already the case in the existing code — `extract_target_paths` is called before `extract_and_validate_project_authorization`). The ordering dependency is preserved.

### Finding 2.4 — Unclassified target_paths warning

**File:** `scripts/bridge_applicability_preflight.py`

In `build_packet()`, after extracting `declared_target_paths`:
- Import `classify_target` from `groundtruth_kb.governance.project_authorization_operation_time`
- For each declared target path, call `classify_target(path)` and check if `mutation_class == "unclassified"`
- Collect unclassified paths into `unclassified_target_paths` list
- Add to the `warnings` sub-dict in the packet
- Display in `format_markdown()` output

**Import:** Add `from groundtruth_kb.governance.project_authorization_operation_time import classify_target` with a try/except fallback (the preflight already imports from `groundtruth_kb` via `implementation_authorization`).

**Key design decision:** This is a warning, not a blocking error, because:
1. `unclassified` paths may be intentionally unclassified (new file types)
2. The `begin` validator remains the authoritative gate
3. The warning surfaces the issue early so the agent can refine the glob before `begin` fails

### Test additions

**File:** `platform_tests/scripts/test_bridge_applicability_preflight.py`

Add tests:
1. `test_preflight_warns_on_missing_author_metadata` — proposal content missing `author_identity` → `author_metadata_warnings` includes the field name
2. `test_preflight_no_metadata_warnings_when_complete` — proposal with all required metadata → empty `author_metadata_warnings`
3. `test_preflight_warns_on_unclassified_target_paths` — `target_paths` with a path like `foo/bar.xyz` (no classifier rule) → `unclassified_target_paths` includes it
4. `test_preflight_no_unclassified_warnings_for_known_paths` — `target_paths` with `scripts/foo.py` → empty `unclassified_target_paths`

**File:** `platform_tests/scripts/test_implementation_authorization.py`

Add test:
1. `test_begin_error_includes_pauth_hint` — proposal with work item in an active PAUTH's `included_work_item_ids` but no `Project Authorization:` header → error message includes "Hint: active PAUTH" with the matching PAUTH ID

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "enforcement-timing and surfacing changes to platform scripts",
  "provenance": "GO'd advisory gtkb-governance-friction-reduction-002; owner decision DELIB-202667078",
  "canonical_authority": "bridge_applicability_preflight.py; implementation_authorization.py; bridge_author_metadata.py",
  "primary_route": "additive: new preflight checks, new metadata resolver function, new PAUTH hint in error messages, new test coverage",
  "before_behavior": "agents discover missing metadata, unclassified paths, and missing PAUTH one error at a time at begin, after GO",
  "after_behavior": "agents see metadata warnings, unclassified path warnings at preflight (filing) time; begin errors include PAUTH hints",
  "self_descriptive_naming": "resolve_author_metadata, _suggest_pauth_for_work_item, author_metadata_warnings, unclassified_target_paths",
  "obsolete_guidance_disposition": "no existing guidance is superseded; all changes are additive",
  "history_preservation": "no existing artifacts are deleted or rewritten; existing functions are extended, not replaced",
  "baseline": "existing tests + ruff check + ruff format --check",
  "expected_result": "all tests pass, ruff clean, new preflight checks and PAUTH hint work",
  "rollback": "revert the commit; no data migration or state change to roll back",
  "hard_invariants": "begin validator remains authoritative; preflight warnings are advisory; PAUTH grant is not automated",
  "fail_closed_conditions": "missing metadata warnings do not block filing; begin remains the hard gate",
  "essential_context_preservation": "all changes are durable code artifacts (scripts, tests)"
}
```

## Specification-Derived Verification Plan

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Verify this proposal cites all governing specs (visual inspection) | yes | (pending) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short` | (pending) | (pending) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify proposal author identity matches resolved session role | yes | (pending) |
| `GOV-12` | Verify TEST-11689 exists and is linked to WI-5644 | yes | (pending) |
| `GOV-13` | Verify TEST-11689 is assigned to PHASE-001 | yes | (pending) |

## Acceptance Criteria

1. `bridge_applicability_preflight.py` `build_packet()` output includes `author_metadata_warnings` in the `warnings` sub-dict when required author-metadata fields are missing from the proposal content.
2. `bridge_applicability_preflight.py` `build_packet()` output includes `unclassified_target_paths` in the `warnings` sub-dict when any declared target path classifies as `unclassified`.
3. `bridge_author_metadata.py` exports `resolve_author_metadata()` that returns a dict of resolved metadata fields from env vars.
4. `bridge_author_metadata.py` `--emit` CLI mode outputs resolved metadata as YAML-like frontmatter lines.
5. `implementation_authorization.py` `create_authorization_packet()` error messages include PAUTH ID hints when a matching active PAUTH is found for the proposal's work item.
6. New tests in `test_bridge_applicability_preflight.py` and `test_implementation_authorization.py` pass.
7. All existing tests pass: `python -m pytest platform_tests/scripts/ -q --tb=short`.
8. `ruff check` and `ruff format --check` pass on modified scripts.
9. No existing governance gate is weakened or removed — preflight warnings are advisory, `begin` remains authoritative.

## Risks / Rollback

- **Risk: Preflight import of `classify_target`** — the preflight runs as a standalone script; importing from `groundtruth_kb.governance` may fail if the package is not on the path. Mitigation: use try/except with a fallback that skips the unclassified check if the import fails (fail-soft).
- **Risk: PAUTH query performance** — the `_suggest_pauth_for_work_item` function opens the DB read-only. Mitigation: the query is a simple SELECT with a small result set; add a LIMIT 10.
- **Risk: Metadata resolver env-var drift** — if new env vars are added to `FIELD_ENV_NAMES` but not to the resolver, the resolver may miss fields. Mitigation: the resolver iterates over `FIELD_ENV_NAMES` dynamically, so new fields are automatically included.
- **Risk: False-positive unclassified warnings** — new file types may legitimately be `unclassified`. Mitigation: warnings are advisory, not blocking; the agent can ignore them if the path is intentionally unclassified.
- **Rollback:** Revert the commit. No data migration, no state change. All changes are additive code in scripts and tests.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py` — add metadata-presence checks, unclassified target_paths warnings
- `scripts/implementation_authorization.py` — add PAUTH auto-resolve hint in error messages
- `scripts/bridge_author_metadata.py` — add `resolve_author_metadata()` function and `--emit` CLI mode
- `platform_tests/scripts/test_bridge_applicability_preflight.py` — add tests for new preflight checks
- `platform_tests/scripts/test_implementation_authorization.py` — add test for PAUTH auto-resolve hint

## Recommended Commit Type

`feat`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
