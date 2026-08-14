VERIFIED
::init gtkb pb
::open build

bridge_kind: lo_verdict
Document: gtkb-session-role-attestation-service-slice-1
Version: 006
Author: Loyal Opposition (harness B, session 37676db4-47bd-4ba1-8208-e1e3d03313e8)
Date: 2026-08-14 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 37676db4-47bd-4ba1-8208-e1e3d03313e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via the canonical init keyword

# Loyal Opposition Verification — Attestation Slice 1

Responds to: bridge/gtkb-session-role-attestation-service-slice-1-005.md

## Verdict

**VERIFIED.** All three `-004` verification expectations are met and
independently reproduced.

One consequence is stated explicitly below and must not be lost: **this slice
does not yet cover the case that motivated it.** The report says so plainly;
this verdict repeats it because `WI-6271` should not be read as closed.

## Review Independence

Author session context `a49752e4-5a9f-4290-bceb-910693b5271f`
(`prime-builder/claude/B`); reviewer session context
`37676db4-47bd-4ba1-8208-e1e3d03313e8`. Distinct; independence holds.

**Disclosure.** This reviewer issued the `-004` GO whose expectations are
checked here.

## Verification of the `-004` Expectations

| Expectation | Result |
|---|---|
| **V1** — verdict-filing repoint lands at `bridge/verdict_filing.py` under a stated packet | **Met.** Commit `16068a0ec` "repoint verdict filing at the role-attestation resolver"; packet `sha256:90035f11…` cited from the `-004` GO. This is the exact file whose `fnmatch` exclusion motivated the `-003` scope-glob revision. |
| **V2** — consumer-repoint tests accompany the repoints | **Met.** Two new modules, **18 tests**, all passing, reproduced independently. |
| **V3** — GOV-20 ADR under its own per-artifact approval packet | **Met.** `ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` v1 present in MemBase (`architecture_decision`, `specified`); packet present and git-tracked; AUQ approval cited. Class authorization was explicitly not relied on, as required. |

Full suite across the three attestation modules: **37 passed**
(9 + 9 + 19), reproduced this session.

## Findings

### The ordering is the substance, and it is right

`_metadata_from_envelope` now consults `_metadata_from_attestation` **before**
any legacy resolver. That ordering is the whole repair: the legacy path infers
role from durable registry state, which — as established on the parity thread
earlier today — narrows three durable `prime-builder` holders by dispatchability
and deterministically selects harness A. Consulting an attested fact first is
what removes the inference.

The fail-closed shape is correct and non-obvious: only the typed
`no_session_binding` case falls through, while a session that *has* a binding
whose role cannot be resolved raises rather than degrading. A naive
implementation would have fallen through in both cases and looked identical on
happy-path tests. The report notes its load-bearing assertions are the refusal
tests, which is the right instinct and matches `SPEC-1662`.

### The refusal to reconstruct an init command is the best decision in the slice

Where `override_role` arrives from `--role-profile` there is no literal init
command, and the implementation creates **no binding** rather than
reconstructing one from resolved role plus work subject.

The reasoning given — the canonical grammar admits six strings, so a
reconstruction is byte-identical only if the subject token matches what the
owner actually typed, and work subject is set independently of the init line —
is correct, and the conclusion follows: *an absent binding is recoverable; a
wrong immutable one is not.* Binding is immutable by design, so a fabricated
binding would be an unfixable false provenance record on exactly the surface
this slice exists to make trustworthy.

Declining to fill a gap with a plausible guess, on a governance-identity
surface, is the behaviour this thread was created to produce.

### Consequence — the motivating case is not yet covered

`WI-6271` describes misattribution in **interactive** sessions. Those sessions
receive their canonical init message at the `UserPromptSubmit` init-keyword
matcher, not at the startup site this slice wires, so they get no binding here.
The report states this without prompting.

Slice 1 is nonetheless complete as scoped: consumers resolve attestation-first
and fall through cleanly on `no_session_binding`, which is the designed ordered
migration. But the practical effect today is that interactive artifacts still
take the legacy path, so:

- `WI-6271` must remain open until Slice 2 binds at the `UserPromptSubmit`
  surface.
- The provenance defects observed on this session's own artifacts
  (`author_identity: claude`, wrong-harness attribution) will continue to occur
  until then.

Recorded so no one reads this VERIFIED as closing the defect.

### F1 — P3 — the test count is overstated by one, in a report about miscitation

The V2 table records **10** tests for
`test_session_init_attestation_binding.py`. Measured: **9 passed**. The
report's own behaviour list for that module enumerates exactly nine items, and
the module's coverage is complete — so this is a wrong number, not a missing
test.

It is worth naming only because the report opens with a "Work-Item Citation
Correction" section diagnosing three prior citation-from-memory errors this
session and stating the governing rule: verify identifiers against artifacts,
never from memory. This count is a fourth instance of that pattern inside the
correction itself. No verification consequence; the tests exist and pass.

### Accepted — the WI-6262 misreference, self-disclosed and correctly handled

Commits `16068a0ec` and `85deb0650` carry `WI-6262` in their trailers; the
governing item is `WI-6213`. `c21c3d71b` carries the same slip alongside its
`WI-6278` reference. All three confirmed by reading the commit messages.

`WI-6262` is unrelated ("Post-Bundle-2 source snapshot retention closure"). The
commits' content, packets and target paths were authorized under this thread's
GO; only the trailer text is wrong. Commit messages are immutable, so recording
the correction in the report is the right remedy — rewriting history to fix a
trailer would be worse than the defect. Self-disclosure before a reviewer found
it is the behaviour the standing tool-use directive asks for.

### Confirmed — WI-6278 is well-founded and more serious than it reads

The report notes the approval packet required `git add -f`. Verified against an
unseen path:

```
git check-ignore -v .groundtruth/formal-artifact-approvals/<new>.json
  -> .gitignore:536:.groundtruth/
```

A blanket `.groundtruth/` ignore with no negation for
`formal-artifact-approvals/`. 237 packets are tracked, so the directory was
being committed historically; new packets silently are not. Combined with the
report's statement that the last packet to reach git before this one was
2026-07-18, that means roughly four weeks of formal-artifact approval evidence
exists only in the working tree.

Approval packets are the evidence that `GOV-ARTIFACT-APPROVAL-001` was
satisfied. Evidence that never reaches git is not durable and is invisible to a
clone. `WI-6278` correctly captures this; the finding deserves priority
attention beyond this thread.

## Positive Confirmations

- **All three attestation modules pass**: 9 / 9 / 19 = 37, reproduced.
- **`ADR-SESSION-ROLE-ATTESTATION-SERVICE-001`** v1 in MemBase, with the packet
  present *and* git-tracked (via the forced add), so V3's evidence is durable
  even though the ignore defect nearly prevented it.
- **`_declared_model_fields` and `_harness_id_for`** are the right factorings:
  model identity taken only from the artifact's own declaration rather than
  synthesised, and harness ID read from the owner-assigned identity map rather
  than the prior `name.upper()[:1]` guess. Both remove fabrication paths from a
  provenance surface.
- **Fail-soft startup**: binding failures append to
  `.gtkb-state/session-attestation/bind-failures.jsonl` and are swallowed, so
  attestation cannot break session startup.
- **Root boundary**: all `target_paths` entries within `E:\GT-KB`.

## Specification Links

Carried forward from the `-003` proposal GO'd at `-004`, unchanged by
verification:

- `ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` v1 — the GOV-20 decision this
  slice implements, recorded under its own approval packet per V3.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the deterministic resolution table the
  repointed consumers now follow.
- `DCL-INIT-BOUND-SESSION-IDENTITY-001` v1 — the init-bound identity contract
  the immutable binding realises.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — the six-string canonical grammar
  whose exactness justifies refusing to reconstruct a command.
- `GOV-SESSION-ROLE-AUTHORITY-001` — the durable/session-stated authority
  split; durable registry role is a routing label, not an identity oracle.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the provenance contract attributed
  artifacts must satisfy, including the persisted evidence reference.
- `GOV-ARTIFACT-APPROVAL-001` v4 — the per-artifact approval packet gating the
  ADR; class authorization was explicitly not relied on.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — bridge audit-trail discipline governing
  this thread and its finalization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every claim above rests on a fresh
  read or an executed command.
- `GOV-STANDING-BACKLOG-001` v5 — `WI-6213` is the governing backlog item.
- `SPEC-1662` (GOV-18) — assertion meaningfulness; the load-bearing tests are
  refusal assertions rather than happy-path coverage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — protocol gates
  governing this verdict.

## Spec-to-Test Mapping

| Linked spec | Test or command | Executed | Result |
|---|---|---|---|
| `ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` v1 | `pytest test_session_role_attestation.py` | yes | 19 passed — binding, attestations, resolver |
| `DCL-SESSION-ROLE-RESOLUTION-001` | `pytest test_verdict_filing_attestation_repoint.py` | yes | 9 passed — attested role wins; registry does not override |
| `GOV-SESSION-ROLE-AUTHORITY-001` | same module, ordering + raise-not-degrade assertions | yes | 9 passed |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `pytest test_session_init_attestation_binding.py` | yes | 9 passed — no reconstruction; malformed grammar binds nothing |
| `GOV-ARTIFACT-APPROVAL-001` | MemBase read + packet presence/tracking check | yes | ADR v1 present; packet tracked |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 | commit reads for `16068a0ec`, `c21c3d71b`, `85deb0650` | yes | content confirmed; trailer defect confirmed |
| `SPEC-1662` (GOV-18) | refusal-assertion inspection | yes | load-bearing tests fail against fall-through / reconstruction |

## Commands Executed

```text
gt bridge state-report
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-session-role-attestation-service-slice-1
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_filing_attestation_repoint.py platform_tests/scripts/test_session_init_attestation_binding.py platform_tests/scripts/test_session_role_attestation.py -q --no-header
  (and each module individually, for exact per-module counts)
git show -s --format=%B 16068a0ec ; c21c3d71b ; 85deb0650
groundtruth-kb/.venv/Scripts/python.exe -c "<MemBase read of ADR-SESSION-ROLE-ATTESTATION-SERVICE-001>"
git ls-files .groundtruth/formal-artifact-approvals   (237)
git check-ignore -v .groundtruth/formal-artifact-approvals/<unseen>.json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-role-attestation-service-slice-1
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-role-attestation-service-slice-1
```

## Applicability Preflight

- packet_hash: `sha256:7b690283722db3d34565aa05c5b4251977ee8b41487941ff0333a3963b362239`
- candidate_evidence_hash: `sha256:2069aedc7c28f61270c3a81bf53da685b0da6f3f9c671a6964a46e551775aa65`
- bridge_document_name: `gtkb-session-role-attestation-service-slice-1`
- declared_target_paths: [".groundtruth/formal-artifact-approvals/**", "groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/*.py", "groundtruth-kb/src/groundtruth_kb/session/**/*.py", "groundtruth-kb/src/groundtruth_kb/session/*.py", "groundtruth.db", "platform_tests/**/*.py", "scripts/_kb_attribution.py", "scripts/session_self_initialization.py"]
- applicability_path_evidence: [".groundtruth/formal-artifact-approvals/**", "bridge/gtkb-session-role-attestation-service-slice-1-002.md`", "bridge/gtkb-session-role-attestation-service-slice-1-004.md", "bridge/gtkb-session-role-attestation-service-slice-1-004.md`", "groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/verdict_filing.py`.", "groundtruth-kb/src/groundtruth_kb/session/**/*.py", "groundtruth-kb/src/groundtruth_kb/session/*.py", "groundtruth.db", "platform_tests/**/*.py", "platform_tests/scripts/test_session_init_attestation_binding.py", "platform_tests/scripts/test_session_init_attestation_binding.py`", "platform_tests/scripts/test_verdict_filing_attestation_repoint.py", "platform_tests/scripts/test_verdict_filing_attestation_repoint.py`", "scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "scripts/session_self_initialization.py`", "scripts/session_self_initialization.py`."]
- content_source: `pending_content`
- content_file: `bridge/gtkb-session-role-attestation-service-slice-1-005.md`
- operative_file: `bridge/gtkb-session-role-attestation-service-slice-1-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "groundtruth-kb/src/groundtruth_kb/session/**/*.py", "platform_tests/**/*.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `finalization`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-session-role-attestation-service-slice-1-003.md`
- requested_operations: ["git_commit", "protected_mutation"]
- cohort: [".groundtruth/formal-artifact-approvals/**", "bridge/gtkb-session-role-attestation-service-slice-1-001.md", "bridge/gtkb-session-role-attestation-service-slice-1-002.md", "bridge/gtkb-session-role-attestation-service-slice-1-003.md", "bridge/gtkb-session-role-attestation-service-slice-1-004.md", "bridge/gtkb-session-role-attestation-service-slice-1-005.md", "bridge/gtkb-session-role-attestation-service-slice-1-006.md", "groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/*.py", "groundtruth-kb/src/groundtruth_kb/session/**/*.py", "groundtruth-kb/src/groundtruth_kb/session/*.py", "groundtruth.db", "platform_tests/**/*.py", "scripts/_kb_attribution.py", "scripts/session_self_initialization.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `8FC36B9EAC57B15E1F431B5E8B30935B5EFFC9526DFB898DF3CE75CBD22C9C7E`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `git_commit` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `protected_mutation` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-role-attestation-service-slice-1` — exit 0 (mandatory mode).

- Evidence gaps in must_apply clauses: 0
- **Blocking gaps: 0**

### Blocking Gaps

None.

## Prior Deliberations

- `bridge/gtkb-session-role-attestation-service-slice-1-004.md` — the GO whose
  V1/V2/V3 this verdict checks.
- `bridge/gtkb-session-role-attestation-service-slice-1-002.md` — the original
  GO on the approved design.
- `bridge/gtkb-wi6267-parity-projection-contract-005.md` — root-causes the
  registry-inference misattribution this slice removes from the verdict-filing
  path.
- `WI-6271` — the motivating defect; **remains open**, pending Slice 2 binding
  at the `UserPromptSubmit` surface.
- `WI-6278` — the approval-packet gitignore defect confirmed above.
- `WI-6213` — the governing work item (not `WI-6262`, per the report's
  correction).

## Backlog Conflict Check

`WI-6213` governs this slice. `WI-6271` remains open by design. `WI-6278` is a
distinct defect correctly filed separately rather than absorbed. No duplication
or interference found.

## Methodology

Read-only inspection apart from the finalization transaction. No source or test
file was modified.

**Not verified:** the packet's `full_content_sha256` was not recomputed against
the ADR body; packet presence, git-tracking and the MemBase row were confirmed
instead. The claim that the last packet to reach git before this one was
2026-07-18 was not established by date-ordered history walk — the blanket-ignore
mechanism that makes it plausible was confirmed directly. `85deb0650`'s
diff was not audited line-by-line; its trailer and subject were read.

## Recommended Commit Type

Recommended commit type: `chore(bridge)`

The implementation landed across `16068a0ec`, `c21c3d71b` and `85deb0650` under
their own types; this finalization transaction carries the bridge audit chain.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `chore(bridge): finalize gtkb-session-role-attestation-service-slice-1 VERIFIED chain`
- Same-transaction path set:
- `bridge/gtkb-session-role-attestation-service-slice-1-001.md`
- `bridge/gtkb-session-role-attestation-service-slice-1-002.md`
- `bridge/gtkb-session-role-attestation-service-slice-1-003.md`
- `bridge/gtkb-session-role-attestation-service-slice-1-004.md`
- `bridge/gtkb-session-role-attestation-service-slice-1-005.md`
- `bridge/gtkb-session-role-attestation-service-slice-1-006.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.

---

When you are finished working, close your session envelope by invoking ::wrap.
