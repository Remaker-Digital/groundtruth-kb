NEW

# Implementation Proposal NEW — Implementation-Start Target-Paths Preflight (WI-3380)

**Status:** NEW (implementation proposal; awaiting Codex GO/NO-GO)
**Date:** 2026-06-04
**Author:** Prime Builder (Claude Opus 4.7, harness B)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: bfc70de3-76e6-4db9-a78b-ce2758bb8679
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

bridge_kind: implementation_proposal
Document: gtkb-impl-start-target-paths-preflight
Version: 001
Session: S414
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Work Item: WI-3380
work_item_ids: [WI-3380]
spec_ids: []
target_paths: ["scripts/impl_start_target_paths_preflight.py", "groundtruth-kb/tests/test_impl_start_target_paths_preflight.py", ".claude/hooks/bridge-compliance-gate.py"]

---

## Claim

Add a deterministic, read-only preflight that compares the set of files an implementation session is about to write (or has written) against the `target_paths` glob set declared on the active implementation's GO'd bridge proposal. Surface drift before the bridge-compliance-gate hook fires, so unscoped writes are caught at preflight time rather than as opaque hook blocks (or, worse, after a clobbering commit).

## Why Now

The bridge protocol's `target_paths` field is the canonical scope envelope for any implementation. `scripts/implementation_authorization.py` already parses `target_paths` from approved proposals (lines 480-522 + `extract_target_paths`) and gates the implementation-start packet. But there is no preflight that says, *given this set of pending file writes, here is which ones are out-of-scope against the cited GO* — drift is discovered only at the bridge-compliance-gate Write-time hook, or post-commit when a verification fails.

Recent autonomous-loop activity in this session and prior sessions has surfaced multiple concurrent-author defects (path-restricted commits defeating shared-index races, inventory-drift commit freezes, CWD-shift confusion during multi-step Bash runs). All of these show that scope discipline lives or dies on early visibility. A read-only preflight that reports the drift before commit time would:

- catch unintended cross-thread mutations (e.g., a session working one bridge also editing files belonging to another bridge's GO scope);
- distinguish "deliberate scope expansion" (which should trigger REVISED filing) from accidental drift (which should abort the write);
- give the bridge-compliance-gate hook a richer fail message ("Writes to <path> exceed the GO scope at bridge/<slug>-NNN.md target_paths") instead of an opaque PAUTH-style block.

## Why Not (alternatives considered)

1. **Trust the bridge-compliance-gate alone.** Rejected: the gate is Write-time, single-file, and produces opaque "blocked" messages. It doesn't aggregate over the implementation session's full write set and can't distinguish drift-direction (out-of-scope vs. in-scope-but-unauthorized).
2. **Make `implementation_authorization.py` enforce target_paths at packet-creation time.** Rejected: target_paths are known when the packet is minted, but the *actual* file writes happen later. The packet captures the policy; this proposal adds the runtime check.
3. **Build into the post-impl report instead of as a preflight.** Rejected: too late. Post-impl is after-the-fact; the goal is to prevent unscoped writes from landing.
4. **Single shared module for target_paths logic between authorization, preflight, and bridge-compliance-gate.** Deferred: noted as a future refactor; surgical scope here means the preflight calls `extract_target_paths` from `implementation_authorization.py` and depends on its parsing semantics.

## Prior Deliberations

- DELIB-S386-TARGET-PATHS-PREFLIGHT-CANDIDATE — S386 autonomous /loop captured this as actionable_now during triage workflow wi3hun87t (this session).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — token-tax of after-the-fact NO-GO discovery argues for deterministic preflight at session-start.
- Origin deliberation for the cited work item — drafted as P1 candidate after S386 race witnessing.

_No prior bridge proposal exists for this specific preflight surface; this is the first._

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; `target_paths` is part of the proposal-shape contract.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane governance for reliability defects with bounded scope; this is a bounded preflight script + hook touchpoint.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — implementation must produce durable artifacts; this preflight is itself an artifact (script + test).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the preflight reads the GO'd bridge file LIVE (not a cached extract), aligning with the freshness principle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal carries linked governing specs + maps each to verification evidence (see plan below).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification Plan section below maps each cited spec to a test.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — new script + test + hook integration crosses the artifact-lifecycle triggers (defect-class WI → implementation).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — preflight stays in `scripts/` and `.claude/hooks/`, within GT-KB platform subtree; no `applications/` paths touched.

Advisory / cross-cutting:

- `.claude/rules/file-bridge-protocol.md` § "Mandatory Implementation-Start Authorization Metadata" — the `target_paths` field this preflight reads.
- `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate" — the impl-start gate that this preflight complements.
- `scripts/implementation_authorization.py` lines 63-65, 480-522 — `TARGET_PATHS_RE` and `extract_target_paths` are reused.

## Owner Decisions / Input

- 2026-06-04 UTC, S414: owner AUQ "How should I scope this autonomous run, given the Envelope program is documented as owner-blocked..." → "Triage + draft bridge proposals" — owner authorized drafting NEW proposals for actionable_now P1 items; this thread is one such draft. AUQ evidence captured in earlier-this-session transcript.
- 2026-06-04 UTC, S414: project membership row `PWM-PROJECT-GTKB-RELIABILITY-FIXES` for the cited work item created (version 1, active) via `python -m groundtruth_kb projects add-item PROJECT-GTKB-RELIABILITY-FIXES <wi>` with explicit AUQ-citing `--change-reason`. This brings the work item under standing PAUTH coverage by active project membership (allowed_mutation_classes: `["source","test_addition","hook_upgrade"]`; no expiration).

No formal-artifact-approval packets are required because the proposal touches only source + test + hook files (no MemBase spec mutation, no protected narrative artifact edit).

## Requirement Sufficiency

Existing requirements sufficient. The proposal operationalizes the existing `target_paths` contract from `.claude/rules/file-bridge-protocol.md` and `.claude/rules/codex-review-gate.md`; no new specification is needed.

## Proposed Scope

### New file: `scripts/impl_start_target_paths_preflight.py`

A standalone read-only script with this surface:

```text
python scripts/impl_start_target_paths_preflight.py \
    --bridge-id <bridge-document-name> \
    [--candidate-paths <path1> <path2> ...] \
    [--git-diff] \
    [--json]
```

Behavior:

1. Locate the current latest-`GO` file in `bridge/<bridge-id>-NNN.md` per `bridge/INDEX.md`.
2. Call `extract_target_paths(go_file_text)` (imported from `scripts/implementation_authorization.py`) to get the canonical glob set.
3. Build candidate set:
   - If `--candidate-paths` provided: explicit set.
   - Else if `--git-diff`: parse `git diff --name-only HEAD` for staged + unstaged paths.
   - Else: read the current implementation-authorization packet at `.gtkb-state/implementation-authorization/current.json` and use its recorded `target_paths` as both expected and candidate (for verification of consistency).
4. Compute set drift:
   - `in_scope`: candidates matching at least one target glob.
   - `out_of_scope`: candidates matching no target glob.
   - `unused`: target globs with no matching candidate (informational; not a failure).
5. Emit a structured report:

```json
{
  "bridge_id": "...",
  "go_file": "bridge/.../-NNN.md",
  "target_paths": [...],
  "candidate_paths": [...],
  "in_scope": [...],
  "out_of_scope": [...],
  "unused_targets": [...],
  "verdict": "in_scope_only | out_of_scope_drift | no_go_file_found | missing_target_paths"
}
```

6. Exit codes: 0 (in_scope_only), 5 (out_of_scope_drift), 3 (no_go_file_found), 4 (missing_target_paths).

The script is read-only: it never writes, modifies, or stages anything. The verdict is informational.

### Hook integration: `.claude/hooks/bridge-compliance-gate.py`

Add a non-blocking advisory branch: when a `Write`/`Edit` tool call targets a file path, the hook MAY call the preflight in `--candidate-paths <single>` mode to enrich its block message with the matching/non-matching target glob. The hook continues to block based on its existing logic; the preflight call only enriches the message.

This is the lightest-touch integration. Future iterations can promote the preflight to a blocking gate, but Slice 1 keeps it advisory.

### Tests: `groundtruth-kb/tests/test_impl_start_target_paths_preflight.py`

Test cases:

| Test | Coverage |
|------|----------|
| `test_preflight_passes_when_candidates_all_in_scope` | basic happy path: all candidate paths match target globs |
| `test_preflight_detects_single_out_of_scope` | one candidate is out-of-scope; exit 5; verdict `out_of_scope_drift` |
| `test_preflight_detects_multiple_out_of_scope` | multiple candidates out-of-scope; all reported |
| `test_preflight_handles_glob_target_patterns` | target_paths includes glob patterns (e.g., `groundtruth-kb/src/**/*.py`); matching is correct |
| `test_preflight_reports_unused_targets_informational` | target glob with no candidate match → reported but not a failure |
| `test_preflight_reads_authorization_packet_when_no_candidates` | `--candidate-paths` omitted + packet exists → uses packet's target_paths as candidates |
| `test_preflight_exits_3_when_no_go_file_for_bridge_id` | bridge id has no GO file; exit 3; verdict `no_go_file_found` |
| `test_preflight_exits_4_when_go_file_missing_target_paths` | GO file exists but no `target_paths` metadata; exit 4 |
| `test_preflight_json_output_matches_schema` | `--json` emits valid JSON matching the documented schema |
| `test_preflight_git_diff_integration` | `--git-diff` mode reads `git diff --name-only HEAD` correctly (uses subprocess mock) |

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection. Re-run after this NEW entry is added to bridge/INDEX.md:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
```

Expected: `preflight_passed: true`, `missing_required_specs: []`.

## Specification-Derived Verification Plan

| Spec | Verification |
|------|--------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_preflight_reads_go_file_per_index` asserts the script's GO-resolution path matches `bridge/INDEX.md` semantics. |
| `GOV-RELIABILITY-FAST-LANE-001` | Bounded scope: one script + one test file + one hook touchpoint. Diff size kept under fast-lane threshold (<500 LOC). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_preflight_reads_go_file_fresh_on_each_invocation` asserts no cached extract; live bridge-file read every call. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites every relevant spec + maps each to a verification artifact (this table). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The test list above covers every cited functional spec. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Defect-class WI (origin=defect — gap in target_paths visibility) → fix → test → bridge artifact chain; this thread is the chain. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target_paths are within `scripts/`, `.claude/hooks/`, `groundtruth-kb/tests/` — GT-KB platform subtree only. |

Verification commands (will be run before filing the post-implementation report):

```text
cd /e/GT-KB && groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_impl_start_target_paths_preflight.py -v
ruff check scripts/impl_start_target_paths_preflight.py groundtruth-kb/tests/test_impl_start_target_paths_preflight.py
ruff format --check scripts/impl_start_target_paths_preflight.py groundtruth-kb/tests/test_impl_start_target_paths_preflight.py
python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --candidate-paths scripts/impl_start_target_paths_preflight.py groundtruth-kb/tests/test_impl_start_target_paths_preflight.py
```

## Risk / Rollback

- **Risk:** false positives if `target_paths` globs are too narrow (legitimate writes flagged as drift). Mitigation: Slice 1 is advisory-only; future blocking promotion is a separate proposal.
- **Risk:** glob-matching semantics drift from `extract_target_paths` parser. Mitigation: the preflight imports `extract_target_paths` from `implementation_authorization.py` — single source.
- **Rollback:** the script is a new file; delete it and revert the hook touchpoint to restore prior behavior. Zero data state mutated.

## Bridge Filing (INDEX-Canonical)

After this file is written, an entry will be inserted at the top of `bridge/INDEX.md`:

```text
Document: gtkb-impl-start-target-paths-preflight
NEW: bridge/gtkb-impl-start-target-paths-preflight-001.md
```

## Recommended Commit Type

`feat:` — new script + new test + minor hook integration.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
