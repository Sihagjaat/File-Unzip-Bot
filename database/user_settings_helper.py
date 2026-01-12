from database.database import user_settings_collection


def get_default_settings():
    """Get default user settings"""
    return {
        "upload_as_document": True,
        "custom_caption": None,
        "caption_entities": None,
        "thumbnail": None,
        "caption_replacements": "",
        "filename_replacements": "",
        "filename_prefix": None,
        "filename_suffix": None
    }


def get_user_settings(user_id):
    """
    Get user settings from database or return defaults
    
    Args:
        user_id (int): Telegram user ID
    
    Returns:
        dict: User settings
    """
    settings = user_settings_collection.find_one({"user_id": user_id})
    
    if not settings:
        # Return default settings if user hasn't configured anything yet
        return get_default_settings()
    
    # Remove MongoDB _id field
    settings.pop('_id', None)
    
    # Ensure all fields exist (for backward compatibility)
    defaults = get_default_settings()
    for key, value in defaults.items():
        if key not in settings:
            settings[key] = value
    
    return settings


def update_user_settings(user_id, updates):
    """
    Update specific user settings fields
    
    Args:
        user_id (int): Telegram user ID
        updates (dict): Dictionary of fields to update
    
    Returns:
        bool: True if successful
    """
    try:
        user_settings_collection.update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error updating user settings: {e}")
        return False


def reset_user_settings(user_id):
    """
    Reset user settings to defaults
    
    Args:
        user_id (int): Telegram user ID
    
    Returns:
        bool: True if successful
    """
    try:
        defaults = get_default_settings()
        defaults["user_id"] = user_id
        
        user_settings_collection.update_one(
            {"user_id": user_id},
            {"$set": defaults},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error resetting user settings: {e}")
        return False
