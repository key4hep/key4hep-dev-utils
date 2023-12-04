#!/env/python

# This script will create a CMakeLists.txt file for a Key4hep project

import os
import sys
import shutil
import re
import argparse
import requests
import jinja2

# ANSI color codes
RESET = "\033[0m"    # Reset to default text color
RED = "\033[91m"      # Red text color
GREEN = "\033[32m"    # Green text color
YELLOW = "\033[93m"   # Yellow text color
BLUE = "\033[94m"     # Blue text color
MAGENTA = "\033[95m"  # Magenta text color
CYAN = "\033[96m"     # Cyan text color
ORANGE = "\033[33m"   # Orange text color

build_order = ['podio',
               'EDM4hep',
               'LCIO',
               'iLCUtil',
               'GEAR',
               'LCCD',
               'Marlin',
               'Gaudi',
               'k4FWCore',
               'k4-project-template',
               'k4EDM4hep2LcioConv',
               'k4SimGeant4',
               'k4MarlinWrapper',
               'k4geo',
               'k4Reco',
               'k4SimDelphes',
               'FCCAnalyses',
]

possible_organizations = ['key4hep', 'AIDASoft', 'iLCSoft', 'HEP-FCC',
                          'CEPC', 'CLICdp']

env_variables = ['PATH', 'LD_LIBRARY_PATH', 'PYTHONPATH', 'ROOT_INCLUDE_PATH',
                 'CMAKE_PREFIX_PATH']

parser = argparse.ArgumentParser(description='Setup a Key4hep project')
parser.add_argument('repositories', nargs='*', help='List of repositories to clone')
# parser.add_argument('--shallow', type=int, help='')
args = parser.parse_args()

# First, copy the template
if not os.path.exists('CMakeLists.txt'):
    shutil.copyfile(f'{os.path.dirname(__file__)}/CMakeLists.txt.jinja2', 'CMakeLists.txt.jinja2')
else:
    print(f'{RED}CMakeLists.txt already exists in the current directory. Aborting.{RESET}')
    sys.exit(1)

if 'KEY4HEP_STACK' not in os.environ:
    print(f'{ORANGE}Warning: KEY4HEP_STACK environment variable not set{RESET}')

to_add = []
# Find if there are any simlinks to the Key4hep packages or other packages
for f in os.listdir('.'):
    if f == 'CMakeLists.txt' or f == 'build':
        continue
    if os.path.isdir(f) and 'CMakeLists.txt' in os.listdir(f):
        # Try to find the project name
        with open(os.path.join(f, 'CMakeLists.txt'), 'r') as cmake_list:
            print('Searching for project name in', os.path.join(f, 'CMakeLists.txt'))
            project_name = re.search('project\( *(\S*) *.*\)', cmake_list.read(),
                                     re.IGNORECASE).group(1)
            # If not found
            project_name = project_name or f
        to_add.append((f, project_name))

if not to_add and not args.repositories:
    print(f'{ORANGE}Warning: No repositories have been found. The template CMakeLists.txt will be copied'
          f' but no packages will be built.{RESET}')

sym_packages = []
for f, project_name in to_add:
    sym_packages.append( {'name': f,
                          'project_name': project_name})

downloaded_packages = []

for repo in args.repositories:
    # Guess which organization it belongs to
    for org in possible_organizations:
        r = requests.get(f"https://api.github.com/repos/{org}/{repo}")
        if r.status_code == 200:
            default_branch = r.json()['default_branch']
            break
    else:
        org = 'org_not_found'
        default_branch = 'master'
    
    downloaded_packages.append({'name': repo,
                                'org': org,
                                'tag': default_branch,
                                'project_name': repo.upper()})

# Sort the packages in the order they should be built
all_packages = [p[1] for p in to_add] + args.repositories
packages_in_order = []
index_mapping = {}
for p2 in list(all_packages):
    for i, p in enumerate(build_order):
        if p.lower() == p2.lower():
            index_mapping[i] = p2
            all_packages.remove(p2)
            break
packages_in_order = [index_mapping[i] for i in sorted(index_mapping.keys())]
# Add the packages that haven't been found at the end
# so it's more likely that they will build
packages_in_order += all_packages

if all_packages:
    print(f'{ORANGE}Warning: the following packages "{" ".join(all_packages)}" were not found in the build order.'
        f' They will be added at the end of the list. Please edit the CMakeLists.txt file manually if needed.{RESET}')

jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
template = jinja2_env.get_template('CMakeLists.txt.jinja2')
with open('CMakeLists.txt', 'w') as f:
    f.write(template.render(sym_packages=sym_packages,
                            downloaded_packages=downloaded_packages,
                            build_order=packages_in_order))

os.remove('CMakeLists.txt.jinja2')

print(f'''{GREEN}CMakeLists.txt file created.{RESET} You can now run

. env.sh
mkdir build
cd build
cmake ..
make -j N install

to build the project.''')

with open('env.sh', 'w') as f:
    paths = '|'.join([f'/{p.lower()}/' for p in packages_in_order])
    packages_or = ' or '.join([f'${{BLUE}}\\"/{p.lower()}/\\"${{RESET}}' for p in packages_in_order])
    f.write('''BLUE="\e[34m"
GREEN="\e[32m"
RED="\e[31m"
RESET="\e[0m"
''')

    # Check to make sure the script is being sourced
    f.write('''
if [ -n "$BASH_SOURCE" ]; then
    if [ "$0" == "$BASH_SOURCE" ]; then
        echo -e "${RED}Error${RESET}: This script should be sourced, not executed directly."
        exit 1
    fi
elif [ -n "$ZSH_SOURCE" ]; then
    if [ "$0" == "$ZSH_SOURCE" ]; then
        echo -e "${RED}Error${RESET}: This script should be sourced, not executed directly."
        exit 1
    fi
fi\n''')

    f.write(f'''echo -e "Removed from the env variables\
${{BLUE}} PATH LD_LIBRARY_PATH PYTHONPATH ROOT_INCLUDE_PATH CMAKE_PREFIX_PATH${{RESET}}\
 any path that contains the following strings: {packages_or}"
''')
    for v in env_variables:
        f.write(rf'export {v}=$(echo ${v} | tr ":" "\n" | grep -Ev "{paths}" | tr "\n" ":")' + '\n')

    f.write('''echo -e "Added (if not present already) the following paths:
${BLUE}PATH              -> $PWD/install/bin${RESET}
${BLUE}LD_LIBRARY_PATH   -> $PWD/install/lib:$PWD/install/lib64${RESET}
${BLUE}PYTHONPATH        -> $PWD/install/python${RESET}
${BLUE}ROOT_INCLUDE_PATH -> $PWD/install/include${RESET}
${BLUE}CMAKE_PREFIX_PATH -> $PWD/install${RESET}"

if [[ ":$PATH:" != *":$PWD/install/bin:"* ]]; then
    export PATH=$PWD/install/bin:$PATH
fi

if [[ ":$LD_LIBRARY_PATH:" != *":$PWD/install/lib:"* ]]; then
    export LD_LIBRARY_PATH=$PWD/install/lib:$PWD/install/lib64:$LD_LIBRARY_PATH
fi

if [[ ":$PYTHONPATH:" != *":$PWD/install/python:"* ]]; then
    export PYTHONPATH=$PWD/install/python:$PYTHONPATH
fi

if [[ ":$ROOT_INCLUDE_PATH:" != *":$PWD/install/include:"* ]]; then
    export ROOT_INCLUDE_PATH=$PWD/install/include:$ROOT_INCLUDE_PATH
fi

if [[ ":$CMAKE_PREFIX_PATH:" != *":$PWD/install:"* ]]; then
    export CMAKE_PREFIX_PATH=$PWD/install:$CMAKE_PREFIX_PATH
fi\n''')
