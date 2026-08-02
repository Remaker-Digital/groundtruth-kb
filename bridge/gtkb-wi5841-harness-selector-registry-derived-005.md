REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; manual physical-bridge continuation; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5841-harness-selector-registry-derived
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5841-harness-selector-registry-derived-004.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5841

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this proposal creates no formal-artifact approval
packet and requires no approval-packet path in `target_paths`.

# REVISED Proposal — Registry-Derived Durable-ID Harness Selector

## Revision Claim

This revision accepts the version-004 correction that version 003 did not
close the thread, accepts the finding that the original implementation is
absent, and corrects the original proposal's incomplete harness count,
two-copy scope, test mapping, and collision sequence. It also corrects the
version-004 approval premise: WI-5841 is an active member of an active project
whose controlling authorization is an active, unexpired, list-free
whole-project PAUTH. The legacy `work_items.approval_state` value is not a
second implementation-approval gate.

No implementation begins from this revision. A fresh independent Loyal
Opposition verdict, current exact work-intent claim, and schema-v3
implementation-start packet remain mandatory after the predecessor sequence
defined below is complete.

## Problem and Corrected Current State

There are eight durable harness identities. The current hard-coded selector in
both operational consumers directly recognizes only Claude and Codex. The six
registered harnesses that otherwise fall through are Antigravity (`C`), Ollama
(`D`), Cursor (`E`), OpenRouter (`F`), Goose (`G`), and Alibaba Cloud Studio
(`H`). The two consumers are:

- `scripts/bridge_work_intent_registry.py`, which gates claim-role resolution;
- `scripts/implementation_authorization.py`, which gates implementation-start
  packet finalization.

The two functions presently have matching visible branch behavior, but only
because a foreign, uncommitted hunk removed `CODEX_HOME` from the registry
copy. That hunk is governed by WI-5877 and is not WI-5841 implementation. The
duplicate functions remain an architectural drift risk even while their
current branch text matches.

The identity SoT already provides a sufficient data schema: each registered
harness has a unique durable `id` mapped to its canonical harness name. It does
not contain per-harness environment-variable lists, and this revision does not
invent or hand-edit such metadata. Runtime producers already expose generic
identity signals: `GTKB_HARNESS_ID` or `GTKB_AUTHOR_HARNESS_ID`. The selector
can map either generic durable ID through the canonical identity reader without
compiling a new harness-name if-chain.

## Requirement Sufficiency

Existing requirements sufficient.

The linked harness-portability, onboarding, provenance, source-of-truth,
project-authorization, bridge, testing, worktree-hygiene, and non-impairment
requirements govern the complete change. No new specification, identity-registry
schema, formal artifact, or owner clarification is required for this four-path
implementation.

## Proposed Change

### S1 — One registry-derived selector contract

Keep one selector implementation in
`scripts/bridge_work_intent_registry.py`. Make the implementation-authorization
consumer delegate to that implementation instead of maintaining an independent
behavioral copy.

The precedence and failure contract will be:

1. A nonblank `GTKB_HARNESS_NAME` remains the highest-precedence explicit
   document selector.
2. `GTKB_BRIDGE_POLLER_RUN_ID` still returns no selector so dispatched work
   cannot inherit the parent harness identity.
3. When either `GTKB_HARNESS_ID` or `GTKB_AUTHOR_HARNESS_ID` is present, map
   the unique supplied ID through
   `groundtruth_kb.harness_projection.read_identity()` to the registered
   harness name.
4. If both generic ID variables are present and disagree, the identity is
   unknown, the durable ID is non-unique, or the canonical identity projection
   is unavailable or malformed, fail closed with a typed diagnostic; never
   choose a harness by guess or registration order.
5. When no generic ID is supplied, retain the live legacy marker fallbacks:
   `CLAUDE_CODE_SESSION_ID` or `CLAUDECODE` selects Claude, and
   `CODEX_THREAD_ID` selects Codex.
6. With no justified selector, return `None` and preserve the canonical
   envelope resolver's exact-match/ambiguity checks.

This is registry-derived because the durable registry supplies the ID-to-name
mapping for every registered harness. Adding another harness identity gives it
the same generic-ID route without adding a selector branch. No direct read of
the JSON file is permitted; committed code must use the canonical reader.

### S2 — Explicitly supersede the obsolete `CODEX_HOME` expectation

Version 001 treated `CODEX_HOME` as a Codex regression surface. WI-5877 and
the current exact foreign hunk establish the corrected contract: a permanent
installation directory is not a live session signal. This revision therefore
requires `CODEX_HOME` alone to select no harness while preserving
`CODEX_THREAD_ID` as the live Codex marker.

WI-5841 will neither overwrite nor attribute the current one-line source hunk.
WI-5877 must govern, verify, and terminalize that correction first.

### S3 — Full-registry and two-consumer regression coverage

The registry tests will enumerate all eight canonical identity records and
prove that each durable ID resolves to the corresponding harness name through
both generic ID variable routes. They will also cover unknown, conflicting,
duplicate, missing, and malformed identity data; explicit-name and poller
precedence; Claude and Codex legacy live markers; `CODEX_HOME` non-selection;
and the no-signal `None` result.

The implementation-authorization selector suite will prove that packet
finalization delegates to the same selector contract and retains fail-closed
worker-envelope provenance validation. It will not duplicate the full mapping
logic in a second implementation.

## Findings Addressed

### F1 — Improper `NO-ACTION` closure

Accepted. Version 003's disposition-close rationale was invalid. This v005 is
the substantive `REVISED` successor requested by version 004. Versions 001
through 004 remain immutable append-only evidence, and the work remains open
until implementation, independent verification, and governed finalization are
complete.

### F2 — Current target evidence does not implement the proposal

Accepted. No registry-derived selector implementation or full-registry
regression exists. The only current registry-source delta is the exact foreign
WI-5877 `CODEX_HOME` removal disclosed below. The expanded four-path scope
covers both operational consumers and their focused tests. No current byte is
claimed as WI-5841 implementation evidence.

### F3 — Incomplete facts, coordination, and approval conclusion

Partially accepted and corrected.

- Accepted: the correct fall-through count is six; the second selector copy
  must be included; the version-001 helper placeholder was invalid; and shared
  target work requires explicit sequencing.
- Corrected: `gt projects show` reports
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` active at version 3, WI-5841 has
  active membership
  `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-5841`, and the cited
  list-free whole-project PAUTH is active at version 2 with no expiry or work
  item allowlist. Under `DELIB-202667719`, `DELIB-202667724`, and
  `DELIB-202667732`, that project authorization controls over the legacy
  `work_items.approval_state` field. No additional WI-specific owner approval
  is required.
- Preserved: WI-5841 remains open and backlogged. A fresh review, claim, and
  start packet are still required; project approval does not bypass them.

## Exact Current Baseline and Foreign-Work Boundary

Fresh SHA-256 values were computed from worktree bytes on 2026-08-01 UTC:

| Path | Current SHA-256 | Git state and ownership |
| --- | --- | --- |
| `scripts/bridge_work_intent_registry.py` | `633e22acff0e6e5b9964827ccac40a3299d7fd513918f24c90469ac9a338f1e3` | Modified. The sole visible diff removes `or os.environ.get("CODEX_HOME")`; HEAD SHA-256 is `792f3fb422706f40819c443eb691ec90874b68c13209030ab7d8fbd2f9484655`. The hunk belongs to WI-5877. |
| `scripts/implementation_authorization.py` | `bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891` | Clean in Git status; no WI-5841 hunk. |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | `f886f15e229ba1bc56e7c2513f67772031459b14a5c49a7c8a258ca23158a5ab` | Clean in Git status; no WI-5841 hunk. |
| `platform_tests/scripts/test_implementation_authorization_harness_selector.py` | `4efa6dee10e42471cc9dd5fedb3db149c7a4e0e1a168f895547c0d688d44ccb1` | Clean in Git status; no WI-5841 hunk. |

An exploratory combined focused run collected 57 tests. One timing-sensitive
WI-5784 contention assertion produced a pre-attempt deadline diagnostic once;
its isolated rerun passed. That result is not selector implementation evidence.
It remains inside WI-5784's exact source/test responsibility and reinforces the
required predecessor order below rather than expanding WI-5841.

## Mandatory Collision and Implementation Sequence

No active work-intent claim currently reserves the four proposed paths, but
absence of a claim does not transfer ownership of foreign bytes or erase live
same-target bridge work.

1. WI-5877 (`gtkb-wi584x-codex-home-harness-selector-false-positive`, current
   v005 `REVISED`) must receive an independent positive verdict, exact
   re-observation, claim/start authority, implementation report, independent
   verification, and terminal finalization. It owns the current one-line
   `CODEX_HOME` hunk.
2. Owner-approved WI-5784 (`gtkb-wi5784-work-intent-claim-lock-retry`, current
   v006 `NO-GO`) must then complete its lawful correction, focused contention
   verification, report, independent verification, and finalization on the
   same registry source/test pair.
3. Immediately before any WI-5841 implementation claim, re-read the current
   heads, claims, target bytes, and collision state for WI-5828, WI-5829,
   WI-5815, WI-5877, and WI-5784. Any live overlapping implementation claim or
   unexplained target delta fails closed.
4. Recompute all four target hashes, obtain a fresh independent verdict on this
   revision, acquire an exact current-session claim, and finalize a schema-v3
   implementation-start packet before modifying any protected target.

The sequence is a start condition, not permission to activate or mutate the
dispatcher or TAFE. Those surfaces remain deliberately disabled and out of
scope.

## Acceptance Criteria

1. Every harness in the canonical identity projection maps from its durable ID
   to its canonical name using either generic live ID variable; no harness name
   is added to a selector if-chain.
2. `GTKB_HARNESS_NAME` remains first in precedence and headless poller presence
   still suppresses inherited selection.
3. Conflicting generic IDs, unknown or duplicate IDs, and unavailable or
   malformed identity data fail closed with a deterministic diagnostic.
4. `CLAUDE_CODE_SESSION_ID` and `CLAUDECODE` continue to select Claude;
   `CODEX_THREAD_ID` continues to select Codex; `CODEX_HOME` alone selects no
   harness.
5. With no justified signal, the selector returns `None` and the canonical
   worker-envelope resolver retains its exact-match and ambiguity behavior.
6. Implementation authorization uses the same selector implementation as the
   work-intent registry; no second behavioral copy remains.
7. The exact four declared paths are the only WI-5841 implementation targets,
   and every pre-existing or concurrently introduced foreign byte is preserved
   or causes a fail-closed revision.
8. Focused selector, claim-role, and implementation-start tests plus Ruff,
   formatting, compile, and exact-scope checks pass before an implementation
   report is filed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5841; NO-GO v004; DELIB-2192; DELIB-202667724; DELIB-202667732",
  "canonical_authority": "The canonical identity reader maps durable harness IDs to names; validated worker-session envelopes remain the sole role authority.",
  "primary_route": "Use explicit GTKB_HARNESS_NAME first, suppress inherited identity for poller work, then resolve a generic durable harness ID through the canonical identity projection, with legacy live markers only as fallback.",
  "before_behavior": "Two duplicated selector functions recognize only Claude and Codex directly; six registered harnesses can fall through and ambiguous envelope lookup can deny otherwise valid claim or start authority.",
  "after_behavior": "One shared selector maps every registered durable ID without per-harness branches, while both consumers preserve explicit, poller, live-marker, and envelope-validation boundaries.",
  "self_descriptive_naming": "Existing GTKB_HARNESS_NAME, GTKB_HARNESS_ID, GTKB_AUTHOR_HARNESS_ID, and worker-harness-selector names describe declaration, durable identity, author identity, and selection roles without new aliases.",
  "obsolete_guidance_disposition": "Version 001's CODEX_HOME regression expectation and five-harness count are superseded by this revision; prior numbered files remain historical evidence.",
  "history_preservation": "All numbered bridge versions, the foreign WI-5877 hunk, current project records, and unrelated worktree bytes are preserved append-only or byte-for-byte.",
  "baseline": {
    "registry_source_sha256": "633e22acff0e6e5b9964827ccac40a3299d7fd513918f24c90469ac9a338f1e3",
    "authorization_source_sha256": "bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891",
    "registry_test_sha256": "f886f15e229ba1bc56e7c2513f67772031459b14a5c49a7c8a258ca23158a5ab",
    "authorization_selector_test_sha256": "4efa6dee10e42471cc9dd5fedb3db149c7a4e0e1a168f895547c0d688d44ccb1"
  },
  "expected_result": {
    "registered_harnesses": "All eight durable IDs have a registry-derived selector route.",
    "role_authority": "Only the validated worker-session envelope supplies role authority.",
    "scope": "Exactly four source/test paths change after predecessor closure and fresh start authorization."
  },
  "rollback": {
    "instructions": "Preserve the bridge/report/verdict chain and perform a separately governed four-path revert to the immediately preceding verified bytes.",
    "verification": "Re-run the same selector, claim-role, packet-finalization, lint, format, compile, and exact-scope checks after rollback."
  },
  "hard_invariants": [
    "A selector chooses a document location but never supplies role authority.",
    "Explicit harness naming remains highest precedence.",
    "Headless poller work never inherits a parent selector.",
    "CODEX_HOME is not a live session signal.",
    "Dispatcher and TAFE remain untouched."
  ],
  "fail_closed_conditions": [
    "Predecessor WI-5877 or WI-5784 is not terminalized.",
    "A generic harness ID conflicts, is unknown, or is non-unique.",
    "The canonical identity projection cannot be validated.",
    "Any target hash, diff, claim, project authorization, or start packet is stale.",
    "Any focused regression or exact-scope check does not pass."
  ],
  "essential_context_preservation": "Keep durable identity selection separate from session-envelope role authority, preserve exact foreign-hunk ownership, and retain the complete append-only bridge and project-authorization history."
}
```

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` — registered harnesses must be able to
  operate under assigned roles without vendor-specific role logic.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — claim and implementation-start
  eligibility are part of the operating capability floor.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — multi-harness role configuration
  must remain portable and registry-aligned.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — durable identity signals select only
  the candidate envelope; provenance remains validated.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the selected worker envelope, not an
  ambient registry role, determines session-role provenance.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the identity projection, claims,
  project authority, and target bytes are freshly re-read at action time.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — implementation
  stays inside active project membership, PAUTH classes, and exact operations.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project approval does not
  replace a fresh verdict, claim, or implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the machine-readable
  project, PAUTH, and WI linkage above is mandatory.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this is the next append-only numbered
  proposal response and requires independent review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every governing
  requirement is linked before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — terminal verification
  requires the specification-derived executed evidence below.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — exact targets, identities,
  precedence, diagnostics, and rollback are mechanically evaluable.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — portability,
  provenance, and failure behavior receive deterministic regression coverage.
- `GOV-WORK-TREE-HYGIENE-001` — foreign dirty bytes retain their owning thread
  and cannot be silently adopted by WI-5841.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the change centralizes selector
  behavior without impairing explicit, poller, Claude, Codex, or envelope paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — findings, owner decisions, predecessor
  holds, proposal, report, and verdict remain a durable lifecycle graph.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all active targets and evidence
  remain inside `E:/GT-KB`.

## Specification-Derived Verification

| Specification or invariant | Deterministic verification | Required result |
| --- | --- | --- |
| Harness portability and onboarding | Parameterize all current `read_identity()` rows through `GTKB_HARNESS_ID` and `GTKB_AUTHOR_HARNESS_ID` in `platform_tests/scripts/test_bridge_work_intent_registry.py`. | All eight IDs resolve to their registered names; no per-harness selector branch exists. |
| Selector precedence | Exercise explicit name plus conflicting generic/live signals; poller plus generic/live signals. | Explicit name wins; poller returns `None`. |
| Fail-closed identity handling | Fixtures for conflicting generic IDs, unknown ID, duplicate ID, missing projection, and malformed projection. | Deterministic typed rejection; no guessed harness. |
| Claude/Codex non-impairment | Fixtures for `CLAUDE_CODE_SESSION_ID`, `CLAUDECODE`, `CODEX_THREAD_ID`, and `CODEX_HOME` alone. | Claude and live Codex markers work; `CODEX_HOME` alone returns `None`. |
| One behavioral implementation | `platform_tests/scripts/test_implementation_authorization_harness_selector.py` exercises implementation-start finalization through the shared selector. | Both consumers produce identical selection and provenance outcomes without duplicated mapping logic. |
| Envelope authority | Selected Prime Builder and Loyal Opposition envelope fixtures with matching and mismatched IDs/session IDs. | Selector narrows location only; the validated envelope supplies the role and mismatches fail closed. |
| Exact scope and quality | Focused pytest, Ruff check/format, compile, `git diff --check`, and exact four-path status inventory. | All checks pass and only the four declared paths contain attributable WI-5841 changes. |

Planned commands after fresh authority and predecessor closure:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
git --no-optional-locks diff --check -- scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py
```

## Prior Deliberations

- `DELIB-2192` — verified harness-registry architecture and canonical durable
  identity context.
- `DELIB-202667719` — project-level authorization controls over legacy
  work-item approval state during the transition, with list-free grants
  controlling when present.
- `DELIB-202667724` — owner authorized the list-free whole-project Bridge
  Protocol Reliability PAUTH.
- `DELIB-202667732` — owner authorized the active v2 repair of that PAUTH while
  preserving its list-free implementation intent.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` — contention must
  receive generous bounded observation and canonical-state rechecks rather
  than duplicate transactions.
- `bridge/gtkb-wi5841-harness-selector-registry-derived-001.md` through
  `-004.md` — complete proposal, verdict, invalid closure, and corrective
  NO-GO chain to which this revision responds.
- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-005.md` —
  current WI-5877 ownership and exact-re-observation plan for the foreign
  `CODEX_HOME` hunk.

## Owner Decisions / Input

- On 2026-07-31 the owner reproduced the Goose claim-provenance failure,
  confirmed that explicit `GTKB_HARNESS_NAME=goose` avoided it, and directed
  the work to be governed rather than left as a per-invocation workaround.
- `DELIB-202667724` and `DELIB-202667732` provide active list-free
  whole-project implementation approval for WI-5841 through its active project
  membership. No separate work-item approval state is required.
- In the current owner transcript, the owner approved exact re-observation of
  the foreign `CODEX_HOME` hunk and explicitly approved WI-5784. Those decisions
  establish the predecessor sequence; they do not transfer either thread's
  bytes to WI-5841.
- The owner directed that TAFE remain disabled for repairs and that long-running
  work receive generous observation under contention. This proposal performs
  no dispatcher or TAFE action and externalizes no new timer.

No further owner decision is requested for this technical revision. Any later
scope expansion into identity-registry records, harness launchers, MemBase, or
additional protected files requires a new revision and any artifact-specific
approval evidence then applicable.

## Risks and Rollback

- **Ambient-ID risk.** A stale or inherited generic ID could point at the wrong
  harness. Mitigation: explicit-name/poller precedence, disagreement checks,
  canonical unique-ID validation, and final envelope validation. A conflict
  fails closed.
- **Registry availability risk.** Identity projection latency or corruption
  could deny selection. Mitigation: generous bounded execution, typed
  diagnostics, no guessed fallback when an explicit generic ID cannot be
  validated, and preservation of legacy live-marker behavior when no generic
  ID is supplied.
- **Cross-consumer regression risk.** Delegation could change implementation-
  start behavior while claim behavior passes. Mitigation: both focused suites
  exercise the shared function through their real consumers.
- **Foreign-hunk risk.** Concurrent predecessor work could change either shared
  source or test. Mitigation: ordered terminalization, exact SHA-256 and diff
  re-observation, collision checks, and a new revision on any unexplained drift.

Rollback preserves this complete numbered bridge history and uses a separately
governed four-path revert to the immediately preceding verified target bytes.
The same specification-derived suite must pass after rollback. Identity records,
MemBase, dispatcher/TAFE state, credentials, Git history, deployment, and release
state are outside both implementation and rollback scope.

## Pre-Filing Preflight

The completed temporary candidate was evaluated with the candidate-content
applicability preflight, mandatory clause preflight, and intended-bridge-path
compliance audit:

- Applicability: passed; `missing_required_specs: []`,
  `missing_advisory_specs: []`, and no blocking errors.
- Project authorization operation-time evaluation: allowed for both
  `implementation_packet_create` and `implementation_start`; all four targets
  classified inside the active PAUTH's source/test classes.
- Mandatory clause gate: exit 0; four clauses `must_apply`, zero evidence gaps,
  and zero blocking gaps.
- Compliance audit: passed with no denial reason for intended path
  `bridge/gtkb-wi5841-harness-selector-registry-derived-005.md`.

These checks must be repeated against the exact publication candidate
immediately before any live filing. Any different result blocks publication;
the temporary draft and these checks create no bridge status or implementation
authority.

## Recommended Commit Type

`fix` — correct cross-harness claim and implementation-start selector behavior
and remove a duplicated behavioral implementation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
