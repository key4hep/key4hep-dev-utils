#!/bin/bash

# This script is used to sync files from to the destination in
# all the repositories in /key4hep-dev-utils/scripts/get_packages.sh

# Usage example:
# ./sync-files.sh /path/to/destination/ /absolute/path/to/file1 /absolute/path/to/file2
# Set SYNC_PACKAGES to a whitespace-separated list of owner/repository names to
# sync only those packages.


TOP_DIR=$(git rev-parse --show-toplevel)
source $TOP_DIR/scripts/get_packages.sh
source $TOP_DIR/scripts/synced-defaults.sh

if [[ -n "${SYNC_PACKAGES:-}" ]]; then
  read -r -a packages <<< "${SYNC_PACKAGES}"
fi


function git_checkout_and_update {
  packages_list_name=$1[@]
  destination=$2
  files_to_sync=("${@:3}")
  packages_list=("${!packages_list_name}")
  for package_name in "${packages_list[@]}"; do
    echo "Syncing package $package_name"
    git clone --quiet git@github.com:${package_name}.git --depth 1
    pushd $(basename $package_name)
    for file in "${files_to_sync[@]}"; do
      default_file=""
      if [[ "$file" == "$TOP_DIR/defaults/"* ]]; then
        default_file="${file#"$TOP_DIR/defaults/"}"
      fi
      if [[ -n "$default_file" ]] && is_synced_default_excluded "$package_name" "$default_file"; then
        echo "Skipping $default_file for $package_name (not applicable)"
        continue
      fi
      cp $file $destination
      git add $destination/$(basename $file)
    done
    old_message=$(git log -1 --format=%s)
    git commit -am "Run the key4hep build workflow on ubuntu 24"
    git push --quiet
    popd
  done
}

tmp_dir=$(mktemp -d -t tmp_XXXXXXXXXX)

pushd $tmp_dir

files=("${@:2}")
dest=$1

echo "Will sync the following files to $dest"
for file in "${files[@]}"; do
  echo $file
done

git_checkout_and_update packages $dest "${files[@]}"

popd

rm -rf $tmp_dir
