REVISED

bridge_kind: prime_proposal
Document: gtkb-wi4522-author-metadata-per-harness-resolution
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T09-10-25Z-prime-builder-B-536c93
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: headless bridge auto-dispatch worker; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4522
target_paths: ["scripts/bridge_author_metadata.py", "platform_tests/scripts/test_bridge_author_metadata.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4522 (REVISED-2): Resolve bridge author metadata at filing time from the filing harness's own context (durable identity + runtime envelope), removing the shared `current.json` baseline

## Revision Scope

This REVISED-2 (`-003`) responds to the Loyal Opposition NO-GO at `-002`. It does
not change the work item, the PAUTH, or the owner-chosen approach
("per-harness resolution at filing time"). It corrects the **design** so the
replacement metadata source is sound: it stops claiming that a durable-identity
lookup can supply the full six-field author metadata set, and it makes the
no-env headless case provenance-safe (fail-closed) rather than silently
inheriting the stale shared file. `target_paths` is adjusted to name the real
existing test module (`platform_tests/scripts/test_bridge_author_metadata.py`)
instead of a non-existent path.

## Response to NO-GO (`-002`)

The NO-GO is **correct and accepted**. Verified against live state:

1. **`harness-state/harness-identities.json`** carries only `id`, `assigned_at`,
   `assigned_by` (and optional `status`) per harness — no model/session fields.
2. **`harness-state/harness-registry.json`** harness records carry
   `harness_name`, `harness_type`, `id`, `invocation_surfaces`, `role`,
   `status`, record `version` — **no `author_model`, `author_model_version`,
   `author_model_configuration`, or `author_session_context_id`**.
3. **`scripts/_kb_attribution.resolve_changed_by`** (the pattern `-001` cited)
   resolves only a `<role>/<harness_name>` LABEL — i.e. at most
   `author_identity` + `author_harness_id`, **2 of the 6 required fields**.

So `-001`'s `_resolve_metadata_from_harness_identity` could never return a
complete `author_*` dict, and would either fail validation or fall back to the
stale `current.json` it was meant to retire — exactly as the NO-GO states.

**Root design finding (the reason `-001` was wrong):** the six `author_*` fields
have **two different lifetimes**:

- **Durable per-harness facts** — `author_identity`, `author_harness_id` — are
  resolvable from the registry per call.
- **Per-session runtime facts** — `author_session_context_id`, `author_model`,
  `author_model_version`, `author_model_configuration` — exist only inside the
  running model session. **No durable GT-KB store holds them, by design.** They
  can only come from the filing harness's own runtime envelope (env vars the
  harness sets for itself, or its self-authored bridge header), or from an
  explicit value threaded by a launcher that knows them.

This REVISED design uses Codex's **acceptable direction #3** (durable registry
for the stable fields; the live runtime envelope for the session/model fields),
which is also the faithful reading of the owner's cycle-12 AUQ — "per-harness
resolution at filing time" means the filing harness resolves **its own** context
at file time, never a shared global cache. It deliberately does **not** adopt
direction #2 ("per-session/per-harness keyed packet"), because the owner
explicitly rejected "key cache by session/harness id" in that AUQ.

**Honest note on the NO-GO's required test.** The NO-GO asks for a test proving
a *complete* stamp "when env vars are unset and stale `current.json` contains
another harness." With env unset **and** no self-authored header, the four
runtime fields have **no per-harness durable source**, so a complete stamp is
impossible without re-introducing either the shared-file hazard or the
owner-rejected keyed cache. The provenance-safe answer in that exact scenario is
to **fail closed (raise)** — never stamp another harness. This proposal proves
the complete-stamp behavior when the runtime envelope **is** populated (the
production reality), and proves fail-closed when it is not. If Loyal Opposition
judges that a complete-stamp-with-env-unset is a hard requirement, that is a
genuine approach-level tension with the owner's rejection of the keyed cache and
should be escalated to the owner rather than resolved by a dispatched worker.

## Summary

WI-4522 (P3, `bridge-protocol`, origin=improvement): `load_author_metadata`
(`scripts/bridge_author_metadata.py:224`) merges a single shared mutable
`.gtkb-state/bridge-author-metadata/current.json` (`:32`, `:237`) as the
lowest-precedence baseline beneath env (`:238`) and explicit (`:239`). As shared
mutable state, the last harness to write `current.json` wins, so a
concurrently-dispatched headless worker whose body lacks embedded metadata and
whose env is unset inherits the previous harness's metadata (the 2026-06-13 S389
incident: a bridge filed by a headless Prime worker was stamped Claude/B while
its prose header self-IDs as Codex/A — a GOV-DOCUMENT-AUTHOR-PROVENANCE-001
inconsistency in the durable record).

The fix replaces the shared baseline with **per-call resolution from the filing
harness's own context**: durable identity fields from the registry, runtime
fields from the live env/explicit envelope, and **fail-closed** when the set is
incomplete — never a silent fall-through to another harness's cached values.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4522 is the backlog authority for this fix
  (P3 bridge-protocol provenance defect). *`CLAUSE-VISIBILITY-BULK-OPS` is
  `not_applicable`:* single-WI scope (one source file + one test module), no
  inventory artifact, no formal-artifact-approval packet, no broad review
  packet; the standard implementation-proposal + LO-review path is the
  appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**,
  **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes
  WI-4522; allows `source` + `test_addition`).
- **GOV-DOCUMENT-AUTHOR-PROVENANCE-001** — the provenance invariant the shared
  `current.json` baseline violates under concurrent harnesses; the per-harness
  fix restores it (fail-closed rather than wrong-stamp).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge (the
  always-applicable bridge-governance trigger); hardens the bridge-authoring
  metadata path without modifying `bridge/INDEX.md` or any workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**,
  **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project /
  work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan
  maps each acceptance criterion to an executed test, including the S389
  concurrent-harness regression and the fail-closed no-source path.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root
  under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory),
  **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory),
  **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked fix to a
  provenance read-surface that GOV-DOCUMENT-AUTHOR-PROVENANCE-001 depends on.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4522 + the S389
repro), the root cause is localized in `load_author_metadata`, the bounded PAUTH
authorizes `source` + `test_addition`, and GOV-DOCUMENT-AUTHOR-PROVENANCE-001
defines the invariant the fix restores. The design finding above
(runtime-vs-durable field lifetimes) is an implementation-design clarification,
not a new requirement; no new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner
  AUQ admitting WI-4522 (and 7 siblings) under `PAUTH-…-BATCH-2`.
- **Cycle-12 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner
  selected "Per-harness resolution at filing time" over "key cache by
  session/harness id" and "defer". This REVISED honors that choice (direction
  #3; not the keyed cache).
- **Loyal Opposition NO-GO `-002` (Codex, harness A, 2026-06-14)** — established
  that durable identity resolution cannot supply the full author metadata set
  and that the no-env headless path must not silently read the stale shared
  baseline. This REVISED accepts and implements that correction.
- **`scripts/_kb_attribution.py` — `resolve_changed_by`** — the canonical
  per-call durable identity resolver this fix mirrors **for the two durable
  fields only** (name + id), not for the runtime fields.
- _Live semantic deliberation search was not run from this headless
  auto-dispatch worker (no interactive `gt deliberations` surface in the
  dispatch context); prior-decision context was gathered from the live bridge
  thread, the cited rule files, and the live harness-state sources instead._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence;
no new owner AskUserQuestion is required to file or implement it. The NO-GO at
`-002` records "Decision Needed: None from the owner. This is a proposal design
correction for Prime Builder," and this REVISED is that correction.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner
  AUQ (2026-06-13) admitting WI-4522 under `PAUTH-…-BATCH-2` (allowed: `source`,
  `test_addition`).
- **Cycle-12 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner
  selected **"Per-harness resolution at filing time"**, the approach this
  REVISED implements (durable identity + own runtime envelope; not a keyed
  cache). The fix stays within `source` + `test_addition` and changes no formal
  artifact, schema, or KB.

*One owner-relevant escalation is flagged but not blocking:* if Loyal Opposition
holds that a complete metadata stamp must be produced even when the filing
harness supplies no runtime envelope (env unset and no self-authored header),
that requirement cannot be met under the owner's rejection of the keyed cache
and would need an owner decision. This REVISED does not assume that requirement;
it implements the provenance-safe fail-closed behavior instead.

## Design

In `scripts/bridge_author_metadata.py`:

1. **New private helper `_resolve_durable_identity_fields(project_root) ->
   dict[str, str]`.** Resolves ONLY the two durable fields — `author_identity`
   (the resolved harness name, label form mirroring `resolve_changed_by`) and
   `author_harness_id` (the registry `id`) — by reusing the existing
   three-source name resolution (`GTKB_HARNESS_NAME` env → single ACTIVE Prime
   Builder) and the registry `id` lookup. Returns `{}` (not `None`) when the
   harness cannot be resolved unambiguously (zero/multiple active Prime
   Builders, or no registry entry), so it contributes nothing rather than a
   wrong value. It NEVER returns the four runtime fields — it cannot, and must
   not pretend to. Import of `_kb_attribution`/`harness_roles` helpers is done
   locally inside the function to avoid a module import cycle, matching the
   existing pattern in `_kb_attribution.py`.

2. **Modify `load_author_metadata` (`:224`).** Replace the `current.json`
   baseline read (`:237`) with `_resolve_durable_identity_fields(root)`.
   Precedence becomes: **durable-identity (2 fields) < env runtime envelope (up
   to 6 fields) < explicit (up to 6 fields)**. The four runtime fields come ONLY
   from env or explicit — the filing harness's own runtime context — never from
   a shared file. `validate_author_metadata` still raises when the merged set is
   incomplete (unchanged), so a missing runtime envelope fails closed instead of
   inheriting another harness's cached values.

3. **Retire `current.json` as a read source.** `load_author_metadata` no longer
   reads `AUTHOR_METADATA_RELATIVE_PATH`. The constant and any out-of-band write
   path may remain for one slice (deprecated, unread by the loader) so external
   tooling that writes it is not broken abruptly; a follow-on slice removes the
   constant and write path entirely once no readers remain. The `_load_json_metadata`
   helper stays (still used for JSON shape errors elsewhere); only the loader's
   read of it is removed.

This is a surgical change at one call site plus one small, side-effect-free
helper. No schema change, no KB mutation, and no API change for callers of
`ensure_author_metadata` (the already-embedded-metadata short-circuit at
`:271-275` is untouched — interactive and self-authoring sessions are
unaffected).

### Headless-worker filing ability (in-scope behavior + tracked follow-on)

After this fix, a dispatched headless worker that (a) does not self-author a
complete `author_*` header AND (b) has no runtime env vars set will **fail
closed** when `ensure_author_metadata` runs, rather than mis-stamping. This is
strictly better than S389 (which produced a wrong stamp) and is the correct
provenance posture. Two complementary paths keep dispatched workers able to
file correctly:

- **Self-authoring (already supported, demonstrated by this very file):** a
  dispatched Prime worker writes its own complete `author_*` header — the
  `ensure_author_metadata` short-circuit returns it unchanged. This REVISED
  proposal itself was filed this way by a headless worker.
- **Dispatcher env injection (follow-on, out of this surgical slice):** the
  cross-harness trigger / single-harness dispatcher can inject the three fields
  it authoritatively knows at spawn (`GTKB_AUTHOR_IDENTITY` = target harness
  name, `GTKB_AUTHOR_HARNESS_ID` = target id, `GTKB_AUTHOR_SESSION_CONTEXT_ID` =
  dispatch id) so a non-self-authoring worker carries its own per-harness
  envelope; the model fields still come from the harness runtime. This touches
  `scripts/cross_harness_bridge_trigger.py` and is deliberately deferred to a
  sibling WI to keep WI-4522 surgical and within its declared `target_paths`.
  It is recorded here as a tracked follow-on, not silently dropped.

## Verification Plan (Specification-Derived)

All tests in `platform_tests/scripts/test_bridge_author_metadata.py` (the
existing canonical module). Fixtures construct a temp `harness-state/` with
`harness-identities.json` + `harness-registry.json` for a single active Prime
Builder, and use `monkeypatch` for env control.

| Acceptance criterion | Test | Method |
|---|---|---|
| Durable fields resolve from the registry per call (2 fields only) | `test_durable_identity_fields_resolve_from_registry` | fixture registry with single active PB (name=claude,id=B) → `_resolve_durable_identity_fields` returns exactly `{author_identity, author_harness_id}`; asserts it does NOT return any runtime field |
| Stale `current.json` is NOT read as a baseline (S389 regression; replaces the old `test_load_author_metadata_uses_project_session_file`) | `test_stale_current_json_is_not_read_as_baseline` | write `current.json` with WRONG-harness metadata (Codex/A) + env runtime envelope for B → `load_author_metadata` returns B's metadata, current.json ignored |
| Env runtime envelope supplies the four runtime fields with durable identity | `test_runtime_envelope_supplies_session_model_fields` | registry resolves identity+id for B; env supplies the 4 runtime fields; current.json wrong → complete correct stamp for B without reading current.json |
| Incomplete sources fail closed, never a wrong stamp (provenance-safe answer to the NO-GO scenario) | `test_incomplete_sources_fail_closed_not_wrong_stamp` | env unset, no self-authored header, registry supplies only 2 fields, stale `current.json`=A present → `validate_author_metadata` RAISES `BridgeAuthorMetadataError` (asserts A's values never appear) |
| Explicit > env > durable-identity precedence preserved | `test_explicit_overrides_env_and_identity` | identity=B + env author_identity=Y + explicit author_identity=Z → explicit Z wins |
| `ensure_author_metadata` short-circuit on already-embedded metadata preserved | `test_embedded_metadata_short_circuit_preserved` | content with complete `author_*` headers → returned unchanged; no identity/env resolution performed |

**Existing-test disposition (explicit, per protected-behavior discipline):**
`test_load_author_metadata_uses_project_session_file` (`:87`) asserts the exact
behavior this fix removes (trusting `current.json` as a complete baseline). It is
**updated in place** — renamed to `test_stale_current_json_is_not_read_as_baseline`
with the corrected assertion — not deleted-for-convenience. It is the test that
codified the S389 hazard, so changing its expectation is spec-first correction
(GOV-06), explicitly surfaced here for reviewer sign-off rather than done
silently. All other existing tests in the module
(`test_author_metadata_gaps_for_bridge_artifact`,
`test_ensure_author_metadata_inserts_after_status_line`,
`test_ensure_author_metadata_rejects_missing_runtime_source`,
`test_ensure_author_metadata_rejects_placeholder_existing_value`) are unchanged
and must continue to pass.

Pre-file code-quality gates (run before the implementation report): `ruff check`
AND `ruff format --check` on both changed files; `python -m pytest
platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short`; plus the
broader bridge-author-metadata-dependent suites
(`test_cross_harness_bridge_trigger.py`,
`test_single_harness_bridge_dispatcher.py`,
`test_dispatch_author_meets_reviewer.py`) must still pass.

## Risk / Rollback

- **Risk: low-moderate.** One source change at one call site + one small helper.
  The fix removes shared mutable state (a concurrency hazard) rather than adding
  one. The `ensure_author_metadata` short-circuit (interactive seeds) is
  preserved unchanged.
- **Behavioral change (bounded, intended):** a non-self-authoring caller in a
  no-env context that previously returned `current.json`'s (possibly wrong)
  metadata will now raise `BridgeAuthorMetadataError`. This is the provenance-safe
  behavior — better to fail loudly than to stamp the wrong harness — and it is
  confined to the exact buggy path (S389). The dispatched-worker filing-ability
  follow-on above restores correct filing for non-self-authoring workers.
- **Rollback:** revert the `load_author_metadata` change + delete
  `_resolve_durable_identity_fields` + restore the original
  `test_load_author_metadata_uses_project_session_file`. No migration, no schema
  change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (concurrent-harness wrong-stamp under
`current.json` sharing) and restores a GOV-DOCUMENT-AUTHOR-PROVENANCE-001
invariant; no new capability surface, no new public API. Per the Conventional
Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
