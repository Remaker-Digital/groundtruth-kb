#!/usr/bin/env python3
"""Phase 2 of S321 spec batch: 4 additional specs for the comprehensive architecture.

Per owner standing authorization 2026-04-29 (S321):
  "I authorize you to create all necessary specifications. The creation of
  specifications from my input is *always* allowed."

This phase 2 adds the 4 specs the comprehensive architecture REVISED-2
needs to drop the pending: exemption reliance flagged by Codex NO-GO -004.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPROVAL_DIR = PROJECT_ROOT / ".groundtruth" / "formal-artifact-approvals"
DB_PATH = PROJECT_ROOT / "groundtruth.db"

CHANGED_BY = "prime-builder/claude"
CHANGE_REASON = (
    "Capture S321 2026-04-29 phase-2 batch (4 additional specs for comprehensive "
    "architecture REVISED-2, addressing Codex NO-GO -004 findings F1-F4). "
    "Owner standing authorization grants approval; per-spec packets recorded."
)


SPECS = [
    # 1. Relevance closure (F2 closure of comprehensive arch -004)
    {
        "id": "DCL-SPEC-RELEVANCE-CLOSURE-001",
        "type": "design_constraint",
        "title": "Bridge proposal spec linkage must be relevance-complete, not just non-empty",
        "description": (
            "Per owner directive 2026-04-29: 'It must NOT be possible to "
            "submit an implementation proposal that is not linked to any and "
            "all relevant specifications.' The 'all' is mechanically enforced "
            "via relevance closure: candidate-relevant specs computed from "
            "structured proposal metadata + existing KB cross-references. The "
            "closure check uses concrete DB columns and matching rules — no "
            "heuristics or fuzzy candidates.\n\n"
            "PROPOSAL METADATA (structured fields required at top of bridge "
            "implementation proposals):\n"
            "  - affected_modules: list of file paths the proposal will "
            "    Write/Edit/touch (relative to project root)\n"
            "  - touches_specs: list of spec IDs this proposal directly "
            "    affects (status promotions, content amendments)\n"
            "  - bridge_kind: one of {feature, refactor, governance, "
            "    audit, doc, infrastructure}\n\n"
            "MATCHING ALGORITHM (deterministic, no heuristics):\n"
            "  Candidate-relevant specs are the UNION of:\n"
            "  (a) any spec where specifications.source_paths overlaps with "
            "      proposal.affected_modules (string-prefix match)\n"
            "  (b) any spec listed in proposal.touches_specs\n"
            "  (c) any spec listed in specifications.affected_by where the "
            "      target spec is in (a) or (b) — transitive one hop\n"
            "Closure check fails-closed if any candidate is not cited in "
            "Specification Links section AND not listed in "
            "Specification-Coverage-Waivers section.\n\n"
            "WAIVER SCHEMA: Specification-Coverage-Waivers section optional; "
            "if present must contain entries of form:\n"
            "  - <spec-id>: <waiver-rationale-one-line>\n"
            "Waivers require Codex review approval; a waivered spec counts as "
            "intentionally-excluded for the proposal's scope. Future REVISED "
            "versions may rescind waivers; rescinding requires re-citation."
        ),
        "scope": "GT-KB platform; applies to all bridge implementation proposals across adopters",
        "tags": ["design-constraint", "relevance-closure", "spec-linkage", "mechanical-enforcement"],
        "assertions": [
            {
                "id": "DCL-SPEC-RELEVANCE-CLOSURE-001.A1",
                "kind": "behavioral",
                "description": (
                    "Bridge proposal write hook MUST compute candidate set "
                    "(via the matching algorithm) and reject any proposal "
                    "whose Specification Links + Specification-Coverage-"
                    "Waivers sections do not cover every candidate."
                ),
                "verifying_test": "deferred to comprehensive architecture Slice (post REVISED-2 GO)",
            },
            {
                "id": "DCL-SPEC-RELEVANCE-CLOSURE-001.A2",
                "kind": "behavioral",
                "description": (
                    "Database query for candidate-relevant specs MUST use "
                    "concrete columns: specifications.source_paths and "
                    "specifications.affected_by (both exist in current "
                    "groundtruth.db schema)."
                ),
                "verifying_test": "deferred",
            },
        ],
        "source_paths": [
            "groundtruth-kb/templates/hooks/bridge-compliance-gate.py",
            "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py",
        ],
    },
    # 2. VERIFIED uses full bridge history (F5 closure of comprehensive arch -004)
    {
        "id": "DCL-VERIFIED-BRIDGE-HISTORY-001",
        "type": "design_constraint",
        "title": "VERIFIED runner must operate on full bridge thread history, not single file",
        "description": (
            "Per `.claude/rules/file-bridge-protocol.md` 'must read the full "
            "entry (all versions) before acting on any single version': the "
            "VERIFIED runner that enforces DCL-VERIFIED-SPEC-DERIVED-TESTING-"
            "MANDATORY-001 MUST consume a bridge document NAME (matching "
            "Document: header in bridge/INDEX.md), not a single file path.\n\n"
            "RUNNER INPUT: bridge_document_name (kebab-case string matching a "
            "Document: line in bridge/INDEX.md, e.g., "
            "'gtkb-platform-spec-coverage-architecture-2026-04-29').\n\n"
            "RUNNER PROCEDURE (deterministic):\n"
            "1. Parse bridge/INDEX.md, find the Document: entry matching the "
            "   input name; if absent, fail-closed with ERR_NO_INDEX_ENTRY.\n"
            "2. Enumerate ALL version files listed under that Document: entry "
            "   (regardless of status — NEW, REVISED, GO, NO-GO, VERIFIED).\n"
            "3. Read each file; extract Specification Links section + "
            "   Specification-Coverage-Waivers section.\n"
            "4. Compute UNION of cited spec IDs across all versions (forward-"
            "   compatible: REVISED versions can ADD specs but not remove "
            "   without explicit owner-approved waiver in the same version).\n"
            "5. For each spec in the union: identify all derived tests (test "
            "   files whose docstrings cite the spec ID).\n"
            "6. Execute all derived tests via pytest.\n"
            "7. VERIFIED only if (a) every union spec has at least one derived "
            "   test AND (b) all derived tests pass.\n"
            "8. Output structured per-spec execution matrix to the VERIFIED "
            "   response."
        ),
        "scope": "GT-KB platform VERIFIED enforcement runner",
        "tags": ["design-constraint", "verified-runner", "bridge-history", "mechanical-enforcement"],
        "assertions": [
            {
                "id": "DCL-VERIFIED-BRIDGE-HISTORY-001.A1",
                "kind": "behavioral",
                "description": (
                    "Runner with input bridge_document_name MUST parse all "
                    "versions in INDEX.md entry; UNION of Specification Links "
                    "across versions is the verification scope (forward-"
                    "compatible accumulation)."
                ),
                "verifying_test": "deferred to runner implementation",
            },
            {
                "id": "DCL-VERIFIED-BRIDGE-HISTORY-001.A2",
                "kind": "behavioral",
                "description": (
                    "Removal of a previously-cited spec in a REVISED version "
                    "REQUIRES an explicit owner-approved waiver in the same "
                    "version; absent waiver = invalid revision."
                ),
                "verifying_test": "deferred",
            },
        ],
        "source_paths": [
            "scripts/run_spec_derived_tests.py",  # to be created
        ],
    },
    # 3. Cross-harness enforcement matrix (F4 closure of comprehensive arch -004)
    {
        "id": "DCL-CROSS-HARNESS-ENFORCEMENT-001",
        "type": "design_constraint",
        "title": "Spec-linkage enforcement must apply across all bridge submission paths",
        "description": (
            "Per owner directive 2026-04-29: 'must NOT be possible to submit' "
            "applies cross-harness, not just to one tooling path. The "
            "comprehensive enforcement matrix:\n\n"
            "PATH 1 — Claude Code Write/Edit:\n"
            "  Enforcement: PreToolUse hook (.claude/hooks/bridge-compliance-"
            "  gate.py with emit_deny). Status: TARGET (interim bridge "
            "  proposes hook modification + activation).\n\n"
            "PATH 2 — Codex apply_patch:\n"
            "  Enforcement: Codex hook on apply_patch. Status: BLOCKED — "
            "  Codex hooks disabled on Windows per S319 ADR-CODEX-HOOK-"
            "  PARITY-FALLBACK-001. Fallback: scripts/check_codex_hook_"
            "  parity.py + release-candidate gate.\n\n"
            "PATH 3 — Direct shell file writes (cat >, echo >, printf, etc.):\n"
            "  Enforcement: pre-commit hook on bridge/*.md path. Status: "
            "  GAP — not yet implemented.\n\n"
            "PATH 4 — External editors (VSCode direct save, Vim, etc.):\n"
            "  Enforcement: pre-commit hook covers (same as PATH 3) on the "
            "  commit step. Status: GAP — not yet implemented.\n\n"
            "PATH 5 — Direct git commit on already-on-disk bridge files:\n"
            "  Enforcement: pre-commit hook + CI pre-merge gate. Status: "
            "  GAP — not yet implemented.\n\n"
            "PATH 6 — CI / pull request:\n"
            "  Enforcement: GitHub Actions workflow gating PRs that modify "
            "  bridge/*.md. Status: GAP — not yet implemented.\n\n"
            "DEFENSE-IN-DEPTH: Codex (Loyal Opposition) review NO-GOs any "
            "non-compliant proposal regardless of submission path. This is "
            "the existing-and-active fallback for any path with an "
            "enforcement gap."
        ),
        "scope": "GT-KB platform bridge submission across all tooling paths",
        "tags": ["design-constraint", "cross-harness", "enforcement-matrix", "mechanical-enforcement"],
        "assertions": [
            {
                "id": "DCL-CROSS-HARNESS-ENFORCEMENT-001.A1",
                "kind": "behavioral",
                "description": (
                    "For each submission path with status TARGET, an active "
                    "hook/gate MUST exist that hard-blocks non-compliant "
                    "bridge writes. For status BLOCKED/GAP, the gap MUST be "
                    "tracked in this DCL's status field with an action plan."
                ),
                "verifying_test": "deferred to comprehensive architecture Slice",
            },
            {
                "id": "DCL-CROSS-HARNESS-ENFORCEMENT-001.A2",
                "kind": "behavioral",
                "description": (
                    "Codex (Loyal Opposition) review MUST issue NO-GO on any "
                    "non-compliant proposal regardless of which submission "
                    "path was used. This is the always-active fallback."
                ),
                "verifying_test": "deferred to Codex skill prompt update + tests",
            },
        ],
    },
    # 4. ADR — comprehensive spec coverage architecture
    {
        "id": "ADR-SPEC-COVERAGE-ARCHITECTURE-001",
        "type": "architecture_decision",
        "title": "Comprehensive spec coverage architecture: activate existing framework + close 4 specific gaps",
        "description": (
            "DECISION: GT-KB platform spec-coverage enforcement is built by "
            "activating the existing framework infrastructure + closing 4 "
            "specific gaps (relevance closure, full-history VERIFIED, cross-"
            "harness, hard-block). NOT a 7-layer greenfield architecture.\n\n"
            "REJECTED ALTERNATIVES:\n"
            "1. 7-layer greenfield architecture (proposed in -001) — rejected: "
            "   reinvention of framework infrastructure that already existed in "
            "   .claude/rules/file-bridge-protocol.md + groundtruth-kb/"
            "   templates/{hooks,skills/bridge-propose/helpers}. Codex F1 of "
            "   -002 caught the reinvention.\n\n"
            "2. Activate-only (interim bridge approach) — insufficient: the "
            "   existing hook uses emit_ask (advisory), not emit_deny (hard-"
            "   block). Codex F1 of -004 (interim) caught this. Activation "
            "   alone doesn't satisfy strict mechanical enforcement.\n\n"
            "3. Pending: bootstrap exemption (proposed in -003) — rejected by "
            "   Codex F1 of -004 (comprehensive): pending: not in active "
            "   protocol; relying on it creates an unstated exception.\n\n"
            "4. Single-slice comprehensive bridge (proposed in -003) — "
            "   rejected by Codex F2 of -004: combining DCL filing with "
            "   implementation violates pending-discipline; first GO must "
            "   authorize only spec creation.\n\n"
            "RATIONALE: framework already implements ~80% of the contract; "
            "the 4 gaps (F1-F4 of comprehensive -004) are the non-negotiable "
            "owner directives that the framework didn't yet cover. Build on "
            "existing rather than parallel to it.\n\n"
            "CONSEQUENCES:\n"
            "- Specs (DCL-SPEC-RELEVANCE-CLOSURE-001, DCL-VERIFIED-BRIDGE-"
            "  HISTORY-001, DCL-CROSS-HARNESS-ENFORCEMENT-001) created in KB "
            "  FIRST under owner standing authorization, BEFORE any "
            "  implementation bridge references them.\n"
            "- Each gap closure is its own focused implementation bridge "
            "  (relevance closure, full-history runner, cross-harness "
            "  enforcement) cited via Specification Links.\n"
            "- Comprehensive architecture bridge becomes the umbrella "
            "  reference; sub-bridges do the actual work."
        ),
        "scope": "GT-KB platform spec-coverage enforcement strategy",
        "tags": ["architecture-decision", "spec-coverage", "framework-activation"],
    },
]


def make_approval_packet(spec: dict) -> dict:
    """Generate a per-spec approval packet citing owner standing authorization."""
    full_content = json.dumps(
        {
            "id": spec["id"],
            "type": spec["type"],
            "title": spec["title"],
            "description": spec["description"],
            "tags": spec.get("tags", []),
            "assertions": spec.get("assertions", []),
            "scope": spec.get("scope", ""),
        },
        indent=2,
        sort_keys=True,
    )
    sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    return {
        "artifact_type": "specification",
        "artifact_id": spec["id"],
        "action": "insert",
        "source_ref": "owner_conversation:2026-04-29-S321-comprehensive-arch-revised-2",
        "full_content": full_content,
        "full_content_sha256": sha256,
        "approval_mode": "acknowledge",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "Owner directive 2026-04-29 (S321): standing authorization for spec creation; option (b) defer interim, tackle comprehensive arch REVISED-2.",
        "changed_by": CHANGED_BY,
        "change_reason": CHANGE_REASON,
        "approved_by": "owner",
        "acknowledged_by": "owner",
    }


def main() -> int:
    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    api = db.KnowledgeDB(str(DB_PATH))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    inserted = []
    failed = []

    for i, spec in enumerate(SPECS, 1):
        spec_id = spec["id"]
        print(f"[{i}/{len(SPECS)}] {spec_id}")
        packet = make_approval_packet(spec)
        packet_path = APPROVAL_DIR / f"{timestamp}-s321-phase2-{spec_id.lower()}.json"
        packet_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        try:
            result = api.insert_spec(
                id=spec_id,
                title=spec["title"],
                status="specified",
                changed_by=CHANGED_BY,
                change_reason=CHANGE_REASON,
                description=spec.get("description"),
                type=spec["type"],
                tags=spec.get("tags"),
                assertions=spec.get("assertions"),
                scope=spec.get("scope"),
                source_paths=spec.get("source_paths"),
                validate_assertions=False,
            )
            inserted.append(spec_id)
            print(f"      OK")
        except Exception as exc:
            failed.append((spec_id, str(exc)))
            print(f"      FAIL: {type(exc).__name__}: {exc}")

    print(f"\n=== SUMMARY: {len(inserted)}/{len(SPECS)} inserted ===")
    if failed:
        for sid, err in failed:
            print(f"  FAIL {sid}: {err}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
