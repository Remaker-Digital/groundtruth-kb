# Platform tests package marker.
#
# Restored after GTKB-ISOLATION-018 18.E.1 moved the original tests/__init__.py
# to applications/Agent_Red/tests/__init__.py. The platform tests under
# tests/scripts/, tests/hooks/, tests/skills/, etc. import from project-root
# modules (e.g., `from scripts.foo import bar`), which requires `tests/` to
# be a Python package so pytest's parent-traversal stops at project root
# rather than putting `tests/` on sys.path (which makes `tests/scripts/` shadow
# the root `scripts/` package).
#
# Owner-approved scope expansion via AskUserQuestion 2026-05-11; documented in
# bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
