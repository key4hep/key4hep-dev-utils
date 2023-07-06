import yaml
import os
import argparse

argparser = argparse.ArgumentParser(description='Add nightly versions to spec file')
argparser.add_argument('repo', help='Repository name')
argparser.add_argument('spec', help='Spec file')
argparser.add_argument('default_branch', help='Default branch')
argparser.add_argument('release', help='Scratch release path')
argparser.add_argument('latest_release', help='Release path')
parser = argparser.parse_args()

def add_versions_to_spec(repo, spec, default_branch, release, latest_release):
    packages = os.listdir(release)
    to_add = []
    for p in packages:
        if not os.path.isdir(os.path.join(release, p)):
            continue
        versions = os.listdir(os.path.join(release, p))
        for v in versions:
            # If the version is the scratch nightly
            if '=develop' in v:
                latest_versions = os.listdir(os.path.join(latest_release, p))
                # Check also the latest nightly, if found there let's use this one
                for lv in latest_versions:
                    if '=develop' in lv:
                        to_add.append(f'{p}@{lv[:lv.find("=develop")+len("=develop")]}')
                        break
                else:
                    to_add.append(f'{p}@{v[:v.find("=develop")+len("=develop")]}')
                    break
                # Found so we can break
                break
    with open(spec, 'r+') as f:
        spec_data = yaml.safe_load(f)
        current_specs = set([s.split('@')[0] for s in spec_data['spack']['specs']])
        current_specs.add(repo)
        spec_data['spack']['specs'] += [f'{repo}@{default_branch}'] + [p for p in to_add if p.split('@')[0] not in current_specs]
        f.seek(0)
        yaml.dump(spec_data, f, default_flow_style=False)

add_versions_to_spec(parser.repo, parser.spec, parser.default_branch, parser.release, parser.latest_release)
