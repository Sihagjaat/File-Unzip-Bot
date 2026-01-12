# MongoDB Collections Structure Documentation
# This file documents the schema for MongoDB collections

"""
Users Collection:
{
    "id": int,  # Telegram user ID (unique)
    "username": str,
    "first_name": str,
    "join_date": datetime,
    "tier": str,  # 'free', 'premium', 'ultra_premium'
    "premium_expiry": datetime,
    "daily_count": int,
    "last_reset": datetime,
    "is_banned": bool  # Flag for users who blocked the bot
}

Downloads Collection:
{
    "user_id": int,
    "filename": str,
    "size": int,  # in bytes
    "timestamp": datetime
}

Subscriptions Collection:
{
    "user_id": int,
    "plan_type": str,  # 'premium' or 'ultra_premium'
    "start_date": datetime,
    "end_date": datetime,
    "amount": int  # in rupees
}

ForceSubChannels Collection:
{
    "channel_id": int,  # unique
    "channel_title": str,
    "added_date": datetime
}

BotConfig Collection:
{
    "setting_name": str,  # unique
    "setting_value": str
}

RedeemCodes Collection:
{
    "code": str,  # 6-digit unique code
    "plan_type": str,  # 'premium' or 'ultra_premium'
    "duration_days": int,  # 1, 7, or 30
    "is_used": bool,
    "used_by": int,  # user_id who redeemed
    "created_date": datetime,
    "used_date": datetime
}

OngoingProcesses Collection:
{
    "user_id": int,
    "process_type": str,  # 'extraction', 'broadcast', etc.
    "filename": str,
    "start_time": datetime,
    "status": str  # 'downloading', 'extracting', 'uploading'
}

UserSettings Collection:
{
    "user_id": int,  # unique
    "upload_as_document": bool,  # True for document, False for media
    "custom_caption": str or None,  # Caption template with variables
    "caption_entities": list or None,  # Telegram MessageEntity objects for formatting
    "thumbnail": str or None,  # file_id of thumbnail image
    "caption_replacements": str,  # Pipe-separated: "old:new | word"
    "filename_replacements": str,  # Pipe-separated: "old:new | word"
    "filename_prefix": str or None,  # Prefix (space added automatically)
    "filename_suffix": str or None  # Suffix (space added automatically, before extension)
}
"""
