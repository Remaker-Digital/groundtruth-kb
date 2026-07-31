NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; owner-declared role via ::init gtkb pb, persisting per DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001. NOTE: this session's runtime marker currently reads loyal-opposition with role_resolution_source=session_resolver_fallback -- a live instance of the WI-5723 defect (GO at gtkb-wi5723-session-resolver-fallback-removal-002). Marker files carry no role authority; the owner-declared transcript role governs.
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5841-harness-selector-registry-derived
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5841

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this proposal creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# Derive the worker-document selector from the harness registry instead of a hardcoded two-harness if-chain

## Problem — five registered harnesses cannot resolve claim provenance

`scripts/bridge_work_intent_registry.py` `_worker_harness_selector()` (line 734)
narrows the canonical worker-envelope lookup. Its resolution order is:

```python
configured = os.environ.get("GTKB_HARNESS_NAME", "").strip()
if configured:
    return configured                      # explicit override
if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"):
    return None                            # headless dispatch
if os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDECODE"):
    return "claude"
if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_HOME"):
    return "codex"
return None                                # everything else
```

`harness-state/harness-identities.json` registers eight harnesses. **Two are
detected.** `goose`, `cursor`, `antigravity`, `ollama`, and
`alibaba-cloud-studio` all fall through to `return None`.

**Consequence.** With no selector, `resolve_worker_role_provenance` falls back
to a glob across `harness-state/*/session-envelopes/<session-id>.json`. When
that does not match exactly one document it raises *"Worker role provenance is
missing for the current session"* or *"is ambiguous across session envelopes"*,
so the harness cannot mint a `go_implementation` claim and cannot obtain an
implementation-start packet. It can file nothing and implement nothing.

**Reproduced on Goose desktop, 2026-07-31**, by the owner, who confirmed the
harness works with `GTKB_HARNESS_NAME=goose` set — the designed override at
line 742. That override is correct but is per-invocation environment: it must
be set wherever the harness launches, and a harness that forgets it silently
loses claim eligibility rather than failing loudly.

**Operational urgency.** Goose (harness `G`) is being stood up now to take
Prime Builder implementation work on GO'd bridge items. The same failure is
latent for four other registered harnesses.

## Proposed Change

### S1 — derive the selector from the registry

Replace the hardcoded `claude`/`codex` if-chain with a lookup driven by
`harness-state/harness-identities.json`. Each registered harness contributes
its detection signal; adding a harness to the registry becomes sufficient to
make it detectable, with no code change.

Detection signals are read from the registry record rather than compiled in.
Where a registered harness has no declared signal, it simply does not
self-detect and the explicit override remains available — the same posture as
today, but per-harness and visible in the registry instead of implicit in a
missing `elif`.

### S2 — preserve the three existing behaviors exactly

The resolution order is unchanged and remains precedence-ordered:

1. `GTKB_HARNESS_NAME` explicit override wins (unchanged, line 742).
2. Headless dispatch (`GTKB_BRIDGE_POLLER_RUN_ID`) returns `None` so a
   dispatched worker never inherits the parent selector (unchanged, line 745).
3. Registry-derived detection replaces the if-chain.
4. No match still returns `None` — the ambiguity check downstream is
   unchanged and remains the fail-closed path.

`claude` and `codex` must continue to resolve from exactly the environment
variables they resolve from today; their behavior is a regression surface, not
a redesign target.

### S3 — regression test over the full registry

A test asserting that **every** harness registered in
`harness-state/harness-identities.json` either resolves a selector from its
declared signals or is explicitly recorded as override-only. This is the check
that makes the class of defect non-recurring: registering a ninth harness
without a detection story fails the suite rather than silently producing a
harness that cannot claim work.

### Explicitly out of scope

- **Removing the `GTKB_HARNESS_NAME` override.** It is the designed escape
  hatch and remains first in precedence.
- **Changing `resolve_worker_role_provenance` or its ambiguity semantics.**
  This proposal supplies a selector; it does not alter what the resolver does
  with one.
- **The session-envelope role-flip defect** — that is WI-5723 (GO'd at
  `gtkb-wi5723-session-resolver-fallback-removal-002`). Adjacent surface,
  different mechanism: that one overwrites a correct role, this one fails to
  select a document at all.
- **Per-session envelope isolation for non-Claude harnesses** — that is
  `WI-5815`, which does not declare `scripts/bridge_work_intent_registry.py`
  in its `target_paths` and does not address `_worker_harness_selector`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-HARNESS-ROLE-PORTABILITY-001`
establishes that roles are portable across registered harnesses, and
`GOV-HARNESS-ONBOARDING-CONTRACT-001` sets the capability floor a new harness
must meet. A registered harness that cannot mint a claim does not meet that
floor. No new or revised requirement is needed.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Every registered harness resolves or is override-only | Parametrized test over all entries in `harness-identities.json` | no harness silently returns `None` without a recorded reason |
| Goose resolves without the env var | Fixture with Goose's declared signal set, `GTKB_HARNESS_NAME` unset | selector returns `goose` |
| Explicit override still wins | `GTKB_HARNESS_NAME=x` plus a conflicting detection signal | returns `x` |
| Headless dispatch still returns None | `GTKB_BRIDGE_POLLER_RUN_ID` set plus a detection signal | returns `None` |
| Claude detection unchanged | `CLAUDE_CODE_SESSION_ID` set; and `CLAUDECODE` set | returns `claude` in both cases |
| Codex detection unchanged | `CODEX_THREAD_ID` set; and `CODEX_HOME` set | returns `codex` in both cases |
| Unknown environment still returns None | no signals set | returns `None`; downstream ambiguity check unchanged |
| Registry unreadable fails safe | registry missing or malformed | returns `None` and surfaces the error; never guesses a harness |
| Precedence order preserved | override + dispatch + detection all present | override wins, then dispatch, then detection |
| No regression | full work-intent registry suite | all pass |

Commands to be executed and reported in the implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_gtkb_session_id.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
```

## Acceptance Criteria

1. Every harness in `harness-identities.json` resolves a selector or is explicitly override-only.
2. Goose resolves without `GTKB_HARNESS_NAME`.
3. `GTKB_HARNESS_NAME` remains first in precedence.
4. Headless dispatch still returns `None`.
5. `claude` and `codex` detection is byte-for-byte behaviorally unchanged.
6. Registry unavailability fails safe and never guesses.
7. A newly registered harness without a detection story fails the suite.
8. The existing work-intent registry suite passes.
9. Only the two declared target paths are modified.

## Bridge Chain Discipline

Filed as `bridge/gtkb-wi5841-harness-selector-registry-derived-001.md`, the
first numbered file of a fresh append-only chain. No prior versioned bridge
file is deleted, rewritten, or renumbered.

## Coordination Note — shared target with WI-5784

`scripts/bridge_work_intent_registry.py` and its test are also the declared
targets of `gtkb-wi5784-work-intent-claim-lock-retry` (currently NO-GO at
`-006`, pending a fresh implementation-start packet), and of
`gtkb-wi5829-claim-lifecycle-report-filing` (NEW). This overlap is recorded in
`WI-5836`. The changes are disjoint in function — WI-5784 hardens SQLite
acquire/release retry, WI-5829 addresses claim lifecycle at report filing, and
this proposal touches only `_worker_harness_selector` — but they collide in
file, so implementation must be sequenced rather than run concurrently. This
proposal claims no priority; sequencing is the owner's or the reviewer's call.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `WI-5841` — the carrier, filed this session after the owner reproduced the defect on Goose desktop and confirmed the `GTKB_HARNESS_NAME` workaround.
- `WI-5723` — session-envelope role-flip removal, GO'd; adjacent surface, different mechanism (overwrites a correct role rather than failing to select a document).
- `WI-5815` — per-session envelope isolation for non-Claude harnesses; does not declare this file and does not mention `_worker_harness_selector`.
- `WI-5784` / `WI-5829` — the other two live threads targeting this same file; see the Coordination Note.
- `WI-5836` — the cross-thread target-collision record covering that overlap.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which this session files.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner report, 2026-07-31: identified `_worker_harness_selector()` as the root cause, confirmed the harness works with `GTKB_HARNESS_NAME=goose` set, and asked whether existing work covered it. It did not; `WI-5841` was created.
- Owner directive, 2026-07-31: *"Goose will pick up the PB work items for 'GO' and 'NO-GO' items"* — which makes Goose's claim eligibility operationally blocking.
- Owner directive, 2026-07-31: *"Continue driving implementation proposals."*
- Implementation authority is inherited from the active list-free whole-project PAUTH cited in the header. No new owner decision is requested by this proposal.

## Risk And Rollback

Principal risk is a behavior change to `claude` or `codex` detection, which
would break claim minting for the two harnesses that currently work. Mitigated
by treating their detection as a regression surface with explicit per-variable
tests (`CLAUDE_CODE_SESSION_ID`, `CLAUDECODE`, `CODEX_THREAD_ID`,
`CODEX_HOME`), and by preserving the precedence order exactly.

Secondary risk is the registry becoming a new failure dependency: if the
identity file is unreadable, selector resolution now has a dependency it did
not have before. Mitigated by failing safe to `None` — precisely today's
behavior for an unrecognized harness — and surfacing the error rather than
guessing.

Rollback is reversion of the two target files through a separately governed
transaction. No historical bridge file, MemBase row, registry file, or session
document is mutated by this change.

## Recommended Commit Type

`fix` — repairs claim-provenance resolution for five registered harnesses; adds no new capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
