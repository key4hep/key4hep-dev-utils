import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts" / "merge_pre_commit.py"
SPEC = importlib.util.spec_from_file_location("merge_pre_commit", SCRIPT)
MERGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MERGER)


class MergePreCommitTests(unittest.TestCase):
    def test_merges_hook_overrides_additions_and_disabling(self):
        base = {
            "default_language_version": {"python": "python3"},
            "repos": [
                {
                    "repo": "https://example.invalid/hooks",
                    "rev": "v1.0.0",
                    "hooks": [
                        {"id": "format", "args": ["--base"]},
                        {"id": "remove-me"},
                    ],
                },
                {"repo": "local", "hooks": [{"id": "clang-format", "entry": "clang-format -i"}]},
            ],
        }
        overlay = {
            "minimum_pre_commit_version": "3.0.0",
            "repos": [
                {
                    "repo": "https://example.invalid/hooks",
                    "rev": "v1.0.0",
                    "hooks": [
                        {"id": "format", "exclude": "generated/"},
                        {"id": "remove-me", "disabled": True},
                    ],
                },
                {
                    "repo": "local",
                    "hooks": [{"id": "readme-links", "entry": "python check_links.py"}],
                },
                {
                    "repo": "https://example.invalid/project-hooks",
                    "rev": "v2.0.0",
                    "hooks": [{"id": "project-check"}],
                },
            ],
        }

        result = MERGER.merge_configs(base, overlay)

        self.assertEqual(result["minimum_pre_commit_version"], "3.0.0")
        hooks = result["repos"][0]["hooks"]
        self.assertEqual(hooks, [{"id": "format", "args": ["--base"], "exclude": "generated/"}])
        self.assertEqual(result["repos"][1]["hooks"][-1]["id"], "readme-links")
        self.assertEqual(result["repos"][2]["repo"], "https://example.invalid/project-hooks")

    def test_rejects_changing_a_centrally_pinned_revision(self):
        base = {
            "repos": [
                {"repo": "https://example.invalid/hooks", "rev": "v1.0.0", "hooks": [{"id": "check"}]}
            ]
        }
        overlay = {
            "repos": [
                {"repo": "https://example.invalid/hooks", "rev": "v2.0.0", "hooks": [{"id": "check"}]}
            ]
        }

        with self.assertRaisesRegex(MERGER.ConfigError, "cannot change"):
            MERGER.merge_configs(base, overlay)

    def test_writer_creates_a_regular_yaml_file(self):
        config = {"repos": [{"repo": "local", "hooks": [{"id": "check", "entry": "true"}]}]}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / ".pre-commit-config.yaml"
            MERGER.write_config(config, output)
            self.assertTrue(output.read_text(encoding="utf-8").startswith("# Generated"))
            self.assertEqual(yaml.safe_load(output.read_text(encoding="utf-8")), config)


if __name__ == "__main__":
    unittest.main()
