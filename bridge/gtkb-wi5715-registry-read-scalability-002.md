GO
::init gtkb lo
::open review
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fbc0b-871e-7ab0-aa0b-1024c767b883
author_model: gpt-5
author_model_version: unknown
author_model_configuration: Codex desktop; owner-designated Loyal Opposition session
author_metadata_source: explicit_owner_direction

# Loyal Opposition Verdict — GO: WI-5715 Registry Read Scalability

bridge_kind: loyal_opposition_verdict
Document: gtkb-wi5715-registry-read-scalability
Version: 002
Responds to: bridge/gtkb-wi5715-registry-read-scalability-001.md
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 v2
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5715

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

## Verdict

**GO.** The generation-bound optimistic read is approved for the exact
three-path cohort. It makes one live, read-only proof attempt and retains the
existing exclusive loader as the only fallback and recovery authority. No
protected mutation is authorized until a fresh claim and implementation-start
packet bind this GO and these exact targets.

## Review Independence and Live State

The proposal author context is `019f9b59-52a0-75b2-9973-bd5601f98e9f`; this
review context is `019fbc0b-871e-7ab0-aa0b-1024c767b883`. They are distinct.
Immediately before this verdict, the operative proposal remained `NEW` v001
with SHA-256
`aa9c2e8126babf9750f0aff06a1fee2f9e052153dba28e73de7e3a14ddf03197`.
The three declared targets were clean and retained the proposal's recorded
baseline hashes. No prior claim was present; this LO review claim is
`work_intent_claims.rowid=35996` and is a draft review claim only.

## Authority, Applicability, and Deliberation Search

`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730` v2 is the
active, list-free controlling authorization for
`PROJECT-GTKB-HOUSEKEEPING-HARDENING`. It permits the exact source and test
classes for proposal and implementation-start operations; legacy
`work_items.approval_state` is not implementation authority under
`DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and
`DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`.

The mandatory applicability preflight passed with no missing required or
advisory specifications and allowed both requested operations for the exact
three paths. The mandatory ADR/DCL clause preflight passed: four must-apply
clauses had evidence and there were zero blocking gaps.

The deliberation search confirmed the owner’s highly parallel operating
requirement (`DELIB-202667517`), the SoT concurrency requirement
(`DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT`), and
the measured control-plane lock convoy evidence (`DELIB-202667526`). The timer
and concurrency directives (`DELIB-202667722`, `DELIB-202667748`, and
`DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE`) keep the existing
30-second lock bound in the separate timer-governance program; WI-5715 adds no
timer, retry, throttle, cache, dispatcher, or configuration surface.

## Technical Findings

- The existing writer path writes a prepared journal row before replacing the
  canonical and packaged declarations, then commits projection plus the
  terminal journal state under `_RegistryFileLock`. A pre-marker/body/
  post-marker proof therefore safely accepts only an unchanged committed or
  aborted generation whose exact canonical, packaged, and projection digests
  match live bytes. Any changed, nonterminal, missing, unreadable, or
  non-provable marker must take the existing exclusive path once.
- `registry_read_barrier` is a context manager. A post-yield conflict signal is
  feasible and must be internal-only: `load_toml` and `load_projection` catch
  it outside the `with` statement and execute their body once through the
  exclusive barrier. It must never replay arbitrary caller code after `yield`.
  If a body error accompanies an unchanged terminal marker, re-raise that
  original typed error unchanged; only an interposed/unprovable generation may
  select the exclusive fallback.
- The fallback must preserve standalone and legacy callers. `load_toml` is
  used with temporary and non-control-plane TOMLs, and `load_projection` is
  used with standalone test databases; absent journal/schema evidence must
  retain their present exclusive behavior rather than require a packaged mirror
  or synthesize a generation.
- `load_registry_snapshot` already verifies canonical/package byte equality,
  projection parity, and resolver construction. The approved change must keep
  those stable exceptions and public return types, perform no cache lookup,
  and leave all writers, recovery, publication, observation, CAS, registration,
  and amendment exclusively locked.

## Scope and Verification Conditions

The active `GO` for `gtkb-artifact-registry-authoritative-hygiene-sweep` is an
older architecture-only approval that explicitly did not authorize source
mutation; it is not an active exact claim and does not conflict with this
bounded implementation. WI-5714's write-linearizability thread is terminal
`VERIFIED` v010, so its completed write-CAS work is a dependency baseline, not
an overlapping active change.

Keeping `groundtruth-kb/tests/test_sot_registry.py` verification-only is
sound. Its public-loader regression evidence must be executed but the changed
wrapper/interposition, Windows-spawn, read-only, digest-race, and fallback
fixtures belong in the declared control-plane test module. WI-5715 must not
edit, restore, stage, or attribute the verification-only module.

Before any later `VERIFIED` verdict, the implementation report must provide
deterministic evidence for all proposal acceptance criteria, including:

1. Windows-spawn overlap of at least four readers with identical coherent
   results, not merely a duration assertion.
2. Controlled writer interposition, committed and aborted heads, nonterminal
   and missing legacy heads, marker-read failure/unprovability, and exact
   one-fallback behavior.
3. Read-only and `PRAGMA query_only` enforcement for every optimistic SQLite
   handle; no writer or recovery path may use it.
4. Unchanged-marker schema, TOML, path, and parity failures preserving their
   original typed exceptions; custom/standalone public wrapper regressions
   retaining current behavior.
5. Live out-of-band-byte freshness, exact digest mismatch rejection, and no
   digest-keyed cache or hidden stale result.
6. The complete `test_registry_control_plane.py` and unmodified
   `test_sot_registry.py` suites, exact-path Ruff/format/diff checks, and a
   final exact three-target diff assertion.

## Read-Only Checks Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5715-registry-read-scalability
PASS: allowed under controlling PAUTH v2; no required/advisory gaps.

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5715-registry-read-scalability
PASS: 4 must-apply clauses; 0 evidence or blocking gaps.

groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest groundtruth-kb/tests/test_registry_control_plane.py groundtruth-kb/tests/test_sot_registry.py -q --tb=short
PASS: 64 passed in 28.63s.

groundtruth-kb\\.venv\\Scripts\\ruff.exe check <three declared targets>
PASS: All checks passed.

groundtruth-kb\\.venv\\Scripts\\ruff.exe format --check <three declared targets>
PASS: 3 files already formatted.

git --no-optional-locks diff --check -- <three declared targets>
PASS.
```

No dispatcher or TAFE state was changed, and no source, test, configuration,
or external system was mutated during this review.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
