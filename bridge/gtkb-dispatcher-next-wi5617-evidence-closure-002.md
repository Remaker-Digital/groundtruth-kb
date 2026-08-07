WITHDRAWN
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 345fab55-33fc-40c1-933b-d2413de27158
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; activity build

bridge_kind: prime_withdrawal
Document: gtkb-dispatcher-next-wi5617-evidence-closure
Version: 002
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-dispatcher-next-wi5617-evidence-closure-001.md

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5617

# WITHDRAWN — superseded by a concurrent thread on owner decision

## Reason

Duplicate work. While this thread was being drafted, a second interactive
Prime Builder session (`author_session_context_id`
`7c5bf02a-db61-459e-9321-695a31696526`) independently filed
`bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-001.md` against the
same work item (WI-5617), the same project authorization
(`PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`), and **the same target file**
`config/dispatcher-next/requirements-spike.txt`.

The owner selected "Merge into the Goose thread" via AskUserQuestion on
2026-08-06 (options presented: merge into the concurrent thread; keep this one
and withdraw that one; let Loyal Opposition arbitrate; merge the concurrent
scope into this one). This thread is withdrawn accordingly.

`WITHDRAWN` is used rather than `DEFERRED` because this thread is terminal: its
implementation scope is fully absorbed elsewhere and it will not resume. Per
the transition table in `.claude/rules/file-bridge-protocol.md`, `NEW ->
WITHDRAWN` is lawful, and this file is append-only evidence, not a deletion.

## Independent convergence (corroboration, not coincidence)

Both sessions, working without shared context, arrived at the same relocated
path `config/dispatcher-next/requirements-spike.txt` rather than the cohort's
original `groundtruth-kb/requirements-dispatcher-next-spike.txt`. That
convergence is corroborating evidence that the relocation is correct, and the
reviewing role should treat it as such when reviewing the surviving thread.

## Findings that MUST carry forward

This withdrawal must not discard the evidence that motivated it. The surviving
thread does not currently state these; they are recorded here so the audit trail
retains them and the reviewing role can require them.

1. **The original cohort path is unauthorizable, not merely absent.**
   `TARGET_PATH_RE` (`scripts/implementation_authorization.py:122`) recognizes
   only `groundtruth-kb/src/**` and `groundtruth-kb/tests/**` under that tree, so
   `groundtruth-kb/requirements-dispatcher-next-spike.txt` classifies
   `unclassified`; no PAUTH permits that class. Measured on this thread's own
   draft: original path -> `preflight_passed: false`, exit 5, PAUTH denial for
   both `implementation_packet_create` and `implementation_start`; relocated path
   -> `mutation_class: configuration`, `allowed: true`, `preflight_passed: true`,
   exit 0. This is why the predecessor chain could never close.

2. **Two of WI-5617's three recorded blockers are false.** Project
   `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE` is `active` (v3,
   2026-07-31T03:12:01Z), not retired. `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`
   is active, unexpired, and explicitly enumerates WI-5617..WI-5629, so no
   "widening into whole-project authority" is required.

3. **The parking decision rested on an already-false premise.**
   `bridge/gtkb-dispatcher-next-foundation-spike-011.md` selected recovery route
   "A (Rehome)" because the parent project was retired; its author session is
   `G-2026-07-31T07-41-38Z`, roughly four and a half hours after the project was
   reactivated at 03:12:01Z.

4. **The foundation is delivered and green.** `python -m pytest
   platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q
   --no-header` -> `11 passed`, emitting `DISPATCHER_NEXT_ADOPTION_MANIFEST` with
   `"outcome":"adopt_dbos_a2a"` and all six predicates true. The five other
   cohort targets (~2,949 lines) are committed and clean.

5. **Observed dependency values** for the pin file: `dbos==2.27.0`,
   `a2a-sdk==1.1.1`, python 3.14.0 — from the manifest's `python_3_14`
   `observed_value`, cross-checked against `pip show` in `groundtruth-kb/.venv`.
   These are transcribed observations; no version should be chosen by an author.

## Work NOT absorbed by the surviving thread

The surviving thread declares `kb_mutation_in_scope: false`, so it does **not**
correct `WI-5617.status_detail`, which still asserts the retired-project,
PAUTH-widening, and "NO-GO v010" claims falsified above. That correction is
re-filed separately per the owner's decision. Until it lands, WI-5617's
narrative remains contradicted by canonical project, PAUTH, and bridge rows.

Also still open and unowned by either thread:

- **DECISION DEFERRED** — teach the authorization classifier to recognize
  dependency manifests (`requirements*.txt`) as `configuration`; captured as a
  standing backlog item, not performed here.
- **DECISION DEFERRED** — sweep the remaining 11 open Dispatcher Next work items
  for the same stale-retirement narrative class.

## Non-Impairment

No file, MemBase row, dispatcher state, or TAFE state was mutated by this
thread. The legacy dispatcher remains disabled per the standing owner directive.
`bridge/gtkb-dispatcher-next-wi5617-evidence-closure-001.md` is retained
unmodified as append-only audit history.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
