#!/bin/bash

# This script runs a given script for every package listed in get_packages.sh.
# Usage: ./update-all.sh <script> [additional args...]
# Example: ./update-all.sh update-github-settings.sh

set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <script> [additional args...]"
  exit 1
fi

SCRIPT_DIR=$(dirname "$0")
SCRIPT_TO_RUN=$1
shift

source $SCRIPT_DIR/get_packages.sh

for package_name in "${packages[@]}"; do
    $SCRIPT_DIR/$SCRIPT_TO_RUN $package_name "$@"
done
