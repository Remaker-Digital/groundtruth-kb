#!/usr/bin/env python3
"""Update GitHub wiki pages for Agent Red."""

import pathlib

WIKI = pathlib.Path("C:/Users/micha/AppData/Local/Temp/agent-red.wiki")

def write_wiki(name, content):
    path = WIKI / name
    path.write_text(content, encoding="utf-8", newline="
")
    print(f"  Written: {name} ({len(content)} bytes)")

def main():
    # Files will be written by calling write_project_status(), etc.
    write_project_status()
    write_test_coverage()
    write_testing_strategy()
    write_defect_log()
    write_changelog()
    print("All wiki pages updated.")

if __name__ == "__main__":
    main()
