#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

BIN="${BIN:-"${HOME}/.local/bin"}"

function run() {
  if command -v gum > /dev/null 2>&1; then
    prefix="$(gum style --background=14 --padding="0 1" RUN)"
    message="$(gum style --foreground=14 "${*}")"
    gum join --horizontal "${prefix}" " " "${message}"
  fi
  "${@}"
}

function copy() {
  mkdir --parents "$(dirname "${2}")"
  cp "${1}" "${2}"
  if command -v gum > /dev/null 2>&1; then
    prefix="$(gum style --background=10 --padding="0 1" COPY)"
    message="$(gum style --foreground=10 "${1} -> ${2}")"
    gum join --horizontal "${prefix}" " " "${message}"
  fi
}

workspace="$(git rev-parse --show-toplevel || pwd)"
cd "${workspace}"
name="$(poetry version | awk '{ print $1 }')"

run bash "${workspace}/scripts/build.sh"
copy "${workspace}/dist/${name}" "${BIN}/${name}"
