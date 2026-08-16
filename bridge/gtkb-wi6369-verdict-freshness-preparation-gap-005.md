NEW
::init gtkb lo
::open build

# gtkb-wi6369-verdict-freshness-preparation-gap — Post-implementation report

bridge_kind: implementation_report
Document: gtkb-wi6369-verdict-freshness-preparation-gap
Version: 005
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: ad641b84-988f-4b49-bd56-25cb521d078c
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-16 UTC

Responds to: bridge/gtkb-wi6369-verdict-freshness-preparation-gap-004.md

Work Item: WI-6369
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-3
Project Authorization: PAUTH-GET-HEALTHY-PHASE-3-20260815

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This report performs no MemBase mutation and no `groundtruth.db` write.

---

## Implementation Provenance — Read This First

**This session did not write this code.** The change was found already complete
and uncommitted in the shared worktree by session
`ad641b84-988f-4b49-bd56-25cb521d078c`, which verified it and is filing this
report so the thread can progress.

The implementing session is **unknown to this session**. Both target files were
`M` in `git status` with the change in place, the thread was still at `-004 GO`
with no report filed, and no work-intent claim was held — the
implementation-start packet minted cleanly, which is the authoritative
contention check.

Stated plainly rather than implied, so the verifier weighs the evidence below as
*verification by an independent session*, not as authorship. Everything in
§ Verification Performed was executed by this session; nothing is carried over
from an implementing session's claims, because none were available.

This is the second instance of the same pattern this session (see also WI-6444):
GO'd work implemented and left unreported, plausibly because the finalization
path was blocked.

## What Is Implemented

Exactly the approved change.

**1. `scripts/gtkb_bridge_writer.py`** — `publish_lo_verdict()` now prepares the
verdict candidate before running the guards, mirroring `write_bridge_file`. The
block sits between the `target` assignment (`:1466`) and
`_run_provider_verdict_guards` (`:1489`), importing
`verdict_candidate_needs_preparation` / `prepare_verdict_candidate` and failing
closed via `BridgeComplianceError`.

It carries an explanatory comment naming WI-5554 / WI-6369 and stating the
convergence argument: preparation is what stamps a self-consistent
`candidate_evidence_hash`, so without it the freshness guard compares an
author-supplied hash against a hash over *unprepared* content — which no author
can reproduce, because preparation is the step that makes any value
self-consistent. Preparation is idempotent, so the second pass inside
`write_bridge_file` is a no-op.

**2. `platform_tests/scripts/test_gtkb_bridge_writer.py`** —
`test_write_bridge_file_rejects_envelope_for_unmapped_status` is marked
`@pytest.mark.known_debt(...)` at `:917`, citing WI-6392 per the proposal.

## Why This Matters

Loyal Opposition verdict publication was failing platform-wide on a
`candidate_evidence_hash` mismatch that **no author could satisfy** — stamping
the demanded value did not converge. The two publication paths had divergent
pipelines; Path B (`publish_lo_verdict`) lacked the preparation step Path A
(`write_bridge_file`) already performed.

This is the publication half of the terminal-state blockage. The gate half was
addressed under WI-6365 earlier this session, where the bridge-compliance gate's
demand for same-transaction evidence — impossible under commit-then-verdict
canon — was replaced with acceptance of post-commit evidence. Neither alone
restores terminal state; both are necessary.

## Verification Performed By This Session

```text
python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --no-header
    -> 1 failed, 56 passed, 1 warning in 9.72s
       GT-KB test-debt summary (WI-6222): new failures 0
```

**The single failure is the expected one.** It is
`test_write_bridge_file_rejects_envelope_for_unmapped_status` — precisely the
test item 2 marks as `known_debt` citing WI-6392 — and the debt-aware runner
reports **`new failures: 0`**. The suite is green against its debt baseline.

Independent corroboration that WI-6392 is a live condition, not a paper
exemption: this session hit it directly while trying to file a `WITHDRAWN`
after-action record and was refused with `bridge status WITHDRAWN has no formal
responder-role envelope mapping`. The marked test is describing a real gap.

## Spec-to-Test Mapping

| Specification | Test | Observed |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` — verdict publication must converge | full `test_gtkb_bridge_writer.py` module (56 passing) | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — path A / path B parity | preparation block present in both publication paths, read at `:1476-1487` and `:1200-1211` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived evidence executed | commands above | PASS |
| Known-debt discipline — the exempted test is declared, not silently skipped | `known_debt` mark at `:917`; runner reports `new failures: 0` | PASS |

## Not Re-Verified, And Why

`ruff check` / `ruff format --check` were **not** run against these two files by
this session. The edits were pre-existing and unattributed, and this session did
not modify either file, so a formatting gate would attest to another session's
work rather than to any change made here. Flagged as a gap for the verifier
rather than presented as clean: if the verifier requires the code-quality gates
on this diff, they should be run as part of verification.

## Acceptance Criteria Check

| Criterion from `-003` | Met |
|---|---|
| Preparation block added to `publish_lo_verdict` between `target` and the guards | yes — `:1475-1487` |
| Imports `verdict_candidate_needs_preparation` / `prepare_verdict_candidate` | yes |
| Fails closed via `BridgeComplianceError` | yes |
| `test_write_bridge_file_rejects_envelope_for_unmapped_status` marked `known_debt` citing WI-6392 | yes — `:917` |
| No regression in the module | yes — 56 passed, `new failures: 0` |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication integrity and the audit
  trail that verdict publication carries.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — § Spec-to-Test Mapping.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the metadata triple.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`;
  `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` — filed under
  `PAUTH-GET-HEALTHY-PHASE-3-20260815`; no PAUTH created or relaxed.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every line reference and test result here
  is a fresh read taken this session.
- `GOV-STANDING-BACKLOG-001` — WI-6369 governs; WI-6392 is the cited debt.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets in-root.
- `SPEC-1662` (GOV-18) — assertions are behavioural.

## Prior Deliberations

- **WI-5554** — cited in the implementation comment as the companion
  verdict-candidate preparation work.
- **WI-6392** — the known-debt citation for the envelope/unmapped-status gap;
  independently reproduced by this session.
- **WI-6365** — the gate half of the same terminal-state blockage; implemented
  earlier this session, report at `-005`.
- **WI-6140 / WI-6342** — the `packet_hash` circularity family this
  non-convergence belongs to.
- **WI-6357** — measures the finalization pipeline at `13 candidate(s), 0 ready`.
- **WI-6444** — the other instance this session found of GO'd work implemented
  but unreported.

## Risk / Rollback

**Risk: double preparation.** Addressed by idempotency — `write_bridge_file`
performs the same preparation, and the second pass is a no-op. The comment states
this and the 56 passing tests exercise both paths.

**Risk: this report attests to unattributed work.** Mitigated by verifying rather
than accepting: the module was executed by this session and the single failure
explained against the debt baseline. The unrun formatting gates are disclosed
above rather than assumed clean.

**Rollback.** Remove the preparation block from `publish_lo_verdict` and the
`known_debt` mark; both are additive with no migration or persisted state.

## Owner Decisions / Input

No new owner decision was required or taken. Implementation proceeds on the
`-004` GO within `PAUTH-GET-HEALTHY-PHASE-3-20260815`.

The session directive was to spend remaining capacity on the highest-impact
PB-actionable items in the GET HEALTHY PHASE 3 authorization scope. WI-6369 was
selected because it is the publication half of the terminal-state blockage whose
gate half was addressed earlier in the same session, and because live chain-state
and contention checks showed it GO'd, unclaimed, and unreported.

## Recommended Commit Type

`fix` — repairs a publication path that could not converge. No new capability
surface. Not `feat`, not `chore` (runtime behaviour changes), not `test` (source
changed too).

Recommended commit type: `fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
