# Clone the list of dependents repo to the current one
# and also an input list of repos in branch other than the default one
# Usage: python3 fetch_and_checkout.py current_repo owner1 repo1 branch1 onwer2 repo2 branch2 ...
import subprocess
import sys
import re

EXCLUDE = set([
    'acts',
    'cepcsw',
    'fccdetectors',
    'gaudi',
    'ilcsoft',
    'k4actstracking',
    'k4pandora',
    'key4dcmtsim',
    'key4hep-stack',
])

# From Spack we get who are the dependent packages but not the order
# This is the build order that will be used for the packages, a package
# that appears in the list before another one will be built before
# Maybe there is a way of getting this ordering in Spack
build_order = ['podio',
               'edm4hep',
               'lcio',
               'ilcutil',
               'gear',
               'lccd',
               'marlin',
               'gaudi',
               'k4fwcore',
               'k4projecttemplate',
               'k4edm4hep2lcioconv',
               'k4gen',
               'dd4hep',
               'k4simgeant4',
               'k4marlinwrapper',
               'k4geo',
               'k4reccalorimeter',
               'fccsw',
               'k4reco',
               'k4simdelphes',
               'fccanalyses',
]

DEFAULT_BRANCH_PATTERN = r'Safe versions: *\n.*on branch \b([\w-]*)\b'
# Something like https://github.com/AIDASoft/DD4hep.git
GIT_ADDRESS_PATTERN = r'http(?:s|)://github.com/[\w-]*/[\w-]*.git'

cache = {}

if len(sys.argv) == 1:
    print('fetch_and_checkout.py: No packages to checkout')
    sys.ext()
name = sys.argv[1]
if len(sys.argv) == 3 and sys.argv[2]:  # owner name branch
    packages = [x.split() for x in sys.argv[2].split('\n')]
else:
    packages = []

# Spack uses the names of the repo in lower caps
for p in packages:
    p[1] = p[1].lower()
packages = [p for p in packages if p[1] not in EXCLUDE]
repos = set(p[1] for p in packages)

out = subprocess.check_output(f'spack dependents {name}'.split()).decode()
for p in out.split():
    p = p.strip()
    if p in EXCLUDE or p in repos:
        continue
    # TODO: fix finding the right owner
    if p not in cache:
        cache[p] = subprocess.check_output(f'spack info {p}'.split()).decode()

    res = re.search(r'github\.com/([\w-]*)/', cache[p])
    owner = res.group(1)

    packages.append([owner, p, None])

index_mapping = {}
for p2 in list(packages):
    for i, p in enumerate(build_order):
        if p.lower() == p2[1].lower():
            index_mapping[i] = p2
            packages.remove(p2)
            break
packages_in_order = [index_mapping[i] for i in sorted(index_mapping.keys())]
# Add the packages that haven't been found at the end
packages_in_order += packages

# Add 01, 02, ... to the names of the packages
# so that they are sorted in the order of the build
digits = len(str(len(packages_in_order)))

for i, (owner, repo, branch) in enumerate(packages_in_order):
    print(owner, repo, branch)
    if repo not in cache:
        cache[repo] = subprocess.check_output(f'spack info {repo}'.split()).decode()
    res = re.search(DEFAULT_BRANCH_PATTERN, cache[repo])
    address = re.search(GIT_ADDRESS_PATTERN, cache[repo])
    if not address:
        print(f'fetch_and_checkout.py: No git address found for {repo}')
        continue
    default_branch = res.group(1)
    if branch:
        subprocess.check_output(f'git clone {address.group(0)} {i:0{digits}}_{repo} --depth 1 -b {branch}', shell=True)
    else:
        subprocess.check_output(f'git clone {address.group(0)} {i:0{digits}}_{repo} --depth 1', shell=True)
