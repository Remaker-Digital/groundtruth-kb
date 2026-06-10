NEW
author_identity: Prime Builder
author_harness_id: B
author_session_context_id: session-mq5ki8hp
author_model: Claude Sonnet 4
author_model_version: 4
author_model_configuration: Prime Builder session-scoped bridge work

bridge_id: gtkb-sp1b-dispatch-outcome-tracker
bridge_kind: prime_proposal

# SP-1b: Async Dispatch Outcome Tracker

## Status
- **Priority:** P1 (High)
- **Effort:** Medium (2-3 days)
- **Blocked by:** None

## Background
LO investigation (2026-06-08) found 82+ dispatches since June 5 with no systematic post-dispatch verification. When dispatch succeeds (HTTP 200), no background task verifies that Ollama actually produced a verdict file.

**Impact:** Silent failures, no telemetry on success rate, debugging requires manual chain-detector runs.

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- DCL-OBSERVABILITY-REQUIREMENTS-001

## Target Paths
- scripts/cross_harness_bridge_trigger.py (add async verification)
- scripts/dispatch_outcome_tracker.py (new file)
- .gtkb-state/dispatch-outcomes/ (new directory)

## Implementation
1. SQLite DB schema: dispatches(dispatch_id, timestamp, target_slug, status, verdict_path, error_message)
2. Async poller thread: poll bridge/ every 30s, 10-min timeout
3. CLI: python scripts/dispatch_outcome_tracker.py show-recent --since 24h
4. Metrics export to .gtkb-state/metrics/dispatch-outcomes.jsonl

## LO Review Criteria
- [ ] Database schema matches spec
- [ ] Poller non-blocking
- [ ] Timeout configurable
- [ ] CLI works
- [ ] Metrics file written
- [ ] Code passes ruff
