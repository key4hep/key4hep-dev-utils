#!/bin/bash
TOP_DIR=$(git rev-parse --show-toplevel)
source $TOP_DIR/scripts/ci-repo.sh

function git_checkout_and_update_ci {
  prd_list_name=$1[@]
  workflow_file=$2
  prd_list=("${!prd_list_name}")
  for prod in "${prd_list[@]}"; do
    iprd_arr=(${prod})
    prod_name=${iprd_arr[0]//_/-}
    echo "--------------------------------------------------------------"
    echo "********************* $prod_name *****************************"
    git clone --quiet git@github.com:key4hep/${prod_name}.git --depth 1
    pushd ${prod_name}
    cp $workflow_file .github/workflows
    git add .github/workflows
    old_message=`git log -1|grep -v "^commit"`
    git commit -am "syncing $(basename $workflow_file); previous commit: ${old_message}"
    git push --quiet
    popd
  done
}

tmp_dir=$(mktemp -d -t tmp_XXXXXXXXXX)

pushd $tmp_dir

git clone --depth 1 git@github.com:key4hep/key4hep-actions.git

git_checkout_and_update_ci packages_with_ci $PWD/key4hep-actions/workflows/downstream-build.yaml

popd

rm -rf $tmp_dir
