#!/env/python

# This script will create a CMakeLists.txt file for a Key4hep project

import os
import sys
import shutil
import re
import argparse
import requests

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
               'k4MarlinWrapper',
               'k4EDM4hep2LCIOConv',
               'k4geo',
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
    shutil.copyfile(f'{os.path.dirname(__file__)}/CMakeLists.txt', 'CMakeLists.txt')
else:
    print("CMakeLists.txt already exists in the current directory. Aborting.")
    sys.exit(1)

if 'KEY4HEP_STACK' not in os.environ:
    print('Warning: KEY4HEP_STACK environment variable not set')

to_add = []
# Find if there are any simlinks to the Key4hep or other packages
for f in os.listdir('.'):
    if f == 'CMakeLists.txt' or f == 'build':
        continue
    if os.path.isdir(f) and 'CMakeLists.txt' in os.listdir(f):
        # Try to find the project name
        with open(os.path.join(f, 'CMakeLists.txt'), 'r') as cmake_list:
            project_name = re.search('project\( *(\S*) *\)', cmake_list.read(),
                                     re.IGNORECASE).group(1)
            # If not found
            project_name = project_name or f
    to_add.append((f, project_name))

if not to_add and not args.repositories:
    print('Warning: No repositories have been found. The template CMakeLists.txt will be copied'
          ' but no packages will be built.')

template = """
FetchContent_Declare(
  {}
  SOURCE_DIR ${{CMAKE_SOURCE_DIR}}/{}
  FIND_PACKAGE_ARGS NAMES {}
)
"""
new_text = ''
for f, project_name in to_add:
    new_text += template.format(f, f, project_name)

template = """
FetchContent_Declare(
  {}
  GIT_REPOSITORY https://github.com/{}/{}.git
  GIT_TAG {}
  FIND_PACKAGE_ARGS NAMES {}
)
"""

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
    
    new_text += template.format(repo, org, repo, default_branch, repo.upper())

new_text += '\n' + 'FetchContent_MakeAvailable(${pkgs})'

# Now let's add the other repositories

with open('CMakeLists.txt', 'r') as cmake_list:
    original = cmake_list.read()
all_packages = [p[1] for p in to_add] + args.repositories
newls = []
for p in build_order:
    for p2 in all_packages:
        if p.lower() == p2.lower():
            newls.append(p)
            all_packages.remove(p2)
            break
newls += all_packages
if all_packages:
    print(f'Warning: the following packages "{" ".join(all_packages)}" were not found in the build order.'
        ' They will be added at the end of the list. Please edit the CMakeLists.txt file manually if needed.')
original = re.sub(r'set\(pkgs .*\)', rf'set(pkgs {" ".join(newls)})', original)
with open('CMakeLists.txt', 'w') as cmake_list:
    cmake_list.write(original + new_text)
print('''CMakeLists.txt file created. You can now run


. env.sh
mkdir build
cd build
cmake ..
make -j N install

to build the project.''')

with open('env.sh', 'w') as f:
    paths = '|'.join([f'/{p.lower()}/' for p in newls])
    packages_or = ' or '.join([f'${{BLUE}}\\"/{p.lower()}/\\"${{RESET}}' for p in newls])
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
