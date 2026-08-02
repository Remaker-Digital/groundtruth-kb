REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Prime Builder correction held by exact draft claim row 36026 after physical v008 NO-GO; governed-writer publication by this author session
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5812-goose-governed-filing-attestation
Version: 009
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5812-goose-governed-filing-attestation-008.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5812

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/bridge_author_metadata.py", "scripts/gtkb_session_id.py", "scripts/goose_harness.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_goose_governed_filing.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5812 REVISED Implementation Proposal — Atomic Goose Envelope Mint and Governed Filing

## Revision Disposition

This revision answers every finding in physical version 008 while preserving
the original forward-only eight-target scope. The Goose wrapper no longer
constructs a session id from its own timestamp. It creates the exact Goose
session envelope through the canonical `open_session` operation and injects
the returned `envelope["session_id"]` into the child. The envelope's
`opened_at`, derived id, harness identity, and Prime Builder role provenance
are therefore created by one operation and cannot cross independent clock
samples.

Historical receipt back-fill, poisoned/capability-row recovery, republish, and
durable pending-context recovery remain exclusively delegated to WI-5825. That
thread is currently `NO-GO` at physical version 004; its historical version-002
GO is not current implementation authority.

### Response to F1 — remove the independent timestamp mint

Version 008 correctly found that the version-007 design sampled time in
`goose_harness.py` and later let `envelope open` independently assign
`opened_at`. Crossing a UTC second made the inherited `GOOSE_SESSION_ID`
incompatible with the exact envelope's deterministic id.

The corrected operation is:

1. Before `goose run`, the wrapper calls canonical
   `groundtruth_kb.session.envelope.open_session` with harness `goose`, durable
   id `G`, role `prime-builder`, canonical PB init/subject, and an explicit
   wrapper-launch role-provenance source.
2. `open_session` calls `_base_envelope`, which samples `opened_at` once and,
   because no caller-supplied `session_id` is passed, derives `session_id` from
   that exact same value.
3. The wrapper takes the returned envelope's exact `session_id`; it never
   recomputes or normalizes a timestamp itself.
4. The wrapper copies the child environment and injects
   `GTKB_HARNESS_NAME=goose` and `GOOSE_SESSION_ID=<returned session_id>` before
   spawning `goose run`.
5. A later `gt session envelope open` sees the Goose host binding, loads that
   exact pre-opened per-session document, validates harness, open state, and
   document-authoritative worker-role provenance, and reuses it. It does not
   create a second envelope or resample time.

The wrapper establishes PB role provenance in the original atomic open by
passing `role="prime-builder"` and a non-placeholder
`worker_role_source="goose_wrapper_launch"`. There is deliberately no later
role-authority upgrade from ambient state. An exact pre-opened envelope missing
PB worker-role provenance, carrying another role, closed, or bound to another
harness fails closed when the CLI attempts reuse. Tests cover successful reuse
of the wrapper-created PB envelope and every such rejection.

### Response to F2 — truthful live-chain and governed-candidate evidence

Physical v007 is a live `REVISED` artifact, SHA-256
`f678e187694176c60f1d8d87523ee6a77ea03202a0abc67cedb7d7d735283463`.
Physical v008 is the current strict `NO-GO`, SHA-256
`b951c6fb4b45a3d87182404e63114f577466b3e1370cca6c35daadf8d9f233af`.
All versions 001–008 resolve strict with no quarantine or blocking lifecycle
diagnostic.

Physical v009 does not exist at this pre-filing checkpoint. Prime Builder
session `019fb19b-7814-73c1-8707-204e432cbf00` holds exact draft claim row
`36026` for this slug, acquired `2026-08-01T11:28:20Z` and bounded through
`2026-08-01T12:28:20Z`. Both mandatory preflights are rerun against this exact
claimed candidate before governed-writer publication. Successful filing must
be followed by canonical readback of physical v009 and claim consumption. No
direct bridge write and no TAFE/dispatcher activation or mutation is
authorized.

### Response to F3 — state WI-5825 authority accurately

WI-5825 owns the disjoint five-target recovery implementation, but its physical
latest version is 004 `NO-GO`, SHA-256
`0196ffee147ba11d8ad55163bcf60e82024d222a73c5450c88c196a725d7d6a4`.
Therefore:

1. WI-5812 may proceed only after this corrected revision receives its own
   independent current GO, claim, and start packet.
2. WI-5825 remains a separate later revision/review cycle and cannot implement
   under historical v002.
3. Recovery implementation begins only after WI-5812 lands and WI-5825 has a
   fresh current GO, claim, and start packet.

## Current Authority, Isolation, and Baselines

- `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS` is active.
- Membership `PWM-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WI-5812` v1 is active.
- List-free PAUTH
  `PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730` v1 is
  active, unexpired, and anchored by `DELIB-202667731`; both included and
  excluded work-item lists are null.
- Legacy `work_items.approval_state` is not operation-time implementation
  authority. The active direct-parent project PAUTH is controlling, while
  independent GO, claim, start, exact targets, report, and VERIFIED remain
  mandatory.
- Exact draft claim row `36026` is live for this Prime Builder session through
  `2026-08-01T12:28:20Z`. Before acquisition, the canonical cross-claim target
  evaluator returned no foreign-session overlap for the eight paths; the same
  check must remain clear at implementation start.
- `git status --short -- <eight targets>` returned no output. The new test
  module is absent as planned.

| Target | Current SHA-256 / state |
|---|---|
| `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` | `f843237ed5db443418389a1b3b1276b2d0bf1342f4f9b03d5d0910b7912381dd` |
| `scripts/bridge_author_metadata.py` | `0ac4168859e2e4ff855e860a3c5f6b6a21cb57dc4b7336d624728ee2f741a90d` |
| `scripts/gtkb_session_id.py` | `cc1eac2a7138232adb4b135a9bb81833eb06ac8e146f29f8918fd571a9951d62` |
| `scripts/goose_harness.py` | `fb38e3f4a52b20dce8929b8d1e76c3264843e8118b74e5d19b1ca9b79c140dba` |
| `platform_tests/scripts/test_session_envelope_cli_provenance.py` | `b2c2a41bbc55323c0f362267dfe935c572b02af8da54db01229a3a2472a1e230` |
| `platform_tests/scripts/test_bridge_author_metadata.py` | `39dd96e0987346a68869c0e872331ab7ecea9aa647b0fd247e15130bfdf82097` |
| `platform_tests/scripts/test_gtkb_session_id.py` | `8aeaf094836923d5ada1738f8af81c4b332830789866bcf01495f8717e4c9b77` |
| `platform_tests/scripts/test_goose_governed_filing.py` | absent; planned new module |

Immediately before any later implementation, reread these eight states and run
the same canonical cross-claim overlap check. Drift or an overlap fails closed.

## Proposed Design

### Slice A — exact Goose envelope reuse and attestation

In `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:

- add `goose -> GOOSE_SESSION_ID` to the host/session binding map;
- add `goose-envelope-open-corroboration` as the Goose metadata source;
- when `envelope open` sees `GOOSE_SESSION_ID`, load the exact pre-opened
  document and validate its session id, open state, Goose/G identity, and PB
  worker-role provenance before reuse;
- never create or upgrade role provenance from ambient variables when exact
  provenance is absent or invalid;
- during attestation, require the supplied and ambient ids to equal the exact
  document's id and require that id to equal the canonical derivation from its
  own `harness_id` and `opened_at`;
- preserve all existing model, source, role, harness, and state rejections.

### Slice B — fail-closed author-metadata resolution

In `scripts/bridge_author_metadata.py`:

- register the Goose exact-envelope metadata-source token;
- accept only the exact attested Goose per-session document;
- add `GOOSE_SESSION_ID` to session-context environment resolution;
- preserve six-field completeness, placeholder rejection, source equality,
  explicit/environment/exact-envelope precedence, and the prohibition on
  treating the shared current-session projection as author authority.

### Slice C — deterministic session-id registry

In `scripts/gtkb_session_id.py`:

- add `GOOSE_SESSION_ID` to the frozen recognized set;
- add it at the documented deterministic position in both bridge-work-intent
  and marker-continuity orders without changing the other precedence rules;
- update the full-permutation drift-lock tests.

### Slice D — canonical wrapper mint and child injection

In `scripts/goose_harness.py`:

- open one exact Goose/G PB envelope through `open_session` before each child
  spawn, passing no caller-created session id;
- establish `worker_role_provenance` during that same open with explicit
  `prime-builder` role and `goose_wrapper_launch` source;
- copy the child environment, inject `GTKB_HARNESS_NAME=goose` and the exact
  returned `GOOSE_SESSION_ID`, and pass that environment to `subprocess.run`;
- never independently sample a timestamp or synthesize the id;
- do not launch the child if canonical envelope creation or provenance
  establishment fails.

This slice creates one authoritative exact envelope per wrapper spawn. Broader
cross-process uniqueness/collision enforcement and claim-CLI ambient hardening
remain WI-5815 scope.

## Scope Boundaries

This proposal excludes:

- every WI-5825 capability-row, receipt, back-fill, republish, compensation,
  and pending-context target;
- WI-5815 global uniqueness and claim-CLI hardening;
- dispatcher/TAFE activation, configuration, lease, routing, or mutation;
- schema, MemBase, formal-artifact, credential, external-system, deployment,
  release, push, history rewrite, or destructive-cleanup operations;
- new timeout, TTL, interval, retry, throttle, scheduler, or daemon literals.

## Cross-Harness Disposition

- **Goose:** gains the bounded canonical envelope mint, exact child binding,
  attestation source, and governed-filing tests described above.
- **Codex and Cursor:** existing host-session bindings and attestation sources
  remain byte-for-byte behaviorally unchanged and are covered by adjacent
  regressions.
- **Claude, Antigravity, Ollama, and OpenRouter:** no harness-specific hook,
  launcher, role, or configuration target changes. Shared envelope and metadata
  behavior must remain unchanged under the focused existing test suites.
- No harness exclusion or parity waiver is requested.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — required Goose governed-filing capability floor.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required governed writer and append-only chain authority.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — required exact-session author identity and role provenance.
- `GOV-SESSION-ROLE-AUTHORITY-001` — required document-authoritative role resolution; ambient selectors cannot grant roles.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` — required exact per-session envelope durability and reuse semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active parent-project authority remains operation-time gated.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, and WI linkage is explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every governing source is concretely linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — later verification must execute the mapped behaviors.
- `GOV-ARTIFACT-APPROVAL-001` — no formal-artifact mutation is proposed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all eight targets remain inside `E:\GT-KB`.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — advisory exact-envelope/registry authority.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory deterministic fail-closed gates.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory wrapper mechanics belong in code.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory fresh bridge/project/claim/target reads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory spec/test/evidence linkage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory NO-GO to REVISED lifecycle.
- `GOV-STANDING-BACKLOG-001` — advisory nonduplicated WI-5812/WI-5815/WI-5825 carriers.

## Prior Deliberations

- `DELIB-202667730` — Harness Test synthesis identifying Goose governed-filing exclusion.
- `DELIB-202667731` — active list-free Harness Test Corrections project authorization.
- `DELIB-202667726` — owner mandate for the Harness Test/corrections program.
- `DELIB-202667722` — timer and concurrency direction; no new hard-coded timer is introduced.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — NO-ACTION is corrective routing, not closure.
- `bridge/gtkb-wi5812-goose-governed-filing-attestation-008.md` — independent finding that required the single canonical mint/open operation.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-004.md` — current recovery-thread NO-GO; historical GO is not current authority.

## Owner Decisions / Input

- `DELIB-202667731` is the owner-approved list-free whole-project PAUTH inherited
  by active member WI-5812. Legacy WI `approval_state` is noncontrolling.
- No new owner decision is requested. This revision still requires independent
  GO, a fresh exact claim, start packet, bounded implementation report, and
  independent VERIFIED.
- The owner directed that TAFE/dispatcher remain disabled for repairs. This
  proposal neither activates nor mutates them.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5812 / TEST-11768, the linked
harness-onboarding, author-provenance, role-authority, envelope-durability, and
bridge specifications, plus v008's concrete race evidence, fully determine the
forward correction. WI-5825 separately owns historical recovery. No new or
revised requirement is needed before review.

## Specification-Derived Verification Plan

| Requirement | Required deterministic evidence |
|---|---|
| Canonical single mint/open | Freeze or step the clock across a second boundary; assert wrapper gets the id returned by `open_session`, and its id remains derived from that envelope's single `opened_at` sample. |
| No independent wrapper id | Patch canonical open to return a sentinel exact id; assert child `GOOSE_SESSION_ID` is precisely the sentinel and no wrapper timestamp-derived value appears. |
| Pre-opened PB provenance | Assert wrapper-created envelope contains validated Goose/G `prime-builder` worker-role provenance sourced from `goose_wrapper_launch`; later `envelope open` reuses it. |
| Provenance fail closed | Exact pre-opened envelopes with missing provenance, wrong role, wrong harness/id, wrong session id, or closed state reject without rewrite or child launch. |
| Attestation | Exact derived id succeeds and records `goose-envelope-open-corroboration`; borrowed id and ambient mismatch reject. |
| Six-field author metadata | Attested exact envelope plus exact ambient id resolves all author/session/model/harness fields; unattested/source-mismatch/placeholder paths reject. |
| Session-id drift lock | Frozen set and both precedence tuples include Goose at the declared position without other reordering. |
| Governed filing | Fixture open → reuse → attest → actor resolution → governed proposal dry-run/file validation accepts valid `NEW` and rejects invalid status. |
| Spawn isolation | Two wrapper invocations receive different canonical returned ids and exact per-spawn child environments, without starting external Goose in tests. |
| WI boundaries | Diff inspection shows no WI-5815 claim hardening and no WI-5825 recovery target or behavior. |
| Timer direction | No new hard-coded timeout/TTL/interval/retry/throttle literal. |
| Quality | Focused pytest, Ruff check, Ruff format check, compile, and diff checks pass on the exact cohort. |

Planned focused command:

`python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_goose_governed_filing.py -q --tb=short`

The implementation report must record exact commands and observed results;
planned tests are not execution evidence.

## Acceptance Criteria

1. The wrapper creates one exact Goose/G PB envelope through canonical
   `open_session` before every child spawn and injects only its returned id.
2. A forced second-boundary crossing cannot cause id/opened-at disagreement.
3. Later envelope-open and attestation reuse the exact pre-opened document and
   validate its PB role provenance without ambient authority or rewrite.
4. Missing, wrong-role, wrong-harness, closed, borrowed-id, source-mismatch,
   and ambient-mismatch cases fail before metadata, bridge, or child mutation.
5. Complete Goose author metadata reaches governed filing without the existing
   missing/invalid filing-session identity failure.
6. Existing Codex/Cursor and shared-envelope tests remain green.
7. No WI-5815 or WI-5825 implementation is absorbed, and WI-5825 remains
   blocked pending its own corrected REVISED and new GO after WI-5812 lands.
8. Only the exact eight target paths change; current baselines and overlap are
   reread immediately before implementation.
9. Focused tests, adjacent tests, Ruff lint, Ruff format, compile, and diff
   checks pass with observed evidence.
10. No new hard-coded timer or any dispatcher/TAFE, database, credential,
    external-system, deployment, release, push, or history mutation occurs.

## Risk and Rollback

- **Pre-open side effect before child launch:** envelope creation becomes an
  explicit wrapper prerequisite. If child launch fails, the exact open envelope
  remains durable failure evidence; no fabricated receipt or silent deletion is
  permitted. Later lifecycle cleanup is outside this bounded change.
- **Role overreach:** the wrapper may establish only its declared PB role. Exact
  provenance is validated on reuse; missing or conflicting provenance rejects.
- **Projection confusion:** author authority remains the exact per-session
  document; current projection writes remain compatibility output only.
- **Precedence regression:** full-permutation tests retain all existing order.
- **Recovery duplication:** WI-5825's five paths and behaviors remain excluded.
- **Rollback:** through a governed successor, revert only the four later source
  hunks and four test changes. Do not rewrite envelopes, bridge history,
  capability rows, receipts, or unrelated files.

## Candidate Pre-Filing Preflights

Both mandatory checks must run against this exact non-live candidate after its
final content hash is stable and again immediately before live governed filing.
The results are candidate evidence only, never GO, claim, publication, start,
implementation, or verification authority.

## DISARM — Implementation and Publication Boundary

This candidate authorizes no protected edit. Live filing requires a valid
Prime Builder claim for this exact slug and governed physical publication.
Implementation then requires a new independent GO, fresh `go_implementation`
claim, fresh schema-v3 start packet, exact target/overlap recheck, factual
implementation report, and independent atomic VERIFIED. No direct bridge write,
diagnostic-only database retry, or TAFE/dispatcher activation is authorized.

## Recommended Commit Type

Recommended later implementation type: `feat:` — add canonical Goose envelope,
attestation, and governed-filing capability with fail-closed coverage.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
