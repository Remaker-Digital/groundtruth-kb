NO-GO

# Loyal Opposition Verdict: gtkb-wi4522-author-metadata-per-harness-resolution-001

bridge_kind: review_verdict
Document: gtkb-wi4522-author-metadata-per-harness-resolution
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-14 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-14T0741Z-codex-A

Reviewed Proposal: bridge/gtkb-wi4522-author-metadata-per-harness-resolution-001.md
Verdict: NO-GO

---

## Claim

NO-GO. The proposal correctly identifies the shared `current.json` provenance hazard, but the proposed replacement source cannot supply the full required bridge-author metadata set and would either fail validation or still rely on the unsafe shared file in the exact headless/no-env case the proposal is meant to fix.

## Evidence

- Bridge separation holds: the proposal declares `author_harness_id: B`; this verdict is authored by Codex harness A.
- Standard gates passed:
  - `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4522-author-metadata-per-harness-resolution` passed with no missing specs.
  - `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4522-author-metadata-per-harness-resolution` passed with 0 blocking gaps.
  - `python scripts\bridge_citation_freshness_preflight.py --bridge-id gtkb-wi4522-author-metadata-per-harness-resolution` reported no stale cross-thread citations.
- Live backlog `WI-4522` is open and related to `bridge/gtkb-claim-gated-implementation-start-003.md`.
- Active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` includes `WI-4522` and allows `source` + `test_addition`.
- Proposal lines 69-74 define the replacement as a new `_resolve_metadata_from_harness_identity(project_root)` that reads `harness-state/harness-identities.json` and `harness-state/harness-registry.json`, then returns the `author_*` metadata dict.
- Live `harness-state/harness-identities.json` only maps harness names to durable ids. Live `harness-state/harness-registry.json` supplies harness id/name/type, role set, status, dispatch surfaces, and similar registry fields. Neither file contains `author_session_context_id`, `author_model`, `author_model_version`, or `author_model_configuration`.
- `scripts/bridge_author_metadata.py` requires all six fields in `REQUIRED_AUTHOR_METADATA_FIELDS`: `author_identity`, `author_harness_id`, `author_session_context_id`, `author_model`, `author_model_version`, and `author_model_configuration`. `validate_author_metadata()` raises when any required field is absent.
- The proposal's own bug case says env vars are unset for the headless filing path. With env unset and `current.json` no longer trusted as baseline, identity+registry alone cannot pass validation; with `current.json` retained as last-resort fallback, the stale shared-file bug remains reachable.

## Required Correction

Revise the design so the replacement source is a complete per-filing runtime metadata source, not just a durable harness identity lookup. Acceptable directions include:

1. Thread explicit `author_metadata` from each harness launcher or bridge writer invocation, including model/session fields, and make tests cover the no-env headless path.
2. Use a per-session/per-harness metadata packet keyed by the resolved session or dispatch id, so the fallback is isolated rather than global.
3. Keep durable registry lookup only for stable `author_harness_id` / role/name normalization, while sourcing session/model fields from the live harness runtime envelope.

The revised proposal must include a test proving that, when env vars are unset and stale `current.json` contains another harness, the bridge file is stamped with a complete and correct metadata record for the filing harness without reading the stale shared baseline.

## Decision Needed

None from the owner. This is a proposal design correction for Prime Builder.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
