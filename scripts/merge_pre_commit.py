#!/usr/bin/env python3
"""Render a regular pre-commit configuration from a Key4hep base and overlay.

The generated file is intentionally a conventional .pre-commit-config.yaml:
pre-commit itself never needs to know that it was assembled from two inputs.
"""

import argparse
import copy
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigError(ValueError):
    """Raised when a base or overlay does not follow the merge contract."""


def load_config(path: Path, label: str, require_repos: bool) -> Dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    except FileNotFoundError as error:
        raise ConfigError("{} does not exist: {}".format(label, path)) from error
    except yaml.YAMLError as error:
        raise ConfigError("{} is not valid YAML: {}".format(label, path)) from error

    if config is None:
        config = {}
    if not isinstance(config, dict):
        raise ConfigError("{} must contain a YAML mapping".format(label))

    validate_config(config, label, require_repos=require_repos, is_overlay=not require_repos)
    return config


def validate_config(
    config: Dict[str, Any], label: str, require_repos: bool, is_overlay: bool
) -> None:
    if "repos" not in config:
        if require_repos:
            raise ConfigError("{} must contain a 'repos' list".format(label))
        return

    repositories = config["repos"]
    if not isinstance(repositories, list):
        raise ConfigError("{}: 'repos' must be a list".format(label))

    repository_names = set()
    for repository in repositories:
        if not isinstance(repository, dict):
            raise ConfigError("{}: every repository must be a mapping".format(label))
        name = repository.get("repo")
        if not isinstance(name, str) or not name:
            raise ConfigError("{}: every repository needs a non-empty 'repo'".format(label))
        if name in repository_names:
            raise ConfigError("{}: duplicate repository '{}'".format(label, name))
        repository_names.add(name)

        hooks = repository.get("hooks")
        if not isinstance(hooks, list):
            raise ConfigError("{}: repository '{}' needs a 'hooks' list".format(label, name))

        hook_ids = set()
        for hook in hooks:
            if not isinstance(hook, dict):
                raise ConfigError("{}: hooks in '{}' must be mappings".format(label, name))
            hook_id = hook.get("id")
            if not isinstance(hook_id, str) or not hook_id:
                raise ConfigError("{}: hooks in '{}' need a non-empty 'id'".format(label, name))
            if hook_id in hook_ids:
                raise ConfigError("{}: duplicate hook '{}' in '{}'".format(label, hook_id, name))
            hook_ids.add(hook_id)

            if "disabled" in hook:
                if not is_overlay:
                    raise ConfigError("{}: 'disabled' is only allowed in an overlay".format(label))
                if not isinstance(hook["disabled"], bool):
                    raise ConfigError("{}: 'disabled' must be true or false".format(label))


def clean_hook(hook: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(hook)
    result.pop("disabled", None)
    return result


def merge_existing_repository(
    base_repository: Dict[str, Any], overlay_repository: Dict[str, Any]
) -> None:
    unexpected = set(overlay_repository) - {"repo", "rev", "hooks"}
    if unexpected:
        raise ConfigError(
            "overlay for existing repository '{}' may only contain repo, rev, and hooks; "
            "found {}".format(base_repository["repo"], ", ".join(sorted(unexpected)))
        )

    if "rev" in overlay_repository and overlay_repository["rev"] != base_repository.get("rev"):
        raise ConfigError(
            "overlay for '{}' cannot change the centrally pinned revision".format(
                base_repository["repo"]
            )
        )

    hooks = base_repository["hooks"]
    hooks_by_id = {hook["id"]: hook for hook in hooks}
    disabled_ids = set()

    for overlay_hook in overlay_repository["hooks"]:
        hook_id = overlay_hook["id"]
        if overlay_hook.get("disabled", False):
            if set(overlay_hook) != {"id", "disabled"}:
                raise ConfigError(
                    "disabled hook '{}:{}' may only contain id and disabled".format(
                        base_repository["repo"], hook_id
                    )
                )
            if hook_id not in hooks_by_id:
                raise ConfigError(
                    "cannot disable unknown hook '{}:{}'".format(base_repository["repo"], hook_id)
                )
            disabled_ids.add(hook_id)
            continue

        if hook_id in hooks_by_id:
            hooks_by_id[hook_id].update(clean_hook(overlay_hook))
        else:
            hooks.append(clean_hook(overlay_hook))
            hooks_by_id[hook_id] = hooks[-1]

    if disabled_ids:
        base_repository["hooks"] = [hook for hook in hooks if hook["id"] not in disabled_ids]


def merge_configs(base: Dict[str, Any], overlay: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    if overlay is None:
        return result

    for key, value in overlay.items():
        if key != "repos":
            result[key] = copy.deepcopy(value)

    base_repositories = {repository["repo"]: repository for repository in result["repos"]}
    for overlay_repository in overlay.get("repos", []):
        name = overlay_repository["repo"]
        if name not in base_repositories:
            if any(hook.get("disabled", False) for hook in overlay_repository["hooks"]):
                raise ConfigError("cannot disable a hook in new repository '{}'".format(name))
            new_repository = copy.deepcopy(overlay_repository)
            new_repository["hooks"] = [clean_hook(hook) for hook in new_repository["hooks"]]
            result["repos"].append(new_repository)
            base_repositories[name] = new_repository
            continue
        merge_existing_repository(base_repositories[name], overlay_repository)

    result["repos"] = [repository for repository in result["repos"] if repository["hooks"]]
    validate_config(result, "merged configuration", require_repos=True, is_overlay=False)
    return result


def write_config(config: Dict[str, Any], output: Path) -> None:
    parent = output.parent
    if not parent.is_dir():
        raise ConfigError("output directory does not exist: {}".format(parent))

    contents = (
        "# Generated by scripts/merge_pre_commit.py; do not edit directly.\n"
        + yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
    )
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=str(parent), prefix=".pre-commit-config.", delete=False
        ) as temporary_file:
            temporary_file.write(contents)
            temporary_name = temporary_file.name
        os.replace(temporary_name, output)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--global-config",
        "--base-config",
        dest="global_config",
        required=True,
        type=Path,
        help="Path to the Key4hep base configuration.",
    )
    parser.add_argument(
        "--local-config",
        type=Path,
        help="Optional repository-local overlay configuration.",
    )
    parser.add_argument(
        "--output", required=True, type=Path, help="Generated .pre-commit-config.yaml path."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    try:
        base = load_config(args.global_config, "base configuration", require_repos=True)
        overlay = (
            load_config(args.local_config, "local overlay", require_repos=False)
            if args.local_config
            else None
        )
        write_config(merge_configs(base, overlay), args.output)
    except ConfigError as error:
        print("error: {}".format(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
