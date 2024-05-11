#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

export OPENSSL_CONF="openssl.cnf"
args=(tld)
for year in {2020..2023}; do
  for term in {1..3}; do
    semester="${year}-$((year + 1))-${term}"
    args+=(--semester="${semester}")
  done
done
"${args[@]}"
