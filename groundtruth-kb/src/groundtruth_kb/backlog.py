"""Legacy backlog migration tooling — retired at Slice 7-prime.

The one-time migration of the legacy markdown backlog view into the canonical
MemBase ``work_items`` table is complete (see
``DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION``). The migration
command and its markdown parse/insert backend have been removed now that the
legacy markdown backlog view is retired.

The canonical backlog is read via ``gt backlog list`` / ``gt backlog status``
against MemBase ``work_items``. Legacy approval-state compatibility helpers
remain under ``groundtruth_kb.backlog`` for historical rows only.
"""

from __future__ import annotations
