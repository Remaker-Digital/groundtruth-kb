"""Register Azure Readiness Taxonomy entries in the local MemBase (KB).

This script is idempotent: if an entry already exists it reports and
skips; otherwise it inserts via the `groundtruth_kb.db.KnowledgeDB` API.

Entries registered:

1. ``ADR-AZURE-READINESS-TEMPLATE`` — spec of type
   ``architecture_decision`` naming the reusable ADR template shape
   for per-category Azure readiness decisions.
2. ``SPEC-AZURE-READINESS-VERIFICATION-PLAN`` — spec of type
   ``requirement`` naming the offline/live verification plan shape.
3. ``DOC-AZURE-READINESS-TAXONOMY`` — document entry pointing at
   ``docs/reference/azure-readiness-taxonomy.md``.

Authorized by bridge ``gtkb-azure-enterprise-readiness-taxonomy`` GO.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure we can import the local package without `pip install -e .` in
# environments where the script is run standalone.
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

ADR_ID = "ADR-AZURE-READINESS-TEMPLATE"
SPEC_ID = "SPEC-AZURE-READINESS-VERIFICATION-PLAN"
DOC_ID = "DOC-AZURE-READINESS-TAXONOMY"

ADR_TITLE = "Azure Readiness Decision Template"
ADR_DESCRIPTION = (
    "Reusable template shape for per-category Azure readiness decisions. "
    "This is a TEMPLATE, not an instance decision. Per-category instance "
    "ADRs are created by downstream child bridges "
    "(gtkb-azure-adr-template-activation et al.) and reference this "
    "template in their content. Template fields: decision name, category, "
    "tier, context, considered options, decision, consequences, failed "
    "approaches, rejected alternatives, review triggers. Registered under "
    "the existing architecture_decision spec type (no new type introduced). "
    "Full template specification lives in "
    "docs/reference/azure-readiness-taxonomy.md Section 5."
)

SPEC_TITLE = "Azure Enterprise Readiness Verification Plan"
SPEC_DESCRIPTION = (
    "Shape of `gt project doctor --readiness azure-enterprise "
    "[--offline|--live]`. Offline mode (default): checks spec presence, "
    "ADR presence, CI workflow file presence, grep/glob assertions, and "
    "file-pattern presence across the 13 readiness categories. Live mode "
    "(explicit `--live` opt-in): additionally queries Azure ARM / Entra / "
    "Key Vault APIs to verify declared readiness posture against deployed "
    "state (e.g., managed identity presence on Container Apps, "
    "no-static-secret on federated credentials, backup/PITR enabled on "
    "data stores). Full verification plan lives in "
    "docs/reference/azure-readiness-taxonomy.md Section 6."
)

DOC_TITLE = "Azure Readiness Taxonomy"
DOC_SOURCE_PATH = "docs/reference/azure-readiness-taxonomy.md"
DOC_CATEGORY = "taxonomy"

CHANGED_BY = "register_azure_taxonomy_kb.py"
CHANGE_REASON = (
    "Register Azure Readiness Taxonomy entries authorized by bridge gtkb-azure-enterprise-readiness-taxonomy GO."
)


def _adr_content() -> str:
    return (
        "# Azure Readiness Decision Template\n\n"
        "This is a **template**, not an instance decision. Per-category\n"
        "instance ADRs created by downstream child bridges copy this shape.\n\n"
        "## Fields\n\n"
        "| Field | Required | Description |\n"
        "|-------|----------|-------------|\n"
        "| Decision name | yes | The concrete decision, scoped to one category. |\n"
        "| Category | yes | One of the 13 categories from the taxonomy. |\n"
        "| Tier | yes | Lowest tier that requires this decision. |\n"
        "| Context | yes | Why this decision is needed now. |\n"
        "| Considered options | yes | At least two options with pros/cons. |\n"
        "| Decision | yes | The chosen option, in imperative form. |\n"
        "| Consequences | yes | Follow-on work and obligations. |\n"
        "| Failed approaches | yes | Approaches tried that did not work. |\n"
        "| Rejected alternatives | yes | Options considered and declined. |\n"
        "| Review triggers | yes | Events that should reopen this decision. |\n\n"
        "See docs/reference/azure-readiness-taxonomy.md Section 5 for the\n"
        "canonical definition.\n"
    )


def _spec_content() -> str:
    return (
        "# Azure Enterprise Readiness Verification Plan\n\n"
        "See docs/reference/azure-readiness-taxonomy.md Section 6 for the\n"
        "canonical definition.\n\n"
        "## Offline mode\n\n"
        "`gt project doctor --readiness azure-enterprise` (offline is\n"
        "implied when `--live` is absent). Checks spec presence, ADR\n"
        "presence, CI workflow file presence, grep/glob assertions, and\n"
        "file-pattern presence across all 13 categories.\n\n"
        "## Live mode\n\n"
        "`gt project doctor --readiness azure-enterprise --live`. Requires\n"
        "explicit opt-in. Queries ARM, Entra, and Key Vault APIs to verify\n"
        "deployed state matches declared readiness.\n"
    )


def _print_section(title: str) -> None:
    print()
    print(f"--- {title} ---")


def register() -> int:
    db_path = REPO_ROOT / "groundtruth.db"
    if not db_path.exists():
        print(f"NOTE: {db_path} does not exist yet; schema will be created on connect.")
    db = KnowledgeDB(db_path=db_path)

    exit_code = 0

    # 1. ADR template spec
    _print_section(f"1. {ADR_ID}")
    existing = db.get_spec(ADR_ID)
    if existing is not None:
        print(f"  EXISTS  id={existing['id']} version={existing['version']} status={existing['status']}")
        print(f"          title={existing['title']!r}")
    else:
        result = db.insert_spec(
            id=ADR_ID,
            title=ADR_TITLE,
            description=ADR_DESCRIPTION,
            status="implemented",
            type="architecture_decision",
            priority="P1",
            tags=["azure", "readiness", "template", "taxonomy"],
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
            source_paths=["docs/reference/azure-readiness-taxonomy.md"],
            # content is not a first-class column on specifications; embed
            # the template shape in description above and in the linked
            # taxonomy doc. ADR content remains in the taxonomy file.
        )
        if result is None:
            print(f"  FAILED to insert {ADR_ID}")
            exit_code = 1
        else:
            print(f"  INSERTED id={result['id']} version={result['version']} status={result['status']}")

    # 2. Verification plan spec
    _print_section(f"2. {SPEC_ID}")
    existing = db.get_spec(SPEC_ID)
    if existing is not None:
        print(f"  EXISTS  id={existing['id']} version={existing['version']} status={existing['status']}")
        print(f"          title={existing['title']!r}")
    else:
        result = db.insert_spec(
            id=SPEC_ID,
            title=SPEC_TITLE,
            description=SPEC_DESCRIPTION,
            status="specified",
            type="requirement",
            priority="P1",
            tags=["azure", "readiness", "verification", "doctor", "taxonomy"],
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
            source_paths=["docs/reference/azure-readiness-taxonomy.md"],
        )
        if result is None:
            print(f"  FAILED to insert {SPEC_ID}")
            exit_code = 1
        else:
            print(f"  INSERTED id={result['id']} version={result['version']} status={result['status']}")

    # 3. Taxonomy document entry
    _print_section(f"3. {DOC_ID}")
    existing_doc = db.get_document(DOC_ID)
    if existing_doc is not None:
        print(f"  EXISTS  id={existing_doc['id']} version={existing_doc['version']} status={existing_doc['status']}")
        print(f"          title={existing_doc['title']!r} category={existing_doc['category']!r}")
        print(f"          source_path={existing_doc['source_path']!r}")
    else:
        result_doc = db.insert_document(
            id=DOC_ID,
            title=DOC_TITLE,
            category=DOC_CATEGORY,
            status="published",
            tags=["azure", "readiness", "taxonomy", "reference"],
            source_path=DOC_SOURCE_PATH,
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
        )
        if result_doc is None:
            print(f"  FAILED to insert {DOC_ID}")
            exit_code = 1
        else:
            print(f"  INSERTED id={result_doc['id']} version={result_doc['version']} status={result_doc['status']}")

    _print_section("Summary")
    adr = db.get_spec(ADR_ID)
    spec = db.get_spec(SPEC_ID)
    doc = db.get_document(DOC_ID)
    print(f"  {ADR_ID}: {'present' if adr else 'MISSING'}")
    print(f"  {SPEC_ID}: {'present' if spec else 'MISSING'}")
    print(f"  {DOC_ID}: {'present' if doc else 'MISSING'}")

    if adr is None or spec is None or doc is None:
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(register())
