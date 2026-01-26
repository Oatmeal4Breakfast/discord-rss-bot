import yaml
from pathlib import Path
from typing import Any, Tuple
from src.models import Config, FeedEntries

script_dir: Path = Path.cwd()
config_path: Path = script_dir / "config.yaml"


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


def parse_config(loaded_config: dict[str, Any]) -> Tuple[Config, FeedEntries]:
    """
    Parse the config object return by the load function and return
    feeds and return config object
    """
    config: Config = Config(
        default_webhook=loaded_config.get("default_webhook", ""),
        rate_limit_delay=loaded_config.get("rate_limit_delay", 0.5),
        batch_size=loaded_config.get("batch_size", 5),
        filter_by_today=loaded_config.get("filter_by_today", True),
    )

    feed_items: FeedEntries = loaded_config.get("feeds", [])

    return config, feed_items


if __name__ == "__main__":
    print(f"config path: {config_path}")
    print("loading config file now....")
    loaded_config = load_config(config_path)
    print(f"raw config object: {loaded_config}")
    print("=" * 50)
    config, feed_items = parse_config(loaded_config)
    print(f"Config: {config}")
    print("=" * 50)
    print(f"feed_items: {feed_items}")
