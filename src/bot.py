import json
import httpx
from html2text import HTML2Text
from pathlib import Path
from collections import defaultdict

from src.config import Config
from src.feed_handler import Feed, Entry
from src.logger import get_logger


# TODO: review send_batch method
# TODO: Implement logging
# TODO: Complete the test suite


class DiscordBot:
    def __init__(self, config: Config, parser: HTML2Text) -> None:
        self.config: Config = config
        self.parser: HTML2Text = parser
        self.sent_items: dict[str, list[str]] = self._load_sent_items()
        self.path: Path = Path.cwd() / f"{config.sent_file}"
        self.logger = get_logger(__name__, config)

    def _load_sent_items(self) -> dict[str, list[str]]:
        """Creates a sent_items.json to store sent entries

        Args:
            None

        Returns:
            dict[str,list[str]]
        """
        if not self.path.is_file():
            self.logger.warning(f"file with name {self.config.sent_file} not found")
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
        self.logger.info(f"added {entry.feed} to {self.config.sent_file}.")
        return self.sent_items[entry.feed].append(entry.id)

    def _save_sent_entry(self) -> None:
        """saves the sent entries to the file json in the path attribute"""
        try:
            with open(file=self.path, mode="w") as file:
                json.dump(self.sent_items, fp=file, indent=4)
            self.logger.info(f"successfully saved to {self.config.sent_file}")
        except IOError as e:
            self.logger.error(
                f"IOError occured when saving to {self.config.sent_file}: {e}"
            )
        except PermissionError as e:
            self.logger.error(
                f"PermissionError occured when saving to {self.config.sent_file}: {e}"
            )

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
        self.logger.info(f"parsing {entry.id}...")
        return self.parser.handle(data=entry.summary).strip()[:2048]

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
                self.logger.info(f"found unsent entry {entry.id}")
                unsent_entries.append(entry)
        return unsent_entries

    def _process_entries(self, entries: list[Entry]) -> list[dict[str, str]]:
        payloads: list[dict[str, str]] = []
        for entry in entries:
            self.logger.info(f"Processing {entry.id}...")
            payload: dict[str, str] = {
                "title": entry.title,
                "link": entry.link,
                "description": self._parse_entry_summary(entry),
            }
            payloads.append(payload)
        return payloads

    def _webhook_lookup(
        self, entries: list[Entry], feeds: list[Feed]
    ) -> dict[str, list[Entry]]:
        """Map entries to their feed webhook_url

        Args:
            entries - list of Entry objects
            feeds - list of Feed objects

        Returns:
            a dictionary that maps the webhook_url to the entries
        """
        feed_map: dict[str, str] = {feed.name: feed.webhook for feed in feeds}
        results: dict[str, list[Entry]] = defaultdict(list)
        for entry in entries:
            webhook: str = feed_map.get(entry.feed, "")
            if webhook:
                results[webhook].append(entry)
        return dict(results)

    async def send_batch(self, entries: list[Entry], feeds: list[Feed]) -> None:
        """send the batch of entries from the feed

        Args:
            entries - list of entry objects

        Returns:
            None
        """
        valid_entries: list[Entry] = self._filter_entries(entries)
        batches: dict[str, list[Entry]] = self._webhook_lookup(
            entries=valid_entries, feeds=feeds
        )
        for webhook_url, entry_list in batches.items():
            payloads = self._process_entries(entry_list)
            async with httpx.AsyncClient() as client:
                try:
                    response: httpx.Response = await client.post(
                        url=webhook_url, json={"embeds": payloads}
                    )
                    response.raise_for_status()
                except httpx.HTTPStatusError as exec:
                    self.logger.warn(
                        f"Error {exec.response.status_code} when making the request"
                    )
