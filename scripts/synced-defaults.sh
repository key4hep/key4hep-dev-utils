#!/usr/bin/env bash

# Source:destination mappings for files maintained in defaults/. Destinations are
# relative to each package repository.
synced_default_files=(
  '.clang-format:.clang-format'
  'cmake/Key4hepConfig.cmake:cmake/Key4hepConfig.cmake'
)

# Package:source entries for defaults that do not apply to a package. Keep this
# list explicit: a missing file is otherwise treated as a synchronization error.
synced_default_exclusions=(
  'key4hep/CLDConfig:.clang-format'
  'key4hep/CLDConfig:cmake/Key4hepConfig.cmake'
)

is_synced_default_excluded() {
  local package="$1"
  local default_file="$2"
  local exclusion
  for exclusion in "${synced_default_exclusions[@]}"; do
    [[ "${exclusion}" == "${package}:${default_file}" ]] && return 0
  done
  return 1
}
