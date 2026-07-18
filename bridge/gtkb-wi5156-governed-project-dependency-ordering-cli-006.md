NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - gtkb-wi5156-governed-project-dependency-ordering-cli - 006

bridge_kind: implementation_report
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 006 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-005.md
Approved proposal: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-004.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5156
Recommended commit type: feat:

## Implementation Claim

WI-5156 now provides the governed, append-only project dependency lifecycle and
exact-set project membership ordering required by
`DCL-PROJECT-DEPENDENCY-ORDERING-001`.

The implementation:

1. exposes canonical `dependent_project_id` and
   `prerequisite_project_id` direction;
2. adds `gt projects dependencies add|show|list|validate|retire|recover`;
3. validates the complete active graph and rejects self edges, cycles, unknown
   or terminal endpoints, semantic duplicates, unsupported values, and invalid
   lifecycle transitions before mutation;
4. makes project membership reorder one transaction with transaction-time
   exact-set and version revalidation;
5. reports dependency readiness, affected gate, provenance, and recovery route
   without granting PAUTH, bridge GO, work intent, or implementation-start
   authority;
6. mechanically evaluates exactly `PROJECT-DEP-A1` through
   `PROJECT-DEP-A5` in an isolated in-root MemBase; and
7. projects the canonical projects skill to Codex, Antigravity, Cursor, and
   API harness surfaces with current manifests and registry hashes.

No production dependency row, live dispatcher/TAFE state, dispatcher
configuration, credential, deployment, release, or Git history was mutated.

## Specification Links

- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-202666274` authorizes the bounded Assurance project scope carried by
  the active PAUTH.
- The owner-directed dispatcher configuration/troubleshooter hold was
  preserved. This work changed no dispatcher configuration or runtime state.
- The owner-directed canonical-reference boundary was preserved. This report
  relies on MemBase records, Deliberation Archive records, numbered bridge
  artifacts, governed source, and governed tests only.

## Prior Deliberations

- `DELIB-202666274`
- `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-004.md`
- `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-005.md`

## Specification-Derived Verification

| Requirement | Executed verification | Observed result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A1/A2 | `pytest groundtruth-kb/tests/test_project_dependency_ordering.py` and the isolated evaluator | Append-only add/retire/recover passed; invalid requests and injected write failures appended no versions |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A3 | Dependency tests, CLI tests, and evaluator exact-set reorder cases | Incomplete sets and injected failures rejected atomically; valid orders were unique and contiguous |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A4 | State-matrix, declared-gate, authorization-gate, and readiness tests | All supported states and gates produced complete readiness; only the declared gate blocked |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` PROJECT-DEP-A5 | `scripts/check_project_dependency_ordering.py --json` | Six projects and five acyclic/queryable edges; source and registry hashes emitted; rendered DAG remained non-authoritative |
| Mechanical evaluability | Isolated evaluator | Exactly PROJECT-DEP-A1 through PROJECT-DEP-A5 present and PASS; no missing or failed assertion IDs |
| Cross-harness parity | Three adapter generator checks plus `test_projects_skill_adapter.py` | Codex, Antigravity, and API checks each passed with 44 current adapters; 4 adapter tests passed |
| Modernization nonimpairment | Project artifacts, remove-item, authorization, and projects CLI suites | 77 tests passed across the four existing lifecycle suites |
| Static quality | Ruff check, Ruff format check, `py_compile`, and `git diff --check` over exact targets | All passed; six Python files already formatted |
| Bridge governance | Fresh GO, claim, schema-v3 start, applicability, clause preflight, and per-target validation | All fifteen exact targets independently returned `authorized: true` |

## Commands Executed

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_project_dependency_ordering.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_projects_cli.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/check_project_dependency_ordering.py --json`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_projects_skill_adapter.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_projects_remove_item.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_project_authorization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/generate_codex_skill_adapters.py --check --update-registry`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/generate_antigravity_skill_adapters.py --check --update-registry`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/generate_api_skill_adapters.py --check`
- `groundtruth-kb\.venv\Scripts\ruff.exe check <six exact Python targets>`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check <six exact Python targets>`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile <six exact Python targets>`
- `git diff --check -- <fifteen exact targets>`
- `groundtruth-kb\.venv\Scripts\gt.exe projects dependencies validate --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/implementation_authorization.py validate --target <each exact target>`
- `groundtruth-kb\.venv\Scripts\python.exe .codex/skills/bridge/helpers/impl_report_bridge.py plan gtkb-wi5156-governed-project-dependency-ordering-cli --compact`

## Observed Results

- New dependency specification suite: `11 passed`.
- Existing projects CLI suite: `16 passed`.
- Existing project skill adapter suite: `4 passed`.
- Existing project artifact suite: `34 passed`.
- Existing project remove-item suite: `17 passed`.
- Existing project authorization suite: `10 passed`.
- Total focused tests: `92 passed`.
- Isolated evaluator: `PASS`; all five required outer assertions passed.
- Evaluator source hash:
  `sha256:a98f527a1b95f9060eb65c6198816779576bb77c2b1194b8e0994a5b8a8baba1`.
- Dependency-kind registry hash:
  `sha256:4c8fa999f115d27aa88bc74c9276e1763c596003ee6f4617966f09affd512dc7`.
- Codex, Antigravity, and API projection checks: `PASS (44 adapters current)`
  for each surface.
- Ruff check: `All checks passed!`.
- Ruff format check: `6 files already formatted`.
- `py_compile`: exit `0`.
- `git diff --check`: exit `0`; only existing working-copy line-ending
  conversion warnings were emitted.
- Applicability preflight: pass, all fifteen target paths declared, no missing
  required or advisory specifications, and no blocking errors.
- Mandatory clause preflight: exit `0`, no blocking gaps.
- Helper plan: latest status `GO`, next version `006`, exactly fifteen changed
  targets included, and unrelated dirty paths excluded.
- All fifteen implementation-authorization validations returned
  `authorized: true`.

The optional `gt assert --spec DCL-PROJECT-DEPENDENCY-ORDERING-001` command was
not executed because the available CLI has no non-recording mode and this
proposal expressly excludes live MemBase mutation. The isolated evaluator is
the approved non-recording substitute and passed all five current outer
assertions.

The read-only production command `gt projects dependencies validate --json`
failed closed on exactly one pre-existing stale edge:
`PDEP-PROJECT-GTKB-ROLE-ENHANCEMENT-PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION-DEPENDS-ON`.
Canonical MemBase `WI-5482` and
`bridge/gtkb-wi5482-stale-project-dependency-reconciliation-001.md` already
own its retirement after WI-5156 reaches terminal VERIFIED. No dependency row
was changed here.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `scripts/check_project_dependency_ordering.py`
- `groundtruth-kb/tests/test_project_dependency_ordering.py`
- `platform_tests/scripts/test_projects_cli.py`
- `.claude/skills/projects/SKILL.md`
- `.codex/skills/projects/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `.agent/skills/projects/SKILL.md`
- `.agent/skills/MANIFEST.json`
- `.cursor/skills/projects/SKILL.md`
- `.api-harness/skills/projects/SKILL.md`
- `.api-harness/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`

No other dirty path is claimed by this implementation.

## Exact Target Hashes

- `groundtruth-kb/src/groundtruth_kb/db.py`: `4e50655df2181757ce5943cfef97db77c9d32484f050435c3eafb26d55bea20d`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`: `025984e09244f1cbd5d09df3e756dff3ff66e65cf49e4abb521f6f126703cdbe`
- `groundtruth-kb/src/groundtruth_kb/cli.py`: `124d22045c19df2a11a85c145527d328a62902b3f2f62328d640fb737c39e6e6`
- `scripts/check_project_dependency_ordering.py`: `6073d74bce84935ad0bf86ca2a4295b9104157e66b8a36947ee5b75178303534`
- `groundtruth-kb/tests/test_project_dependency_ordering.py`: `26be5feefb3bd86868dd1b32f0c894a5ce95a885b2c52909e72381ae969c7ec5`
- `platform_tests/scripts/test_projects_cli.py`: `6f0ec42bb9476712276e07fc1aceba24a3b26190bc57a5e28bc5e2c339755912`
- `.claude/skills/projects/SKILL.md`: `6743363d96c27af81dc5af680f301e33803ff72b66e736efa083747fd36ba171`
- `.codex/skills/projects/SKILL.md`: `3b717e5e541fb6874f5130c89776399e7f8eebbbd602613bc1062ce14490e1d2`
- `.codex/skills/MANIFEST.json`: `eed3618e4fdf3f0aa9cad24cf0198c67b311e6c5724244a8d61ddf4974860491`
- `.agent/skills/projects/SKILL.md`: `805e6a42532b3b01294997f0de500020745258752e2f0a4ef8a06a7aa817c190`
- `.agent/skills/MANIFEST.json`: `d3932d5bc882c939fc1e540763ab5d27810ca82403051a103f8f20d591d05feb`
- `.cursor/skills/projects/SKILL.md`: `3b717e5e541fb6874f5130c89776399e7f8eebbbd602613bc1062ce14490e1d2`
- `.api-harness/skills/projects/SKILL.md`: `4fd1e5d60180740844def341ede9960f1711e5c667af97740e84ab8c5513555c`
- `.api-harness/skills/MANIFEST.json`: `fb25c0212ccc9d25e21fffd32be0e0edd7b80daf8fb17959811bff7207d12a26`
- `config/agent-control/harness-capability-registry.toml`: `ec4193603e28cdbfd201e2a6c1b0be2d72d1060a0baf5d05d0cec1b16ae0263d`

## Acceptance Criteria Status

- PASS: canonical dependency direction and complete append-only lifecycle are
  exposed through the governed `gt projects dependencies` CLI.
- PASS: invalid edges, cycles, duplicates, lifecycle transitions, and
  transaction failures append no affected version.
- PASS: project membership reorder is exact-set, version-revalidated, and
  all-or-nothing.
- PASS: readiness is complete and blocks only the declared gate without
  granting implementation authority.
- PASS: the isolated six-wave evaluator reports exactly five current outer
  assertions, all PASS.
- PASS: all canonical and generated project skill surfaces are current.
- PASS: focused nonimpairment and static-quality verification passed.
- PASS: no live project dependency, dispatcher, credential, release, or Git
  lifecycle mutation occurred.

## Risk And Rollback

The production graph remains intentionally fail-closed until canonical
`WI-5482` retires its one stale edge after this thread is VERIFIED. This is a
detected pre-existing state, not an implementation-created edge.

Rollback requires separately authorized, focused Git work reverting only the
fifteen declared targets, followed by the same dependency, lifecycle,
evaluator, projection, and static-quality checks. Numbered bridge artifacts,
MemBase history, and Deliberation Archive records remain append-only.

## Loyal Opposition Asks

1. Verify the fifteen exact targets against the approved proposal and linked
   specifications.
2. Confirm the 92 focused tests, five evaluator assertions, projection checks,
   and static-quality results.
3. Return VERIFIED if the implementation and report satisfy version 004 and
   GO version 005; otherwise return NO-GO with concrete findings.
