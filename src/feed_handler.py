import feedparser
import yaml
import uuid

from pathlib import Path
from feedparser import FeedParserDict
from dataclasses import dataclass

from src.config import Config


type FeedData = list[dict[str, str]]


@dataclass
class Feed:
    name: str
    url: str
    webhook: str


@dataclass
class Entry:
    id: str
    title: str
    link: str
    published: str
    summary: str


class FeedHandler:
    def __init__(self, config: Config) -> None:
        self.feeds_file: Path = Path.cwd() / f"{config.feed_file}"
        self.feeds: list[Feed] = []

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
            raise

    def extract_feeds(self) -> None:
        """creates a data structure for the list to work with later

        Raises:
            RuntimeError if there is no feeds.yaml file
        """

        data: FeedData = self._load_feeds()
        for item in data:
            values: list[str] = [value for value in item.values()]
            if None in values:
                print("Log: incomplete Feed object")
                continue
            feed: Feed = Feed(
                name=item.get("name", ""),
                url=item.get("url", ""),
                webhook=item.get("webhook", ""),
            )
            self.feeds.append(feed)
        if not len(self.feeds) >= 0:
            raise RuntimeError("No feeds found in feeds.yaml")

    def fetch_feed_entries(self, feed_url: str, max_entries: int = 5) -> list[Entry]:
        """Fetch entries from the feed up to the mac items in the config

        Args:
            feed_url: str - url of the feed
            max_entries: int - max number of entries you would like. Defaults to 5

        Returns:
            list[Entry]
        """
        feed: FeedParserDict = feedparser.parse(url_file_stream_or_string=feed_url)
        entries: list[Entry] = []
        for entry in feed.entries[:max_entries]:
            new_entry: Entry = Entry(
                id=str(uuid.uuid4()),
                title=entry.title,
                link=entry.link,
                published=entry.published,
                summary=entry.summary if "summary" in entry else "",
            )
            entries.append(new_entry)
        if feed.bozo:
            return []
        return entries


if __name__ == "__main__":
    from src.config import config
    from dataclasses import asdict

    handler: FeedHandler = FeedHandler(config=config)
    entries: list[Entry] = handler.fetch_feed_entries(
        feed_url="https://www.reddit.com/r/FastAPI/.rss"
    )
    print(asdict(entries[0]))
    print(len(entries))
