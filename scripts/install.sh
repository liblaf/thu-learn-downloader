#!/usr/bin/bash
set -o errexit
set -o nounset
set -o pipefail

if command -v rich > /dev/null 2>&1; then
  function info() {
    rich --print "[bold bright_blue]${*}"
  }
else
  function info() {
    echo -e -n "\x1b[1;94m"
    echo -n "${*}"
    echo -e "\x1b[0m"
  }
fi

function call() {
  info "+ ${*}"
  "${@}"
}

REPO_HOME="$(realpath --canonicalize-missing "${0}/../..")"
call cd "${REPO_HOME}"
call poetry run build
mkdir --parents "${HOME}/.local/bin"
call cp "${REPO_HOME}/dist/$(basename "${REPO_HOME}")" "${HOME}/.local/bin"
