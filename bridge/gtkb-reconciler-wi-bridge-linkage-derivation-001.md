NEW

bridge_kind: prime_proposal
Document: gtkb-reconciler-wi-bridge-linkage-derivation
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder; explanatory output style; autonomous PB loop

Project Authorization: PAUTH-WI4533-RECONCILER-LINKAGE-20260613
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4533

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true

---

# Implementation Proposal — Reconciler WI→Bridge Linkage Derivation (WI-4533)

## Summary

WI-4533 (P2, `backlog-reconciler`, defect): `bridge_verified_backlog_reconciler.py` resolves a VERIFIED work item only when the WI's own `related_bridge_threads` field names the bridge slug. WIs created via `gt backlog add` and then driven to VERIFIED keep `related_bridge_threads = []`, so `classify_work_item` skips them (`no_related_bridge_threads`) and they stay `open` forever despite a VERIFIED bridge. Confirmed S438: WI-4481, WI-4532, WI-4443, WI-4452 were all VERIFIED yet open with empty links (resolved manually this session — a recurring manual tax per the Deterministic Services Principle).

The linkage is one-directional: bridge *files* carry the canonical `Work Item: WI-XXXX` metadata line (file→WI), but nothing populates the reverse WI→bridge link in MemBase. This proposal makes the reconciler **derive** the reverse link: it parses each indexed bridge slug's files for the canonical `Work Item:` metadata line, builds a `work_item_id → [slug]` index, and supplements each WI's `related_bridge_threads` with the derived slugs before classification. A VERIFIED bridge that declares a WI then resolves that WI even when its link field was never populated — and retroactively, for existing unlinked WIs.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — VERIFIED-driven completion/retirement is automatic (no owner confirmation). This fix extends the reconciler's reach so the automation actually fires for bridged-but-unlinked WIs, which is what that governance promises.
- `GOV-STANDING-BACKLOG-001` — the backlog (MemBase `work_items`) is the durable work authority; this fix keeps its resolution state truthful.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, project authorization, and governing specs linked (this section + header).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable `Project Authorization:` / `Project:` / `Work Item:` metadata present.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-4533 active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps each behavior to executed test evidence (Spec-to-Test Mapping below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical workflow state; the derivation reads only the indexed slugs' files and does not mutate INDEX. CLAUSE-INDEX-IS-CANONICAL satisfied by the Bridge Filing section below.

## Prior Deliberations

- `WI-4533` — the gap this implements; captured S438 after the dual-LO idle-queue reconciliation surfaced four VERIFIED-but-open WIs.
- `WI-4384` — adjacent "Project PAUTH auto-completion ignores current bridge verification state" gap; this proposal addresses the WI-resolution linkage layer, distinct from the PAUTH-completion layer.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — the reconciler's governing deliberation (cited in its own `_completion_evidence`); this fix operationalizes its intent for unlinked WIs.
- Owner S438 cleanup (this session): WI-4481/4532/4443/4452 manually resolved + linked; the manual step is what WI-4533 eliminates going forward.

## Owner Decisions / Input

Owner directive (S438, this session): "implement WI-4533" — issued directly after the owner chose "Backlog-accuracy cleanup" via AskUserQuestion, whose option text explicitly included "implement the linkage fix so VERIFIED work auto-resolves going forward." That is the owner-decision evidence authorizing this implementation scope, under the standing autonomous-loop directive `DELIB-20263143` and bounded by `PAUTH-WI4533-RECONCILER-LINKAGE-20260613`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` already mandates automatic VERIFIED-driven resolution; WI-4533 + the S438 evidence fully specify the linkage-derivation gap. No new or revised requirement is needed.

## Implementation Plan

All changes in `scripts/bridge_verified_backlog_reconciler.py` plus tests.

1. **Reverse-index builder.** Add `build_work_item_bridge_index(project_root, bridge_statuses) -> dict[str, list[str]]`. For each slug in `bridge_statuses` (the live INDEX slugs), read its bridge files (`_bridge_thread_files`) and extract the canonical `Work Item:` metadata line(s) via a new module-level regex `_WORK_ITEM_METADATA_RE = re.compile(r"^Work Item:\s*(WI-[A-Za-z0-9-]+)\s*$", re.MULTILINE | re.IGNORECASE)`. Map each declared `WI-XXXX → {slug}`, return `{wi_id: sorted(slugs)}`. Parsing the **metadata line only** (not arbitrary WI-ID mentions) ensures context-cited WIs in prose are not falsely linked.

2. **`classify_work_item` gains an additive `derived_links` parameter** (keyword-only, default `None`). After computing `parsed_links` from the WI's own `related_bridge_threads`, append any `derived_links.get(item["id"], [])` slugs not already present. Everything downstream (recognized/missing/parent_evidence/classification) is unchanged. When `derived_links` is `None`/empty, behavior is byte-identical to today (non-regression).

3. **`reconcile()` builds the index once** (`build_work_item_bridge_index(project_root, bridge_statuses)`) and passes it as `derived_links` to both `classify_work_item` (resolve pass) and `classify_reconciler_resolution` → `classify_work_item` (repair/reopen pass), so the reopen pass uses the same supplemented links and does not reopen a WI that the derivation legitimately resolves.

Safety properties preserved:
- The existing "all recognized links must be VERIFIED" gate (`linked_bridge_not_verified`) still protects multi-thread WIs: a derived VERIFIED slug is additive; if the WI also links a non-VERIFIED thread, it is not resolved.
- `bridge_thread_has_parent_evidence` (the `missing_parent_evidence` gate) is unchanged and automatically satisfied for derived slugs, because the derivation is based on the bridge file carrying the WI's `Work Item:` line (which `_contains_work_item_id` matches).
- No INDEX mutation, no schema change, no change to the `--apply`/`--repair-overbroad` write semantics.

Out of scope (noted in WI-4533): the separate `missing_parent_evidence` cases where a *linked* VERIFIED bridge does not cite the WI at all (e.g., WI-4520, WI-4455) — those bridges genuinely lack the WI's metadata and are a distinct judgment call.

## Spec-Derived Verification Plan

```text
python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short
Expected: pass; new derivation tests green; all existing reconciler tests unchanged and green (non-regression of the derived_links=None path).

python -m ruff check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
python -m ruff format --check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
Expected: pass.
```

## Spec-to-Test Mapping

| Spec / behavior | Derived test | Result |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — VERIFIED-but-unlinked WI auto-resolves | `test_derives_link_from_bridge_work_item_metadata_resolves_unlinked_wi` — WI with `related_bridge_threads=[]` + a VERIFIED bridge whose file declares `Work Item: WI-X` → `action=resolve` | PASS (expected) |
| Precision — prose mention does NOT link | `test_derivation_ignores_prose_work_item_mentions` — a bridge that mentions `WI-Y` only in prose (no `Work Item:` line) does not link/resolve WI-Y | PASS (expected) |
| Multi-thread safety preserved | `test_derived_link_with_unverified_sibling_thread_not_resolved` — WI derived to a VERIFIED slug but also linking a non-VERIFIED thread → `linked_bridge_not_verified` (not resolved) | PASS (expected) |
| Non-regression (derived_links=None) | existing reconciler suite unmodified + a `derived_links=None` classify call equals prior behavior | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed commands above | PASS |

## Risk / Rollback

Risk: the derivation could resolve a WI whose VERIFIED bridge declares it but which the owner considers still open. Mitigation: the `Work Item:` metadata line IS the thread's declared deliverable; a VERIFIED verdict on that thread is dated evidence the WI is done — the same semantic the reconciler already applies to explicitly-linked WIs. The multi-thread gate prevents premature resolution when other declared threads are unverified.

Rollback: single-file revert of `scripts/bridge_verified_backlog_reconciler.py` (one new function + one additive param + one call-site) plus the test additions; no on-disk state, schema, or INDEX change.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` as `bridge/gtkb-reconciler-wi-bridge-linkage-derivation-001.md`, with a `NEW` entry added to `bridge/INDEX.md` via the serialized `gt bridge index add-document` CLI (`scripts/bridge_index_writer.py` holds the lock and performs an atomic temp-then-replace read-modify-merge). This is version 001; no prior version files are deleted or rewritten. `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`; agent-tool Write/Edit of INDEX is additionally blocked by the WI-4481 INDEX-write-guard hook. The reconciler's derivation reads bridge files read-only and never mutates INDEX.

## Recommended Commit Type

`fix:` — closes WI-4533 (VERIFIED-but-unlinked WIs silently staying open); restores automatic VERIFIED-driven resolution. No new feature surface beyond the linkage derivation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
