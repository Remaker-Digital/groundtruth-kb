---
name: S259 session summary
description: Manual testing defect collection, async email-bridge escalation, bridge autonomy fix, identity/WhatsApp investigations
type: project
---

S259 (2026-04-04 to 2026-04-05). Branch: codex/groundtruth-control-surface.

**Two commits:** 9b263613 (defect remediation + escalation, 20 files), 0cf02884 (bridge autonomy, 5 files).

**Defect collection:** 15 defects from owner manual testing on staging v1.98.80. 10 work items created (WI-3030..WI-3039). 9 resolved in-session.

**Key fixes:** focus-visible for widget (:focus-visible guard in 5 components), coming-soon removal (languages + integrations), agent logo replacement ({r} monogram), Conversation Preview uses draft config, admin consent suppression, saved configs sorting, panel dimension preview resize.

**Escalation pipeline:** 3 Codex review rounds. v1 NO-GO (live handoff). v2 GO direction (async email-bridge). v2.1 final fix (idempotent send path). Owner decision: async-only, no live handoff. Email bridge sends transcript to customer + agent (ACS replyTo). Chat continues after escalation. Concurrency caps removed.

**Bridge autonomy:** Codex proposal accepted (4 phases). Phase A: rglob crash fix (absolute paths). Phase B: scheduled tasks canonical runtime. Phase C: recovering state + consecutive error tracking. Phase D: autonomy proof (valid message processed, malformed handled). Both workers HEALTHY.

**Owner decisions (future roadmap):** Phone as primary identity (ACS SMS), WhatsApp live escalation (merchant WhatsApp client, customer chooses channel), canonical identity model needed before implementation.

**Pending:** WI-3030 Phase 2 (AI addresses question before escalation). Build + deploy for re-test. INV-1/INV-2 implementation.
