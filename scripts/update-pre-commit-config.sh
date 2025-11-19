#!/bin/bash

# This script is used to update the pre-commit configuration for a single repository

# Usage example:
# ./update-pre-commit-settings.sh organization/repo

set -e

org=$(dirname "$1")
repo=$(basename "$1")

git clone https://github.com/$org/$repo.git
if [ -f ${repo}/.github/pre-commit-config-local.yaml ]; then
    python merge_pre_commit.py --global-config ../defaults/.pre-commit-config-key4hep.yaml --local-config ${repo}/.github/pre-commit-config-local.yaml
    mv generated.yaml ${repo}/.pre-commit-config.yaml
else
    echo "No local pre-commit configuration found for $repo, using the default one."
    cp ../defaults/..pre-commit-config.yaml ${repo}/.pre-commit-config.yaml
fi
cd ${repo}
git add .pre-commit-config.yaml
git commit -m "Update pre-commit configuration"
# git push --quiet

echo "Updated the pre-commit configuration for $repo"
