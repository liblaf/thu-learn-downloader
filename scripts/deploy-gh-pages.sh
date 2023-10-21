#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

local_dir=${1:-$PWD}
branch=${2:-"gh-pages"}
origin=$(git remote get-url origin)

temp_dir=$(mktemp --directory)
trap "rm --force --recursive $temp_dir" EXIT
cp --archive --no-target-directory $local_dir $temp_dir

cd $temp_dir
rm --force --recursive "$temp_dir/.git"
git init
git remote add origin $origin
git checkout --orphan $branch
git add --all
git commit --message="ci: deploy to $branch"
git push --force origin $branch
