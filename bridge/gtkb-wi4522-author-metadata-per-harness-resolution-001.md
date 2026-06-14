NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4522-author-metadata-per-harness-resolution
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4522
target_paths: ["scripts/bridge_author_metadata.py", "groundtruth-kb/tests/test_bridge_author_metadata_per_harness_resolution.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4522: Resolve bridge author metadata from harness identity per call (replace shared `current.json` baseline)

## Summary

WI-4522 (P3, `bridge-protocol`, origin=improvement): `ensure_author_metadata` (`scripts/bridge_author_metadata.py:254`) stamps `author_*` fields on every filed bridge version that lacks embedded metadata, sourcing those fields from a single shared `.gtkb-state/bridge-author-metadata/current.json` (line 32, read by `load_author_metadata` at line 237). As shared mutable state, the last harness to write `current.json` wins — so a concurrently-dispatched headless worker can inherit the previous harness's metadata.

S389 evidence (2026-06-13): an interactive Claude (B) session set `current.json` to Claude metadata; a concurrently-dispatched headless Prime worker then filed `gtkb-claim-gated-implementation-start-003.md` stamped Claude/B while its prose header self-IDs as "Codex, harness A" — a GOV-DOCUMENT-AUTHOR-PROVENANCE-001 inconsistency in the durable bridge record.

**Cycle-12 triage (this session) located the precise scope:** `ensure_author_metadata` returns content unchanged when complete author metadata is already in the body (lines 271-275 in `bridge_author_metadata.py`). The wrong-harness-stamp bug fires only for callers that file bridge content WITHOUT body-embedded `author_*` headers — typically scripted/dispatched headless workers that don't author their own header — at which point `load_author_metadata` (line 224) merges `current.json` (line 237) as the lowest-precedence baseline beneath env (line 238) and explicit (line 239). When env vars are unset (the headless case), `current.json` is the winner.

**Owner cycle-12 AskUserQuestion decision: "Per-harness resolution at filing time."** This proposal replaces the `current.json` baseline in `load_author_metadata` with a per-call **harness-identity resolution** — at filing time, derive the metadata from `harness-state/harness-identities.json` + the active harness's role (the same registry used elsewhere in the project for harness attribution) rather than from a shared mutable cache. Env and explicit overrides retain their existing precedence. The shared `current.json` becomes an optional last-resort fallback (or is retired); the canonical baseline becomes the durable identity registry.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4522 is the backlog authority for this fix (P3 bridge-protocol provenance defect). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one source file edit + one test file), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4522; allows `source` + `test_addition`).
- **GOV-DOCUMENT-AUTHOR-PROVENANCE-001** — the provenance invariant the current `current.json` sharing violates under concurrent harnesses; the per-harness fix restores it.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger). It hardens the bridge-authoring metadata path without modifying `bridge/INDEX.md` or any bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a concurrent-harness regression that reproduces S389.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked fix to a provenance read-surface that GOV-DOCUMENT-AUTHOR-PROVENANCE-001 depends on.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4522 + the S389 repro), cycle-12 triage localized the root cause in `load_author_metadata`, the bounded PAUTH authorizes the `source` + `test_addition` work, and GOV-DOCUMENT-AUTHOR-PROVENANCE-001 defines the invariant the fix restores. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4522 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **Cycle-12 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Per-harness resolution at filing time" over "key cache by session/harness id" and "defer", scoping this slice as the root-cause harness-identity resolution path (not the lighter shared-cache keyed variant).
- **`scripts/_kb_attribution.py` — `resolve_changed_by` / priority-3 single-active-prime-builder resolution** — the canonical pattern for per-call harness-identity resolution that this fix mirrors for `author_*` metadata. Sharing the resolver path keeps the two attribution surfaces aligned (KB attribution + bridge author metadata both honor the durable identity registry).
- **`harness-state/harness-identities.json` + `harness-state/harness-registry.json` (canonical role registry)** — the durable identity + role authority this fix reads at file time, replacing the shared mutable `current.json` baseline.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live source instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4522 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-12 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Per-harness resolution at filing time"**, authorizing the root-cause fix (resolve `author_*` from harness identity + role at file time) over the keyed-cache and defer alternatives. The fix stays within `source` + `test_addition` and changes no formal artifact, schema, or KB.

## Design

In `scripts/bridge_author_metadata.py`:

1. **New private helper `_resolve_metadata_from_harness_identity(project_root)` -> `dict[str, str] | None`**: reads `harness-state/harness-identities.json` (the durable identity map: `harness_name -> {id, ...}`) and `harness-state/harness-registry.json` (the canonical role registry projection: harness id -> role set), resolves the single ACTIVE Prime Builder (or the active harness with `status == "active"`), and returns the `author_*` metadata dict for that harness. Mirrors the priority-3 path in `_kb_attribution.resolve_changed_by` — same registry sources, same single-active-PB invariant, same fail-closed semantics when zero or multiple active Prime Builders exist (returns `None` so env/explicit can still drive the metadata; the caller raises if validation fails).
2. **Modify `load_author_metadata` (`:224`):** replace the `current.json` baseline (`:237`) with `_resolve_metadata_from_harness_identity(root)`. Keep env (`:238`) and explicit (`:239`) overrides at their existing precedence. When per-harness resolution returns `None` (registry absent / ambiguous), fall through to env and explicit; if those don't supply the required fields, `validate_author_metadata` raises as today (no silent fallback to a wrong harness).
3. **Retire the shared `current.json` write path** in this scope only as a *baseline-source*. `AUTHOR_METADATA_RELATIVE_PATH` and any `current.json` write code may remain (so an out-of-band override path exists) but `load_author_metadata` no longer reads it as the baseline. Decision: keep the file as a deprecated last-resort fallback for now (after env / explicit / identity-resolution all yield nothing), to avoid breaking any out-of-band tooling that writes it; remove fully in a follow-on slice if no callers remain.

This is a minimal, surgical change at one call site: substituting one baseline source for another with the same `dict[str, str]` shape. No schema change, no KB mutation, no helper API change for callers of `ensure_author_metadata`.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `groundtruth-kb/tests/test_bridge_author_metadata_per_harness_resolution.py`) | Method |
|---|---|---|
| Baseline metadata resolves from harness identity (WI-4522 root) | `test_baseline_resolves_from_identity` | fixture identity + registry → assert `load_author_metadata` returns the correct `author_*` dict without reading `current.json` |
| `current.json` no longer overrides per-call resolution (S389 regression) | `test_stale_current_json_does_not_override_identity` | write `current.json` with WRONG harness metadata + valid identity/registry for harness X → assert `load_author_metadata` returns X's metadata, not `current.json`'s |
| Env vars still override per existing precedence | `test_env_overrides_identity` | identity resolves to harness X + env vars set author_identity to Y → assert env wins |
| Explicit overrides still win | `test_explicit_overrides_env_and_identity` | identity X + env Y + explicit Z → assert explicit Z wins |
| Ambiguous identity (zero or multiple active PBs) does not silently fall back to a wrong harness | `test_ambiguous_identity_does_not_silently_fallback` | identity with zero active PBs → `_resolve_metadata_from_harness_identity` returns None; if env/explicit also unset → `validate_author_metadata` raises (no wrong-harness stamp) |
| `ensure_author_metadata` skip path preserved (already-embedded metadata wins) | `test_embedded_metadata_short_circuit_preserved` | content with complete `author_*` headers → `ensure_author_metadata` returns unchanged (no identity resolution performed) |
| Concurrent-harness regression: write `current.json` to A, file a bridge whose body lacks metadata while the identity resolves to B → assert filed bridge is stamped B (not A) | `test_concurrent_harness_regression_s389` | reproduces the 2026-06-13 S389 incident in a fixture; without the fix the test fails, with the fix it passes |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest groundtruth-kb/tests/test_bridge_author_metadata_per_harness_resolution.py -q --tb=short`; plus the existing bridge-author-metadata regression suites must still pass (env/explicit precedence, validation, render lines).

## Risk / Rollback

- **Risk: low-moderate.** One source-file change at one call site (`load_author_metadata` baseline source), one new private helper that mirrors a well-tested attribution pattern from `_kb_attribution.py`. The fix is per-call (no shared mutable state) so it removes a concurrency hazard rather than introducing one. The `ensure_author_metadata` short-circuit on already-embedded metadata (the case for most interactive seeds) is preserved unchanged.
- **Edge case considered:** when neither identity-resolution NOR env NOR explicit yield metadata, `validate_author_metadata` raises rather than silently using a stale `current.json`. This is the correct provenance-safe behavior: better to fail loudly than to stamp the wrong harness. Callers that currently rely on a baseline `current.json` to fill gaps will see a raise — and that raise is the bug surfacing, not regressing.
- **Rollback:** revert the `load_author_metadata` change + delete `_resolve_metadata_from_harness_identity` + delete the test. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (concurrent-harness wrong-stamp under `current.json` sharing) and restores a GOV-DOCUMENT-AUTHOR-PROVENANCE-001 invariant; no new capability surface, no new public API. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
