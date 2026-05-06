REVISED

# Implementation Proposal - GTKB-PRE-FILING-PREFLIGHT-HOOK (REVISED-1)

**Author:** Prime Builder (Codex, harness A)
**Filed:** 2026-05-06
**Prior review:** `bridge/gtkb-pre-filing-preflight-hook-002.md` (`NO-GO`)
**Work type:** PreToolUse bridge-governance enforcement

## Claim

Revise the hook implementation so it validates the pending `Write` content, not
the current indexed bridge file. The first implementation slice is explicitly
`Write`-only for the applicability preflight check; `Edit` post-edit content
reconstruction is deferred to a separate bridge item.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the hook protects bridge packets before
  they are filed into the authoritative bridge queue.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the hook blocks
  bridge proposals that omit required governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation must
  include regression tests proving pending-content enforcement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the gate preserves durable
  governance artifacts rather than allowing defective bridge packets into the
  lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the applicability preflight remains
  deterministic, local, and traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - blocked, revised, and verified bridge
  lifecycle states remain explicit.
- `.claude/rules/project-root-boundary.md` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all pending-content scratch files
  stay under `E:\GT-KB`; application and Agent Red files remain under
  `applications/` when relevant.

## NO-GO Finding Response

| Finding | Disposition in this revision |
| --- | --- |
| F1 - subprocess preflight validates indexed disk content | Closed by adding a content-aware preflight mode and making the hook pass pending `Write` content. |
| F2 - `Edit` handling underspecified | Closed for this slice by explicitly limiting applicability enforcement to `Write` and deferring `Edit` reconstruction. |
| F3 - caching contradiction | Closed by removing caching from the design. Every hook invocation evaluates its own pending content. |

## Proposed Changes

### 1. Add content-aware applicability preflight

Extend `scripts/bridge_applicability_preflight.py` with a pending-content mode:

```text
python scripts/bridge_applicability_preflight.py --bridge-id <id> --content-file <path>
```

Behavior:

- `--bridge-id` remains required so the report is tied to the intended bridge
  document name and expected index entry.
- `--content-file` makes the preflight evaluate the supplied Markdown content
  instead of reading the latest operative file from `bridge/INDEX.md`.
- The report identifies the content source as `pending_content` and records the
  supplied file path, but it still reports the current indexed operative file
  for context when one exists.
- Required and advisory specification detection uses the same matcher as the
  existing index-backed mode.
- No cache is added.

### 2. Wire the hook to pending `Write` content

Update `.claude/hooks/bridge-compliance-gate.py` so the applicability preflight
check runs only when all of these are true:

- the tool is `Write`;
- the target path is a bridge packet under `bridge/`;
- the pending content starts with a bridge lifecycle status such as `NEW` or
  `REVISED`;
- the target bridge document can be derived from the filename.

The hook writes the pending content to a short-lived scratch file under
`E:\GT-KB\.tmp\bridge-preflight-hook\` and invokes the new `--content-file`
mode. The scratch path must be root-contained and removed best-effort after the
check. Hook failure output should include the missing required spec IDs and the
pending file path being blocked.

### 3. Explicitly defer `Edit` applicability enforcement

The hook remains free to keep existing `Edit` behavior, but this slice does not
claim that `Edit` payloads are applicability-preflighted. A follow-on bridge
item should reconstruct the post-edit file content before applying this same
preflight to `Edit`.

## Proposed Test Plan

- `test_preflight_content_file_uses_pending_content`: indexed disk packet is
  compliant, pending content removes a required specification, and
  `--content-file` reports `missing_required_specs`.
- `test_preflight_content_file_passes_for_pending_compliant_content`: pending
  content with required links passes even when the indexed file is stale.
- `test_bridge_hook_blocks_write_when_pending_content_fails_preflight`: the
  hook rejects a `Write` payload that would remove required spec links.
- `test_bridge_hook_allows_write_when_pending_content_passes_preflight`: the
  hook allows a compliant pending bridge packet.
- `test_bridge_hook_does_not_claim_edit_applicability_preflight`: `Edit`
  payloads are not treated as content-aware applicability checks until a
  separate reconstruction slice exists.
- `test_bridge_hook_preflight_has_no_cache`: two writes to the same path with
  different content are evaluated independently.
- `test_bridge_hook_scratch_path_is_root_contained`: the scratch content path is
  created under `.tmp/bridge-preflight-hook/` inside the GT-KB project root.

## Out Of Scope

- Reconstructing post-edit file content for `Edit`.
- Changing bridge transition semantics.
- Restoring or replacing the retired OS poller.
- Reading or writing live GT-KB artifacts outside `E:\GT-KB`.

## Implementation Sequence

1. Add `--content-file` support and focused tests to
   `scripts/bridge_applicability_preflight.py`.
2. Add the `Write`-only hook adapter in `.claude/hooks/bridge-compliance-gate.py`.
3. Add hook regression tests for pass, block, no-cache, and root-contained
   scratch behavior.
4. Run targeted pytest and ruff checks on the touched scripts/tests.
5. File a post-implementation bridge report with exact commands and observed
   results.

## Risk / Impact

This narrows the first enforcement slice but makes it mechanically correct for
the content surface that `Write` actually provides. It avoids approving stale
index content while making the remaining `Edit` gap explicit and separately
reviewable.

## Decision Needed From Owner

None.
