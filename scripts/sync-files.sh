#!/bin/bash

# This script is used to sync files from to the destination in
# all the repositories in /key4hep-dev-utils/scripts/get_packages.sh

# Usage example:
# ./sync-files.sh /path/to/destination/ /absolute/path/to/file1 /absolute/path/to/file2


TOP_DIR=$(git rev-parse --show-toplevel)
source $TOP_DIR/scripts/get_packages.sh


function git_checkout_and_update {
  packages_list_name=$1[@]
  destination=$2
  files_to_sync=("${@:3}")
  packages_list=("${!packages_list_name}")
  for package_name in "${packages_list[@]}"; do
    echo "Syncing package $package_name"
    git clone --quiet git@github.com:${package_name}.git --depth 1
    pushd ${package_name}
    for file in "${files_to_sync[@]}"; do
      cp $file $destination
      git add $destination/$(basename $file)
    done
    old_message=$(git log -1 --format=%s)
    git commit -am "Syncing $(basename $files_to_sync); previous commit: ${old_message}"
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
