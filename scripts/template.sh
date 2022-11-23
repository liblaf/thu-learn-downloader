#!/usr/bin/bash
set -o errexit
set -o nounset
set -o pipefail

function exists() {
  command -v "${@}" > /dev/null 2>&1
}

function info() {
  if exists rich; then
    rich --print --style "bold bright_blue" "${*}"
  else
    echo -e -n "\x1b[1;94m"
    echo -n "${*}"
    echo -e "\x1b[0m"
  fi
}

function call() {
  info "+ ${*}"
  "${@}"
}

cd "$(git rev-parse --show-toplevel || echo .)"
REPO_NAME="$(basename "$(pwd)")"

description="${*}"
echo "# ${REPO_NAME}" > "README.md"
if [[ -n ${description} ]]; then
  echo "" >> "README.md"
  echo "${description}" >> "README.md"
fi

files=(
  "mkdocs.yaml"
  "pyproject.toml"
)
for file in "${files[@]}"; do
  call sed --in-place "s@template@${REPO_NAME}@g" "${file}"
done

call sed --in-place "s@description =.*@description = \"${description}\"@g" pyproject.toml

call gh repo edit --description "${description}"
call gh repo edit --homepage "https://liblaf.github.io/${REPO_NAME}/"

call git add --all
call git commit --message "build: initialize" --gpg-sign
call git push
