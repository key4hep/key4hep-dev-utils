
import os
import re
import argparse
import requests

argparser = argparse.ArgumentParser(description='Check tagged versions')
argparser.add_argument('file', help='file with the spack concretization output')

args = argparser.parse_args()

package_and_version = re.compile(r'([a-z0-9-]+)@([0-9\.a-z]+)')
version_re = re.compile(r'([0-9]+)')

packages = {}
with open(args.file, 'r') as f:
    for line in f:
        m = package_and_version.search(line)
        if m:
            package = m.group(1)
            version = m.group(2)
            packages[package] = version

headers = {"Accept": "application/vnd.github+json"}

# gitlab doesn't seem to need a token, maybe there is some rate limiting without one
token = os.environ.get("GITHUB_TOKEN", None)
if token:
    headers["Authorization"] = f"token {token}"

orgs = ['key4hep', 'AIDASoft', 'iLCSoft', 'HEP-FCC', 'CEPC']
for org in orgs:
    repos = requests.get(f'https://api.github.com/orgs/{org}/repos', headers=headers).json()
    for repo in repos:
        name = repo['name']
        if org == 'key4hep' and name == 'Gaudi':
            continue
        if org == 'CEPC' and name == 'ConformalTracking':
            continue
        tags = requests.get(f'https://api.github.com/repos/{org}/{name}/tags', headers=headers).json()
        # Sort by name which will mean that the latest tag is either the first or second
        # because tag v00-10 is sorted before than v00-10-0x
        if len(tags) == 0:
            continue
        if len(tags) > 1:
            # Now get the date of the commit for the first two tags
            date = requests.get(f'https://api.github.com/repos/{org}/{name}/commits/{tags[0]["commit"]["sha"]}', headers=headers).json()['commit']['committer']['date']
            other_date = requests.get(f'https://api.github.com/repos/{org}/{name}/commits/{tags[1]["commit"]["sha"]}', headers=headers).json()['commit']['committer']['date']
            if date > other_date:
                latest_tag = tags[0]['name']
            else:
                latest_tag = tags[1]['name']
        else:
            latest_tag = tags[0]['name']
        if latest_tag[0] == 'v':
            latest_tag = latest_tag[1:]
        latest_tag = latest_tag.replace('-', '.')
        if name.lower() in packages:
            spack_groups = version_re.findall(packages[name.lower()])
            original_groups = version_re.findall(latest_tag)
            if all([int(s) == int(o) for s, o in zip(spack_groups, original_groups)]):
                print(f'{name} is up to date')
            else:
                print(f'{name} is not up to date: {packages[name.lower()]} != {latest_tag}')
