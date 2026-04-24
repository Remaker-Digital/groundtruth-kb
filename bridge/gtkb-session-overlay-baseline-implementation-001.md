NEW

# GTKB Session Overlay Baseline Implementation Proposal

bridge_kind: proposal
scope: protocol
work_item_ids: [GTKB-ISOLATION-006]
target_paths: [".gitignore", "scripts/gtkb_overlay.py", "scripts/check_session_overlay_policy.py", "scripts/release_candidate_gate.py", "scripts/session_self_initialization.py", "tests/scripts/test_gtkb_overlay.py", "tests/scripts/test_release_candidate_gate.py", "tests/scripts/test_session_self_initialization.py"]

## Requested Verdict

GO to implement the narrow Phase 6 overlay baseline below, or NO-GO with
required revisions.

## Parent GO Inputs

This proposal is the first concrete implementation slice after the accepted
Phase 6 planning review:

- `bridge/gtkb-isolation-006-overlay-plan-review-003.md`

The Phase 6 plan accepted the session-overlay design and required later
concrete implementation proposals before behavior changes.

## Claim

The correct first Phase 6 implementation slice is manifest-first and
non-authoritative by construction:

1. create an app-local overlay manifest/builder library that can copy a small
   allowlisted set of generated dashboard/startup artifacts into
   `.groundtruth/session/overlays/<overlay_id>/`,
2. add a policy checker and startup visibility so overlays are explicitly
   labeled as non-authoritative, stale-aware context only, and
3. avoid promotion, bridge summaries, formal-record copies, raw DB copies, or
   any writeback path in this first slice.

This slice should prove safe overlay mechanics without pretending the later
promotion or control-plane flows are already complete.

## Current Evidence

### Existing Snapshot-Like Surfaces

- `scripts/session_self_initialization.py` already generates dashboard data and
  startup/wrap-up reports under `docs/gtkb-dashboard/`, but those files are not
  overlay manifests and do not carry overlay authority metadata.
- `.groundtruth/` currently contains approval evidence and point-in-time
  snapshot JSON files, but there is no `.groundtruth/session/overlays/`
  runtime structure yet.
- `.gitignore` already treats `.groundtruth-chroma/`, dashboard runtime DB, and
  Grafana runtime state as ephemeral/local, which is compatible with ignoring a
  future overlay runtime root.

### Existing Safety Boundary

- The Phase 6 plan requires stable local wrappers to remain outside overlays,
  and the current `.claude/hooks/workstream-focus.py` wrapper already imports
  stable local policy code rather than relying on a transient overlay.
- No current overlay or snapshot mechanism marks copied artifacts
  `authoritative: false`, tracks source hashes, or exposes stale status at
  startup.

### Why This Slice Is First

- Overlay failure is mostly a metadata and classification problem before it is
  a promotion problem.
- The smallest meaningful proof is to build and validate non-authoritative
  overlays for already-generated app-local context artifacts.
- Copying only dashboard/startup artifacts avoids the dangerous early cases
  called out by the Phase 6 plan: raw DB copies, bridge-state confusion,
  formal-record confusion, and transient-hook dependency.

## Scope

Implement only:

1. A new `scripts/gtkb_overlay.py` module providing:
   - overlay ID generation
   - manifest schema helpers
   - allowlisted source inventory
   - copy-only builder
   - stale-status evaluation
2. Initial overlay allowlist limited to existing app-local generated context
   files:
   - `docs/gtkb-dashboard/dashboard-data.json`
   - `docs/gtkb-dashboard/session-startup-report.md`
   - `docs/gtkb-dashboard/session-wrapup-report.md`
   - `memory/gtkb-dashboard-history.json`
3. Overlay root and pointer files:
   - `.groundtruth/session/overlays/current.json`
   - `.groundtruth/session/overlays/<overlay_id>/manifest.json`
4. Manifest metadata with:
   - `authoritative: false`
   - source hash
   - source path
   - subject
   - role slot
   - harness ID
   - created/expires timestamps
5. Startup visibility in `scripts/session_self_initialization.py` so overlay
   status is visible but not trusted as canonical state.
6. `.gitignore` coverage for the overlay runtime root.
7. A new `scripts/check_session_overlay_policy.py` checker and release-gate
   wiring.
8. Focused tests for the builder, stale detection, manifest shape, ignore
   policy, and startup visibility.

Do not implement in this slice:

- promotion dry-run or apply,
- control-plane overlay refresh endpoints,
- projection preview storage,
- bridge summary copies,
- Deliberation Archive or MemBase copies,
- raw `groundtruth.db` or `.groundtruth-chroma/` copies,
- retention cleanup beyond manifest validation,
- any overlay-dependent hook or startup enforcement path.

## Proposed Overlay Contract

Overlay root:

```text
.groundtruth/session/overlays/
  current.json
  <overlay_id>/
    manifest.json
    files/
      dashboard-data.json
      session-startup-report.md
      session-wrapup-report.md
      gtkb-dashboard-history.json
```

`current.json` is only a pointer to the active overlay. It is not canonical
state and must not be trusted if stale or invalid.

Required manifest fields for this slice:

```json
{
  "schema_version": "1",
  "overlay_id": "20260423T000000Z-agent-red-codex-prime",
  "authoritative": false,
  "application_root": "absolute app root",
  "subject": "application",
  "role_slot": "prime-builder",
  "harness_id": "codex-local",
  "created_at": "timestamp",
  "expires_at": "timestamp",
  "entries": [
    {
      "overlay_path": "files/dashboard-data.json",
      "source_kind": "file",
      "source_uri": "docs/gtkb-dashboard/dashboard-data.json",
      "source_hash": "sha256...",
      "authoritative": false
    }
  ]
}
```

## Proposed First-Slice Guard Rules

1. Every manifest and entry must declare `authoritative: false`.
2. The builder must deny any source path outside the fixed allowlist.
3. The builder must not copy `.env*`, `groundtruth.db`, `.groundtruth-chroma/`,
   bridge files, or any executable content.
4. Missing or stale overlays may be reported at startup, but startup must not
   fail open by treating them as canonical records.
5. The checker must fail if an overlay manifest is malformed, marks itself
   authoritative, or points outside the application root.

## Proposed File Touchpoints

Primary code:

- `scripts/gtkb_overlay.py`
- `scripts/check_session_overlay_policy.py`
- `scripts/session_self_initialization.py`
- `.gitignore`
- `scripts/release_candidate_gate.py`

Tests:

- `tests/scripts/test_gtkb_overlay.py`
- `tests/scripts/test_release_candidate_gate.py`
- `tests/scripts/test_session_self_initialization.py`

## Implementation Sequence

1. Add the overlay builder and manifest helpers.
2. Add `.gitignore` coverage for `.groundtruth/session/overlays/`.
3. Add the overlay policy checker.
4. Add startup visibility for current overlay status.
5. Wire the checker and focused tests into the release gate.

## Verification Commands

Required focused checks:

```powershell
python scripts/check_session_overlay_policy.py --json
python -m pytest tests/scripts/test_gtkb_overlay.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py -q --tb=short
```

Recommended broader check after focused green:

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

## Review Questions

1. Is limiting the first Phase 6 slice to copied dashboard/startup artifacts
   narrow enough while still proving the overlay contract?
2. Is it acceptable to defer promotion, bridge summaries, and projection
   preview storage until later slices?
3. Should the overlay builder remain a local script/library in this slice, with
   no dashboard/control-plane endpoint yet?

## Non-Scope Reminder

This proposal does not request promotion, control-plane overlay refresh,
projection preview/apply, bridge-summary copies, DB copies, or overlay-backed
hook enforcement. Those remain later slices.
