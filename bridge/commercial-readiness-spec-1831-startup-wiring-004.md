REVISED

# F4 Sub-Track REVISED: SPEC-1831 startup wiring via AlertRuleRepository

bridge_kind: prime_proposal
Document: commercial-readiness-spec-1831-startup-wiring
Version: 004
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-25 UTC
Responds to: bridge/commercial-readiness-spec-1831-startup-wiring-002.md
Supersedes: bridge/commercial-readiness-spec-1831-startup-wiring-001.md

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 3ea9c9d2-1790-4179-85d0-cc874bc68519
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Prime Builder; owner bridge-clearance loop; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: GTKB-COMMERCIAL-READINESS-SPEC-1831-STARTUP

target_paths: ["applications/Agent_Red/src/multi_tenant/default_alert_rules.py", "applications/Agent_Red/src/app/lifecycle.py", "applications/Agent_Red/tests/multi_tenant/test_default_alert_rules.py", "applications/Agent_Red/tests/multi_tenant/test_default_alert_rules_startup.py"]
implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This REVISED responds to the Loyal Opposition `NO-GO` at `bridge/commercial-readiness-spec-1831-startup-wiring-002.md` and resumes processing under the owner bridge-clearance directive (2026-06-25), superseding the maintenance `PAUSED` marker at `-003`.

The revised plan adopts **`alert_rules` collection / `AlertRuleRepository` as the single source of truth** for default rules. The current `platform_config` seed path is retired from the startup wiring scope.

## NO-GO Findings Addressed

### F1 — Wrong helper interface and storage path

- Refactor `seed_default_alert_rules(rule_repo: AlertRuleRepository | None = None) -> int` to accept an optional repository (default: construct `AlertRuleRepository()`).
- Existing-rule detection uses `await rule_repo.list_all()` on `alert_rules`, not `PlatformConfigRepository.get_config`.
- Seed writes create engine-compatible documents via repository APIs.

### F2 — AlertEngine / provider API visibility

- Map each `DEFAULT_ALERT_RULES` entry to engine fields:
  - `rule_id` preserved as stable id for SPEC-1831 IDs.
  - `rule_type` set to a collector-backed type where available (`circuit_breaker`, `sla_breach`, `secret_expiry`, etc.).
  - `condition.threshold` populated from legacy `condition.value`.
  - `notification_channels` default `[]`.
- Defer SPEC-1831 KB `verified` promotion until integration tests prove `list_enabled()` returns seeded defaults.

### F3 — Lifecycle test scope

- Add `_startup_seed_default_alert_rules()` immediately after `_startup_alert_engine` in `register_startup_handlers()`.
- Tests invoke the handler directly with mocked `AlertRuleRepository`.
- Separate test asserts registration order and `list_enabled()` visibility after seed.

## Specification Links

- `SPEC-1831` - default alert rules at startup; engine parity.
- `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` - live-path tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - paths under `applications/Agent_Red/`.

## Owner Decisions / Input

Carried forward: owner 2026-04-18 decision "Fix impl". Bridge-clearance directive 2026-06-25 resumes paused commercial-readiness sub-tracks.

## Verification Plan

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_default_alert_rules.py applications/Agent_Red/tests/multi_tenant/test_default_alert_rules_startup.py -q --tb=short
python -m ruff check applications/Agent_Red/src/multi_tenant/default_alert_rules.py applications/Agent_Red/src/app/lifecycle.py
python -m ruff format --check applications/Agent_Red/src/multi_tenant/default_alert_rules.py applications/Agent_Red/src/app/lifecycle.py
```

## Out Of Scope

- SPEC-1831 MemBase status promotion in this slice.
- `platform_config` dual-write compatibility layer.

## Recommended Commit Type

`feat:`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
