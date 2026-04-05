import os
import time
import string
import random
import asyncio
import aiofiles
import datetime

from FileStream.utils.broadcast_helper import send_msg
from FileStream.utils.database import Database
from FileStream.bot import FileStream
from FileStream.server.exceptions import FIleNotFound
from FileStream.config import Telegram, Server
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums.parse_mode import ParseMode

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)
broadcast_ids = {}


@FileStream.on_message(filters.command("status") & filters.private & filters.user(Telegram.OWNER_ID))
async def status_handler(c: Client, m: Message):
    total_users = await db.total_users_count()
    banned_users = await db.total_banned_users_count()
    total_links = await db.total_files()
    await m.reply_text(
        text=(
            "📊 <b>Bot Statistics</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Total Users:</b> <code>{total_users}</code>\n"
            f"🚫 <b>Banned Users:</b> <code>{banned_users}</code>\n"
            f"🔗 <b>Total Links Generated:</b> <code>{total_links}</code>"
        ),
        parse_mode=ParseMode.HTML,
        quote=True
    )


@FileStream.on_message(filters.command("ban") & filters.private & filters.user(Telegram.OWNER_ID))
async def ban_handler(b, m: Message):
    user_id = m.text.split("/ban ")[-1].strip()
    if not user_id.lstrip('-').isdigit():
        await m.reply_text("⚠️ <b>Usage:</b> <code>/ban &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML, quote=True)
        return
    if not await db.is_user_banned(int(user_id)):
        try:
            await db.ban_user(int(user_id))
            await db.delete_user(int(user_id))
            await m.reply_text(
                text=f"🚫 User <code>{user_id}</code> has been <b>banned</b>.",
                parse_mode=ParseMode.HTML, quote=True
            )
            if not str(user_id).startswith('-100'):
                try:
                    await b.send_message(
                        chat_id=int(user_id),
                        text="🚫 <b>You have been banned from using this bot.</b>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
        except Exception as e:
            await m.reply_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode=ParseMode.HTML, quote=True)
    else:
        await m.reply_text(f"ℹ️ User <code>{user_id}</code> is already banned.", parse_mode=ParseMode.HTML, quote=True)


@FileStream.on_message(filters.command("unban") & filters.private & filters.user(Telegram.OWNER_ID))
async def unban_handler(b, m: Message):
    user_id = m.text.split("/unban ")[-1].strip()
    if not user_id.lstrip('-').isdigit():
        await m.reply_text("⚠️ <b>Usage:</b> <code>/unban &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML, quote=True)
        return
    if await db.is_user_banned(int(user_id)):
        try:
            await db.unban_user(int(user_id))
            await m.reply_text(
                text=f"✅ User <code>{user_id}</code> has been <b>unbanned</b>.",
                parse_mode=ParseMode.HTML, quote=True
            )
            if not str(user_id).startswith('-100'):
                try:
                    await b.send_message(
                        chat_id=int(user_id),
                        text="✅ <b>You have been unbanned. You can use the bot again.</b>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass
        except Exception as e:
            await m.reply_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode=ParseMode.HTML, quote=True)
    else:
        await m.reply_text(f"ℹ️ User <code>{user_id}</code> is not banned.", parse_mode=ParseMode.HTML, quote=True)


@FileStream.on_message(filters.command("broadcast") & filters.private & filters.user(Telegram.OWNER_ID) & filters.reply)
async def broadcast_handler(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break

    out = await m.reply_text("📡 <b>Broadcast started.</b> You'll be notified when done.", parse_mode=ParseMode.HTML)
    start_time = time.time()
    total_users = await db.total_users_count()
    done = failed = success = 0

    broadcast_ids[broadcast_id] = dict(total=total_users, current=done, failed=failed, success=success)

    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user['id']), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))
            try:
                await out.edit_text(
                    f"📡 <b>Broadcasting...</b>\n\n"
                    f"Sent: <code>{done}</code> / <code>{total_users}</code>\n"
                    f"✅ Success: <code>{success}</code>  ❌ Failed: <code>{failed}</code>",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass

    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()

    result_text = (
        f"✅ <b>Broadcast Complete</b>\n\n"
        f"⏱ Time: <code>{completed_in}</code>\n"
        f"👤 Total users: <code>{total_users}</code>\n"
        f"📨 Sent: <code>{done}</code>\n"
        f"✅ Success: <code>{success}</code>  ❌ Failed: <code>{failed}</code>"
    )

    if failed == 0:
        await m.reply_text(result_text, parse_mode=ParseMode.HTML, quote=True)
    else:
        await m.reply_document(document='broadcast.txt', caption=result_text, parse_mode=ParseMode.HTML, quote=True)

    if os.path.exists('broadcast.txt'):
        os.remove('broadcast.txt')


@FileStream.on_message(filters.command("del") & filters.private & filters.user(Telegram.OWNER_ID))
async def del_handler(c: Client, m: Message):
    file_id = m.text.split(" ")[-1].strip()
    try:
        file_info = await db.get_file(file_id)
    except FIleNotFound:
        await m.reply_text("ℹ️ <b>File not found.</b> It may have already been deleted.", parse_mode=ParseMode.HTML, quote=True)
        return
    await db.delete_one_file(file_info['_id'])
    await db.count_links(file_info['user_id'], "-")
    await m.reply_text(
        text=f"🗑 <b>File deleted successfully.</b>\n\n<code>{file_info['file_name']}</code>",
        parse_mode=ParseMode.HTML,
        quote=True
    )
