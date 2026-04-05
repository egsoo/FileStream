# FileStreamBot

A Telegram bot that converts Telegram files into direct streaming and download links. Users can watch videos or download files via direct links without needing Telegram.

## Architecture

- **Bot framework:** Pyrogram (pyrofork fork) for Telegram interaction
- **Web server:** aiohttp serving streaming and download pages
- **Database:** MongoDB via Motor (async driver)
- **Templating:** Jinja2 for HTML pages

## Project Structure

```
FileStream/
  __main__.py          # Entry point — starts bot + web server
  config.py            # All config loaded from environment variables
  bot/
    __init__.py        # Bot client init
    clients.py         # Multi-client load balancing
    plugins/
      start.py         # /start, /help, /about, /files commands
      stream.py        # File receive handlers (private + channel)
      callback.py      # Inline keyboard callbacks
      admin.py         # Admin commands (/status, /ban, /unban, /broadcast, /del)
  server/
    __init__.py        # aiohttp app factory
    stream_routes.py   # /dl/{id} and /watch/{id} route handlers
    exceptions.py      # Custom exceptions
  template/
    play.html          # Video streaming page (dark theme, Plyr.js player)
    dl.html            # File download page (dark theme)
  utils/
    translation.py     # All bot message strings and inline keyboard buttons
    database.py        # MongoDB data access layer
    bot_utils.py       # Helper functions (link gen, user checks)
    file_properties.py # Extract file metadata from messages
    render_template.py # Render HTML templates for web pages
    human_readable.py  # File size formatting
```

## Required Environment Secrets

| Variable | Description |
|---|---|
| `API_ID` | Telegram API ID from my.telegram.org |
| `API_HASH` | Telegram API Hash from my.telegram.org |
| `BOT_TOKEN` | Bot token from @BotFather |
| `MONGO_DB_URI` | MongoDB connection string (mongodb+srv://...) |
| `FLOG_CHANNEL` | Telegram channel ID for file logs (integer) |
| `ULOG_CHANNEL` | Telegram channel ID for user logs (integer) |

## Optional Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | 5000 | Web server port |
| `BIND_ADDRESS` | 0.0.0.0 | Server bind address |
| `FQDN` | BIND_ADDRESS | Public domain for link generation |
| `HAS_SSL` | 0 | Set to 1 for HTTPS links |
| `NO_PORT` | 0 | Set to 1 to omit port from links |
| `OWNER_ID` | 7978482443 | Telegram user ID of bot owner |
| `UPDATES_CHANNEL` | Telegram | Updates channel username for buttons |
| `FORCE_SUB` | false | Require channel subscription |
| `MODE` | primary | primary = bot+server, secondary = server only |

## Running

The workflow command is: `python -m FileStream`

Web server runs on port 5000.

## UI Design

- Bot messages: Clean, professional HTML with emoji, no unicode small-caps
- Web pages: Self-contained dark theme (CSS variables), no external CDN dependencies except Google Fonts and Plyr.js
- No images used anywhere in bot responses
- play.html: Plyr.js-powered video player with stream/download/copy/external player options
- dl.html: Minimal download card with file info, download button, copy link
