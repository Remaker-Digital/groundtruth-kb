GO

# GENERATOR-HARDENING-CROSS-REPO - Codex Scoping Review

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-cross-repo-001.md`

## Claim

GO for the three-layer cross-repo subprocess remediation scope.

The proposal addresses the architectural defect Codex identified in GH-002:
generator-only allowlisting is insufficient because the audit-hook runner has
its own independent path policy. This scope correctly changes the generator,
lane, and runner so they share the same resolved allowlist contract.

## Evidence

The proposal covers all required enforcement points:

- Generator: `_git_checkout_info(...)` degrades when the checkout path is
  outside `--project-root` and outside `--allowed-cross-repo-roots`.
- Lane: `_build_generator_argv(...)` and `_build_subprocess_command(...)` pass
  the same cross-repo roots to the generator and runner.
- Runner: `_build_allowed_path_rules(...)`, `build_is_allowed(...)`, and
  `build_audit_hook(...)` accept additional allowed prefixes.

That is the missing co-design layer from the earlier GH-002 NO-GO.

## GO Conditions

Implementation should preserve these constraints:

1. The allowlist must use resolved exact repository roots, not broad parent
   directories such as `E:/Claude-Playground/CLAUDE-PROJECTS`.
2. The lane output should record the resolved cross-repo allowlist in
   `dashboard-regen-plan.json` or the audit-hook proof block so the zero
   violation result is auditable.
3. Add one negative runner/lane test proving a cross-repo subprocess outside
   the allowlist still produces a violation or degraded record.
4. Keep default behavior strict: no allowlist means the generator degrades
   cross-repo upgrade posture rather than running a cross-repo git subprocess.
5. The `.claude/settings.json` adopter update remains a separate follow-up,
   not part of this implementation bridge.

## Decision Needed From Owner

None for scoping. The lane discovery heuristic can proceed as proposed, with
the resolved path captured in output evidence so reviewers can verify exactly
what was allowed.

