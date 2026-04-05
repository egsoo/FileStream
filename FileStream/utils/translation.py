from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FileStream.config import Telegram


class LANG(object):

    START_TEXT = (
        "<b>👋 Welcome, {}!</b>\n\n"
        "I'm <b>FileStream Bot</b> — your personal Telegram file streaming server.\n\n"
        "📤 <b>Send me any file</b> (video, audio, document, photo) and I'll instantly generate:\n"
        "  • 🔗 A direct <b>streaming link</b> to watch online\n"
        "  • 📥 A direct <b>download link</b>\n\n"
        "Works with both <b>private chats</b> and <b>channels</b>.\n\n"
        "Use the buttons below to learn more. Powered by @{}"
    )

    HELP_TEXT = (
        "📖 <b>Commands &amp; Usage Guide</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>👤 User Commands</b>\n"
        "  /start — Start the bot &amp; see welcome message\n"
        "  /help  — Show this help guide\n"
        "  /about — Info about this bot\n"
        "  /files — Browse all your generated links\n\n"
        "<b>📤 How to Generate a Link</b>\n"
        "  1. Send any file directly to this bot in private chat\n"
        "  2. The bot will reply with a streaming &amp; download link\n"
        "  3. Share the link — no Telegram account required to access it\n\n"
        "<b>📡 Channel Mode</b>\n"
        "  1. Add this bot as an <b>admin</b> in your channel\n"
        "  2. Post any media — the bot auto-attaches a download button\n\n"
        "<b>🔒 Admin Commands</b> <i>(Owner only)</i>\n"
        "  /status   — Bot statistics (users, links, banned)\n"
        "  /ban &lt;id&gt; — Ban a user from using the bot\n"
        "  /unban &lt;id&gt; — Unban a user\n"
        "  /del &lt;id&gt;  — Delete a specific file link\n"
        "  /broadcast — Reply to a message to broadcast it to all users\n\n"
        "<b>⚠️ Note:</b> Adult content is strictly prohibited."
    )

    ABOUT_TEXT = (
        "ℹ️ <b>About FileStream Bot</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🤖 <b>Name:</b> {}\n"
        "🔢 <b>Version:</b> {}\n"
        "📅 <b>Last Updated:</b> 2024\n\n"
        "<b>What I do:</b>\n"
        "I convert Telegram files into direct streaming &amp; download links. "
        "Videos can be watched in-browser without downloading the full file first. "
        "Supports multi-client load balancing for high traffic.\n\n"
        "🛠 Built with Pyrogram &amp; aiohttp"
    )

    STREAM_TEXT = (
        "✅ <b>Link Generated Successfully!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>File:</b>\n{}\n\n"
        "📦 <b>Size:</b> {}\n\n"
        "📥 <b>Download:</b>\n{}"
    )

    STREAM_TEXT_X = (
        "✅ <b>Link Generated Successfully!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>File:</b>\n{}\n\n"
        "📦 <b>Size:</b> {}\n\n"
        "📥 <b>Download:</b>\n{}"
    )

    BAN_TEXT = (
        "🚫 <b>You have been banned from using this bot.</b>\n\n"
        "If you believe this is a mistake, contact the admin: "
        "<a href='tg://user?id={}'>[Support]</a>"
    )


class BUTTON(object):
    START_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ʜᴇʟᴘ 🦋", callback_data="help"),
                InlineKeyboardButton("ᴀʙᴏᴜᴛ ✨", callback_data="about"),
            ],
            [
                InlineKeyboardButton("ᴍʏ ꜰɪʟᴇꜱ ♻️", callback_data="myfiles_1"),
            ],
        ]
    )

    HELP_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="home"),
            ],
        ]
    )

    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="home"),
            ],
        ]
    )
