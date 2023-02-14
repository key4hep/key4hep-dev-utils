# Add manually some externals so that spack can pick them up
import subprocess
import os
import re
import yaml

PACKAGES = '/root/.spack/packages.yaml'
EXTERNALS = ['root', 'cmake', 'python', 'py-cython', 'py-pip', 'libyaml', 'py-setuptools', 'py-wheel', 'py-markupsafe',
             'py-jinja2', 'py-pyyaml', 'nlohmann-json', 'intel-tbb', 'boost', 'gaudi', 'dd4hep', 'gdb']
VERSION = re.compile('\d*\.\d*\.\d*')

out = subprocess.check_output(f'spack external find {" ".join(EXTERNALS)}'.split()).decode()
print(out)
with open(PACKAGES) as f:
    base = yaml.safe_load(f.read())
for p in EXTERNALS:
    if f'{p}@' not in out:
        path = [x for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x]
        if not path:
            print(f'Unable to find external {p}')
            continue
        path = path[0]
        version = re.search(VERSION, path).group(0)
        base['packages'][f'{p}'] = {'externals': [{'spec': f'{p}@{version}', 'prefix': f'{path}'}]}
yaml.dump(base, open(PACKAGES, 'w'))
