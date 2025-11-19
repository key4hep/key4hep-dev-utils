#!/bin/bash

# This script is used to update the pre-commit configuration for a single repository

# Usage example:
# ./update-pre-commit-settings.sh organization/repo

set -e

org=$(dirname "$1")
repo=$(basename "$1")

git clone https://github.com/$org/$repo.git
python merge_pre_commit.py --global-config .pre-commit-config.yaml --local-config ${repo}/.github/pre-commit-config-local.yaml
mv generated.yaml ${repo}/.pre-commit-config.yaml
cd ${repo}
git add .pre-commit-config.yaml
git commit -m "Update pre-commit configuration"
git push --quiet

echo "Updated the pre-commit configuration for $repo"
