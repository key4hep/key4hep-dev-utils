#!/bin/bash
set -e

repo=$1

# The name has to match the one in the ruleset file
id=$(gh api \
  -H "Accept: application/vnd.github+json" \
  /repos/$repo/rulesets | jq '.[] | select(.name == "Default branch (Key4hep)") | .id')

if [ -z "$id" ]; then
  echo "No default branch ruleset found"
else
  gh api \
    --method DELETE \
    -H "Accept: application/vnd.github+json" \
    /repos/$repo/rulesets/$id
fi

out=$(gh api\
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/$repo/rulesets \
  --input ../defaults/github/default-branch-ruleset.json)

echo "Added default branch ruleset to $repo"
