import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin Configuration
ADMINS = list(map(int, os.getenv("ADMINS", "").split()))

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "unzip_bot")

# Download Configuration
DOWNLOAD_DIR = "downloads"
MAX_CONCURRENT_DOWNLOADS = 3

# User Tier Limits
# Format: {tier: {"daily_files": count, "max_size_bytes": size}}
USER_LIMITS = {
    "free": {
        "daily_files": 1,
        "max_size_bytes": 1 * 1024 * 1024 * 1024,  # 1 GB
    },
    "premium": {
        "daily_files": 15,
        "max_size_bytes": 2 * 1024 * 1024 * 1024,  # 2 GB
    },
    "ultra_premium": {
        "daily_files": 50,
        "max_size_bytes": 2 * 1024 * 1024 * 1024,  # 2 GB
    }
}

# Premium Plans
# Format: {plan_type: {duration_days: {"inr": price, "usdt": price}}}
PREMIUM_PLANS = {
    "premium": {
        1: {"inr": 5, "usdt": 0.05},
        7: {"inr": 30, "usdt": 0.30},
        30: {"inr": 90, "usdt": 0.90}
    },
    "ultra_premium": {
        1: {"inr": 15, "usdt": 0.15},
        7: {"inr": 50, "usdt": 0.50},
        30: {"inr": 140, "usdt": 1.40}
    }
}

# Force Subscription
MAX_FORCE_SUB_CHANNELS = 4

# File Types
SUPPORTED_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']

# Messages
START_MESSAGE = """
👋 **Welcome to Unzip Bot!**

I can help you extract compressed files easily!

**How to use:**
1️⃣ Send me any ZIP/RAR/7Z file
2️⃣ Reply to it with `/unzip` (or `/unzip "password"` if protected)
3️⃣ Get your extracted files!

**Features:**
✅ Support for password-protected archives
✅ Multiple archive formats (ZIP, RAR, 7Z, etc.)
✅ Fast extraction and delivery

📊 Use /myplan to check your usage
💎 Use /premium to upgrade your plan
❓ Use /help for detailed instructions
"""

HELP_MESSAGE = """
📖 **How to Use Unzip Bot**

**Step-by-Step Guide:**

1️⃣ **Send a File:**
   • Upload any compressed file (ZIP, RAR, 7Z, etc.)
   • Or forward a file from any chat
   • Or send a Telegram file link (t.me/channel/message)

2️⃣ **Extract the File:**
   • Reply to the file with `/unzip`
   • For password-protected files: `/unzip "your_password"`

3️⃣ **Receive Files:**
   • Bot will extract and send all files to you
   • Progress updates will be shown

**Available Commands:**
/start - Start the bot
/help - Show this help message
/unzip - Extract file (reply to file message)
/myplan - Check current plan and usage
/premium - View premium plans
/redeem - Redeem premium code
/cancel - Cancel ongoing process

**User Tiers:**
🆓 **Free:** 1 file/day, 1GB max
💎 **Premium:** 15 files/day, 2GB max
⭐ **Ultra Premium:** 50 files/day, 2GB max

**Redeem Codes:**
Get premium codes and redeem with `/redeem CODE123`

**Supported Formats:**
.zip, .rar, .7z, .tar, .gz, .bz2
"""
