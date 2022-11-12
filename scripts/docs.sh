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

function prepare() {
  if [[ ! -f "docs/index.md" ]]; then
    call cp "README.md" "docs/index.md"
  fi
}

function build() {
  call poetry run mkdocs build
}

function deploy() {
  call poetry run mkdocs gh-deploy
}

cmd="${1}"
shift 1
case "${cmd}" in
  *)
    "${cmd}" "${@}"
    ;;
esac
