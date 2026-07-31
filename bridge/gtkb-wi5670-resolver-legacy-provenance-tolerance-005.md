NO-ACTION
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: operational_state_change
Document: gtkb-wi5670-resolver-legacy-provenance-tolerance
Version: 005
Responds to: bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-004.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5670
target_paths: []

# WI-5670 GO Stop — Stated Real-World Acceptance Is Unreachable

## Disposition

No implementation action is authorized under version 004. After acquiring the
current-session claim, Prime Builder stopped before source mutation or staging
for two independent reasons:

1. The named implementation-start packet still belongs to prior Prime session
   `2b72a308-90ed-492d-aaeb-16015fe5efaf`, not the current claim holder.
2. More importantly, the proposed implementation cannot satisfy acceptance
   criterion 3 or the claimed WI-5152 real-world unblock.

The two target files retain their pre-existing unstaged candidate and foreign
hunks; this session changed neither file.

## Blocking Evidence

`bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md`, the exact
artifact cited by versions 003 and 004, lacks both `author_identity:` and
`Responds to:` metadata. A direct read-only resolution now fails:

```text
WRONG_RESPONDS_TO_LINK at
bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md
```

The WI-5670 design deliberately retains strict Document/Version/Responds-to
checks and relaxes only missing `author_identity`. Its tests likewise contain
no structurally legacy `include_responds=False` case. Therefore the proposed
change cannot make
`implementation_authorization.py begin --bridge-id
gtkb-wi5152-modernization-hard-invariant-registry` return `authorized: true`.
Changing the fixture would abandon rather than prove the stated live unblock.

## Clear Condition

A fresh Prime revision and independent LO review must first resolve the
requirement choice:

- explicitly extend grandfathering to missing historical linkage metadata and
  add fail-closed operative-link tests; or
- narrow WI-5670 to author-provenance conformance, remove the WI-5152 unblock
  claim, and route the linkage defect as separate governed work.

That choice materially changes the observable scope and cannot be inferred
from the current GO. A later implementation must also issue a fresh
current-session packet and preserve the approved cached-hunk isolation.

## Requirement Sufficiency

Existing requirements are insufficient for the newly exposed linkage-policy
decision. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` governs author metadata but does
not by itself establish whether historical `Responds to` linkage is also
grandfathered.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELIABILITY-FAST-LANE-001`

## Prior Deliberations

- `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-003.md` — approved
  revision containing the now-disproved WI-5152 acceptance claim.
- `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-004.md` — GO relying
  on the same incomplete reproduction.
- `DELIB-20260683` — author-provenance grandfathering contract; no explicit
  linkage-metadata disposition was found.

## Specification-Derived Verification

- Direct numbered-file read confirmed the cited v002 artifact lacks both
  metadata fields.
- Direct resolver execution reached `WRONG_RESPONDS_TO_LINK`, proving the
  proposed author-only change cannot satisfy the live acceptance command.
- Focused resolver suite remains green (`52 passed`), Ruff check and format
  pass, and the implementation/foreign hunks remain unstaged and separable;
  these facts do not cure the acceptance-scope mismatch.

## Owner Decisions / Input

No prior owner decision resolves whether structural linkage metadata shares
the author-provenance grandfathering rule. Preserve this as the clear condition
for a later corrected proposal; no implementation proceeds meanwhile.

## Risk / Rollback

Proceeding would create a false-terminal implementation report for an
acceptance criterion that remains impossible. No implementation mutation or
commit occurred, so no rollback is required. Bridge history remains
append-only.
