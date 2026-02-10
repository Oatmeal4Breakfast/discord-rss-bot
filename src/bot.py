import json
from html2text import HTML2Text
from pathlib import Path

from src.config import Config, config
from src.feed_handler import FeedData, FeedHandler, Feed, Entry


class DiscordBot:
    def __init__(self, config: Config, parser: HTML2Text) -> None:
        self.config: Config = config
        self.parser: HTML2Text = parser
        self.sent_items: list[dict[str, str]] = self._load_sent_items()
        
    def _load_sent_items(self) -> None:
        """
        loads the json for the sent entries
        """
        sent_items: Path = Path.cwd() / "sent_items.json"
        with open(file=sent_items, mode="r") as file:
            sent_items = json.load(file)
            self.sent_items.append(sent_items)


    def _parse_html(self, description_html: str) -> str:
        """
        Parse the html in the description of the entry to send plain ASCII strings to Discord
        """
        return self.parser.handle(data=description_html)

    def _validate_entries(self, entries: FeedEntries) -> FeedEntries:
        valid_entries: FeedEntries = []
        for entry in entries:
            if entry not in self.sent_items:
                valid_entries.append(entry)
        return valid_entries

    def send_batch(self, entries: FeedEntries, feed_name: str) -> None:
        """
        send the batch of entries from the feed
        """

        valid_entries: FeedEntries = self._validate_entries(entries)
        for entry in valid_entries:

        # TODO: Workout logic needed for processing. Maybe split up th processing to another method
