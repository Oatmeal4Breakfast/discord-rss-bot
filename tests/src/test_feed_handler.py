import pytest
from pathlib import Path

from src.feed_handler import FeedHandler, Feed, Entry, FeedData


@pytest.fixture
def fake_handler() -> FeedHandler:
    return FeedHandler()


class TestFeedHandler:
    def test_load_feeds_success(fake_handler: FeedHandler) -> None:
        data: FeedData = fake_handler._load_feeds()

        assert data is not None
        assert isinstance(data, list[dict[str, str]])

    def test_load_feeds_fails() -> None:
        bad_file: Path = Path.cwd() / "fake_file.yaml"
        with pytest.raises(expected_exception=FileNotFoundError):
            FeedHandler(feeds_file=bad_file)

    def test_extract_feeds(fake_handler: FeedHandler) -> None:
        fake_handler.extract_feeds()

        assert len(fake_handler.feeds) > 0
        assert isinstance(fake_handler.feeds, list[Feed])

    def test_extract_feeds_fails() -> None:
        # TODO: Find way to write this test
        raise NotImplementedError
