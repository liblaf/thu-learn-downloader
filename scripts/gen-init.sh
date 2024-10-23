#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

git_root=$(git rev-parse --show-toplevel)
src_dir=$git_root/src/thu_learn_downloader

readarray -t dpaths < <(find "$src_dir" -type d)
for dpath in "${dpaths[@]}"; do
  if [[ $dpath -ef $src_dir ]]; then
    continue
  fi
  cp "$src_dir/__init__.py" "$dpath/__init__.py"
done
