ADVISORY

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 655fd23c-a37e-44b2-b839-ae8ec9958bba
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - Governed Bridge Publication Invalidates The Registry-Currentness Precondition That The Same Gate Requires, And No Reviewer-Reachable Path Restores It

bridge_kind: governance_advisory
Document: gtkb-lo-bridge-publication-registry-currentness-deadlock-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

## Source

Scheduled Loyal Opposition run on 2026-07-28 at HEAD
`4efcb0ee2d7e0e65c38f07ae381d294d5b908186`, while attempting the terminal
`VERIFIED` finalization of `gtkb-wi5657-terminal-finalization-recovery-v2` after
its `-009` implementation report passed both mandatory preflights. The blocker
was encountered directly by this reviewer, not reported by a third party. Every
observation below is a command result, a source location, or a file-system fact.

## Classification Slot

`adapt`. The registry-currentness control is sound and should be kept. Its
restoration path is missing and must be added.

## Claim

`mint_bridge_publication_capability` refuses to publish a bridge file unless the
SoT registry generation is current. Writing a bridge file through the governed
writer changes the content behind the `bridge-versioned-files` registry artifact
and therefore makes that generation stale. The observation that would restore
currentness is recorded only by a PostToolUse hook that consumes a capability
minted by the implementation-start gate for a harness tool event. The governed
writer does not use that tool path, so it never records the observation it
invalidates.

The consequence is a deadlock with a moving trigger point: bridge publications
succeed until enough uncounted bridge writes accumulate, and then terminal
`VERIFIED` finalization becomes unrunnable for every thread at once, with no
command available to a Loyal Opposition reviewer that clears it.

## Evidence

All observations are from a scheduled Loyal Opposition run on 2026-07-28 at HEAD
`4efcb0ee2d7e0e65c38f07ae381d294d5b908186`.

1. A `NO-GO` verdict published successfully through
   `scripts/gtkb_bridge_writer.py` `publish_lo_verdict` at
   `bridge/gtkb-wi5718-retired-session-role-authority-purge-002.md`. The registry
   was current at that moment.

2. A subsequent `VERIFIED` finalization on
   `gtkb-wi5657-terminal-finalization-recovery-v2` failed at
   `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2567`
   with:

   ```text
   RegistryAuthorizationError: bridge publication requires a current registry generation:
   {'current': False, 'missing_revisions': [],
    'stale': [{'id': 'bridge-versioned-files',
               'observed': 'sha256:480390e9b46afb11a4520b937b5d9408a1554f785b6c5e7dcca5c38f67bd29f3',
               'current': 'sha256:1077602425b45a698528f95397f811b0a8579a24fa4d210171b079e6665da160'}]}
   ```

3. `gt registry sync --json` reports `coherent: true`, `identity_state.current:
   true`, and `currentness.stale: []` with `audit_performed: false`. The
   read-only diagnostic therefore reports a healthy registry while the
   publication gate is blocked. A reviewer following the documented diagnostic
   path is told nothing is wrong.

4. `gt registry reconcile --json` returns `batch_records: []`,
   `admission_candidates: []`, and `audit_performed: false`. It does not refresh
   content observations.

5. `gt registry reconcile --audit --json` sets `audit_performed: true` and
   enumerates many `stale_content_observation` gaps, but returns
   `audit_complete: false`. It is a detector, not a writer.

6. `gt admin inventory refresh` is documented as "Check the declared SoT artifact
   inventory without ..." and does not record observations either.

7. The only writer is `append_passive_observation` in
   `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2256`.
   Its callers are `scripts/implementation_start_gate.py`, which mints an
   observation capability bound to a session id, tool event id, bridge id, and
   start-packet hash, and `scripts/registry_observation_hook.py`, whose `main()`
   reads a PostToolUse JSON payload from stdin and consumes that capability.
   There is no argument parser and no standalone invocation surface.

8. `.claude/skills/gtkb-verify/helpers/write_verdict.py` `finalize_verified_commit`
   calls `write_bridge_file(..., release_claim=False)` directly. That path
   performs a `write_bytes`, not a harness `Write` tool call, so no PostToolUse
   event is produced and no observation capability is ever minted or consumed.

## Deficiency Rationale

The registry-currentness gate is a reasonable control: publishing a governed
artifact against a stale view of the registry is a real risk. The defect is that
the control's precondition is consumed by the very operation it guards, and its
restoration path is reachable only from a different execution surface.

Three properties make this worse than an ordinary missing command:

- **It is silent until it is total.** Currentness degrades as untracked bridge
  files accumulate. Nothing warns as the margin erodes. When it crosses, every
  terminal `VERIFIED` in the repository is blocked simultaneously.
- **The diagnostic disagrees with the gate.** `gt registry sync` reports the
  registry healthy because its default currentness check is `audit_only` and
  does not perform the audit. A reviewer diagnosing the block is actively
  misdirected.
- **The only unblock is forgery.** A reviewer who understands the mechanism can
  see exactly which record is stale and exactly which function would fix it, but
  every legitimate caller requires a capability minted for a tool event that did
  not occur. Synthesizing one would fabricate governance evidence about an
  operation that never happened. Failing closed is correct, and it leaves the
  reviewer with no action.

This interacts badly with the by-reference finalization pattern. Threads such as
WI-5657 and WI-5659 exist specifically to close chains whose finalization was
previously interrupted. Each accumulates a long untracked chain while awaiting
terminal verification, and every version added moves the registry further from
current. The recovery mechanism enlarges the condition that blocks recovery.

## Impact

- Terminal `VERIFIED` finalization is currently unavailable to Loyal Opposition
  reviewers on this checkout. `gtkb-wi5657-terminal-finalization-recovery-v2`
  reached a fully verified state at `-009` with both mandatory preflights clean
  and could not be closed.
- Untracked bridge chains keep growing, which is the exact condition the
  WI-4871 untracked-terminal-VERIFIED durability guard exists to detect.
- Non-terminal verdicts still publish, so the failure is asymmetric: reviewers
  can block work but cannot complete it.

## Recommended Prime Action

Classification `adapt`. The control is sound; its restoration path is missing.

1. **Record the observation inside the governed writer.** `write_bridge_file`
   already mints a publication capability. Have the same transaction record the
   passive content observation for the artifact it just changed, so a governed
   publication leaves the registry current by construction. This is the
   narrowest fix and removes the deadlock at its source.
2. **Provide a reviewer-reachable refresh.** Add an explicit
   `gt registry observe --artifact <id>` (or equivalent) that records a passive
   content observation for a named registry artifact without requiring a
   synthetic tool event. Scope it to observation only; it must not amend
   declarations or identity rows.
3. **Make the diagnostic agree with the gate.** `gt registry sync` should either
   perform the audit its `currentness` field implies, or state explicitly that
   `current: null` means "not checked" rather than presenting a clean report.
   The present output actively misleads.
4. **Warn before the cliff.** Surface stale-observation count in
   `gt bridge state-report` or the doctor so the condition is visible while it is
   still a margin rather than a wall.

Option rationale: fixing the writer (1) is preferred over adding a manual
command (2) because a manual step reintroduces the same class of drift the
registry exists to prevent. (2) is still worth having as an operator escape
hatch. (3) is cheap and prevents the misdirection that cost this session most of
its diagnostic time. (4) converts a total outage into a warning.

## Secondary Observations

Recorded here because they were surfaced by the same registry reconciliation and
would otherwise be lost. Neither is blocking.

- **Stray cross-shell artifacts at the project root.** `gt registry reconcile`
  enumerates a file named `$null` (0 bytes, last written 2026-07-20, ignored via
  `.gitignore:587`) and a directory named `-p` (created 2026-07-01). Both are
  the signature of shell-syntax mismatches: a Bash-style `> $null` redirect
  evaluated where `$null` is not special, and a `mkdir -p` where `-p` is not a
  recognized flag. They are inert but they pollute registry traversal and
  suggest commands elsewhere in the toolchain silently did not do what their
  author intended.
- **Staging-directory proliferation under `.gtkb-state/`.** The directory holds
  at least a dozen near-synonymous bridge staging surfaces, including
  `bridge-drafts`, `bridge-propose-drafts`, `bridge-report-drafts`,
  `bridge-impl-reports`, `bridge-implementation-reports`, `bridge-verdicts`,
  `bridge-verdict-drafts`, `verdict-drafts`, `verdicts-pending`,
  `lo-verdict-bodies`, `lo-verdict-drafts`, and `lo-verdict-scratch`. A reviewer
  choosing where to stage a verdict body has no principled basis for the choice.
  This compounds the discoverability problem already filed at
  `bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md`.

## Relationship To Existing Advisories

This advisory does not duplicate the three finalization advisories already on
disk. Each addresses a different failure:

- `gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`
  concerns an interrupted transaction that strands a published terminal verdict.
  Here nothing was published; the gate refused before any write.
- `gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md` concerns
  discoverability of the legal authoring path. Here the path was found and
  followed correctly; the registry precondition blocked it.
- `gtkb-lo-verify-helper-path-drift-and-verdict-concurrency-advisory-001.md`
  concerns a documented helper path that does not exist. Here the helper exists
  and executes.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. Recommendation 1 modifies `scripts/gtkb_bridge_writer.py` and the registry
control plane; recommendations 2 through 4 add CLI and reporting surfaces.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to:

1. Should the governed writer record its own passive observation (option 1), or
   should observation remain strictly tied to harness tool events with an
   operator command as the only escape hatch (option 2)? This is a governance
   question about whether observation provenance must always name a real tool
   event.
2. Is a reviewer-invocable observation command acceptable, given that it records
   an observation with no tool-event provenance, and if so what provenance
   should it record instead?
3. Should stale-observation count become a blocking doctor check, a warning, or
   reporting only?

### Required durable owner decisions

- The chosen restoration mechanism for registry currentness.
- Whether observation records may exist without tool-event provenance.
- The severity class for the pre-cliff warning surface.

## Owner Decision Needed

Yes, but not urgently, and not before Prime Builder runs the grilling gate above.
The substantive owner decision is question 1: whether observation provenance must
always name a real harness tool event, or whether a governed in-process writer
may record its own passive observation. That choice determines which of the four
recommended actions is the primary fix and which are supporting. No owner
decision is required to record this advisory.

## Owner Action Required

None immediately. This advisory records the condition and does not itself
authorize implementation. The terminal finalization of
`gtkb-wi5657-terminal-finalization-recovery-v2` remains blocked until the
registry-currentness condition is resolved by some path; its `-009` report is
otherwise fully verified and needs no further review work.

## Skills applied

gtkb-bridge, gtkb-advisory-proposal, gtkb-lo-opportunity-radar

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
