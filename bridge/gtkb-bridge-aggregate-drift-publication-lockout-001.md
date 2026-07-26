ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6c2d71b4-210a-4119-988d-d1860598093e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker (loyal-opposition-worker task); transcript-resolved role loyal-opposition
author_metadata_source: session envelope (harness-state/claude/session-envelopes/6c2d71b4-210a-4119-988d-d1860598093e.json)

bridge_kind: governance_advisory
Document: gtkb-bridge-aggregate-drift-publication-lockout
Version: 001
Author: Loyal Opposition (Claude, harness B) — advisories are role-agnostic per DELIB-202667454
Date: 2026-07-26

# Bridge Aggregate Drift Causes Platform-Wide Publication Lockout With No Durable Recovery

## Source

Discovered empirically during the WI-5441 v4-005 post-implementation verification
(`bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`, VERIFIED).
Both findings below were triggered, observed, and repaired live in session
`6c2d71b4-210a-4119-988d-d1860598093e` on 2026-07-26. They are not speculative.

Owner directive in this session (2026-07-26): file these findings as a separate
thread rather than as findings against WI-5441.

This advisory does not contest the WI-5441 VERIFIED verdict. That implementation
satisfies its approved proposal and all ten acceptance criteria, each independently
re-executed by this reviewer. These findings concern an operational property the
approved scope did not cover and the implementation report did not disclose.

## Claim

Two P1 defects in the bridge publication control plane.

### Finding F1 (P1) — a stale bridge aggregate hard-blocks ALL bridge publication, platform-wide

**Claim.** When the registered `bridge-versioned-files` glob record is stale, no
bridge file can be published by any harness, on any thread, for any status.

**Evidence.**

- `scripts/gtkb_bridge_writer.py` `write_bridge_file` routes every publication
  through `mint_bridge_publication_capability` (line ~1065) whenever
  `_registry_publication_enabled` is true, which it is whenever the canonical
  registry, packaged registry, and `groundtruth.db` all exist.
- `groundtruth_kb/project/registry_control_plane.py`
  `mint_bridge_publication_capability` (line ~2171) raises
  `RegistryAuthorizationError` unless registry currentness is green.
- Observed live: with the aggregate stale, a VERIFIED publication failed with
  `bridge publication requires a current registry generation`. The block is not
  scoped to the failing thread; it is a precondition on the shared writer.

**Risk / impact.** The aggregate is a glob over `bridge/*-[0-9][0-9][0-9].md`, so
its digest changes on ANY out-of-band change to `bridge/` — a crash, a process
timeout, an editor, and most concerningly ordinary git operations such as
`checkout`, `stash`, or a branch switch. Any of these can leave the platform unable
to publish bridge work at all, halting the Prime Builder / Loyal Opposition
protocol entirely. This is a single point of failure for the whole coordination
mechanism.

**Recommended action.** Provide a durable, governed re-observation path that can
restore aggregate currentness after out-of-band drift without requiring currentness
as its own precondition (the present circularity). Note that the one-time bootstrap
`recover_wi5441_bridge_aggregate` is retired and raises immediately (line ~2701),
and `recover_registry` (line ~1433) recovers transaction-journal states only, not
aggregate observation drift — so no in-band recovery presently exists.

### Finding F2 (P1) — publication compensation cannot survive process death

**Claim.** The designed rollback for a failed post-create publication is in-process
only and is lost if the process dies.

**Evidence.**

- `scripts/gtkb_bridge_writer.py` keys pending publications in
  `_PENDING_BRIDGE_PUBLICATIONS`, a module-level dict.
- `rollback_pending_bridge_publication` (line ~977) looks the publication up in
  that dict; when absent and registry publication is enabled it raises
  `BRIDGE_PUBLICATION_REPAIR_REQUIRED: pending capability context is unavailable;
  file and claim are retained`.
- Observed live: a `--finalize-verified` run was killed by an external timeout
  after `write_bridge_file` had created the verdict and appended the aggregate
  revision, but before the git commit. Neither `finalize_pending_bridge_publication`
  nor `rollback_pending_bridge_publication` ran, and the in-memory record died with
  the process, leaving an uncommitted verdict with no reachable compensation path.

**Risk / impact.** Any abnormal termination (timeout, kill, crash, host restart)
during the publication window leaves a bridge artifact whose compensation state is
unrecoverable. Recovery then depends on operator judgement — which is precisely how
this session produced the F1 lockout: an out-of-band deletion of the orphaned
artifact desynchronized the aggregate from its recorded revision.

**Recommended action.** Persist pending-publication state durably (journal or
control-plane table) so compensation and finalization are reachable by a later
process, and add a governed resume/rollback entrypoint keyed to that record.

### Reproduction and repair evidence

- Stale state observed: `current: false`, sole stale record `bridge-versioned-files`,
  DB-recorded `sha256:70ac8fe33d363d5fcbce93024e91dff936e364d15b74fde3492eb1ea48454f56`
  versus live-on-disk `sha256:47c039b6518332b0b464830c2257c077766d276e9d7621d5e94f392b336ac4ff`.
  (In `registry_currentness`, `observed` is the DB revision and `current` is the
  live computed digest — the field names read counter-intuitively and misled this
  reviewer once.)
- Repair: restoring the artifact byte-exactly returned the live digest to the
  DB-recorded value. Post-repair `gt registry inspect --no-census --json` reports
  `current: true`, `stale: []`, `missing_revisions: []`, `coherent: true`,
  `record_count: 145`, with declaration, generation, and projection digests
  unchanged from their pre-incident values.
- Blast radius was confined to one record's observation freshness; no registry
  content or structure was affected.

## Owner Decision Needed

None required to file this advisory. Three owner decisions are required before any
derived implementation proposal may be filed; they are enumerated in the
Owner-Grilling Gate below rather than duplicated here.

## Recommended Prime Action

1. Conduct the owner-grilling pass below and capture the three decisions as durable
   `AskUserQuestion` evidence.
2. File one or two implementation proposals (scoping is decision 3) citing this
   advisory as `Source advisory` and in `Prior Deliberations`.
3. Treat F1 as the higher priority: until an in-band recovery path exists, any
   out-of-band `bridge/` change can halt all bridge coordination, and the repair
   demonstrated here (byte-exact artifact restoration) depends on still holding the
   exact bytes — which will not generally be true.

## Classification Slot

**adopt** — both defects are confirmed, reproduced, and have concrete remediation
directions. No design alternatives require evaluation before Prime Builder scopes
the work; the open questions are scope and posture, not whether the defects are
real.

### Required Prime Builder Owner-Grilling Gate

**Implementation implied: yes.** Both findings require source changes to
`scripts/gtkb_bridge_writer.py` and
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`, plus
regression coverage.

**Grill-the-owner questions.** Prime Builder must obtain durable
`AskUserQuestion`-recorded answers to:

1. **Recovery authority model.** Should out-of-band aggregate drift be repairable
   by a standing governed command, or must each repair carry per-incident owner
   authorization? The retired WI-5441 bootstrap chose the latter; F1 shows the cost
   is a platform-wide outage with no in-band exit.
2. **Failure posture.** Should a stale aggregate continue to hard-block ALL bridge
   publication (fail-closed, current behavior), or degrade to blocking only
   publications that would themselves mutate the stale record? This is a
   safety-versus-availability trade the owner should set explicitly.
3. **Scope and sequencing.** Are F1 and F2 one work item or two, and do they
   precede, follow, or run alongside the outstanding WI-5640 work that WI-5441 was
   unblocking?

**Required durable owner decisions** before a derived proposal is filed: the
recovery-authority model (1), the failure posture (2), and work-item scoping and
sequencing (3).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`

## Prior Deliberations

- `DELIB-202666498` — Loyal Opposition Corrected GO Verdict, WI-5316 Failed
  VERIFIED Finalization Repair. The closest adjacent precedent: prior handling of a
  failed VERIFIED finalization. It does not address aggregate observation drift or
  durable pending-publication state.
- `DELIB-20265642` — WI-4697 Implementation Start Gate Emergency Exemption.
  Establishes that the broad emergency path intentionally fails closed for ordinary
  non-bridge protected paths; cited because it is why no existing exemption reaches
  the registry control plane.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — registry is the
  ultimate artifact-membership authority; unchanged by this advisory.
- `DELIB-202667454` — advisories are role-agnostic; basis for the role-neutral
  `governance_advisory` kind and the absence of a role envelope on `ADVISORY`.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` — the
  VERIFIED verdict during which both findings were discovered.
- Semantic Deliberation Archive search for bridge-aggregate drift, registry
  currentness, and publication lockout returned no controlling prior decision on
  this exact failure mode.

## Non-Approval Statement

This advisory is not implementation approval. It records two confirmed defects and
recommended remediation directions for governed disposition. It does not bypass the
bridge proposal, Loyal Opposition `GO`, implementation-start authorization, or
verification gates, and it does not by itself authorize any source mutation or
widen any existing project scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
