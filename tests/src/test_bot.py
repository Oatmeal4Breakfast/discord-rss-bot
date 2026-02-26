from typing import Iterator
import pytest
import json

from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

from src.bot import DiscordBot
from src.feed_handler import Entry, Feed


@pytest.fixture
def fake_feed() -> Feed:
    return Feed(
        name="fake_feed", url="https://example.com", webhook="https://webhook_url.com"
    )


@pytest.fixture
def fake_sent_items(tmp_path) -> Iterator[Path]:
    file_path: Path = tmp_path / "sent.json"
    file_path.write_text(json.dumps({"TechCrunch": ["id1", "id2", "id3"]}))
    yield file_path

    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def bot(fake_sent_items, tmp_path) -> DiscordBot:
    config = MagicMock()
    config.sent_file: str = str(fake_sent_items)
    config.log_level: str = "DEBUG"
    config.log_file: str = str(tmp_path / "test.log")
    config.retry_count = 3
    return DiscordBot(config=config)


@pytest.fixture
def fake_entry() -> Entry:
    return Entry(
        id="id4",
        feed="fake_feed",
        title="Fake Hacker News",
        link="https://fake_hacker_news.com",
        summary="<p> fake news <\\p>",
    )


class TestDiscordBot:
    def test_load_sent_items(self, bot) -> None:
        bot._load_sent_items()

        assert isinstance(bot.sent_items, dict)
        assert bot.sent_items == {"TechCrunch": ["id1", "id2", "id3"]}

    def test_load_sent_items_no_sent_file(self, tmp_path) -> None:
        config = MagicMock()
        config.sent_file: str = "file_dne.json"
        config.log_level = "DEBUG"
        config.log_file: str = str(tmp_path / "test.log")
        bot = DiscordBot(config=config)

        bot._load_sent_items()

        assert isinstance(bot.sent_items, dict)
        assert len(bot.sent_items) == 0

    def test_add_sent_entry(self, fake_entry, bot) -> None:
        bot._add_sent_entry(fake_entry)

        assert bot.sent_items.get(fake_entry.feed)
        assert bot.sent_items.get(fake_entry.feed) == ["id4"]

    def test_parse_entry_summary(self, fake_entry, bot) -> None:
        fake_entry.summary += fake_entry.summary * 2048
        parsed_summary: str = bot._parse_entry_summary(fake_entry)

        assert len(parsed_summary) <= 2048
        assert parsed_summary[0] != " "
        assert parsed_summary[-1] != " "

    def test_filter_entries_entry_not_in_list(self, fake_entry, bot) -> None:
        unsent_entries: list[Entry] = bot._filter_entries([fake_entry])

        assert fake_entry in unsent_entries

    def test_filter_entries_entry_in_list(self, fake_entry, bot) -> None:
        bot._load_sent_items()
        bot._add_sent_entry(fake_entry)

        unsent_entries: list[Entry] = bot._filter_entries([fake_entry])

        assert not unsent_entries

    def test_process_entries(self, fake_entry, bot) -> None:
        payloads: list[dict[str, str]] = bot._process_entries([fake_entry])

        assert payloads
        assert payloads[0].get("title") == fake_entry.title
        assert payloads[0].get("url") == fake_entry.link
        assert payloads[0].get("description") == bot._parse_entry_summary(fake_entry)

    def test_webhook_lookup(self, fake_entry, fake_feed, bot) -> None:
        results: dict[str, list[Entry]] = bot._webhook_lookup([fake_entry], [fake_feed])

        assert isinstance(results, dict)
        assert isinstance(results.get(fake_feed.webhook), list)

        entries = results.get(fake_feed.webhook)
        assert fake_entry in entries

    @pytest.mark.asyncio
    async def test_send_with_retry(self, bot) -> None:
        rate_limited = MagicMock()
        rate_limited.status_code = 429
        rate_limited.headers: dict[str, int] = {"retry_after": 1000}

        success = MagicMock()
        success.status_code = 200

        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=[rate_limited, success])

        with patch("src.bot.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client

            result = await bot._send_with_retry(
                "https://webhook.url", {"title": "test"}
            )

            assert result == 200
            assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_send_with_retry_no_retry_needed(self, bot) -> None:
        success = MagicMock()
        success.status_code = 200

        mock_client = AsyncMock()
        mock_client.post.return_value = success

        with patch("src.bot.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            result = await bot._send_with_retry(
                "https://webhook.url", {"title": "test"}
            )

        assert result == 200
        assert mock_client.post.call_count == 1

    def test_prune_sent_entries_under_threshold(self, bot) -> None:
        bot.sent_items = {"FeedA": [f"id{i}" for i in range(50)]}

        bot.prune_sent_entries()

        assert len(bot.sent_items["FeedA"]) == 50

    def test_prune_sent_entries_over_threshold(self, bot) -> None:
        bot.sent_items = {"FeedA": [f"id{i}" for i in range(105)]}

        bot.prune_sent_entries()

        assert len(bot.sent_items["FeedA"]) == 95
        assert bot.sent_items["FeedA"][0] == "id10"

    def test_prune_sent_entries_multiple_feeds(self, bot) -> None:
        bot.sent_items = {
            "FeedA": [f"id{i}" for i in range(105)],
            "FeedB": [f"id{i}" for i in range(30)],
        }

        bot.prune_sent_entries()

        assert len(bot.sent_items["FeedA"]) == 95
        assert len(bot.sent_items["FeedB"]) == 30

    def test_save_sent_entries(self, bot) -> None:
        bot.sent_items = {"TestFeed": ["id1", "id2"]}

        bot.save_sent_entries()

        with open(bot.path, "r") as f:
            saved_data = json.load(f)

        assert saved_data == {"TestFeed": ["id1", "id2"]}

    def test_save_sent_entries_overwrites_existing(self, bot) -> None:
        bot.save_sent_entries()

        bot.sent_items = {"NewFeed": ["new_id"]}
        bot.save_sent_entries()

        with open(bot.path, "r") as f:
            saved_data = json.load(f)

        assert saved_data == {"NewFeed": ["new_id"]}
        assert "TechCrunch" not in saved_data

    @pytest.mark.asyncio
    async def test_send_batch(self, bot, fake_entry, fake_feed) -> None:
        success = MagicMock()
        success.status_code = 200
        success.text = "OK"

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=success)

        with patch("src.bot.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client

            await bot.send_batch([fake_entry], [fake_feed])

        assert fake_entry.id in bot.sent_items.get(fake_entry.feed, [])
        assert mock_client.post.call_count == 1

    @pytest.mark.asyncio
    async def test_send_batch_skips_already_sent(self, bot, fake_feed) -> None:
        already_sent = Entry(
            id="id1",
            feed="TechCrunch",
            title="Old Article",
            link="https://example.com/old",
            summary="<p>old</p>",
        )

        success = MagicMock()
        success.status_code = 200
        success.text = "OK"

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=success)

        tc_feed = Feed(
            name="TechCrunch",
            url="https://techcrunch.com",
            webhook="https://webhook_url.com",
        )

        with patch("src.bot.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client

            await bot.send_batch([already_sent], [tc_feed])

        assert mock_client.post.call_count == 0

    @pytest.mark.asyncio
    async def test_send_batch_does_not_add_on_failure(self, bot, fake_entry, fake_feed) -> None:
        failure = MagicMock()
        failure.status_code = 500
        failure.text = "Internal Server Error"

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=failure)

        with patch("src.bot.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client

            await bot.send_batch([fake_entry], [fake_feed])

        assert fake_entry.feed not in bot.sent_items or fake_entry.id not in bot.sent_items.get(fake_entry.feed, [])
