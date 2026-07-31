ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 077da0d1-f51e-43b0-ace9-13eb98da71ab
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# LO Advisory - Unresolved Harness Identity Fails Open To Prime Builder Without Ever Reading The Role Registry, And The Test Named For That Property Asserts Nothing

bridge_kind: governance_advisory
Document: gtkb-lo-role-resolution-fallback-privilege-escalation-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5679

---

## Source

Read-only observation during a scheduled Loyal Opposition queue run, branch
`research`, 2026-07-28 UTC. Surfaced while establishing this session's own role
for review-independence purposes on bridge thread
`gtkb-wi5657-terminal-finalization-recovery-v2`.

Trigger: `.claude/session/envelope.json` reported `role: prime-builder` with
`role_resolution.durable_registry_role: loyal-opposition` and
`worker_role_provenance.role_resolution_source: session_resolver_fallback`, for a
session in which no `::init gtkb pb` was ever typed.

## Classification Slot

`adopt` - the defect is mechanically reproducible, it fails open toward the
higher-privilege role, and the detection fix is self-contained.

## Claim

`scripts/harness_roles.py::role_for_harness` returns `prime-builder` whenever the
harness identity cannot be resolved, **returning before the role registry is read
at all**. Because the caller in `scripts/session_self_initialization.py` resolves
the harness name two different ways within a single run, a startup invocation
that omits `--harness-name` writes a worker session document asserting
`role: prime-builder` for a harness whose durable registry role is
`loyal-opposition`.

The regression test named for this exact property exercises the defective branch
and asserts only that the result is a member of the set of valid roles, so it
passes while the defect is live.

## Evidence

### E1 - The fail-open, at `scripts/harness_roles.py:999-1015`

```python
 999    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
1000    path = role_assignments_path(project_root, assignment_path)
1001    document = load_role_assignments(project_root, assignment_path)
1002    if resolved_id is None:
1003        return ROLE_PRIME_BUILDER, document, path
1004
1005    record = _ensure_record(document, resolved_id, harness_name=harness_name)
...
1015    role_set = _normalize_role_field(record.get("role"))
```

Line 1001 loads the registry document; line 1003 returns without consulting it.
The per-harness role is not read until line 1015, which is unreachable on this
path. The returned role is a constant, not a lookup.

### E2 - Reproduced against live state (read-only)

```
harness_name='claude'  -> loyal-opposition     # correct; registry consulted
harness_name=None      -> prime-builder        # registry never consulted
harness_name='codex'   -> prime-builder        # correct for harness A
```

The `None` case returns the higher-privilege role from a constant. The live
registry (`harness-state/harness-registry.json`, unchanged since 2026-07-21)
records B as `loyal-opposition`; MemBase `harnesses` shows B's newest row at
version 110 with `["loyal-opposition"]`.

### E3 - The caller resolves harness name two different ways in one run

`scripts/session_self_initialization.py`, same `main()`:

- Role resolution (7631-7636) passes only `args.harness_name`, so an invocation
  without the flag yields `None` and takes the E1 branch.
- Envelope writing (7653-7657) falls back further:

```python
7653    runtime_harness_name = (
7654        args.harness_name
7655        or os.environ.get("GTKB_HARNESS_NAME")
7656        or ("claude" if (os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_SESSION_ID")) else "codex")
7657    )
```

The result is a document that simultaneously records harness `B` / `claude` and
role `prime-builder`. The observed `role_resolution` block reproduces exactly
from `_role_resolution(root, 'B', role='prime-builder',
role_source='session_resolver_fallback')`
(`groundtruth-kb/src/groundtruth_kb/session/envelope.py:228-266`).

The registered SessionStart hook is **not** the vector: `.claude/settings.json`
passes `--harness-name claude`, and `session_start_dispatch_core.py:946-957` adds
`--harness-id`. The reachable vector is any non-hook invocation - manual,
scripted, or wrapper - that omits the flag.

### E4 - The guarding test is false-green

`platform_tests/scripts/test_session_self_initialization.py:807-812`:

```python
def test_startup_model_discovers_durable_operating_role() -> None:
    module = _load_module()
    discovered_role = module.discover_role_profile(REPO_ROOT)

    assert discovered_role in module.ROLE_PROFILES
```

Two independent failures of coverage. It calls `discover_role_profile` with **no
harness name**, so it exercises precisely the defective branch; and it asserts
only set membership, never equality with the registry value. A constant return of
`prime-builder` satisfies it. The test's name promises the property it does not
check.

### E5 - No other surface covers it

`platform_tests/scripts/test_session_envelope_runtime.py:118,133` and
`test_modernization_harness_parity.py:164` assert that
`role_resolution["durable_registry_role"]` is *recorded* correctly - never that
`role` agrees with it under a fallback source. The doctor's
`_check_role_set_topology_consistency` validates registry wire form and topology,
not envelope-versus-registry agreement.

### E6 - Ruled out as causes

- Registry corruption: `harness-state/harness-registry.json` mtime 2026-07-21,
  `current_prime_ids = ['A','G']`, B = `loyal-opposition`.
- `ensure_prime_on_startup` self-correction (`harness_roles.py:1007-1013`): did
  not fire; a Prime holder exists.

## Deficiency Rationale

**The direction of the failure is the problem.** GT-KB's role model is a
privilege boundary: Prime Builder may mutate source, tests, configuration, and
MemBase; Loyal Opposition may not, and is additionally constrained by the
file-safety allow-list. A fallback that resolves *toward* Prime Builder when
identity is unknown grants the higher privilege on the strength of missing
information. Every other failure mode in this subsystem fails closed;
`primary_role()` itself returns `loyal-opposition` for an empty role set, so the
constant at line 1003 is inconsistent with the module's own convention.

**The concrete harm is bounded today, but only by accident.** Three surfaces that
could have consumed the wrong role do not:

- `author_identity` comes from the durable registry
  (`scripts/bridge_author_metadata.py:442-499`), not the envelope, so bridge
  artifacts are attributed correctly.
- `.claude/hooks/lo-file-safety-gate.py:294-311` resolves role via
  `resolve_interactive_session_role` plus the registry, so LO write-gating still
  fires.
- The verify-skill verdict path has no role gate at all.

That is three independent surfaces each reading role from a *different* source
and happening to agree. The provider publication path does **not** agree:
`scripts/gtkb_bridge_writer.py:478-481` (`_resolve_lo_worker`, called from
`publish_lo_verdict`) hard-refuses unless the worker session document says
`loyal-opposition`. A session carrying the bad envelope role would fail closed
there - correct behavior, but it means the same session is simultaneously
treated as Prime by one surface and refused as non-LO by another.

**Why this matters beyond the immediate bug.** Review independence, the
file-safety boundary, and implementation authorization are all keyed on role. A
role that can be set to Prime Builder by *omitting an argument* is not a boundary;
it is a default. The defect is currently masked by consumers that route around
the envelope, which means it can persist indefinitely without visible symptoms
and will surface the first time a consumer trusts the envelope.

## Recommended Prime Action

Ordered by risk; all additive.

1. **Fix the fallback direction (smallest, highest value).** Change
   `harness_roles.py:1002-1003` to fail closed. Two viable forms: raise on
   unresolved identity, or return `ROLE_LOYAL_OPPOSITION` to match
   `primary_role()`'s empty-set convention. Raising is preferable because a
   silent LO default would merely invert the guess; the caller genuinely does
   not know who it is and should say so.
2. **Repair the test.** Replace the vacuous membership assertion with equality
   against the registry value for a named harness, and add a case asserting the
   unresolved-identity path fails closed rather than returning Prime.
3. **Unify harness-name resolution in the caller.** Have
   `session_self_initialization.main()` compute `runtime_harness_name` once
   (7653-7657) and pass it to role resolution (7631-7636), so role and identity
   cannot disagree within a run.
4. **Add a doctor check** asserting that every open worker session document whose
   `role_resolution_source` is `session_resolver_fallback` has `role` equal to
   `durable_registry_role`. This detects existing drifted documents, which
   fixing the code path will not retroactively repair.

## Related And Non-Duplicated Work

- `bridge/gtkb-wi5679-session-role-keying-continuity-*` - session-id keying
  continuity. Overlapping subsystem; this advisory is about the *fallback role
  value*, not key continuity.
- `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-00{1,2}.md` - the
  hook-versus-envelope divergence noted above. This advisory adds the upstream
  cause and the false-green test, which those do not cover.
- `platform_tests/hooks/test_session_start_dispatch_role_cache.py:101` documents
  the deliberate decision that the startup writer no longer consults registry
  role. That split is by design; the silent `prime-builder` constant is not, and
  the two should not be conflated when scoping the fix.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. Recommendations 1-3 mutate `scripts/harness_roles.py`,
`scripts/session_self_initialization.py`, and
`platform_tests/scripts/test_session_self_initialization.py`. Recommendation 4
mutates `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

### Grill-the-owner questions

Prime Builder must obtain durable AskUserQuestion-recorded answers to:

1. **Fail-closed form.** Should unresolved harness identity raise, or return
   `loyal-opposition`? Raising surfaces the condition; returning LO keeps startup
   working but silently guesses. This is a governance-posture choice.
2. **Blast radius.** Are there known callers that rely on the current
   `prime-builder` default to bootstrap a fresh install where no identity exists
   yet? If so, the fix needs an explicit bootstrap path rather than a blanket
   change.
3. **Scope.** Is recommendation 3 (unifying harness-name resolution) in the first
   slice, or does it stay separate because it touches the startup path used by
   every session?
4. **Drifted documents.** Should existing worker session documents with the wrong
   role be repaired, and if so by what mechanism? There is currently **no
   supported CLI** to correct an open envelope's role - the only channel is an
   owner-typed `::init gtkb lo`. `gt session envelope open` is not a substitute:
   it mints a new session id and writes no `worker_role_provenance` block, which
   is strictly worse than the drifted state.

### Required durable owner decisions

- The fail-closed form (raise vs. LO default).
- Whether a bootstrap exemption is needed.
- First-slice scope.
- Whether an envelope role-repair CLI is authorized, given none exists.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `SPEC-1662`

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - role, status, and
  dispatchability as orthogonal axes; the model this fallback violates by
  conflating "identity unknown" with "role = Prime".
- `DELIB-20263438` - role/status orthogonality; same basis.
- `DELIB-20260673` - parallel-session fragmentation, where independent sessions
  consulted different aliases of the same source of truth and produced divergent
  state claims. The three-different-role-sources condition documented above is
  the same failure shape applied to role rather than to state.

## Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | Make unresolved harness identity fail closed, and make the guarding test meaningful. |
| Preconditions | Owner-grilling gate answers recorded via AskUserQuestion. No existing authorization covers this work. |
| Evidence paths | `scripts/harness_roles.py:999-1015`; `scripts/session_self_initialization.py:7631-7673`; `platform_tests/scripts/test_session_self_initialization.py:807-812`; `groundtruth-kb/src/groundtruth_kb/session/envelope.py:228-266`. |
| File touchpoints | `scripts/harness_roles.py`, `scripts/session_self_initialization.py`, `platform_tests/scripts/test_session_self_initialization.py`, and for recommendation 4 `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. |
| Verification steps | Assert `role_for_harness(root, harness_name=None)` no longer returns Prime; assert equality with the registry for a named harness; run the full session-initialization and envelope-runtime suites, since the changed default is load-bearing at startup. |
| Rollback notes | Single-function revert; no data migration. Drifted envelope documents are unaffected either way and need the separate repair decided at grilling question 4. |
| Open decisions | All four grilling questions above. |

## Owner Decision Needed

None from this advisory. It records a condition and proposes future work.

## Commands Executed

```powershell
gt harness roles
python -c "harness_roles.role_for_harness(root, harness_name=<'claude'|None|'codex'>)"   # read-only
```

Read-only source inspection: `scripts/harness_roles.py:993-1016`;
`platform_tests/scripts/test_session_self_initialization.py:805-813`. Read-only
reads of `harness-state/harness-registry.json`,
`harness-state/claude/session-envelopes/*.json`, and MemBase `harnesses`.

No repository file was modified by this observation other than the creation of
this advisory artifact through the governed bridge writer.

## Skills applied

- gtkb-bridge
- gtkb-advisory-proposal
- gtkb-lo-opportunity-radar

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
