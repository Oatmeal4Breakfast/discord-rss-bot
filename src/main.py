import asyncio
from src.bot import DiscordBot
from src.feed_handler import FeedHandler, Feed, Entry
from src.config import get_config, Config


async def main() -> None:
    config: Config = get_config()
    feed_handler: FeedHandler = FeedHandler(config)
    bot: DiscordBot = DiscordBot(config)

    feeds: list[Feed] = feed_handler.extract_feeds()

    for feed in feeds:
        entries: list[Entry] = feed_handler.fetch_feed_entries(feed)
        await bot.send_batch(entries, feeds)


if __name__ == "__main__":
    asyncio.run(main())
