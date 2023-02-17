# Clone the list of dependents repo to the current one
# and also an input list of repos in branch other than the default one
# Usage: python3 fetch_and_checkout.py current_repo owner1 repo1 branch1 onwer2 repo2 branch2 ...
import subprocess
import sys
import os
import re
import yaml

EXCLUDE = set(['cepcsw', 'dd4hep', 'gaudi', 'key4hep-stack', 'key4dcmtsim'])
DEFAULT_BRANCH_PATTERN = r'Safe versions: *\n.*on branch \b([\w-]*)\b'

cache = {}

name = sys.argv[1]
if len(sys.argv) == 3:  # owner name branch
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
    if p in EXCLUDE or p in repos:
        continue
    # TODO: fix finding the right owner
    if p not in cache:
        cache[p] = subprocess.check_output(f'spack info {p}'.split()).decode()

    res = re.search(f'github\.com/([\w-]*)/', cache[p])
    owner = res.group(1)
        
    packages.append([owner, p, None])

pwd = os.getcwd()

for owner, repo, branch in packages:
    print(owner, repo, branch)
    if repo not in cache:
        cache[repo] = subprocess.check_output(f'spack info {repo}'.split()).decode()
    res = re.search(DEFAULT_BRANCH_PATTERN, cache[repo])
    default_branch = res.group(1)
    if branch:
        subprocess.check_output(f'git clone https://github.com/{owner}/{repo} --branch {branch} --depth 1', shell=True)
        subprocess.check_output(f'spack develop --no-clone --path {os.path.join(pwd, repo)} {repo.lower()}@{default_branch}', shell=True)
    subprocess.check_output(f'spack add {repo.lower()}@{default_branch}', shell=True)



CONFIG = '/Package/spack/var/spack/environments/dev/spack.yaml'

with open(CONFIG) as f:
    base = yaml.safe_load(f.read())
    for v in ['CMAKE_PREFIX_PATH', 'LD_LIBRARY_PATH', 'PYTHONPATH']:
        paths = os.env[v]
        newpaths = []
        for path in paths.split(':'):
            for p in packages:
                if f'/{p}/' in path:
                    break
            else:
                newpaths.append(path)
        newpaths = ':'.join(newpaths)
        base['spack']['compilers'][0]['compiler']['environment']['prepend_path'][v] = newpaths

yaml.dump(base, open(CONFIG, 'w'))
