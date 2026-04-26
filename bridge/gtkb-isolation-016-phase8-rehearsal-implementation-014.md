GO

# GTKB-ISOLATION-016 Phase 8 Rehearsal Revision Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`
**Mode:** Implementation proposal re-review
**Decision:** GO

## Verdict

GO for Wave 1. The `-013` revision resolves the `-012` blocker: the `applications/Agent_Red` topology is now backed by a formal upstream ADR, the Phase 9 plan paragraph is locally superseded, and the Agent Red KB has a local ADR mirror.

## Evidence

- Upstream commit `affa5a0567a64f79bb4c5aae891889d4af50a72a` exists in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`.
- The upstream ADR file exists at `docs/architecture/adrs/ADR-ISOLATION-APPLICATION-PLACEMENT-001.md`.
- The Agent Red Phase 9 plan now strikes the old outside-root paragraph at lines 95-99 and adds a `SUPERSEDED` notice citing the upstream commit at lines 101-108.
- `.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json` exists and cites the owner S310 Option B directive plus Codex GO at `bridge/gtkb-adr-isolation-application-placement-004.md`.
- `groundtruth.db` contains `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in `specifications` with `type='architecture_decision'` and `status='specified'`.
- `git ls-tree --name-only -d HEAD` confirms `scripts`, `website`, and `widget` are tracked top-level directories; `-013` adds them to the conflated-surface list.

## GO Conditions

- Implement `validate_target_root()` as a positive allow rule: target roots under `E:\GT-KB\` are valid only when they resolve under `E:\GT-KB\applications\<name>\` with a valid `<name>`. The blocklist is useful evidence, but it must not be the only protection against hidden or newly-added root-level directories.
- Keep `tools` in the test parameterization even though it was already present before `-013`; the full 31-entry blocklist should be covered.
- The post-implementation report should include the exact command proving the Phase 9 plan annotation and ADR mirror still exist after Wave 1, because this proposal now depends on cross-repo governance state.

## Non-Blocking Notes

- `applications_namespace` is useful in the manifest because it makes the ADR-backed namespace machine-readable for later Phase 9 tooling.
- The local ADR status of `specified` is acceptable here because `-013` explicitly defers promotion to `implemented` pending a future DCL with machine-checkable assertions.

## Verification

Static review plus live evidence checks. No implementation tests were run because this is a pre-implementation proposal review.

## Decision Needed From Owner

None.

