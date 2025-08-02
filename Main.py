# main.py
"""
🛡️ Restricted Content Saver Telegram Bot
A single-file Pyrogram bot to extract and save restricted/protected Telegram media.
Inspired by: https://github.com/V9store/Save-Restricted-Content-Bot-v3
"""

import os
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("21283957"))
API_HASH = os.getenv("aade44a828de52da2a6ef816b120020b")
BOT_TOKEN = os.getenv("8089332775:AAFsC5Hb58cqYzowJu6hBs_Wxz1Uns5Y7b8")
OWNER_ID = int(os.getenv("6917342289"))  # Only admin who can use admin commands

# Initialize bot
bot = Client("restricted_saver_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Simple in-memory banlist and log (can be replaced by DB)
banlist = set()
log_data = []

@bot.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text("👋 Welcome! Reply to any protected message with /save to download it.")

@bot.on_message(filters.command("save") & filters.reply)
async def save_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in banlist:
        await message.reply_text("🚫 You are banned from using this bot.")
        return

    replied = message.reply_to_message
    try:
        media = None
        caption = replied.caption or replied.text or ""

        if replied.photo:
            media = replied.photo
        elif replied.video:
            media = replied.video
        elif replied.document:
            media = replied.document
        elif replied.audio:
            media = replied.audio
        elif replied.voice:
            media = replied.voice
        elif replied.sticker:
            media = replied.sticker

        if media:
            saved = await media.download()
            log_data.append((user_id, media.file_id, datetime.utcnow()))
            await message.reply_document(saved, caption=f"✅ Saved content from restricted message.\n\nOriginal caption: {caption}")
        else:
            await message.reply_text("⚠️ Unsupported or empty media type.")
    except Exception as e:
        await message.reply_text(f"❌ Error while saving: {e}")

@bot.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_handler(client: Client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /ban <user_id>")
    try:
        uid = int(message.command[1])
        banlist.add(uid)
        await message.reply_text(f"✅ User {uid} has been banned.")
    except:
        await message.reply_text("❌ Invalid user ID.")

@bot.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_handler(client: Client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /unban <user_id>")
    try:
        uid = int(message.command[1])
        banlist.discard(uid)
        await message.reply_text(f"✅ User {uid} has been unbanned.")
    except:
        await message.reply_text("❌ Invalid user ID.")

@bot.on_message(filters.command("log") & filters.user(OWNER_ID))
async def log_handler(client: Client, message: Message):
    logs = "\n".join([f"User {uid} saved at {ts}" for uid, _, ts in log_data[-10:]])
    await message.reply_text(f"📝 Last 10 saves:\n{logs if logs else 'No activity yet.'}")

if __name__ == "__main__":
    print("🚀 Bot is running...")
    bot.run()
