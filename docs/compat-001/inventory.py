"""Lab-only source evidence generator; never imported by a Frappe application.

Usage: python inventory.py SOURCE_DIRECTORY OUTPUT_JSON
Input directories must be named APP-COMMIT from immutable GitHub archives.
This produces syntactic call sites, not a resolved runtime call graph.
"""

import ast
import hashlib
import json
import pathlib
import sys

PINS = {
    "frappe": "988e54f3c4c291e2077a83809663f123731abe76",
    "erpnext": "4048fb70e14d1843956fcdabb7c3cca75a1cbcdd",
    "lending": "06fc075ae062ce38ac38a763f7f290da4ddd6fdb",
}


class Inventory(ast.NodeVisitor):
    def __init__(self, relative):
        self.relative = relative
        self.scope = []
        self.functions = []
        self.calls = []

    def visit_ClassDef(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node):
        self.scope.append(node.name)
        self.functions.append({"name": ".".join(self.scope), "line": node.lineno,
                               "decorators": [ast.unparse(d) for d in node.decorator_list]})
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        self.calls.append({"caller": ".".join(self.scope) or "<module>",
                           "line": node.lineno, "expression": ast.unparse(node.func)})
        self.generic_visit(node)


def main():
    root, output = map(pathlib.Path, sys.argv[1:])
    result = {"format": 1, "kind": "STATIC_SOURCE_INVENTORY_NOT_RUNTIME_PROOF",
              "pins": PINS, "files": [], "parse_errors": [],
              "limitations": ["Dynamic dispatch, imports, hooks and SQL calls are unresolved.",
                              "Line matches are candidates, not proven reachable financial paths.",
                              "No runtime tests or guard-coverage result is implied."]}
    markers = ("for_update", "ignore_", "from_bulk", "is_imported", "commit(",
               "rollback(", "savepoint(", "make_gl_entries", "cancel", "repost",
               "enqueue(", "db_set(", "db.sql(", "whitelist", "scheduler_events")
    for app, pin in PINS.items():
        source = root / f"{app}-{pin}"
        if not source.is_dir():
            raise SystemExit(f"Missing pinned source {source.name}")
        for path in sorted(source.rglob("*.py")):
            raw = path.read_bytes()
            relative = f"{app}/" + path.relative_to(source).as_posix()
            text = raw.decode("utf-8-sig")
            visitor = Inventory(relative)
            try:
                visitor.visit(ast.parse(text))
            except SyntaxError as exc:
                result["parse_errors"].append({"file": relative, "line": exc.lineno,
                                               "error": exc.msg})
            result["files"].append({"file": relative, "sha256": hashlib.sha256(raw).hexdigest(),
                                    "functions": visitor.functions, "calls": visitor.calls,
                                    "candidates": [{"line": i, "markers": [m for m in markers if m in line]}
                                                   for i, line in enumerate(text.splitlines(), 1)
                                                   if any(m in line for m in markers)]})
    output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(result["files"]),
                      "functions": sum(len(f["functions"]) for f in result["files"]),
                      "call_sites": sum(len(f["calls"]) for f in result["files"]),
                      "parse_errors": result["parse_errors"],
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
