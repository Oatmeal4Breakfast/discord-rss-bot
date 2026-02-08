import feedparser
import yaml
from pathlib import Path
from feedparser import FeedParserDict

from src.models import Entry


class FeedHandler:
    def __init__(self) -> None:
        self.feeds_file: Path = Path.cwd() / "feeds.yaml"

    def load_feed(self) -> dict[str, str]:
        """
        returns yaml object from the feeds file
        """
        try:
            with open(file=self.feeds_file, mode="r") as file:
                return yaml.safe_load(stream=file)
        except FileNotFoundError:
            raise
        except FileExistsError:
            raise

    def fetch_feed_entries(self, url: str, max_items: int = 5) -> list[Entry]:
        """
        Fetch entries from the feed up to the max items set in the config.
        Defaults to 5

        Returns a list of entries
        """
        feed: FeedParserDict = feedparser.parse(url_file_stream_or_string=url)
        entries: list[Entry] = []
        for entry in feed.entries[:max_items]:
            new_entry: Entry = Entry(
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
    feeds_handler = FeedHandler()
    entries: list[Entry] = feeds_handler.fetch_feed_entries(
        url="https://www.reddit.com/r/FastAPI/.rss"
    )
    print(entries)
    print(len(entries))
