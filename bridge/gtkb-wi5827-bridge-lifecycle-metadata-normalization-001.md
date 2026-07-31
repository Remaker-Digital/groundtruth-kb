NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb; CF-10 serialization leadership held per DELIB-20260730-CF10-LEADER-GRANT-B34D5B84
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5827-bridge-lifecycle-metadata-normalization
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5827

target_paths: ["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Normalize enumerated historical bridge-metadata forms in the strict lifecycle resolver

## Problem

A mechanical survey on 2026-07-31 resolved all 17 Prime-Builder-actionable
bridge threads through `bridge_lifecycle_resolver.resolve_bridge_lifecycle`.
**14 of 17 fail before any content is evaluated.** Because bridge files are
append-only and immutable, none can be repaired in place; because
`scripts/implementation_authorization.py` converts
`BridgeLifecycleResolutionError` into `AuthorizationError`, no
implementation-start packet can ever be minted for any of them. The work in
those threads is permanently stranded by metadata form, not by any defect in
the proposals themselves.

The failures are not 14 independent defects. They reduce to two mechanical
causes in the parser:

**Cause A - exact-prefix key match (10 threads).**
`_metadata_values` (`scripts/bridge_lifecycle_resolver.py:202-203`) matches
metadata with a literal prefix:

```python
prefix = f"{field}:"
values = [line[len(prefix):].strip() for line in lines[1:] if line.startswith(prefix)]
```

`_METADATA_FIELDS` declares the canonical key as `"Responds to"`. Every
near-miss key written by any harness parses as `None` and then fails the
`expected_response` equality check at line 334 with `WRONG_RESPONDS_TO_LINK`.
Observed historical variants, each written by a different harness or era:

| Variant key | Observed in |
| --- | --- |
| `Reviewed:` | `gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-002`, `-004`; `gtkb-envelope-protocol-slice-d-worker-hook-injection-016`; `gtkb-authority-foundations-project-authorization-008` |
| `Responds to GO:` | `gtkb-envelope-protocol-slice-d-worker-hook-injection-017` |
| `Responds to NO-GO:` | `gtkb-envelope-protocol-slice-d-worker-hook-injection-019`, `-021`, `-023` |
| `Responds-To:` (hyphenated) | `gtkb-wi5113-verified-finalizer-git-no-window-003`, `-005` |
| `revised_document:` | `gtkb-wi5113-verified-finalizer-git-no-window-002` |

**Cause B - trailing-parenthetical value decoration (2 threads).** The key
parses correctly but the *value* carries an annotation, so the equality
checks at lines 325 and 334 fail:

| Field | Observed value | Thread |
| --- | --- | --- |
| `Version` | `005 (NEW; Stage A verification request)` | `gtkb-file-move-rename-canonicalization-v3-005` |
| `Responds to` | `bridge/gtkb-research-clean-branch-publication-003.md (NO-ACTION)` | `gtkb-research-clean-branch-publication-004` |

## Proposed Change

Two bounded normalizations in `scripts/bridge_lifecycle_resolver.py`, both
built on **closed enumerated allowlists**, plus focused tests.

### N1 - Enumerated key-synonym resolution

Introduce a module-level frozen mapping:

```python
_METADATA_KEY_SYNONYMS: dict[str, tuple[str, ...]] = {
    "Responds to": (
        "Reviewed",
        "Responds-To",
        "Responds to GO",
        "Responds to NO-GO",
        "revised_document",
    ),
}
```

`_metadata_values` consults the canonical key first. Only when the canonical
key yields no value does it try each enumerated synonym in declared order,
returning the first hit. Any key not in the canonical set or this table
continues to yield no value and continues to fail closed exactly as today.

The synonym set is deliberately **closed and enumerated**, not a pattern.
This is the point of reconciliation with `WI-5636`, whose approved scope
states it "retain[s] fail-closed denial for arbitrary alternative metadata."
This proposal does not weaken that stance: an unrecognized key is still a
hard failure. It recognizes exactly five documented historical forms, each
with a cited producing artifact in the table above. Adding a sixth requires
a new governed change to this table, not a parser behavior change.

### N2 - Trailing-parenthetical value normalization

Introduce a bounded normalizer applied to `Version` and `Responds to` values
only:

```python
_TRAILING_ANNOTATION_RE = re.compile(r"\s*\([^()]*\)\s*$")
```

Applied once (not repeatedly) to strip a single trailing parenthetical
annotation before the equality comparison. The raw pre-normalization value is
preserved on `BridgeVersion` for audit. Values with no trailing parenthetical
are returned unchanged. This does not tolerate a *wrong* predecessor path or a
*wrong* version number - only a correct value carrying a trailing annotation.

### Explicitly out of scope - these remain fail-closed

Two of the 14 wedged threads are **not** covered, deliberately:

1. **`gtkb-modernization-rc-evidence-closure`** - version `-002` has no
   `Version:` line at all. This is genuinely absent metadata, not a variant
   form. Synthesizing it from the filename would be the parser inventing
   governance evidence. `MISSING_BRIDGE_METADATA` correctly stands.
2. **`codex-poller-misdiagnosis`** - fails `WRONG_STATUS_AUTHOR_ROLE` because
   `_author_role()` cannot classify the author identity, and separately
   because a `NO-ACTION` was authored by Loyal Opposition when
   `DCL-NO-ACTION-STATUS-SEMANTICS-001` reserves that status to Prime
   Builder. Both are author-provenance and role-authority concerns, not
   metadata-form concerns. Related carrier: `WI-5670` (author-provenance
   tolerance). Not addressed here.

Expected effect: **12 of the 14 wedged threads become resolvable**; 2 remain
correctly fail-closed. This proposal makes no claim about whether the content
of any revived thread is sound - only that its chain becomes machine-readable
so normal review can proceed.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` establishes
the append-only numbered-file chain this change makes readable;
`DCL-NO-ACTION-STATUS-SEMANTICS-001` and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
bound the deliberately-excluded author-role scope; `WI-5636`'s approved
fail-closed stance is preserved by the closed-allowlist design. No new or
revised requirement is needed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only numbered-file chain is canonical bridge authority; this change restores machine-readability of that chain without mutating any historical file.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - governs the deliberately-excluded `codex-poller-misdiagnosis` role case.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - forward-only provenance contract; the author-role failure class is left to its carrier.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the survey evidence is a fresh canonical read, re-run at review time.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation authority derives from the active list-free whole-project PAUTH cited above.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - PAUTH, membership, target classes, and operations are revalidated immediately before mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass independent GO, claim, start packet, report, or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH/Project/Work Item metadata declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing specification is linked to concrete proposed behavior.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps each requirement to executed test evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the change is deterministic, fails closed on unknown input, and is fully testable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the wedged threads are durable artifacts whose lifecycle this change restores.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both target paths are in-root.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| N1 recognizes each enumerated synonym | Focused unit test per synonym key (`Reviewed`, `Responds-To`, `Responds to GO`, `Responds to NO-GO`, `revised_document`) with an otherwise-valid chain | Chain resolves; `responds_to` equals the canonical predecessor path |
| N1 preserves fail-closed for unknown keys (`WI-5636` reconciliation) | Fixture with `Responds toward:` and with `Answers:` | `WRONG_RESPONDS_TO_LINK` still raised |
| N1 canonical key takes precedence | Fixture carrying both `Responds to:` and `Reviewed:` with different values | Canonical value wins; no duplicate-metadata failure |
| N2 strips one trailing annotation on `Version` | Fixture `Version: 005 (NEW; Stage A verification request)` | Resolves as version 005 |
| N2 strips one trailing annotation on `Responds to` | Fixture `Responds to: bridge/<slug>-003.md (NO-ACTION)` | Resolves against `-003.md` |
| N2 does not mask a wrong predecessor | Fixture pointing at `-002.md` when `-003.md` expected, with and without annotation | `WRONG_RESPONDS_TO_LINK` still raised |
| N2 does not mask a wrong version | Fixture `Version: 004 (REVISED)` in file `-005.md` | `WRONG_BRIDGE_VERSION_METADATA` still raised |
| Missing metadata still fails | Fixture with no `Version:` line | `MISSING_BRIDGE_METADATA` still raised |
| Author-role scope untouched | Existing `WRONG_STATUS_AUTHOR_ROLE` tests | Unchanged, still passing |
| No regression in existing resolver behavior | Full existing suite | All existing tests pass |
| Real-world effect | Re-run `resolve_bridge_lifecycle` across the 17 surveyed threads | 12 previously-wedged threads resolve; `gtkb-modernization-rc-evidence-closure` and `codex-poller-misdiagnosis` still fail closed with their current reason codes |

Commands to be executed and reported in the implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/bridge_lifecycle_resolver.py platform_tests/scripts/test_bridge_lifecycle_resolver.py
```

## Acceptance Criteria

1. Each of the five enumerated synonym keys resolves to the canonical
   `Responds to` value.
2. Any key outside the canonical set and the enumerated table still fails
   closed.
3. A single trailing parenthetical annotation on `Version` or `Responds to`
   is normalized; the raw value is preserved for audit.
4. Wrong predecessor paths, wrong version numbers, and absent metadata all
   still fail closed.
5. The author-role failure class is unchanged.
6. The full existing resolver test suite passes.
7. Exactly 12 of the 14 surveyed wedged threads resolve after the change,
   with the 2 named exclusions still failing for their stated reasons.
8. Only the two declared target paths are modified.

## Prior Deliberations

- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` - CF-10 leadership grant scoping this session's bridge-processing authority; the survey that produced this proposal was performed under it.
- `WI-5827` (this work item) - carries the owner-selected remedy; its `status_detail` records the full 14-thread survey evidence.
- `WI-5833` - P0 governance incident for commit `9373c5231`, which introduced the strict parse that retroactively wedged these threads.
- `WI-5636` - narrow `Responds to GO:` tolerance with an explicit fail-closed-for-arbitrary-metadata stance; the closed-allowlist design here is the reconciliation with that stance and should be reviewed against it.
- `WI-5814` - surfacing unparseable bridge chains; complementary detection work, not superseded by this change.
- `WI-5670` - author-provenance tolerance; carrier for the deliberately-excluded author-role class.
- `WI-5648` - established fail-closed behavior on invalid strict chains across claim, dispatch, authorization, and review preflight; this change reduces the population of invalid chains without weakening that behavior.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner AskUserQuestion, 2026-07-31, session `b34d5b84-5746-4eee-bd95-b6eeb3e70715`: presented with the 14-of-17 wedged-thread survey and four remedy options, the owner selected **"Normalize the parser (via WI-5827)"** over per-thread by-reference recovery, a combined approach, or further investigation. That decision selects the remedy direction implemented here.
- Owner AskUserQuestion, same session: selected **"File as a P0 governance incident"** for commit `9373c5231`, captured as `WI-5833`.
- Implementation authority is inherited from the active list-free whole-project PAUTH cited in the header, per the owner's standing rule that work items inherit approval from the parent project.
- No new owner decision is requested by this proposal.

## Risk And Rollback

The principal risk is over-tolerance: a normalization that silently accepts a
genuinely wrong linkage would let a malformed chain pass review. This is
mitigated structurally - the synonym set is closed and enumerated rather than
pattern-based, the value normalizer strips exactly one trailing parenthetical
and nothing else, and four dedicated negative tests assert that wrong
predecessors, wrong versions, absent metadata, and unknown keys all still
fail closed.

Secondary risk is scope creep into author-provenance, explicitly excluded and
tested against.

Rollback is reversion of the two target files through a separately governed
transaction; no historical bridge file, MemBase row, or project state is
touched by this change, so reverting restores exactly the prior behavior.

## Recommended Commit Type

`fix` - repairs a parser defect that strands governed work; adds no new
capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
