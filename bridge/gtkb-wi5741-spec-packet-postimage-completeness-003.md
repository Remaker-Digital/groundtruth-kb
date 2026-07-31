REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop


# WI-5741 — Preserve FAB-14 While Binding the Complete Spec Postimage

bridge_kind: prime_proposal
Document: gtkb-wi5741-spec-packet-postimage-completeness
Version: 003
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5741-spec-packet-postimage-completeness-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5741

target_paths: ["groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_update.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_record.py", "platform_tests/groundtruth_kb/governance/test_approval_packet.py", "platform_tests/groundtruth_kb/cli/test_spec_update.py", "platform_tests/groundtruth_kb/cli/test_spec_record.py", "platform_tests/scripts/test_fab14_formal_autodiscovery.py"]

implementation_scope: exact-seven-path-source-and-test-repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Summary

Version 002 correctly found that version 001 would break FAB-14 packet
autodiscovery by changing the hash of the required `--content-file` bytes. This
revision preserves `full_content` byte-for-byte and leaves
`full_content_sha256` as the SHA-256 of those exact bytes. It adds a separate,
versioned, deterministic semantic-postimage envelope to the shared approval
packet constructor and validator.

The new envelope covers the exact normalized non-description row postimage,
not only the five JSON options named in the original defect. This is necessary
because `gt spec update` and `gt spec record` also persist title, lifecycle
status, and other scalar metadata. Artifact identity/type remain bound by the
existing packet fields; description remains bound by `full_content` and its
existing hash. No hook source, live approval packet, MemBase row, dispatcher,
repository history, release, deployment, credential, or external system is a
mutation target of this proposal.

This proposal performs no MemBase mutation or `groundtruth.db` write. It also
performs no live approval-evidence file write; implementation tests use only
temporary project roots.

## Finding-by-Finding Response to Version 002

### F1 — FAB-14 autodiscovery

**Accepted and corrected.** The implementation must not append anything to
`full_content`. Both `full_content` and `full_content_sha256` remain identical
to the content-file text and hash used by `_autodiscover_packet`. Structured
and scalar postimage evidence is carried only in the dedicated fields below.
Neither hook copy changes.

### F2 — Missing hook constraint link

**Accepted and corrected.** `DCL-ARTIFACT-APPROVAL-HOOK-001` is now a governing
Specification Link. Its v5 text explicitly permits deterministic packet
autodiscovery when artifact id and full-content hash match. This proposal
preserves both operands.

### F3 — Gate-facing regression and requirement sufficiency

**Accepted and corrected.** The test plan now constructs a structured packet
through the production CLI, proves `_autodiscover_packet` still finds it by the
unchanged content-file hash, and proves the hook's shared validator rejects a
corrupted semantic-postimage hash.

No new DCL is required. `GOV-ARTIFACT-APPROVAL-001` v4 already requires the
review packet to include title, lifecycle status, metadata, links,
assertions/constraints where applicable, and full content.
`DCL-ARTIFACT-APPROVAL-HOOK-001` v5 already specifies the artifact-id plus
full-content-hash discovery contract. The three new field names and canonical
JSON hashing rule are a backward-compatible internal encoding that implements
those existing requirements; no new CLI option, owner workflow, lifecycle
rule, or hook-selection semantic is introduced. Fast-lane criterion 3 remains
satisfied.

### F4 — Over-broad approval-store target

**Accepted and corrected.** The live approval-evidence store is excluded from
`target_paths`, and no packet there is written. Tests use temporary roots only.

### F5 — Record-path compatibility guard

**Accepted and corrected.** The record suite now independently proves that
`full_content` and `full_content_sha256` remain the content-file bytes and hash.
The packet may gain the new semantic envelope; the FAB-14 binding bytes do not
change.

### F6 — Imprecise source citation

**Accepted and corrected.** The defect site is
`groundtruth-kb/src/groundtruth_kb/cli_spec_update.py:157-201`: the row mutation
contains description plus scalar and JSON overrides, while the packet builder
at `:133-154` receives only the description text. The record path has the same
separation at `cli_spec_record.py:168-181` and `:265-279`.

## Exact Proposed Change

### 1. Shared semantic-postimage envelope

Extend `groundtruth_kb.governance.approval_packet` with three optional fields:

- `postimage_schema_version`: integer `1`;
- `postimage_fields`: the exact normalized non-description semantic row
  postimage; and
- `postimage_sha256`: lowercase SHA-256 over the canonical binding envelope.

The hash input is canonical UTF-8 JSON for this object:

```json
{
  "action": "<packet action>",
  "artifact_id": "<packet artifact_id>",
  "artifact_type": "<packet artifact_type>",
  "fields": {"<semantic field>": "<normalized value>"},
  "full_content_sha256": "<existing content-file hash>",
  "schema_version": 1,
  "source_ref": "<packet source_ref>"
}
```

Canonicalization uses `json.dumps(..., ensure_ascii=False, sort_keys=True,
separators=(",", ":"), allow_nan=False)` with UTF-8 encoding and no added
newline. The shared constructor accepts `postimage_fields`, detaches it through
a canonical JSON round trip, inserts schema version 1, and computes the hash;
callers never supply the hash.

The shared validator enforces these invariants:

1. Legacy packets with none of the three fields remain valid.
2. Presence is atomic: if any field is present, all three are required.
3. Schema version is exactly integer 1; Boolean values do not qualify.
4. `postimage_fields` is a non-empty JSON-native object with string keys.
   Tuples, sets, bytes, non-string keys, non-finite floats, and other
   non-JSON-native values are rejected recursively.
5. Explicit empty list/dict field values remain distinct from omission.
6. The validator recomputes the exact binding-envelope hash and rejects any
   mismatch.
7. Constructor output is detached from later caller mutation.

The two live formal-artifact hooks already prefer this shared validator when
the package is importable, so their source does not change. Their repair-forward
fallback remains backward-compatible with the unchanged mandatory packet
fields; it does not become an alternate schema authority.

### 2. Complete update postimage

After loading the current spec row and validating all request values,
`cli_spec_update.py` builds a fixed-key normalized postimage by applying the
supplied overrides to the current row. It includes:

`title`, `status`, `priority`, `scope`, `section`, `handle`, `tags`,
`assertions`, `constraints`, `affected_by`, `testability`, `source_paths`, and
`application_scope`.

All keys are present, including normalized null/empty values, so the evidence
is the final semantic row postimage rather than a change fragment. The
description remains exclusively in `full_content`; id/type/action/source
version remain in existing packet fields. The same normalized values are sent
to `KnowledgeDB.update_spec`, preventing packet/row dual drift.

### 3. Complete record postimage

`cli_spec_record.py` passes the fixed-key normalized create postimage for the
same thirteen fields to the shared constructor. Required `title` and `status`
are therefore evidenced even when none of the five JSON options is supplied.
The values used for the packet are the values sent to `KnowledgeDB.insert_spec`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` — requires complete native review evidence,
  including title, lifecycle status, metadata, links, and assertions or
  constraints where applicable.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — permits artifact-id/full-content-hash
  autodiscovery; the binding remains unchanged and is tested directly.
- `GOV-RELIABILITY-FAST-LANE-001` — governing defect fast lane; this remains a
  small internal repair with no new API, workflow, or requirement.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — packet evidence and persisted semantic
  row must derive from one normalized postimage.
- `PB-ARTIFACT-APPROVAL-001` — owner-facing approval behavior remains enforced
  while evidence completeness is repaired.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — central constructor/validator remains
  the packet schema implementation authority.
- `SPEC-1662` (`GOV-18`) — tests assert semantic equality and tamper detection,
  not field presence alone.
- `GOV-10` — CLI tests exercise the production update and record interfaces.
- `GOV-12` — WI-5741 carries focused regression additions.
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Prior Deliberations

- `DELIB-202667528` — owner routing context for the blocked DCL v8
  re-derivation.
- `DELIB-202667526` — live session-role evidence whose durable formalization
  requires a complete approval postimage.
- `DELIB-202667220` — retired-authority purge order blocked on the same repair.
- `DELIB-202667523` — manual-dispatcher program mandate and fast-lane routing.
- `bridge/gtkb-wi5679-session-role-keying-continuity-016.md` F1 and
  `bridge/gtkb-wi5718-retired-session-role-authority-purge-012.md` F2 — the
  independent findings this tooling correction unblocks.
- `bridge/gtkb-wi5741-spec-packet-postimage-completeness-002.md` — the FAB-14,
  linkage, test, scope, compatibility, and citation findings answered here.

## Owner Decisions / Input

The owner already directed the DCL v8 re-derivation through
`AUQ-20260729-DCL-V8-REDERIVATION` and the reliability program through
`DELIB-202667523`. This revision introduces no new owner-facing format or
workflow choice: it implements packet contents already required by
`GOV-ARTIFACT-APPROVAL-001` while preserving the explicit autodiscovery
contract in `DCL-ARTIFACT-APPROVAL-HOOK-001`. No additional owner decision is
required before independent review.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-ARTIFACT-APPROVAL-001` v4 defines
the complete evidence categories and `DCL-ARTIFACT-APPROVAL-HOOK-001` v5 defines
the preserved discovery binding. The schema-versioned JSON envelope is an
internal implementation mechanism for those existing requirements, not a new
governed behavior.

## Spec-Derived Test Plan

### Shared constructor and validator

In `platform_tests/groundtruth_kb/governance/test_approval_packet.py`:

1. Prove deterministic, order-independent hashing for nested Unicode JSON.
2. Reject each partial trio, a wrong hash, Boolean/unsupported schema versions,
   non-string keys, non-JSON values, and non-finite floats.
3. Prove explicit empty list/dict values survive, output is detached from later
   caller mutation, and a legacy packet without the trio still validates.

### Update CLI

In `platform_tests/groundtruth_kb/cli/test_spec_update.py`:

4. Update scalar plus all five JSON fields and assert the packet's fixed-key
   normalized postimage equals the persisted/dry-run row values.
5. Prove explicit empty list/dict overrides are evidenced rather than collapsed
   into omission.
6. Prove a description-only update retains exact content-file
   `full_content`/hash and carries forward the current semantic postimage.

### Record CLI

In `platform_tests/groundtruth_kb/cli/test_spec_record.py`:

7. Record scalar plus structured fields and assert packet evidence equals the
   values supplied to the row writer, including required title/status.
8. Prove a description-only record retains exact content-file
   `full_content`/hash while still evidencing the normalized scalar postimage.

### Live FAB-14 integration

In `platform_tests/scripts/test_fab14_formal_autodiscovery.py`:

9. Generate a structured packet through the production CLI, write it under a
   temporary approval store, and prove `_autodiscover_packet` finds it by the
   unchanged artifact id and content-file hash.
10. Corrupt only `postimage_sha256` and prove `gate._validate_packet` rejects
    the packet through the shared validator.

## Verification Plan

1. Baseline and post-change focused suite:
   `python -m pytest platform_tests/groundtruth_kb/governance/test_approval_packet.py platform_tests/groundtruth_kb/cli/test_spec_update.py platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/scripts/test_fab14_formal_autodiscovery.py -q --tb=short`.
2. Ruff check and format-check the three Python source files and four test
   files.
3. `git diff --check` over the exact seven targets and an exact-path worktree
   audit proving no foreign byte entered the implementation cohort.
4. After an independent GO only, `implementation_authorization.py begin
   --no-write` and the durable begin must authorize all seven exact targets
   before any protected edit.
5. Live acceptance: a DCL v8 `gt spec update --dry-run` packet retains the
   description content hash used by FAB-14 and its validated postimage contains
   the full final assertion inventory plus the normalized scalar metadata.

Baseline evidence before this revision: the exact four-module suite passed
`38 passed` with one unrelated pytest configuration warning in 26.57 seconds.

## Acceptance Criteria

1. Every newly generated update/record packet carries a validated, versioned,
   deterministic semantic postimage for the exact final non-description row
   fields.
2. `full_content` and `full_content_sha256` remain the exact content-file bytes
   and hash, and FAB-14 autodiscovery succeeds for structured updates.
3. Legacy packets without the new trio remain valid; malformed or tampered new
   envelopes fail closed in the shared validator.
4. Packet evidence and row-writer inputs use the same normalized values,
   including explicit empty collections and carried-forward update values.
5. All focused tests, Ruff checks, formatting checks, and exact-path diff checks
   pass with no hook or approval-store mutation.

## Authorization And Worktree Evidence

The active standing PAUTH covers WI-5741 through active project membership.
Canonical operation-time evaluation of this exact seven-path envelope passes
`bridge_proposal_filing`, `work_intent_acquire`,
`implementation_packet_create`, `implementation_start`,
`protected_mutation`, and `git_commit`. The paths classify as three `source`
and four `test` targets; the PAUTH's `test_addition` permission normalizes to
the canonical `test` class. Evaluated envelope SHA-256:
`22340B42C2947B068C8C72839D869912A37640707BA71DAA20A161AB4812B363`.

All seven targets were clean at revision drafting. The broader worktree is
shared and dirty, so any later implementation/finalization must remain
exact-path only. No bridge GO, proposal revision, claim, or implementation
packet authorizes adoption of unrelated changes.

## Risk And Rollback

Risk is bounded to packet-schema compatibility and row/evidence drift. The
atomic optional trio, legacy validation path, unchanged autodiscovery hash, and
production-CLI integration test constrain that risk. Rollback is an exact-path
revert of the seven-target implementation commit; already-issued packets remain
append-only evidence and continue to validate under the legacy-or-v1 rule.

## Pre-Filing Preflight Evidence

- Applicability preflight: exit `0`; `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; no missing parent or unclassified target path;
  candidate packet hash
  `sha256:66da8078aa363af115c0a1d6c80ec119887df416454dceebfe9763a921bf2fae`.
  Draft author-metadata warnings are expected; the governed writer inserts the
  authoritative session metadata before publication.
- Clause preflight: exit `0`; five clauses evaluated; three `must_apply`, two
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps.

Any missing specification, blocking clause gap, version race, claim loss, or
authorization denial at publication aborts filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
