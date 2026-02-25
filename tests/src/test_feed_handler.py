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
        webhook="https://discord.webhool.url",
    )


@pytest.fixture
def sample_entry(sample_feed) -> Entry:
    return Entry(
        id="123",
        feed=sample_feed.name,
        title="Test Article",
        link="https://link_to_entry.com",
        summary="<p> example entry </p>",
    )


@pytest.fixture
def sample_entries(sample_feed) -> list[Entry]:
    return [
        Entry(
            id="1",
            feed=sample_feed.name,
            title="Test 1",
            link="https://link_to_entry1.com",
            summary="<p> test entry 1 </p>",
        ),
        Entry(
            id="2",
            feed=sample_feed.name,
            title="Test 2",
            link="https://link_to_entry1.com",
            summary="<p> test entry 2 </p>",
        ),
        Entry(
            id="3",
            feed=sample_feed.name,
            title="Test 3",
            link="https://link_to_entry1.com",
            summary="<p> test entry 3 </p>",
        ),
    ]


@pytest.fixture
def fake_feed_file(tmp_path) -> Path:
    file_path = tmp_path / "feeds.yaml"
    data: dict[str, dict[str, str]] = {
        "feeds": {
            "name": "fake_feed",
            "url": "https://example.com/feed",
            "webhook": "https://discord.webhool.url",
        }
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

    def test_extract_feeds_fails(self, fake_handler) -> None:
        bad_file: str = "fake_file.yaml"
        bad_handler: FeedHandler = FeedHandler(feed_file=bad_file)
        with pytest.raises(expected_exception=RuntimeError):
            bad_handler.extract_feeds()

    def test_fetch_feed_entries(self, fake_handler) -> None:
        fake_feed: list[Feed] = fake_handler.extract_feeds()[0]

        entries: list[Entry] = fake_handler.fetch_feed_entries(feed=fake_feed)

        assert entries
        assert len(entries) <= 5
        assert isinstance(entries, list)
        assert isinstance(entries[0], Entry)
