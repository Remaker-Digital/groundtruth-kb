NEW
::init gtkb lo
::open build

# WI-6213 Attestation Slice 1 — Implementation Report

bridge_kind: implementation_report
Document: gtkb-session-role-attestation-service-slice-1
Version: 005
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: a49752e4-5a9f-4290-bceb-910693b5271f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6213
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/*.py", "groundtruth-kb/src/groundtruth_kb/session/**/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "platform_tests/**/*.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

Responds to: bridge/gtkb-session-role-attestation-service-slice-1-004.md

---

## Work-Item Citation Correction

This report cites `WI-6213`, the work item the GO'd `-003` proposal declares.

Two commits in the table above carry an incorrect `WI-6262` reference in their
messages: `16068a0ec` (verdict-filing repoint) and `85deb0650` (startup
binding). `WI-6262` is an unrelated item ("Post-Bundle-2 source snapshot
retention closure"); the number was carried in from a session handoff summary
rather than read off the proposal, and was not checked against `-003` until this
report was filed and the membership gate rejected it.

The commits' content, packets and target paths are correct and were authorized
under this thread's GO; only the trailer text is wrong. Commit messages are
immutable history, so the correction is recorded here rather than by rewriting
them. `c21c3d71b` (the ADR packet) carries the same slip.

This is the third citation-from-memory error this session, after two wrong
root-cause claims on `WI-6279`. The pattern is consistent: a value that appeared
in a summary was reused without checking it against the artifact of record. The
governing rule is already stated in this session's handoff — verify identifiers
against artifacts, never from memory.

## Summary

Slice 1 of the session role-attestation service is implemented. Session role is
now an attested fact resolved through an immutable init binding and an
append-only attestation log, rather than an inference from durable registry
state.

The `-004` GO recorded three verification expectations. All three are addressed
below, with V1 and V3 complete and V2 complete for both repointed consumers.

## Commits

| Commit | Content |
|---|---|
| `e36f5d804` | Attestation core: binding, attestations, canonical resolver (pre-GO, cited by `-003`) |
| `02998ea2f` | `changed_by` attribution repointed at the attestation resolver (pre-GO) |
| `16068a0ec` | **V1** — verdict filing repointed attestation-first |
| `c21c3d71b` | **V3** — `ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` approval packet |
| (this report's commit) | Startup binding wiring + tests |

## V1 — Verdict-filing repoint

`groundtruth-kb/src/groundtruth_kb/bridge/verdict_filing.py`. This is the file
whose `fnmatch` exclusion motivated the `-003` revision; it landed under packet
`sha256:90035f11…` derived from the `-004` GO.

`_metadata_from_envelope` now calls `_metadata_from_attestation` **before** any
legacy resolver. The ordering is the substance: the legacy resolvers infer role
from durable registry state, which is a routing label rather than an identity
oracle, so consulting them first is what produced the WI-6271 misattribution.

Fail-closed behavior: only the typed `no_session_binding` case returns `None`
and falls through (the ordered Slice 1-3 migration path). A session that HAS a
binding but whose role cannot be resolved raises `VerdictFilingError` rather
than degrading.

Two helpers were factored out while there:

- `_declared_model_fields` — model identity is never derived, only taken from
  the artifact's own declaration, because a placeholder would fabricate
  provenance on a governance artifact.
- `_harness_id_for` — the name-to-ID mapping is owner-assigned, so it is read
  from the identity map rather than computed from the name (the prior fallback
  used `name.upper()[:1]`).

## Startup binding wiring

`scripts/session_self_initialization.py`. `_bind_session_role_attestation` is
called beside the existing role-marker writes, so the attested fact and the
marker cache are established in the same place and cannot drift apart at
creation.

**A scope limit found during implementation, stated plainly.** The binding
digests the init command and is immutable. The proposal's site carries a literal
canonical init message only on the dispatch path
(`GTKB_BRIDGE_DISPATCH_KEYWORD`, matched at the `override_role` resolution).
When `override_role` comes from `--role-profile` instead, no literal command
exists.

The implementation therefore **refuses to reconstruct** a command from resolved
role plus work subject, and creates no binding in that case. Reconstruction was
considered and rejected: the canonical grammar admits six strings, so a
reconstruction is byte-identical *only if* the subject token matches what the
owner typed — and the work subject is set independently of the init line, so a
mismatch would permanently bind a subject the owner never stated. An absent
binding is recoverable; a wrong immutable one is not.

**Consequence for coverage, not hidden:** interactive sessions — the exact case
WI-6271 describes — do not receive a binding at this site. Their canonical init
message arrives at the `UserPromptSubmit` init-keyword matcher, which is a
different surface. Slice 2 should bind there. This does not weaken Slice 1: the
consumers already resolve attestation-first and fall through cleanly on
`no_session_binding`, which is the designed migration behavior.

Fail-soft: unexpected binding failures are appended to
`.gtkb-state/session-attestation/bind-failures.jsonl` and swallowed; startup
never breaks on attestation.

## V3 — GOV-20 ADR

`ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` v1 is in MemBase, recording the
decision, the three failed approaches (marker files as authority, env-var
provenance, registry role with a dispatchability tiebreak), the rejected
alternatives, and the fail-closed / ordered-migration consequences.

Per-artifact approval packet at
`.groundtruth/formal-artifact-approvals/2026-08-14-ADR-SESSION-ROLE-ATTESTATION-SERVICE-001.json`,
`full_content_sha256: 2d7316aa90a5670e0c1d82eacf9e632005c3785df7e98906b37e463b9e179671`,
owner approval via AskUserQuestion this session ("Approve as drafted") against
the ADR text presented verbatim in the transcript. Class authorization was not
relied on, as the GO required.

The packet needed `git add -f`: `.groundtruth/` carries a blanket ignore with no
negation for `formal-artifact-approvals/`, so new packets do not enter git by
default although 236 peers are tracked. Filed as **WI-6278**; the last packet to
reach git before this one was 2026-07-18.

## V2 — Consumer-repoint tests

| Module | Tests | Covers |
|---|---|---|
| `platform_tests/scripts/test_verdict_filing_attestation_repoint.py` | 9 | attested role wins; evidence reference persisted; role reflects the init command not the registry; model fields taken from declaration and omitted when absent; `no_session_binding` falls through; **bound-but-unresolvable raises rather than falling through**; entry point prefers attestation; harness ID read from the identity map |
| `platform_tests/scripts/test_session_init_attestation_binding.py` | 10 | literal command binds; role matches the command; **absent command binds nothing**; malformed/near-miss grammar binds nothing; re-entry is a no-op that cannot append a contradicting attestation; missing session id binds nothing; unexpected failure logged and swallowed; absent schema self-created; corrupt DB does not break startup |

The load-bearing assertions in each module are the refusal ones — the ordering
test in the first and the no-reconstruction test in the second. Both would pass
trivially against a naive implementation that fell through or reconstructed, so
they are written to fail in exactly those cases.

## Specification Links

Carried forward from the `-003` proposal GO'd at `-004`, unchanged:

- `ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` v1 — the GOV-20 decision this slice
  implements, recorded under its own approval packet as V3 required.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the deterministic resolution table the
  consumers now follow.
- `GOV-SESSION-ROLE-AUTHORITY-001` — the durable/session-stated authority split;
  durable registry role is a routing label, not an identity oracle.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the provenance contract that attributed
  artifacts must satisfy, including the evidence reference persisted here.
- `GOV-ARTIFACT-APPROVAL-001` — the per-artifact approval packet gating the ADR.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — bridge audit-trail discipline governing
  this thread and its finalization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every claim below rests on a fresh
  read or an executed command, cited by commit SHA or node id.
- `SPEC-1662` (GOV-18) — the added assertions are behavioral, and the
  load-bearing ones are refusal tests rather than happy-path coverage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1;
  `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` — protocol gates governing this document.

## Spec-to-Test Mapping

| Specification | Clause | Test evidence |
|---|---|---|
| `ADR-SESSION-ROLE-ATTESTATION-SERVICE-001` | consumers resolve role only through the log | `test_envelope_entry_point_prefers_the_attestation` |
| `ADR-…-001` | fail-closed, no silent fallthrough | `test_bound_context_with_unresolvable_role_raises_rather_than_falling_through` |
| `ADR-…-001` | binding immutable; second init changes nothing | `test_re_entry_is_a_no_op_not_a_failure` |
| `ADR-…-001` | only the exact canonical form creates a binding | `test_malformed_command_creates_nothing` |
| `DCL-SESSION-ROLE-RESOLUTION-001` | resolution table drives attribution | `test_attested_role_reflects_the_init_command_not_the_registry` |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | evidence reference persisted on the artifact | `test_attestation_metadata_persists_the_evidence_reference` |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | model identity never fabricated | `test_model_fields_come_from_the_artifact_declaration`, `test_model_fields_omitted_when_the_artifact_declares_none` |
| `GOV-SESSION-ROLE-AUTHORITY-001` | durable registry role is not an identity oracle | `test_harness_id_resolves_from_the_identity_map_not_from_the_name` |

## Commands Executed

```
python -m pytest platform_tests/scripts/test_verdict_filing_attestation_repoint.py -q      -> 9 passed
python -m pytest platform_tests/scripts/test_session_init_attestation_binding.py -q        -> 10 passed
python -m pytest <verdict + attestation + attribution module set> -q                       -> 119 passed, 4 failed
python -m pytest <session_self_initialization + session_startup module set> -q             -> 153 passed, 4 failed (219s)
python -m ruff check <changed files>                                                       -> All checks passed
python -m ruff format --check <changed files>                                              -> all formatted
python -c "import scripts.session_self_initialization"                                     -> import OK
```

Both failure sets were confirmed **pre-existing** by the same method: restore the
`HEAD` version of the changed module, re-run only the failing node ids, then
restore the working copy and assert byte-equality.

The 4 startup failures reproduce identically at `HEAD` without the attestation
wiring — `test_startup_model_contains_role_governance_and_kpi_inventory`,
`test_cursor_harness_emit_resolves_default_lifecycle_guard`,
`test_generated_disclosure_includes_review_independence_for_loyal_opposition`,
`test_canonical_helper_matches_index_section`. They are unrelated drift in the
startup disclosure surface, not regressions from this slice.

The 4 verdict/attestation failures likewise reproduce at the `HEAD` version of
`verdict_filing.py`:
(`test_batch_archive_terminal_verdicts.py::test_discover_selects_terminal_non_finalizable_only`,
`test_pre_verdict_executability_check.py::{test_placeholder_gate_new_file_denies,test_placeholder_gate_clean_content_allows}`,
`test_verdict_evidence_anchor_preflight.py::test_hook_deny_reason_for_content_blocks_fabricated_nogo`.)

## Findings Recorded in Passing (tool-use-is-a-test directive)

1. **WI-6277** — the bridge write path accepts a role-less `author_identity`
   that the verdict publish path fails closed on. Cost two full review cycles
   this session. WI-6271's documented workaround (`GTKB_HARNESS_NAME=claude`)
   *causes* it, trading a silent-wrong attribution for a publication-blocking
   one; the two notes need reconciling.
2. **WI-6278** — approval packets have not entered git since 2026-07-18.
3. **WI-6279** — the protected-commit gate's committed-bridge evidence route is
   unavailable to in-flight threads (P3 after correction; the blocked commit
   that prompted it was an expired claim, not a gate defect).
4. **D1 banner misfire, two further instances.** Editing
   `scripts/session_self_initialization.py` under this thread's live GO drew
   "Bridge proposal for this module has NO-GO status … `gtkb-wi5586-scaffold-startup-canonical-routes`",
   an unrelated thread. Seventh and eighth observed instances; already scoped in
   WI-6216 Slice 1, which reached GO at `-006`.

## Acceptance Criteria Check

- Attestation resolver consulted before legacy resolvers in both repointed
  consumers — **met** (V1, tests).
- Evidence reference persisted on attributed artifacts — **met**.
- Fail-closed on bound-but-unresolvable — **met**.
- Binding established at startup — **met for the dispatch path**; interactive
  coverage deferred to Slice 2 with the reason stated above rather than left
  implicit.
- GOV-20 ADR under its own approval packet — **met** (V3).

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-14, "ADR approval"**: owner selected "Approve as
  drafted" against the ADR text presented verbatim. That is the sole owner
  decision this slice required, and it authorized the V3 artifact.
- No further owner decision is requested by this report.

## Prior Deliberations

- `bridge/gtkb-session-role-attestation-service-slice-1-004.md` — the GO whose
  V1/V2/V3 expectations this report answers.
- `bridge/gtkb-session-role-attestation-service-slice-1-002.md` — the GO on the
  original `-001` design.
- `WI-6271` — the misattribution defect motivating the service.
- `WI-6263` / `WI-6264` — the role-flip incidents sharing the root cause.
- `DELIB-20266272` — the PHASE-Y dispatcher go-live whose asymmetry shaped the
  dispatch-path assumptions.

## Recommended Commit Type

`feat` — a new attested-role capability surface with its consumers repointed,
not a repair of existing behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
