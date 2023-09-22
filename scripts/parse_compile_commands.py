import json
import argparse
import os
import collections

parser = argparse.ArgumentParser()
parser.add_argument("compile_commands_json", help="Path to compile_commands.json")

args = parser.parse_args()
with open(args.compile_commands_json, 'r') as f:
    compile_commands = json.load(f)
prefix = os.path.dirname(compile_commands[0]['directory'])

package_commands = collections.defaultdict(list)
for command in compile_commands:
    if command['file'].startswith(prefix):
        package_commands[command['file'][len(prefix)+1:].split('/')[0]].append(command)

dirs = os.listdir(prefix)
for package, commands in package_commands.items():
    if package == 'build':
        continue
    # print(package, len(commands))
    if package not in dirs:
        print(f'{package} not in {prefix}')
        continue
    with open(os.path.join(prefix, package, 'compile_commands.json'), 'w') as f:
        json.dump(commands, f, indent=2)
