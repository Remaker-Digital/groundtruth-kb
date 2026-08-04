NEW
::init gtkb pb
::open build

bridge_kind: prime_proposal
Document: gtkb-wi5933-bridge-publication-currentness-livelock
Version: 001
Date: 2026-08-03 UTC

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T00-46-39Z
author_model: goose
author_model_version: goose
author_model_configuration: interactive owner session, ::init gtkb pb, ::open build

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5933

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py"]

No KB mutation proposed by this entry. This entry records the defect and the
emergency-bootstrap authority under which it was repaired; the repair commit
and its evidence are recorded in the companion WITHDRAWN after-action entry at
version 002.

# NEW — WI-5933 Bridge-Publication Currentness Livelock

## Summary

`mint_bridge_publication_capability` in
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` gated
bridge publication on `registry_currentness` over the `bridge/*-NNN.md` glob.
`registry_currentness` is audit state, not publication authority (its own
docstring: hot mutation/publication paths should select exact records or use
`registry_identity_state`). Gating on it required a caller-recorded observation
(taken OUTSIDE the mint's serialized lock) to equal freshly-computed content.
Under concurrent governed publishers the recorded observation always lagged
actual content, so the currentness check never converged and every publication
failed closed: an optimistic-CAS livelock over an append-only aggregate.

This livelock blocked all governed bridge publication while it was active.

## Defect mechanism (root cause)

- The mint is a compare-and-swap chain: caller observes the aggregate ->
  records a generation G (outside any lock) -> mint (under `_RegistryFileLock`)
  requires recorded-observation == freshly-computed content.
- The observe that establishes the preimage happens OUTSIDE the serialization
  boundary. Under concurrent publishers each one's recorded preimage goes stale
  the instant another append lands, and because the content hash over
  ~15,000 files takes ~10s the conflict window is large.
- Reality moved faster than observations got recorded -> the preimage could
  never catch up -> livelock. Optimistic CAS was being used where writers are
  concurrent and the conflict domain is the whole append-only glob.

The immediate triggering incident: a runaway automated batch-publish loop
(`.gtkb-state/_lo_publish_from_recs.py`, two instances) was appending ~1
bridge file per minute, keeping the aggregate generation perpetually unstable
so `mint_bridge_publication_capability` failed closed on every other
publication. Even after that flooder was stopped and the worker pool quiesced,
the observe->mint race persisted for any concurrent governed publisher; the
structural defect is the observe-outside-lock gap, independent of the flooder.

## Why this is an emergency-bootstrap repair (protocol section (a))

The defect being repaired is the bridge-publication infrastructure that the
normal bridge protocol depends on. Filing a NEW proposal and running a normal
GO -> implementation -> VERIFIED cycle requires the very publication path that
was livelocked. Per the governance emergency-bootstrap exception protocol
(`governance-emergency-bootstrap-protocol.md`, section (a)):

1. Foundational governance subsystem broken with an active failure: the
   bridge-publication path failed closed on every publication.
2. The normal bridge path was blocked by the defect itself.
3. The change is the minimal repair that restores the subsystem (no scope
   creep).

The repair was implemented under emergency-bootstrap authority in commit
`b04fdf70e` (see version 002 of this thread for the full record and evidence).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - required (blocking) - the numbered bridge
  chain is the canonical audit surface; this thread is filed append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - required
  (blocking) - this entry cites the specs that constrain the closed work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - required (blocking) -
  governs the spec-derived verification surface; the executed regression suite
  (finalization-atomicity + evaluation-bound + registry-control-plane) is the
  test evidence recorded for this repair.
- `GOV-ARTIFACT-APPROVAL-001` - required (blocking) - retroactive
  owner-approval capture for the emergency-bootstrap action.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - required (blocking) - the closed
  work scope was in-root under `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\`.

## Requirement Sufficiency

Existing requirements sufficient. WI-5933, the cited specifications, and the
DELIB-202668164 durable-concurrency-fix directive fully constrain this repair;
no new or revised specification is required.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

- `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:
  publication-finalization atomicity and consume-path regression via
  `platform_tests/scripts/test_bridge_publication_finalization_atomicity.py`.
- Protected-commit bounded evaluation (the gate this publication path feeds)
  via `platform_tests/scripts/test_protected_commit_evaluation_bound.py`.
- Registry control-plane behavior (mint / capability / serialization) via
  `groundtruth-kb/tests/test_registry_control_plane.py`.

Observed result: 97 passed, 2 skipped (the 2 skips are the deliberately-deferred
WI-5742 Layer-C stubs, not part of this repair). Independent Loyal Opposition
verification of the repaired publication path is deferred to the WI-5742 Layer C
governed cycle; this repair is NOT self-VERIFIED.

## Proposed change (what the repair does)

- Remove the global-generation `registry_currentness` gate from the mint
  (docstring-justified: audit state is not publication authority).
- Establish the aggregate preimage via a self-observe (`_append_revision`)
  INSIDE the existing `_RegistryFileLock` + one-active-capability boundary, so
  `latest == current` by construction and concurrent governed publishers
  serialize correctly instead of livelocking.

Follow-on (not part of this minimal repair): make the aggregate generation
hash incremental so the serialized critical section is cheap under high
publication concurrency.

## Prior Deliberations

- `DELIB-202668164` - owner directive that concurrency issues receive a durable
  platform-wide fix; serialization is the durable fix.
- The WI-5742 Layer C thread (`gtkb-wi5742-bound-protected-commit-evaluation`,
  v005 proposal, v006 GO) is adjacent: it owns the late-mint / compensation
  reordering of the same publication transaction and is NOT superseded by this
  repair.

## Owner Decisions / Input

- The owner directed stopping the runaway batch-publish flooder (PIDs 63460 +
  45200) that was destabilizing the bridge aggregate.
- The owner selected the separate-finalization path (Option 1) for this repair
  in interactive session `G-2026-08-03T00-46-39Z`: WI-5933 finalizes on its own
  emergency-bootstrap cycle; WI-5742 Layer C proceeds separately.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
