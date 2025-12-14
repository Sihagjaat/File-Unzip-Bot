from datetime import datetime, timedelta
from database.database import users_collection, downloads_collection
from config import USER_LIMITS


def check_user_quota(user_id):
    """
    Check if user has remaining quota for the day
    Returns: (can_proceed: bool, message: str, current_tier: str)
    """
    user = users_collection.find_one({"id": user_id})
    
    if not user:
        # New user, should be registered first
        return False, "Please use /start first to register.", "free"
    
    # Check if premium has expired
    if user.get('tier') in ['premium', 'ultra_premium']:
        if user.get('premium_expiry') and user['premium_expiry'] < datetime.utcnow():
            users_collection.update_one(
                {"id": user_id},
                {"$set": {"tier": "free"}}
            )
            user['tier'] = 'free'
    
    # Reset daily count if needed
    if user.get('last_reset', datetime.utcnow()) < datetime.utcnow() - timedelta(days=1):
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"daily_count": 0, "last_reset": datetime.utcnow()}}
        )
        user['daily_count'] = 0
    
    # Get tier limits
    tier_limits = USER_LIMITS.get(user.get('tier', 'free'), USER_LIMITS['free'])
    daily_limit = tier_limits['daily_files']
    
    # Check if user has quota
    if user.get('daily_count', 0) >= daily_limit:
        return False, f"❌ Daily limit reached! You can extract {daily_limit} file(s) per day.\nUpgrade to premium for more quota: /premium", user.get('tier', 'free')
    
    return True, "OK", user.get('tier', 'free')


def check_file_size(user_id, file_size):
    """
    Check if file size is within user's tier limit
    Returns: (can_proceed: bool, message: str)
    """
    user = users_collection.find_one({"id": user_id})
    
    if not user:
        return False, "Please use /start first to register."
    
    # Get tier limits
    tier_limits = USER_LIMITS.get(user.get('tier', 'free'), USER_LIMITS['free'])
    max_size = tier_limits['max_size_bytes']
    
    if file_size > max_size:
        from utils.helpers import format_size
        return False, f"❌ File too large! Your tier allows max {format_size(max_size)}\nFile size: {format_size(file_size)}\nUpgrade to premium: /premium"
    
    return True, "OK"


def increment_user_quota(user_id, filename, file_size):
    """Increment user's daily count and log download"""
    # Increment daily count
    users_collection.update_one(
        {"id": user_id},
        {"$inc": {"daily_count": 1}}
    )
    
    # Log download
    downloads_collection.insert_one({
        "user_id": user_id,
        "filename": filename,
        "size": file_size,
        "timestamp": datetime.utcnow()
    })


def get_user_stats(user_id):
    """
    Get user statistics
    Returns: dict with user info
    """
    user = users_collection.find_one({"id": user_id})
    
    if not user:
        return None
    
    # Check premium expiry
    if user.get('tier') in ['premium', 'ultra_premium']:
        if user.get('premium_expiry') and user['premium_expiry'] < datetime.utcnow():
            users_collection.update_one(
                {"id": user_id},
                {"$set": {"tier": "free"}}
            )
            user['tier'] = 'free'
    
    # Reset daily count if needed
    if user.get('last_reset', datetime.utcnow()) < datetime.utcnow() - timedelta(days=1):
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"daily_count": 0, "last_reset": datetime.utcnow()}}
        )
        user['daily_count'] = 0
    
    tier_limits = USER_LIMITS.get(user.get('tier', 'free'), USER_LIMITS['free'])
    
    return {
        'tier': user.get('tier', 'free'),
        'daily_used': user.get('daily_count', 0),
        'daily_limit': tier_limits['daily_files'],
        'max_file_size': tier_limits['max_size_bytes'],
        'premium_expiry': user.get('premium_expiry'),
        'join_date': user.get('join_date', datetime.utcnow())
    }


def reset_all_quotas():
    """Reset all users' daily quotas (for scheduled task)"""
    result = users_collection.update_many(
        {},
        {"$set": {"daily_count": 0, "last_reset": datetime.utcnow()}}
    )
    print(f"✅ Reset quotas for {result.modified_count} users")
