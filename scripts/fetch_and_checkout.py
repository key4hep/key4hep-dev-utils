# Clone the packages that depend (transitively) on the current repository,
# using the dependency information of the LCG (lcgcmake) nightly release that
# has been sourced with `source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh`.
# Only packages in the ORGANIZATIONS below are cloned. The clones are named
# 01_<name>, 02_<name>, ... so that sorting them gives a valid build order.
#
# Usage: python3 fetch_and_checkout.py <owner/repo> ["owner1 repo1 branch1\nowner2 repo2 branch2..."]
#   - <owner/repo>: the current repository, e.g. key4hep/EDM4hep (the owner can be omitted,
#     and if it doesn't match, e.g. for forks, only the name of the repository is used)
#   - The optional second argument is a list of packages to check out in a branch
#     different from the default one
import os
import re
import subprocess
import sys
import urllib.request
from graphlib import TopologicalSorter

ORGANIZATIONS = {"key4hep", "hep-fcc"}

EXCLUDE = {
    "fccsw",
    "k4actstracking",
    "key4hep_stack",
}

LCGCMAKE_RAW_URL = "https://gitlab.cern.ch/sft/lcgcmake/-/raw/{commit}/cmake/toolchain/{toolchain}.cmake"
LCG_PACKAGE_PATTERN = r"^\s*LCG_external_package\(\s*(\S+)\s+.*\bGIT=(\S+?)\s*\)"
GITHUB_PATTERN = r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?$"


def find_release(view_dir):
    """Find the release area (with the summary file) the LCG view points to"""
    platform = os.path.basename(view_dir)
    release = os.path.dirname(view_dir).replace("/views/", "/nightlies/")
    if os.path.isfile(f"{release}/LCG_externals_{platform}.txt"):
        return release, platform
    # Fall back to following one of the symlinks in the view, which point to
    # <release>/<name>/<version>/<platform>/...
    for entry in os.scandir(f"{view_dir}/lib"):
        if entry.is_symlink():
            target = os.path.realpath(entry.path)
            if f"/{platform}/" in target:
                release = target.split(f"/{platform}/")[0]
                return os.path.dirname(os.path.dirname(release)), platform
    sys.exit(f"fetch_and_checkout.py: Could not find the release for the view {view_dir}")


def read_summary(release, platform):
    """Return a dictionary name -> (home, set of direct dependencies)"""
    packages = {}
    with open(f"{release}/LCG_externals_{platform}.txt") as f:
        for line in f:
            fields = [x.strip() for x in line.split(";")]
            if len(fields) < 5:
                continue
            # Dependencies look like name-hash
            deps = {d.rsplit("-", 1)[0] for d in fields[4].split(",") if d}
            packages[fields[0]] = (fields[3], deps)
    return packages


def lcgcmake_commit(packages):
    """Get the lcgcmake commit used for the release from the .buildinfo file of
    key4hep_stack, which depends on everything and is therefore built last"""
    try:
        home = packages["key4hep_stack"][0]
        with open(f"{home}/.buildinfo_key4hep_stack.txt") as f:
            return re.search(r"GITHASH: '?(\w+)", f.read()).group(1)
    except (KeyError, OSError, AttributeError):
        return "master"


def read_git_urls(commit, toolchain):
    """Return a dictionary name -> git URL from the toolchain"""
    url = LCGCMAKE_RAW_URL.format(commit=commit, toolchain=toolchain)
    with urllib.request.urlopen(url) as f:
        text = f.read().decode()
    return {res.group(1): res.group(2) for line in text.splitlines()
            if (res := re.match(LCG_PACKAGE_PATTERN, line))}


def owner_repo(url):
    res = re.search(GITHUB_PATTERN, url)
    return (res.group(1).lower(), res.group(2).lower()) if res else (None, None)


def closure(start, graph):
    """All the nodes reachable from start (not including start)"""
    seen, todo = set(), list(graph.get(start, ()))
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n)
            todo.extend(graph.get(n, ()))
    return seen


if len(sys.argv) == 1:
    sys.exit("fetch_and_checkout.py: No package given")
current = sys.argv[1].lower()
branches = {}
extra = []
if len(sys.argv) == 3 and sys.argv[2]:
    for line in sys.argv[2].split("\n"):
        if line.split():
            owner, repo, branch = line.split()
            branches[repo.lower()] = branch
            extra.append((owner, repo))

if "LCG_VIEW_DIR" not in os.environ or "LCG_VERSION" not in os.environ:
    sys.exit("fetch_and_checkout.py: LCG_VIEW_DIR or LCG_VERSION not set, has an LCG view been sourced?")
release, platform = find_release(os.environ["LCG_VIEW_DIR"])
print(f"Using release {release} for platform {platform}")
packages = read_summary(release, platform)
commit = lcgcmake_commit(packages)
print(f"Using lcgcmake commit {commit}")
urls = read_git_urls(commit, f"heptools-{os.environ['LCG_VERSION']}")


def matches(name, with_owner):
    owner, repo = owner_repo(urls.get(name, ""))
    if with_owner:
        return f"{owner}/{repo}" == current
    current_repo = current.split("/")[-1]
    return repo == current_repo or name.lower() == current_repo


# Match first owner/repo and then only the name of the repository, for forks
target = next((name for name in packages if matches(name, True)), None) or \
    next((name for name in packages if matches(name, False)), None)
if target is None:
    print(f"fetch_and_checkout.py: {current} not found in the release, nothing to build")
    sys.exit(0)

dependents = {}
for name, (_, deps) in packages.items():
    for dep in deps:
        dependents.setdefault(dep, set()).add(name)

selected = {
    name for name in closure(target, dependents)
    if name.lower() not in EXCLUDE and owner_repo(urls.get(name, ""))[0] in ORGANIZATIONS
}
# Packages with a non-default branch are built even if they don't depend on the current one
for owner, repo in extra:
    name = next((n for n in packages if owner_repo(urls.get(n, ""))[1] == repo.lower()), None)
    if name is None:
        name = repo.lower()
        urls[name] = f"https://github.com/{owner}/{repo}.git"
        packages[name] = (None, set())
    if name != target:
        selected.add(name)

# Use all the (transitive) dependencies so that the order is correct even when
# packages in between are not selected
dependencies = {name: deps for name, (_, deps) in packages.items()}
graph = {name: closure(name, dependencies) & selected for name in selected}
order = list(TopologicalSorter(graph).static_order())

print(f"Packages depending on {target} that will be built: {' '.join(order)}")
digits = len(str(len(order)))
for i, name in enumerate(order):
    url = urls[name]
    branch = branches.get(owner_repo(url)[1])
    print(url, branch or "(default branch)")
    cmd = ["git", "clone", url, f"{i:0{digits}}_{name.lower()}", "--depth", "1", "-q"]
    if branch:
        cmd += ["-b", branch]
    subprocess.check_call(cmd)
