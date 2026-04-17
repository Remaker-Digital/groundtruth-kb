# Phase 3: F7 + F5 — REVISED v5 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Type:** Revised Implementation Proposal (addresses NO-GO -010)

## NO-GO -010 Resolution

### Finding 1: F5 confirm omits F3 quality/tier path → FIXED

**Resolution:** `confirm_intake()` now calls `score_spec_quality()` on the
newly created spec and includes quality/tier data in the confirmation result
and audit record.

**Revised confirm_intake() flow:**
1. Parse deliberation content
2. Create spec: `db.insert_spec(id=..., type=proposed_type, authority=proposed_authority, ...)`
3. Score quality: `quality = db.score_spec_quality(db.get_spec(created_id))`
4. Compute impact: `impact = db.compute_impact("add", db.get_spec(created_id))`
5. Check constraints: `constraints = db.check_constraints_for_spec(created_id)`
6. Patch content: `intake_status="confirmed"`, `confirmed_spec_id=created_id`,
   `quality_tier=quality["tier"]`, `quality_score=quality["overall"]`
7. Update deliberation `outcome="owner_decision"`
8. Return `{spec, quality, impact, constraints}`

**Tier-based assertion guidance:** For Phase 3, the tier is computed and
returned as advisory metadata. Automatic assertion generation based on tier
is deferred to a follow-up (requires spec-content analysis beyond intake scope).
The confirm result includes `quality.tier` and `quality.flags` so the caller
(hook or CLI) can display tier-appropriate guidance text.

**New test:** "Confirm returns F3 quality score and tier" — confirms an intake,
asserts result contains `quality` dict with `overall`, `tier`, and `flags` keys.

F5 test count: 30 → 31.

---

## All Prior Fixes Preserved

**F7 (14 tests, unchanged):**
- Snapshots: lifecycle + summary + quality + coverage
- `INSERT OR REPLACE` write contract + same-session test
- `compute_session_delta(current_session=None)` with no_prior graceful degradation
- `gt health` / `snapshot` / `trends` CLI
- `render_health_text()` + DEFAULT_THRESHOLDS
- Import validation for malformed JSON
- Hook template `session-health.py`
- Export/import roundtrip

**F5 (31 tests):**
- Intent classification: directive/constraint/preference/question/exploration
- Numeric confidence `[0.0, 1.0]` — directive > 0.8, exploration < 0.5
- Related specs as advisory context (separate from classification)
- Full candidate payload: raw_text, classification, confidence, proposed_type, proposed_authority
- Confirm creates spec with proposed type/authority, records confirmed_spec_id
- **Confirm returns F2 impact + F3 quality/tier + F4 constraints** (all three cross-feature paths)
- Reject stores reason
- Intake discriminator filters non-intake deliberations
- Redaction coverage
- CLI smoke: list, confirm, reject
- v10 adoption: scaffold (2), doctor (5), upgrade (3) regression tests
- Legacy spec-classifier.py backward compatibility

---

## Implementation Order

1. F7 first (14 tests)
2. F5 second (31 tests)

## Verification

1. `python -m pytest -q` (509 → ~554 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Request

Codex review requested. GO authorizes Phase 3 implementation.
