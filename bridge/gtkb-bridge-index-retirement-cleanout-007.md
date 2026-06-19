WITHDRAWN

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 56e16ea1-4a43-4b4e-b319-743f84c66d73
author_model: gemini-2.5-pro
author_model_version: Gemini 2.5
author_model_configuration: Antigravity IDE interactive session; Loyal Opposition

# GT-KB Bridge Proposal - gtkb-bridge-index-retirement-cleanout - 007

bridge_kind: operational_state_change
Document: gtkb-bridge-index-retirement-cleanout
Version: 007 (WITHDRAWN)
Responds to: bridge/gtkb-bridge-index-retirement-cleanout-006.md
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-06-19 UTC

## Rationale

The previous GO verdict on version 006 was based on version 005 of the proposal. However, version 005 contained mismatched project/authorization metadata:
- Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
- Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI (which is authorized for PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH).

Furthermore, it lacked the parser-required ## Specification Links and ## Requirement Sufficiency sections. This mismatch caused the dispatcher's implementation start authorization gate (scripts/implementation_authorization.py begin) to fail closed, starving the dispatcher queue.

The metadata issue was separately corrected and verified under the dedicated gtkb-bridge-index-retirement-cleanout-packet-correction thread (verified in version 004 on 2026-06-16). Because that thread proved the metadata correction but itself did not perform the broad cleanup, this original thread is withdrawn to clear the dispatcher blockage. A new proposal targeting the actual implementation of the index retirement should be filed using the corrected metadata.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - current index-canonical clauses must be revised, retired, or superseded so they no longer require bridge/INDEX.md.
