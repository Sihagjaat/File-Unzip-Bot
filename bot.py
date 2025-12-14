import os
import shutil
from pyrogram import Client, filters
from pyrogram.types import BotCommand
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_DIR
from database.database import init_db

# Create downloads directory
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Cleanup old downloads on startup
def cleanup_downloads():
    """Clean up downloads folder on bot startup"""
    try:
        if os.path.exists(DOWNLOAD_DIR):
            # Remove all files and folders in downloads
            for item in os.listdir(DOWNLOAD_DIR):
                item_path = os.path.join(DOWNLOAD_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Error cleaning up {item_path}: {e}")
            print(f"Cleaned up {DOWNLOAD_DIR} folder")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Initialize Pyrogram Client with optimized settings
app = Client(
    "unzip_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    sleep_threshold=60,  # Prevent flood wait
    workers=8  # Increase concurrent workers for better performance
)


@app.on_message(filters.command("start") & filters.private, group=-1)
async def setup_commands_on_first_start(client, message):
    """Set bot commands on first interaction"""
    # This will only set commands once
    pass


async def set_bot_commands():
    """Set bot commands menu"""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help and usage info"),
        BotCommand("unzip", "Extract archive file"),
        BotCommand("myplan", "Check your current plan"),
        BotCommand("premium", "Purchase premium subscription"),
        BotCommand("redeem", "Redeem a premium code"),
        BotCommand("cancel", "Cancel ongoing process")
    ]
    
    await app.set_bot_commands(commands)


if __name__ == "__main__":
    print("Starting Unzip Bot...")
    
    # Cleanup old files
    cleanup_downloads()
    
    # Initialize database
    init_db()
    
    # Set commands when bot starts
    async def on_startup():
        await set_bot_commands()
    
    app.start()
    app.loop.run_until_complete(on_startup())
    
    
    print("Running...")
    
    # Keep the bot running
    from pyrogram import idle
    idle()
    app.stop()


