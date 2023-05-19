import yaml
import os
import argparse

argparser = argparse.ArgumentParser(description='Add nightly versions to spec file')
argparser.add_argument('repo', help='Repository name')
argparser.add_argument('spec', help='Spec file')
argparser.add_argument('release', help='Release path')
argparser.add_argument('default_branch', help='Default branch')
parser = argparser.parse_args()

def add_versions_to_spec(repo, spec, release, default_branch):
    packages = os.listdir(release)
    to_add = []
    for p in packages:
        if not os.path.isdir(os.path.join(release, p)):
            continue
        versions = os.listdir(os.path.join(release, p))
        for v in versions:
            if '=develop' in v:
                to_add.append(f'{p}@{v[:v.find("=develop")+len("=develop")]}')
                break
    with open(spec, 'r+') as f:
        spec_data = yaml.safe_load(f)
        current_specs = set([s.split('@')[0] for s in spec_data['spack']['specs']])
        current_specs.add(repo)
        spec_data['spack']['specs'] += [f'{repo}@{default_branch}' + ' '.join(f'^{p}' for p in to_add if p not in current_specs)]
        f.seek(0)
        yaml.dump(spec_data, f, default_flow_style=False)

add_versions_to_spec(parser.repo, parser.spec, parser.release, parser.default_branch)
