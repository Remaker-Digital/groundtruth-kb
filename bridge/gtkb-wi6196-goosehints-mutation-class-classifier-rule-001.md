NEW
::init gtkb lo
::open build

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4ce6b493-2826-4d39-809d-b5a880132c6c
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: interactive session, owner-declared role via canonical init keyword
session_init_keyword: ::init gtkb pb
activity_init_keyword: ::open build

bridge_kind: prime_proposal
Document: gtkb-wi6196-goosehints-mutation-class-classifier-rule
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-08-13 UTC
Reviewer: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6196
related_work_items: ["WI-5918", "WI-5917", "WI-6001"]
Recommended commit type: fix
target_paths: ["config/governance/project-authorization-operation-taxonomy.toml", "platform_tests/scripts/test_implementation_authorization.py"]
implementation_scope: add one classifier path rule so the root Goose guidance dotfile classifies as configuration, plus a regression test
kb_mutation_in_scope: false
database_mutation_in_scope: false
registry_mutation_in_scope: false
database_registry_or_index_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Implementation Proposal - WI-6196: admit the root Goose guidance dotfile to the mutation-class taxonomy

## Problem

`.goosehints` classifies as `unclassified`, and the PAUTH operation-time gate
hard-denies unclassified target paths. This makes any bridge proposal that
declares `.goosehints` in `target_paths` **unfileable**, which in turn makes
Goose's only role-guidance surface mechanically unmaintainable.

This is not theoretical. Filing the WI-5918 parity revision with `.goosehints`
in `target_paths` -- exactly as required by the Loyal Opposition NO-GO at
`bridge/gtkb-goose-governance-hook-enforcement-parity-002.md` finding F1 (P1,
blocking) -- was hard-blocked at write time by the governed bridge writer:

```text
BridgeComplianceError: [Governance] Pre-filing applicability preflight failed:
file_path=bridge/gtkb-goose-governance-hook-enforcement-parity-003.md;
preflight={"blocking_errors": [
  "PAUTH operation-time denial (implementation_packet_create): target_mutation_class_not_allowed: .goosehints (unclassified)",
  "PAUTH operation-time denial (implementation_start): target_mutation_class_not_allowed: .goosehints (unclassified)"
], "missing_required_specs": []}
```

The result is a governance deadlock. F1 requires `.goosehints` in `target_paths`
and explicitly rejects descoping it, because Acceptance Criterion 6 and the owner
survivability constraint depend on it. The mutation-class gate makes any such
proposal unfileable. Both requirements cannot be satisfied until the classifier
admits the path. The predecessor session's removal of `.goosehints` from that
cohort was therefore mechanically forced, not an oversight.

## Root Cause

`classify_target` in
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
(L206-268) resolves a mutation class from registered `path_rules` first, then a
name and prefix heuristic. Exactly one path rule is registered today:
`.githooks/**` -> `configuration`.

The heuristic's `configuration` branch (L236-265) matches a first-segment set
that includes `.agent`, `.api-harness`, `.claude`, `.codex`, `.cursor`,
`.github`, `.goose` and `config`; an exact-name set that includes `agents.md`,
`claude.md`, `.dockerignore`, `.env`, `groundtruth.toml` and `pyproject.toml`;
and any `.toml` / `.yaml` / `.yml` suffix.

`.goosehints` is a root-level extensionless dotfile. Its first path segment is
the entire filename, which is absent from the prefix set; it is absent from the
exact-name set; and it has no matching suffix. It therefore reaches the terminal
fallthrough and classifies `unclassified`.

The inconsistency is precise and worth stating: the `.goose/` **directory**
classifies `configuration`, and the direct cross-harness analogues `agents.md`
and `claude.md` are both explicitly listed as `configuration`, but Goose's
root guidance **file** is not. This proposal removes that inconsistency rather
than introducing a new category.

## Two Distinct Mechanisms (do not conflate)

An unclassified target path is not merely diagnostic:

1. `_check_unclassified_target_paths` in
   `scripts/bridge_applicability_preflight.py` (L576-588) reports unclassified
   paths as diagnostic metadata under
   `target_path_coverage.unclassified_target_paths`, and `preflight_passed`
   (L1202) is computed as `not missing_required and not blocking_errors`, which
   does not consider that list.
2. The PAUTH operation-time evaluation independently **hard-denies**, and its
   denial lands in `blocking_errors`, which does fail the preflight.

Mechanism 2 is what blocks the parity filing. Recording both here so a later
reader does not conclude from mechanism 1 that unclassified paths are harmless.

## Proposed Change

Add one data-driven path rule to
`config/governance/project-authorization-operation-taxonomy.toml`:

```toml
[[path_rule]]
pattern = ".goosehints"
mutation_class = "configuration"
```

No code change. The rule mechanism already exists and is validated:
`_registered_path_rules` (L74-113) requires `pattern` and `mutation_class`
strings and rejects any class outside the canonical set.

## Measured Evidence

Validated in memory against the live taxonomy, writing nothing, by appending the
proposed rule to a copy via `dataclasses.replace` and re-classifying:

```text
canonical_classes: bridge, configuration, documentation, governance_evidence,
                   metadata, repository_metadata, runtime_state, source, test
existing path_rules: [('.githooks/**', 'configuration')]

BEFORE: .goosehints -> unclassified
AFTER : .goosehints -> configuration

regression_drift: NONE (all eight other WI-5918 target paths classify identically)
```

The eight regression-checked paths were
`.agents/plugins/gtkb/hooks/hooks.json` (governance_evidence),
`config/agent-control/gtkb-harness-capability-registry.toml` and
`config/registry/sot-artifacts.toml` (configuration),
`platform_tests/scripts/test_goose_hook_parity.py` and
`platform_tests/scripts/test_harness_parity.py` (test),
`scripts/check_harness_parity.py`, `scripts/goose_hook_adapter.py` and
`scripts/lo_file_safety_payloads.py` (source).

`configuration` is a canonical class and is already present in the
`allowed_mutation_classes` of both
`PAUTH-PROJECT-GTKB-GET-HEALTHY-RECOVERY-HARNESS-PARITY-001` and this
proposal's own authorization, so no PAUTH amendment is required and none is
sought.

## Why `configuration` And Not `documentation`

Both are canonical and both are allowed by the relevant authorizations.
`configuration` is chosen for consistency with the existing heuristic, which
already classifies `agents.md`, `claude.md` and the `.goose/` directory as
`configuration`. Choosing `documentation` would classify Goose's guidance file
differently from its Claude and Codex analogues for no functional reason, and
would leave the observed inconsistency partly intact.

## Explicitly Rejected Alternative

Do **not** add `unclassified` to any PAUTH `allowed_mutation_classes` list. That
would authorize every path the classifier cannot name, converting a fail-closed
gate into a fail-open one for the entire class of unrecognized targets. The
defect is that the classifier does not recognize a legitimate path, not that the
gate is too strict. This proposal keeps the gate fail-closed and narrows what is
unrecognized by exactly one path.

## Scope Boundary

This proposal adds one path rule and one regression test. It does not:

- alter `classify_target`'s heuristic or any other classifier code path;
- add any other pattern, including sibling harness dotfiles such as
  `.cursorrules`; a general root-dotfile rule may be warranted but is a wider
  change requiring its own evidence and review;
- modify any PAUTH, allowed-class list, or forbidden-operation list;
- touch `.goosehints` itself, which remains WI-5918's work under the parity
  cohort;
- perform any MemBase, database, registry, index, dispatcher, or TAFE mutation.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is the mechanical
implementation-start gate in `.claude/rules/codex-review-gate.md`, which requires
that protected mutations be authorized by a live GO'd proposal's `target_paths`
and an implementation-start packet. That gate is working as designed; the defect
is that a legitimate governed path cannot be expressed to it. No new or revised
requirement is needed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority model; this fix restores the
  ability to file a compliant proposal for a legitimate governed path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing
  specification is cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification mapping
  below derives an executable test per linked specification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the deadlock, the measured denial, and
  the rejected alternative are preserved as durable artifacts on WI-6196.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability preserved across
  WI-6196, WI-5918, the parity NO-GO, and this proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the blocked state of WI-5918 and the
  prerequisite relationship are explicit.
- `GOV-STANDING-BACKLOG-001` - work remains on canonical WI-6196; no second
  backlog is created.
- `.claude/rules/codex-review-gate.md` - the mechanical implementation-start
  gate whose target-path authorization this fix makes expressible.

## Prior Deliberations

- `bridge/gtkb-goose-governance-hook-enforcement-parity-002.md` - the Loyal
  Opposition NO-GO whose finding F1 requires `.goosehints` in `target_paths` and
  explicitly rejects descoping it. This proposal is the prerequisite that makes
  F1 satisfiable.
- `DELIB-20260808012227` - owner decision establishing Claude/Goose parity as the
  root problem and folding it into the Get Healthy program; the reason
  `.goosehints` must be maintainable at all.
- `DELIB-20260808012226` - owner decision reconciling Get Healthy authority
  scope; precedent for keeping authority explicit rather than inferred.
- `DELIB-202667185` - records that Loyal Opposition NO-GO at
  `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-008.md` (F1) correctly
  refused to expand implementation authority by interpretation. That precedent is
  why this fix is filed as its own carrier under an authorization that actually
  covers it, rather than absorbed into WI-5918 whose PAUTH whitelist is
  `["WI-5917", "WI-5918"]` and does not include WI-6196.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner AUQ 2026-08-13, session `4ce6b493-2826-4d39-809d-b5a880132c6c`: asked
  which carrier the classifier proposal should use given WI-6196 falls outside
  the parity PAUTH whitelist, the owner selected "Carry WI-6196 under
  BRIDGE-PROTOCOL-RELIABILITY" -- add WI-6196 to
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` and cite
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  (verified: `included_work_item_ids` empty so it covers all project work items,
  `allowed_mutation_classes` includes `configuration` and `test`, active v2, no
  expiry, and `--covers-path` confirms it covers the taxonomy file), while
  retaining the Get Healthy membership so the program still tracks WI-6196 as a
  WI-5918 prerequisite. That membership change was applied before this filing.
- Owner AUQ 2026-08-13, same session: directed this session to revise the NO-GO'd
  parity fix. That revision is blocked by this prerequisite, which is why this
  proposal exists; it grants no new implementation scope.
- No new owner decision is requested by this filing.

## Specification-Derived Verification Mapping

| Linked specification | Derived test / evidence |
|---|---|
| `.claude/rules/codex-review-gate.md` implementation-start gate | New regression test in `platform_tests/scripts/test_implementation_authorization.py` asserting `classify_target(".goosehints").mutation_class == "configuration"` against the live taxonomy. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Same test additionally asserts non-regression: each of the eight other WI-5918 target paths classifies to its pre-change class (`governance_evidence`, `configuration` x2, `test` x2, `source` x3). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end proof that the deadlock is broken: after the rule lands, `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-goose-governance-hook-enforcement-parity` returns `blocking_errors: []` for a candidate carrying `.goosehints`, where it currently returns the two `target_mutation_class_not_allowed` denials quoted above. Both before and after outputs recorded in the implementation report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on this proposal exits 0 with `missing_required_specs: []`. |
| Taxonomy integrity | Assert `load_operation_taxonomy()` still parses and that the new rule's class is in `canonical_mutation_classes`, so `_registered_path_rules` validation is exercised rather than bypassed. |
| Fail-closed preservation | Assert an unrelated unrecognized path (for example a root extensionless dotfile not named `.goosehints`) still classifies `unclassified`, proving the fix narrows the unrecognized set by exactly one path and does not weaken the fallthrough. |
| Code quality | `ruff check` and `ruff format --check` on the changed test file, reported separately per the Pre-File Code-Quality Gates. |

## Risk and Rollback

- Risk: the rule pattern is matched case-sensitively by `fnmatchcase` against a
  lowercased path, so a differently-cased filename would not match. Mitigation:
  `classify_target` lowercases before matching (L212) and the pattern is already
  lowercase; the test asserts the exact live behavior rather than assuming it.
- Risk: a future second rule matching `.goosehints` would produce
  `len(governed_classes) > 1` and classify `unclassified` again (L218-219).
  Mitigation: the regression test pins the resolved class, so any future
  overlapping rule fails the test rather than silently re-breaking the path.
- Risk: broadening classification weakens the fail-closed posture. Mitigation:
  exactly one exact-match pattern is added, no wildcard; a dedicated test asserts
  unrelated unrecognized paths still classify `unclassified`.
- Risk: the taxonomy file is shared with other in-flight work. Verified at filing
  time that `config/governance/project-authorization-operation-taxonomy.toml` is
  clean; the exact preimage is bound at implementation start from the worktree
  blob.
- Rollback: delete the four-line `[[path_rule]]` block and the added test.
  `.goosehints` returns to `unclassified` and the prior deadlock resumes; no
  other path, class, authorization, or gate is affected. No migration or state
  cleanup is required.

## Files Expected To Change

- Modified: `config/governance/project-authorization-operation-taxonomy.toml`
  (one `[[path_rule]]` block added)
- Tests: `platform_tests/scripts/test_implementation_authorization.py`
  (regression + non-regression + fail-closed assertions added)

Both entries appear in `target_paths`; `target_paths` declares nothing absent
from this list.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
