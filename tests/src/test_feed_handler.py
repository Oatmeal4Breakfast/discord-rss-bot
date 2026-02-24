import pytest

from src.feed_handler import FeedHandler, Feed, Entry, FeedData


@pytest.fixture
def fake_handler() -> FeedHandler:
    return FeedHandler(feed_file="example.feeds.yaml")


class TestFeedHandler:
    def test_load_feeds_success(self, fake_handler) -> None:
        data: FeedData = fake_handler._load_feeds()

        assert data is not None
        assert isinstance(data, dict)

    def test_load_feeds_fails(self) -> None:
        bad_file: str = "fake_file.yaml"
        with pytest.raises(expected_exception=RuntimeError):
            FeedHandler(feed_file=bad_file)._load_feeds()

    def test_extract_feeds(self, fake_handler) -> None:
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
        fake_handler._load_feeds()
        fake_feed: list[Feed] = fake_handler.extract_feeds()[0]

        entries: list[Entry] = fake_handler.fetch_feed_entries(feed=fake_feed)

        assert entries
        assert len(entries) <= 5
        assert isinstance(entries, list)
        assert isinstance(entries[0], Entry)
