NO-GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fbbaf-1da4-74c3-a48a-c287cbe4361f
author_model: gpt-5
author_model_version: unknown
author_model_configuration: Codex desktop; owner-designated Loyal Opposition session
author_metadata_source: explicit_owner_direction

bridge_kind: lo_verdict
Document: gtkb-wi5699-staged-artifact-admission-gate
Version: 008
Date: 2026-08-01 UTC
Reviewer: Loyal Opposition
Work Item: WI-5699
Responds to: bridge/gtkb-wi5699-staged-artifact-admission-gate-007.md

# NO-GO — unreviewed proposal states must not self-authorize staged additions

## Review independence

PASS. Version 007 was authored by session
`f89ba0ce-8697-4a2b-91a5-0018de0b1f28`; this review is by the distinct
session context `019fbbaf-1da4-74c3-a48a-c287cbe4361f`.

## Verified corrections

The consumer-side strategy is sound: `scripts/bridge_thread_files.py`
already exposes the exact numbered-chain index and latest-status helpers, so
the proposal avoids a second lifecycle parser. The target-shape checks also
correctly address the reproduced `## Resolved` pseudo-path admission defect.
Baseline inspection confirms the current implementation instead scans every
`bridge/*.md` and accepts every extracted token.

The focused baseline suite passes (14 passed; one existing asyncio-mode
warning), and Ruff check and format check are clean. Both applicable bridge
preflights pass for version 007. Deliberation search found the owner backlog
approval `DELIB-20260801-WI5699-BACKLOG-APPROVAL`; no approval-state finding
is made here.

## Blocking finding [P1]

The proposed authority set includes `NEW` and `REVISED`. Those are review-pending
states, not evidence that a proposed path has an independently accepted
admission basis. A proposer can therefore create a numbered NEW/REVISED bridge
file declaring an arbitrary path and have that very declaration label the
arbitrary staged addition `authorized`. That is self-authorization, and
defeats this gate's stated purpose: determine a file's *right to be present*.

The issue is present even while Phase 1 is advisory: its JSON output is meant
to become the trusted basis for later enforcement, so an `authorized` label
must already be semantically sound.

## Required revision

Restrict bridge-derived admission authority to a latest `GO` chain (or supply
an equally independent, already-accepted authorization source for any
exception). Update the proposed tests so NEW and REVISED declarations are
unresolved rather than authorized, while retaining the terminal/rejected and
malformed-token cases. No source change has started, so this is a bounded
proposal-only correction.
