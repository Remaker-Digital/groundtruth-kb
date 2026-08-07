REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: f60c8a1c-ab58-4887-a466-8b8444126390
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5942-bridge-helper-publication-capability
Version: 013
Responds to: bridge/gtkb-wi5942-bridge-helper-publication-capability-012.md
Approved proposal: bridge/gtkb-wi5942-bridge-helper-publication-capability-011.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5942
Recommended commit type: fix:
target_paths: [".goose/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_bridge_helper_publication_capability.py"]

# GT-KB Bridge Implementation Proposal - WI-5942 helper publication capability - 013 (REVISED)

## Why This Revision Exists

`-012` granted GO on `-011`. Before writing any code under that GO, this
session verified `-011`'s central scope claim against the source and found it
**false**. This REVISED corrects the record before implementation rather than
implementing a proposal known to rest on a wrong premise. `GO -> REVISED` is a
lawful transition; no code was written under the GO.

`-011` Disclosure 2 asserted: *"All five helper copies lack mint/consume
entirely ... Fixing `.goose` alone leaves Claude, Codex, Cursor and every
scaffolded adopter still stranding bridges."* That assertion is withdrawn.

## Correction 1 - The scope claim was wrong (3 defective copies, not 6)

`-011`'s evidence was a **marker census** for the literal symbols
`mint_bridge_publication_capability` / `consume_bridge_publication_capability`.
Those symbols are indeed absent from all six copies - but three of the six
achieve the identical effect by **delegating** to
`scripts.gtkb_bridge_writer.write_bridge_file`, which mints and consumes
internally. The census measured a proxy and reported it as the property.

Corrected evidence - actual write mechanism per copy:

| Copy | Write mechanism | Produces receipt |
| --- | --- | --- |
| `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` | `_bridge_writer.write_bridge_file(...)` (3 refs) | **yes - correct** |
| `.codex/skills/gtkb-bridge-propose/helpers/write_bridge.py` | `_bridge_writer.write_bridge_file(...)` (3 refs) | **yes - correct** |
| `.cursor/skills/gtkb-bridge-propose/helpers/write_bridge.py` | `_bridge_writer.write_bridge_file(...)` (2 refs) | **yes - correct** |
| `.goose/skills/gtkb-bridge-propose/helpers/write_bridge.py` | `bridge_file.write_bytes(...)` direct (L587) | **no - defective** |
| `groundtruth-kb/templates/skills/gtkb-bridge-propose/helpers/write_bridge.py` | `write_bytes(...)` direct (2 refs, 0 delegation) | **no - defective** |
| `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` | `write_bytes(...)` direct (2 refs, 0 delegation) | **no - defective** |

`.claude`, `.codex` and `.cursor` require **no change** and are removed from
`target_paths`. The surviving half of `-011`'s argument stands and is the
reason this thread is still broader than WI-5942's original one-file scope:
**both scaffold templates are defective**, so every adopter inherits the
stranding defect from first use.

## Correction 2 - `.goose` skills are not generator-backed

`-011` and WI-5999 described the `.goose` helper as a *generated projection* to
be fixed by regeneration. `scripts/` contains
`generate_antigravity_skill_adapters.py`, `generate_api_skill_adapters.py`,
`generate_codex_skill_adapters.py` and `generate_cursor_skill_adapters.py` -
but **no goose skill-adapter generator**. `generate_goose_manifest.py` declares
`source_of_truth = ".goose/skills/gtkb-*/SKILL.md"`; it indexes existing
adapters rather than emitting them.

`.goose` helper files are therefore **maintained copies**, and the fix is a
direct edit bringing `.goose` to the same delegating form as canonical
`.claude` - not a regeneration step.

## Correction 3 - The loss mechanism is inferred, not proven

`-011` attributed the destruction of the prior WI-5942 implementation to commit
`629fead8c`. That commit's 42-path set includes
`.goose/skills/gtkb-verify/helpers/write_verdict.py` but **not**
`.../gtkb-bridge-propose/helpers/write_bridge.py`. It never committed a change
to the lost file. A bulk copy writing bytes identical to HEAD would leave no
diff and no commit entry, which is consistent with every observation - but that
is an inference, not evidence, and it is recorded as such.

What remains **fully evidenced** is the loss itself: the helper is tracked and
unmodified, HEAD contains no capability code, and the two implementation-
asserting tests fail today where `-010` recorded 4 passed on 2026-08-06.
WI-5999 has been corrected accordingly (v2): its hazard is narrowed to the four
generator-backed surfaces and no longer cites `.goose` as an instance.

## Correction 4 - The existing test mandates the wrong design

`platform_tests/scripts/test_bridge_helper_publication_capability.py::test_helper_has_mint_consume_integration`
asserts that `inspect.getsource(propose_bridge_codex_non_bypass)` contains the
literal strings `mint_bridge_publication_capability`,
`consume_bridge_publication_capability`, `_registry_publication_enabled` and
`recover_bridge_publication`.

The **correct** implementation - the canonical `.claude` delegating form -
contains none of those literals. The test as written therefore fails the
correct design and passes only a design that inlines the governed writer's
two-phase-commit transaction into each helper copy. That would duplicate
roughly two hundred lines of mint/sidecar/write/verify/consume/compensate logic
across every harness copy and create a fresh divergence hazard of exactly the
kind this thread exists to close.

The test is therefore rewritten to assert the **behavioural** property:
a helper-written bridge file yields a `consumed` row in
`sot_registry_bridge_publication_capabilities`. Delegation satisfies it;
inlining would also satisfy it; neither is mandated by assertion shape.

## Proposed Change

1. `.goose/.../write_bridge.py` - replace the direct
   `bridge_file.write_bytes(...)` path in `propose_bridge_codex_non_bypass`
   (and `propose_bridge`) with delegation to
   `_bridge_writer.write_bridge_file(...)`, matching canonical `.claude`
   byte-for-byte in that region.
2. Both `groundtruth-kb/templates/.../write_bridge.py` copies - same delegation
   change, so scaffolded adopters inherit the receipt-producing path.
3. `platform_tests/scripts/test_bridge_helper_publication_capability.py` -
   replace the literal-symbol assertions with a behavioural assertion over the
   capability table, and extend coverage from `.goose` alone to all six copies
   so parity is mechanically enforced rather than asserted per-file.

### KB / MemBase mutation scope

This implementation performs no MemBase mutation. The change edits three helper
copies and one test file; it inserts, updates and retires nothing in
`groundtruth.db`, and `groundtruth.db` is therefore correctly absent from
`target_paths`.

Two adjacent facts, stated so the boundary is unambiguous:

- The **runtime** effect of the repaired helper is that a future bridge write
  will mint and consume a publication-capability row. That is product behaviour
  of the governed writer, exercised later by whoever files a bridge document -
  not a write performed by this change.
- The **behavioural test** must therefore bind to an isolated fixture database,
  never canonical `groundtruth.db`. This is an explicit acceptance condition,
  not an implementation detail: WI-5317 recorded the failure mode where writer
  fixtures reached real project state, and this thread must not reproduce it.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed.
This work restores conformance to existing constraints; the corrections above
change the factual basis and the scope, not the governing requirements.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail and publication-capability authority; the receipts this work produces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - cross-harness parity enforcement; the constraint the delegating form satisfies.
- `ADR-CROSS-HARNESS-PARITY-001` - Cross-Harness Behavioral Parity Invariant; behavioural parity is what the rewritten test asserts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived test mapping below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section.
- `GOV-WORK-TREE-HYGIENE-001` - worktree-state integrity; the loss disclosure.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims derive from fresh canonical reads; the discipline that produced all four corrections above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - corrections preserved as durable artifacts (WI-5999 v2, this version) rather than left in session context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development decision underlying that stance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers; discovering an approved proposal's premise to be false is a capture-threshold event, discharged by this REVISED.

## Owner Decisions / Input

- Owner AskUserQuestion 2026-08-07 (session `f60c8a1c`), "GO disposition":
  selected **"Accept GO and implement"**.
- Owner AskUserQuestion 2026-08-07 (session `f60c8a1c`), "Correction", after
  this session surfaced that the approved scope claim was false: selected
  **"File REVISED -013 with corrected analysis"** in preference to implementing
  the approved text. That decision is the direct authority for this version.
- No owner waiver is requested.

## Prior Deliberations

- `bridge/gtkb-wi5942-bridge-helper-publication-capability-011.md` - the proposal whose scope claim is corrected here.
- `bridge/gtkb-wi5942-bridge-helper-publication-capability-012.md` - the GO being revised against.
- `bridge/gtkb-wi5942-bridge-helper-publication-capability-010.md` - NO-GO whose Finding 1 remains open.
- `DELIB-202667533` (AT-01) - owner-ratified commit-first-publish-after finalization ordering.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - VERIFIED commit-finalization is mandatory.
- `DELIB-20266278` - owner authorization of the dispatch-treadmill-drain program.
- WI-5825 - governed recovery for unreceipted chains; still blocks terminal VERIFIED for `-001`/`-003`.
- WI-5999 (v2) - generated-projection overwrite hazard, corrected and narrowed by this session.

## Specification-Derived Verification Plan

| Specification / requirement | Test or verification command | Expected result |
| --- | --- | --- |
| WI-5942 receipt production (behavioural) | rewritten `pytest platform_tests/scripts/test_bridge_helper_publication_capability.py -q` | all pass; a helper-written bridge file yields a `consumed` capability row |
| `ADR-CROSS-HARNESS-PARITY-001` - parity across copies | delegation census asserting every one of the six copies reaches `write_bridge_file` | 6/6 delegate |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `.goose` delegating region compared against canonical `.claude` | equivalent |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | query `sot_registry_bridge_publication_capabilities` after a helper-written file | row present, `capability_state='consumed'` |
| `GOV-WORK-TREE-HYGIENE-001` | `ruff check` and `ruff format --check` on changed Python files | clean on both gates |

## Cross-Harness Disposition

`target_paths` no longer touch `.claude/skills/**` or `.codex/skills/**`, so the
harness-surface marker set is not triggered. The section is retained because
cross-harness parity is the substance of this thread.

| Harness / surface | Disposition |
| --- | --- |
| Claude, Codex, Cursor | **No change required.** Verified this session to delegate to the governed writer and already produce consumed receipts. Removed from `target_paths`. |
| Goose | **Behavioural parity restored by direct edit.** `.goose` is a maintained copy, not a generated projection - no goose skill-adapter generator exists - so it is brought to the canonical delegating form in place. |
| Scaffold templates (all adopters) | **Behavioural parity.** Both template copies write directly today; adopters therefore inherit the defect from first use. This is the load-bearing reason the thread is broader than one file. |
| Antigravity (`.agent`), API harness (`.api-harness`) | **Not applicable.** Neither surface carries a `gtkb-bridge-propose/helpers/write_bridge.py`; confirmed by repository-wide file census this session. |

## Risk / Rollback

- **Risk: another unverified premise.** Three of `-011`'s claims failed
  verification. This version states the write mechanism per copy with line-level
  evidence, and marks the loss mechanism explicitly as inference. Reviewers
  should treat any remaining unlabelled causal claim as a defect.
- **Risk: the rewritten test is weaker than the literal assertions.** A
  behavioural assertion over the capability table is strictly stronger for the
  property that matters (a receipt exists) and strictly weaker for implementation
  shape - which is the intended trade, since shape-assertion is what mandated the
  wrong design.
- **Risk: terminal VERIFIED still blocked.** Unchanged and unmitigated: `-001`
  and `-003` remain unreceipted pending WI-5825. This proposal does not request
  VERIFIED.
- **Rollback:** revert the four target paths; no capability row is minted by
  this change outside the helper's own runtime path, and no committed state is
  altered.

## Recommended Commit Type

- Recommended commit type: `fix:` - downgraded from `feat:` in `-011`. With the
  corrected scope this repairs three defective copies to match an existing
  correct implementation and rewrites a test; it introduces no new capability
  surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
