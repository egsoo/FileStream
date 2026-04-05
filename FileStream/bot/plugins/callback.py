import datetime
import math
from FileStream import __version__
from FileStream.bot import FileStream
from FileStream.config import Telegram, Server
from FileStream.utils.translation import LANG, BUTTON
from FileStream.utils.bot_utils import gen_link, file_icon, truncate_name
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes
from FileStream.server.exceptions import FIleNotFound
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
from pyrogram.enums.parse_mode import ParseMode

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


@FileStream.on_callback_query()
async def cb_data(bot, update: CallbackQuery):
    usr_cmd = update.data.split("_")

    if usr_cmd[0] == "home":
        await update.message.edit_text(
            text=LANG.START_TEXT.format(update.from_user.mention, FileStream.username),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=BUTTON.START_BUTTONS
        )

    elif usr_cmd[0] == "help":
        await update.message.edit_text(
            text=LANG.HELP_TEXT,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=BUTTON.HELP_BUTTONS
        )

    elif usr_cmd[0] == "about":
        await update.message.edit_text(
            text=LANG.ABOUT_TEXT.format(FileStream.fname, __version__),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=BUTTON.ABOUT_BUTTONS
        )

    elif usr_cmd[0] == "myfiles":
        page = int(usr_cmd[1]) if len(usr_cmd) > 1 else 1
        file_list, total_files = await gen_file_list_button(page, update.from_user.id)
        await update.message.edit_text(
            text=f"📁 <b>My Files</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n<b>Total links generated:</b> <code>{total_files}</code>\n\nSelect a file to view its options:",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(file_list)
        )

    elif usr_cmd[0] == "N/A":
        await update.answer("N/A", True)

    elif usr_cmd[0] == "close":
        await update.message.delete()

    elif usr_cmd[0] == "msgdelete":
        await update.message.edit_text(
            text=(
                "⚠️ <b>Confirm Deletion</b>\n\n"
                "Are you sure you want to permanently delete this file link?\n"
                "This action cannot be undone."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ʏᴇs, ᴅᴇʟᴇᴛᴇ ✅", callback_data=f"msgdelyes_{usr_cmd[1]}_{usr_cmd[2]}"),
                    InlineKeyboardButton("ᴄᴀɴᴄᴇʟ ❌", callback_data=f"myfile_{usr_cmd[1]}_{usr_cmd[2]}")
                ]
            ])
        )

    elif usr_cmd[0] == "msgdelyes":
        await delete_user_file(usr_cmd[1], int(usr_cmd[2]), update)
        return

    elif usr_cmd[0] == "msgdelpvt":
        await update.message.edit_text(
            text=(
                "⚠️ <b>Confirm Deletion</b>\n\n"
                "Are you sure you want to permanently delete this file link?\n"
                "This action cannot be undone."
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("ʏᴇs, ᴅᴇʟᴇᴛᴇ ✅", callback_data=f"msgdelpvtyes_{usr_cmd[1]}"),
                    InlineKeyboardButton("ᴄᴀɴᴄᴇʟ ❌", callback_data=f"mainstream_{usr_cmd[1]}")
                ]
            ])
        )

    elif usr_cmd[0] == "msgdelpvtyes":
        await delete_user_filex(usr_cmd[1], update)
        return

    elif usr_cmd[0] == "mainstream":
        _id = usr_cmd[1]
        reply_markup, stream_text = await gen_link(_id=_id)
        await update.message.edit_text(
            text=stream_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
        )

    elif usr_cmd[0] == "userfiles":
        file_list, total_files = await gen_file_list_button(int(usr_cmd[1]), update.from_user.id)
        await update.message.edit_text(
            text=f"📁 <b>My Files</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n<b>Total links generated:</b> <code>{total_files}</code>\n\nSelect a file to view its options:",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(file_list)
        )

    elif usr_cmd[0] == "myfile":
        await gen_file_menu(usr_cmd[1], usr_cmd[2], update)
        return

    elif usr_cmd[0] == "sendfile":
        myfile = await db.get_file(usr_cmd[1])
        file_name = myfile['file_name']
        await update.answer(f"Sending: {file_name}")
        await update.message.reply_cached_media(myfile['file_id'], caption=f'<b>{file_name}</b>', parse_mode=ParseMode.HTML)

    else:
        await update.message.delete()


async def gen_file_list_button(file_list_no: int, user_id: int):
    file_range = [file_list_no * 10 - 10 + 1, file_list_no * 10]
    user_files, total_files = await db.find_files(user_id, file_range)

    file_list = []
    async for x in user_files:
        icon = file_icon(x.get("mime_type", ""))
        label = truncate_name(x['file_name'])
        file_list.append([InlineKeyboardButton(f"{icon} {label}", callback_data=f"myfile_{x['_id']}_{file_list_no}")])

    if total_files > 10:
        file_list.append([
            InlineKeyboardButton("◀", callback_data="{}".format("userfiles_" + str(file_list_no - 1) if file_list_no > 1 else "N/A")),
            InlineKeyboardButton(f"{file_list_no} / {math.ceil(total_files / 10)}", callback_data="N/A"),
            InlineKeyboardButton("▶", callback_data="{}".format("userfiles_" + str(file_list_no + 1) if total_files > file_list_no * 10 else "N/A")),
        ])

    if not file_list:
        file_list.append([InlineKeyboardButton("📭 No files yet", callback_data="N/A")])

    file_list.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="home")])
    return file_list, total_files


async def gen_file_menu(_id, file_list_no, update: CallbackQuery):
    try:
        myfile_info = await db.get_file(_id)
    except FIleNotFound:
        await update.answer("File not found.")
        return

    file_id = FileId.decode(myfile_info['file_id'])

    if file_id.file_type in PHOTO_TYPES:
        file_type = "🖼 Image"
    elif file_id.file_type == FileType.VOICE:
        file_type = "🎙 Voice"
    elif file_id.file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
        file_type = "🎬 Video"
    elif file_id.file_type == FileType.DOCUMENT:
        file_type = "📄 Document"
    elif file_id.file_type == FileType.STICKER:
        file_type = "🎭 Sticker"
    elif file_id.file_type == FileType.AUDIO:
        file_type = "🎵 Audio"
    else:
        file_type = "📦 Unknown"

    page_link = f"{Server.URL}watch/{myfile_info['_id']}"
    stream_link = f"{Server.URL}dl/{myfile_info['_id']}"
    is_video = "Video" in file_type

    if is_video:
        action_buttons = [
            [
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🧬", url=page_link),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 💗", url=stream_link),
                InlineKeyboardButton("ɢᴇᴛ ꜰɪʟᴇ 📂", callback_data=f"sendfile_{myfile_info['_id']}"),
            ]
        ]
    else:
        action_buttons = [
            [
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 💗", url=stream_link),
                InlineKeyboardButton("ɢᴇᴛ ꜰɪʟᴇ 📂", callback_data=f"sendfile_{myfile_info['_id']}"),
            ]
        ]

    action_buttons += [
        [
            InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ ꜰɪʟᴇ 👻", callback_data=f"msgdelete_{myfile_info['_id']}_{file_list_no}"),
            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"userfiles_{file_list_no}"),
        ],
    ]

    time_val = myfile_info['time']
    if isinstance(time_val, float):
        date_str = datetime.datetime.fromtimestamp(time_val).strftime("%Y-%m-%d")
    else:
        date_str = str(time_val)

    await update.message.edit_text(
        text=(
            f"📋 <b>File Details</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📂 <b>Name:</b> {myfile_info['file_name']}\n\n"
            f"📦 <b>Size:</b> {humanbytes(int(myfile_info['file_size']))}\n\n"
            f"🏷 <b>Type:</b> {file_type}\n\n"
            f"📅 <b>Created:</b> {date_str}"
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(action_buttons)
    )


async def delete_user_file(_id, file_list_no: int, update: CallbackQuery):
    try:
        myfile_info = await db.get_file(_id)
    except FIleNotFound:
        await update.answer("File already deleted.")
        return

    await db.delete_one_file(myfile_info['_id'])
    await db.count_links(update.from_user.id, "-")
    await update.message.edit_text(
        text=(
            "🗑 <b>File link deleted successfully.</b>\n\n"
            f"<code>{myfile_info['file_name']}</code> has been removed."
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="userfiles_1")]
        ])
    )


async def delete_user_filex(_id, update: CallbackQuery):
    try:
        myfile_info = await db.get_file(_id)
    except FIleNotFound:
        await update.answer("File already deleted.")
        return

    await db.delete_one_file(myfile_info['_id'])
    await db.count_links(update.from_user.id, "-")
    await update.message.edit_text(
        text=(
            "🗑 <b>File link deleted successfully.</b>\n\n"
            f"<code>{myfile_info['file_name']}</code> has been removed."
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data="home")]
        ])
    )
