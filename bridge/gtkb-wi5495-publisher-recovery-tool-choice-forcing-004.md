NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: f39e4f90-52c0-4b1a-a703-b2fb23fa3f74
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent; independent Loyal Opposition bulk bridge processing round 3; distinct session context from the proposal author (d067ca16-171b-4b2e-89f5-642340e605a6), the version-002 reviewer (9e57c1e3-8af4-4d1a-864c-9c9748238789), and the version-003 NO-ACTION author (019f5f66-9582-7f03-a3f1-3c75e6bd9d0a)

# LO Review NO-GO (review_no_action correction) - gtkb-wi5495-publisher-recovery-tool-choice-forcing

bridge_kind: lo_verdict
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 004
Reviewed: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-001.md
Responds to: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-003.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

## Verdict

NO-GO. This is the corrected verdict issued under the `review_no_action`
disposition of the version-003 Prime Builder `NO-ACTION`, superseding the
version-002 `GO`.

## Processing The NO-ACTION (Not Trusted On Its Face)

Per `DCL-NO-ACTION-STATUS-SEMANTICS-001`, version 003 is a well-formed
`NO-ACTION`: authored by Prime Builder, sits atop a prior Loyal Opposition `GO`
(version 002) in this same thread, states concretely what the reviewing role
must fix, and routes back to Loyal Opposition via `review_no_action`. Its form
is correct, but form alone does not earn compliance -- its substantive claim
was independently re-derived from primary evidence below rather than accepted
on trust. The corrective direction turned out to be technically sound, and the
required-revision language it requests is *more* concrete and evidence-bearing
than the verdict it replaces, not vaguer -- the opposite of the governance-gaming
pattern this review was briefed to watch for.

## Independent Technical Verification

- `scripts/ollama_harness.py:532` (`call_ollama_chat`) builds the request URL as
  `endpoint.rstrip("/") + "/api/chat"` -- Ollama's native chat endpoint, not the
  OpenAI-compatible `/v1/chat/completions` surface. Read directly from current
  HEAD, not from the proposal's prose.
- The current (post-revert) payload construction at
  `scripts/ollama_harness.py:1277` is
  `payload = {"model": model_route.model_id, "messages": messages, "tools": schemas, "stream": False}`
  -- no `tool_choice` key under any branch or condition. This independently
  confirms the NO-ACTION's claim that the ineffective D source/test hunks were
  fully removed under the (now-released) implementation claim.
- `git status --short -- scripts/ollama_harness.py scripts/cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_cloud_harness_base.py`
  shows only `scripts/cloud_harness_base.py` and
  `platform_tests/scripts/test_cloud_harness_base.py` as Modified; the two
  `ollama_harness.py`-side target paths do not appear, i.e. they are clean
  relative to HEAD. This matches the NO-ACTION's claim "Both D target paths are
  clean relative to HEAD" exactly.
- `git diff -- scripts/cloud_harness_base.py` shows a correctly-scoped
  `elif profile.dialect == DIALECT_OPENAI_CHAT:` branch added to the existing
  publisher-only-recovery block in `run_tool_loop` (around line 2389), setting
  `payload["tool_choice"] = {"type": "function", "function": {"name": PUBLISH_BRIDGE_VERDICT_TOOL}}`
  -- exactly mirroring the shipped `DIALECT_ANTHROPIC_MESSAGES` pattern in the
  same `if` block, and matching the version-001 proposal's stated scope for the
  F/OpenRouter half only.
- `git diff -- platform_tests/scripts/test_cloud_harness_base.py` shows the
  matching negative-control test assertions the version-002 GO's Conditions
  section required: `tool_choice` absent on the pre-recovery and
  post-publish turns, and present with the exact forced-function shape on the
  recovery turn.
- A repository-wide search for the literal string `tool_choice` (via the Grep
  tool) returns zero matches in `scripts/ollama_harness.py` or
  `platform_tests/scripts/test_ollama_harness.py`. The only live (unstaged)
  matches are the `cloud_harness_base.py` / `test_cloud_harness_base.py` pair;
  all other matches are historical bridge files (this thread's own -001/-002/-003)
  or the unrelated, separately-verified Alibaba (`H`) harness threads
  (`gtkb-wi5245`/`-5258`/`-5267`/`-5302`). This is consistent with the
  NO-ACTION's "quarantined candidate evidence" characterization: the F fix is
  real, isolated, and untouched by anything else currently unstaged.

Given the above, the version-001 proposal's central claim -- that adding "the
standard OpenAI Chat Completions forced-function tool_choice directive ... to
both harnesses during recovery, mirroring the existing Anthropic-only pattern"
would fix both D and F -- is factually incorrect for `ollama_harness.py`. That
file's only network call for chat turns targets Ollama's native `/api/chat`
route via a payload dict this review confirmed has no `tool_choice`-consuming
code path anywhere in the module. Ollama's native chat endpoint is a narrower,
distinct request contract from the OpenAI Chat Completions API the proposal's
fix mechanism targets; a `tool_choice` field written into that payload would be
inert against the live provider and would not mechanically force
`PublishBridgeVerdict`, leaving the D/Ollama half of WI-5495's defect
unresolved even after a "passing" mocked-payload unit test. The harness's own
`ModelRoute.tool_calling_supported: bool` (a coarse yes/no capability flag,
not a forcing control) is consistent with this: Ollama's native tool-calling
surface does not expose fine-grained tool-choice forcing semantics the way the
OpenAI Chat Completions dialect does.

The version-002 GO adopted the proposal's "mirror the pattern in both files"
premise without independently confirming the D-side endpoint contract, and its
own Conditions section's D-side testing instruction ("assert the exact
tool_choice payload shape ... is present only during publisher-only recovery")
describes a test that can pass by asserting a Python dict key while proving
nothing about provider-side enforcement. That is exactly the verification gap
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (state claims must derive from fresh
canonical reads, not proposal prose) and
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (spec-derived verification
must actually establish compliance, not merely execute) require a reviewer to
catch before approving.

## Rationale For NO-GO

The version-001 proposal, as written, cannot satisfy its own Acceptance
Criteria for the D/Ollama half:

- "A unit test asserts the equivalent tool_choice field is present in
  ollama_harness.py's payload construction under the same recovery condition"
  is satisfiable by a shallow mock that only inspects the constructed Python
  dict, and would give false confidence that D's livelock is fixed.
- "A live direct-invocation smoke test ... completes without raising the
  publisher-recovery-exhausted error" does not establish that
  `PublishBridgeVerdict` is actually being *forced*; a non-compliant model
  could still avoid crashing the harness by chance while never being
  mechanically constrained, which is the actual defect WI-5495 exists to fix.

The F/OpenRouter half of the same proposal is independently confirmed correct,
complete, and test-covered (see Independent Technical Verification above), but
the proposal is not separable after the fact -- it was filed, reviewed, and
GO'd as one four-file, two-harness unit, and version 001 as written is not an
accurate description of what can currently be safely implemented. `NO-GO`
against version 001 is therefore the correct disposition; the live F diff
remains quarantined pending a fresh, correctly-scoped proposal.

## Specification-Derived Verification

| Requirement | Verification | Observed Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability preflight against operative file `-003` | PASS; `preflight_passed=true`; `missing_required_specs` empty. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | PASS; matched via `doc:*`, `Specification Links` content. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause preflight + direct source re-verification | Clause preflight PASS (zero blocking gaps); substantively this is the exact clause the version-002 GO's D-side test plan fails on independent re-check (mocked payload-shape assertion does not establish provider-side enforcement for a field the live endpoint does not consume). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Direct read of `scripts/ollama_harness.py` (current HEAD) vs. proposal's prose claim | FAIL for the version-001/002 D-side claim: the endpoint/payload claim was not grounded in a fresh canonical read of the actual request contract. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Target inventory | `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py` -- all resolve inside `E:\GT-KB`. |
| `GOV-RELIABILITY-FAST-LANE-001` | `KnowledgeDB.get_work_item("WI-5495")` re-check | origin=`defect`, no new public API/CLI/behavior beyond defect removal, `Requirement Sufficiency` correctly states no new spec needed, current scope (2-4 files, few lines each) is small/single-concern -- eligibility itself still holds; the defect is in mechanism correctness, not fast-lane eligibility. |
| `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` | `KnowledgeDB.get_project_authorization(...)` re-check | `status=active`, `expires_at=None`, covers `PROJECT-GTKB-RELIABILITY-FIXES`, `allowed_mutation_classes` includes `source`/`test_addition`; no forbidden operation implicated by this disposition. |

## Applicability Preflight

- packet_hash: `sha256:3cccaf4fd5b083186f1d902b7bab23b5822d65e5970900d7b3e5ffc9ce28f20b`
- operative_file (at time of this review): `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-003.md`
- preflight_passed: true
- missing_required_specs: (empty list)
- missing_advisory_specs: (empty list)
- blocking_errors: (empty list)

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code observed: 0 (pass)

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail and numbered-file discipline for this correction.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - governs the well-formedness of version 003 and the `review_no_action` disposition this verdict performs.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - carried forward from the proposal under review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the substantive basis for this NO-GO (mocked payload-shape tests do not establish the D-side spec-derived verification the proposal claims).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the substantive basis for this NO-GO (D-side endpoint claim was not grounded in a fresh canonical read).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - target-path and project-linkage evidence carried forward.
- `GOV-RELIABILITY-FAST-LANE-001` - re-checked; eligibility criteria still hold for a corrected proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain in-root; carried forward.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing specification, carried forward from prior versions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing specification, carried forward from prior versions.

## Required Revision

A `REVISED` proposal must, at minimum:

1. Preserve the F/OpenRouter `DIALECT_OPENAI_CHAT` forced-function fix in
   `scripts/cloud_harness_base.py` and its test coverage in
   `platform_tests/scripts/test_cloud_harness_base.py` -- both independently
   re-verified correct in this review and ready to file as-is.
2. Either (a) replace the D/Ollama fix mechanism with something the native
   `/api/chat` contract actually supports (which may mean documenting that no
   mechanical forcing is currently available on that endpoint and choosing a
   different mitigation, e.g. stricter prompt-level constraint plus tighter
   recovery-turn budgeting, with that limitation stated explicitly rather than
   implied), or (b) if switching D to an OpenAI-compatible Ollama endpoint is
   pursued, explicitly scope the endpoint-selection and response-envelope
   normalization change and test it against the actual selected endpoint, not
   a mock of the native one.
3. Add or revise tests that assert the real request target (endpoint path/
   dialect) and payload contract actually sent for D, not just the presence of
   a dict key, so a future reviewer cannot repeat this same verification gap.
4. Consider splitting F (ready now) from D (pending the above design choice)
   into separate proposals so the confirmed-correct F fix is not blocked
   behind an open D design question; this is Prime Builder's scoping choice to
   make, not a requirement of this verdict.
5. File the revision through a fresh `bridge_claim_cli.py claim`,
   `REVISED` status, and (after a fresh independent `GO`) a fresh
   implementation-start authorization packet before any further mutation of
   either target pair.

## Owner Decisions / Input

Not required for this verdict file (verdict files are excluded from the
Mandatory Owner Decisions / Input Section Gate). No new owner decision is
needed for this technical correction; WI-5495 remains within the standing
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` authorization once refiled
correctly.

## Prior Deliberations

- `DELIB-202666257`, `DELIB-202666266`, `DELIB-202666227`, `DELIB-202666174`,
  `DELIB-202666256` - independently re-confirmed present in the Deliberation
  Archive with `go` outcomes; carried forward from versions 001-003.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

