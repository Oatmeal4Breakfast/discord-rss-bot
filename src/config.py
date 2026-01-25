import yaml
from pathlib import Path
from typing import Any, Tuple, List, Dict
from models import Config

script_dir: Path = Path.cwd()
config_path: Path = script_dir / "config.yaml"

type FeedItems = List[Dict[str, str]]


def load_config(config_file: Path | str) -> dict[str, Any]:
    """
    returns yaml object from the config file
    """

    try:
        with open(config_file, mode="r") as file:
            return yaml.safe_load(stream=file)
    except FileNotFoundError:
        raise
    except FileExistsError:
        raise


def parse_config(config_file: dict[str, Any]) -> Tuple[Config, FeedItems]:
    """
    Parse the config object return by the load function and return
    feeds and return config object
    """
    config: Config = Config(
        default_webhook=config_file.get("default_webhook", ""),
        rate_limit_delay=config_file.get("rate_limit_delay", 0.5),
        batch_size=config_file.get("batch_size", 5),
        filter_by_today=config_file.get("filter_by_today", True),
    )

    feed_items: FeedItems = config_file.get("feeds", [])

    return config, feed_items


if __name__ == "__main__":
    print(config_path)
    config = load_config(config_path)
    print(config)
