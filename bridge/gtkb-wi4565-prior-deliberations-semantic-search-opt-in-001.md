NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

# Make propose_bridge/Prior-Deliberations semantic search opt-in and hang-proof (WI-4565)

bridge_kind: implementation_proposal
Document: gtkb-wi4565-prior-deliberations-semantic-search-opt-in
Version: 001 (NEW)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4565

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/skills/test_bridge_propose_helper.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

The bridge-proposal filing helper silently runs a ChromaDB semantic deliberation search on its default-args path, and that search can hang the filing process. This is a docstring-vs-behavior mismatch plus an unbounded-cost defect on the hot proposal-filing path.

Root cause (tri-state `db` handling, `None` auto-opens):
- `groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py:176-181` resolves the `db` argument as: `db is False` -> no semantic search; `db is None` -> `active_db = _try_open_default_db()` (AUTO-OPEN); else use the provided instance. So `db=None` does **not** skip semantic search — it opens the default store.
- `prior_deliberations.py:31-38` `_try_open_default_db()` constructs `KnowledgeDB(DEFAULT_DB_PATH)` ("groundtruth.db"), and `prior_deliberations.py:184-190` then calls `active_db.search_deliberations(query, limit=limit)`.

Default-args propagation (every caller hits auto-open):
- `.claude/skills/bridge-propose/helpers/write_bridge.py:415` declares `db: Any | None = None`; lines 474-481 forward `db=db` into `pre_populate_prior_deliberations` whenever `pre_populate_prior_deliberations=True` (also the default). Therefore `propose_bridge(slug, body)` with no overrides runs a semantic query on every filing — invisible token + latency cost on the hot path.
- A second production caller has the identical latent behavior: `.claude/skills/verify/helpers/write_verdict.py:67-85` (`seed_prior_deliberations`) defaults `db=None` and forwards it, so verdict filing is exposed to the same auto-open.

Docstring-vs-behavior mismatch:
- `write_bridge.py:452-454` documents `db`: "`None` skips semantic search; glossary-source seeding still runs." That statement is **false** against the current `prior_deliberations.py:178-179` code, which auto-opens on `None`. (This is exactly the mismatch WI-4565 reports; the fix makes the code honor the already-correct docstring.)

Where it hangs:
- The `search_deliberations` *query* is already timeout-bounded (`groundtruth-kb/src/groundtruth_kb/db.py:8536-8539`, `_call_with_timeout(..., _CHROMA_QUERY_TIMEOUT_SECONDS=10s)`; FAB-17 / WI-4453 / WI-4519).
- The remaining unbounded step is the **store open / first collection access**: `_try_open_default_db()` -> `KnowledgeDB(...)` -> on first query `_get_chroma_collection()` (`db.py:8265-8286`) constructs `chromadb.PersistentClient(path=...)` and calls `get_or_create_collection(...)`, which can trigger the embedding-function model load. The in-repo comment at `db.py:113-122` explicitly warns this embedding-model step "could hang indefinitely on an offline/stalled embedding step." None of that construction path is wrapped in `_call_with_timeout`. Under a contended deliberation store (observed this session during the WI-4519 always-on-LIKE-merge work), the filing process sat with zero output and no file written for >2 minutes until killed.

This violates `GOV-AUTOMATION-VALUE-VS-COST-001`: an expensive, hang-capable operation (ChromaDB init + semantic query + token cost) is spent unconditionally on the filing hot path with no cheap deterministic gate and no opt-in. It is the read-side analogue of the WI-4453/WI-4519 latency work, which bounded the query but left the auto-open default unguarded.

## Proposed Change

Minimal, source-only. Make semantic search **opt-in** (default off) and bound the explicit auto-open so it can never hang. Preserve glossary-source seeding (deterministic, in-process) and preserve explicit opt-in pre-population.

1. **Stop auto-opening on `None`** — `prior_deliberations.py:176-181`. Re-map the tri-state so the default skips semantic search:
   - `db is None` -> `active_db = None` (NO semantic search; glossary-only seeding still runs). This makes `None` behave like the current `False` and makes `write_bridge.py:453`'s docstring true.
   - `db is True` -> `active_db = _try_open_default_db()` (explicit opt-in to auto-open the default store).
   - any other value -> treat as a live DB instance (unchanged).
   - `db is False` -> `None` (unchanged; preserves the existing explicit-disable contract relied on by tests).
   This is the cheap deterministic gate: callers that want helper-suggested semantic candidates pass `db=True` (or a live instance); the hot default path does zero ChromaDB work.

2. **Bound the explicit auto-open so opt-in cannot hang** — `prior_deliberations.py:31-38` `_try_open_default_db()`. Wrap the `KnowledgeDB(DEFAULT_DB_PATH)` construction in the existing daemon-thread timeout. Lazily import the guard alongside the existing lazy `KnowledgeDB` import already in that function: `from groundtruth_kb.db import KnowledgeDB, _call_with_timeout` and return `_call_with_timeout(lambda: KnowledgeDB(DEFAULT_DB_PATH), _OPEN_DB_TIMEOUT_SECONDS)`, catching `TimeoutError`/`Exception` and returning `None` (graceful degradation to glossary-only). Add a module constant `_OPEN_DB_TIMEOUT_SECONDS = float(os.environ.get("GTKB_DA_OPEN_TIMEOUT_SECONDS") or "10")` near the other defaults (`prior_deliberations.py:16-19`) so it is overridable and consistent with the FAB-17 env-tunable convention. (`import os` already present at `prior_deliberations.py:6`.) This guards the one construction step the FAB-17 query-timeout does not cover.

3. **Correct the helper docstring** — `write_bridge.py:452-454`. Update the `db` parameter doc to state the new contract: "`None` (default) skips semantic search; glossary-source seeding still runs. Pass `db=True` to opt in to a timeout-bounded default-store semantic search, or pass a live `KnowledgeDB` instance." Mirror the one-line behavior note in the `propose_bridge` Phase-0 docstring (`write_bridge.py:421-430`) and in `propose_bridge_codex_non_bypass` (`write_bridge.py:516-534`) if it repeats the claim. No signature change to either public function — `db` stays `Any | bool | None` and the default stays `None`; only the meaning of `None` changes from "auto-open" to "skip," matching the documented contract.

Notes on blast radius:
- Both production callers (`propose_bridge`, `write_verdict.seed_prior_deliberations`) currently rely on the `None` default and never pass a live DB; after the change they get fast, deterministic glossary-only seeding by default and are no longer exposed to the hang. No caller passes a live `KnowledgeDB`, so flipping `None` breaks no real semantic-search consumer.
- The `### Helper-suggested candidates` block (seen in `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-001.md`) is still produced for glossary seeds and for explicit `db=True`/instance opt-in; only the default-args semantic block is removed.
- Existing `db=False` callers/tests (`platform_tests/skills/test_bridge_propose_helper.py:104-150,228-257`) are unaffected — `False` semantics are preserved.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` — governing principle: gate the expensive, hang-capable ChromaDB operation behind a cheap deterministic opt-in instead of spending it unconditionally on the filing hot path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` — WI-4565 is the governed backlog candidate for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed files are under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the helper source and its companion template are lifecycle-coupled surfaces.

## Owner Decisions / Input

- This is project-authorized reliability work under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`; the project-authorization (PAUTH) citation above is finalized by the interactive Prime Builder session per the owner's AskUserQuestion authorization of the unauthorized bridge-tooling defect batch (WI-4565 / WI-4662 / WI-4701). It is a defect remediation against an already-backlogged, owner-governed work item (WI-4565), not new scope.
- No fresh owner decision is required to proceed after Loyal Opposition GO: the change is source-only, additive-to-safe (default flips toward the documented contract), behind graceful degradation, and reversible by a single revert.

## Prior Deliberations

- `DELIB-20265287` — owner_decision (2026-06-19) capturing the "corrected automation value/cost principle"; the owner-decision anchor for `GOV-AUTOMATION-VALUE-VS-COST-001`, which this fix operationalizes in the bridge-authoring read path.
- `DELIB-20263467` — "Loyal Opposition Advisory - WI-4453 ChromaDB Latency" (2026-06-13); the latency lineage this fix continues. WI-4453/WI-4519 bounded the semantic *query*; this proposal closes the remaining unbounded *store-open* default on the filing hot path.
- `DELIB-0802` — VERIFIED `chromadb-semantic-search` bridge thread (the timeout-guard / semantic-search infrastructure this change reuses via `_call_with_timeout`).
- Deliberation search `gt deliberations search "ChromaDB semantic search timeout hang deliberation search fallback bridge proposal filing"` and `"...automation value versus cost gate expensive operation cheap deterministic check default off"` surfaced the anchors above but **no prior decision governs the specific default-arg opt-in policy for `pre_populate_prior_deliberations`**; this proposal does not revisit a previously-rejected approach.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-AUTOMATION-VALUE-VS-COST-001` is the governing requirement; this proposal derives a concrete read-path behavior (opt-in + bounded auto-open) from it. No new specification is required before implementation.

## Specification-Derived Verification Plan

New/extended unit tests in `platform_tests/skills/test_bridge_propose_helper.py` (spec-to-test mapping):

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` — default args do NOT open a DB / do NOT run semantic search | call `pre_populate_prior_deliberations(slug, body)` with `db` omitted (default `None`), monkeypatching `_try_open_default_db` to raise if called | `_try_open_default_db` is never invoked; no `search_deliberations` call; glossary seeds still present; audit log `semantic_search_attempted == False` |
| Default-args `propose_bridge` performs no semantic search | `propose_bridge(slug, body, bridge_dir=...)` with default `db`, `_try_open_default_db` patched to raise | file written; no auto-open; body contains only glossary/placeholder candidates |
| Opt-in preserved — `db=True` auto-opens (bounded) | `pre_populate_prior_deliberations(slug, body, db=True)` with `_try_open_default_db` patched to return a fake DB | fake DB's `search_deliberations` called once; search candidates present |
| Opt-in preserved — live instance still works | existing `test_default_db_path_invokes_semantic_search` (explicit `db=fake_db`) | unchanged: one search call; both fake results present |
| Explicit disable unchanged | existing `db=False` tests | unchanged: no auto-open; glossary-only |
| Bounded auto-open fast-fails instead of hanging | patch `KnowledgeDB` construction to block past `GTKB_DA_OPEN_TIMEOUT_SECONDS` (set low via monkeypatched env) with `db=True` | `_try_open_default_db` returns `None` within the timeout; result degrades to glossary-only; no exception propagates |
| Docstring matches behavior | assert `write_bridge.py` `propose_bridge.__doc__` no longer claims `None` auto-opens / states `db=True` opt-in | docstring contract string present |

Commands:
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper.py -q --tb=short`
- regression: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_propose_helper_work_intent.py platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q --tb=short`
- `ruff check groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py .claude/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py`
- `ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py .claude/skills/bridge-propose/helpers/write_bridge.py platform_tests/skills/test_bridge_propose_helper.py`

## Risk And Rollback

- Risk: an author who relied on the (undocumented) default-args semantic candidates now sees only glossary seeds. Mitigation: this matches the documented contract; semantic candidates remain one explicit `db=True` away, and the `### Helper-suggested candidates` block is still produced for glossary seeds and explicit opt-in. The change reduces silent cost, which is the intent of WI-4565.
- Risk: a template/parity drift between the canonical helper and `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`. Mitigation: the tri-state logic lives in the importable `prior_deliberations.py` (both helpers import it; neither duplicates it), so only the `write_bridge.py` docstring text differs. If `test_bridge_propose_helper.py::test_codex_skill_adapter_parity_check` / `test_template_helper_contains_new_function` flag a hash/string drift, mirror the docstring edit into the template helper as part of this change (no logic divergence).
- Risk: bounding the construction could mask a genuinely-needed semantic result under heavy load. Mitigation: graceful degradation to glossary-only is the existing FAB-17/WI-4519 contract; authors always review and prune `## Prior Deliberations` and run the mandatory `gt deliberations search` themselves per `.claude/rules/deliberation-protocol.md`.
- Rollback: revert the single source commit; the new tests are additive. No state migration; audit-log schema (`semantic_search_attempted`, etc.) unchanged.

## Acceptance Criteria

- [ ] Default-args `propose_bridge` / `pre_populate_prior_deliberations` (`db` omitted) perform NO ChromaDB open and NO `search_deliberations` call; glossary-source seeding and the placeholder path still work.
- [ ] `db=True` opts in to the default-store semantic search; a live `KnowledgeDB` instance still works; `db=False` still disables (unchanged).
- [ ] The explicit auto-open is bounded by `GTKB_DA_OPEN_TIMEOUT_SECONDS` and fast-fails to glossary-only on timeout instead of hanging.
- [ ] `write_bridge.py` `db` docstring matches the implemented behavior (`None` skips; `db=True` opts in).
- [ ] New unit tests pass; `test_bridge_propose_helper_work_intent.py` and `test_verify_prior_deliberations_pre_population.py` regressions pass; `ruff check` + `ruff format --check` clean on all changed files.
- [ ] No change to the `db=False` contract; no signature change to either public helper.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
