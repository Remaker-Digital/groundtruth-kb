# Conversation Quality — Operational Lessons

> Full reference: KB DOC-CONVERSATION-QUALITY

## Testing Lessons
- Chat pipeline must be initialized (201 not 503) before running quality tests
- Jailbreak scenarios may return empty responses (critic rejection) — expected, not failure
- Golden dataset expects KB data that may not exist — seed with `evaluation/seed_quality_kb.py`
