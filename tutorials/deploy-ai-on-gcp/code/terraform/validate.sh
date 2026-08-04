#!/usr/bin/env bash

set -euo pipefail

module_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/deploy-ai-on-gcp-terraform.XXXXXX")"

cleanup() {
  rm -rf -- "${validation_dir}"
}
trap cleanup EXIT

cp "${module_dir}"/*.tf "${module_dir}"/*.tftpl "${validation_dir}/"

terraform -chdir="${validation_dir}" init \
  -backend=false \
  -input=false \
  -no-color
terraform -chdir="${validation_dir}" validate -no-color
