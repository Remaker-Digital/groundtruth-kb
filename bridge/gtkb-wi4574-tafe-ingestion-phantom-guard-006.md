NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c50a9788-517e-4adc-a32d-a14594942b91
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code autonomous Prime Builder session; WI-4574 impl report under GO -005
author_metadata_source: env runtime envelope (WI-4522)

# WI-4574 — Implementation Report: TAFE ingestion phantom-guard + reconcile the isolated `sp1` orphan

bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4574
Responds to: bridge/gtkb-wi4574-tafe-ingestion-phantom-guard-005.md (GO)
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py", "groundtruth-kb/tests/test_tafe_bridge_ingestion.py", "config/governance/tafe-acknowledged-archived-bridges.toml"]

## Summary

Implemented WI-4574 per GO `bridge/gtkb-wi4574-tafe-ingestion-phantom-guard-005.md` (impl-start packet
`sha256:d3e9bbb7888115e6f787577829b214c2e7a28db698df62d22bcaef2139c0dcb5`). The two scoped defect fixes
are in place and verified: (1) the ingestion phantom-guard prevents future mismatched-`subject_id`
orphans; (2) the reversible `sp1` acknowledged-archived config entry reconciles the existing isolated
orphan so `gt flow regen-verify` no longer gates on it. No database `--apply` re-ingest was run (per the
GO residual note; that step belongs to WI-4510 Phase-0).

## Implementation Provenance (honest attribution)

The source/test/config edits were first staged in the working tree by a now-disabled, auto-dispatched
Prime worker (session `2026-06-15T04-35-16Z-prime-builder-B-34e432`) before the owner turned the bridge
dispatcher off (`harness-state/bridge-substrate.json` → `substrate: none`); that worker lapsed without
filing a report. Under this GO (`-005`) + the impl-start packet, this session
(`c50a9788-517e-4adc-a32d-a14594942b91`) reviewed, adopted, and independently verified those edits; no
further source changes were required. Per the GO's residual note, only the three GO-authorized
`target_paths` files are in scope; unrelated in-flight harness/user changes are preserved and not staged.

## Changes Implemented

1. **`groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py`** (+31): added `_file_slug_from_path()`
   (derives `<slug>` from a `bridge/<slug>-NNN.md` path; returns `None` on an unparseable path) and the
   `_plan_thread` phantom-guard — after `slug = block.name`, derive the file-slug from the latest
   version-line `path`; when it is determinable AND differs from `slug`, return `None` (skip the block;
   no mismatched-`subject_id` flow_instance/artifact is created). Fail-open on unparseable paths so a
   legitimate thread is never dropped.
2. **`config/governance/tafe-acknowledged-archived-bridges.toml`** (+4): appended a reversible
   `[[acknowledged]]` entry `slug = "sp1-dispatch-reliability-prime-handoff"` with a reason documenting
   it as a phantom duplicate (same `artifact_ref` as `gtkb-sp1-…`, zero content loss) and citing
   `DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615`.
3. **`groundtruth-kb/tests/test_tafe_bridge_ingestion.py`** (+114/-1): added guard coverage —
   mismatch-skipped, matching-slug-ingested, and unparseable-path-fail-open.

## Specification Links (carried forward from -004)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — honored: no change writes `bridge/INDEX.md`; the guard is
  read-derive-only, the config edit is governance config, and regen-verify is read-only.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the guard enforces the D2 identity contract (`subject_id`
  consistent with the thread's bridge files).
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — the rule-3 acknowledged-archived mechanism the
  `sp1` reconciliation uses (shared `_candidate_is_archived` oracle).
- `GOV-RELIABILITY-FAST-LANE-001` — the source/test fast-lane authorization basis.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` — the WI-4510 cutover this precursor unblocks.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
  — cross-cutting; the spec-to-test mapping + executed evidence below comply.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory trio).
- `GOV-STANDING-BACKLOG-001` — WI-4574 is the governed work item.

## Spec-to-Test Mapping

| Spec clause | Test / evidence |
|---|---|
| `ADR-TAFE-SLICE-C-INGESTION-001` D2 (subject_id↔file consistency) | `test_tafe_bridge_ingestion.py`: mismatch-skipped (no orphan), matching-slug-ingested, unparseable-path-fail-open |
| `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` rule 3 (sp1 acknowledged) | read-only `gt flow regen-verify --json` → `sp1` in `extra_archived_in_generated`, NOT in `extra_divergent_in_generated` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no INDEX write) | guard/regen-verify are read-only of INDEX; no `bridge/INDEX.md` mutation |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the executed commands + results below |

## Verification Evidence (executed this session)

```text
python -m pytest groundtruth-kb/tests/test_tafe_bridge_ingestion.py -q
  -> 24 passed

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py groundtruth-kb/tests/test_tafe_bridge_ingestion.py
  -> All checks passed!

python -m ruff format --check (same two files)
  -> 2 files already formatted

gt flow regen-verify --json    (READ-ONLY; no --apply-refresh)
  -> sp1-dispatch-reliability-prime-handoff in extra_archived_in_generated: True
  -> sp1-dispatch-reliability-prime-handoff in extra_divergent_in_generated: False
  -> extra_divergent_in_generated: [] (empty)
  -> missing_in_generated: ["gtkb-wi4574-tafe-ingestion-phantom-guard"]   (shadow staleness only)
```

The read-only regen-verify confirms the WI-4574 deliverable: the `sp1` orphan is reclassified from
gating (`extra_divergent`) to tolerated (`extra_archived`). The overall `ok` remains `False` solely
because `gtkb-wi4574-tafe-ingestion-phantom-guard` is `missing_in_generated` — the WI-4574 thread itself
is not yet in the shadow. That is pure shadow-staleness reconciled by WI-4510's Phase-0
`gt flow ingest-bridge-index --apply` (which this WI-4574 fix deliberately does NOT run, per GO `-005`).
No `gt flow ingest-bridge-index --apply` was executed for WI-4574.

## Owner Decisions / Input

`DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615` — owner directive ("continue with WI-4574")
authorizing the fast-lane ingestion-guard (source/test) and the owner-curated reversible `sp1`
acknowledged-archived config entry. No new owner decision arose during implementation.

## Risk / Rollback

Additive guard + reversible config entry; no schema change, no INDEX mutation, no DB `--apply`. Rollback
= revert `tafe_bridge_ingestion.py` + the test to HEAD and remove the `sp1` config entry; the append-only
shadow is untouched by this fix.

## Recommended Commit Type

Recommended commit type: `fix:` — repairs the ingestion orphan-creation defect and reconciles the
resulting isolated `sp1` shadow residue; no new capability surface.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/tafe_bridge_ingestion.py`
- `groundtruth-kb/tests/test_tafe_bridge_ingestion.py`
- `config/governance/tafe-acknowledged-archived-bridges.toml`
