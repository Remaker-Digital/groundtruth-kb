NEW

# Implementation Proposal - GTKB-ISOLATION-017 Slice 5.5: Overlay Refresh, Disposability, and Chroma Regeneration API

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Follow-on implementation proposal
**Risk tier:** Medium (adopter overlay/cache regeneration and clean-adopter regression coverage; no production deployment)
**Backlog item:** `GTKB-ISOLATION-017-SLICE-5.5`

---

## Background

Slice 5 clean-adopter tests shipped stale-overlay detection but explicitly
deferred refresh and disposability. The deferral was owner-approved because the
user-facing Chroma regeneration API did not exist in `groundtruth-kb/src/`; only
the rehearsal lane existed at `scripts/rehearse/_chromadb_regen.py`.

This proposal files the deferred Slice 5.5 work through the normal bridge
lifecycle. It does not implement the API or tests until Loyal Opposition
returns `GO`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  the governing release, bridge, isolation, and testing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation report
  must map the tests below to these cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 31 of
  `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the overlay API and test evidence
  must remain durable, traceable, and stateful.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - adopter work must stay under the
  GT-KB root and application placement boundary; no live dependency on
  `E:\Claude-Playground` is allowed.
- `.claude/rules/file-bridge-protocol.md` and
  `.claude/rules/codex-review-gate.md` - no implementation before `GO`.
- `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` -
  owner-approved deferral of overlay refresh/disposability into Slice 5.5.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "Slice 5.5 overlay refresh disposability chroma regeneration API clean adopter isolation" --limit 8
```

Relevant result: `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE`
directly authorizes deferring refresh and disposability from Slice 5 into this
follow-on slice. Adjacent ChromaDB review records (`DELIB-0700`, `DELIB-0703`)
are context only and do not reject this work.

## Proposed Scope

1. Add a public adopter-facing Chroma regeneration surface in the GT-KB package.
   Recommended shape:
   - `groundtruth_kb.project.chroma.regenerate(target: Path, *, dry_run: bool = False)`
   - `gt project chroma regenerate --dir <adopter> [--dry-run] [--json]`
2. Reuse the deterministic behavior proven in `scripts/rehearse/_chromadb_regen.py`
   where appropriate, but do not expose the rehearsal driver itself as the
   adopter API.
3. Add clean-adopter tests:
   - `groundtruth-kb/tests/adopter/test_overlay_refresh.py`
   - `groundtruth-kb/tests/adopter/test_overlay_disposability.py`
4. Keep the existing stale-detection tests intact.
5. Document the API briefly in the isolation chapter or adjacent adopter docs
   only if needed for test discoverability.

## Acceptance Criteria

- A clean adopter can delete `.groundtruth-chroma/` and regenerate it from
  authoritative GT-KB records without manual rehearsal scripts.
- Refresh is deterministic and bounded to the provided adopter target.
- Disposability test proves delete-cache -> regenerate -> doctor pass.
- The API refuses paths outside the current GT-KB/adopter boundary.
- No code reads or writes `E:\Claude-Playground`.
- The implementation report includes passing targeted tests and a spec-to-test
  map.

## Test Plan

Suggested commands:

```powershell
cd groundtruth-kb
python -m pytest tests/adopter/test_overlay_stale_detection.py tests/adopter/test_overlay_refresh.py tests/adopter/test_overlay_disposability.py -q --tb=short
python -m pytest tests/test_doctor_isolation.py -q --tb=short
python -m ruff check src tests
python -m ruff format --check src tests
```

## Out Of Scope

- Rebuilding all historical Chroma stores.
- Changing the Deliberation Archive semantic search model.
- Restoring deleted external/archive paths.
- Publishing `v0.7.0-rc1`.

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO`, starting with the library API and CLI, then
the two clean-adopter tests.

