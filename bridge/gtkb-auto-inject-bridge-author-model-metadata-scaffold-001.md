NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Auto-inject bridge proposal author/model audit metadata block (6 lines) in scaffold step

bridge_kind: prime_proposal
Document: gtkb-auto-inject-bridge-author-model-metadata-scaffold
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3495

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/tests/test_cli_bridge_propose.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The `gt bridge propose` deterministic draft CLI (`groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`) emits a proposal scaffold whose `_BASE_TEMPLATE` (lines 57-117) places the status token `NEW`, then the `# Title`, then the `bridge_kind:` / `Document:` / `Version:` / `Date:` block — but never emits the six-line author/model audit metadata block (`author_identity`, `author_harness_id`, `author_session_context_id`, `author_model`, `author_model_version`, `author_model_configuration`) that every bridge artifact carries (see the gold-standard exemplar `bridge/gtkb-project-pauth-autocomplete-verified-gate-001.md` lines 2-7). The author must therefore add those six lines by hand on every draft, and the values that CAN be resolved deterministically from the filing harness's own context — via the existing `scripts/bridge_author_metadata.load_author_metadata()` / `render_author_metadata_lines()` machinery — are not pre-filled. WI-3495 (origin=improvement, P3) is to auto-inject the six-line metadata block during the scaffold step, deterministically populating the resolvable fields and emitting a clearly-marked placeholder stub for any field that cannot be resolved read-only, so the author hand-fills only the genuinely per-session unknowns instead of all six lines.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` already establishes that bridge artifacts must carry accurate author/model provenance metadata, and `scripts/bridge_author_metadata.py` already defines the canonical six required fields (`REQUIRED_AUTHOR_METADATA_FIELDS`) and the deterministic resolver/renderer. This change makes the `gt bridge propose` scaffold emit that established block at authoring time; it introduces no new public surface, no new field, and no new or revised specification. The behavior is additive convenience aligned with the existing provenance contract.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, `groundtruth-kb/tests/test_cli_bridge_propose.py`.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - governing authority for bridge/document author-provenance metadata; this change makes the `gt bridge propose` scaffold emit the six provenance fields at authoring time, advancing the provenance contract to the draft surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge artifacts are the authoritative audit trail; the six-line author/model block is part of that audit record, so the scaffold that seeds bridge proposals should emit it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the durable bridge-proposal artifact complete-by-construction (provenance present from creation) rather than relying on per-author manual addition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-1830` - operational procedures must be code, not conversation; auto-injecting the deterministic provenance lines moves repetitive author boilerplate from per-session manual typing into the scaffold service.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform package (`groundtruth-kb/src/...`) and its tests; no adopter/application surface is touched and no placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3495 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the deterministic resolver already shares harness/env resolution conventions across harnesses; the scaffold injection reuses that resolver so the emitted provenance is harness-agnostic.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - provenance becomes an artifact-backed property of the draft rather than an inferred-after-the-fact addition.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the proposal-creation lifecycle step with emission of the required provenance fields.

## Prior Deliberations

- `DELIB-20263246` - WI-4522 Implementation Verification Verdict - established the current `load_author_metadata` behavior (durable identity resolved per call; per-session runtime fields from env only; fail-closed on missing envelope). The scaffold injection reuses exactly that loader, so it inherits the same fail-closed / no-shared-baseline semantics.
- `DELIB-20263483` - WI-4522 Author Identity Env Alias Defect - directly informs the field-resolution surface this change consumes; confirms the env-alias precedence the scaffold will rely on for resolvable fields.
- _No further prior deliberations: WI-3495 is a narrow scaffold-output improvement with no additional DA precedent beyond the WI-4522 author-metadata thread cited above; the other LIKE-seeded candidates (backlog-CLI PAUTH, audit-path isolation, generic backlog progress) are not on-topic and were pruned._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the active project authorization covering this non-fast-lane PROJECT-GTKB-RELIABILITY-FIXES batch; WI-3495 is an included member, so implementation is authorized through active project membership under this PAUTH.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3495 is in scope for that authorization.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, add an `${author_metadata_block}` substitution token to `_BASE_TEMPLATE` immediately after the `Date: ${date}` line and before the `Project Authorization:` line, so the rendered draft mirrors the canonical bridge-artifact header order (status token -> title -> bridge_kind/Document/Version/Date -> author metadata block -> project linkage).
2. Add a deterministic helper (e.g. `_author_metadata_block(project_root)`) that lazily imports `render_author_metadata_lines` + `load_author_metadata` + `BridgeAuthorMetadataError` from `scripts.bridge_author_metadata` (mirroring the existing function-scope `from scripts._kb_attribution import resolve_changed_by` pattern in `cli_backlog_add.py` and the `scripts/bridge_author_metadata.py` probe in `bridge/prior_deliberations.py`). It returns the rendered six-line block when the filing harness identity + runtime envelope resolve, and degrades to the canonical placeholder stub (the same six field names with `TODO:`/`<fill ...>` values) when resolution fails — so the read-only deterministic draft NEVER hard-fails on environment, consistent with the CLI's existing degrade-to-placeholder behavior for spec links, prior delibs, and owner decisions.
3. Wire the helper output into `build_propose_context` (compute `context["author_metadata_block"]` from `config.project_root`) so all six proposal kinds inherit the block (it lives in `_BASE_TEMPLATE`, not in `TEMPLATE_CONTEXT_BY_KIND`).
4. Add regression tests in `groundtruth-kb/tests/test_cli_bridge_propose.py` (see verification plan).

This is the minimal additive path. It does NOT change `scripts/bridge_author_metadata.py`, the bridge-author-metadata write-time gate, or the filing helpers; it only enriches the draft scaffold output. The legacy `scripts/gtkb_propose_scaffold.py` helper (a separate composer surface) is out of scope for this WI, which is scoped to the `gt bridge propose` CLI scaffold step.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (all six provenance fields present) | `test_scaffold_emits_six_author_metadata_field_labels` | A rendered implementation draft contains all six `author_*:` field labels (`author_identity`, `author_harness_id`, `author_session_context_id`, `author_model`, `author_model_version`, `author_model_configuration`). |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (canonical header order) | `test_scaffold_author_block_after_date_before_project_auth` | In the rendered draft the author metadata block appears after the `Date:` line and before the `Project Authorization:` line. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (resolvable fields auto-populated) | `test_scaffold_author_block_populates_resolvable_fields_from_env` | With author/model env vars set (e.g. `GTKB_AUTHOR_IDENTITY`, `GTKB_AUTHOR_MODEL`, ...), the rendered draft carries those resolved values, not placeholders. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (degrade, never hard-fail) | `test_scaffold_author_block_degrades_to_placeholder_when_unresolvable` | With no resolvable identity/runtime envelope, the CLI still exits 0 and the draft emits the six field labels with a placeholder/TODO value (no exception, no missing block). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no optional-dep regression) | `test_cli_bridge_propose_no_optional_deps` (existing, extended) | The CLI source imports no `jinja2`/`chromadb`; `--dry-run` still exits 0 with the author block present. |

Execution commands:
- `python -m pytest groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py`

## Acceptance Criteria

1. A draft rendered by `gt bridge propose --kind implementation ...` contains the six-line author/model metadata block positioned after `Date:` and before `Project Authorization:`, for all proposal kinds.
2. Fields resolvable from the filing harness's durable identity + env runtime envelope are populated with real values; unresolvable fields emit a clearly-marked placeholder, and the CLI exits 0 in both cases (no hard-fail on environment).
3. The new derived tests pass, the existing `test_cli_bridge_propose.py` suite still passes, and `ruff check` + `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: importing `scripts.bridge_author_metadata` from inside the package could fail when CWD is not repo root. Mitigation: resolve the module via the established parent-walk probe (`bridge/prior_deliberations._discover_project_root` pattern) / function-scope import with a broad except that degrades to the placeholder stub; the draft is never blocked by a resolution failure.
- Risk: the auto-resolved `author_identity`/`author_harness_id` could be wrong if the registry is ambiguous. Mitigation: `load_author_metadata` already fails closed (returns nothing rather than a wrong value) when the active Prime Builder is ambiguous; in that case the field degrades to a placeholder for the author to fill — never a guessed value.
- Risk: over-coupling the draft CLI to write-time metadata gate behavior. Mitigation: the scaffold only renders text; it does not invoke or duplicate the write-time gate, and the gate remains the authoritative check at filing.
- Rollback: revert the `_BASE_TEMPLATE` token, the `_author_metadata_block` helper, and the `build_propose_context` wiring plus the added tests; the change is a single template token + one helper + context line, fully reversible with no migration and no schema/state impact.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/tests/test_cli_bridge_propose.py`

## Recommended Commit Type

`feat`
