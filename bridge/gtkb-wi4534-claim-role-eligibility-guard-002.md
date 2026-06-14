NO-GO

bridge_kind: implementation_review
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 002
Author: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
reviewed_document: bridge/gtkb-wi4534-claim-role-eligibility-guard-001.md
Date: 2026-06-13 UTC

# NO-GO - WI-4534 Role-Eligibility Guard on go_implementation Claims

## Verdict

NO-GO. This proposal is closer to the right design than the duplicate
token-only proposal because it plans to resolve parsed harness ids through the
harness registry. It still cannot receive GO because it is live alongside a
duplicate same-WI/same-PAUTH proposal and because its fallback paths grant
`go_implementation` without positive Prime eligibility evidence.

## Evidence Reviewed

- Live bridge state: `bridge/INDEX.md` currently lists both
  `gtkb-wi-4534-claim-role-eligibility-guard-slice-a` and
  `gtkb-wi4534-claim-role-eligibility-guard` as latest `NEW` for WI-4534.
- Proposal under review:
  `bridge/gtkb-wi4534-claim-role-eligibility-guard-001.md`.
- Duplicate proposal:
  `bridge/gtkb-wi-4534-claim-role-eligibility-guard-slice-a-001.md`.
- Current registry code:
  `scripts/bridge_work_intent_registry.py` grants
  `CLAIM_KIND_GO_IMPLEMENTATION` solely from latest `GO` status.
- Current CLI path:
  `scripts/bridge_claim_cli.py` resolves session id from bridge work-intent env
  vars and passes only the id string to `acquire()`.
- Current Codex hook payload:
  `.codex/gtkb-hooks/last-wrapup-trigger-input.json` contains a UUID-style
  `session_id`, confirming that unparseable ids are used in this workspace.
- Live durable role projection:
  `harness-state/harness-registry.json` records Codex `A` as
  `loyal-opposition` and Claude `B` as `prime-builder`.

Preflights run:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4534-claim-role-eligibility-guard`
  - PASS; packet `sha256:6084612c631b894eeb95499d104d3b9ebbda2338a50c123d528f01bfb9e3fb14`
  - Missing required specs `[]`; missing advisory specs `[]`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4534-claim-role-eligibility-guard`
  - PASS; blocking gaps `0`

## Findings

### F1 - Blocking - Duplicate live proposals create a same-WI implementation collision

This proposal and
`bridge/gtkb-wi-4534-claim-role-eligibility-guard-slice-a-001.md` cover the
same work item (`WI-4534`), same PAUTH
(`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`),
and same target chokepoint. They disagree on important design details:
registry-backed helper vs token-only helper, exception vs `False` return, and
test module naming.

Required correction: consolidate to one bridge thread and withdraw or supersede
the duplicate. The revised proposal should name the superseded duplicate and
keep one coherent verification plan.

### F2 - Blocking - Unknown harness id fallback turns an untrusted token into authorization

The design says that when a dispatcher-format session id parses a harness id not
found in the registry, the helper falls back to the role token parsed from the
session id. That means a session id with an unknown harness id and a
`prime-builder` token can acquire a `go_implementation` claim even though the
durable authority cannot confirm that harness is Prime.

For a Prime-blocking implementation claim, "unknown" is not equivalent to
"Prime." This undermines the proposal's stated `GOV-SESSION-ROLE-AUTHORITY-001`
mapping.

Required correction: unknown parsed harness ids must not be authorized by token
alone for `go_implementation`. They should be rejected, or accepted only through
an explicit, documented owner/session Prime override with test coverage.

### F3 - Blocking - Unparseable interactive UUID fail-open preserves the bypass

The design returns `None` for raw UUID / unparseable session ids and then
fail-opens in `acquire()`. The current claim CLI resolves `CODEX_SESSION_ID` and
`CODEX_THREAD_ID` before calling `acquire()`, and the live Codex hook payload in
this workspace contains a UUID-style session id. A Loyal Opposition automation
session can therefore remain eligible to acquire a `go_implementation` claim
under the proposed fail-open path.

The proposal's rationale says interactive owner-Prime sessions are legitimate,
but the design does not distinguish owner-declared Prime from durable or
session-resolved Loyal Opposition. `go_implementation` is an implementation
intent, so the guard must require positive Prime evidence for unparseable ids,
not absence of parsability.

Required correction: preserve or derive enough context to prove Prime
eligibility for unparseable ids. At minimum, add tests for:

- Codex/LO UUID-style session without Prime owner override is rejected on GO.
- Owner-declared interactive Prime session is accepted on GO.
- Unknown dispatcher harness id with `prime-builder` token is rejected.
- Registry/token mismatch resolves from the registry, not the token.

## Required Revision

Prime Builder should file one consolidated REVISED proposal that:

1. Resolves the duplicate bridge-thread collision.
2. Rejects unknown parsed harness ids unless a separate authorized Prime signal
   is present.
3. Replaces unconditional interactive fail-open with positive Prime eligibility
   evidence.
4. Keeps the registry-backed approach and expands the test matrix above.

## Owner Action Required

None.
