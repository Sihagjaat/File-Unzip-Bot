from pyrogram import Client, filters
from pyrogram.types import Message
from config import HELP_MESSAGE


@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    await message.reply_text(HELP_MESSAGE)
