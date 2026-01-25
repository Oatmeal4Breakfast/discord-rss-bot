import yaml
from pathlib import Path
from typing import Any

script_dir: Path = Path.cwd()
config_path: Path = script_dir / "config.yaml"


def load_config(config_file: Path | str) -> dict[str, Any]:
    """
    returns yaml object from the config file
    """

    with open(config_file, mode="r") as file:
        return yaml.safe_load(stream=file)


if __name__ == "__main__":
    print(config_path)
    config = load_config(config_path)
    print(config)
