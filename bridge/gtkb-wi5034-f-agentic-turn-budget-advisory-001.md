ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c0dc7bd5-3e1a-4215-921d-bc79d92a36be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; Loyal Opposition dispatcher watch

bridge_kind: governance_advisory
Document: gtkb-wi5034-f-agentic-turn-budget-advisory
Version: 001 (ADVISORY)
Author: Loyal Opposition (Claude, interactive dispatcher watch)
Date: 2026-07-06 UTC
Work Item: WI-5034

# Advisory: F harness exhausts its agentic bridge-review turn budget

## Source
Dispatcher watch (2026-07-06), Loyal Opposition harness B. Cited records: WI-5034; DELIB-F-OPENROUTER-GUARDRAIL-INTERFERENCE-20260705; DELIB-F-GUARDRAIL-REMEDIATION-REENABLE-20260705; DELIB-F-POSTFIX-VERIFICATION-SSL-WATCH-20260706; DELIB-F-MAXTURN-PERSISTS-REDISABLE-20260706. Worker evidence: F run stderr on 2026-07-06T00:50:15Z and 00:51:09Z ("max-turn exhaustion before final assistant text").

## Claim
The F provider-backed low-cost Loyal Opposition harness cannot complete an agentic bridge-review within its turn/step budget: every dispatch ends in max-turn exhaustion (no final assistant text, exit 1), producing zero verdicts. The failure persisted AFTER the owner disabled the F provider workspace guardrails, so guardrail interference was not the determinant; the agentic bridge-review loop and model are the cause. F is 0-for-all and is currently re-disabled for dispatch. D covers the low-cost LO role with exit-0 verdicts; B and C are healthy.

## Owner Decision Needed
No owner decision is required to file this advisory or to keep F disabled. A future owner disposition may choose among: (a) fund a fix per the Recommended Prime Action; (b) leave F disabled indefinitely (D already covers the low-cost LO role, so there is no capacity gap); or (c) retire F from the harness registry.

## Recommended Prime Action
1. Verify that F max-turn exhaustion persists with guardrails off (the agentic bridge-review loop, not provider guardrails, is the cause).
2. Determine the optimal resolution among: a materially larger step/turn budget for the F shim; a different F model capable of agentic bridge-review within budget; or classifying F current model as unsuitable for agentic dispatch.
3. Author an implementation proposal for WI-5034. Do NOT re-enable F until a fix produces a successful verdict under the max_items=1 cap.

## Classification Slot
Defect-remediation advisory (dispatcher / harness reliability). Prime Builder disposition to be recorded: adopt (fix) / defer / reject (retire F). Prime Builder converts this advisory into a normal implementation proposal for WI-5034, or records a defer/retire deliberation.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
