# Add manually some environment variables because when there is A depends on B depends on C
# dependency and B is an external the dependency A->C is lost in spack
import subprocess
import os
import yaml
import re

CONFIG = '/Package/spack/var/spack/environments/dev/spack.yaml'
CMAKE_PATHS = ['nlohmann-json']
CPATHS = ['vdt']
PYTHON = ['py-markupsafe']
VERSION = re.compile('\d*\.\d*\.\d*')

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

paths = [[x for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x][0] for p in CMAKE_PATHS]
base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CMAKE_PREFIX_PATH'] = ':'.join(base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CMAKE_PREFIX_PATH'].split(':')+paths)

paths = [[os.path.join(x, 'include') for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x][0] for p in CPATHS]
base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CPATH'] = ':'.join(base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['CPATH'].split(':')+paths)

paths = [[os.path.join(x, 'lib/python3.9/site-packages') for x in os.environ['CMAKE_PREFIX_PATH'].split(':') if f'/{p}/' in x][0] for p in PYTHON]
base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['PYTHONPATH'] = ':'.join(base['spack']['compilers'][0]['compiler']['environment']['prepend_path']['PYTHONPATH'].split(':')+paths)

yaml.dump(base, open(CONFIG, 'w'))
