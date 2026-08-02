NEW
::init gtkb pb
::open build

# WI-5806 — Establish the typed operational-control configuration foundation

bridge_kind: prime_proposal
Document: gtkb-wi5806-operational-control-config-foundation
Version: 001
Date: 2026-08-01 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; host product surface only, with no inferred foundation-model ID; transcript-defined ::init gtkb pb; ordinary per-WI PB authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript, CODEX_INTERNAL_ORIGINATOR_OVERRIDE, and open per-session envelope

Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5806
Related Work Items: WI-5510, WI-5610, WI-5611, WI-5742, WI-5784, WI-5804, WI-5805, WI-5807, WI-5839, WI-5869, WI-5870, WI-5871, WI-5872, WI-5873, WI-5874, WI-5875, WI-5876, WI-5878, WI-5899, WI-5900

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py", "config/governance/operational-controls.toml", "groundtruth-kb/tests/test_operational_control_config.py"]

implementation_scope: source_configuration_and_test_foundation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_mutation_in_scope: false
tafe_mutation_in_scope: false
runtime_activation_in_scope: false

This proposal performs no MemBase or KB mutation, write, insert, change, or
edit; `groundtruth.db` is not an implementation target.

---

## Summary

Create one small, typed, fail-closed resolution service for the operational
control classes named by the owner: timers, TTLs, expiries, grace windows,
timeouts, retry counts and schedules, throttles, rate limits, thresholds,
per-dispatch fan-out, and live-worker concurrency. The service reads one
checked-in catalog that defines types, units, relaxed defaults, tolerance
bounds, environment keys, and cross-control invariants. A governed read surface
creates an immutable snapshot from the exact root `.env.local` file and never
silently substitutes raw process-environment values. Live environment-specific
overrides therefore remain attributable only to the platform `.env.local`
scope established by `GOV-ENV-LOCAL-AUTHORITY-001`.

This is the non-consuming foundation slice. It does not migrate an existing
timer, change any current value, configure or activate the dispatcher, replace
`config/dispatcher/rules.toml`, alter `timer_config.py`, or mutate TAFE. The
initial production catalog carries its schema and policy but no active control
definition; each later consumer slice must add its definition and replace its
legacy literal or split loader in the same governed transaction. That ordering
prevents the new catalog from becoming a second, inert authority while existing
consumers continue to read another value.

## Standing Backlog Bulk-Operation Disposition

This exact slice is not a bulk backlog or project operation. It changes three
new files and no Work Item, project membership, dependency, Test, or production
configuration record during implementation. The owner-directed project-scope
correction and the missing GOV-12 linked Test were completed separately through
the governed CLI before filing: PROJECT-GTKB-TIMER-GOVERNANCE is current v2 and
WI-5806 is current v3 with linked `TEST-11821`.

## Current Baseline And Scope Identity

Current repository HEAD at proposal preparation is
`75decbfa704fe50288aecbc5669def329a0825df`. The exact mutation cohort is clean
and absent:

| Path | Current state | Intended ownership |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py` | absent | immutable catalog model, parser, validation, snapshot, and resolution API |
| `config/governance/operational-controls.toml` | absent | checked-in schema/default catalog; not a live environment-value store |
| `groundtruth-kb/tests/test_operational_control_config.py` | absent | focused contract, failure, bound, invariant, and non-mutation tests |

PROJECT-GTKB-TIMER-GOVERNANCE v2 is active. Its purpose, outcome, and scope now
carry the full `DELIB-202667748` operational-control directive rather than the
obsolete timer-only census outcome. The current list-free project authorization
is `PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730` v2, active and
unexpired. WI-5806 v3 is open/backlogged, an active project member, and links
integration Test `TEST-11821` in `PHASE-002`. No bridge thread or live claim
exists for this slug at preparation time.

The owner-widened project now also carries additive active memberships for
WI-5610, WI-5611, and WI-5510. WI-5510's original Reliability membership is
preserved. These planning links establish project affiliation and PAUTH
eligibility only: every new membership has `membership_order=null`, so the
planned WI-5806 → WI-5610 → WI-5611 → WI-5510 sequence remains
non-authoritative until the governed WI-5899 dependency route or another
independently accepted ordering surface records it. The links do not create
dependencies, change any Work Item, or grant dispatcher mutation authority.

At `2026-08-01T18:29:14Z`, a targeted read found `.git/index.lock` absent. The
foreign zero-byte lock observed earlier disappeared without any mutation by
this session; current absence is not evidence of its owner, remover, or
remediation path. Lock state is rechecked immediately before implementation
and finalization, and a reappearing lock is preserved and routed through its
independently governed remediation rather than deleted, renamed, or adopted.
Any target, project, PAUTH, claim, dependency, or lock-state change invalidates
this baseline and requires fresh canonical readback.

## Requirement Sufficiency

**Existing requirements are sufficient.** `DELIB-202667748` expressly leaves
the `.env.local` versus dedicated-registry choice to implementation. This slice
chooses the least-regret split already compatible with
`GOV-ENV-LOCAL-AUTHORITY-001`: the checked-in TOML is the type/default/invariant
catalog, while `.env.local` remains the only platform live-value authority.
There is no new credential store, dispatcher authority, or managed artifact
type. Existing deterministic-service, freshness, non-impairment, dispatcher
control-surface, project authorization, bridge, and spec-derived verification
requirements fully constrain the implementation.

## Specification Links

- `GOV-ENV-LOCAL-AUTHORITY-001` v2 — root `.env.local` remains the sole platform authority for live environment-specific values; the checked-in catalog may contain only non-secret schemas, keys, bounds, and relaxed defaults.
- `ADR-ENV-SOT-TOPOLOGY-001` v1 — the platform has exactly one environment SoT at root `.env.local`; application SoTs remain lifecycle-independent and cross-scope reads are forbidden.
- `DCL-ENV-CLI-ENFORCEMENT-001` v1, especially A1/A3/A5 — `load_platform_control_environment_snapshot()` is the bounded governed process-start/read surface for this control class, not a general direct-file-read permission. Production consumers use this surface and never embed literal live values; all writes and later environment-schema additions or renames remain governed by `gt env` and are outside this slice.
- `GOV-SOT-SINGLETON-001` — each control definition, relaxed default, live override, unit, bound, and invariant has one declared authoritative home; raw process environment and legacy loaders cannot become competing persistent or mutation authority.
- `GOV-PLATFORM-SOT-REGISTRY-001` v3 — the new load-bearing catalog is already recursively covered by active registry row `governance-config-tree`; registry show/validate evidence is mandatory and no direct registry edit is in scope.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — later dispatcher consumers must expose resolved caps through the governed `gt bridge dispatch` reporting/configuration surface; this foundation neither changes nor activates that surface.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` — direct mutation of dispatcher rules or runtime configuration remains prohibited; neither is a target here.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — resolution, validation, provenance, and failures are deterministic and reusable rather than reimplemented per caller.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — each resolution binds the exact catalog byte hash and the supplied environment snapshot; stale cached summaries are not authority.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — every outer assertion below has current, executable evidence and missing or contradictory evidence cannot pass.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the cross-cutting foundation declares the current authority, measurable before/after behavior, superseded-guidance disposition, hard invariants, and rollback.
- `GOV-STANDING-BACKLOG-001` — WI-5806 and TEST-11821 remain the durable work and acceptance carriers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — owner decisions, the project correction, WI, linked Test, proposal, implementation evidence, and later consumer migrations remain one durable traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the foundation, later consumer migrations, obsolete per-file resolution paths, and terminal evidence retain explicit candidate, active, superseded, verified, and retired states rather than being inferred from file presence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the project envelope never substitutes for independent GO, the exact claim, or a fresh schema-v3 start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — proposal, project authority, and executed verification evidence remain mechanically linked.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered bridge state, role eligibility, independent review, implementation report, and independent terminal verification remain mandatory.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation, configuration, and evidence remain under `E:/GT-KB` and do not depend on harness-local scratch state.

The current registry-wide baseline is intentionally disclosed rather than
misreported as green. At `2026-08-01T18:39:34Z`, `gt registry validate --json`
exited `1` with `coherent=true`, `valid=false`,
`registry_membership_incomplete`, and 22 pre-existing
`unregistered_load_bearing` paths. The SHA-256 of the sorted compact-JSON path
array is
`sha256:7c2814aa730e77804a6c86d3d8c1a1fa1ebdaae83c037a15f4498ec8a6acef69`.
That global debt is outside this three-target slice. Immediately before the
first mutation, implementation captures the exact then-current sorted gap set
as the comparison preimage. Post-change acceptance requires `coherent=true`,
active recursive `governance-config-tree` coverage, the new catalog classified
as registered and absent from the gap set, `post_gaps - pre_gaps = {}`, and
`post_count <= pre_count`. Unrelated concurrent repairs may reduce the set;
this slice may not add to it. A nonzero global validator exit remains disclosed
and is not itself attributed to WI-5806.

## Prior Deliberations

- `DELIB-202667722` — established timers and throttles as a first-class, relaxed-first, measured governance program with one resolution path.
- `DELIB-202667748` — widened the program to retries, thresholds, rate limits, fan-out, and per-harness concurrency; required evidence-triggered correction work and recurring, right-censor-aware tuning.
- `DELIB-202667725` — owner authorization for the list-free Timer Governance project envelope while preserving every per-WI bridge, claim, start, report, and verification gate.
- `DELIB-202667517` — requires highly parallel Prime Builder operation with only short atomic critical sections; a central configuration service must not introduce a global worker leader or long serialization boundary.
- WI-5804 evidence shows the historical `495 literals / 138 files` census is not reproducible. This foundation therefore defines no migration population and does not size values from that number; the deterministic inventory remains WI-5804's separate responsibility.
- WI-5742 and WI-5839 establish the first invariant-coupled timer case. Their current `timer_config.py` and `protected-commit-timers.toml` carriers remain untouched and authoritative until a later, exact consumer-migration proposal replaces them.
- WI-5610, WI-5611, and WI-5510 provide the concrete distinction between per-dispatch item fan-out, per-role worker caps, and per-harness live-worker concurrency. This foundation models those as separate control IDs and units; it does not collapse them into one `max_items` value.

## Owner Decisions / Input

No new owner decision is required to file this proposal. The exact owner
decision in `DELIB-202667748` authorizes the centralized operational-control
direction and delegates the `.env.local` versus dedicated-registry choice to
the program. `DELIB-202667725` supplies the active project envelope. The
proposal chooses `.env.local` for live environment-specific values and a
checked-in typed catalog for non-secret defaults, units, bounds, and invariants.
Protected implementation still requires an independent Loyal Opposition GO,
the exact WI-5806 claim, and a fresh schema-v3 start packet.

## Proposed Configuration Contract

1. Add `operational_control_config.py` as the only generic parser and resolver.
   Callers do not parse the TOML or environment keys independently. The module
   exposes immutable `OperationalControlDefinition`, `OperationalControlCatalog`,
   `ResolvedOperationalControl`, and a typed `OperationalControlConfigError`.
2. The production catalog path is exactly
   `config/governance/operational-controls.toml`. Its top-level
   `schema_version` is closed at `1`. It declares the root `.env.local` scope
   as live override authority but never stores, echoes, or inventories
   credentials or arbitrary environment values. Existing active registry row
   `governance-config-tree` recursively covers the path; the implementation
   must prove coherent coverage with `gt registry show` and `gt registry
   validate` rather than directly editing registry declarations.
3. A control definition has a bounded canonical ID, unique bounded environment
   schema reference, closed numeric kind (`integer` or `decimal`), explicit unit
   (`seconds`, `milliseconds`, `count`, `ratio`, or `percent`), relaxed default,
   inclusive minimum and maximum, category, scope, zero semantics, human
   rationale, tolerance rationale, and migration state. Boolean values,
   untyped strings, NaN, infinity, implicit unit conversion, and duplicate IDs
   or environment references are rejected. An environment reference is not a
   second schema authority: it must bind a versioned non-secret operational-
   control field produced by the governed `gt env` schema surface, use the
   reserved `GTKB_CONTROL_` namespace, and exclude credential/secret-class name
   segments such as `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, and
   `AUTH`. Missing, stale, unverified, cross-scope, or secret-class schema
   bindings fail closed before any `.env.local` value is selected or hashed.
4. The catalog supports bounded relational invariants over declared controls
   using a closed operator vocabulary (`lt`, `lte`, `eq`, `gte`, `gt`) and an
   optional non-negative minimum-separation margin `m` in the same unit. The
   normalized relations are exactly `left + m < right`, `left + m <= right`,
   `left == right`, `left >= right + m`, and `left > right + m`, respectively.
   `eq` permits only an omitted or zero margin; a nonzero `eq` margin is
   rejected rather than interpreted as tolerance. Both sides must exist, use
   compatible kinds and units, and resolve from one immutable catalog and
   environment snapshot. This makes coupled values impossible to validate from
   split reads.
5. Production resolution uses three explicit steps: load the immutable catalog;
   create an immutable `PlatformControlEnvironmentSnapshot` by reading the
   exact root `.env.local` file and retaining only environment keys declared by
   that catalog; then resolve a requested control set from those two snapshots.
   Raw `os.environ`, a caller-supplied mapping, and `scripts/_env.py`'s
   setdefault-mutated process environment are not production authority and are
   never implicitly consulted.
6. Resolution precedence is exactly: key absent from the attested root
   `.env.local` control snapshot means use the checked-in relaxed default; key
   present means parse that exact value. Presence includes an empty or
   whitespace-only value, so those values produce a typed failure and never
   fall back. Any present malformed or out-of-bounds override likewise fails
   closed. Unrelated `.env.local` keys are discarded from the control snapshot
   and never returned. A test-only fixture snapshot carries
   `source_kind=test_fixture`; it cannot be labeled or reported as root
   `.env.local` evidence.
7. Every successful result carries the normalized typed value, unit, source
   class (`platform_env_local` or `catalog_relaxed_default`), control ID,
   catalog schema version, exact catalog SHA-256, definition digest, and the
   bounded control-snapshot provenance/digest. It never returns the entire
   environment, arbitrary key names, or raw values for other controls.
8. `load_operational_control_catalog(project_root)` and
   `load_platform_control_environment_snapshot(project_root, catalog)` resolve
   their exact root-bound canonical paths, reject symlink or non-regular-file
   substitution, read bytes once, parse once, freeze their results, and perform
   no write. The `.env.local` reader retains and hashes only declared control
   key/value pairs, not credentials or unrelated values. Test-only explicit
   path helpers may load bounded temporary fixtures but are not production
   consumer routes.
9. Resource bounds are deterministic: catalog bytes, control count, invariant
   count, key length, environment-name length, prose length, numeric magnitude,
   and decimal precision each have explicit constants and focused rejection
   tests. No regex is evaluated from catalog input and no recursive structure
    is accepted.
   Capacity, fan-out, and live-worker-concurrency definitions have mandatory
   `zero_semantics = "disable"`: resolved cap `0` disables the governed route
   or dimension. A missing applicable definition, unknown control ID, or
   missing/unknown upstream capacity observation needed to compute an effective
   cap fails closed and is never converted to an unlimited or guessed value.
   An explicitly declared, in-bounds catalog relaxed default remains policy,
   not an unknown observation.
10. The initial production catalog contains schema/policy metadata and zero
    active control definitions. Test fixtures exercise the complete definition
    and invariant contract with explicitly test-typed schema bindings. A later
    consumer proposal must first use the governed `gt env` schema-add/read
    surface (or an independently accepted governed equivalent) to create and
    attest the non-secret field, then append only that versioned schema
    reference and switch the consumer in the same governed cycle. The current
    `gt env` surface does not yet expose that general capability, so its absence
    is a fail-closed start hold for every env-backed consumer migration, not
    hidden scope in this foundation. The TOML may not become a second writable
    env schema, add a dormant duplicate value, or switch a consumer without the
    canonical definition and schema binding.
11. Existing `timer_config.py`, `protected-commit-timers.toml`, dispatcher
    rules, environment files, registry control plane, TAFE, and daemon state
    remain byte-identical. No import-time global catalog read is introduced.
    Consumers opt in explicitly in their own reviewed slices.

## Serialization, Dependencies, And Start Holds

This proposal is reviewable now, but implementation is disabled until all of
the following are true at operation time:

1. An independent session has issued GO against these exact proposal bytes and
   target paths. The current Timer Governance PAUTH, v2 project, WI-5806
   membership, TEST-11821 linkage, and Requirement Sufficiency evidence remain
   current and applicable.
2. The exact current session holds the live `go_implementation` claim for this
   slug and has finalized a fresh schema-v3 implementation-start packet naming
   only the three paths above. Claim and start authority are rechecked before
   every protected mutation.
3. A canonical exact-path overlap and cross-claim collision check remains clean.
   The three new paths currently have no bridge declaration or worktree bytes,
   but that fact is re-read rather than assumed.
4. `.git/index.lock` is absent on a fresh targeted read immediately before
   implementation and again before finalization. If it reappears, stop and use
   its independently governed remediation route. This proposal neither
   diagnoses ownership nor removes it, and absence is not credited to this
   session.
5. WI-5804 does not block this parser foundation because no migration census or
   production value is consumed here. It does block any claim that the catalog
   is a complete inventory. WI-5742/WI-5839 do not overlap these paths but keep
   ownership of their existing coupled pair until a later consumer-migration
   cycle.
6. WI-5610, WI-5611, and WI-5510 remain later consumers in that order. Their
   work-item dependencies are not fabricated in proposal prose: canonical
   dependency mutation waits for the generic governed dependency service under
   WI-5899 or another independently accepted route.

No global worker quiescence, global MemBase leader, dispatcher drain, runtime
activation, timer reduction, foreign claim takeover, or unrelated path
reservation is authorized. Catalog resolution is read-only and local; later
mutable configuration surfaces remain short, governed CLI transactions.

## Cross-Harness Disposition

The catalog schema, precedence, value parsing, unit rules, invariant outcome,
resource bounds, provenance, and typed failures are identical for Claude,
Codex, Cursor, Goose, Antigravity, Ollama, OpenRouter, and future registered
harnesses. Harness identity may select a future control ID but cannot alter
parsing semantics or create a harness-local configuration authority. No
scratchpad, session cache, prompt excerpt, or current-pointer file is accepted
as a value source.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "load_operational_control_catalog + load_platform_control_environment_snapshot + resolve_operational_controls",
  "baseline": "Operational controls are resolved by many local constants, TOML readers, environment reads, and implicit precedence rules; timer_config.py is one narrow coupled-pair exception rather than a system-wide service.",
  "canonical_authority": "Root .env.local owns live platform values under GOV-ENV-LOCAL-AUTHORITY-001; config/governance/operational-controls.toml owns only typed definitions, non-secret relaxed defaults, units, bounds, and invariants and is recursively covered by registry row governance-config-tree.",
  "expected_result": "One immutable snapshot deterministically resolves declared controls with explicit provenance and rejects malformed, contradictory, split-snapshot, unknown, secret-class, schema-unbound, or over-bound input.",
  "fail_closed_conditions": [
    "missing, unreadable, oversized, symlinked, or malformed catalog",
    "unknown schema, kind, unit, operator, control, or environment-key duplication",
    "missing required field, invalid decimal, NaN, infinity, excessive precision, or out-of-bound value",
    "present-but-invalid .env.local override",
    "missing, stale, cross-scope, non-governed, or credential/secret-class environment-schema binding",
    "raw or unattested process-environment input on a production route",
    "invariant endpoint, type, unit, relation, or margin failure",
    "stale PAUTH, claim, schema-v3 start, target, or collision evidence before implementation"
  ],
  "hard_invariants": [
    "one live platform-value authority at root .env.local",
    "one generic resolution implementation with no implicit os.environ read",
    "explicit units and bounds for every control",
    "coupled controls resolve and validate from one snapshot",
    "fan-out and active-worker concurrency remain distinct",
    "missing or unknown capacity fails closed and cap zero disables every capacity, fan-out, or live-worker-concurrency route or dimension",
    "no existing consumer or runtime value changes in this foundation"
  ],
  "history_preservation": "Existing specialized loaders and configuration remain current until separately governed consumer migrations replace them; history is cited but not loaded as current generic authority.",
  "provenance": "WI-5806, TEST-11821, DELIB-202667722, DELIB-202667748, PROJECT-GTKB-TIMER-GOVERNANCE v2, and its active list-free PAUTH.",
  "self_descriptive_naming": "operational_control_config names the complete governed class rather than mislabeling concurrency and retry controls as timers.",
  "before_behavior": "Each caller knows its own literal, file, environment key, precedence, unit, and validation rules.",
  "after_behavior": "Later consumers import one resolver and receive a typed value plus exact authority provenance from one catalog/environment snapshot.",
  "essential_context_preservation": "No current value, consumer, dispatcher rule, daemon state, TAFE state, claim, or existing timer configuration is changed.",
  "obsolete_guidance_disposition": "The unreproducible 495/138 census is not used for sizing; max_items is not treated as worker concurrency; per-file environment reads are not copied into new consumers.",
  "rollback": "Remove only the three new files through a separately governed exact-path change; because no consumer changes in this slice, rollback restores the exact pre-slice runtime behavior."
}
```

## Spec-Derived Verification Plan

Linked Test of record: `TEST-11821`, **Operational-control configuration
resolves typed values from one fail-closed source**.

| Assertion | Governing specifications | Required executable evidence |
| --- | --- | --- |
| `WI5806-A1` catalog and authority | `GOV-ENV-LOCAL-AUTHORITY-001`, `ADR-ENV-SOT-TOPOLOGY-001`, `DCL-ENV-CLI-ENFORCEMENT-001` A1/A5, `GOV-SOT-SINGLETON-001`, `GOV-PLATFORM-SOT-REGISTRY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The production catalog is root-bound, regular, schema v1, non-secret, initially has zero active definitions, and is recursively covered by active `governance-config-tree`; exact bytes produce a stable SHA-256. Registry evidence requires coherence, active recursive coverage, the new path classified registered/not a gap, no post-minus-pre load-bearing gaps, and a non-increasing gap count; it does not claim current global validity. The loader is the governed platform process-start/read surface; writes and environment-schema mutation remain `gt env`-governed. Active definitions reject absent/stale/cross-scope bindings and reserved-namespace or secret-class violations before value selection. |
| `WI5806-A2` typed resolution | `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Table-driven fixtures prove integer/decimal kinds, every unit, relaxed-default and attested `.env.local` precedence, stable bounded provenance, unknown-ID rejection, and rejection without fallback for every present-but-invalid override including empty and whitespace-only values; capacity/fan-out/concurrency cap zero disables, and missing/unknown applicable capacity fails closed rather than becoming unlimited. Raw process environment cannot be accepted or labeled as platform `.env.local` authority. |
| `WI5806-A3` invariant snapshot | `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Every normalized operator relation and minimum-separation margin passes/fails at its exact boundary; nonzero `eq` margin, missing endpoints, incompatible kind/unit, duplicate invariant definitions, invalid margins, contradictory relations, and a deliberately split snapshot fail closed. |
| `WI5806-A4` resource and path bounds | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Oversized bytes/collections/strings/numbers/precision, malformed TOML, symlink/non-file/root escape, NaN/infinity, unsupported recursive values, and arbitrary environment leakage are rejected deterministically. |
| `WI5806-A5` non-impairment | `DCL-ENV-CLI-ENFORCEMENT-001` A3/A5, dispatcher specifications, and owner deliberations | Existing `timer_config.py`, protected-commit config, dispatcher rules/runtime, `.env.local`, env schema, registry, and TAFE hashes/state are unchanged; importing the module performs no file or environment read; no consumer imports the new resolver or embeds a live value in this slice. |
| `WI5806-A6` governance gates | project/bridge/verification specifications | Applicability and clause gates pass on exact proposal/report bytes; target/claim/start evidence is current; focused tests and static checks pass; a different session reviews implementation and executed evidence before any terminal disposition. |
| `WI5806-A7` governed env read boundary | `ADR-ENV-SOT-TOPOLOGY-001`, `DCL-ENV-CLI-ENFORCEMENT-001` A1/A3/A5 | Production reads of declared platform control values use only the bounded governed process-start/read surface; direct consumer `.env.local` reads, raw process-environment substitution, cross-scope paths, literal live values, unbound names, and credential/secret-class schema references are rejected or absent. Writes and schema add/rename remain outside this module and exclusively `gt env`-governed; lack of the required schema-add/read capability holds later migrations. |

Required focused commands (use generous outer tool budgets; trust actual test
collection rather than an estimate):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_operational_control_config.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py groundtruth-kb/tests/test_operational_control_config.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py groundtruth-kb/tests/test_operational_control_config.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py groundtruth-kb/tests/test_operational_control_config.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py config/governance/operational-controls.toml groundtruth-kb/tests/test_operational_control_config.py
gt registry show governance-config-tree --json
gt registry validate --json  # current exit 1 is expected; evaluate the disclosed exact non-regression fields, not global VALID
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5806-operational-control-config-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5806-operational-control-config-foundation
```

## Risk / Rollback

The main design risks are accidentally creating a second live-value authority,
silently falling back after a malformed override, allowing a catalog reference
to select/hash a credential, letting coupled values come from different
snapshots, or making a generic loader so broad that unbounded input becomes a
denial-of-service surface. The authority split, empty initial active catalog,
governed non-secret schema binding, reserved namespace, immutable one-read
snapshot, explicit closed vocabularies, resource bounds, and focused negative
tests constrain those risks.

Rollback is additive and narrow: remove the three new files through a separately
governed exact-path change. No existing consumer changes in this slice, so
runtime behavior and all current specialized configuration remain unchanged.
No Git, deployment, dispatcher, TAFE, or production rollback is part of this
proposal.

## Bridge Filing

This is the first status-bearing file for
`gtkb-wi5806-operational-control-config-foundation`. Filing must use the
governed credential-scanned writer and append-only numbered chain. It creates
reviewable bridge state only; it does not activate the dispatcher or TAFE,
change dispatch configuration, acquire an implementation claim, create a
schema-v3 start packet, or touch any implementation target.

## Recommended Commit Type

`feat` — adds the typed operational-control configuration foundation and its
contract tests without changing any existing consumer or runtime value.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
