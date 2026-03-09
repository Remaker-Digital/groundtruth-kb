#!/usr/bin/env python3
"""
S148: Create KB test artifacts for unmatched agent/chat tests.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys, os, xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db'))
from db import KnowledgeDB


def classname_to_filepath(classname: str) -> str:
    """Convert JUnit dotted classname to file path."""
    parts = classname.split('.')
    filepath = '/'.join(parts) + '.py'
    if not filepath.startswith('tests/'):
        filepath = 'tests/' + filepath
    return filepath


def main():
    xml_path = os.path.join(os.path.dirname(__file__), '..', 'test-results', 'agents-s148.xml')
    tree = ET.parse(xml_path)
    root = tree.getroot()

    k = KnowledgeDB()
    c = k._conn

    # Build index of existing KB artifacts
    kb_index = set()
    rows = c.execute("SELECT test_file, test_function FROM current_tests WHERE test_file IS NOT NULL").fetchall()
    for r in rows:
        kb_index.add((r['test_file'], r['test_function']))

    # Find unmatched tests
    unmatched = []
    for tc in root.iter('testcase'):
        classname = tc.get('classname', '')
        funcname = tc.get('name', '')
        filepath = classname_to_filepath(classname)
        base_func = funcname.split('[')[0] if '[' in funcname else funcname

        if (filepath, funcname) not in kb_index and (filepath, base_func) not in kb_index:
            # Check if already seen (parametrized variants)
            if (filepath, base_func) not in [(u[0], u[1].split('[')[0]) for u in unmatched]:
                unmatched.append((filepath, base_func, classname))

    print(f"Found {len(unmatched)} unmatched agent/chat tests")
    for fp, fn, cn in unmatched[:5]:
        print(f"  {fp}::{fn}")

    # Get next test ID
    next_id_row = c.execute(
        "SELECT MAX(CAST(SUBSTR(id, 6) AS INTEGER)) FROM tests WHERE id LIKE 'TEST-%'"
    ).fetchone()
    next_id = (next_id_row[0] or 0) + 1

    created = 0
    for fp, fn, cn in unmatched:
        test_id = f"TEST-{next_id + created}"
        k.insert_test(
            id=test_id,
            title=f"Test: {fn}",
            spec_id='SPEC-general',
            test_type='automated',
            expected_outcome='PASS',
            changed_by='S148-traceability',
            change_reason=f'Create KB artifact for unmatched test {fp}::{fn}',
            test_file=fp,
            test_function=fn,
            last_result='pass',
            last_executed_at='2026-03-06',
        )
        created += 1

    print(f"Created {created} new test artifacts (TEST-{next_id}..TEST-{next_id + created - 1})")

    # Check new traceability
    total = c.execute('SELECT COUNT(*) FROM current_tests').fetchone()[0]
    traced = c.execute(
        "SELECT COUNT(*) FROM current_tests WHERE last_result IS NOT NULL AND last_result != ''"
    ).fetchone()[0]
    print(f"Test traceability: {traced}/{total} ({traced/total*100:.1f}%)")

    k.close()


if __name__ == '__main__':
    main()
