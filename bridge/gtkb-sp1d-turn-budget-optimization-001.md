NEW
author_identity: Prime Builder
author_harness_id: B
author_session_context_id: session-mq5ki8hp
author_model: Claude Sonnet 4
author_model_version: 4
author_model_configuration: Prime Builder session-scoped bridge work

bridge_id: gtkb-sp1d-turn-budget-optimization
bridge_kind: implementation_proposal

# SP-1d: Ollama LO Turn Budget Optimization

## Status
- **Priority:** P2 (Medium)
- **Effort:** Small (0.5 day)
- **Blocked by:** SP-1a

## Background
LO investigation: 72% (36/50) of recent NO-GOs hit turn limit (12 turns) before completing. Current max_turns=12, timeout=120s is insufficient for complex reviews.

## Specification Links
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-ARTIFACT-INTEGRITY-001
- DCL-DISPATCH-TELEMETRY-001

## Target Paths
- scripts/cross_harness_bridge_trigger.py (increase defaults)
- .claude/config/ollama-dispatch-env.json (configurable)

## Implementation
1. New defaults: max_turns=20, timeout=300s
2. Config file: .claude/config/ollama-dispatch-env.json
3. Telemetry: log to .gtkb-state/dispatch-telemetry.jsonl
4. Truncation detection: if verdict exists but metadata missing, log TRUNCATED
5. Env var overrides: OLLAMA_DISPATCH_MAX_TURNS, OLLAMA_DISPATCH_TIMEOUT

## LO Review Criteria
- [ ] Defaults increased
- [ ] Config file read
- [ ] Env vars override config
- [ ] Telemetry written
- [ ] Truncation detected
- [ ] Code passes ruff
