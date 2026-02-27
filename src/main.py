import asyncio
from src.bot import DiscordBot
from src.feed_handler import FeedHandler, Feed, Entry
from src.config import get_config, Config


async def main() -> None:
    config: Config = get_config()
    feed_handler: FeedHandler = FeedHandler(config.feed_file)
    bot: DiscordBot = DiscordBot(config)

    feeds: list[Feed] = feed_handler.extract_feeds()

    entries: list[Entry] = []
    for feed in feeds:
        feed_entries: list[Entry] = feed_handler.fetch_feed_entries(feed)
        for entry in feed_entries:
            entries.append(entry)

    await bot.send_batch(entries, feeds)

    bot.prune_sent_entries()
    bot.save_sent_entries()


if __name__ == "__main__":
    asyncio.run(main())
