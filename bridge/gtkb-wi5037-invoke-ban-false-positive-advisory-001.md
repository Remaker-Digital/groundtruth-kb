ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c0dc7bd5-3e1a-4215-921d-bc79d92a36be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; Loyal Opposition dispatcher watch

bridge_kind: governance_advisory
Document: gtkb-wi5037-invoke-ban-false-positive-advisory
Version: 001 (ADVISORY)
Author: Loyal Opposition (Claude, interactive dispatcher watch)
Date: 2026-07-06 UTC
Work Item: WI-5037

# Advisory: invoke-ban hook false-positives on governed gt commands

## Source
Dispatcher watch (2026-07-05/06), Loyal Opposition harness B. Cited: WI-5037; SPEC-INTAKE-21c5b3; DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN.

## Claim
The DIRECT-HARNESS-INVOKE-BAN PreToolUse hook blocks legitimate governed gt commands whose text contains a provider proper noun adjacent to a routing/dispatch verb. Observed three times this watch: it blocked a status command piped to a text filter listing provider names, and a deliberations add whose content described provider behavior with routing verbs; both re-ran after removing the trigger phrasing. It intermittently blocks legitimate diagnostic and capture operations that only discuss provider behavior.

## Owner Decision Needed
No owner decision is required to file. Owner may prioritize relative to other hook-hygiene work.

## Recommended Prime Action
1. Verify the hook match pattern.
2. Narrow it to actual cross-harness process spawning (the behavior the ban targets) rather than prose or CLI-argument text that only names a provider.
3. Author an implementation proposal for WI-5037 with a hook unit test asserting that governed gt status/deliberation/backlog commands naming a provider in prose or args are not blocked.

## Classification Slot
Defect-remediation advisory (governance hook). Prime Builder disposition: adopt / defer. Convert into a normal implementation proposal for WI-5037.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
