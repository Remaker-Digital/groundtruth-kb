---
name: Pedagogical Comments Standard
description: Every artifact (code, scripts, configs touched in active work) must be commented thoroughly enough that a student can use it as a reference. Module docstrings + section/why comments + rationale links to directives.
type: feedback
originSessionId: 2c8e1d6f-cf03-4ec2-a4a8-6d3ff5a453da
---
Every artifact should be commented thoroughly enough that a student may use it as a reference.

**Why:** Owner directive S307 (2026-04-24). GT-KB's purpose is being a teachable, adopter-friendly Internal Developer Platform; opaque code defeats that. Adopters and future maintainers (including Claude/Codex in later sessions) read these files cold — comments must explain *why*, not just *what*.

**How to apply:**
- Every modified file gets a teaching-grade module/file header docstring or comment block explaining purpose, callers, invariants.
- For non-obvious patterns (especially refactors), add a brief comment naming the rationale or directive driving the choice. Example: when replacing a hardcoded path with `Path(__file__).resolve()`, add `# Per S307 hardcoded-path directive: derive from script location, not env-coupled literal`.
- The most-reviewed artifacts (migration tools, hooks, skill SKILL.md files) should read like tutorials, not like terse production code.
- This *expands* the project's prior "default to writing no comments" guidance: that guidance applied to obvious internal logic; this directive applies to artifacts that adopters or students will read as reference.
- Skill markdown is already pedagogical by genre — keep it that way and ensure new examples include 1-2 sentences explaining why the pattern works for adopter / pip-install scenarios.
- Do NOT add comments to historical / archive artifacts that are frozen as evidence; those preserve their original style.
