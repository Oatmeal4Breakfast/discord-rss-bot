import feedparser
import yaml
from pathlib import Path
from feedparser import FeedParserDict
from dataclasses import dataclass

feeds_pathh: Path | str = Path.cwd() 

# TODO: Add default feeds yaml file to method for fetching entries
# TODO: use the Feed Dataclass to clean up the data that I'll be extracting from each list items
# TODO: Implement storage feature. Use a JSON that stores the title, the feed it was sent from, and when it was sent
# TODO: Implement feature to read and save to the aforementioned file


@dataclass
class Feed:
    name: str
    url: str
    webhook: str


@dataclass
class Entry:
    title: str
    link: str
    published: str
    summary: str


@dataclass
class FeedHandler:
    feeds: list[str] = self.load_feeds() # Fix this bug. Need to learn out to implement the call. 
    sent_entries: list[str]
    def load_feeds(self, feeds_file: Path | str = ) -> dict[str, str] | None:

        """
        returns yaml object from the feeds file
        """
        try:
            with open(file=feeds_file, mode="r") as file:
                file_data: dict[str, str] = yaml.safe_load(stream=file)
        except FileNotFoundError:
            raise
        except FileExistsError:
            raise

    def fetch_feed_entries(self, feed_url: str, max_items: int = 5) -> list[Entry]:
        """
        Fetch entries from the feed up to the max items set in the config.
        Defaults to 5

        Returns a list of entries
        """
        feed: FeedParserDict = feedparser.parse(url_file_stream_or_string=feed_url)
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
    entries: list[Entry] = fetch_feed_entries(
        url="https://www.reddit.com/r/FastAPI/.rss"
    )
    print(entries)
    print(len(entries))
