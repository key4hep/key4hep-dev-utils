#!/usr/bin/env python3
"""Find namespace-scope functions and variables that could have internal linkage.

A function or variable that is defined in a source file, is not declared in any
header and is not used from any other file is only needed by that translation
unit. It can be put in an unnamed namespace (or made ``static``) so that it is
not exported from the library, which avoids symbol clashes between libraries
and lets the compiler warn when it becomes unused.

Functions marked ``inline`` or ``constexpr`` are also reported, since at
namespace scope they still have external linkage.

This is a heuristic, text-based scan (no compiler involved). Expect some false
positives (e.g. functions looked up by name with ``dlsym`` or from ROOT
macros) and misses (e.g. multiple declarators in one statement). Always build
after making changes: a forward declaration earlier in the same file also needs
to be changed, and a newly internal function that turns out to be unused will
trigger ``-Wunused-function``.

Usage:
    find-internal-linkage-candidates.py REPO [REPO ...]

By default tests, examples and files with a ``main`` function (executables) are
skipped; use ``--include-tests`` and ``--include-executables`` to keep them.
"""

import argparse
import os
import re
import sys

SOURCE_EXTENSIONS = (".cpp", ".cc", ".cxx")
HEADER_EXTENSIONS = (".h", ".hh", ".hpp", ".hxx", ".ipp", ".icc", ".inl")
# Files where a name can be referenced from without a C++ declaration
OTHER_EXTENSIONS = (".C", ".py", ".jinja2")
SKIP_DIRS = {".git", "build", "install", "_deps", "test_data"}
TEST_DIR_RE = re.compile(r"(^|/)(tests?|unittests|examples?|benchmarks?|doc|docs|scripts)/", re.IGNORECASE)
MAIN_RE = re.compile(r"\bint\s+main\s*\(")

FUNC_RE = re.compile(
    r"(?P<head>[A-Za-z_][\w:<>,\s\*&\[\]]*?[\s\*&>])(?P<name>[A-Za-z_]\w*)\s*\((?P<args>[^;{}]*)\)\s*"
    r"(?P<tail>(?:const|noexcept|override|final|->[^{;]*|\s)*)\{$"
)
VAR_RE = re.compile(
    r"^(?P<head>[A-Za-z_][\w:<>,\s\*&]*?[\s\*&>])(?P<name>[A-Za-z_]\w*)\s*(\[[^\]]*\])?\s*(=[^;]*|\{[^;]*\})?;$"
)
KEYWORDS = {"if", "for", "while", "switch", "return", "catch", "sizeof", "decltype", "alignof", "static_assert"}
# Functions that already have internal linkage (inline and constexpr functions
# at namespace scope still have external linkage, so they are not skipped)
LINKAGE_RE = re.compile(r"\bstatic\b")
VAR_SKIP_RE = re.compile(
    r"\b(static|extern|const|constexpr|using|typedef|return|template|friend|inline|thread_local)\b"
)


def strip_comments_and_strings(text):
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    text = re.sub(r'R"(\w*)\(.*?\)\1"', '""', text, flags=re.S)
    text = re.sub(r'"(\\.|[^"\\\n])*"', '""', text)
    text = re.sub(r"'(\\.|[^'\\\n])*'", "''", text)
    return text


def strip_preprocessor(text):
    out = []
    continued = False
    for line in text.split("\n"):
        if continued or line.lstrip().startswith("#"):
            continued = line.rstrip().endswith("\\")
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def at_namespace_scope(stack):
    return all(kind in ("ns", "extern_c") for kind in stack)


def scan_file(path):
    """Yield (line, kind, name) for namespace-scope definitions with external linkage."""
    with open(path, errors="ignore") as f:
        text = strip_preprocessor(strip_comments_and_strings(f.read()))
    stack = []  # kinds of the enclosing scopes: 'ns', 'anon', 'extern_c', 'other'
    stmt, stmt_line, line = "", 1, 1
    for c in text:
        if c == "\n":
            line += 1
        if c == "{":
            s = stmt.strip()
            kind = "other"
            m_ns = re.search(r"(?:^|\s)(inline\s+)?namespace(\s+[\w:]+)?\s*$", s)
            if re.search(r'extern\s*""\s*$', s):
                kind = "extern_c"
            elif m_ns:
                kind = "ns" if m_ns.group(2) else "anon"
            elif at_namespace_scope(stack):
                flat = " ".join(s.split())
                m = FUNC_RE.search(flat + "{")
                if m and m.group("name") not in KEYWORDS:
                    head = m.group("head")
                    is_member = "::" in flat[max(0, m.start("name") - 2) : m.start("name")]
                    is_operator = "operator" in flat[: m.start("name")][-12:]
                    is_type = re.match(r"^(class|struct|union|enum)\b", flat)
                    if not (is_member or is_operator or is_type or LINKAGE_RE.search(head)) and m.group("name") != "main":
                        yield stmt_line, "template" if "template" in head else "function", m.group("name")
            stack.append(kind)
            stmt, stmt_line = "", line
            continue
        if c == "}":
            if stack:
                stack.pop()
            stmt, stmt_line = "", line
            continue
        if c == ";":
            if at_namespace_scope(stack):
                flat = " ".join(stmt.split())
                m = VAR_RE.match(flat + ";")
                if (
                    m
                    and not VAR_SKIP_RE.search(m.group("head"))
                    and "(" not in m.group("head")
                    and not flat.startswith(("using", "typedef", "class ", "struct ", "enum ", "namespace", "template"))
                ):
                    yield stmt_line, "variable", m.group("name")
            stmt, stmt_line = "", line
            continue
        if not stmt.strip():
            stmt_line = line
        stmt += c


def collect_files(repo):
    sources, others = [], []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith("build")]
        for f in files:
            path = os.path.join(root, f)
            if f.endswith(SOURCE_EXTENSIONS):
                sources.append(path)
            elif f.endswith(HEADER_EXTENSIONS + OTHER_EXTENSIONS):
                others.append(path)
    return sorted(sources), others


def read(path):
    with open(path, errors="ignore") as f:
        return f.read()


def scan_repo(repo, include_tests, include_executables):
    sources, others = collect_files(repo)
    contents = {p: read(p) for p in sources + others}
    findings = []
    for path in sources:
        rel = os.path.relpath(path, repo)
        if not include_tests and TEST_DIR_RE.search(rel):
            continue
        if not include_executables and MAIN_RE.search(contents[path]):
            continue
        for line, kind, name in scan_file(path):
            word = re.compile(r"\b" + re.escape(name) + r"\b")
            # Declared in a header or used from another file: needs external linkage
            if any(word.search(text) for p, text in contents.items() if p != path):
                continue
            findings.append((rel, line, kind, name))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repos", nargs="+", help="Paths to the repositories to scan")
    parser.add_argument("--include-tests", action="store_true", help="Also scan tests and examples")
    parser.add_argument("--include-executables", action="store_true", help="Also scan files with a main function")
    args = parser.parse_args()

    total = 0
    for repo in args.repos:
        findings = scan_repo(repo, args.include_tests, args.include_executables)
        total += len(findings)
        if len(args.repos) > 1:
            print(f"# {repo}: {len(findings)} candidate(s)")
        for rel, line, kind, name in findings:
            print(f"{rel}:{line}: {kind} '{name}' could have internal linkage")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
