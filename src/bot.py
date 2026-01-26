from html2text import HTML2Text

from src.models import Config, FeedEntries


class DiscordBot:
    def __init__(self, config: Config, parser: HTML2Text) -> None:
        self.config: Config = config
        self.parser: HTML2Text = parser

    def _parse_html(self, description_html: str) -> str:
        """
        Parse the html in the description of the entry to send plain ASCII strings to Discord
        """
        return self.parser.handle(data=description_html)

    def _validate_entries(self, entries: FeedEntries) -> FeedEntries:
        # TODO: figure out the storage for the sent items. SQLITE? JSON?
        valid_entries: FeedEntries = []
        for entry in entries:
            if entry not in sent_list:
                valid_entries.append(entry)
        return valid_entries

    def send_batch(self, entries: FeedEntries, feed_name: str) -> None:
        """
        send the batch of entries from the feed
        """

        valid_entries: FeedEntries = self._validate_entries(entries)
        for entry in valid_entries:

        # TODO: Workout logic needed for processing. Maybe split up th processing to another method
