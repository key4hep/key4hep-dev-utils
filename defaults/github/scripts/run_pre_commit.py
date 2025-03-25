#!/usr/bin/env python
import os
import sys
import yaml
import subprocess

HERE = os.path.dirname(os.path.realpath(__file__))


def main():
    key4hep_config = yaml.safe_load(
        open(os.path.join(HERE, "../workflows/.pre-commit-config-key4hep.yaml"))
    )
    if os.path.exists(os.path.join(HERE, "../workflows/.pre-commit-config-local.yaml")):
        key4hep_config = key4hep_config["repos"]
        key4hep_names = [elem["repo"] for elem in key4hep_config]
        local_config = yaml.safe_load(open(os.path.join(HERE, "../workflows/.pre-commit-config-local.yaml")))
        local_config = local_config["repos"]
        for local_elem in local_config:
            current_repo = local_elem["repo"]
            # If the repo doesn't exist then add it
            if current_repo not in key4hep_names:
                key4hep_config.append(local_elem)
                continue
            # Otherwise let's look at the hooks
            key4hep_repo = key4hep_config[key4hep_names.index(current_repo)]
            key4hep_ids = [elem["id"] for elem in key4hep_repo["hooks"]]
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
    else:
        print(
            "No local config found for this repository. Using the Key4hep default configuration."
        )
    yaml.safe_dump(key4hep_config, open(os.path.join(HERE, "generated.yaml"), "w"))

    cfg = os.path.join(HERE, "generated.yaml")
    cmd = ["pre-commit", "run", "--config", cfg, "--all-files", "--show-diff-on-failure", "--color=always"]

    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    sys.exit(main())
