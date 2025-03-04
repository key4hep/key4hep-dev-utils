#!/bin/bash

# This script is used to update rulesets for all packages in 
# all the repositories in /key4hep-dev-utils/scripts/get_packages.sh

# Usage example:
# ./update-ruleset-all.sh

SCRIPT_DIR=$(dirname "$0")
source $SCRIPT_DIR/get_packages.sh

destination=$2
files_to_sync=("${@:3}")
for package_name in "${packages[@]}"; do
    $SCRIPT_DIR/update-ruleset.sh $package_name
done
