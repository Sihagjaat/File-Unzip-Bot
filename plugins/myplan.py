from pyrogram import Client, filters
from pyrogram.types import Message
from utils.quota_manager import get_user_stats
from utils.helpers import format_size, format_date
from config import USER_LIMITS


@Client.on_message(filters.command("myplan") & filters.private)
async def myplan_command(client: Client, message: Message):
    """Handle /myplan command"""
    user_id = message.from_user.id
    
    stats = get_user_stats(user_id)
    
    if not stats:
        await message.reply_text("❌ Please use /start first to register.")
        return
    
    # Format tier name
    tier_name = {
        'free': '🆓 Free',
        'premium': '💎 Premium',
        'ultra_premium': '⭐ Ultra Premium'
    }.get(stats['tier'], stats['tier'])
    
    # Build message
    text = f"📊 **Your Plan Details**\n\n"
    text += f"**Current Tier:** {tier_name}\n"
    text += f"**Daily Usage:** {stats['daily_used']}/{stats['daily_limit']} files\n"
    text += f"**Max File Size:** {format_size(stats['max_file_size'])}\n"
    
    if stats['tier'] in ['premium', 'ultra_premium']:
        if stats['premium_expiry']:
            text += f"**Premium Expires:** {format_date(stats['premium_expiry'])}\n"
    
    text += f"\n**Member Since:** {format_date(stats['join_date'])}\n"
    
    if stats['tier'] == 'free':
        text += f"\n💡 Want more quota? Check /premium"
    
    await message.reply_text(text)
