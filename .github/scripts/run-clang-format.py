#!/usr/bin/env python3

import sys
import subprocess

from identify import identify


def get_output_lines(cmd):
    """Get the output from the cmd"""
    return (
        f
        for f in subprocess.run(cmd, capture_output=True).stdout.decode().split("\n")
        if f
    )


def get_repo_files():
    """Get all files of the current repository as a list assuming this is run at
    the repo root"""
    return get_output_lines(["git", "ls-files"])


def get_cpp_files(all_files):
    """Return a generator expression that only contains the c++ files"""
    for f in all_files:
        # Filter out files that are inputs for config steps
        if ".in." not in f and "c++" in identify.tags_from_path(f):
            yield f


def run_clang_format(files):
    """Run clang-format on all passed files"""
    return subprocess.run(
        ["clang-format-12", "-i", "--style=file"] + list(files)
    ).returncode


def get_changed_files():
    """Get all files that changed"""
    return get_output_lines(["git", "diff", "--name-only"])


if __name__ == "__main__":
    cpp_files = get_cpp_files(get_repo_files())
    run_clang_format(cpp_files)
    for f in get_changed_files():
        print(f"Formatted {f}")
