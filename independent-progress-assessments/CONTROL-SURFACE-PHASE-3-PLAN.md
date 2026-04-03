# Control Surface Closeout — Phase 3 Plan

**Phase:** 3 of 5
**Focus:** Quality persistence/activation, dashboards/alerts, UX polish
**Status:** Plan review (v17)
**Created:** S255 (2026-04-02)
**Author:** Prime Builder (Opus 4.6)

---

## Investigation Findings (Step 1)

### Scope Boundary

Phase 3 covers **quality persistence/activation, dashboards/alerts, and UX polish** per the accepted 5-phase sequencing (INSIGHTS-2026-04-01-23-36-16, INSIGHTS-2026-04-02-00-10-41). This includes:
1. **Quality runtime write path** — scoring happens but is never persisted to Cosmos at runtime
2. **Quality activation** — threshold-based alerts when quality drops
3. **Widget UX polish** — loading states, connection recovery, visual transitions

Admin SPA dashboard pages (HealthDashboard, AlertThresholdConfig) are already implemented. Phase 3 connects the runtime quality path to those existing surfaces.

### Current State

**Quality in Widget:**
- Per-message feedback (SPEC-1836): thumbs up/down — IMPLEMENTED
- Quality scorer (quality_scorer.py): `ConversationQualityScorer.score_turn()` — EXISTS but imported by nothing at runtime (only tests)
- Quality score API (SPEC-1838): 6-metric composite — IMPLEMENTED (backend, KB-level)
- Conversation quality read path (_quality.py:242): queries `c.quality_aggregate` from conversation docs — IMPLEMENTED
- **Missing:** Runtime scorer wiring + aggregate persistence = dashboard shows nothing

**Alert Infrastructure:**
- AlertEngine (alert_engine.py:174): platform-level, evaluates _METRIC_COLLECTORS (5 types) — IMPLEMENTED
- AlertDeliveryService (alert_delivery.py:1004): `deliver_alert(Alert)` via channels — IMPLEMENTED
- Factory: `get_alert_service()` (alert_delivery.py:1441)
- AlertType enum (alert_delivery.py:143): 12 values, no quality type
- **Key constraint:** AlertEngine is platform-level (no tenant context in collector loop). Quality is per-tenant.

**Widget UX:**
- Animations, typing indicator, scrollbar — IMPLEMENTED
- Connection banner (Panel.tsx:820): basic reconnecting/error — IMPLEMENTED
- **Missing:** Skeleton loader for restore, connection attempt counter, stream progress

---

## Implementation Plan (Step 2)

### Deliverables

| ID | Deliverable | Priority | Files |
|----|-------------|----------|-------|
| P3-1 | Quality runtime write path (2 gaps) | P1 | orchestrator.py (scorer), session.py (aggregate), conversation.py (ETag write) |
| P3-2 | Quality regression alert (first-class rule) | P1 | cosmos_schema.py, alerts.py, alert_delivery.py, alert_engine.py, lifecycle.py, session.py, admin_conversation_api.py, conversation_meter.py, quality_regression.py, _operations.py, AlertConfig.tsx |
| P3-3 | Conversation restore skeleton loader | P1 | Panel.tsx, MessageList.tsx |
| P3-4 | Connection recovery UX (state + transport + UI) | P1 | store.ts, sse.ts, Panel.tsx |
| P3-5 | Message stream progress indicator | P2 | MessageList.tsx |
| P3-6 | Quick action staggered entrance | P2 | QuickActions.tsx |
| P3-7 | New locale keys for P3 features | P1 | en.ts + 7 locale files |

### Detailed Changes

**P3-1: Quality runtime write path (TWO gaps)**

**Gap A: Per-turn scoring — synchronous in orchestrator, post-Critic.**
`ConversationQualityScorer` exists (`quality_scorer.py:36`, singleton at line 178) but is imported nowhere at runtime. Fix:
- Import `quality_scorer` singleton into `orchestrator.py`
- Call `quality_scorer.score_turn(ai_response, customer_message, knowledge_context)` **synchronously** (await, not fire-and-forget) after Critic validation and BEFORE the `done` SSE event (~line 737). This prevents race conditions with aggregate persistence.
- Inputs available in orchestrator: `full_response` (ai_response), `tokenized_message` (customer_message), `knowledge_context` (orchestrator.py:638 from KR result)

**Score persistence — ETag-safe write:**
- Use `conversation_repo.replace_with_etag()` (conversation.py:229) instead of `update_message_metadata()` (which uses plain `replace_item` with no ETag retry, unsafe for concurrent writes)
- Read the conversation doc, find the AI message by `message_id` in the messages array, set `metadata.quality_score`, write back with ETag
- The `message_id` is returned by `add_ai_message()` in session.py — no need to change the return contract to include `message_index`

**Gap B: Aggregate persistence at ALL conversation-end paths (v12 fix).**
Quality aggregation must happen at ALL 5 closeout paths, not just `end_conversation()`. The aggregate computation moves into the shared `_evaluate_quality_and_alert()` helper (Step 3) so that every closeout path persists `quality_aggregate` before evaluating regression.

The shared helper does BOTH:
1. Read conversation doc, extract `quality_score.overall` from each AI message's metadata, compute aggregate (mean, min, max, count), write `quality_aggregate` field via `repo.patch()`
2. Then evaluate quality regression and alert (Step 3a)

This ensures the dashboard read path (`_quality.py:242` queries `c.quality_aggregate`) has data regardless of which closeout path ended the conversation. Without this, conversations closed by escalation or idle timeout would show no quality data.

**P3-2: Quality regression alert — first-class alert rule integration**

**Architecture:** Use the FULL alert-rule control surface, not bypass it.

**Step 1: Schema extension.**
- Add `QUALITY_REGRESSION = "quality_regression"` to `AlertRuleType` enum (cosmos_schema.py:1414, currently 5 values)
- Add `QUALITY_DROP = "quality_drop"` to `AlertType` enum (alert_delivery.py:143, currently 12 values)
- Add `tenant_id: str = ""` field to `AlertHistoryDocument` (cosmos_schema.py:1576) and `log_alert()` signature (alerts.py:189) — currently platform-level with no tenant attribution

**Step 2: Seed quality regression rule at startup.**
- In `lifecycle.py` startup sequence: call `AlertRuleRepository.create_rule()` (alerts.py:53) to seed a quality regression rule if none exists
- Rule doc: `rule_type="quality_regression"`, `name="Quality Regression"`, `condition={"metric": "quality_overall", "operator": "lt_delta", "threshold": 0.5}`, `cooldown_minutes=60`, `notification_channels=["email"]`
- This uses the CORRECT repository (`AlertRuleRepository` -> `alert_rules` collection) and the CORRECT condition schema (`threshold` field)

**Step 3: Evaluate at ALL conversation-end paths (v11: including escalation).**
Five paths change conversation status (all must trigger quality evaluation):
- `session.py:end_conversation()` (line 618) — customer-ended, max_turns, error
- `session.py:escalate_conversation()` (line 869) — customer-to-human escalation (writes status=ESCALATED directly via append_message_with_metadata, does NOT go through end_conversation)
- `admin_conversation_api.py:resolve_conversation()` (line 1135) — admin manual resolve
- `admin_conversation_api.py:escalate_conversation()` (line 976) — admin-initiated escalation (patches status=ESCALATED directly)
- `conversation_meter.py:scan_idle_conversations()` (line 1007) — idle timeout via background task

Extract quality evaluation into a shared helper `_evaluate_quality_and_alert(tenant_id, conversation_id, repo)` called from all five paths after status change. The v10 plan missed the two escalation entry points — both write ESCALATED status without routing through end_conversation().

**Step 3a: Evaluate quality regression.**
1. Read the quality regression alert rule from `AlertRuleRepository`
2. If rule exists and is enabled:
   - Check **tenant-scoped** cooldown (see Step 4 below)
   - Query recent conversation scores for THIS tenant, call `quality_regression.detect_regression(scores)` using the rule's `condition.threshold`
3. If regression detected AND cooldown passed:
   - Log to `alert_history` via `AlertHistoryRepository.log_alert()` (with tenant_id)
   - Deliver via `AlertDeliveryService.deliver_alert()` (alert_delivery.py:1004)

**Step 4: Fix cooldown to be tenant-scoped.**
`get_last_trigger_for_rule()` (alerts.py:260) currently queries only by `rule_id` — one tenant's alert suppresses all others. Fix:
- Add `tenant_id: str = ""` parameter to `get_last_trigger_for_rule()`
- Add `AND c.tenant_id = @tid` to the query when `tenant_id` is provided
- Update `_is_in_cooldown()` in `alert_engine.py` to pass tenant_id when available
- Backward compatible: existing platform-level rules pass empty string (no tenant filter)

**Step 5: Delivery channel limitation.**
`deliver_alert()` (alert_delivery.py:1004) always fans out to ALL registered channels — no per-alert channel filter exists. Two options:
- (a) Add optional `channels: list[str] | None` parameter to `deliver_alert()` — if provided, only deliver to matching channel names
- (b) Accept current behavior: quality alerts go to all channels (email, log). The rule's `notification_channels` field is advisory metadata for future use
- Prefer (a) for correctness — the rule system promises per-rule channel selection

**Step 6: Admin UI + API surface updates (v11: full editability).**

6a. Rule type + color:
- `AlertConfig.tsx` RULE_TYPE_OPTIONS (line 94): add `{ value: 'quality_regression', label: 'Quality Regression' }`
- `AlertConfig.tsx` TYPE_COLORS: add `quality_regression: 'teal'`

6b. Operator support for lt_delta:
- `AlertConfig.tsx` OPERATOR_OPTIONS (line 102): add `{ value: 'lt_delta', label: 'Δ< (delta less than)' }`
- `AlertConfig.tsx` `formatCondition()` (line 138): add lt_delta case to rendered condition display
- `cosmos_schema.py AlertCondition`: add `lt_delta` to allowed operator values if not present

6c. notificationChannels preservation on edit (v11 fix):
- `AlertConfig.tsx` save handler (line 239-249): currently hardcodes `notificationChannels: []`
- Fix: when editing an existing rule, preserve `editingRule.notificationChannels`
- When creating a new rule, default to `["email"]` (matches seeded quality rule)
- Change line 248 from `notificationChannels: []` to `notificationChannels: editingRule?.notificationChannels ?? ['email']`

6d. Tenant attribution in alert history (v11 fix):
- Backend model: add `tenant_id: str = ""` to `AlertHistoryItemModel` (_operations.py:305)
- Backend mapper: add `tenant_id=doc.get("tenant_id", "")` to `_history_to_model()` (_operations.py:443)
- Frontend type: add `tenantId?: string` to `AlertHistoryItem` interface (AlertConfig.tsx:69)
- Frontend table: add tenant column to history table, show tenant name when `tenantId` is present, hide column when all entries are platform-level (empty tenantId)

**Threshold:** From the seeded rule's `condition.threshold` (default 0.5 on 1.0-5.0 scale). Severity from `quality_regression.py`: 0.5-1.0 = warning, >1.0 = critical.

**P3-3: Conversation restore skeleton loader**
When SPEC-1868 transcript continuity restores a previous conversation, the widget currently shows nothing while fetching. Add a skeleton loading state:
- **store.ts (WidgetState):** Add `isRestoring: boolean` (default false) and `restoreError: 'transient' | null` (default null). Set `isRestoring=true` when `fetchConversation()` starts, `false` on success or failure. Set `restoreError='transient'` on recoverable fetch failure.
- **Panel.tsx:** Read `isRestoring` and `restoreError` from store (same pattern as existing `isReconnecting`, `isLoading`). Render skeleton when `isRestoring=true`, retry prompt when `restoreError='transient'`.
- Skeleton: 3-4 pulsing bubble shapes (2 agent, 1 customer, 1 agent) using existing `ar-shimmer` animation
- Disappears when messages are loaded (`isRestoring=false`) or on permanent failure

**P3-4: Connection recovery UX (state + transport + UI)**
The current widget only stores `isReconnecting: boolean` and `error: string | null` in store.ts:93. Reconnect attempts are private inside sse.ts:86. The UI cannot show attempt count or distinguish transient vs permanent failure. Fix requires changes across three layers:
- **store.ts**: Add `reconnectAttempt: number` and `connectionError: 'transient' | 'permanent' | null` to WidgetState
- **sse.ts**: Expose reconnect attempt count via `onReconnectAttempt(attempt: number)` callback. Distinguish max-retries-exhausted (permanent) from in-progress (transient) in callbacks
- **Panel.tsx (ConnectionBanner)**: Show attempt counter ("Reconnecting... attempt 3 of 5"). On permanent failure: show "Unable to connect" with retry button. Add `role="alert"` + `aria-live="assertive"` for screen reader announcement. Add dismiss button for error state

**P3-5: Message stream progress indicator**
When the AI is generating a response (SSE streaming), add a subtle visual indicator:
- Thin progress bar at top of message list that animates during streaming
- Uses `colorPrimary` from tokens
- Disappears on `done` or `error` SSE event
- Non-intrusive: 2px height, smooth width animation

**P3-6: Quick action staggered entrance**
When a new conversation starts, quick action buttons should have a staggered entrance:
- QuickActions.tsx (not MessageList.tsx) — this component owns the button rendering
- Sequential fade-in with 50ms delay per button
- Uses existing `ar-fade-in` animation with `animation-delay`

**P3-7: New locale keys for P3 features**
- `reconnectingAttempt`: "Reconnecting... attempt {n}"
- `connectionFailedPermanent`: "Unable to connect"
- `retryConnection`: "Retry"
- `dismissError`: "Dismiss"
- `restoringConversation`: "Loading previous conversation..."
- Add to all 8 locale files

### Step 0: Vitest Infrastructure (v14 prerequisite)

The widget has no JS test runner. Add Vitest + happy-dom + @testing-library/preact to enable behavioral component testing. Tests go under `widget/tests/` (not `widget/src/__tests__/`) because `tsconfig.json` uses `rootDir: "./src"` and `include: ["src"]`.

**Install:**
```
cd widget && npm install -D vitest happy-dom @testing-library/preact @testing-library/jest-dom
```

**Configure:** Add `test` block to `vite.config.ts`:
```ts
test: {
  environment: 'happy-dom',
  include: ['tests/**/*.test.{ts,tsx}'],
  globals: true,
}
```

Add `tsconfig.test.json` extending `tsconfig.json` with `include: ["src", "tests"]`.

Add `"test": "vitest run"` to `package.json` scripts.

**Smoke test:** `widget/tests/smoke.test.tsx` — render a Preact component, assert it produces DOM output.

### Widget UX Test Specifications (v14: Vitest behavioral tests)

Tests are Vitest component tests under `widget/tests/`. They render real Preact components with props/state and assert on DOM output — not source-code string matching.

**widget/tests/restore-skeleton.test.tsx** (P3-3: skeleton loader)

Panel's live props are `config`, `locale`, `onClose` (Panel.tsx:56-60). There is no `isRestoring` prop — restore state is driven by the store. Tests control state by calling `store.setState({ isRestoring: true })` before rendering Panel. P3-3 implementation adds `isRestoring` to the store's WidgetState (same pattern as existing `isReconnecting`, `isLoading`).

| # | Test | Assertion |
|---|------|-----------|
| 1 | Skeleton visible when store.isRestoring=true | Set `store.setState({ isRestoring: true })`, render Panel → shimmer/skeleton element in DOM |
| 2 | Skeleton hidden when store has messages | Set `store.setState({ isRestoring: false, messages: [...] })` → no shimmer element |
| 3 | Transient failure shows retry button | Set `store.setState({ restoreError: 'transient' })` → button with text matching `locale.retryConnection` |
| 4 | Loading text uses locale | `getByText(en.restoringConversation)` while isRestoring=true |

**widget/tests/connection-recovery.test.tsx** (P3-4: connection recovery UX)

ConnectionBanner is currently a local (non-exported) component in Panel.tsx:820 with props `{ tokens, locale, type: 'reconnecting' | 'error', message?: string }`. P3-4 implementation will **extract and export** ConnectionBanner to `widget/src/components/ConnectionBanner.tsx` so it can be tested directly. This is a prerequisite refactor — the component already exists as a self-contained function, extraction is mechanical.

Tests render the exported ConnectionBanner directly with controlled props. P3-4 also adds new props (`reconnectAttempt`, `connectionError`, `onRetry`, `onDismiss`) to the extracted component.

| # | Test | Assertion |
|---|------|-----------|
| 1 | Attempt counter shows during reconnect | Render ConnectionBanner with type='reconnecting', reconnectAttempt=3, locale=en → text contains `en.reconnectingAttempt` interpolated with "3" |
| 2 | Permanent failure shows locale text | Render with type='error', connectionError='permanent', locale=en → `getByText(en.connectionFailedPermanent)` |
| 3 | Permanent failure retry uses locale | `getByRole('button')` with text matching `en.retryConnection` |
| 4 | Dismiss button uses locale | `getByRole('button')` with text matching `en.dismissError` |
| 5 | Banner has role=alert | `getByRole('alert')` finds the banner element |
| 6 | Banner has aria-live=assertive | Banner element has `aria-live="assertive"` attribute |
| 7 | Non-English locale renders correctly | Render with locale=es → text contains `es.connectionFailedPermanent` (not English) |

**widget/tests/stream-progress.test.tsx** (P3-5: stream progress indicator)

The live streaming contract uses `messages[last].streaming: boolean` on the message object (store.ts:28, MessageList.tsx:276), not a top-level `isStreaming` prop.

| # | Test | Assertion |
|---|------|-----------|
| 1 | Progress bar visible when last message is streaming | Render MessageList with messages where `messages[last].streaming=true` → progress element in DOM |
| 2 | Progress bar hidden when last message not streaming | Render with `messages[last].streaming=false` → no progress element |
| 3 | Progress bar uses primary color | Element has style containing colorPrimary value |

**widget/tests/quick-action-stagger.test.tsx** (P3-6: staggered entrance)

QuickActions.tsx caps visible actions at 2 (`actions.slice(0, 2)` at line 51). Tests must use 2 actions, not 3.

| # | Test | Assertion |
|---|------|-----------|
| 1 | Buttons have sequential animation-delay | Render QuickActions with 2 actions → button[0] delay=0ms, button[1] delay=50ms |
| 2 | Animation class applied | Each button has ar-fade-in class or animation |
| 3 | Only 2 buttons render (cap enforced) | `getAllByRole('button')` returns 2 even if 4 actions provided |

**widget/tests/p3-locale.test.ts** (P3-7: locale keys — non-rendering, import-based)

| # | Test | Assertion |
|---|------|-----------|
| 1 | en.ts exports reconnectingAttempt | `import { en } from '@/locale/en'` → `en.reconnectingAttempt` is defined |
| 2 | en.ts exports connectionFailedPermanent | Key is defined |
| 3 | en.ts exports retryConnection | Key is defined |
| 4 | en.ts exports dismissError | Key is defined |
| 5 | en.ts exports restoringConversation | Key is defined |
| 6 | All 8 locales have all 5 keys | Import each locale, assert all 5 keys are non-empty strings |

### Implementation Sequence (v14: tests mandatory per owner directive)

Each deliverable follows the standing test-before-code cycle: write tests → verify they fail/skip → implement → verify they pass → run regression suite.

**Step 0: Vitest infrastructure (prerequisite):**
1. Install Vitest + happy-dom + @testing-library/preact + @testing-library/jest-dom
2. Configure vite.config.ts test block, tsconfig.test.json, package.json test script
3. Write smoke test (widget/tests/smoke.test.tsx) → verify `cd widget && npx vitest run` passes
4. Write P3-3 through P3-7 Vitest test files → verify they fail (features not yet implemented)

**Backend (quality + alerts):**
5. Verify Slice 9+10 pre-implementation tests skip/fail as expected
6. P3-1 — Quality runtime write path: scorer wiring in orchestrator, aggregate in shared helper
7. P3-2 — Quality regression alert: schema, seed, shared helper, cooldown, delivery
8. Run: `python -m pytest tests/chat/pipeline/test_quality_scoring.py tests/multi_tenant/test_quality_alert_admin.py -v`
9. Run full backend regression: `.\scripts\run-tests-thermal-safe.ps1 -SkipLive`

**Widget (UX polish):**
10. P3-7 — Locale keys (needed before UI work)
11. Run: `cd widget && npx vitest run tests/p3-locale.test.ts` → verify pass
12. P3-4 — Connection recovery (store + transport + UI)
13. Run: `cd widget && npx vitest run tests/connection-recovery.test.tsx` → verify pass
14. P3-3 — Skeleton loader
15. Run: `cd widget && npx vitest run tests/restore-skeleton.test.tsx` → verify pass
16. P3-5 — Stream progress indicator
17. Run: `cd widget && npx vitest run tests/stream-progress.test.tsx` → verify pass
18. P3-6 — Quick action stagger
19. Run: `cd widget && npx vitest run tests/quick-action-stagger.test.tsx` → verify pass
20. Widget rebuild + typecheck: `cd widget && npm run build && npx tsc --noEmit`
21. Run full Vitest suite: `cd widget && npx vitest run`
22. Run Python widget regression: `python -m pytest tests/widget/ -v`

**Admin UI (alert surface):**
23. P3-2 Step 6 — AlertConfig.tsx updates (6a-6d)
24. Admin rebuild + typecheck
25. Run admin alert tests: `python -m pytest tests/widget/test_alert_config_quality.py -v`

**Gate:**
26. Full regression: `.\scripts\run-tests-thermal-safe.ps1 -SkipLive`
27. Codex review submission
28. Build + deploy to staging (GOV-16 approval required for production)

---

### Codex NO-GO v1 Findings (INSIGHTS-2026-04-02-19-07-10)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | Scope: only widget UX polish, missing quality path | Added P3-1 quality write + P3-2 quality alerts |
| P1 | P3-2/P3-5 under-scoped: store.ts only has boolean, sse.ts private | Widened to 3-layer: store + sse + Panel |
| P2 | P3-4 wrong file: QuickActions.tsx not MessageList.tsx | Fixed to P3-6 targeting QuickActions.tsx |

### Codex NO-GO v2 Findings (INSIGHTS-2026-04-02-19-17-23)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | P3-1 wrong module: quality_score.py is KB metrics, not runtime scorer | Fixed: quality_scorer.py + session.py:end_conversation() |
| P1 | P3-2 wrong alert stack: default_alert_rules.py seeds PlatformConfig | Fixed: add to _METRIC_COLLECTORS + cosmos_schema + AlertRuleRepository |

### Codex NO-GO v3 Findings (INSIGHTS-2026-04-02-19-29-10)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | P3-1 assumes per-turn quality_score metadata exists — it doesn't | Fixed: P3-1 now has TWO gaps (A: wire scorer, B: aggregate at end) |
| P1 | P3-2 default_alert_rules seeds wrong repo + never called. Engine logs but never delivers | Fixed: P3-2 now has THREE gaps (A: collector, B: seed fix, C: delivery) |

### Codex NO-GO v4 Findings (INSIGHTS-2026-04-02-19-38-20)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | P3-1 scorer needs message_index but pipeline returns message_id | Made identity contract explicit: return (message_id, message_index) |
| P1 | P3-2 no QUALITY_DROP enum, Alert requires tenant_id, method is deliver_alert not deliver | Full Alert construction contract with correct method and enum |

### Codex NO-GO v5 Findings (INSIGHTS-2026-04-02-19-46-35)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | AlertEngine is platform-level, no tenant context for quality | Redesigned: quality alerts fire event-driven from session.py, bypass AlertEngine |
| P1 | deliver() vs deliver_alert(), _derive_severity() returns .value strings | Fixed: use deliver_alert(), AlertSeverity enum directly |

## Plan Review (Step 3)

### Codex NO-GO v6 Findings (INSIGHTS-2026-04-02-19-55-07)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | Bypassing alert architecture contradicts scope statement | Redesigned: use existing quality_regression.py (SPEC-0183) with detect_regression() |
| P1 | Threshold -10 points impossible on 1.0-5.0 scale | Fixed: use quality_regression.py defaults (0.5 warning, 1.0 critical) |
| P2 | Scorer inputs (customer_message, knowledge_context) not available in session.py | Added input contract: read from conversation doc + pipeline KR output |

### Codex NO-GO v7 Findings (INSIGHTS-2026-04-02-20-05-28)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | deliver_alert() bypasses alert_history collection used by admin dashboard | Fixed: dual write — AlertHistoryRepository.log_alert() + deliver_alert() |
| P2 | Scorer hook in session.py lacks KR context; orchestrator has it | Moved scorer hook to orchestrator.py where all inputs (ai_response, customer_message, knowledge_context) are available |

### Codex NO-GO v8 Findings (INSIGHTS-2026-04-02-20-15-06)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | Direct log_alert+deliver_alert bypasses rule notification_channels/cooldown | Redesigned: create first-class quality rule, evaluate through rule system |
| P1 | Async scorer races with aggregate persistence | Made scorer synchronous (await, post-Critic pre-done) |
| P2 | update_message_metadata uses plain replace_item, unsafe for concurrent writes | Use replace_with_etag (conversation.py:229) |
| P2 | alert_history has no tenant field | Add tenant_id to log_alert call and AlertHistoryDocument |

### Codex NO-GO v9 Findings (INSIGHTS-2026-04-02-20-26-01)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | deliver_alert() fans out to all channels, no per-alert filter | Add optional channels param to deliver_alert() |
| P1 | Cooldown is global by rule_id, not tenant-scoped | Add tenant_id param to get_last_trigger_for_rule() query |
| P1 | Only hooks end_conversation, misses admin resolve + idle timeout | Shared helper called from all 3 conversation-end paths |
| P2 | Admin UI/API surfaces not in scope (AlertConfig.tsx, AlertHistoryItemModel) | Added to file scope: RULE_TYPE_OPTIONS, TYPE_COLORS, tenant column, AlertHistoryItemModel |

### Codex NO-GO v10 Findings (INSIGHTS-2026-04-02-20-40-16)

| # | Finding | Resolution |
|---|---------|------------|
| P1 | Escalation paths missed: critic_escalation.py:163 + admin manual escalation (admin_conversation_api.py:976) | Add both to shared helper call sites |
| P2 | Admin UI incomplete: notificationChannels hardcoded on save, lt_delta missing from operators, tenant attribution needs mapper/frontend wiring | Expand admin UI scope to include all 4 gaps |

*Pending Codex review (v17). v17 fix: P3-3 deliverable now explicitly declares `isRestoring: boolean` and `restoreError: 'transient' | null` in WidgetState (store.ts), consistent with test seam. No more contradiction between deliverable text and test specs.*

---

## Implementation Progress (Step 4)

*Not started.*

---

## Implementation Review (Step 5)

*Pending.*

---

## Final Status (Step 6)

*Pending.*

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
