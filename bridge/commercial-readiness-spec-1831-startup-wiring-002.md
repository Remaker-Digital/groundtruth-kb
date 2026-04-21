NO-GO

# F4 Sub-Track Review: SPEC-1831 Startup Wiring for Default Alert Rules

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-19
**Reviewed proposal:** `bridge/commercial-readiness-spec-1831-startup-wiring-001.md`

## Verdict

NO-GO. The proposal correctly identifies that `seed_default_alert_rules()` is not wired into startup, but the proposed implementation path does not satisfy SPEC-1831 as currently framed. The proposal mixes two different storage paths:

- `AlertRuleRepository` / `alert_rules`, which the alert engine and provider alert-rule API use.
- `PlatformConfigRepository` / `platform_config`, which the current `seed_default_alert_rules()` helper uses.

As a result, simply adding a lifecycle handler around the current helper would create a `platform_config` document but would not make the default rules evaluable by `AlertEngine` or editable through the current alert-rule API.

## Evidence Reviewed

- `bridge/commercial-readiness-spec-1831-startup-wiring-001.md`
- `bridge/commercial-readiness-spec-verification-002.md`
- `bridge/commercial-readiness-spec-verification-003.md`
- `.claude/rules/file-bridge-protocol.md`
- `src/app/lifecycle.py`
- `src/multi_tenant/default_alert_rules.py`
- `src/multi_tenant/repositories/alerts.py`
- `src/multi_tenant/repositories/platform.py`
- `src/multi_tenant/alert_engine.py`
- `src/multi_tenant/superadmin_api/_operations.py`
- `tests/multi_tenant/test_default_alert_rules.py`

Command evidence:

```text
$ rg -n "seed_default_alert_rules\(" src tests bridge -S
src\multi_tenant\default_alert_rules.py:146:async def seed_default_alert_rules() -> int:
tests\multi_tenant\test_default_alert_rules.py:114:            count = await seed_default_alert_rules()
tests\multi_tenant\test_default_alert_rules.py:135:            count = await seed_default_alert_rules()
tests\multi_tenant\test_default_alert_rules.py:152:            await seed_default_alert_rules()
tests\multi_tenant\test_default_alert_rules.py:171:            count = await seed_default_alert_rules()
```

```text
$ python -m pytest tests/multi_tenant/test_default_alert_rules.py -q --tb=short
13 passed in 0.27s
```

The existing unit tests pass, but they only prove helper behavior when called directly. They still do not prove startup activation, alert-engine evaluation, or provider-admin editability.

## Findings

### F1 - Blocker - Proposed wiring calls the wrong helper interface and checks the wrong storage source

**Claim:** The proposal says the startup handler should check existing rules through `AlertRuleRepository`, then call `seed_default_alert_rules(rule_repo)`.

**Evidence:**

- Proposal `bridge/commercial-readiness-spec-1831-startup-wiring-001.md:30-31` says to check via `AlertRuleRepository` and call `seed_default_alert_rules(rule_repo)`.
- Current helper signature is `async def seed_default_alert_rules() -> int` at `src/multi_tenant/default_alert_rules.py:146`; it accepts no repository argument.
- The helper instantiates `PlatformConfigRepository()` internally at `src/multi_tenant/default_alert_rules.py:153-154`.
- Existing-rule detection reads `platform_config` key `alert_rules:all_rules` at `src/multi_tenant/default_alert_rules.py:162`.
- The seed write creates one `PlatformConfigDocument` with `config_type="alert_rules"` and `config_key="all_rules"` at `src/multi_tenant/default_alert_rules.py:175-179`.
- Existing tests patch `PlatformConfigRepository`, not `AlertRuleRepository`, at `tests/multi_tenant/test_default_alert_rules.py:111`, `:132`, `:149`, and `:168`.

**Risk/impact:** Implementing the proposal literally will either fail with a `TypeError` by passing an argument to the helper, or it will check `AlertRuleRepository` while the helper writes `platform_config`, leaving two divergent sources of truth. If the alert-rule collection is empty but the platform-config seed document exists, the proposed "zero rules" check and helper skip logic can disagree.

**Required action:** Pick one canonical storage path before wiring startup:

1. If SPEC-1831 means executable alert rules, refactor the seeder to create engine-compatible documents through `AlertRuleRepository` or an equivalent repository method, then test that the `alert_rules` collection contains the eight defaults.
2. If SPEC-1831 intentionally means a platform-config bundle, revise the spec and proposal to explain how the alert engine and provider alert-rule API consume that bundle.

### F2 - Blocker - Current helper output is not consumed by AlertEngine or the provider alert-rule API

**Claim:** SPEC-1831 verification still requires evidence that default rules are evaluated like custom alert rules.

**Evidence:**

- The parent NO-GO cited the current SPEC-1831 requirement text: "Default rules created during application startup if no rules exist" and "Alert engine evaluates default rules identically to custom rules" in `bridge/commercial-readiness-spec-verification-002.md:35`.
- `AlertEngine.evaluate_all()` reads rules from `self._rule_repo.list_enabled()` at `src/multi_tenant/alert_engine.py:196`.
- The engine expects each rule to have `rule_type` and an engine-style condition with a `threshold` at `src/multi_tenant/alert_engine.py:204-208`.
- Metric collector selection is keyed by `rule_type` at `src/multi_tenant/alert_engine.py:212`.
- `AlertRuleRepository` is explicitly the repository for the `alert_rules` collection at `src/multi_tenant/repositories/alerts.py:38-41`, and `list_enabled()` queries that collection at `src/multi_tenant/repositories/alerts.py:122-128`.
- The provider endpoint `GET /alerts/rules` lists `_state._alert_rule_repo.list_all()` at `src/multi_tenant/superadmin_api/_operations.py:478`.
- The current default rule definitions have `rule_id`, `severity`, `cooldown_minutes`, and `condition.value`, but no `rule_type` and no `condition.threshold`, in `src/multi_tenant/default_alert_rules.py:31-135`.

**Risk/impact:** A startup handler that only calls the current `seed_default_alert_rules()` would not make the eight defaults visible to `AlertEngine.evaluate_all()` or `/alerts/rules`. Promoting SPEC-1831 to `verified` after that change would still overstate the implementation.

**Required action:** The revised proposal must include one of these paths:

- Convert the eight defaults into `alert_rules` documents with `rule_type`, `condition.threshold`, `notification_channels`, and any other fields required by `AlertRuleRepository` and `AlertEngine`.
- Or, explicitly revise SPEC-1831 away from alert-engine parity and provider-admin editability before promoting it.

The verification plan must include an integration test proving that seeded defaults are returned by `AlertRuleRepository.list_enabled()` and are candidates for `AlertEngine.evaluate_all()`, not only that a platform-config document contains eight IDs.

### F3 - Major - Proposed lifecycle tests are likely too broad unless scoped to the new handler and registration order

**Claim:** The proposal says to "run startup handlers" for the new tests.

**Evidence:**

- `register_startup_handlers()` collects many unrelated startup handlers at `src/app/lifecycle.py:2120-2177`, including Cosmos, NATS, AGNTCY SDK, vectorizers, copilot ingestion, alert delivery, migrations, Redis, and entitlement service.
- The lifespan runner executes every collected startup handler sequentially at `src/app/lifecycle.py:2223-2226`.
- The current relevant alert-engine setup is `_startup_alert_engine()` at `src/app/lifecycle.py:1566-1615`, with registration at `src/app/lifecycle.py:2163`.

**Risk/impact:** A unit test that executes the full startup list will be slow, brittle, and may require mocks for many unrelated services. It can also mask the actual contract: the new default-rule startup handler must be registered after `_startup_alert_engine` and before background alert evaluation can observe rules.

**Required action:** Scope tests to the new handler and registration contract:

- Directly invoke the new `_startup_seed_default_alert_rules()` with repository/helper mocks.
- Assert `register_startup_handlers()` places it after `_startup_alert_engine`.
- Keep a separate minimal test that proves the seeder writes to the same repository surface that `AlertEngine` reads.

## Required Revision Conditions

A revised bridge should:

1. Resolve the canonical storage decision: `alert_rules` collection versus `platform_config`.
2. If using `alert_rules`, update or wrap `seed_default_alert_rules()` so it seeds engine-compatible rule documents.
3. Ensure existing-rule detection and seed writes use the same repository/source of truth.
4. Add tests for startup handler behavior, registration order after `_startup_alert_engine`, seeded default IDs, no duplication on restart, and alert-engine visibility.
5. Defer SPEC-1831 status promotion until the implementation evidence covers startup creation and alert-engine parity.

## Decision Needed From Owner

No new owner decision is required if the intent remains "Fix impl." The Prime Builder needs to revise the implementation plan so that the startup seed lands in the rule store actually used by alert evaluation and provider administration, or explicitly ask the owner to narrow/rewrite SPEC-1831.

