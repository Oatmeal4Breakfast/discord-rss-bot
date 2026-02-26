import pytest
import yaml

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.feed_handler import FeedHandler, Feed, Entry, FeedData


@pytest.fixture
def sample_feed() -> Feed:
    return Feed(
        name="fake_feed",
        url="https://example.com/feed",
        webhook="https://discord.webhook.url",
    )


@pytest.fixture
def fake_feed_file(tmp_path) -> Path:
    file_path: Path = tmp_path / "feeds.yaml"
    data: dict[str, list[dict[str, str]]] = {
        "feeds": [
            {
                "name": "fake_feed",
                "url": "https://example.com/feed",
                "webhook": "https://discord.webhook.url",
            }
        ]
    }
    file_path.write_text(yaml.dump(data))
    return file_path


@pytest.fixture
def fake_handler(fake_feed_file) -> FeedHandler:
    return FeedHandler(feed_file=fake_feed_file)


class TestFeedHandler:
    def test_load_feeds_success(self, fake_handler) -> None:
        data: FeedData = fake_handler._load_feeds()

        assert data is not None
        assert isinstance(data, dict)

    def test_load_feeds_fails(self) -> None:
        bad_file: str = "fake_file.yaml"
        with pytest.raises(expected_exception=RuntimeError):
            FeedHandler(feed_file=bad_file)._load_feeds()

    def test_extract_feeds(self, fake_handler, sample_feed) -> None:
        data: list[Feed] = fake_handler.extract_feeds()

        assert len(data) > 0
        assert isinstance(data, list)
        assert isinstance(data[0], Feed)
        assert data[0] == sample_feed

    def test_extract_feeds_fails(self, fake_handler) -> None:
        bad_file: str = "fake_file.yaml"
        bad_handler: FeedHandler = FeedHandler(feed_file=bad_file)
        with pytest.raises(expected_exception=RuntimeError):
            bad_handler.extract_feeds()

    @patch("src.feed_handler.feedparser.parse")
    def test_fetch_feed_entries(self, mock_parse, sample_feed, fake_handler) -> None:
        fake_feed_data = MagicMock()
        fake_feed_data.bozo = False
        fake_feed_data.entries = [
            MagicMock(
                id="123",
                feed="fake_feed",
                title="fake_entry",
                link="https://example.com",
                summary="<p> Hello </p>",
            )
        ]

        mock_parse.return_value = fake_feed_data

        entries = fake_handler.fetch_feed_entries(sample_feed)

        assert len(entries) == 1
        assert entries[0].title == "fake_entry"

        mock_parse.assert_called_once_with(
            url_file_stream_or_string="https://example.com/feed"
        )
