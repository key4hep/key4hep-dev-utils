#!/usr/bin/env bash

# Render the Key4hep pre-commit policy for one repository without changing it.

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: update-pre-commit-config.sh <organization/repository> [options]

Options:
  --run-all-files      Also run pre-commit on every file before finishing.
  -h, --help           Show this help message.

The optional target-repository overlay is .pre-commit-config.local.yaml.
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -lt 1 ]]; then
    usage >&2
    exit 2
fi

repository=$1
shift
run_all_files=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --run-all-files)
            run_all_files=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown option '$1'" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

if [[ ! $repository =~ ^[^/[:space:]]+/[^/[:space:]]+$ ]]; then
    echo "error: repository must be in organization/repository form" >&2
    exit 2
fi

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root_dir=$(cd "$script_dir/.." && pwd)

for command in git python3 pre-commit; do
    if ! command -v "$command" >/dev/null; then
        echo "error: required command not found: $command" >&2
        exit 2
    fi
done

workspace=$(mktemp -d -t key4hep-pre-commit.XXXXXXXXXX)
cleanup() {
    rm -rf "$workspace"
}
trap cleanup EXIT
checkout="$workspace/$(basename "$repository")"

git clone --quiet "https://github.com/${repository}.git" "$checkout"

overlay=""
if [[ -f "$checkout/.pre-commit-config.local.yaml" ]]; then
    overlay="$checkout/.pre-commit-config.local.yaml"
fi

render_command=(
    python3 "$script_dir/merge_pre_commit.py"
    --global-config "$root_dir/defaults/.pre-commit-config-key4hep.yaml"
    --output "$checkout/.pre-commit-config.yaml"
)
if [[ -n $overlay ]]; then
    render_command+=(--local-config "$overlay")
fi
"${render_command[@]}"

pre-commit validate-config "$checkout/.pre-commit-config.yaml"

if [[ -z $(git -C "$checkout" status --porcelain -- .pre-commit-config.yaml) ]]; then
    echo "$repository is already up to date"
    exit 0
fi

if git -C "$checkout" ls-files --error-unmatch .pre-commit-config.yaml >/dev/null 2>&1; then
    git -C "$checkout" diff -- .pre-commit-config.yaml
else
    git -C "$checkout" diff --no-index -- /dev/null .pre-commit-config.yaml || true
fi

if [[ $run_all_files == true ]]; then
    (
        cd "$checkout"
        pre-commit run --all-files --show-diff-on-failure
    )
fi

echo "No remote changes were made."
