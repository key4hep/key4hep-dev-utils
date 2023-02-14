# Clone the list of dependents repo to the current one
# and also an input list of repos in branch other than the default one
# Usage: python3 fetch_and_checkout.py current_repo owner1 repo1 branch1 onwer2 repo2 branch2 ...
import subprocess
import sys
import os

EXCLUDE = ['cepcsw', 'dd4hep', 'gaudi', 'key4hep-stack']

name = sys.argv[1]
if len(sys.argv) == 3:
    packages = [x.split() for x in sys.argv[2].split('\n')]
else:
    packages = []
# Spack uses the names of the repo in lower caps
for p in packages:
    p[1] = p[1].lower()
repos = set(p[1] for p in packages)

# packages.append('jmcarcell podio test'.split())
# print(packages)

out = subprocess.check_output(f'spack dependents {name}'.split()).decode()
for p in out.split():
    if p in EXCLUDE or p in repos:
        continue
    if p not in ['podio', 'edm4hep', 'k4edm4hep2lcioconv']:
        continue
    # TODO: fix finding the right owner
    packages.append(['key4hep', p, None])

pwd = os.getcwd()

for owner, repo, branch in packages:
    print(owner, repo, branch)
    if branch:
        subprocess.check_output(f'git clone https://github.com/{owner}/{repo} --branch {branch} --depth 1', shell=True)
        subprocess.check_output(f'spack develop --no-clone --path {os.path.join(pwd, repo)} {repo.lower()}@master', shell=True)
    subprocess.check_output(f'spack add {repo.lower()}@master', shell=True)
