# Add manually some externals so that spack can pick them up
import subprocess
import os
import re
import yaml

CONFIG = '/Package/spack/var/spack/environments/dev/spack.yaml'
# PACKAGES = '/root/.spack/packages.yaml'
EXTERNALS = [
    'boost',
    'catch2',
    'clhep',
    'cmake',
    'dd4hep',
    'eigen',
    'evtgen',
    'fastjet',
    'gaudi',
    'gdb',
    'geant4',
    'hepmc',
    'hepmc3',
    'heppdt',
    'intel-tbb',
    'libyaml',
    'marlin',
    'ninja',
    'nlohmann-json',
    'py-awkward',
    'py-cython',
    'py-jinja2',
    'py-markupsafe',
    'py-pip',
    'py-pyyaml',
    'py-setuptools',
    'py-six',
    'pythia8',
    'python',
    'py-wheel',
    'root',
    'rsync',
    'simsipm',
    'util-linux-uuid',
    'vdt',
    'zlib',
]
VERSION = re.compile('(:?\d+\.)+\d*')

out = subprocess.check_output(f'spack external find {" ".join(EXTERNALS)}'.split()).decode()
print(out)
with open(CONFIG) as f:
    base = yaml.safe_load(f.read())
for p in EXTERNALS:
    if f'{p}@' not in out and p not in base['spack']['packages']:
        path = [x for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x]
        if not path:
            print(f'Unable to find external {p}')
            continue
        path = path[0]
        version = re.search(VERSION, path).group(0)
        base['spack']['packages'][p] = {'externals': [{'spec': f'{p}@{version}', 'prefix': f'{path}'}]}
yaml.dump(base, open(CONFIG, 'w'))

# When A depends on B which depends on C but B is an external,
# spack won't set up the dependency C for us so it has to be done manually
# Instead of selecting only the packages that are needed try to do all of them
with open(CONFIG) as f:
    base = yaml.safe_load(f.read())
if 'compilers' not in base['spack']:
    path = [x for x in os.environ['CXX'].split(':') if f'/gcc/' in x][0]
    if '/bin/g++' in path:
        path = path.removesuffix('/bin/g++')
    version = re.search(VERSION, path).group(0)
    base['spack']['compilers'] = [{'compiler': {'spec': f'gcc@{version}',
     'paths': {'cc': os.path.join(path, 'bin/gcc'),
      'cxx': os.path.join(path, 'bin/g++'),
      'f77': os.path.join(path, 'bin/gfortran'),
      'fc': os.path.join(path, 'bin/gfortran')},
     'flags': {},
     'operating_system': 'centos7',
     'target': 'x86_64',
     'modules': [],
     'environment': {},
     'extra_rpaths': []}}]
if 'prepend_path' not in base['spack']['compilers'][0]['compiler']['environment']:
    base['spack']['compilers'][0]['compiler']['environment']['prepend_path'] = {'CMAKE_PREFIX_PATH': '', 'CPATH': '', 'PYTHONPATH': ''}

paths = [[x for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x][0] for p in EXTERNALS]
base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CMAKE_PREFIX_PATH'] = ':'.join(base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CMAKE_PREFIX_PATH'].split(':')+paths)

paths = [[os.path.join(x, 'include') for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x][0] for p in EXTERNALS]
base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CPATH'] = ':'.join(base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CPATH'].split(':')+paths)

paths = []
for p in EXTERNALS:
    for x in os.environ['CMAKE_PREFIX_PATH'].split(':'):
        if f'/{p}/' in x:
            if os.path.exists(os.path.join(x, 'lib/python3.9/site-packages')):
                paths.append(os.path.join(x, 'lib/python3.9/site-packages'))
            elif os.path.exists(os.path.join(x, 'python')):
                paths.append(os.path.join(x, 'python'))
            else:
                paths.append(os.path.join(x, 'lib'))

base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['PYTHONPATH'] = ':'.join(base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['PYTHONPATH'].split(':')+paths)

yaml.dump(base, open(CONFIG, 'w'))
