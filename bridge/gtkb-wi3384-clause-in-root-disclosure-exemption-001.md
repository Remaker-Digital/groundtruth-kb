NEW

bridge_kind: implementation_proposal
Document: gtkb-wi3384-clause-in-root-disclosure-exemption
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3384
target_paths: ["scripts/adr_dcl_clause_preflight.py", "config/governance/adr-dcl-clauses.toml", "platform_tests/scripts/test_clause_in_root_disclosure_exempt.py"]
implementation_scope: source, config, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-3384: CLAUSE-IN-ROOT detector — exempt marked disclosure mentions while always scanning the target-path declaration

## Summary

WI-3384 (P3, `governance`, origin=defect): the `adr_dcl_clause_preflight` CLAUSE-IN-ROOT failure detector (the `failure_pattern` regex registered for `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` at `config/governance/adr-dcl-clauses.toml` line ~55) matches an out-of-root user-profile / temp directory path token **anywhere** in a bridge proposal's content and refutes the in-root evidence — even when the path is mentioned only in an explicit disclosure that it is NOT a GT-KB artifact (for example, documenting an out-of-root location for context while drawing the in-root boundary). A fully in-root-compliant proposal that needs to discuss such a path for disclosure is forced to omit the literal path. Originally observed 2026-05-19 on a prior proposal; **reproduced firsthand this session on the WI-4530 install-shim proposal**, where every out-of-root path literal had to be stripped from the body even though the proposal declared only in-root `target_paths` and performed no out-of-root placement.

**Cycle-17 triage (this session) confirms WI-3384 is genuinely OPEN.** Live read: `scripts/adr_dcl_clause_preflight.py` `evaluate_evidence` (lines ~182-191) applies `clause.failure_pattern` to the ENTIRE proposal `content` (`re.search(clause.failure_pattern, content)`); on a match the evidence is "treated as inverted/refuted." The `failure_pattern` mechanism is generic (other clauses reuse it for whole-content checks where that is correct), so the fix must be CLAUSE-IN-ROOT-specific and opt-in.

**Owner cycle-17 AskUserQuestion decision: "Seed WI-3384 (safe-hybrid design)."** This proposal implements the lowest-false-negative-risk fix: **always scan the `target_paths` declaration** (so a proposal that genuinely DECLARES an out-of-root target path is still refuted — no governance weakening), while **exempting path mentions inside an explicit author-marked disclosure block**. Unmarked prose mentions still refute (conservative by default). The change is gated behind a new per-clause config flag so only CLAUSE-IN-ROOT opts in; every other clause's `failure_pattern` behavior is unchanged.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-3384 is the backlog authority for this fix (P3 governance-detector false-positive defect). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one source file + one config clause + one test), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (owner AUQ 2026-06-14, DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION; includes WI-3384; allows `source`, `test_addition`, `hook_upgrade`, `config`). This fix uses `source` + `config` + `test` only.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** (the spec whose CLAUSE-IN-ROOT this detector enforces) — the fix PRESERVES the clause's intent: it still refutes proposals that DECLARE out-of-root artifact placement (the real violation), and only stops refuting on non-declaration disclosure mentions. The in-root invariant is strengthened in precision, not weakened.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the clause preflight is bridge-governance infrastructure; this fix improves its precision without altering `bridge/INDEX.md`, the GO/NO-GO discipline, or any other clause's behavior.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including an explicit no-false-negative regression (out-of-root target-path declaration still refutes).
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked precision fix to a governance detector with explicit test coverage.

(Self-referential note: this proposal deliberately contains NO literal out-of-root path string — it describes the offending paths and the `failure_pattern` regex abstractly — precisely because the unfixed detector would otherwise refute this very proposal. That is the WI-3384 false-positive in miniature.)

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-3384 + the firsthand WI-4530 reproduction this session), cycle-17 triage confirmed the detector applies `failure_pattern` to whole content, the bounded PAUTH authorizes the `source` + `config` + `test` work, and ADR-ISOLATION-APPLICATION-PLACEMENT-001 defines the in-root invariant the fix preserves. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14, cycle 14) authorizing WI-3384 (and siblings 3439/3448/4396) under the bounded PAUTH.
- **Cycle-17 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Seed WI-3384 (safe-hybrid design)" over the declaration-scoping design and the stay-wrapped option, authorizing the always-scan-target_paths + marked-disclosure-exemption design.
- **WI-4530 (this session's install-shim seed; GO'd)** — the firsthand reproduction: the proposal had to strip every out-of-root path literal because the detector refuted mentions; this WI removes that friction for honest disclosure while preserving declaration enforcement.
- **The existing `failure_pattern` mechanism in `adr_dcl_clause_preflight.py`** — applied whole-content by design for clauses where that is correct (e.g. the spec-links-placeholder clause). This fix adds an OPT-IN per-clause flag so only CLAUSE-IN-ROOT changes; the generic mechanism is untouched for all other clauses.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live detector source + config instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14) authorizing WI-3384 under `PAUTH-…-COMPLIANCE-DISPATCH-BATCH-001` (allowed: `source`, `test_addition`, `hook_upgrade`, `config`; forbids narrative_artifact + formal-artifact mutation).
- **Cycle-17 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Seed WI-3384 (safe-hybrid design)"**, authorizing the always-scan-target_paths + marked-disclosure-exemption scope (NOT a rules-file edit; the disclosure-marker convention is documented in the config comment + the preflight docstring, both in-scope, since `.claude/rules/file-bridge-protocol.md` is a narrative artifact the PAUTH forbids). A follow-on slice may add the convention to file-bridge-protocol.md under a narrative-artifact authorization.

## Design

1. **Config (`config/governance/adr-dcl-clauses.toml`):** add a new opt-in boolean field to the CLAUSE-IN-ROOT clause entry, e.g. `failure_pattern_disclosure_exempt = true`, plus a comment documenting the disclosure-marker convention (the marker is the in-scope home for the convention text, since the rules file is out-of-PAUTH-scope). Default for all other clauses is the existing whole-content behavior (flag absent / false).
2. **Clause loader (`scripts/adr_dcl_clause_preflight.py`):** add the `failure_pattern_disclosure_exempt: bool = False` field to the `Clause` dataclass and load it in `load_clauses`.
3. **`evaluate_evidence` scoping:** when `clause.failure_pattern_disclosure_exempt` is True, build the scanned text as the union of:
   - the proposal content with explicitly-marked disclosure spans REMOVED. The marker is a paired HTML-comment block, e.g. `<!-- in-root-disclosure -->` … `<!-- /in-root-disclosure -->`; only content between a matched open/close pair is stripped. (HTML comments are inert in the rendered proposal and are an established convention in `bridge/INDEX.md`.)
   - **PLUS the raw `target_paths` declaration line(s)** re-extracted from the original content (via the existing `target_paths:` line pattern). This is appended UNCONDITIONALLY, so an out-of-root path inside `target_paths` is scanned **even if the author wrapped it in a disclosure marker** — closing the evasion path and guaranteeing no false-negative on the primary declaration surface.
   Apply the `failure_pattern` to that scanned text. When the flag is False (every other clause), apply to full content exactly as today.
4. **No signature change is required** — `evaluate_evidence` re-extracts the `target_paths` line from `content`; `paths` need not be threaded through. No change to applicability, owner-waiver, or any other clause's evidence logic.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_clause_in_root_disclosure_exempt.py`) | Method |
|---|---|---|
| Disclosure-marked out-of-root mention does NOT refute CLAUSE-IN-ROOT (WI-3384 root / WI-4530 repro) | `test_marked_disclosure_mention_not_refuted` | content with an out-of-root path ONLY inside `<!-- in-root-disclosure -->…<!-- /in-root-disclosure -->` + in-root `target_paths` → evidence NOT refuted |
| **No false-negative: out-of-root path in `target_paths` STILL refutes, even inside a disclosure marker** | `test_out_of_root_target_paths_still_refutes` | `target_paths` declaring an out-of-root path (and the same wrapped in a disclosure marker) → evidence REFUTED both ways |
| Unmarked prose mention still refutes (conservative default) | `test_unmarked_mention_still_refutes` | out-of-root path in prose with NO disclosure marker → evidence REFUTED |
| Other clauses are unaffected (flag absent → whole-content scan) | `test_other_clauses_unchanged` | a clause without the flag whose `failure_pattern` matches content → refuted as today |
| agent-red-rehearsal exception preserved | `test_rehearsal_exception_preserved` | the rehearsal-sandbox path token (the existing negative-lookahead exception in the regex) → not refuted, regardless of marker |
| Loader parses the new flag; default False | `test_flag_default_false` | a clause entry without the flag loads with `failure_pattern_disclosure_exempt == False` |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on the changed Python; `python -m pytest platform_tests/scripts/test_clause_in_root_disclosure_exempt.py -q --tb=short`; plus the existing clause-preflight regression suite must still pass (other clauses' refutation behavior unchanged). Note: this repo's venv currently needs `-o addopts=""` to run pytest (the project `addopts` requires `pytest-timeout`, absent in the venv — a separate env defect).

## Risk / Rollback

- **Risk: low, and false-negative-safe by construction.** The change is opt-in (one config flag, CLAUSE-IN-ROOT only) and ADDITIVELY NARROWS the refutation: it removes refutations only for explicitly-marked disclosure mentions, while the primary violation surface (the `target_paths` declaration) is ALWAYS scanned — so a proposal that genuinely declares out-of-root placement is still caught. Unmarked mentions still refute (no silent loosening). Every other clause's `failure_pattern` behavior is byte-for-byte unchanged.
- **Residual:** a non-`target_paths` out-of-root OUTPUT declaration written in prose AND wrapped in a disclosure marker could evade; this requires the author to deliberately misrepresent a declaration as disclosure, which LO review catches. The honest-disclosure case (the WI's subject) is fully served. A follow-on may extend always-scan to additional structured output-declaration fields if any are introduced.
- **Rollback:** remove the config flag + the loader field + the `evaluate_evidence` branch + the test. The detector reverts to whole-content scanning. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (a governance-detector false-positive that refutes valid in-root proposals on non-declaration disclosure mentions), restoring detector precision without weakening enforcement. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
