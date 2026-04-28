---
name: Verify source before parallel proposals
description: When filing multiple bridge proposals in parallel, each one must independently verify cross-references against actual source code — hallucinated facts surface as Codex NO-GOs and multiply rework. S313.
type: feedback
originSessionId: edd21d0c-c044-4405-902e-57685ce1b332
---
When filing multiple bridge proposals in parallel, each proposal must independently pass a source-verification gate before submission. Cross-references to other slices' classifications, CLI flags of existing tools, schema fields of existing artifacts, and Phase plan §-section requirements must all be checked against the actual file at the actual line, not against my memory of what I think is there.

**Why:** Session S313 — I filed 5 parallel Slice 7-11 proposals. Codex returned 5 NO-GOs. Two were textbook factual errors:
- Slice 7 stated Slice 6 classified `release-candidate-gate.yml` as `framework`. Actual `_release_readiness_split.py:165` writes `classification_signal: "application_release_gate_surface"` (adopter). I had the cross-reference backwards.
- Slice 11 named generator CLI flags `--legacy-root`, `--target-root`, `--dry-data`, `--no-history-update`, `--output-dir`. Running `python scripts/session_self_initialization.py --help` shows actual flags `--project-root`, `--dashboard-dir`, `--history-path`. The flags I named don't exist.

The remaining three NO-GOs (Slice 8 versioning, Slice 9 missing deploy surfaces, Slice 10 sample-vs-full-enumeration) are deeper design gaps but share the root cause — designs not stress-tested against the Phase 8 plan's documented constraints.

This is exactly the failure mode `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` names: AI-driven procedures have higher error rates than mechanical lookups. A `gt cross-reference-verify` service would catch the Slice 7 / Slice 11 class of error before submission.

**How to apply:** Before submitting any bridge proposal that cites another slice, another file's classification, an existing CLI's flags, or a numbered §-section of a plan: read the actual source at the actual line. If filing multiple proposals in parallel, run the verification on every one — parallel filing only saves time when each filing is high quality. If proposals can't be verified in the time available, file them sequentially with verification between each.

The lesson is *not* "don't parallelize." It's "parallel filing requires per-filing source-verification gates."
