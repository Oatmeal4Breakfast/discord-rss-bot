import feedparser
import yaml
import uuid

from pathlib import Path
from feedparser import FeedParserDict
from dataclasses import dataclass

from src.config import Config


@dataclass
class Feed:
    name: str
    url: str
    webhook: str


@dataclass
class Entry:
    id: str
    feed: str
    title: str
    link: str
    summary: str


type FeedData = dict[str, list[dict[str, str]]]


class FeedHandler:
    def __init__(self, config: Config) -> None:
        self.feeds_file: Path = Path.cwd() / f"{config.feed_file}"

    def _load_feeds(self) -> FeedData:
        """Loads feeds from feed_file
        Returns:
            yaml object from the feeds file
        """
        try:
            with open(file=self.feeds_file, mode="r") as file:
                data: list[dict[str, str]] = yaml.safe_load(stream=file)
                return data
        except FileNotFoundError:
            raise RuntimeError("Unable to locate feeds.yaml file")

    def extract_feeds(self) -> list[Feed]:
        """creates a data structure for the list to work with later

        Raises:
            RuntimeError if there is no feeds.yaml file
        """
        data: FeedData = self._load_feeds()
        feeds: list[Feed] = []
        for item in data["feeds"]:
            name: str = item.get("name", "")
            url: str = item.get("url", "")
            webhook: str = item.get("webhook", "")

            if any(not s for s in [name, url, webhook]):
                print("Log: incomplete Feed object")
                continue

            feed: Feed = Feed(name=name, url=url, webhook=webhook)
            feeds.append(feed)

        if not feeds:
            raise RuntimeError("No feeds found in feeds.yaml")
        return feeds

    def fetch_feed_entries(self, feed: Feed, max_entries: int = 5) -> list[Entry]:
        """Fetch entries from the feed up to the max items in the config

        Args:
            feed_url: str - url of the feed
            max_entries: int - max number of entries you would like. Defaults to 5

        Returns:
            list[Entry]
        """
        parsed_feed: FeedParserDict = feedparser.parse(
            url_file_stream_or_string=feed.url
        )
        entries: list[Entry] = []
        for entry in parsed_feed.entries[:max_entries]:
            new_entry: Entry = Entry(
                id=str(uuid.uuid4()),
                feed=feed.name,
                title=entry.title,
                link=entry.link,
                summary=entry.summary if "summary" in entry else "",
            )
            entries.append(new_entry)
        if parsed_feed.bozo:
            return []
        return entries


if __name__ == "__main__":
    from src.config import config
    from dataclasses import asdict

    handler: FeedHandler = FeedHandler(config=config)
    feeds: list[Feed] = handler.extract_feeds()
    entries: list[Entry] = handler.fetch_feed_entries(feed=feeds[0])
    print(asdict(entries[0]))
    print(len(entries))
