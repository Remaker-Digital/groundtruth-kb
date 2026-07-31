ADVISORY

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# Advisory — WI-5688 Requires an Independent Correction to a Premature GO

bridge_kind: governance_advisory
Document: gtkb-lo-wi5688-premature-go-correction-advisory
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-07-29 UTC

## Source

Post-publication independent read-only analysis of
`bridge/gtkb-wi5688-doctor-crash-fastlane-003.md` and the source-level
proposal it describes. The current same-session GO is
`bridge/gtkb-wi5688-doctor-crash-fastlane-004.md`.

## Claim

WI-5688 revision 003 still fails its stated missing-output acceptance path.
It proposes `text=False` followed by
`completed.stdout.decode("utf-8", errors="replace")`, while also promising
an exit-zero missing-output warning. If `completed.stdout is None`, the direct
`.decode()` throws before that warning branch runs. `errors="replace"` handles
invalid bytes, not a missing value. The planned absent-output regression is
therefore insufficient unless it proves no exception and no sweep-complete
claim.

The GO at version 004 was published before this independent evidence arrived.
This session cannot formally review or supersede its own GO; bridge review
independence is session-context based. The live GO must not be treated as
implementation permission until a distinct Loyal Opposition session files a
governed correction.

## Evidence

- `gtkb-wi5688-doctor-crash-fastlane-003.md` Corrected Design step 1 invokes
  `.decode()` directly; step 3 requires a warning for absent/unusable output.
- The exact `stdout=None` shape was the original production crash at
  `doctor.py:2603`, so this is a required, not hypothetical, failure path.
- The current source at `doctor.py:2576-2603` remains unchanged and confirms
  the target behavior is unimplemented. The focused four-test baseline passed,
  but it contains no revision-003 absent-output regression yet.
- Duplicate search found only the WI-5688 proposal/history references; no
  current ADVISORY captures this post-GO session-independence correction need.

## Impact

Implementing the current GO would replace one `stdout=None` crash with another
at the newly proposed decode boundary, while falsely claiming the no-output
path is warning-safe. A same-session NO-GO would be invalid self-review, so
silently writing one would compound the governance defect.

## Recommended Prime Action

Do not begin WI-5688 implementation under GO v004. Obtain a distinct Loyal
Opposition session to review the recorded defect and publish the next governed
verdict. The corrected revision must guard `None`/non-bytes before decode and
separately test invalid UTF-8 bytes, absent output, and exit-zero empty output
as applicable. Continue to leave the WI-5740 sibling scope untouched.

## Prior Deliberations

- `DELIB-202667528` records the fast-lane routing, not a waiver of independent
  review or the missing-output acceptance criterion.
- `DELIB-202667193` and `DELIB-20260724-WI5668-SEVERITY-CONTRACT` require
  warning fidelity while references remain.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` retains the normal GO, start,
  report, and independent VERIFIED gates.

## Owner Decision Needed

The owner must arrange or authorize a distinct Loyal Opposition session context
to issue the corrective governed verdict; this current LO session is ineligible
to overwrite its own GO. No source or project mutation is requested.

## Classification Slot

- Classification: `adapt`.
- Implementation implied: no until the distinct-session correction completes.

## Non-Approval Statement

This ADVISORY is not implementation approval and does not itself supersede GO
v004. It authorizes no source/test edit, claim, implementation-start packet,
dispatcher action, or bridge-status bypass.
