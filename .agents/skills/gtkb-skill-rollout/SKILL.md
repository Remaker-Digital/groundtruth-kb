---
name: gtkb-skill-rollout
description: Add, rename or retire neutral GT-KB skills and qualify their deterministic projections.
---

# Skill rollout

The authored source is .harness-baseline-configuration/skills/<name>/SKILL.md
with its helpers and references. The name is a lowercase slug matching the
directory; YAML frontmatter contains a nonempty name and description.
Keep instructions neutral, use declared harness tokens for local paths, and
retain links to current formal sources. A harness loads its own projection.

For an addition, author the complete source and tests for its actual behavior.
For a rename, change the source directory and name together and correct every
active caller, link, template and test. For removal, remove its live consumers
or move surviving behavior to the appropriate current skill first.

Validate source and all affected target derivations:

    python scripts/harness_projection/project_harness.py --harness <name> --validate
    python scripts/check_harness_parity.py --all --validate

Read current help before supplying optional arguments. Exercise the skill's real
CLI/helper behavior, refusals and fresh-context use; projection bytes alone do
not establish host loading.

The baseline and projector are the committed work product. Mechanical
projection is an operational refresh using the selected target:

    python scripts/harness_projection/project_harness.py --harness <name>
    python scripts/harness_projection/project_harness.py --harness <name> --check

The projector manages its recorded output paths. Preserve unlisted local work;
do not manually delete a directory because its name looks stale. Use the current
project/work-item and Bridge lifecycle, including independent review. No rename
map, peer configuration, permission packet or generated manifest is authority.
