NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 2 Proposal

Status: NO-GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md` is not approved as
written. The slice direction is right, but the proposal has blocking contract
and verification defects that would make the inventory lane incomplete and the
test suite unstable.

## Findings

### F1 - Blocking: inventory output omits required per-file metadata

The proposal states that `inventory.json` will contain a `{path -> sha256,
size, mtime}` map plus aggregate stats
(`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md:32`). The proposed
`_walk_inventory()` implementation instead calls `hash_set_walk()` and returns
`"files": hashes`, where each value is only the SHA-256 string
(`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md:168`).

Impact: downstream lanes would receive an inventory that does not satisfy the
slice's own contract. Aggregate `total_bytes` does not replace per-file `size`
and `mtime`, and tests that only assert file count or existence would miss the
defect.

Required revision: make `inventory["files"]` a per-file object map, for example
`{relative_path: {"sha256": "...", "size": 123, "mtime": "..."}}`, or revise
the formal scope if hash-only is truly sufficient. Add tests that assert each
file entry carries hash, size, and mtime. If the implementation keeps using
`hash_set_walk()`, it still needs a second per-file `stat()` pass with clear
TOCTOU handling; alternatively, implement the inventory walk directly in
`_inventory.py` with the same ignore semantics.

### F2 - Blocking: proposed integration test hashes the live legacy root

The proposal includes `test_run_happy_path_against_real_matrix`, which uses the
real production manifest and matrix and expects `run()` to return `ok`
(`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md:312`). The proposed
`run()` calls `_walk_inventory(LEGACY_ROOT, manifest)` before parsing the matrix
(`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md:257`), which means that
test hashes the live mixed root.

Existing driver context explicitly warns not to walk the legacy root in default
execution because the walk is expensive and has exceeded 120 seconds on the
live repo (`scripts/rehearse_isolation.py:118` through
`scripts/rehearse_isolation.py:120`). Current pytest config also enforces a
30-second timeout in this checkout, as shown by the verification run.

Impact: the proposed normal test suite can become slow, flaky, or timeout-prone
depending on local caches and runtime files. It also risks reading unrelated
local state that should not be part of a deterministic unit or CI check.

Required revision: keep unit/integration tests on fixture trees and monkeypatch
`LEGACY_ROOT` or `hash_set_walk()` as needed. A real-root inventory check can be
manual, opt-in, or explicitly marked slow outside the normal release gate. The
production lane may still walk the live root when the operator explicitly runs
that lane; the blocker is making it part of the ordinary automated test path.

### F3 - Blocking: runtime surface schema is not yet justified for downstream lanes

The source manifest says runtime `surface_treatments` should follow the matrix
Required Matrix Shape, including `surface_id`, path/capability/environment,
ownership, subject authority, access model, and verification evidence
(`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml:56`
through `:60`). The authority matrix document's Required Matrix Shape lists
fields such as `surface_id`, `path_globs`, `target_subject`, environment
controls, and verification
(`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:58`
through `:85`).

The proposal instead parses only the six-column "Preliminary Authority Matrix"
section (`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md:33`) and asks
Codex to confirm that this six-field shape is enough for downstream lanes
(`bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md:355`). I cannot confirm
that from the current evidence.

Impact: lanes 2-11 could be built against an underspecified runtime manifest
and then need another schema correction after implementation begins.

Required revision: explicitly define the runtime `surface_treatments` schema for
Wave 2 and show which downstream lanes consume which fields. If the six-column
preliminary table is intentionally enough for Slice 2, document that as a
bounded interim schema and add tests for exactly that contract. If the Required
Matrix Shape is required, extend the parser/source data before using the
runtime manifest as the downstream contract.

## Recommended Action

Revise Slice 2 before implementation:

- Fix the inventory file-entry shape or narrow the scope explicitly.
- Replace live-root automated tests with fixture-based tests.
- Resolve the runtime `surface_treatments` schema question before lanes 2-11
  depend on it.

## Decision Needed From Owner

None.
