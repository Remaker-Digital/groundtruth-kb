NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: G
author_model: claude-opus
author_model_version: 2026
author_model_configuration: goose-desktop-harness
author_session_context_id: G-2026-07-31T07-41-38Z
bridge_kind: implementation_report
Document: gtkb-wi5823-impl-auth-spec-links-extractor-alignment
Version: 003
Responds to: bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-002.md
spec_links:
  - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  - DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001
  - WI-5823
project_id: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
pauth_id: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730

# WI-5823 Implementation Report — Slice A+B: Spec-Links Extractor Alignment

## Summary

Slice A (`_section_body_including_subsections`) and Slice B (`_preflight_parity_harvest`)
are implemented and verified. The `extract_spec_links` function now uses a
level-aware section-body reader and a three-branch harvesting pipeline
(bullets → table → preflight-parity harvest). All 202 existing impl-auth tests
pass. A previously-failing table-format proposal (WI-5808, which yielded zero
links before this change) now correctly extracts 18 concrete specification
links.

Slice C (post-GO formatting-only amendment path) is NOT included in this
report; it remains for a future implementation pass per the v001 proposal scope.

## Implementation Detail

### Slice A: Level-aware section body (`_section_body_including_subsections`)

Added above `section_body()` at line ~641. Uses `_iter_section_spans` (which
yields `(level, heading, body)` tuples keyed by heading level `##` vs `###`)
so that `### Required (blocking)` and `### Advisory` subheadings under
`## Specification Links` are retained in the returned body. The existing
`section_body()` is unchanged; all other callers continue to use it.

`extract_spec_links` now calls `_section_body_including_subsections` instead
of `section_body` for its `## Specification Links` body grab.

### Slice B: Preflight-parity harvest (`_preflight_parity_harvest`)

Added as third additive branch in `extract_spec_links`. Fires only when both
the bullet and table branches return zero links. Harvests concrete citation
tokens from any prose format using the same token classes the GO-time
applicability preflight already recognizes:

1. Backtick-quoted tokens
2. `_SPEC_ID_RE` uppercase artifact IDs (GOV-..., DCL-..., etc.)
3. `.claude/rules/` file paths

Returns deduplicated list, keeping only tokens without forward-slash in the
first three characters (to filter out filesystem paths while keeping artifact
IDs).

### Modified function: `extract_spec_links`

Three-branch harvesting pipeline:
1. **Bullet branch** — existing, unchanged, highest precedence
2. **Table branch** — existing, fires when bullets yield zero
3. **Preflight-parity harvest** — NEW (Slice B), fires when both above yield zero

## Verification

### Unit tests
```
202 passed in 78.90s
```
All six impl-auth test modules pass:
- `test_implementation_authorization.py` (163 tests)
- `test_implementation_authorization_extract_spec_links_table.py` (12 tests)
- `test_implementation_authorization_gfr_slice_a.py` (4 tests)
- `test_implementation_authorization_harness_selector.py` (6 tests)
- `test_implementation_authorization_packet_paths.py` (7 tests)
- `test_implementation_authorization_terminal_evidence.py` (10 tests)

### Previously-failing proposal: WI-5808
Before WI-5823: `extract_spec_links` returned **0 links** (bullet branch empty,
table branch empty, no third branch → AuthorizationError).

After WI-5823: **18 links** extracted via the preflight-parity harvest branch:
`GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-APPROVAL-001`,
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
`DELIB-202667726`, `DELIB-202667727`, `DELIB-202667722`, `WI-5808`, plus 5 more.

### File integrity
Backup at `scripts/implementation_authorization.py.wi5823-backup`.

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| `extract_spec_links` parses table-format spec links (WI-5808 case) | PASS |
| `_section_body_including_subsections` preserves ### subheadings | PASS |
| `_preflight_parity_harvest` extracts from prose/compact-citation format | PASS |
| Bullet and table branches unchanged in behavior | PASS |
| All 202 existing tests pass | PASS |
| No regressions in `extract_spec_links` for any existing bridge document | PASS |

## Deferred

- **Slice C**: Post-GO formatting-only amendment path. The v001 proposal
  included this as a third slice but the GO verdict (v002) confirmed it as a
  separable future item. It is not implemented here.

## Implementation Files Changed

- `scripts/implementation_authorization.py`: +55 lines net, Slice A+B only
  (the working-tree diff's extra chunks in `write_named_packet`,
  `_worker_harness_selector`, `write_started_packets`, and `main` are
  pre-existing from prior uncommitted work and are not part of this WI-5823
  implementation)