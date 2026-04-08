#!/usr/bin/env python3
"""
Import cycle detector for CI.

Only detects cycles formed by MODULE-LEVEL imports. Function-scoped
(lazy) imports are excluded because Python handles them correctly
at runtime — they exist specifically to break circular dependencies.

Package __init__.py re-exports (e.g., superadmin_api/__init__.py
importing from superadmin_api._tenants) are also excluded since
submodules importing from their own package is standard Python.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

import ast
import os
import sys
from collections import defaultdict


def is_module_level_import(node: ast.AST, tree: ast.Module) -> bool:
    """Return True if the import is at module level (not inside a function/class method)."""
    # Module-level imports are direct children of the Module node
    for stmt in tree.body:
        if stmt is node:
            return True
        # Also check top-level if/try blocks (common pattern: try/except ImportError)
        if isinstance(stmt, (ast.If, ast.Try)):
            for child in ast.walk(stmt):
                if child is node:
                    return True
    return False


def build_graph(src_dir: str) -> tuple[dict, set]:
    """Build import dependency graph from module-level imports only."""
    graph = defaultdict(set)
    modules = set()

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            mod = path.replace(os.sep, ".").removesuffix(".py")
            if mod.endswith(".__init__"):
                mod = mod.removesuffix(".__init__")
            modules.add(mod)

            try:
                source = open(path, encoding="utf-8").read()
                tree = ast.parse(source, filename=path)
            except SyntaxError:
                continue

            pkg = mod.rsplit(".", 1)[0] if "." in mod else ""

            for node in ast.walk(tree):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue

                # Skip function-scoped imports
                if not is_module_level_import(node, tree):
                    continue

                targets = []
                if isinstance(node, ast.Import):
                    targets = [a.name for a in node.names]
                elif node.module:
                    targets = [node.module]

                for target in targets:
                    if not target.startswith("src"):
                        continue
                    # Skip package __init__ <-> submodule (standard pattern)
                    target_pkg = target.rsplit(".", 1)[0] if "." in target else ""
                    if target_pkg == mod or mod == target_pkg:
                        continue
                    graph[mod].add(target)

    return graph, modules


def find_cycles(graph: dict, modules: set) -> list[list[str]]:
    """DFS cycle detection."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {m: WHITE for m in modules}
    cycles = []

    def dfs(node, path):
        color[node] = GRAY
        for dep in graph.get(node, []):
            target = dep
            while target and target not in modules:
                target = target.rsplit(".", 1)[0] if "." in target else ""
            if not target:
                continue
            if color.get(target) == GRAY:
                idx = path.index(target)
                cycles.append(path[idx:] + [target])
            elif color.get(target) == WHITE:
                dfs(target, path + [target])
        color[node] = BLACK

    for m in sorted(modules):
        if color[m] == WHITE:
            dfs(m, [m])

    return cycles


def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    graph, modules = build_graph(src_dir)
    cycles = find_cycles(graph, modules)

    if cycles:
        print(f"FAIL: {len(cycles)} circular import(s) detected:")
        for c in cycles[:10]:
            print(f"  {' -> '.join(c)}")
        if len(cycles) > 10:
            print(f"  ... and {len(cycles) - 10} more")
        sys.exit(1)
    else:
        print(f"OK: {len(modules)} modules scanned, no circular imports")


if __name__ == "__main__":
    main()
