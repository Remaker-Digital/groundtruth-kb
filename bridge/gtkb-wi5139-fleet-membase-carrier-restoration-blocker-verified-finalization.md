BLOCKER
author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-14T08-50-49Z-loyal-opposition-D-bac342
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

# VERIFIED Finalization Blocker - gtkb-wi5139-fleet-membase-carrier-restoration

document: gtkb-wi5139-fleet-membase-carrier-restoration
blocked_version: 003 (NEW; post-implementation report)
blocker_kind: verified_atomic_finalization_blocked_by_binary_hunk_patch_gate
blocking_session: 2026-07-14T08-50-49Z-loyal-opposition-D-bac342
claim_rowid: 31061

## Blocker Summary

Harness D (Ollama Loyal Opposition) reviewed `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-003.md` and found the implementation report substantively ready for VERIFIED. The work-intent claim was acquired (rowid 31061) after the prior F-session claim contention was resolved.

However, the governed VERIFIED atomic finalization helper cannot commit a same-transaction path set that includes `groundtruth.db` because the helper's hunk-patch isolation gate reads hunk patch files as UTF-8 text and extracts touched paths from `+++ b/<path>` unified-diff lines. `groundtruth.db` is a tracked SQLite binary file whose modification is represented by a `GIT binary patch` / `delta` block, not by UTF-8 `+++ b/groundtruth.db` lines. As a result:

- A `git diff --binary` patch is valid for `git apply` but is not UTF-8-readable text and contains no `+++ b/groundtruth.db` line for the helper's path parser.
- A `git diff --text` patch is readable text and contains `+++ b/groundtruth.db`, but the binary content causes the helper to fail with a UnicodeDecodeError when reading the patch file.

Per the harness instruction to fail closed when publication cannot commit atomically, harness D is recording this blocker instead of leaving a terminal VERIFIED file without its required atomic finalization commit.

## Completed Verification (ready for VERIFIED once finalization gate supports binary tracked paths)

- Applicability Preflight: passed (`preflight_passed: true`; no missing required/advisory specs).
- ADR/DCL Clause Preflight: passed (0 blocking gaps; all must_apply clauses have evidence).
- `pytest platform_tests/scripts/test_restore_fleet_membase_carriers.py -q --tb=short`: `5 passed, 1 warning`.
- `ruff check scripts/restore_fleet_membase_carriers.py platform_tests/scripts/test_restore_fleet_membase_carriers.py`: `All checks passed!`
- `ruff format --check scripts/restore_fleet_membase_carriers.py platform_tests/scripts/test_restore_fleet_membase_carriers.py`: `2 files already formatted`.
- `scripts/restore_fleet_membase_carriers.py --dry-run --json`: reports 41 candidate rows, 0 inserted, 41 skipped existing, confirming the live `groundtruth.db` already contains all restored carrier rows.
- `gt bridge dispatch report --json --compact`: WI-5216 and WI-5222 are PB-actionable GO with metadata resolved; WI-5211 moved from `bridge_metadata_unresolvable` to `missing_source_spec`; WI-5217 and WI-5219 remain `bridge_metadata_unresolvable` (out of scope).
- `gt bridge dispatch health --json`: daemon healthy, severity PASS.
- `gt harness roles`: Codex A remains `prime-builder` only.

## Recommended Next Step

Resolve the binary hunk-patch gate so that a VERIFIED verdict can atomically commit a same-transaction path set that includes a tracked binary SQLite file. Possible paths:

1. Update the atomic VERIFIED finalization helper to accept binary hunk patches by reading patch files as bytes and extracting `+++ b/<path>` from `git diff --text` output, or by allowing binary patches to bypass the `+++ b/` parser when the touched path is explicitly named.
2. Pre-approve an owner/DELIB-driven by-reference finalization waiver for `groundtruth.db` so the binary mutation is reviewed and accepted without requiring a line-oriented hunk patch.
3. Convert `groundtruth.db` to a line-dump representation for the commit, though this is a large project-level change and out of scope for WI-5139.

Once the gate is resolved, the Loyal Opposition harness holding the claim should publish VERIFIED for `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-003.md` with include_paths:

- `scripts/restore_fleet_membase_carriers.py`
- `platform_tests/scripts/test_restore_fleet_membase_carriers.py`
- `groundtruth.db`
- `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-001.md`
- `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-002.md`
- `bridge/gtkb-wi5139-fleet-membase-carrier-restoration-003.md`

Recommended commit message: `fix(governance): restore fleet-goal MemBase carrier metadata (WI-5139)`.
