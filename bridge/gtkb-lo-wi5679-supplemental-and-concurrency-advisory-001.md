ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 47a4ab5b-ea88-4ff2-8ac0-0d7cb0a85e61
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory - Supplemental WI-5679 Review Findings Stranded By A Concurrent Verdict, Plus Two Defects Found In The Process

bridge_kind: governance_advisory
Document: gtkb-lo-wi5679-supplemental-and-concurrency-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

## Source

Produced during a scheduled Loyal Opposition run on 2026-07-28 that completed a
full review of `bridge/gtkb-wi5679-session-role-keying-continuity-003.md` and
then found the `-004` verdict slot already taken by a concurrent Loyal
Opposition session (`6a29f0bd-92ac-4c8f-abdf-912a0dd69c86`). Filing a competing
verdict would corrupt the append-only lifecycle, so the findings are preserved
here instead.

Every claim below was executed by this reviewer against clean HEAD `4efcb0ee2`
using this repository's own tooling.

## Claim

### Group A - WI-5679 findings not present in the filed `-004` verdict

The filed `-004` is a well-formed NO-GO and reaches one substantive finding this
reviewer did **not** reach (its F1: clause C2 relaxing session-id-keyed
provenance authority). This group is complementary, not competing. Its F2
overlaps A1 but states a weaker claim - that the baseline *excludes a module* -
where the actual defect is that the disclosed numbers do not reproduce at all.

#### A1 (P1). The `-003` baseline disclosure does not reproduce

`-003` line 324 records "a fresh 68-test focused run produced 64 passed and 4
failed." Running the exact command set `-003` declares (seven of its eight files
exist; `test_session_role_keying_continuity.py` is a to-be-created target):

```text
7 failed, 135 passed, 2 warnings in 244.34s
```

**142 tests, 7 failures** - not 68 and 4. Five failures are undisclosed:

```text
FAILED test_session_self_initialization.py::test_startup_model_contains_role_governance_and_kpi_inventory
FAILED test_session_self_initialization.py::test_cursor_harness_emit_resolves_default_lifecycle_guard
FAILED test_dcl_role_resolution_authority_001.py::test_gov_session_role_authority_001_dispatcher_only
FAILED test_dcl_role_resolution_authority_001.py::test_dcl_session_role_resolution_001_enforcement_gate_split
FAILED test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity
```

The two failures `-003` *does* attribute come from `test_session_envelope_runtime.py`,
a file absent from its declared command set. Two of the undisclosed failures are
in the test module for `scripts/session_self_initialization.py` - a declared
`target_paths` entry - creating an attribution hazard at verification time.

This makes `-003`'s own instruction ("The implementation report must rerun and
disclose both baselines rather than relabeling unrelated failures as fixed")
unexecutable as written.

#### A2 (P1). The specification retirement `-003` relies on has already broken an active test

```text
FAILED test_dcl_role_resolution_authority_001.py::test_gov_session_role_authority_001_dispatcher_only
AssertionError: GOV-SESSION-ROLE-AUTHORITY-001 description missing
  '## Dispatcher-Only Registry Authority' section (DELIB-20265878).
```

`GOV-SESSION-ROLE-AUTHORITY-001` is v6, `retired` - which is `-003`'s premise for
the PAUTH v2 amendment. But `DELIB-202667220` requires that "Active rules,
manifests, interface maps, generated projections, **tests**, and runtime-facing
documentation must stop citing the retired specification as authority. A
deterministic post-change scan must prove zero active references." This test is a
live active reference; the mandated scan obligation is unmet. `-003` runs this
exact test in its own command set without disclosing the failure.

#### A3 (P1). A specification cited as governing authority fails its own conformance test

```text
FAILED test_dcl_role_resolution_authority_001.py::test_dcl_session_role_resolution_001_enforcement_gate_split
AssertionError: DCL-SESSION-ROLE-RESOLUTION-001 description missing assertion 8
  'assertion_registry_not_authority_for_enforcement_gates' (WI-4781).
```

`DCL-SESSION-ROLE-RESOLUTION-001` is in the PAUTH `included_spec_ids`, in
`-003`'s `## Specification Links`, and a mapped row in its verification plan.

#### A4 (P2). The parity specs were added to the proposal but not to the authorization

`-003` closed the `-002` parity finding by adding
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` to
its links and verification plan. The authorization was not updated. Live read of
`current_project_authorizations` for
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724`
v2:

```text
included_spec_ids = ["DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001",
                     "ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001",
                     "DCL-SESSION-ROLE-RESOLUTION-001",
                     "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001"]
```

Neither parity spec is present. Read against
`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`, the proposal and the
authorization now disagree about what governs the work.

#### A5 (P2). C4's acceptance criterion tests parser agreement, not specification conformance

`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 states: "The first-line-only
constraint (regex anchors `^...$`) is unchanged; the keyword MUST appear as the
entire first line of the owner prompt." Both parsers executed head-to-head:

```text
'::init gtkb pb'                -> anchored: MATCH | envelope: MATCH
'::init gtkb pb\n'              -> anchored: MATCH | envelope: None
'::init gtkb pb\r\n'            -> anchored: None  | envelope: None
'::init gtkb pb\n::open build'  -> anchored: None  | envelope: None
'::init gtkb pb\nDo the thing.' -> anchored: None  | envelope: None
'::init gtkb'                   -> anchored: MATCH | envelope: MATCH
```

`CANONICAL_INIT_KEYWORD_REGEX` carries no `re.M`, so `$` anchors at end of
string: it is a **whole-string** grammar, not a first-line grammar. Neither
parser matches a canonical keyword followed by a further line - the two cases the
spec says MUST match. C4's acceptance criterion ("both parsers agree on the
complete matrix") can therefore pass in full while the cited spec stays violated.

The spec's own quoted regex does not implement its own prose constraint, so
"converge on the anchored grammar" is ambiguous about which of the two to
converge on. That ambiguity is worth resolving at the spec level, not per-thread.

#### A6 (P2). An open governance question was closed by deletion

`-001` disclosed an allow-list edit and asked Loyal Opposition to "confirm
whether it requires its own retrospective bridge record." `-003` states it does
not cite "an unarchived allow-list edit" and removes the disclosure. The edit is
real and in the repository:

```text
git show db07f9dcf -- config/governance/lo-file-safety.toml
 allow_patterns = [
   "memory/MEMORY.md",
-]
+  ".gtkb-state/propose-drafts/**",
+  ".gtkb-state/owner-decisions/**",
+]
```

Commit subject: `Synching backlog`. No bridge reference, no work item, no
governance citation. This is a widening of a Loyal Opposition file-safety control
surface, and it is currently load-bearing - it is the only reason a Loyal
Opposition session can draft a verdict body at all. The change looks defensible
on its merits; it needs a record, not a reversal, and probably its own thread.

#### A7 (P3). An active-harness parity contract is red inside the declared command set

`test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity`
fails on harness `goose`. `-003` invokes both parity specs as governing authority
and runs this contract in its own command set without mentioning it. Whether
goose parity belongs to this thread is arguable; the silence is not.

### Group B - Defects found while performing the review

#### B1 (P2). Two Loyal Opposition scheduled sessions processed the same queue concurrently, duplicating full reviews

On 2026-07-28 this session and session `9f51b71b-...` independently and
simultaneously reviewed `gtkb-wi5659-...-v2-005`; both reached VERIFIED on the
same evidence. Later this session and session `6a29f0bd-...` independently
reviewed `gtkb-wi5679-...-003`; both reached NO-GO. In each case one full review -
including multi-minute test suites - was discarded.

The work-intent claim system did not prevent either collision. Claims carry a
10-minute TTL and are described as protecting *drafting*; a review that spends
four minutes running the declared test set and longer reading the chain outlives
its claim before the verdict is written. Observed directly:
`.gtkb-state/work-intent/` was empty at several points during active review work
on claimed threads.

The cost is not merely tokens. Concurrent finalization is also how terminal
verdicts end up stranded (see B2 in
`bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`,
and the three occurrences this session had to hand-complete).

**Recommended action.** Either give the claim a TTL matched to realistic review
duration with explicit renewal on progress, or add a cheap pre-verdict re-check
("is the next version slot still free?") before a reviewer commits to expensive
verification. The second is the smaller change and would have avoided both
collisions.

#### B2 (P2). The concurrently-filed `-004` verdict cites a project authorization and project that do not exist

`bridge/gtkb-wi5679-session-role-keying-continuity-004.md` header declares:

```text
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5679-SESSION-ROLE-KEYING-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
```

Live MemBase reads:

```text
PAUTHs matching WI5679:
  PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724 (v2, active)
HOUSEKEEPING-HARDENING-WI5679 variant: NOT FOUND
WI-5679 project_name: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
```

Both the cited PAUTH id and the cited project are phantoms; WI-5679 belongs to
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`. Impact is bounded - the verdict is a
NO-GO, so it authorizes nothing, and the miscitation is in header metadata rather
than in a finding - but it is a false linkage claim in an append-only governance
artifact, and no gate caught it.

**Recommended action.** Two options, not mutually exclusive: (a) have the filing
Loyal Opposition session append a corrected successor verdict noting the
metadata error; (b) extend the applicability preflight or the bridge-compliance
gate to resolve `Project Authorization` and `Project` against MemBase and fail
on a non-existent id. Option (b) is the durable fix and would have caught this
mechanically. Note that verdict files are currently exempt from the
project-linkage gate by status, which is why nothing checked it.

## Owner Decision Needed

None blocking. This advisory records evidence and recommendations; it authorizes
no implementation.

## Recommended Prime Action

Group A should be folded into the next WI-5679 `REVISED` alongside the filed
`-004` findings - A1 through A3 are blocking-grade and none is reached by that
verdict. Group B items are platform-level and warrant their own work items: B1
pairs naturally with the existing finalization-concurrency advisory, and B2 is a
small, well-bounded gate extension.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes for Group B. B1 implies a change to the work-intent claim TTL/renewal
semantics or the addition of a pre-verdict slot re-check; B2 implies extending a
preflight or compliance gate to resolve project-linkage metadata against MemBase.
Group A implies no new implementation beyond the WI-5679 revision already in
flight.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to:

1. Should concurrent Loyal Opposition scheduled sessions be prevented
   structurally (claim TTL/renewal, or a pre-verdict slot re-check), or is
   duplicated review an acceptable cost of parallel reviewers? The two mechanisms
   have very different blast radii.
2. Should `Project Authorization` and `Project` header values be resolved against
   MemBase by a gate, and should that gate extend to verdict files - which are
   currently exempt from project-linkage checking by status?
3. Does the `config/governance/lo-file-safety.toml` widening (A6) require a
   retrospective governance record, and if so under which thread?

### Required durable owner decisions

- Scope decision on B1: which concurrency mechanism, if any.
- Scope decision on B2: gate extension and whether verdict files lose their
  project-linkage exemption.
- Disposition of the A6 allow-list widening.

## Prior Deliberations

- `bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md` -
  the existing advisory on stranded terminal verdicts; B1 supplies further
  recurrence evidence.
- `bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md` - this
  reviewer's earlier advisory this session on verdict-authoring friction; B2 is
  adjacent to its C1.
- `DELIB-202667220` - the retirement directive whose zero-active-reference scan
  obligation A2 shows is unmet.
- `DELIB-202667477` - the five-Decision owner record governing WI-5679 scope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the governance basis for A4.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the basis for preferring a
  mechanical gate (B2) over reviewer vigilance.

## Classification Slot

Recommended Prime Builder classification: `adopt` for A1-A3 (fold into the
in-flight WI-5679 revision), `adapt` for B1 and B2 (mechanism choice is an owner
decision), `monitor` for A5 and A7, and `defer` for A6 pending its own thread.

## Non-Approval Semantics

This ADVISORY is not an implementation approval and confers no implementation
authority. It creates no work-item authorization. Any derived work requires a
normal implementation proposal, Loyal Opposition review, and bridge `GO`, plus
the owner decisions enumerated above.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
