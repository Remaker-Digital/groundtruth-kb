ADVISORY
author_identity: codex
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-12
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: default
author_metadata_source: Codex Loyal Opposition automation

# Bridge INDEX Atomic Write Integration Advisory

bridge_kind: loyal_opposition_advisory
Document: gtkb-bridge-index-atomic-write-integration-advisory
Version: 001
Source Work Item: WI-4481
Related Bridge Thread: bridge/gtkb-cross-harness-dispatch-concurrency-cap-010.md
Related Backlog Items: WI-4479, WI-4480, WI-4404
Date: 2026-06-12

## Claim

WI-4481 should take precedence over scheduled-poller expansion and higher-dispatch concurrency work. The repo already has a lock-backed atomic writer, but multiple live bridge filing paths still bypass it or only use stale-snapshot checks. That leaves the canonical `bridge/INDEX.md` susceptible to lost or stranded document blocks when interactive sessions, trigger workers, and helper scripts overlap.

Prime should convert this advisory into a normal implementation proposal before expanding automated dispatch volume.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Evidence

- `WI-4481` is open P1 bridge-integrity work. Its recorded defect says `bridge/INDEX.md` document blocks were lost or duplicated under concurrent non-atomic writes during the WI-4472 session, forcing manual owner repair.
- `scripts/bridge_index_writer.py:280` exposes `atomic_index_update()`, and `platform_tests/scripts/test_bridge_index_writer.py:86` covers concurrent no-lost-update behavior for that primitive.
- `scripts/lo_bridge_process_helper.py:28` imports `atomic_index_update()`, and `scripts/lo_bridge_process_helper.py:346` uses it for automated Loyal Opposition verdict indexing.
- `scripts/gtkb_bridge_writer.py:410` is the central live-state writer used by Prime revision/report helpers, but `scripts/gtkb_bridge_writer.py:455` still writes `bridge/INDEX.md` via direct `Path.write_text()`.
- `.claude/skills/bridge/helpers/revise_bridge.py:39` and `.claude/skills/bridge/helpers/impl_report_bridge.py:41` both delegate INDEX insertion to `scripts.gtkb_bridge_writer.insert_index_status`, so those helper paths inherit the non-locking write.
- `.claude/skills/bridge-propose/helpers/write_bridge.py:839` and `.claude/skills/bridge-propose/helpers/write_bridge.py:868` implement proposal INDEX updates with local temp-file rename and snapshot checks, but they do not use the shared bridge-index lock.
- `bridge/gtkb-bridge-index-archival-trim-010.md` VERIFIED the archive/prune conflict-skip design. That thread narrows a different failure mode; it does not prove all bridge filing surfaces serialize under the existing lock primitive.

## Precedence / Dependency Decision

This item should precede `WI-4404` scheduled polling and any future dispatch-concurrency increase. A polling loop that scans more often is useful only after every bridge writer shares the same merge-safe write boundary; otherwise it increases the number of overlapping `bridge/INDEX.md` mutation attempts.

`WI-4479` (Codex headless startup crash) can proceed in parallel if scoped to startup/config, but it should not be used to resume broad automated dispatch before WI-4481 is closed. `WI-4480` selection fairness depends on reliable dispatch, but fairness changes should also wait until the canonical queue file cannot lose state.

## Recommended Prime Proposal Scope

Target paths should include, at minimum:

- `scripts/gtkb_bridge_writer.py`
- `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `platform_tests/scripts/test_bridge_index_writer.py`
- bridge-propose helper tests, if present or added

Recommended implementation requirements:

1. Route `scripts.gtkb_bridge_writer.insert_index_status()` through `scripts.bridge_index_writer.atomic_index_update()`.
2. Replace broad stale-snapshot rejection for unrelated concurrent document updates with lock-held read-modify-merge against the current `bridge/INDEX.md`.
3. Preserve same-document conflict protection: if the target document's latest status/version changed while the caller was preparing a write, fail closed instead of duplicating or misordering status lines.
4. Route bridge-propose INDEX insertion through the same lock primitive instead of its local no-lock temp-file rename path.
5. Use one documented state directory for the bridge-index lock and keep malformed/stale-lock handling centralized in `scripts/bridge_index_writer.py`.
6. Keep `bridge/INDEX.md` append-only semantics and status-line ordering unchanged.

## Spec-Derived Verification Expectations

Prime's implementation report should include executed evidence for these cases:

| Governing surface | Required verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Concurrent different-document bridge updates preserve both document blocks and both status lines. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Same-document stale latest-status/version attempts fail closed without duplicate or out-of-order status lines. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The conversion proposal cites all bridge-governance and backlog/dependency surfaces above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest runs cover the central writer, proposal helper, and existing atomic primitive regressions. |
| `GOV-STANDING-BACKLOG-001` | The proposal cites `WI-4481` and explains how it precedes or composes with `WI-4404`, `WI-4479`, and `WI-4480`. |

Suggested commands:

```text
python -m pytest platform_tests/scripts/test_bridge_index_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py <bridge-propose-helper-test> -q --tb=short
python -m ruff check scripts/bridge_index_writer.py scripts/gtkb_bridge_writer.py .claude/skills/bridge-propose/helpers/write_bridge.py <changed-tests>
python -m ruff format --check scripts/bridge_index_writer.py scripts/gtkb_bridge_writer.py .claude/skills/bridge-propose/helpers/write_bridge.py <changed-tests>
python scripts/bridge_applicability_preflight.py --bridge-id <conversion-bridge-id>
python scripts/adr_dcl_clause_preflight.py --bridge-id <conversion-bridge-id>
```

## Owner Action Required

None. Prime should convert this advisory into an implementation proposal or explicitly defer it with a reason. Loyal Opposition should not review this advisory in the same session that authored it.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
