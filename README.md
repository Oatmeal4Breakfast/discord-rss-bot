# discord-rss-bot

A lightweight Python script that polls RSS feeds and posts new entries to Discord channels via webhooks. Designed to be run on a schedule (e.g. cron).

## How it works

On each run, the bot:

1. Reads a list of RSS feeds from a YAML config file
2. Fetches the latest entries from each feed (up to 3 per feed)
3. Filters out entries that have already been sent
4. Posts new entries to their configured Discord webhook as embeds
5. Saves the list of sent entry IDs to a JSON file for deduplication on the next run

## Configuration

Create a `.env` file in the project root:

```
FEED_FILE=feeds.yaml
SENT_FILE=data/sent_items.json
LOG_FILE=data/bot.log
LOG_LEVEL=INFO
RETRY_COUNT=3
```

| Variable | Description |
|---|---|
| `FEED_FILE` | Path to the feeds YAML file |
| `SENT_FILE` | Path to the JSON file used to track sent entries |
| `LOG_FILE` | Path to the log file |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `RETRY_COUNT` | Number of retries when Discord rate-limits a request (429) |

## Feeds file

Copy `example.feeds.yaml` to `feeds.yaml` and add your feeds:

```yaml
feeds:
  - name: "TechCrunch"
    url: "https://techcrunch.com/feed/"
    webhook: "https://discord.com/api/webhooks/..."
```

Each feed requires a `name`, RSS `url`, and a Discord `webhook` URL. Multiple feeds can share the same webhook or post to different channels.

## Running

**Locally with uv:**

```bash
uv run -m src.main
```

**With Docker Compose:**

```bash
UID=$(id -u) GID=$(id -g) docker compose up
```

The `data/` directory is mounted as a volume so that `sent_items.json` and logs persist between runs.

## Scheduling

The bot is stateless between runs and intended to be executed on a schedule. Example cron entry to run every 30 minutes:

```
*/30 * * * * cd /path/to/discord-rss-bot && UID=$(id -u) GID=$(id -g) docker compose up
```

## Dependencies

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (package manager)
- feedparser, httpx, pydantic, pyyaml, html2text
