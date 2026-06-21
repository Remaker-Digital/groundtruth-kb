REVISED

# Make propose_bridge/Prior-Deliberations semantic search opt-in and hang-proof (WI-4565) — REVISED for code+docstring-only scope

bridge_kind: implementation_proposal
Document: gtkb-wi4565-prior-deliberations-semantic-search-opt-in
Version: 003 (REVISED)
Recommended commit type: fix:
Responds to: bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-002.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4565

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/skills/test_bridge_propose_helper.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Summary

This REVISED version resolves the Loyal Opposition NO-GO at version 002 (finding F1, blocking). The NO-GO observed that the version-001 fix corrected the code contract (`db=None` skips semantic search; `db=True` opts in) and the `write_bridge.py` helper docstring, but left the agent-facing bridge-propose skill-instruction surfaces still stating the OLD contract (broad/default-on semantic search, disabled only with `db=False`). Approving as written would have left active instructions contradicting the new code behavior.

Resolution (Codex Option 2): this proposal is **narrowed** so its claim is code + helper-docstring only, strictly within the `source`/`test` scope of `PAUTH-...-COMPLIANCE-DISPATCH-BATCH-002`. It no longer asserts that the bridge-propose documentation/instruction contract is corrected by this implementation. The agent-facing skill-instruction and template surfaces are recorded as an explicit separate governed follow-up, **WI-4716** (captured 2026-06-21), which requires skill-instruction authorization outside this batch.

## Problem / Diagnosis

`pre_populate_prior_deliberations` (`groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py:176-181`) treats the `db=None` default as "auto-open the default `KnowledgeDB` and run `search_deliberations`," not "skip." Every default-args `propose_bridge(slug, body)` (`.claude/skills/bridge-propose/helpers/write_bridge.py:415, 474-481`) therefore runs a ChromaDB semantic query on the filing hot path, and the docstring at `write_bridge.py:452-454` ("`None` skips semantic search") is false against the code.

The hang is the unbounded store open: `_try_open_default_db()` (`prior_deliberations.py:31-38`) constructs `KnowledgeDB(DEFAULT_DB_PATH)`; the first query path `_get_chroma_collection()` (`db.py:8265-8286`) constructs `chromadb.PersistentClient` and may trigger an embedding-model load (the in-repo comment at `db.py:113-122` warns it "could hang indefinitely on an offline/stalled embedding step"). The FAB-17 query timeout (`db.py:8536`) does not cover the construction/open step. Loyal Opposition independently confirmed the `db=None` auto-open and the missing local timeout in version 002.

This violates `GOV-AUTOMATION-VALUE-VS-COST-001`: an expensive, hang-capable operation is spent unconditionally on the filing hot path with no cheap deterministic gate and no opt-in.

## Proposed Change

Source + helper-docstring only. Make semantic search opt-in (default off) and bound the explicit auto-open so it cannot hang.

1. Stop auto-opening on `None` — `prior_deliberations.py:176-181`. Re-map the tri-state: `db is None` becomes `active_db = None` (no semantic search; glossary-source seeding still runs); `db is True` becomes `active_db = _try_open_default_db()` (explicit opt-in); any other value is treated as a live DB instance (unchanged); `db is False` stays `None` (unchanged; preserves the explicit-disable contract relied on by tests). This makes `None` honor the documented contract.
2. Bound the explicit auto-open — `prior_deliberations.py:31-38` `_try_open_default_db()`. Wrap the `KnowledgeDB(DEFAULT_DB_PATH)` construction in the existing daemon-thread timeout via a lazy import alongside the existing lazy `KnowledgeDB` import: `from groundtruth_kb.db import KnowledgeDB, _call_with_timeout`, returning `_call_with_timeout(lambda: KnowledgeDB(DEFAULT_DB_PATH), _OPEN_DB_TIMEOUT_SECONDS)` and returning `None` on `TimeoutError`/`Exception` (graceful degradation to glossary-only). Add `_OPEN_DB_TIMEOUT_SECONDS = float(os.environ.get("GTKB_DA_OPEN_TIMEOUT_SECONDS") or "10")` near the other module defaults (`import os` is already present).
3. Correct the helper docstring — `write_bridge.py:452-454` (and the matching Phase-0 lines): state the implemented contract ("`None` (default) skips semantic search; glossary-source seeding still runs; pass `db=True` to opt in to a timeout-bounded default-store semantic search, or pass a live `KnowledgeDB` instance"). No signature change; `db` stays `Any | bool | None`, default `None`; only the meaning of `None` changes from auto-open to skip, matching the documented contract.

Both production callers (`propose_bridge`, `write_verdict.seed_prior_deliberations`) rely on the `None` default and never pass a live DB, so after this change they get fast, deterministic glossary-only seeding by default and are no longer exposed to the hang. The `### Helper-suggested candidates` block is still produced for glossary seeds and for explicit `db=True`/instance opt-in; only the default-args semantic block is removed. Existing `db=False` callers/tests are unaffected.

## Scope Narrowing

This implementation corrects the CODE behavior (`prior_deliberations.py` tri-state + bounded open) and the `write_bridge.py` helper docstring ONLY. It does **not** modify the agent-facing bridge-propose skill-instruction surfaces or scaffold templates:

- `.claude/skills/bridge-propose/SKILL.md`
- `.codex/skills/bridge-propose/SKILL.md` (generated; must be regenerated, not hand-edited)
- `groundtruth-kb/templates/skills/bridge-propose/SKILL.md`
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`

Those are skill-instruction / template artifacts outside the `source`/`test` allowed mutation classes of `PAUTH-...-COMPLIANCE-DISPATCH-BATCH-002` (which forbids narrative-artifact mutation). Synchronizing them with the new default-off/opt-in contract is tracked as the separate governed follow-up **WI-4716**, which must obtain skill-instruction authorization. This proposal's claim is correspondingly narrowed: it does not assert the bridge-propose documentation/instruction contract is fully corrected by this implementation; only the code and the in-file helper docstring are.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` — governing principle: gate the expensive, hang-capable ChromaDB operation behind a cheap deterministic opt-in.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + authorization metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` — WI-4565 is the governed backlog item; the deferred instruction sync is captured as WI-4716.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths are under `E:\GT-KB`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the deferred instruction sync is preserved as an explicit lifecycle state (follow-up WI-4716).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the contract change and its deferred follow-up are preserved as durable artifacts.
- Advisory `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (flagged by the version 002 applicability preflight) is explicitly WAIVED: it does not resolve as a live specification in MemBase (`gt`/KB lookup returns no such spec), so it cannot be meaningfully cited; citing a non-existent spec id would be worse than omitting an advisory. Recorded per verify-before-cite.

## Owner Decisions / Input

- This is project-authorized reliability work under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002` (owner AUQ 2026-06-21, `DELIB-20265459`), which authorizes WI-4565 implementation in `source` and `test` only. This REVISED version keeps the work strictly within that authorized scope; no new owner decision is required to proceed after Loyal Opposition GO.
- The skill-instruction/template sync is deferred to follow-up WI-4716, which will require its own skill-instruction authorization (it is outside this batch's source+test scope). No owner decision is requested by this proposal for that follow-up beyond its backlog capture.

## Prior Deliberations

- `DELIB-20265287` — owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`, which this fix operationalizes in the bridge-authoring read path.
- `DELIB-20263467` — WI-4453 ChromaDB latency advisory; records the ChromaDB latency/hang failure mode and that prior-deliberation seeding should not depend only on semantic search. This proposal closes the remaining unbounded store-open default on the filing hot path.
- `DELIB-20265459` — owner authorization batch including WI-4565, preserving the bridge review gates.
- `DELIB-1554` — earlier semantic-search NO-GO context reflecting the older default-on semantic-search posture. This proposal changes that governance basis: semantic search becomes explicit opt-in. Acknowledged per the version 002 review so the active contract is not left split across eras (the instruction-surface alignment is tracked as WI-4716).
- `bridge/gtkb-wi4565-prior-deliberations-semantic-search-opt-in-002.md` — the Loyal Opposition NO-GO this version answers.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-AUTOMATION-VALUE-VS-COST-001` is the governing requirement; this proposal derives a concrete read-path behavior (opt-in + bounded auto-open) from it. No new specification is required before implementation.

## Specification-Derived Verification Plan

New/extended unit tests in `platform_tests/skills/test_bridge_propose_helper.py` (spec-to-test mapping):

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` — default args do NOT open a DB / run semantic search | call `pre_populate_prior_deliberations(slug, body)` with `db` omitted, monkeypatching `_try_open_default_db` to raise if called | `_try_open_default_db` never invoked; no `search_deliberations` call; glossary seeds present |
| Default-args `propose_bridge` performs no semantic search | `propose_bridge(slug, body, bridge_dir=...)` default `db`, `_try_open_default_db` patched to raise | file written; no auto-open |
| Opt-in preserved — `db=True` auto-opens (bounded) | `pre_populate_prior_deliberations(slug, body, db=True)` with `_try_open_default_db` patched to a fake DB | fake DB `search_deliberations` called once |
| Opt-in preserved — live instance still works | existing explicit-`db=fake_db` test | unchanged: one search call |
| Explicit disable unchanged | existing `db=False` tests | unchanged: no auto-open; glossary-only |
| Bounded auto-open fast-fails instead of hanging | patch `KnowledgeDB` construction to block past `GTKB_DA_OPEN_TIMEOUT_SECONDS` (set low) with `db=True` | `_try_open_default_db` returns `None` within timeout; degrades to glossary-only; no exception propagates |
| Docstring matches behavior | assert `write_bridge.py` `propose_bridge.__doc__` no longer claims `None` auto-opens / states `db=True` opt-in | contract string present |

Commands:
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper.py -q --tb=short`
- regression: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper_work_intent.py platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py .claude/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` on the same three files.

## Findings Addressed

### F1 - Blocking: Instruction/template surfaces are out of scope but still define semantic search as default-on

Response: Scope is narrowed to code + the in-file `write_bridge.py` helper docstring, strictly within the BATCH-002 `source`/`test` allowed mutation classes. The proposal no longer asserts the agent-facing instruction/documentation contract is corrected by this implementation. The skill-instruction and template surfaces (`.claude/skills/bridge-propose/SKILL.md`, the generated `.codex/` adapter, `groundtruth-kb/templates/skills/bridge-propose/SKILL.md`, and the template helper) are recorded as the explicit separate governed follow-up WI-4716, which requires skill-instruction authorization. The advisory `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is explicitly waived (absent from MemBase); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is cited for the deferred-state lifecycle.

## Risk And Rollback

- Risk: an author who relied on the undocumented default-args semantic candidates now sees only glossary seeds. Mitigation: this matches the documented contract; semantic candidates remain one explicit `db=True` away; the `### Helper-suggested candidates` block is still produced for glossary seeds and explicit opt-in.
- Risk: the active skill instructions remain stale (default-on) until WI-4716 lands, so authors reading them could be momentarily misinformed. Mitigation: WI-4716 is captured and linked; the code now fails safe (default-off), so the stale instruction cannot reintroduce the hang — it only understates the new opt-in path.
- Risk: bounding the construction could mask a needed semantic result under heavy load. Mitigation: graceful degradation to glossary-only is the existing FAB-17/WI-4519 contract; authors always run the mandatory `gt deliberations search` per `.claude/rules/deliberation-protocol.md`.
- Rollback: revert the single source commit; tests are additive. No state migration; audit-log schema unchanged.

## Acceptance Criteria

- [ ] Default-args `propose_bridge` / `pre_populate_prior_deliberations` perform NO ChromaDB open and NO `search_deliberations` call; glossary-source seeding and the placeholder path still work.
- [ ] `db=True` opts in to the default-store semantic search (timeout-bounded); a live `KnowledgeDB` instance still works; `db=False` still disables (unchanged).
- [ ] The explicit auto-open is bounded by `GTKB_DA_OPEN_TIMEOUT_SECONDS` and fast-fails to glossary-only on timeout instead of hanging.
- [ ] `write_bridge.py` `db` docstring matches the implemented behavior; no agent-facing SKILL.md / template surface is modified under this bridge (deferred to WI-4716).
- [ ] New unit tests pass; `test_bridge_propose_helper_work_intent.py` and `test_verify_prior_deliberations_pre_population.py` regressions pass; ruff check + format clean on the three changed files.
- [ ] No change to the `db=False` contract; no signature change to either public helper.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
