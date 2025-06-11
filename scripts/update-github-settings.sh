#!/bin/bash

# This script is used to update Github repository settings for a single repository

# Usage example:
# ./update-github-settings.sh organization/repo

set -e

repo=$1

# The JSON file should contain the repository settings to be applied
# Example: ../defaults/github/github-settings.json

gh api \
  --method PATCH \
  -H "Accept: application/vnd.github+json" \
  /repos/$repo \
  --input ../defaults/github/github-settings.json

echo "Updated repository settings for $repo"
