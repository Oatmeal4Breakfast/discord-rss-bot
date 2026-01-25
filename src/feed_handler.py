import feedparser
from feedparser import FeedParserDict
from models import Entry


def fetch_feed_entries(url: str, max_items: int = 5) -> list[Entry]:
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
    entries = fetch_feed_entries(url="https://www.reddit.com/r/FastAPI/.rss")
    print(entries)
