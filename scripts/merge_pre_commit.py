#!/usr/bin/env python
import yaml
import argparse


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--global-config",
        action="store",
        help="Path to the global pre-commit configuration file.",
    )
    arg_parser.add_argument(
        "--local-config",
        action="store",
        help="Path to the local pre-commit configuration file.",
    )

    args = arg_parser.parse_args()

    key4hep_config = yaml.safe_load(open(args.global_config))
    key4hep_config = key4hep_config["repos"]
    key4hep_names = [elem["repo"] for elem in key4hep_config]
    local_config = yaml.safe_load(open(args.local_config))
    local_config = local_config["repos"]

    for local_elem in local_config:
        current_repo = local_elem["repo"]
        # If the repo doesn't exist then add it
        if current_repo not in key4hep_names:
            key4hep_config.append(local_elem)
            continue
        # Otherwise let's look at the hooks
        key4hep_repo = key4hep_config[key4hep_names.index(current_repo)]
        if any("id" not in hook for hook in key4hep_repo["hooks"]):
            raise RuntimeError(
                f"All hooks in the global config must have an id! Problematic repo: {current_repo}"
            )
        key4hep_ids = [hook["id"] for hook in key4hep_repo["hooks"]]
        for hook in local_elem["hooks"]:
            # print(f'{hook=}')
            # If the hook doesn't exist then add it
            if hook["id"] not in key4hep_ids:
                key4hep_repo["hooks"].append(hook)
                continue
            # Otherwise overwrite the hook
            key4hep_hook = key4hep_repo["hooks"][key4hep_ids.index(hook["id"])]
            key4hep_hook.update(hook)

    key4hep_config = {"repos": key4hep_config}

    yaml.safe_dump(key4hep_config, open("generated.yaml"), "w")


if __name__ == "__main__":
    main()
