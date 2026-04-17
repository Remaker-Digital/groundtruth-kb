# Phase 3: F7 + F5 — REVISED v6 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Type:** Revised Implementation Proposal (addresses NO-GO -012)

## NO-GO -012 Resolution

### Finding 1: F5 v10 doctor regression coverage incomplete → FIXED

**Resolution:** Doctor tests expanded from 5 to 8, matching all approved v10 cases:

**Bridge-profile doctor tests (7):**
1. Only intake classifier active → passes
2. Only spec classifier active → passes (legacy backward compat)
3. Both classifiers active → warns (redundant)
4. Neither classifier active → warns (gap)
5. Malformed JSON in settings → warns without crash
6. `hooks` value is a non-dict (e.g., list) → warns without crash
7. `hooks` value is null → warns without crash

**Local-only doctor test (1):**
8. Local-only profile: no classifier-settings check added when settings file absent → no false warning

Total doctor tests: 8 (was 5).

F5 test count: 31 → 34 (was 31: replaced 5 doctor tests with 8).

---

## Complete Test Summary

### F7 (14 tests — unchanged from v4)

1. Snapshot capture — lifecycle + summary + quality + coverage
2. Snapshot includes get_summary() data
3. Same-session replacement (INSERT OR REPLACE)
4. Delta: current-vs-last with no prior → no_prior=True
5. Delta: current-vs-last with prior → deltas computed
6. Delta: explicit session-vs-previous for trends
7. Alert generation — metric above threshold
8. Text rendering — non-empty output
9. Graceful degradation — empty DB
10. Threshold storage via env_config
11. Threshold default fallback
12. Snapshot export/import roundtrip
13. Malformed snapshot JSON import rejected
14. Hook template exists and valid Python

### F5 (34 tests — updated)

**Core intake (13):**
1. Classify directive — confidence > 0.8
2. Classify exploration — confidence < 0.5
3. Classify question
4. Classify constraint
5. Classify ambiguous → exploration, low confidence
6. Classify with related specs populated
7. Capture stores full candidate (classification, confidence, raw_text, proposed_type, proposed_authority)
8. Confirm creates spec with proposed type/authority, records confirmed_spec_id
9. Confirm with default type/authority when proposed fields absent
10. Confirm returns F2 impact + F4 constraints
11. Confirm returns F3 quality score and tier
12. Reject stores reason, updates status
13. Reject reason required

**List/filter (3):**
14. List pending — only pending intakes
15. List all — excludes non-intake deliberations
16. Double confirm idempotent

**Redaction + CLI (4):**
17. Redaction: credential stored redacted, still filterable
18. CLI smoke: `gt intake list`
19. CLI smoke: `gt intake confirm`
20. CLI smoke: `gt intake reject`

**Adoption: scaffold (2):**
21. Bridge-profile — settings includes intake hook
22. Local-only — settings omits intake hook

**Adoption: doctor (8):**
23. Bridge: only intake active → passes
24. Bridge: only spec active → passes (backward compat)
25. Bridge: both active → warns
26. Bridge: neither active → warns
27. Bridge: malformed JSON → warns without crash
28. Bridge: hooks as non-dict → warns without crash
29. Bridge: hooks as null → warns without crash
30. Local-only: no false warning when settings absent

**Adoption: upgrade (3):**
31. Upgrade copy — intake hook copied
32. Upgrade preserve — existing hooks preserved
33. Upgrade local-only — local-only allowlist respected

**Roundtrip (1):**
34. Classify → capture → confirm → spec exists with correct type/authority + quality tier

---

## All Prior Conditions Preserved

- F7: lifecycle + summary + quality + coverage snapshots ✓
- F7: INSERT OR REPLACE write contract + same-session test ✓
- F7: current-vs-last delta with no_prior ✓
- F7: gt health / snapshot / trends CLI ✓
- F7: render_health_text() + DEFAULT_THRESHOLDS ✓
- F7: import validation + malformed JSON rejection ✓
- F7: session-health.py hook template ✓
- F5: numeric confidence [0.0, 1.0] ✓
- F5: intent classification (directive/constraint/preference/question/exploration) ✓
- F5: full candidate payload (raw_text, classification, confidence, proposed_type, proposed_authority) ✓
- F5: confirm creates spec + returns F2 impact + F3 quality/tier + F4 constraints ✓
- F5: intake discriminator filters non-intake deliberations ✓
- F5: redaction coverage ✓
- F5: CLI smoke for list/confirm/reject ✓
- F5: hook + settings + scaffold + doctor + upgrade + docs adoption chain ✓
- F5: legacy spec-classifier.py backward compat ✓

## Implementation Order

1. F7 first (14 tests)
2. F5 second (34 tests)

## Verification

1. `python -m pytest -q` (509 → ~557 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Request

Codex review requested. GO authorizes Phase 3 implementation.
