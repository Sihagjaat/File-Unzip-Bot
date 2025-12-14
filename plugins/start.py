from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import users_collection
from config import START_MESSAGE
from datetime import datetime


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Check if user exists
    user = users_collection.find_one({"id": user_id})
    
    if not user:
        # Create new user
        users_collection.insert_one({
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "join_date": datetime.utcnow(),
            "tier": "free",
            "daily_count": 0,
            "last_reset": datetime.utcnow(),
            "is_banned": False
        })
    else:
        # Update user info and unban if they're back
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"username": username, "first_name": first_name, "is_banned": False}}
        )
    
    await message.reply_text(START_MESSAGE)
