NEW

# WI-4507: TAFE Bridge-INDEX Compatibility-View Generator (non-authoritative preview)

bridge_kind: prime_proposal
Document: gtkb-tafe-bridge-index-preview
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 869ade5b-58a4-4261-b2cb-98fcbecb8c0e
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4507

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_preview.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_preview.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Summary

Implement WI-4507, the **non-authoritative** compatibility-view generator that renders TAFE flow/stage state in the visual shape of `bridge/INDEX.md`. The output is a *preview artifact* operators can inspect to see how TAFE-tracked workflows would look if rendered through the bridge view — it is **not** a substitute for `bridge/INDEX.md`, it is **not** consumed by any agent's bridge scan, and it does **not** participate in the workflow-state authority chain.

Three pieces, single slice:

1. **Pure renderer** — `groundtruth-kb/src/groundtruth_kb/tafe_index_preview.py` with a frozen value object (`BridgeIndexPreview` carrying the rendered text, the source flow/stage counts, the generation timestamp, and a fixed `authoritative=False` flag) and a pure function `render_tafe_bridge_index_preview(flow_instances, stage_instances, *, now)` that produces a markdown string in the bridge-INDEX visual shape (one `Document: <slug>` block per flow instance with status lines per stage). The first line of the rendered output is the canonical non-authoritative header: `<!-- NON-AUTHORITATIVE: generated from TAFE state; bridge/INDEX.md remains canonical per GOV-FILE-BRIDGE-AUTHORITY-001 -->`. The module exposes no write surface; the renderer returns text.
2. **Read-only CLI** — a new `gt flow preview-bridge-index` command (under the existing `flow` group) that resolves the service, calls the renderer, and writes the output to a non-canonical preview path under `.gtkb-state/tafe-preview/bridge-index-preview.md` (which is gitignored runtime state per `.gitignore`'s `.gtkb-state/` rule). `--out PATH` allows overriding the destination; `--stdout` prints to stdout instead. The CLI **refuses** to write to `bridge/INDEX.md` (the refusal is a structural guard, not a runtime suggestion).
3. **Tests** — a new `groundtruth-kb/tests/test_tafe_index_preview.py` that asserts the rendered shape, the non-authoritative header is the first line, the renderer is pure (no `bridge/INDEX.md` reference, no MemBase write), the CLI writes to the non-canonical preview path, the CLI refuses an `--out bridge/INDEX.md` target, and an AST structural guard asserts the module source contains no write surface to canonical paths.

### Bounding (explicit out-of-scope)

This slice ships a **preview generator** only. It MUST NOT:

- Write to `bridge/INDEX.md`, change `bridge/INDEX.md` authority, register a generator as authoritative, or stand up a dual-write path. The PAUTH forbids `authoritative_generated_view`, `dual_write`, and `cutover`; the slice respects all three. `GOV-FILE-BRIDGE-AUTHORITY-001` keeps the live `bridge/INDEX.md` canonical.
- Stand up a live dispatch substrate, mutate flow/stage/lease/telemetry state, change MemBase schema, or consume the WI-4505 stuck detector / WI-4499 dispatch tick. Reads only.
- Add **alert rules**, dashboard panels, or a metric collector. Visualization belongs to WI-4506 (which is a separate authorized slice; the verdict on its implementation report is awaited).
- Begin **dual-write** (WI-4508), **cutover evidence gathering** (WI-4509), or the **governed cutover** itself (WI-4510). Those are explicitly excluded from the active PAUTH and require a separate owner decision.
- Add a scheduled task, hook, or poller; the renderer is invoked on operator demand via the CLI.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — TAFE state should be **renderable** in the existing bridge view shape for operator inspection, while the umbrella also preserves `bridge/INDEX.md` as canonical until a separate governed cutover. This slice is the renderable-but-non-authoritative half.
- `SPEC-TAFE-R7` — MemBase remains canonical; the preview reads via the existing Python API and writes only to a non-canonical runtime path.
- `SPEC-TAFE-R2`, `SPEC-TAFE-R4` — the renderer surfaces the stage-claim and required-role context already specified for stage instances; no policy logic is added.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the live `bridge/INDEX.md` remains the canonical workflow state; the preview file is non-authoritative and never read by any agent's bridge scan.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project-authorization metadata is in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the renderer purity, the non-authoritative header invariant, the bridge/INDEX.md-write refusal, and the structural no-write-surface guard to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-4507 is the backlog authority for this slice; WI-4508/4509/4510 (cutover-class) remain explicitly excluded.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the active tranche-3 PAUTH (which explicitly includes WI-4507) plus the forthcoming Loyal Opposition GO and implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all source and test targets are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the renderer is a durable governed source artifact; WI-4507 stays unresolved until terminal VERIFIED.

## Prior Deliberations

<!-- Reviewed and pruned by author. -->

- `DELIB-20263164` — owner decision backing the tranche-3 PAUTH that explicitly includes WI-4507 with the bound `(NON-AUTHORITATIVE output only)`.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — owner approval promoting the TAFE R-specs to `specified`; the renderer surfaces state defined by those specs.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — owner choice of the TAFE overhaul direction that produced the umbrella spec and the phased cutover plan.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` — GO constrained to advisory/planning; conditions carried forward (no cutover; `bridge/INDEX.md` canonical; live pilot needs a separate owner decision). This slice respects all three by being preview-only.
- `bridge/gtkb-tafe-flow-definition-seed-records-004.md` — VERIFIED seed records for the five flow families this renderer reads.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` — VERIFIED `flow_instances` + `stage_instances` substrate the renderer reads.
- `bridge/gtkb-tafe-dashboard-observability-003.md` — sibling tranche-3 WI-4506 implementation report (awaiting LO VERIFIED). The renderer is **disjoint** from the dashboard surface (markdown preview vs. Grafana panels); the two slices share no target paths.
- No prior deliberations found for TAFE compatibility-view INDEX rendering: `search_deliberations("TAFE compatibility view generator INDEX.md preview non-authoritative WI-4507")` returned no matches on 2026-06-13. This is the first non-authoritative renderer slice, not a revisit of a rejected approach.

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-20263164`** — the owner decision backing the active PAUTH whose `scope_summary` explicitly authorizes "WI-4507 compatibility-view generator (NON-AUTHORITATIVE output only)" under "GT-KB platform code/tests only under `E:/GT-KB`; `bridge/INDEX.md` remains canonical; no cutover, no dual-write, no live dispatch substrate." The slice respects every clause.
- **S438 AskUserQuestion (drive directive)** — the standing owner directive (re-issued each turn this session) is to drive `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` to completion autonomously through the multi-harness swarm. WI-4507 is the next remaining tranche-3-authorized item now that WI-4504/4505/4511 are resolved and WI-4506 is awaiting LO verification; the AUQ-recorded autonomous drive carries forward.
- The slice stays strictly within `source`/`test` mutation classes and respects every `forbidden_operations` clause (`cutover`, `dual_write`, `live_dispatch_substrate`, `authoritative_generated_view`, `kb_schema_change`). No expanded owner authorization is requested.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` calls for parallel-run renderability bounded by `GOV-FILE-BRIDGE-AUTHORITY-001`'s canonical-INDEX guarantee. `SPEC-TAFE-R7` keeps MemBase canonical and constrains derived views. The tranche-3 PAUTH (owner decision `DELIB-20263164`) explicitly enumerates WI-4507 with the `(NON-AUTHORITATIVE output only)` clarification. No new or revised requirement is needed because this slice implements the specified non-authoritative renderable surface, bounds it structurally, and explicitly excludes any authority change.

## Implementation Plan

### Pure renderer module

In `groundtruth-kb/src/groundtruth_kb/tafe_index_preview.py` (new file):

1. **Frozen value object** `BridgeIndexPreview` (dataclass with `frozen=True`): `text: str`, `flow_instance_count: int`, `stage_instance_count: int`, `generated_at: str` (UTC ISO), and a fixed `authoritative: bool = False` constant.
2. **Pure function** `render_tafe_bridge_index_preview(flow_instances, stage_instances, *, now) -> BridgeIndexPreview`:
   - Joins each flow instance to its stage instances via `flow_instance_id`.
   - Renders one section per active flow instance: `Document: <subject_id>` followed by status lines `<status>: <stage_id> (role=<required_role>, claim=<claim_status>)` ordered by descending `stage_index`.
   - The **first line** of `BridgeIndexPreview.text` is the literal non-authoritative header `<!-- NON-AUTHORITATIVE: generated from TAFE state; bridge/INDEX.md remains canonical per GOV-FILE-BRIDGE-AUTHORITY-001 -->`.
   - The function is pure: no file I/O, no subprocess, no MemBase mutation, no `bridge/INDEX.md` reference.
3. The module exposes `__all__` with `BridgeIndexPreview` + `render_tafe_bridge_index_preview` + the canonical header string. No writer function on this module.

### Read-only CLI

In `groundtruth-kb/src/groundtruth_kb/cli.py`:

4. Add `gt flow preview-bridge-index [--out PATH] [--stdout]` under the existing `flow` group. Default output: `.gtkb-state/tafe-preview/bridge-index-preview.md` (the parent directory is created if absent; `.gtkb-state/` is gitignored runtime state). The command:
   - Resolves the service via the existing `_flow_service` helper.
   - Reads active flow + stage instances via the existing `list_flow_instances` / `list_stage_instances` methods.
   - Calls the pure renderer.
   - Writes the rendered text to the resolved output path **after** asserting the resolved path does not equal `bridge/INDEX.md` (any case, any path-normalization form). On `--out bridge/INDEX.md` the command refuses with a clear error and exits non-zero.
   - With `--stdout`, prints the rendered text to stdout instead of writing a file.
5. The CLI command's source contains no canonical-INDEX write; it adds no scheduled task / hook / poller and no dispatch behavior.

### Tests

In `groundtruth-kb/tests/test_tafe_index_preview.py` (new file):

6. Renderer purity / shape tests:
   - The first line of the rendered text is the canonical non-authoritative header (exact string match).
   - One section per active flow instance is rendered, with stage lines in descending `stage_index` order.
   - The renderer never raises on empty inputs (no flows / no stages) and returns the non-authoritative header followed by an empty body.
   - `BridgeIndexPreview.authoritative is False` (fixed value).
7. CLI tests (Click `CliRunner`):
   - Default invocation writes to `.gtkb-state/tafe-preview/bridge-index-preview.md` and the file content equals the renderer's output.
   - `--stdout` prints the rendered text and writes no file.
   - `--out bridge/INDEX.md` returns non-zero exit and writes nothing (refusal guard, the bridge canonical authority).
   - `--out` to a non-canonical custom path works.
8. Structural guard (AST):
   - The renderer module source contains no `Bridge/INDEX.md` write, no `subprocess`, no MemBase mutating method calls, and no canonical-path string equal to `bridge/INDEX.md`.
   - The CLI command function source contains a refusal branch that compares the resolved output path against the canonical `bridge/INDEX.md` token (so a future refactor can't silently delete the guard).

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb/tests/test_tafe_index_preview.py -q --tb=short
Expected: pass; exercises renderer purity + non-authoritative header invariant + empty-input shape + CLI default/stdout/refusal/custom-out paths + AST structural guard.

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_index_preview.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_index_preview.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_index_preview.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_index_preview.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/tafe_index_preview.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_index_preview.py
Expected: no output, exit 0.

# Live bridge/INDEX.md is unchanged after running the preview (smoke check):
git status --short bridge/INDEX.md
Expected: empty output (no change).
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — tests prove TAFE state is renderable in the bridge-INDEX visual shape while the live bridge surface is unchanged.
- `SPEC-TAFE-R7` — structural guard asserts MemBase remains canonical; no canonical mutation surface in the renderer.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the refusal-to-write-bridge/INDEX.md test + the smoke check after `--out` runs prove the live bridge surface remains canonical and untouched.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each linked spec maps to executed evidence.

## Risk / Rollback

Primary risk is scope creep into authoritative-view territory or into dual-write. Mitigation: the slice ships a **preview-only** module + read-only CLI; the renderer's first output line is a non-authoritative header (asserted by test); the CLI refuses `--out bridge/INDEX.md`; structural AST guard asserts no canonical-write surface; the renderer module is pure (no file I/O).

Secondary risk is operator confusion (an operator mistakes the preview file for the canonical INDEX). Mitigation: the preview lives under `.gtkb-state/tafe-preview/` (gitignored runtime state, not under `bridge/`) and carries a load-bearing non-authoritative header. Documentation can carry the same load-bearing header in a follow-on slice; this slice ships the structural guarantee.

Tertiary risk is starting the dual-write/cutover sequence prematurely. Mitigation: WI-4508/4509/4510 are explicitly **excluded** from the active PAUTH (and are listed as `CUTOVER-EXCLUDED` in the PAUTH's id and `scope_summary`); a separate owner decision is required to begin any cutover-class work.

Rollback is a single-commit revert of the new module + test + the additive `gt flow preview-bridge-index` block in `cli.py` (no removal of existing commands). No KB mutation, no schema change, no integration to unwind. Any preview file at `.gtkb-state/tafe-preview/` is gitignored runtime state and may be left in place.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a new `gtkb-tafe-bridge-index-preview` document list in `bridge/INDEX.md` via the serialized `gt bridge index add-document` writer; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

`feat:` — adds a new pure TAFE compatibility-view renderer module plus an additive read-only `gt flow preview-bridge-index` CLI surface with comprehensive tests; no behavior change to existing commands, no canonical bridge authority change, no recovery actuation, and no live dispatch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
