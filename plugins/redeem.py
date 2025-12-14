from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import redeem_codes_collection, users_collection
from datetime import datetime, timedelta
import random
import string


def generate_code():
    """Generate a 6-digit alphanumeric code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# Store user states for multi-step process
user_states = {}


@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_command(client: Client, message: Message):
    """Handle /redeem command for users with smart upgrade/extend logic"""
    user_id = message.from_user.id
    
    # Check if code is provided
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply_text(
            "❌ **Invalid Usage!**\n\n"
            "**Format:** `/redeem CODE123`\n\n"
            "**Example:** `/redeem ABC123`"
        )
        return
    
    code = parts[1].upper()
    
    # Find the code
    redeem_code = redeem_codes_collection.find_one({"code": code})
    
    if not redeem_code:
        await message.reply_text("❌ Invalid redeem code!")
        return
    
    if redeem_code.get('is_used'):
        await message.reply_text("❌ This code has already been used!")
        return
    
    # Get code details
    plan_type = redeem_code['plan_type']
    duration_days = redeem_code['duration_days']
    
    # Get current user data
    user = users_collection.find_one({"id": user_id})
    current_tier = user.get('tier', 'free')
    current_expiry = user.get('premium_expiry')
    
    # Define tier hierarchy
    tier_hierarchy = {'free': 0, 'premium': 1, 'ultra_premium': 2}
    new_tier_level = tier_hierarchy.get(plan_type, 0)
    current_tier_level = tier_hierarchy.get(current_tier, 0)
    
    # Determine action: upgrade, extend, or replace
    if new_tier_level > current_tier_level:
        # UPGRADE: New plan is better, replace current plan
        premium_expiry = datetime.utcnow() + timedelta(days=duration_days)
        action = "upgraded"
    elif new_tier_level == current_tier_level and current_tier != 'free':
        # EXTEND: Same tier, extend from current expiry
        if current_expiry and current_expiry > datetime.utcnow():
            # Extend from existing expiry
            premium_expiry = current_expiry + timedelta(days=duration_days)
            action = "extended"
        else:
            # Expired or no expiry, start fresh
            premium_expiry = datetime.utcnow() + timedelta(days=duration_days)
            action = "activated"
    else:
        # NEW or DOWNGRADE (treat as new)
        premium_expiry = datetime.utcnow() + timedelta(days=duration_days)
        action = "activated"
    
    # Update user
    users_collection.update_one(
        {"id": user_id},
        {"$set": {"tier": plan_type, "premium_expiry": premium_expiry}}
    )
    
    # Mark code as used
    redeem_codes_collection.update_one(
        {"code": code},
        {"$set": {"is_used": True, "used_by": user_id, "used_date": datetime.utcnow()}}
    )
    
    # Create response message
    if action == "upgraded":
        status_msg = f"⬆️ **Plan Upgraded!**"
    elif action == "extended":
        status_msg = f"➕ **Plan Extended!**"
    else:
        status_msg = f"🎉 **Plan Activated!**"
    
    await message.reply_text(
        f"{status_msg}\n\n"
        f"**Plan:** {plan_type.replace('_', ' ').title()}\n"
        f"**Duration:** +{duration_days} days\n"
        f"**Valid Until:** {premium_expiry.strftime('%d %b %Y')}\n\n"
        f"Use /myplan to see your new limits!"
    )
