NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c58a8564-bed2-41d4-851b-075b84e86797
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Document: gtkb-wi5661-skill-rename-live-breaks
Version: 001
bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661
target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "scripts/per_thread_finalization_repair.py", "scripts/harness_parity_phase2.py", "scripts/verify_antigravity_dispatch.py"]

# WI-5661 — Fix 5 WI-5651 skill-rename live breaks (Tier-0 fast-lane slice)

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

1. Origin defect (WI-5661 origin=defect). Yes.
2. No new behavior beyond removing the defect — each change only corrects a stale path constant to the renamed skill directory. Yes.
3. No new or revised requirement. Yes.
4. Single-concern with trivial edits (net under 20 lines). The file count (6) exceeds the ~3-file guide because the identical WI-5651 skill-rename defect recurs across 6 live surfaces, not because the change spans multiple concerns. The owner directed these breaks be fixed together as one Tier-0 slice (AUQ 2026-07-24). Flagged explicitly for Loyal Opposition judgment; if LO prefers, the 6 can be split into two 3-file slices without changing the fix.

Covered by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING through WI-5661's active PROJECT-GTKB-RELIABILITY-FIXES membership (PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-5661).

## Problem (5 live breaks, verified 2026-07-24)

WI-5651 renamed .claude/skills/ directories (bridge to gtkb-bridge, verify to gtkb-verify, bridge-propose to gtkb-bridge-propose) but left stale path constants in live load-bearing code. Verified via workflow w0yjqag3h and direct read of current file state:

1. `scripts/gtkb_bridge_writer.py:630` — `helper = project_root / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"`; lines 631-632 `if not helper.is_file(): raise BridgePublicationError("canonical VERIFIED finalizer is unavailable")`. The bare `verify` dir does not exist, so the provider VERIFIED commit-finalization path fails closed on every provider verdict (Ollama/D, OpenRouter/F, Alibaba/H).
2. `.claude/hooks/bridge-axis-2-surface.py:119` — `helper_path = PROJECT_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "scan_bridge.py"`; `spec.loader.exec_module` raises FileNotFoundError, so `_load_scan_bridge_helper()` raises RuntimeError and axis-2 Claude-native bridge surfacing silently fails every prompt.
3. `config/hooks/gtkb-bridge-axis-2-surface.py:119` — the tracked source-of-record mirror of finding 2 (the .claude/hooks copy is activated from it); must be fixed together or a re-activation re-introduces the break.
4. `scripts/per_thread_finalization_repair.py:24` — `VERIFY_HELPERS = PROJECT_ROOT / ".claude" / "skills" / "verify" / "helpers"` is inserted into sys.path so `from write_verdict import ...` (line 30) resolves; write_verdict.py exists only under gtkb-verify, so the import fails and the module is broken on import.
5. `scripts/harness_parity_phase2.py:448-454` — the `surfaces` dict lists bare `.claude/skills/bridge|verify/helpers` (and bare `.codex`/`.agent`/`.api-harness` skill dirs); `_exists()` returns False for the renamed dirs, producing false `needs_adapter` parity reports for harnesses that do support the path.
6. `scripts/verify_antigravity_dispatch.py:42-43` — `VERDICT_ANCHOR_HELPER_PATHS` lists bare `.codex`/`.claude` `skills/verify/write_verdict.py`; the real helper is now under gtkb-verify, weakening verdict-evidence-anchor validation.

## Proposed Change

For each finding, replace the bare skill-directory segment with the gtkb- prefixed name. For the live import/exec sites (finding 1 finalizer, findings 2/3 axis-2 hook, finding 4 per-thread import), adopt the canonical fallback-tuple resolver pattern from `.claude/skills/gtkb-bridge/helpers/impl_report_bridge.py:31-41` (prefer gtkb- name, fall back to legacy) so a future re-rename cannot re-break them. For the string-list/dict constants (findings 5 and 6), update to the gtkb- paths. No behavior change beyond correct path resolution.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — the fast-lane governance path this slice uses.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge finalization and surface authority; the breaks degrade it (provider finalization + axis-2 surfacing).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation-proposal specification linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization (standing PAUTH coverage).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the config/hooks tracked-mirror model and cross-harness hook parity.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification (TEST-11695).

## Requirement Sufficiency

Existing requirements sufficient. This is a path-resolution repair to match the completed WI-5651 rename; no new or revised requirement is needed.

## Owner Decisions / Input

- Owner AUQ 2026-07-24 (session `c58a8564-bed2-41d4-851b-075b84e86797`): after the verification workflow revealed the WI-5651 reference sweep is a ~48-finding, 6-tier project including 5 live breaks, the owner selected "Live breaks first, then project" — authorizing this Tier-0 fast-lane slice — and "Rename scaffold to gtkb-*" (a later slice of the follow-on project, out of scope for this slice).

## Prior Deliberations

- `DELIB-202667106` (Canonical Skill Renaming Rollout, gtkb- prefix — NO-GO) and `DELIB-202667105` (Rollout v003 — GO) — the authoritative rename these references lag behind; `harness-capability-registry.toml` is already gtkb-*, confirming the rename is canonical and only the references lag.
- `DELIB-202667093` (GFR Slice D — drift and generator hygiene — VERIFIED).
- `WI-5651` — the incomplete reference sweep; this is a distinct live-break slice (WI-5651 covers the `_load_bridge_writer` probe).
- `WI-5660` — the sibling fast-lane fix for `.claude` revise_bridge.py; its Cross-Harness Disposition deferred adapter/template parity to this follow-on program.
- Workflow `w0yjqag3h` (2026-07-24) — the exhaustive verification plus completeness critic that surfaced these 5 live breaks beyond the original enumerated scope.

## Cross-Harness Disposition

target_paths include `.claude/hooks/bridge-axis-2-surface.py`, a harness-behavioral surface. Per-harness disposition:

| Surface | Disposition |
| --- | --- |
| Claude (`.claude/hooks/bridge-axis-2-surface.py` + tracked mirror `config/hooks/gtkb-bridge-axis-2-surface.py`) | FIXED in this proposal, both together (mirror is the source-of-record; fixing only one would re-break on re-activation). |
| Codex / Antigravity / Goose / other harnesses | The AXIS-2 *bridge surface* being repaired is Claude-native (per bridge-essential.md two-axis model; the Codex AXIS-2 mechanism is the separate inventoried Codex app-thread automation, not this hook). No `.codex`/`.agent`/`.goose` equivalent of `bridge-axis-2-surface.py` exists to fix. The other five target files are harness-agnostic platform code under `scripts/`, not per-harness surfaces. No cross-harness parity gap is introduced. |

## Verification Plan (Spec-to-Test Mapping)

TEST-11695 (PHASE-002), plus code-quality gates:

| Concern | Test / command | Expected |
| --- | --- | --- |
| Finalizer path resolves | assert `gtkb_bridge_writer` provider finalizer `helper.is_file()` is True after fix | PASS |
| Axis-2 hook loads | assert `bridge-axis-2-surface._load_scan_bridge_helper()` loads scan_bridge without FileNotFoundError (both .claude and config mirror) | PASS |
| Per-thread repair imports | assert `per_thread_finalization_repair` imports write_verdict successfully | PASS |
| Parity surfaces resolve | assert `harness_parity_phase2` surfaces dict entries resolve to existing gtkb- dirs | PASS |
| Antigravity anchors | assert `verify_antigravity_dispatch` anchor paths use gtkb-verify | PASS |
| Code quality | `ruff check` and `ruff format --check` on the 6 changed files | pass |

## Risk And Rollback

Risk: low. Trivial path corrections restoring intended behavior; each finding verified against current file state. Rollback: revert the 6 files (no data/state change). The risk of NOT fixing is ongoing and active: provider VERIFIED finalization and axis-2 bridge surfacing remain broken until this lands.

## Recommended Commit Type

`fix:` — repairs broken path resolution in live code; no new capability surface.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
