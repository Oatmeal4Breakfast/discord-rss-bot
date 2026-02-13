import json
import httpx
from html2text import HTML2Text
from pathlib import Path
from dataclasses import asdict

from src.config import Config
from src.feed_handler import FeedData, FeedHandler, Feed, Entry


# TODO: Work out the logic for processing

# TODO: Complete the send patch implementation


class DiscordBot:
    def __init__(self, config: Config, parser: HTML2Text) -> None:
        self.config: Config = config
        self.parser: HTML2Text = parser
        self.sent_items: dict[str, list[str]] = self._load_sent_items()
        self.path: Path = Path.cwd() / f"{config.sent_file}"

    def _load_sent_items(self) -> dict[str, list[str]]:
        """Creates a sent_items.json to store sent entries

        Args:
            None

        Returns:
            dict[str,list[str]]
        """
        if not self.path.is_file():
            return {}

        with open(file=self.path, mode="r") as file:
            return json.load(file)

    def _add_sent_entry(self, entry: Entry) -> None:
        """Adds an entry to the sent_items parameter

        Args:
            entry of type Entry

        Returns:
            None
        """
        return self.sent_items[entry.feed].append(entry.id)

    def _save_sent_entry(self) -> None:
        """saves the sent entries to the file json in the path attribute"""
        try:
            with open(file=self.path, mode="w") as file:
                json.dump(self.sent_items, fp=file, indent=4)
        except IOError:
            print("Log: Could not write to file")
        except PermissionError:
            print("Invalid permissions for file system")

    def _prune_sent_entries(self) -> None:
        """Prune the first 10 entries from the list of sent entries"""
        MAX_BEFORE_PRUNE: int = 100
        PRUNE_AMOUNT: int = 10
        for feed, sent_items in self.sent_items.items():
            if len(sent_items) >= MAX_BEFORE_PRUNE:
                del sent_items[:PRUNE_AMOUNT]

    def _parse_entry_summary(self, entry: Entry) -> str:
        """Parse the html in the description of the entry to send plain ASCII strings to Discord

        Args:
            entry: Entry object

        Returns:
            str
        """
        return self.parser.handle(data=entry.summary)

    def _filter_entries(self, entries: list[Entry]):
        """check the entry id against the list of sent entries

        Args:
            entries - list containing entry objects

        Returns:
            a filtered list of entries that haven't been sent yet
        """
        unsent_entries: list[Entry] = []
        for entry in entries:
            if entry.id not in self.sent_items[entry.feed]:
                unsent_entries.append(entry)
        return unsent_entries

    async def send_batch(self, entries: list[Entry]) -> None:
        """send the batch of entries from the feed

        Args:
            entries - list of entry objects

        Returns:
            None
        """
        valid_entries: list[Entry] = self._filter_entries(entries)
        for entry in valid_entries:
            async with httpx.AsyncClient() as client:
                raise NotImplementedError
