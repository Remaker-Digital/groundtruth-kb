REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7c5bf02a-db61-459e-9321-695a31696526
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5617-dispatcher-next-spike-manifest-closure
Version: 003
Responds to: bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-002.md
Date: 2026-08-06 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5617

target_paths: ["config/dispatcher/requirements-dispatcher-next-spike.txt", "platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

**No KB mutation.** This proposal performs no MemBase write and does not modify
`groundtruth.db`.
**No approval-evidence work.** This proposal creates no formal-artifact-approval packet
and writes no approval-packet path.
**No dispatcher or TAFE mutation.** This proposal changes no dispatcher configuration,
substrate, scheduled task, routing rule, or harness registry entry. The legacy
TAFE/dispatcher remains quiesced per `DELIB-20260806011871`.

# WI-5617 - Close the Dispatcher Next foundation spike: declare the pinned-dependency manifest

## Summary

The Dispatcher Next foundation spike is **implemented and green** but has one absent
declared target. This proposal closes that single gap so WI-5617 can reach a legitimate
`VERIFIED` and unblock the WI-5618..WI-5624 spine.

Five of the six targets accepted by the prior `GO` exist on disk and pass:

| Target | State |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py` | present (2,407 B) |
| `groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py` | present (29,445 B) |
| `groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py` | present (32,332 B) |
| `groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py` | present (18,809 B) |
| `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py` | present (38,821 B); **11 passed in 23.97s** |
| `groundtruth-kb/requirements-dispatcher-next-spike.txt` | **ABSENT - and unauthorizable at that path; see Root Cause** |

## Problem Statement

`test_dispatcher_next_foundation.py::test_pinned_dependencies_import_under_python_314`
asserts exact runtime dependency versions through `importlib.metadata`:

```
assert versions == {"a2a-sdk": EXPECTED_A2A_VERSION, "dbos": EXPECTED_DBOS_VERSION}
assert importlib.metadata.version("dbos") == EXPECTED_DBOS_VERSION
assert importlib.metadata.version("a2a-sdk") == EXPECTED_A2A_VERSION
```

Live constants (read from `groundtruth_kb.dispatcher_next.foundation`, 2026-08-06):
`EXPECTED_DBOS_VERSION = 2.27.0`, `EXPECTED_A2A_VERSION = 1.1.1`;
`dependency_versions()` returns `{'dbos': '2.27.0', 'a2a-sdk': '1.1.1'}`.

Nothing in the repository **declares** those pins. A grep of the test module for
`requirements` returns no match, so the manifest is not merely unread - it does not exist.
The consequence is a reproducibility gap: the spike asserts an exact environment it
provides no way to reconstruct. A fresh checkout, a CI runner, or a reviewer attempting
independent verification must discover the pins by reading source constants. That is
precisely the environment-declaration role the manifest was accepted to fill.

## Live State Correction (read before review)

Three claims in WI-5617's current MemBase record and in
`bridge/gtkb-dispatcher-next-foundation-spike-013.md` are **stale against live state**.
They are corrected here rather than carried forward, because they are the stated reason
the P0 spine has been parked.

1. **"parent `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE` is retired"** - false as of
   2026-08-06. `gt projects show PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE` reports
   `GT-KB Dispatcher Next Control Plane [active]`.
2. **"its legacy PAUTH cannot be widened into current whole-project authority"** - moot.
   `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` is at **v4, status `active`**, its `project_id`
   IS `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE`, and its `included_work_item_ids`
   explicitly lists `WI-5617` through `WI-5624` plus `WI-5625`, `WI-5626`, `WI-5628`,
   `WI-5629`. Owner decision of record:
   `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`.
3. **"the accepted six-target verification cohort has drifted because
   `groundtruth-kb/requirements-dispatcher-next-spike.txt` is absent"** - **true**, and it
   is the only surviving blocker. This proposal addresses exactly it.

`-013` listed four prerequisites for resuming: (a) new active project, (b) whole-project
PAUTH, (c) missing requirements file addressed, (d) fresh proposal. (a) and (b) are
already satisfied by live state; this proposal supplies (c) and is (d).

## Disclosure: prior thread terminated by an out-of-role verdict

`bridge/gtkb-dispatcher-next-foundation-spike-013.md` carries first-line status `VERIFIED`
with `author_identity: prime-builder/goose/G` and `bridge_kind: pb_respond`. Two protocol
problems follow, and they are disclosed rather than relied upon:

- `.claude/rules/file-bridge-protocol.md` § Statuses assigns `VERIFIED` to **Loyal
  Opposition**. A Prime-authored `VERIFIED` is not a valid verdict.
- The § Post-Verdict Transition Table permits `VERIFIED` only as a post-`GO` successor to
  `NEW` or `REVISED`. The observed transition is `GO` (v012) -> `VERIFIED` (v013), which the
  table does not allow.

This proposal therefore does **not** treat that thread as legitimately verified, and does
not build on it. It opens a fresh thread and re-derives every claim from live state. The
defect itself is out of scope here (it is a governance-repair concern on a terminal
append-only chain, not implementation work) and is recommended for its own tracked item -
see Follow-On below.

## Revision Basis - the GO'd path is unimplementable

`-002` issued a clean `GO`. Implementation was then refused at the very first Write:

```
BLOCKED (GTKB-WORK-SUBJECT): Current work subject is GT-KB. This change targets
application product artifacts (config/dispatcher-next/requirements-spike.txt).
```

**Cause: GT-KB has two independent path classifiers, and only one is exercised by the
mandatory preflights.**

| Classifier | Purpose | Checked by preflight? | Verdict on `config/dispatcher-next/...` |
| --- | --- | --- | --- |
| `classify_target` (`project_authorization_operation_time`) | PAUTH mutation class | **yes** | `configuration` - allowed |
| `classify_root` (`scripts/workstream_focus`) | work-subject write gate | **no** | `application_product` - **refused** |

`-001` validated the relocation against `classify_target` only. That was my error, and it
was not catchable from the preflight output: `preflight_passed: true`, PAUTH
`allowed: true`, `blocking_errors: []` were all genuine, and the reviewer had no signal that
a second classifier would refuse the write. The structural gap is recorded as **WI-5972**.

**Fix: relocate into a directory already carved out of the blanket `config/` rule.** Measured
2026-08-06, both classifiers agree on the new path:

```
classify_target -> configuration                       (PAUTH: allowed)
classify_root   -> current_repo_bridge_or_governance   (work subject: permitted)
```

`config/dispatcher/` is the existing dispatcher-configuration directory and is one of the six
subdirectories WI-5100 carved out. A pinned-dependency manifest for the dispatcher's
successor is dispatcher configuration, so the location is semantically correct rather than
merely convenient. The filename is widened to
`requirements-dispatcher-next-spike.txt` so the Dispatcher Next scope stays explicit inside a
directory shared with legacy dispatcher config.

Waiting for **WI-5957** (GO'd, blocked on a peer claim) would not have helped: it adds
`config/hooks/` to the carve-out, not `config/dispatcher-next/`.

Nothing else changes. Content, purpose, drift-guard test, acceptance criteria, and the
root-cause analysis of the original `groundtruth-kb/` path are carried forward unaltered;
only the manifest's directory and filename move.

## Root Cause: the accepted cohort contained an unauthorizable target

Investigation for this proposal found why the manifest was never created, and it is not
the retired-parent story. **The accepted target path cannot be authorized by the
operation-time classifier**, so no implementation-start packet could ever be minted for it.

`classify_target` in
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
(lines 163-227) classifies by directory prefix and a fixed extension list. `.txt` appears in
**no** extension branch: `configuration` covers `.toml/.yaml/.yml`, `source` covers
`.py/.js/.ts/.tsx/.jsx/.ps1/.sh/.csv`, `governance_evidence` covers `.md/.json/.jsonl`.
A `.txt` file is therefore classifiable only when its directory prefix classifies it.

`groundtruth-kb/` is not such a prefix - the source branch matches `groundtruth-kb/src/`,
not the package root. Measured live:

```
unclassified   groundtruth-kb/requirements-dispatcher-next-spike.txt
configuration  config/dispatcher/requirements-dispatcher-next-spike.txt
source         applications/Agent_Red/requirements.txt
```

The three existing `requirements*.txt` files in the repository all live under
`applications/Agent_Red/`, classified `source` by their `applications` prefix. There is no
precedent for a requirements file at `groundtruth-kb/` root, and no tracked `.txt` there.

Filing this proposal against the original path reproduced the failure exactly:

```
PAUTH operation-time denial (implementation_packet_create):
  target_mutation_class_not_allowed: groundtruth-kb/requirements-dispatcher-next-spike.txt (unclassified)
PAUTH operation-time denial (implementation_start):
  target_mutation_class_not_allowed: groundtruth-kb/requirements-dispatcher-next-spike.txt (unclassified)
```

This is the documented `unclassified` mutation-class condition in
`.claude/rules/canonical-terminology.md`, whose stated remedy is to refine the path to match
a classified pattern.

**Consequence for review:** this proposal relocates the manifest to
`config/dispatcher/requirements-dispatcher-next-spike.txt`, which classifies `configuration` - a class
PAUTH v4 allows. This is a deliberate, disclosed departure from the prior cohort's declared
path. The artifact, its content, and its purpose are unchanged; only its location moves, to
one the authorization system can actually approve. `config/` is where GT-KB keeps governed
configuration, and a dependency-pin manifest is configuration.

Reviewers who prefer the original location should NO-GO this proposal in favour of the
systemic fix noted under Follow-On, which would make `requirements*.txt` classifiable
anywhere. That fix is deliberately not bundled here: it edits a shared governance
classifier that every thread's authorization depends on, and it should not ride along
inside a P0 unblock.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation
  authorization; discharged by the PAUTH v4 binding above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each acceptance
  criterion to a test.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only; no `applications/`
  path is touched.
- `.claude/rules/file-bridge-protocol.md` - status semantics and the transition table cited
  in the disclosure above.
- `.claude/rules/codex-review-gate.md` - the implementation-start authorization gate.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner decision behind the
  program authorization.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - the master Prime Builder
  authorization for the Dispatcher Next program; the authority this proposal files under.
- `DELIB-20260806011871` - owner directive quiescing the **legacy** TAFE/dispatcher,
  which explicitly does not apply to the Dispatcher Next program. Cited so no reviewer
  reads this proposal as re-activating a quiesced substrate; it does not.
- `bridge/gtkb-dispatcher-next-foundation-spike-007.md` - the REVISED proposal whose
  six-target cohort this proposal completes.
- `bridge/gtkb-dispatcher-next-foundation-spike-013.md` - the out-of-role terminal verdict
  disclosed above; cited as history, not as authority.
- Deliberation search executed 2026-08-06
  (`gt deliberations search "Dispatcher Next foundation spike DBOS A2A pinned dependencies
  manifest" --limit 6`) returned no decision on this topic; all six results scored >1.0
  (distant) and concern unrelated threads. No prior decision accepts or rejects declaring
  the spike's pinned dependencies.

## Requirement Sufficiency

Existing requirements sufficient. The manifest was already an accepted target of the
prior `GO`'d cohort; this proposal supplies the artifact rather than introducing a new
requirement. No requirement is created or revised.

## Proposed Change

### C1 - Create the pinned-dependency manifest

Create `config/dispatcher/requirements-dispatcher-next-spike.txt` declaring exactly the two
pins the foundation asserts at runtime:

```
dbos==2.27.0
a2a-sdk==1.1.1
```

The file carries a header comment naming its authority (WI-5617, the foundation module
constants) so a reader knows the pins are asserted in code, not merely suggested.

### C2 - Guard the manifest against drift from the constants

Create `platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py` asserting the
manifest and the code agree. Without this, the manifest becomes a second source of truth
that can silently diverge from `EXPECTED_DBOS_VERSION` / `EXPECTED_A2A_VERSION` - which
would be worse than having no manifest, because it would be confidently wrong.

The guard parses the manifest and asserts set-equality against `dependency_versions()`, so
adding, removing, or re-pinning a dependency on either side fails the test.

## Test Plan (specification-derived)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | reproducibility gap (Problem Statement) | the manifest file exists at the declared path and is non-empty |
| T2 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | every pin parsed from the manifest matches `dependency_versions()` exactly, as a set comparison in both directions |
| T3 | drift guard (C2) | the manifest names exactly the dependency set the foundation asserts - no extra pin, no missing pin |
| T4 | manifest well-formedness | each non-comment line parses as `name==version` with an exact `==` pin; a range or unpinned line fails |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py
```

The existing foundation suite is re-run to prove this change does not disturb it
(baseline measured 2026-08-06: 11 passed in 23.97s).

## Acceptance Criteria

1. `config/dispatcher/requirements-dispatcher-next-spike.txt` exists, completing the sixth target of the cohort accepted by the prior
   `GO` at its relocated, authorizable path (T1).
2. Manifest pins equal `dependency_versions()` exactly, in both directions (T2, T3).
3. Every manifest line is an exact `==` pin (T4).
4. `test_dispatcher_next_foundation.py` shows no regression - 11 passed.
5. Both ruff gates pass on the new test file.

## Risk and Rollback

- **Risk: the manifest drifts from the constants later.** This is the material risk, since
  a wrong manifest is worse than none. Mitigated by T2/T3, which fail on any divergence in
  either direction.
- **Risk: pins captured from a stale environment.** Mitigated by deriving the values from
  `dependency_versions()` at implementation time and asserting equality in the test, rather
  than transcribing them by hand.
- **Risk: scope creep into the foundation modules.** Explicitly excluded - `target_paths`
  contains only the manifest and its new guard test. No `dispatcher_next/` source file is
  modified.
- **Rollback:** delete both files; the change is purely additive and the foundation suite is
  unaffected by their absence (it passes today without them).

## Follow-On (not in this scope)

1. **Out-of-role terminal verdict.** `bridge/gtkb-dispatcher-next-foundation-spike-013.md`
   (Prime-authored `VERIFIED`; unlawful `GO` -> `VERIFIED` transition) should be tracked as
   its own governance-repair item. Same false-terminal class as WI-5939, on a P0 critical
   path.
2. **`.txt` is unclassifiable by extension.** `classify_target` cannot classify any `.txt`
   file except by directory prefix, so a dependency manifest at a package root is
   permanently unauthorizable. A classifier rule mapping `requirements*.txt` (or `.txt`
   generally, under a considered class) would remove a whole category of silently
   unimplementable cohorts. This proposal works around the gap by relocating; it does not
   fix it. Recommended as its own tracked item because it edits a shared governance
   classifier.

## Owner Decisions / Input

- **Owner directive 2026-08-06 (this session, verbatim):** *"Prioritize the Dispatcher Next
  program and drive it to completion - when it is fully implemented we will activate it."*
  and *"rehome and drive it"*. This proposal is the first concrete step of that directive.
  Investigation established that no rehoming is required - the parent project is already
  active and PAUTH v4 already covers WI-5617 - so the directive is discharged by driving
  the remaining implementation gap rather than by moving project membership.
- **`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`** - owner decision behind
  `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`, the authorization this work files under.
- **`DELIB-20260806011871`** - owner directive quiescing the legacy TAFE/dispatcher;
  scoped explicitly to exclude the Dispatcher Next program.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both declared targets are in-root platform
paths and this bridge file resides under `E:/GT-KB/bridge/`. No generated artifact is
written outside the project root. No `applications/` path is touched.

## Recommended Commit Type

`feat:` - the change adds a new declared artifact (the pinned-dependency manifest) plus its
guard test. It is not `chore:` because the manifest is a load-bearing reproducibility
declaration for a P0 program foundation, not maintenance; and not `fix:` because no
previously-working behaviour was broken.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
