NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - gt backlog add stamps Codex-created rows as prime-builder/claude

bridge_kind: prime_proposal
Document: gtkb-gt-backlog-add-attribution-resolution
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4367

target_paths: ["scripts/_kb_attribution.py", "platform_tests/scripts/test_kb_attribution.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The harness-aware `changed_by` resolver in `scripts/_kb_attribution.py` mis-attributes a MemBase write to the *configured* single active Prime Builder (currently `claude`/harness B) whenever the process running a mutating CLI cannot positively identify its own harness — i.e. when neither an explicit `harness_name` kwarg nor the `GTKB_HARNESS_NAME` environment variable is present. In that case `resolve_changed_by()` falls through to its priority-3 fallback (`_active_prime_builder_harness_name()`), which returns the configured active Prime Builder rather than the harness that actually executed the command. On 2026-06-05 Codex (durable role `loyal-opposition`, harness A, then acting as Prime Builder) ran `gt backlog add` for WI-4360 through WI-4366 in a process where `GTKB_HARNESS_NAME` was not in the environment, so the rows were stamped `prime-builder/claude` even though the same session's Deliberation Archive approval row — written through a path that *did* know it was Codex — was correctly stamped `codex-prime-builder/A`. The defect is a silent cross-harness mis-attribution vector that the harness-aware resolver was specifically introduced to eliminate.

## Defect / Reproduction

Root cause (confirmed by inspection):

1. `resolve_changed_by()` (`scripts/_kb_attribution.py:226-271`) resolves the harness name through `_resolve_harness_name()` (`:172-179`) using a three-source order: (1) explicit `harness_name` kwarg, (2) `GTKB_HARNESS_NAME` env var, (3) `_active_prime_builder_harness_name()` — the single active Prime Builder fallback.
2. `gt backlog add` (`groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py:142-157`, `add_backlog_item` at `:198`) calls `resolve_changed_by()` with **no** `harness_name` kwarg, by design (no `--changed-by` option exists; attribution is resolver-owned).
3. The running harness only reaches priority 1 or 2 if its identity is in-process. But the live environments do not reliably carry that signal:
   - **Claude Code** sets `CLAUDECODE=1` and `CLAUDE_CODE_SESSION_ID` but does NOT set `GTKB_HARNESS_NAME` (verified in a live Claude Code session env: `GTKB_HARNESS_NAME` absent).
   - **Codex** sets `GTKB_HARNESS_NAME=codex` only via the cmd.exe `set` in `.codex/gtkb-hooks/session-start.cmd:2`. A `set` in a `.cmd` does not propagate to a python process spawned from a different shell context (e.g. a Bash-launched `python -m groundtruth_kb ...`), so the env var is frequently absent for the actual CLI subprocess.
4. With priorities 1 and 2 both missing, priority 3 returns `_name_for_harness_id(<single active prime-builder id>)` = `claude`. Every harness that runs `gt backlog add` without the env var is therefore stamped `prime-builder/claude`, regardless of which harness actually ran it.

Reproduction (logical): in a shell with `GTKB_HARNESS_NAME` unset, run `gt backlog add` as any harness other than the configured Prime Builder. The inserted row's `changed_by` is `prime-builder/claude` (the configured PB), not the running harness's `<role>/<name>`. This matches the WI-4360..4366 incident exactly: the durable role map has `claude=prime-builder`, `codex=loyal-opposition`, so the sole-Prime fallback resolves to `claude` whenever the env var is absent.

The fix design follows an existing, proven in-repo precedent: `scripts/cross_harness_bridge_trigger.py:2434-2439` already recovers harness identity from vendor process indicators (`CLAUDE_PROJECT_DIR` -> `claude`; `CODEX_THREAD_ID`/`CODEX_HOME` -> `codex`) when `GTKB_HARNESS_NAME` is absent. This proposal adds the same deterministic vendor-env detection step to the attribution resolver between priority 2 and priority 3, so the *running* harness is identified before any configured-Prime fallback can substitute a different harness.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/_kb_attribution.py`, `platform_tests/scripts/test_kb_attribution.py`. The change is confined to the platform attribution resolver and its platform test module; no application/adopter surface under `applications/` is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal travels the bridge protocol (NEW -> GO -> implement -> report -> VERIFIED); `VERIFIED` is the authoritative terminal signal that gates the eventual commit.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - the governing authority for harness attribution: roles attach to harness identity, not vendor name, so `changed_by` must reflect the harness that actually performed the write; the defect violates this by stamping the configured PB instead of the acting harness.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - the resolver reads harness identity/role from the consolidated harness-state SoT (`harness-state/harness-identities.json`, `harness-state/harness-registry.json`); the fix adds a runtime detection source that maps a vendor signal to a name that is then validated against that same SoT (no new identity authority is introduced).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - accurate `changed_by` provenance keeps the durable `work_items` artifact trail trustworthy; mis-attributed rows degrade the artifact audit trail that governance depends on.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specifications (mandatory linkage gate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives every test from a cited spec clause and lists the exact execution commands (mandatory spec-derived testing gate).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the required Project Authorization / Project / Work Item metadata lines (mandatory project linkage gate).
- `SPEC-AUQ-POLICY-ENGINE-001` - confirms no AskUserQuestion owner decision is required for this fix beyond the standing fast-lane authorization; the proposal claims no new owner-decision scope, so the AUQ policy surface is satisfied by the standing PAUTH cited in Owner Decisions / Input.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform (`scripts/...` + `platform_tests/...`); no application-placement boundary is crossed and no adopter surface is touched.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the defect's Codex limb is precisely a hook-parity gap (the `.cmd` `set` of `GTKB_HARNESS_NAME` does not reach the CLI subprocess); the fix adds a resolver-side mechanical fallback so correct attribution does not depend on hook env propagation, consistent with this ADR's mechanical-fallback stance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - `changed_by` provenance is an artifact-backed fact; the fix keeps that fact derived from the acting harness identity rather than an inferred configured default.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - correct attribution at row-creation time is the lifecycle trigger this fix protects (the `work_items` create event must record the true author).
- `GOV-STANDING-BACKLOG-001` - WI-4367 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES; `gt backlog add` is the standing-backlog capture verb whose attribution this fix corrects.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-HARNESS-ROLE-PORTABILITY-001` already establishes that `changed_by` attribution must reflect the harness identity that performed the work (roles attach to harness identity, not vendor name), and the harness-aware resolver contract (`bridge/gtkb-kb-attribution-harness-aware-003.md`, Codex GO at `-004`) already mandates fail-closed attribution. This fix enforces that existing contract by closing the identity-resolution gap that lets a configured-Prime fallback substitute for the acting harness. No new or revised requirement/specification is introduced; the resolver's documented three-source contract is preserved (priority 3 remains as a last resort) and is only made more accurate by inserting a positive runtime-identity source ahead of the fallback.

## Prior Deliberations

- `DELIB-2026-06-14-WI4483-WI4514-CLOSE-RESOLVED-REGISTRY-CORRECTION` - prior harness role-state correction work; directly relevant precedent that harness identity/role-state drift produces mis-attribution and is corrected at the SoT, not by special-casing a vendor.
- `DELIB-20264748` - Loyal Opposition Verification, S341 Backlog Candidates MemBase Batch Insert - prior verification of a `gt backlog`-class batch insert; relevant context for backlog-capture attribution correctness.
- `DELIB-20264491` - Loyal Opposition Verification, Orphan WI Membership Discovery Slice 1 - relevant work-item provenance/membership context (attribution feeds membership/audit correctness).
- The two `DELIB-20260963` / `DELIB-20261162` (WI-3326 Executable Packet Repair) seeds are not on-topic for attribution resolution and are dropped from this proposal. The governing prior-decision record for the attribution contract itself is the bridge thread `bridge/gtkb-kb-attribution-harness-aware-003.md` (Codex GO at `-004`), which introduced the fail-closed resolver this fix hardens.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - the standing reliability fast-lane authorization. WI-4367 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the mis-attribution, requires no new/revised requirement or spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by this standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-4367 (P3 defect) is in scope of that batch directive.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the owner direction establishing the reliability fast lane that PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING operationalizes; cited here as the durable origin of the fast-lane authorization rationale.

No additional AskUserQuestion owner decision is required: this fix introduces no new requirement, no new public surface, and no destructive or deployment action.

## Proposed Scope

Minimal, single-concern defect removal in two files:

1. In `scripts/_kb_attribution.py`, add a deterministic vendor-env harness-identity detection helper (e.g. `_harness_name_from_runtime_env()`) that returns a harness name only when a recognized vendor process indicator is present, mirroring the proven pattern in `scripts/cross_harness_bridge_trigger.py:2434-2439`:
   - `CLAUDECODE` (or `CLAUDE_CODE_SESSION_ID` / `CLAUDE_PROJECT_DIR`) present -> `"claude"`.
   - `CODEX_HOME` (or `CODEX_THREAD_ID`) present -> `"codex"`.
   - No recognized indicator -> `None` (no guess).
   The helper returns a raw name only; it does NOT bypass the existing identity/role validation in `resolve_changed_by()` (the returned name is still resolved against `harness-state/harness-identities.json` and must still have a durable role, preserving fail-closed semantics).
2. Insert that detection step into `_resolve_harness_name()` **between** priority 2 (`GTKB_HARNESS_NAME`) and priority 3 (`_active_prime_builder_harness_name()`). Resulting order: (1) explicit kwarg, (2) `GTKB_HARNESS_NAME`, (3) **vendor-env runtime detection (new)**, (4) single active Prime Builder fallback (unchanged, now last). This makes the *running* harness identify itself before any configured-Prime substitution can occur, which is the WI's literal ask ("make Codex/Claude attribution resolve from the active harness identity").
3. Preserve the headless-dispatch contract: under headless dispatch (`GTKB_BRIDGE_POLLER_RUN_ID` set), the existing wrappers already export `GTKB_HARNESS_NAME` for the dispatched worker, so priority 2 wins and the new step is never reached; the new step is a no-op for dispatched runs and changes no headless behavior.
4. Add regression tests in `platform_tests/scripts/test_kb_attribution.py` (see verification plan). The new tests redirect harness-state reads via the existing `GTKB_HARNESS_REGISTRY_PATH` / `GTKB_HARNESS_IDENTITIES_PATH` env overrides and monkeypatch the vendor-env signals, so they never read or mutate live state.

Out of scope (would require a new requirement, excluded from this fast-lane fix): changing the resolver's documented three-source public contract by *removing* priority-3; modifying the Codex `.cmd` env-propagation mechanism (the resolver-side fallback makes correctness independent of it); and any change to `cli_backlog_add.py` (it already correctly delegates attribution to the resolver — the defect is entirely in the resolver's identity resolution).

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-HARNESS-ROLE-PORTABILITY-001` (attribution reflects the acting harness, not the configured PB) | `test_runtime_env_detects_codex_over_prime_fallback` | With kwarg=None, `GTKB_HARNESS_NAME` unset, durable map `claude=prime-builder` / `codex=loyal-opposition`, and a Codex vendor signal (`CODEX_HOME`) present, `resolve_changed_by()` == `loyal-opposition/codex` (NOT `prime-builder/claude`). |
| `GOV-HARNESS-ROLE-PORTABILITY-001` (symmetric Claude detection) | `test_runtime_env_detects_claude` | With kwarg=None, `GTKB_HARNESS_NAME` unset, and a Claude vendor signal (`CLAUDECODE=1`) present, `resolve_changed_by()` == `prime-builder/claude` via the runtime-detection step (claude is the acting harness, not via the PB fallback). |
| `gtkb-kb-attribution-harness-aware` contract (explicit kwarg and env var still win) | `test_kwarg_and_env_precede_runtime_env_detection` | An explicit `harness_name` kwarg, and (separately) `GTKB_HARNESS_NAME`, each take precedence over a conflicting vendor signal (e.g. kwarg=`codex` + `CLAUDECODE=1` -> `loyal-opposition/codex`). |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (detection does not bypass SoT validation / fail-closed) | `test_runtime_env_unknown_harness_still_fails_closed` | A vendor-detected name that has no entry in the identities SoT (or no durable role) still raises `RuntimeError`; the new step never returns an unvalidated or `unknown` attribution. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` (priority-3 fallback preserved as last resort — no regression) | `test_single_prime_fallback_still_used_when_no_vendor_signal` | With kwarg=None, `GTKB_HARNESS_NAME` unset, and NO vendor signal present, the existing single-active-Prime fallback still resolves (`prime-builder/claude`), so the existing resolver contract and prior tests are preserved. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_kb_attribution.py -q --tb=short`
- `python -m ruff check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py`
- `python -m ruff format --check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py`

## Acceptance Criteria

1. With `GTKB_HARNESS_NAME` unset and no explicit kwarg, `resolve_changed_by()` resolves to the *acting* harness identity when a recognized vendor process signal is present (Codex -> `<durable-role>/codex`, Claude -> `<durable-role>/claude`), never silently to the configured single active Prime Builder.
2. Explicit `harness_name` kwarg and `GTKB_HARNESS_NAME` continue to take precedence over the new vendor-env detection (no precedence regression).
3. The new detection never bypasses identity/role validation: an unknown vendor-detected name still fails closed with `RuntimeError`; no `unknown`/fallback literal is ever returned.
4. The existing single-active-Prime fallback (priority 3, now last) still resolves when no vendor signal is present (no regression of existing behavior or existing tests).
5. Headless dispatch attribution is unchanged (priority 2 already wins for dispatched workers).
6. All new + existing tests in `test_kb_attribution.py` pass; `ruff check` and `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: a future runtime where BOTH a Claude signal and a Codex signal are present (e.g. one harness invoked from inside the other's shell) could be detected ambiguously. Mitigation: the detection helper checks signals in a fixed, documented order and returns the first match; because explicit kwarg and `GTKB_HARNESS_NAME` both precede detection, any caller that needs certainty already has a higher-priority path, and the fail-closed validation still rejects an unresolved/unknown name. A test pins the precedence order.
- Risk: over-eager detection could mis-classify an ad-hoc shell that happens to carry a stale vendor env var. Mitigation: detection is only consulted when both higher-priority sources are absent, and the detected name is still validated against the harness-state SoT and must have a durable role before it is used; otherwise the resolver raises. This is strictly safer than the current silent priority-3 substitution.
- Risk: behavioral drift for callers that *relied* on the old priority-3 substitution. Mitigation: priority 3 is preserved unchanged as the last resort, so any caller in an environment with no vendor signal sees identical behavior; only environments that DO carry a positive vendor signal change, and for those the new behavior is the correct (acting-harness) attribution.
- Rollback: revert the helper addition and the single inserted resolution step in `scripts/_kb_attribution.py` plus the added tests. The change is additive (one helper + one ordered step + tests), fully reversible, with no schema or data migration.

## Files Expected To Change

- `scripts/_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution.py`

## Recommended Commit Type

`fix`
