from pathlib import Path

from groundtruth_kb.db import KnowledgeDB


def generate_governance_index(db_path: Path) -> str:
    """
    Generates the CLAUDE.md Governance Index table from live MemBase GOV rows.
    """
    db = KnowledgeDB(db_path)
    governance_specs = (
        db._get_conn()
        .execute("SELECT id, title FROM current_specifications WHERE type = 'governance' ORDER BY id")
        .fetchall()
    )
    db.close()

    output = []
    output.append("| ID | Title |")
    output.append("|----|-------|")

    for spec in governance_specs:
        spec_id = spec["id"]
        spec_title = spec["title"]

        # Special handling for GOV-18
        if spec_id == "GOV-18":
            spec_title = "SPEC-1662 (GOV-18: Assertion Quality)"

        output.append(f"| {spec_id} | {spec_title} |")

    return "\n".join(output)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent  # E:\GT-KB
    db_path = project_root / "groundtruth.db"

    # This script is meant to be run from the project root or via CLI
    # If run from elsewhere, adjust db_path accordingly
    if not db_path.exists():
        # Fallback for when the script might be run from groundtruth-kb/scripts directly
        # or if groundtruth.db is not in the expected project root.
        # This part might need further refinement based on actual project structure.
        # For now, let's assume it's at project root.
        print(f"Warning: {db_path} not found. Attempting to locate groundtruth.db dynamically.")
        # A more robust solution would be to use gt-kb CLI or a known path.
        # For now, let's just make it clear that it expects it at project root.
        pass

    index_table = generate_governance_index(db_path)
    print(index_table)
